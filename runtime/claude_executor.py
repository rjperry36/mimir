"""A REAL agent-executor adapter satisfying the kernel's AgentExecutor contract.

This is the concrete implementation behind the previously-stubbed
:class:`~runtime.executor.ClaudeSubagentExecutor`. It runs a wave as a real
Claude agent turn and maps the real outcome onto the kernel's termination-cause
enum, emitting heartbeats on streaming/tool events so the kernel's dead-agent
detection works against real latency.

Honest scope
------------
No live API credentials or SDK are assumed to be present in this environment
(they are not, here). The adapter is therefore built against a small, swappable
:class:`Transport` interface:

* :class:`FakeTransport` - a deterministic, clock-driven transport that replays
  a scripted timeline of token / tool-use / completion / error / 429 events.
  **This is what the tests prove the adapter against.**
* :class:`AnthropicMessagesTransport` - the real transport. If the ``anthropic``
  SDK (Messages API) is installed and an API key is configured, it runs a real
  streaming tool-use loop against ``claude-opus-4-8``, wrapping the request in
  the resilience layer (retry/backoff, 429 -> BUDGET_PAUSED). It is COMPLETE,
  documented code, but **a live run is NOT proven in this sandbox** - it needs
  credentials + the SDK. See the class docstring.

Both transports expose the *same* pull-based ``poll()`` snapshot, so the handle
and the outcome-mapping logic are identical whether the run is fake or real.

Timing model
------------
The transport owns timing via the injected :class:`~runtime.clock.Clock`:
``poll()`` returns a :class:`TransportPoll` whose ``last_activity`` is the
absolute clock time of the most recent heartbeat-worthy event. Under a
``ManualClock`` this is fully deterministic (mirroring ``MockExecutor``); under
a ``MonotonicClock`` in production the real transport's worker thread records
event times against that same clock.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional

from .clock import Clock
from .credentials import Credentials
from .executor import (
    AgentResult,
    ExecutionHandle,
    TerminationCause,
    WaveTask,
)
from .resilience import CircuitBreaker, RetryPolicy, resilient_call

DEFAULT_MODEL = "claude-opus-4-8"


# ---------------------------------------------------------------------------
# Transport interface + snapshot type
# ---------------------------------------------------------------------------


class TransportStatus(str, Enum):
    RUNNING = "RUNNING"          # still producing tokens / tool events
    COMPLETED = "COMPLETED"      # the agent turn finished normally
    ERROR = "ERROR"             # API error persisted after retries
    RATE_LIMITED = "RATE_LIMITED"  # quota / 429 - budget ceiling reached


@dataclass
class TransportPoll:
    """A point-in-time snapshot of a transport's progress.

    ``last_activity`` is an **absolute clock time** (not elapsed): the moment of
    the most recent heartbeat-worthy event (streamed token or tool-use). The
    handle reports it verbatim from :meth:`ExecutionHandle.last_heartbeat`, which
    is what lets the kernel notice a silent death when it stops advancing.
    """

    status: TransportStatus
    last_activity: float
    tokens: int = 0
    tool_uses: int = 0
    output: dict = field(default_factory=dict)
    detail: str = ""


class Transport:
    """Pull-based, clock-driven transport interface.

    An implementation returns cumulative progress from :meth:`poll` and stops
    any underlying work in :meth:`close`. Timing is owned by the transport (via
    an injected clock), so the handle never has to reason about elapsed time.
    """

    def poll(self) -> TransportPoll:  # pragma: no cover - interface
        raise NotImplementedError

    def close(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError


# ---------------------------------------------------------------------------
# FakeTransport - deterministic, scripted, clock-driven (used by the tests)
# ---------------------------------------------------------------------------


@dataclass
class FakeEvent:
    """One scripted event on a fake transport's timeline.

    ``at`` is elapsed seconds from the run's start. ``kind`` is one of:
      * ``"token"``     - a streamed token chunk (heartbeat + tokens).
      * ``"tool_use"``  - a tool call (heartbeat + tool_uses).
      * ``"complete"``  - the turn finished normally (terminal).
      * ``"error"``     - an API error that persisted after retries (terminal).
      * ``"rate_limit"``- a 429 / quota exhaustion (terminal).
    A "silent death" is modelled simply by ending the timeline on heartbeat
    events with *no* terminal event: ``last_activity`` freezes and the kernel's
    grace window elapses.
    """

    at: float
    kind: str
    data: dict = field(default_factory=dict)


class FakeTransport(Transport):
    """Replays a scripted timeline as a function of the injected clock."""

    def __init__(self, clock: Clock, events: List[FakeEvent], *,
                 tokens_per_token_event: int = 100,
                 output: Optional[dict] = None, detail: str = "") -> None:
        self._clock = clock
        self._events = sorted(events, key=lambda e: e.at)
        self._start = clock.now()
        self._closed = False
        self._tpe = tokens_per_token_event
        self._output = output or {}
        self._detail = detail

    def poll(self) -> TransportPoll:
        elapsed = self._clock.now() - self._start
        tokens = 0
        tool_uses = 0
        last_at = 0.0  # relative; start = fresh heartbeat at t0
        status = TransportStatus.RUNNING
        detail = ""
        output: dict = {}

        for e in self._events:
            if e.at > elapsed:
                break
            if self._closed and e.kind in ("token", "tool_use"):
                # once cancelled, no further heartbeats are produced
                continue
            if e.kind == "token":
                tokens += e.data.get("tokens", self._tpe)
                last_at = e.at
            elif e.kind == "tool_use":
                tool_uses += 1
                last_at = e.at
            elif e.kind == "complete":
                status = TransportStatus.COMPLETED
                last_at = e.at
                tokens += e.data.get("tokens", 0)
                output = dict(self._output)
                detail = self._detail or "agent turn completed"
            elif e.kind == "error":
                status = TransportStatus.ERROR
                last_at = e.at
                detail = e.data.get("detail", "API error persisted after retries")
            elif e.kind == "rate_limit":
                status = TransportStatus.RATE_LIMITED
                last_at = e.at
                detail = e.data.get("detail", "quota exhausted (HTTP 429)")

        return TransportPoll(
            status=status,
            last_activity=self._start + last_at,
            tokens=tokens,
            tool_uses=tool_uses,
            output=output,
            detail=detail,
        )

    def close(self) -> None:
        self._closed = True


# ---------------------------------------------------------------------------
# The execution handle
# ---------------------------------------------------------------------------


class _SubagentHandle:
    """Non-blocking handle the kernel polls while monitoring liveness.

    Maps transport status -> :class:`~runtime.executor.TerminationCause`:
      COMPLETED    -> COMPLETED (+ metrics: tokens, tool_uses, duration_ms)
      RATE_LIMITED -> BUDGET_PAUSED  (quota/429)
      ERROR        -> DIED           (API error after the transport's retries)
      cancel(cause)-> whatever cause the kernel passed (DIED / TIMED_OUT), or
                      CANCELLED for an externally-requested stop.
    A silent hang is detected by the *kernel*: ``last_heartbeat`` stops
    advancing, the grace window elapses, and the kernel calls ``cancel(DIED)``.
    """

    def __init__(self, transport: Transport, clock: Clock, task: WaveTask) -> None:
        self._t = transport
        self._clock = clock
        self._task = task
        self._start = clock.now()
        self._cancelled: Optional[TerminationCause] = None
        self._result: Optional[AgentResult] = None
        self._last_hb = self._start

    def poll(self) -> Optional[AgentResult]:
        if self._result is not None:
            return self._result
        if self._cancelled is not None:
            self._result = AgentResult(
                cause=self._cancelled,
                detail=f"run stopped: {self._cancelled.value}")
            return self._result

        p = self._t.poll()
        self._last_hb = p.last_activity

        if p.status is TransportStatus.RUNNING:
            return None
        if p.status is TransportStatus.COMPLETED:
            metrics = {
                "tokens": p.tokens,
                "tool_uses": p.tool_uses,
                "duration_ms": int((self._clock.now() - self._start) * 1000),
            }
            self._result = AgentResult(
                cause=TerminationCause.COMPLETED,
                metrics=metrics,
                output=p.output,
                detail=p.detail or "agent turn completed")
        elif p.status is TransportStatus.RATE_LIMITED:
            self._t.close()
            self._result = AgentResult(
                cause=TerminationCause.BUDGET_PAUSED,
                metrics={"tokens": p.tokens, "tool_uses": p.tool_uses},
                detail=p.detail or "quota exhausted (HTTP 429)")
        elif p.status is TransportStatus.ERROR:
            self._t.close()
            self._result = AgentResult(
                cause=TerminationCause.DIED,
                metrics={"tokens": p.tokens, "tool_uses": p.tool_uses},
                detail=p.detail or "API error persisted after retries")
        return self._result

    def last_heartbeat(self) -> float:
        if self._result is not None or self._cancelled is not None:
            return self._last_hb
        self._last_hb = self._t.poll().last_activity
        return self._last_hb

    def cancel(self, cause: TerminationCause) -> None:
        if self._cancelled is None and self._result is None:
            self._cancelled = cause
        try:
            self._t.close()
        except Exception:  # noqa: BLE001 - cancellation must not raise
            pass


# ---------------------------------------------------------------------------
# The real executor
# ---------------------------------------------------------------------------


TransportFactory = Callable[[WaveTask, object, Clock], Transport]


class ClaudeSubagentExecutor:
    """Runs a wave as a real Claude agent turn behind a swappable transport.

    Satisfies the kernel's ``AgentExecutor`` contract exactly:
    ``submit(task, workspace, clock) -> handle`` with the handle honouring
    ``poll() / last_heartbeat() / cancel()``.

    Construct it with a ``transport_factory``:

      * pass a :class:`FakeTransport` factory in tests (deterministic);
      * pass :func:`default_transport_factory` (the default) for a real run,
        which builds an :class:`AnthropicMessagesTransport` - requires the
        ``anthropic`` SDK and an API key, and raises a clear, documented error
        if neither is available.

    This is a drop-in replacement for ``MockExecutor``: the same kernel logic
    runs against it unchanged.
    """

    def __init__(self, transport_factory: Optional[TransportFactory] = None, *,
                 model: str = DEFAULT_MODEL,
                 system_prompt: str = "",
                 credentials: Optional[Credentials] = None,
                 retry: Optional[RetryPolicy] = None,
                 breaker: Optional[CircuitBreaker] = None) -> None:
        self._factory = transport_factory
        self.model = model
        self.system_prompt = system_prompt
        # BYOK: env-first, then any injected runtime config. Never a hardcoded
        # key, never a committed file. A live run resolves the key from here.
        self.credentials = credentials or Credentials()
        self.retry = retry
        self.breaker = breaker
        self.submitted_waves: List[str] = []

    def submit(self, task: WaveTask, workspace, clock: Clock) -> ExecutionHandle:
        self.submitted_waves.append(task.wave_id)
        factory = self._factory or (
            lambda t, ws, ck: default_transport_factory(
                t, ws, ck, model=self.model, system_prompt=self.system_prompt,
                credentials=self.credentials,
                retry=self.retry, breaker=self.breaker))
        transport = factory(task, workspace, clock)
        return _SubagentHandle(transport, clock, task)


# ---------------------------------------------------------------------------
# AnthropicMessagesTransport - the REAL transport (unproven in this sandbox)
# ---------------------------------------------------------------------------


class AnthropicMessagesTransport(Transport):
    """Real transport: a streaming tool-use loop over the Anthropic Messages API.

    NOT PROVEN IN THIS SANDBOX. A live run additionally requires:
      * ``pip install anthropic`` (the Messages API SDK), and
      * an API key resolvable by the SDK (``ANTHROPIC_API_KEY`` or an
        ``ant auth login`` profile).

    Given both, it:
      * spawns a background worker that opens ``client.messages.stream(...)``
        against the configured model with the task payload as the user turn;
      * records the injected-clock time on every streamed token and tool-use
        event, so :meth:`poll`'s ``last_activity`` advances with real progress
        and the kernel's silent-death detector works against real latency;
      * runs the request through :func:`resilient_call` so transient API errors
        are retried with backoff; a persisted error -> ``ERROR`` (kernel: DIED),
        a ``RateLimitError`` / 429 -> ``RATE_LIMITED`` (kernel: BUDGET_PAUSED);
      * on normal completion reports ``COMPLETED`` with token/tool-use metrics.

    The tool-use loop itself (executing tools the agent requests and feeding
    ``tool_result`` blocks back) is where a subagent would run its tools; it is
    sketched here against the documented Messages API shape. Wiring concrete
    tools is deployment-specific and intentionally left to the integrator - the
    transport contract (``poll``/``close``) and the kernel's correctness do not
    depend on it.
    """

    def __init__(self, task: WaveTask, clock: Clock, *,
                 model: str = DEFAULT_MODEL, system_prompt: str = "",
                 max_tokens: int = 4096,
                 credentials: Optional[Credentials] = None,
                 retry: Optional[RetryPolicy] = None,
                 breaker: Optional[CircuitBreaker] = None,
                 client: Optional[object] = None) -> None:
        creds = credentials or Credentials()
        # BYOK: when we must build a real client, require the user's key FIRST -
        # env-first, then injected config - and fail LOUD if it is absent. We
        # check this before the SDK import so the missing-key message (the thing
        # the operator can fix) wins over an incidental "SDK not installed".
        self._api_key: Optional[str] = None
        if client is None:
            self._api_key = creds.require("ANTHROPIC_API_KEY", service="anthropic")
            try:
                import anthropic  # noqa: F401  (import guarded; may be absent)
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(
                    "AnthropicMessagesTransport needs the 'anthropic' SDK for a "
                    "live run. Install it with `pip install anthropic`. For "
                    "tests, inject a FakeTransport instead."
                ) from exc

        self._task = task
        self._clock = clock
        self._model = model
        self._system = system_prompt
        self._max_tokens = max_tokens
        self._retry = retry or RetryPolicy(
            max_attempts=4, base_delay=0.5, factor=2.0, max_delay=30.0,
            jitter=0.2)
        self._breaker = breaker
        self._client = client  # injectable for testing the real code path

        self._lock = threading.Lock()
        self._start = clock.now()
        self._last_at = self._start
        self._tokens = 0
        self._tool_uses = 0
        self._status = TransportStatus.RUNNING
        self._detail = ""
        self._output: dict = {}
        self._closed = False
        self._started = False
        self._worker: Optional[threading.Thread] = None

    # -- worker -----------------------------------------------------------
    def _ensure_started(self) -> None:
        if self._started:
            return
        self._started = True
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def _mark_activity(self) -> None:
        with self._lock:
            self._last_at = self._clock.now()

    def _run(self) -> None:
        try:
            resilient_call(self._one_request, clock=self._clock,
                           retry=self._retry, breaker=self._breaker)
        except Exception as exc:  # noqa: BLE001
            with self._lock:
                if self._is_rate_limit(exc):
                    self._status = TransportStatus.RATE_LIMITED
                    self._detail = f"rate limited: {exc}"
                else:
                    self._status = TransportStatus.ERROR
                    self._detail = f"API error after retries: {exc}"

    @staticmethod
    def _is_rate_limit(exc: BaseException) -> bool:
        try:
            import anthropic
            if isinstance(exc, anthropic.RateLimitError):
                return True
        except Exception:  # noqa: BLE001
            pass
        return getattr(exc, "status_code", None) == 429

    def _one_request(self) -> None:
        """One streaming Messages API turn. Raises on API error (so the
        resilience layer can retry); a raised RateLimitError bubbles up to
        :meth:`_run` which maps it to RATE_LIMITED."""
        client = self._client
        if client is None:
            import anthropic
            # BYOK: pass the user-supplied key explicitly (resolved in __init__).
            client = anthropic.Anthropic(api_key=self._api_key)

        messages = [{
            "role": "user",
            "content": self._task.payload.get("prompt", self._task.wave_id),
        }]
        with client.messages.stream(
            model=self._model,
            max_tokens=self._max_tokens,
            system=self._system or None,
            messages=messages,
        ) as stream:
            for event in stream:
                if self._closed:
                    break
                etype = getattr(event, "type", None)
                if etype == "content_block_delta":
                    self._mark_activity()
                    with self._lock:
                        self._tokens += 1
                elif etype == "content_block_start":
                    block = getattr(event, "content_block", None)
                    if getattr(block, "type", None) == "tool_use":
                        self._mark_activity()
                        with self._lock:
                            self._tool_uses += 1
            final = stream.get_final_message()

        with self._lock:
            usage = getattr(final, "usage", None)
            if usage is not None:
                self._tokens = getattr(usage, "output_tokens", self._tokens)
            self._status = TransportStatus.COMPLETED
            self._detail = "agent turn completed"

    # -- Transport interface ---------------------------------------------
    def poll(self) -> TransportPoll:
        self._ensure_started()
        with self._lock:
            return TransportPoll(
                status=self._status,
                last_activity=self._last_at,
                tokens=self._tokens,
                tool_uses=self._tool_uses,
                output=dict(self._output),
                detail=self._detail,
            )

    def close(self) -> None:
        self._closed = True


def default_transport_factory(task: WaveTask, workspace, clock: Clock, *,
                              model: str = DEFAULT_MODEL,
                              system_prompt: str = "",
                              credentials: Optional[Credentials] = None,
                              retry: Optional[RetryPolicy] = None,
                              breaker: Optional[CircuitBreaker] = None
                              ) -> Transport:
    """Build the real transport for a live run.

    Raises a clear :class:`~runtime.credentials.CredentialError` if no
    ``ANTHROPIC_API_KEY`` is configured (BYOK - env-first, then injected config),
    or a clear ``RuntimeError`` if the ``anthropic`` SDK is not installed - the
    honest failure modes in this sandbox. Tests bypass this by passing their own
    FakeTransport factory to :class:`ClaudeSubagentExecutor`.
    """
    return AnthropicMessagesTransport(
        task, clock, model=model, system_prompt=system_prompt,
        credentials=credentials, retry=retry, breaker=breaker)
