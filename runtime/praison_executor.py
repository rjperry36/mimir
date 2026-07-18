"""PraisonAI executor adapter — spike proof for the buy-vs-build decision.

Runs a wave as a PraisonAI (``praisonaiagents``) agent turn behind the SAME
``Transport`` seam the Claude adapter uses, so the kernel-proven handle and
outcome mapping in :mod:`runtime.claude_executor` are reused verbatim. This is
the point of the spike: PraisonAI slots in as an execution backend UNDER the
deterministic kernel — it does not replace the kernel, the gates, or any
constitutional control.

Honest scope
------------
Mirrors the Claude adapter's posture exactly:

* The praison-specific code path is proven against an injectable *runner*
  seam (:data:`PraisonRunner`) — deterministic tests inject a scripted runner;
  no API key or network is required.
* :func:`default_praison_runner` is the REAL runner: it maps a WaveTask onto
  a ``praisonaiagents.Agent`` and executes the turn, heartbeating on streamed
  content / tool-call display events. It is complete, documented code, but a
  LIVE run is not proven in this sandbox (needs a configured LLM key).
* Token counts are NOT reliably reported by ``praisonaiagents``'s public
  return value; per the framework's non-fabrication rule the ``tokens`` metric
  is simply absent rather than invented. ``tool_uses`` is counted from
  ``tool_call`` display events.
* PraisonAI has no hard-cancellation API: ``close()`` is cooperative — the
  result of an already-running turn is discarded and the worker thread is
  orphaned until the turn ends. The kernel's timeout/death handling is
  unaffected (it acts on heartbeats, which stop being recorded on close).

BYOK: the key is resolved through :class:`runtime.credentials.Credentials`
(env-first, injected config second, never committed) and passed explicitly to
the Agent. The env var is configurable because PraisonAI is multi-provider
(``OPENAI_API_KEY``, ``ANTHROPIC_API_KEY``, ...).
"""

from __future__ import annotations

import threading
from typing import Callable, List, Optional

from .claude_executor import (
    Transport,
    TransportPoll,
    TransportStatus,
    _SubagentHandle,  # deliberate reuse: the handle is kernel-proven
)
from .clock import Clock
from .credentials import Credentials
from .executor import ExecutionHandle, WaveTask

# Default LLM string handed to praisonaiagents. Provider-prefixed strings
# (e.g. "anthropic/claude-opus-4-8") route via litellm when installed; plain
# model names use the bundled OpenAI-compatible client. Deployment-specific —
# override per executor or per agent payload.
DEFAULT_LLM = "anthropic/claude-opus-4-8"
DEFAULT_API_KEY_ENV = "ANTHROPIC_API_KEY"

Heartbeat = Callable[[], None]
ToolUse = Callable[[], None]

# The injectable seam this adapter is proven against: a callable that BLOCKS
# until the agent turn is done, invoking heartbeat()/tool_use() as activity
# happens, and returns the turn's output dict. Raises on failure; an exception
# with status_code 429 (or a rate-limit message) maps to RATE_LIMITED.
PraisonRunner = Callable[[WaveTask, Heartbeat, ToolUse], dict]


def _is_rate_limit(exc: BaseException) -> bool:
    if getattr(exc, "status_code", None) == 429:
        return True
    return "rate limit" in str(exc).lower() or "429" in str(exc)


def build_praison_agent(task: WaveTask, *, llm: str = DEFAULT_LLM,
                        api_key: Optional[str] = None):
    """Map a mimir WaveTask onto a ``praisonaiagents.Agent``.

    The payload's ``agent`` dict carries the mimir agent-definition fields —
    they translate one-to-one (name/role/goal/backstory/instructions), which
    is the YAML-compatibility claim the spike set out to verify.

    Tool wiring is deployment-specific and intentionally left to the
    integrator (same stance as the Claude adapter): the transport contract and
    kernel correctness do not depend on it.
    """
    try:
        from praisonaiagents import Agent
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "default_praison_runner needs the 'praisonaiagents' package for a "
            "live run. Install it with `pip install praisonaiagents`. For "
            "tests, inject a scripted PraisonRunner instead."
        ) from exc

    spec = task.payload.get("agent", {})
    return Agent(
        name=spec.get("name", task.agent_id),
        role=spec.get("role", task.agent_id),
        goal=spec.get("goal", ""),
        backstory=spec.get("backstory", ""),
        instructions=spec.get("instructions") or None,
        llm=spec.get("llm", llm),
        api_key=api_key,
    )


