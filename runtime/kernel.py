"""The deterministic runtime kernel.

Plain Python plumbing that runs BETWEEN waves - the layer the ASA said must be
deterministic software, not agents. It sequences waves, monitors liveness, fires
gates, guards budget, checkpoints, isolates workspaces, attributes termination
causes, and emits the dashboard's structured state.

The only non-deterministic part (actually running an agent) is delegated to a
pluggable :class:`~runtime.executor.AgentExecutor`. Everything here is proven
against the :class:`~runtime.executor.MockExecutor`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional

from .budget import BudgetGuard
from .checkpoint import Checkpointer
from .clock import Clock, MonotonicClock
from .executor import (
    AgentExecutor,
    AgentResult,
    TerminationCause,
    WaveTask,
)
from .gates import Gate, GateResult, run_gate
from .isolation import WorkspaceManager
from .state import StateEmitter, WaveState


@dataclass
class WaveSpec:
    """One wave = one agent run, with its dependencies and optional gate."""

    wave_id: str
    agent_id: str
    agent_version: str = "v1.0.0"
    depends_on: List[str] = field(default_factory=list)
    gate: Optional[Gate] = None
    est_cost: float = 1.0
    needs_port: bool = False
    human_gate: bool = False


@dataclass
class EngagementSpec:
    engagement_id: str
    waves: List[WaveSpec]


class RunStatus(str, Enum):
    COMPLETED = "COMPLETED"          # every wave COMPLETE
    PAUSED = "PAUSED"               # halted at a budget ceiling, resumable
    AWAITING_APPROVAL = "AWAITING_APPROVAL"  # a human gate is pending
    DEGRADED = "DEGRADED"          # ran, but some wave died/timed out/gate-blocked


@dataclass
class RunResult:
    status: RunStatus
    wave_states: Dict[str, str]
    wave_causes: Dict[str, str]
    detail: str = ""


class KernelConfig:
    """Timing knobs (in the clock's seconds). Defaults are generous so real
    runs never false-positive; tests inject a ManualClock and drive them."""

    def __init__(self, heartbeat_grace: float = 3.0, wave_timeout: float = 120.0,
                 poll_interval: float = 0.5, max_iters: int = 100_000):
        self.heartbeat_grace = heartbeat_grace
        self.wave_timeout = wave_timeout
        self.poll_interval = poll_interval
        self.max_iters = max_iters


class Kernel:
    def __init__(self, engagement_root: str, executor: AgentExecutor,
                 clock: Optional[Clock] = None,
                 config: Optional[KernelConfig] = None,
                 approver: Optional[Callable[[WaveSpec], bool]] = None):
        self.root = engagement_root
        self.executor = executor
        self.clock = clock or MonotonicClock()
        self.config = config or KernelConfig()
        self.approver = approver

        self.state_dir = os.path.join(engagement_root, "runtime-state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.emitter = StateEmitter(self.state_dir)
        self.checkpoint = Checkpointer(os.path.join(self.state_dir, "checkpoint.yaml"))
        self.workspaces = WorkspaceManager(os.path.join(engagement_root, "workspaces"))

        # live view of the run
        self._states: Dict[str, WaveState] = {}
        self._causes: Dict[str, str] = {}
        self._gate_pass: Dict[str, bool] = {}
        self._wave_meta: Dict[str, dict] = {}
        self._decisions: List[dict] = []

    # ------------------------------------------------------------------
    # public entrypoint
    # ------------------------------------------------------------------
    def run(self, engagement: EngagementSpec,
            budget: Optional[BudgetGuard] = None) -> RunResult:
        budget = budget or BudgetGuard(ceiling=float("inf"))
        # resume: adopt any budget already spent in a prior (paused/crashed) run
        budget.consumed = max(budget.consumed, self.checkpoint.budget_consumed)

        order = self._topo_sort(engagement.waves)
        by_id = {w.wave_id: w for w in engagement.waves}

        # seed live view from checkpoint (idempotent resume)
        for w in engagement.waves:
            if self.checkpoint.is_complete(w.wave_id):
                self._states[w.wave_id] = WaveState.COMPLETE
                self._gate_pass[w.wave_id] = True
                self._causes[w.wave_id] = TerminationCause.COMPLETED.value
            else:
                self._states[w.wave_id] = WaveState.PENDING

        self._emit(engagement.engagement_id)

        for wave in order:
            if self.checkpoint.is_complete(wave.wave_id):
                continue  # RSB-01 checkpointing: never re-run a completed wave

            # dependency / upstream-gate release check
            blocked_by = self._blocking_dependency(wave, by_id)
            if blocked_by is not None:
                self._states[wave.wave_id] = WaveState.BLOCKED
                # attribute WHY it is blocked, accurately: a failed upstream
                # gate -> GATE_BLOCKED; a dead/timed-out upstream keeps its own
                # cause so the reason is never misreported.
                dep_state = self._states.get(blocked_by)
                if dep_state == WaveState.GATE_BLOCKED:
                    self._causes[wave.wave_id] = TerminationCause.GATE_BLOCKED.value
                else:
                    self._causes[wave.wave_id] = (
                        f"BLOCKED_BY:{blocked_by}:{dep_state.value if dep_state else 'PENDING'}")
                self._wave_meta[wave.wave_id] = {"blocked_by": blocked_by}
                self._emit(engagement.engagement_id)
                continue

            # RSB-02 budget: pre-dispatch quota check -> graceful pause
            if not budget.can_afford(wave.est_cost):
                self._pause_for_budget(engagement, wave, budget)
                return self._finish(engagement, RunStatus.PAUSED,
                                    f"budget ceiling reached before {wave.wave_id}")

            # human gate -> decisions-queue
            if wave.human_gate and not self._approve(wave):
                self._states[wave.wave_id] = WaveState.AWAITING_APPROVAL
                self._enqueue_decision(engagement, wave)
                self._emit(engagement.engagement_id)
                continue

            self._dispatch_wave(engagement, wave, budget)

        return self._finish(engagement, self._overall_status(engagement),
                            "run finished")

    # ------------------------------------------------------------------
    # per-wave dispatch + the liveness monitor loop (RSB-01)
    # ------------------------------------------------------------------
    def _dispatch_wave(self, engagement: EngagementSpec, wave: WaveSpec,
                       budget: BudgetGuard) -> None:
        run_id = f"{engagement.engagement_id}--{wave.wave_id}"
        workspace = self.workspaces.allocate(run_id, needs_port=wave.needs_port)
        task = WaveTask(wave_id=wave.wave_id, agent_id=wave.agent_id,
                        agent_version=wave.agent_version)

        self._states[wave.wave_id] = WaveState.RUNNING
        self._wave_meta[wave.wave_id] = {
            "workspace": workspace.path, "port": workspace.port}
        self._emit(engagement.engagement_id)

        result = self._monitor(task, workspace)

        # budget is spent whether or not the wave succeeded
        budget.charge(wave.est_cost)
        self.checkpoint.set_budget_consumed(budget.consumed)

        self._record_metrics(engagement, wave, workspace, result)
        self._apply_result(engagement, wave, result)
        self.workspaces.release(workspace)
        self._emit(engagement.engagement_id)

    def _monitor(self, task: WaveTask, workspace) -> AgentResult:
        """Poll the executor, watching heartbeats and the hard deadline.

        Returns an AgentResult whose cause is COMPLETED, DIED, or TIMED_OUT.
        (A genuine crash - poll() raising - propagates out, modelling a real
        process death; the checkpoint of prior waves is already on disk.)
        """
        handle = self.executor.submit(task, workspace, self.clock)
        start = self.clock.now()
        deadline = start + self.config.wave_timeout

        for _ in range(self.config.max_iters):
            result = handle.poll()
            if result is not None:
                return result

            now = self.clock.now()
            silence = now - handle.last_heartbeat()
            if silence > self.config.heartbeat_grace:
                handle.cancel(TerminationCause.DIED)
                return AgentResult(
                    cause=TerminationCause.DIED,
                    detail=f"no heartbeat for {silence:.1f}s (grace "
                           f"{self.config.heartbeat_grace}s)")
            if now >= deadline:
                handle.cancel(TerminationCause.TIMED_OUT)
                return AgentResult(
                    cause=TerminationCause.TIMED_OUT,
                    detail=f"exceeded hard timeout of {self.config.wave_timeout}s")

            self.clock.sleep(self.config.poll_interval)

        # should never happen with sane config; fail safe as TIMED_OUT
        handle.cancel(TerminationCause.TIMED_OUT)
        return AgentResult(cause=TerminationCause.TIMED_OUT,
                           detail="monitor exceeded max iterations")

    # ------------------------------------------------------------------
    # applying a wave result (gate-runner + termination attribution)
    # ------------------------------------------------------------------
    def _apply_result(self, engagement: EngagementSpec, wave: WaveSpec,
                      result: AgentResult) -> None:
        self._causes[wave.wave_id] = result.cause.value

        if result.cause is not TerminationCause.COMPLETED:
            # DIED / TIMED_OUT -> record in integrity register, block dependents
            state = (WaveState.DEAD if result.cause is TerminationCause.DIED
                     else WaveState.TIMED_OUT)
            self._states[wave.wave_id] = state
            self.checkpoint.record_wave(wave.wave_id, state.value,
                                        result={"cause": result.cause.value})
            self.emitter.append_integrity({
                "engagement": engagement.engagement_id,
                "type": result.cause.value,
                "wave": wave.wave_id,
                "agent": wave.agent_id,
                "severity": "CRITICAL" if result.cause is TerminationCause.DIED
                            else "HIGH",
                "detail": result.detail,
            })
            return

        # COMPLETED -> run the gate (if any) deterministically
        gate: Optional[Gate] = wave.gate
        if gate is None:
            self._states[wave.wave_id] = WaveState.COMPLETE
            self._gate_pass[wave.wave_id] = True
            self.checkpoint.record_wave(wave.wave_id, WaveState.COMPLETE.value,
                                        result=result.metrics)
            return

        gr: GateResult = run_gate(gate, result)
        if gr.passed:
            self._states[wave.wave_id] = WaveState.COMPLETE
            self._gate_pass[wave.wave_id] = True
            self.checkpoint.record_wave(
                wave.wave_id, WaveState.COMPLETE.value, result=result.metrics,
                gate={"gate_id": gr.gate_id, "passed": True})
        else:
            # gate failed: wave does NOT release its dependents; recorded.
            self._states[wave.wave_id] = WaveState.GATE_BLOCKED
            self._gate_pass[wave.wave_id] = False
            self._causes[wave.wave_id] = TerminationCause.GATE_BLOCKED.value
            self.checkpoint.record_wave(
                wave.wave_id, WaveState.GATE_BLOCKED.value, result=result.metrics,
                gate={"gate_id": gr.gate_id, "passed": False})
            self.emitter.append_integrity({
                "engagement": engagement.engagement_id,
                "type": "GATE_FAILURE",
                "wave": wave.wave_id,
                "agent": wave.agent_id,
                "gate": gr.gate_id,
                "severity": "HIGH",
                "detail": gr.detail,
            })

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _blocking_dependency(self, wave: WaveSpec,
                             by_id: Dict[str, WaveSpec]) -> Optional[str]:
        """Return the id of a dependency that fails to release this wave."""
        for dep in wave.depends_on:
            if self._states.get(dep) != WaveState.COMPLETE:
                return dep
            if not self._gate_pass.get(dep, False):
                return dep
        return None

    def _pause_for_budget(self, engagement: EngagementSpec, wave: WaveSpec,
                          budget: BudgetGuard) -> None:
        self._states[wave.wave_id] = WaveState.PAUSED
        self._causes[wave.wave_id] = TerminationCause.BUDGET_PAUSED.value
        self.checkpoint.set_budget_consumed(budget.consumed)
        self.emitter.append_integrity({
            "engagement": engagement.engagement_id,
            "type": TerminationCause.BUDGET_PAUSED.value,
            "wave": wave.wave_id,
            "agent": wave.agent_id,
            "severity": "MEDIUM",
            "detail": f"estimate {wave.est_cost} would breach ceiling "
                      f"{budget.ceiling} (consumed {budget.consumed}); "
                      f"paused with resumable checkpoint",
        })
        self._emit(engagement.engagement_id)

    def _approve(self, wave: WaveSpec) -> bool:
        if self.approver is None:
            return False
        return bool(self.approver(wave))

    def _enqueue_decision(self, engagement: EngagementSpec, wave: WaveSpec) -> None:
        item = {
            "wave": wave.wave_id,
            "agent": wave.agent_id,
            "type": "HUMAN_GATE",
            "prompt": f"Approve wave {wave.wave_id} ({wave.agent_id})?",
            "status": "PENDING",
        }
        if item not in self._decisions:
            self._decisions.append(item)
        self.emitter.write_decisions_queue(engagement.engagement_id, self._decisions)

    def _record_metrics(self, engagement: EngagementSpec, wave: WaveSpec,
                        workspace, result: AgentResult) -> None:
        m = dict(result.metrics)
        self.emitter.append_metrics({
            "engagement": engagement.engagement_id,
            "wave": wave.wave_id,
            "agent_id": wave.agent_id,
            "agent_version": wave.agent_version,
            "termination_cause": result.cause.value,
            "workspace": os.path.basename(workspace.path),
            "port": workspace.port,
            "tokens": m.get("tokens"),
            "duration_ms": m.get("duration_ms"),
            "tool_uses": m.get("tool_uses"),
            "gates_passed": m.get("gates_passed"),
            "gates_failed": m.get("gates_failed"),
            "defects_found": m.get("defects_found"),
            "defects_attributed": m.get("defects_attributed"),
            "rework_count": m.get("rework_count"),
        })

    def _emit(self, engagement_id: str) -> None:
        waves = {}
        for wid, state in self._states.items():
            waves[wid] = {
                "state": state.value,
                "termination_cause": self._causes.get(wid),
                **self._wave_meta.get(wid, {}),
            }
        self.emitter.write_wave_status(engagement_id, waves)

    def _overall_status(self, engagement: EngagementSpec) -> RunStatus:
        states = set(self._states.values())
        if WaveState.AWAITING_APPROVAL in states:
            return RunStatus.AWAITING_APPROVAL
        bad = {WaveState.DEAD, WaveState.TIMED_OUT, WaveState.GATE_BLOCKED,
               WaveState.BLOCKED, WaveState.PAUSED}
        if states & bad:
            return RunStatus.DEGRADED
        return RunStatus.COMPLETED

    def _finish(self, engagement: EngagementSpec, status: RunStatus,
                detail: str) -> RunResult:
        self._emit(engagement.engagement_id)
        return RunResult(
            status=status,
            wave_states={k: v.value for k, v in self._states.items()},
            wave_causes=dict(self._causes),
            detail=detail,
        )

    @staticmethod
    def _topo_sort(waves: List[WaveSpec]) -> List[WaveSpec]:
        """Stable topological sort (input order as tiebreak). Raises on cycle."""
        by_id = {w.wave_id: w for w in waves}
        indeg = {w.wave_id: 0 for w in waves}
        for w in waves:
            for dep in w.depends_on:
                if dep in by_id:
                    indeg[w.wave_id] += 1
        order: List[WaveSpec] = []
        ready = [w for w in waves if indeg[w.wave_id] == 0]
        while ready:
            w = ready.pop(0)
            order.append(w)
            for other in waves:
                if w.wave_id in other.depends_on and other not in order:
                    indeg[other.wave_id] -= 1
                    if indeg[other.wave_id] == 0:
                        ready.append(other)
        if len(order) != len(waves):
            raise ValueError("dependency cycle detected in engagement waves")
        return order
