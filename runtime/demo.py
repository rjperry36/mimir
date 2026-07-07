"""Runnable demo: `python -m runtime.demo`

Runs a small toy engagement through the kernel with the MockExecutor so a human
can SEE the kernel work. It deliberately includes:

  * a wave that DIES (heartbeats stop) -> detected as DEAD, not left pending;
  * a wave whose GATE FAILS -> its dependent is blocked and the failure recorded;
  * normal waves that complete cleanly.

It then prints the resulting structured state (the four dashboard ledgers).

The demo uses a ManualClock so it runs instantly and deterministically - no real
waiting - while exercising the exact same kernel code path a real run would.
"""

from __future__ import annotations

import json
import shutil
import tempfile

import yaml

from .budget import BudgetGuard
from .clock import ManualClock
from .executor import MockExecutor, MockScenario
from .gates import Gate
from .kernel import EngagementSpec, Kernel, KernelConfig, WaveSpec


def _fail_gate(_result):
    return False, "seeded gate failure (e.g. CI security gates not wired)"


def build_engagement() -> EngagementSpec:
    return EngagementSpec(
        engagement_id="demo-engagement",
        waves=[
            WaveSpec("w1-plan", "delivery_project_manager_agent",
                     est_cost=5),
            WaveSpec("w2-backend", "engineering_backend_agent",
                     depends_on=["w1-plan"], est_cost=5),
            # w3 completes but its gate FAILS -> w4 must not release
            WaveSpec("w3-security", "security_infosec_manager_agent",
                     depends_on=["w2-backend"], est_cost=5,
                     gate=Gate("security-gate", _fail_gate,
                               description="CI security gates wired?")),
            WaveSpec("w4-release", "roster_appdev_orchestrator_agent",
                     depends_on=["w3-security"], est_cost=5),
        ],
    )


def build_engagement_with_death() -> EngagementSpec:
    return EngagementSpec(
        engagement_id="demo-death",
        waves=[
            WaveSpec("w1-plan", "delivery_project_manager_agent", est_cost=5),
            # w2 dies silently (the 41h incident, in miniature)
            WaveSpec("w2-backend", "engineering_backend_agent",
                     depends_on=["w1-plan"], est_cost=5),
            WaveSpec("w3-frontend", "engineering_frontend_agent",
                     depends_on=["w2-backend"], est_cost=5),
        ],
    )


def _pp(title: str, obj) -> None:
    print(f"\n=== {title} ===")
    if isinstance(obj, list):
        for row in obj:
            print(json.dumps(row))
    else:
        print(yaml.safe_dump(obj, sort_keys=False).rstrip())


def main() -> None:
    workdir = tempfile.mkdtemp(prefix="runtime-demo-")
    try:
        clock = ManualClock()
        cfg = KernelConfig(heartbeat_grace=3.0, wave_timeout=60.0,
                           poll_interval=0.5)

        # --- Engagement A: a gate that blocks -------------------------
        exec_a = MockExecutor(default=MockScenario(behaviour="complete",
                                                   duration=4.0,
                                                   metrics={"tokens": 1800,
                                                            "tool_uses": 12}))
        kernel_a = Kernel(f"{workdir}/A", exec_a, clock=clock, config=cfg)
        eng_a = build_engagement()
        res_a = kernel_a.run(eng_a, budget=BudgetGuard(ceiling=1000))
        print("### DEMO A - gate-block ###")
        print(f"run status: {res_a.status.value}")
        _pp("wave-status.yaml", kernel_a.emitter.read_wave_status())
        _pp("integrity-register.jsonl", kernel_a.emitter.read_integrity())

        # --- Engagement B: a wave that dies ---------------------------
        clock_b = ManualClock()
        exec_b = MockExecutor(
            scenarios={
                "w2-backend": MockScenario(behaviour="die", die_at=5.0,
                                           heartbeat_interval=1.0),
            },
            default=MockScenario(behaviour="complete", duration=4.0,
                                 metrics={"tokens": 1500, "tool_uses": 9}))
        kernel_b = Kernel(f"{workdir}/B", exec_b, clock=clock_b, config=cfg)
        eng_b = build_engagement_with_death()
        res_b = kernel_b.run(eng_b, budget=BudgetGuard(ceiling=1000))
        print("\n### DEMO B - silent death detection ###")
        print(f"run status: {res_b.status.value}")
        _pp("wave-status.yaml", kernel_b.emitter.read_wave_status())
        _pp("integrity-register.jsonl", kernel_b.emitter.read_integrity())
        _pp("metrics-ledger.jsonl", kernel_b.emitter.read_metrics())

        print("\nInterpretation:")
        print(" - DEMO A: w3-security COMPLETED but its gate FAILED -> "
              "w3 GATE_BLOCKED, w4-release BLOCKED (cause GATE_BLOCKED), "
              "recorded in the integrity register. Nothing silently proceeded.")
        print(" - DEMO B: w2-backend stopped emitting heartbeats -> kernel "
              "marked it DEAD (not pending), recorded it CRITICAL, and did not "
              "silently release w3-frontend. This is the 41h-silent-death fix.")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
