"""Contract conformance: ClaudeSubagentExecutor is drop-in for MockExecutor.

Runs a tiny kernel engagement with the fake-backed REAL executor and asserts the
kernel drives it end-to-end - wave-status transitions to COMPLETE and the
metrics ledger records the run - exactly as it does with MockExecutor. This is
the proof that swapping the executor changes nothing the kernel depends on.
"""

import unittest

from runtime.claude_executor import ClaudeSubagentExecutor, FakeEvent, FakeTransport
from runtime.executor import TerminationCause, WaveTask
from runtime.kernel import EngagementSpec, WaveSpec
from runtime.state import WaveState

from .helpers import KernelTestCase


# Per-wave scripted timelines: dense heartbeats then a completion, well inside
# the kernel's heartbeat grace (3s) and hard timeout (30s).
_TIMELINES = {
    "w1": [FakeEvent(1.0, "token", {"tokens": 300}),
           FakeEvent(2.0, "tool_use"),
           FakeEvent(3.0, "token", {"tokens": 200}),
           FakeEvent(4.0, "complete")],
    "w2": [FakeEvent(1.0, "token", {"tokens": 150}),
           FakeEvent(2.0, "token", {"tokens": 150}),
           FakeEvent(3.0, "complete")],
}


def _factory(task, workspace, clock):
    return FakeTransport(clock, _TIMELINES[task.wave_id])


class TestExecutorContract(KernelTestCase):
    def test_real_executor_runs_a_kernel_engagement(self):
        executor = ClaudeSubagentExecutor(transport_factory=_factory)
        kernel = self.make_kernel(executor)
        eng = EngagementSpec("eng-real", [
            WaveSpec("w1", "pm_agent"),
            WaveSpec("w2", "backend_agent", depends_on=["w1"]),
        ])

        result = kernel.run(eng)

        # both waves completed via the real executor's outcome mapping
        self.assertEqual(result.wave_states["w1"], WaveState.COMPLETE.value)
        self.assertEqual(result.wave_states["w2"], WaveState.COMPLETE.value)
        self.assertEqual(result.wave_causes["w1"],
                         TerminationCause.COMPLETED.value)
        self.assertEqual(result.wave_causes["w2"],
                         TerminationCause.COMPLETED.value)

        # wave-status ledger reflects the terminal state machine
        ws = kernel.emitter.read_wave_status()
        self.assertEqual(ws["waves"]["w1"]["state"], "COMPLETE")
        self.assertEqual(ws["waves"]["w2"]["state"], "COMPLETE")

        # metrics ledger recorded a run per wave, with real tokens/tool_uses
        ledger = kernel.emitter.read_metrics()
        by_wave = {r["wave"]: r for r in ledger}
        self.assertEqual(by_wave["w1"]["termination_cause"], "COMPLETED")
        self.assertEqual(by_wave["w1"]["tokens"], 500)
        self.assertEqual(by_wave["w1"]["tool_uses"], 1)
        self.assertEqual(by_wave["w2"]["tokens"], 300)

        # and the executor was actually asked to run both waves (drop-in swap)
        self.assertEqual(executor.submitted_waves, ["w1", "w2"])

    def test_real_executor_death_is_detected_by_kernel(self):
        # a wave whose heartbeats stop and never completes -> kernel marks DEAD
        timelines = {"w1": [FakeEvent(1.0, "token"), FakeEvent(2.0, "token")]}

        def factory(task, workspace, clock):
            return FakeTransport(clock, timelines[task.wave_id])

        executor = ClaudeSubagentExecutor(transport_factory=factory)
        kernel = self.make_kernel(executor)
        eng = EngagementSpec("eng-dead", [WaveSpec("w1", "stuck_agent")])

        result = kernel.run(eng)

        self.assertEqual(result.wave_states["w1"], WaveState.DEAD.value)
        self.assertEqual(result.wave_causes["w1"], TerminationCause.DIED.value)
        integ = kernel.emitter.read_integrity()
        self.assertTrue(any(r["type"] == "DIED" for r in integ))


if __name__ == "__main__":
    unittest.main()
