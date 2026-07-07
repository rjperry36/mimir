"""The pluggable AgentExecutor interface and its implementations.

The kernel MUST NOT hard-depend on Claude / subagent spawning (not available or
testable in this environment). Instead it talks to an :class:`AgentExecutor`:

    handle = executor.submit(task, workspace, clock)
    ...            # kernel polls the handle, watches heartbeats
    result = handle.poll()

Implementations provided here:
  * :class:`MockExecutor`  - REAL, fully-tested. Scriptable to simulate success,
    silent death (heartbeats stop), a hang past the hard timeout, or a hard
    crash. This is what the kernel's logic is proven against.
  * :class:`ClaudeSubagentExecutor` - a documented STUB. The interface it must
    satisfy is fully specified; the wiring to real subagent spawning is future
    work and is clearly marked NotImplemented.

Everything is clock-driven so behaviour is deterministic under ManualClock.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Protocol

from .clock import Clock


class TerminationCause(str, Enum):
    """WHY an agent run stopped. (RSB-04 termination-cause attribution.)

    The whole point: a crash is recorded as ``DIED``, never as ``COMPLETED`` or
    a vague "user-stopped". Each cause is distinguishable in recorded state.
    """

    COMPLETED = "COMPLETED"        # ran to completion, returned a result
    TIMED_OUT = "TIMED_OUT"        # still alive but blew past the hard deadline
    DIED = "DIED"                  # stopped emitting heartbeats (silent death)
    BUDGET_PAUSED = "BUDGET_PAUSED"  # not dispatched / halted: budget ceiling hit
    GATE_BLOCKED = "GATE_BLOCKED"  # blocked because an upstream gate failed
    CANCELLED = "CANCELLED"        # explicitly cancelled (external stop request)


@dataclass
class WaveTask:
    """The unit of work handed to an executor (one wave = one agent run)."""

    wave_id: str
    agent_id: str
    agent_version: str
    payload: dict = field(default_factory=dict)


@dataclass
class AgentResult:
    """What an executor returns when a run finishes.

    ``metrics`` carries the knowable per-run fields the metrics-ledger wants
    (tokens, tool_uses, defects_found, ...). Fields that are genuinely unknown
    are simply absent rather than fabricated.
    """

    cause: TerminationCause
    metrics: dict = field(default_factory=dict)
    output: dict = field(default_factory=dict)
    detail: str = ""


class ExecutionHandle(Protocol):
    """Non-blocking handle the kernel polls while monitoring liveness."""

    def poll(self) -> Optional[AgentResult]:
        """Return the result if finished, else ``None`` (still running)."""

    def last_heartbeat(self) -> float:
        """Clock time of the most recent heartbeat this run emitted."""

    def cancel(self, cause: TerminationCause) -> None:
        """Ask the run to stop (kernel decided it is dead / timed out)."""


class AgentExecutor(Protocol):
    def submit(self, task: WaveTask, workspace, clock: Clock) -> ExecutionHandle:
        ...


# ---------------------------------------------------------------------------
# MockExecutor - REAL, used to prove the kernel's logic.
# ---------------------------------------------------------------------------


@dataclass
class MockScenario:
    """Scripts how one wave behaves, in *simulated* seconds.

    behaviour:
      * ``"complete"``      - heartbeats stay fresh; finishes at ``duration``.
      * ``"die"``           - heartbeats stop at ``die_at``; never finishes
                              (the 41h silent-death case).
      * ``"hang_timeout"``  - heartbeats stay fresh but it never finishes, so
                              the kernel's hard timeout fires (alive-but-stuck).
      * ``"crash"``         - ``poll`` raises immediately, modelling a hard
                              process crash mid-run (used for the resume test).
    """

    behaviour: str = "complete"
    duration: float = 10.0
    die_at: float = 5.0
    heartbeat_interval: float = 1.0
    metrics: dict = field(default_factory=dict)
    output: dict = field(default_factory=dict)


class _MockHandle:
    def __init__(self, scenario: MockScenario, clock: Clock) -> None:
        self._s = scenario
        self._clock = clock
        self._start = clock.now()
        self._cancelled: Optional[TerminationCause] = None

    def _elapsed(self) -> float:
        return self._clock.now() - self._start

    def poll(self) -> Optional[AgentResult]:
        if self._cancelled is not None:
            return None
        s = self._s
        if s.behaviour == "crash":
            raise RuntimeError("simulated hard crash in agent process")
        if s.behaviour == "complete" and self._elapsed() >= s.duration:
            metrics = dict(s.metrics)
            metrics.setdefault("duration_ms", int(s.duration * 1000))
            return AgentResult(
                cause=TerminationCause.COMPLETED,
                metrics=metrics,
                output=dict(s.output),
                detail="run completed",
            )
        # "die" and "hang_timeout" never self-complete.
        return None

    def last_heartbeat(self) -> float:
        s = self._s
        elapsed = self._elapsed()
        if s.behaviour == "die":
            effective = min(elapsed, s.die_at)
        else:
            effective = elapsed
        if s.heartbeat_interval <= 0:
            return self._start
        n = math.floor(effective / s.heartbeat_interval)
        return self._start + n * s.heartbeat_interval

    def cancel(self, cause: TerminationCause) -> None:
        self._cancelled = cause


class MockExecutor:
    """Scriptable executor used to prove the kernel deterministically.

    Also records which waves it was asked to run (``submitted_waves``) so tests
    can assert idempotent resume (completed waves are NOT re-submitted).
    """

    def __init__(self, scenarios: Optional[Dict[str, MockScenario]] = None,
                 default: Optional[MockScenario] = None) -> None:
        self._scenarios = scenarios or {}
        self._default = default or MockScenario()
        self.submitted_waves: list[str] = []

    def scenario_for(self, wave_id: str) -> MockScenario:
        return self._scenarios.get(wave_id, self._default)

    def submit(self, task: WaveTask, workspace, clock: Clock) -> _MockHandle:
        self.submitted_waves.append(task.wave_id)
        return _MockHandle(self.scenario_for(task.wave_id), clock)


# ---------------------------------------------------------------------------
# ClaudeSubagentExecutor - REAL adapter (implemented in claude_executor.py).
# ---------------------------------------------------------------------------
#
# The real adapter satisfies the exact AgentExecutor / ExecutionHandle contract
# above:
#
#   submit(task, workspace, clock) -> handle   (non-blocking)
#   handle.last_heartbeat() -> float           (clock time of last token/tool event)
#   handle.poll() -> AgentResult | None         (COMPLETED / BUDGET_PAUSED / DIED)
#   handle.cancel(cause) -> None                (stops the transport)
#
# It runs a wave as a real Claude agent turn behind a swappable Transport:
#   * FakeTransport         - deterministic, clock-driven (what the tests prove);
#   * AnthropicMessagesTransport - the real Messages-API streaming tool-use loop,
#                             COMPLETE code but unproven without credentials+SDK.
#
# The import lives at the END of this module so the shared types above
# (AgentResult, TerminationCause, WaveTask, ExecutionHandle) are already bound
# when claude_executor imports them back - avoiding a circular-import failure.
from .claude_executor import (  # noqa: E402  (intentional late import)
    AnthropicMessagesTransport,
    ClaudeSubagentExecutor,
    FakeEvent,
    FakeTransport,
    Transport,
    TransportPoll,
    TransportStatus,
    default_transport_factory,
)