def default_praison_runner(task: WaveTask, heartbeat: Heartbeat,
                           tool_use: ToolUse, *,
                           llm: str = DEFAULT_LLM,
                           credentials: Optional[Credentials] = None,
                           api_key_env: str = DEFAULT_API_KEY_ENV) -> dict:
    """The REAL runner: one blocking PraisonAI agent turn.

    Heartbeats on ``llm_content`` (streamed content) and ``tool_call`` display
    events so the kernel's silent-death detector works against real latency.
    Display callbacks are process-global in praisonaiagents; the registered
    callback is disarmed in ``finally`` so it cannot outlive the turn.
    """
    creds = credentials or Credentials()
    # BYOK: resolve the user's key FIRST so the fixable missing-key error wins
    # over an incidental import error (same ordering as the Claude adapter).
    api_key = creds.require(api_key_env, service="praisonai-llm")

    agent = build_praison_agent(task, llm=llm, api_key=api_key)

    from praisonaiagents.main import register_display_callback

    armed = {"on": True}

    def _on_content(*_args, **_kwargs) -> None:
        if armed["on"]:
            heartbeat()

    def _on_tool(*_args, **_kwargs) -> None:
        if armed["on"]:
            heartbeat()
            tool_use()

    try:
        register_display_callback("llm_content", _on_content)
        register_display_callback("tool_call", _on_tool)
    except Exception:  # noqa: BLE001 - degraded heartbeat granularity, not fatal
        pass

    try:
        prompt = task.payload.get("prompt", task.wave_id)
        response = agent.start(prompt)
        if response is not None and not isinstance(response, str):
            # generator (stream=True) or other shape — drain to a string
            try:
                response = "".join(str(chunk) for chunk in response)
            except TypeError:
                response = str(response)
        return {"response": response or ""}
    finally:
        armed["on"] = False


class PraisonAgentTransport(Transport):
    """Thread-backed transport running one blocking :data:`PraisonRunner`.

    Same shape as ``AnthropicMessagesTransport``: a worker thread executes the
    turn; ``poll()`` returns a cumulative snapshot; all event times are read
    from the injected clock so the kernel's liveness logic sees a consistent
    timeline.
    """

    def __init__(self, task: WaveTask, clock: Clock, runner: PraisonRunner) -> None:
        self._task = task
        self._clock = clock
        self._runner = runner
        self._lock = threading.Lock()
        self._start = clock.now()
        self._last_at = self._start
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

    def _heartbeat(self) -> None:
        with self._lock:
            if not self._closed:
                self._last_at = self._clock.now()

    def _tool_use(self) -> None:
        with self._lock:
            if not self._closed:
                self._tool_uses += 1

    def _run(self) -> None:
        try:
            output = self._runner(self._task, self._heartbeat, self._tool_use)
            with self._lock:
                if not self._closed:
                    self._status = TransportStatus.COMPLETED
                    self._last_at = self._clock.now()
                    self._output = dict(output or {})
                    self._detail = "praison agent turn completed"
        except Exception as exc:  # noqa: BLE001
            with self._lock:
                if self._closed:
                    return
                self._last_at = self._clock.now()
                if _is_rate_limit(exc):
                    self._status = TransportStatus.RATE_LIMITED
                    self._detail = f"rate limited: {exc}"
                else:
                    self._status = TransportStatus.ERROR
                    self._detail = f"praison agent error: {exc}"

    # -- Transport contract ----------------------------------------------
    def poll(self) -> TransportPoll:
        self._ensure_started()
        with self._lock:
            return TransportPoll(
                status=self._status,
                last_activity=self._last_at,
                tokens=0,  # not reported by praisonaiagents — absent, not invented
                tool_uses=self._tool_uses,
                output=dict(self._output),
                detail=self._detail,
            )

    def close(self) -> None:
        # Cooperative: no hard-cancel API in praisonaiagents. Discard any
        # further activity/result; the orphaned turn ends on its own.
        with self._lock:
            self._closed = True


class PraisonAIExecutor:
    """Drop-in ``AgentExecutor`` running waves as PraisonAI agent turns.

    Same contract and same construction pattern as ``ClaudeSubagentExecutor``:
    inject a ``runner`` (or a full ``transport_factory``) in tests; leave the
    defaults for a real run — which requires ``praisonaiagents`` plus a key
    resolvable from ``api_key_env`` (BYOK), and fails loud if either is absent.
    """

    def __init__(self, runner: Optional[PraisonRunner] = None, *,
                 llm: str = DEFAULT_LLM,
                 api_key_env: str = DEFAULT_API_KEY_ENV,
                 credentials: Optional[Credentials] = None) -> None:
        self.llm = llm
        self.api_key_env = api_key_env
        self.credentials = credentials or Credentials()
        self._runner = runner
        self.submitted_waves: List[str] = []

    def _default_runner(self) -> PraisonRunner:
        def run(task: WaveTask, heartbeat: Heartbeat, tool_use: ToolUse) -> dict:
            return default_praison_runner(
                task, heartbeat, tool_use, llm=self.llm,
                credentials=self.credentials, api_key_env=self.api_key_env)
        return run

    def submit(self, task: WaveTask, workspace, clock: Clock) -> ExecutionHandle:
        self.submitted_waves.append(task.wave_id)
        runner = self._runner or self._default_runner()
        transport = PraisonAgentTransport(task, clock, runner)
        return _SubagentHandle(transport, clock, task)
