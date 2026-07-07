"""Gate-runner: gates fire deterministically between waves."""

from runtime.executor import MockExecutor, MockScenario, TerminationCause
from runtime.gates import Gate
from runtime.kernel import EngagementSpec, WaveSpec
from runtime.state import WaveState

from .helpers import KernelTestCase


def _pass_gate(_r):
    return True, "ok"


def _fail_gate(_r):
    return False, "security gates not wired"


class TestGateRunner(KernelTestCase):
    def _engagement(self, gate):
        return EngagementSpec("eng-gate", [
            WaveSpec("w1", "security_agent", gate=gate),
            WaveSpec("w2", "release_agent", depends_on=["w1"]),
        ])

    def test_failed_gate_blocks_dependent_and_is_recorded(self):
        executor = MockExecutor(
            default=MockScenario(behaviour="complete", duration=4.0))
        kernel = self.make_kernel(executor)
        result = kernel.run(self._engagement(Gate("g-sec", _fail_gate)))

        # gated wave completed but its gate failed -> GATE_BLOCKED
        self.assertEqual(result.wave_states["w1"], WaveState.GATE_BLOCKED.value)
        # dependent did NOT release
        self.assertEqual(result.wave_states["w2"], WaveState.BLOCKED.value)
        self.assertEqual(result.wave_causes["w2"],
                         TerminationCause.GATE_BLOCKED.value)
        # w2 was never dispatched
        self.assertNotIn("w2", executor.submitted_waves)
        # integrity register records the gate failure
        integ = kernel.emitter.read_integrity()
        gate_fails = [r for r in integ if r["type"] == "GATE_FAILURE"]
        self.assertEqual(len(gate_fails), 1)
        self.assertEqual(gate_fails[0]["gate"], "g-sec")

    def test_passed_gate_releases_dependent(self):
        executor = MockExecutor(
            default=MockScenario(behaviour="complete", duration=4.0))
        kernel = self.make_kernel(executor)
        result = kernel.run(self._engagement(Gate("g-sec", _pass_gate)))

        self.assertEqual(result.wave_states["w1"], WaveState.COMPLETE.value)
        self.assertEqual(result.wave_states["w2"], WaveState.COMPLETE.value)
        self.assertIn("w2", executor.submitted_waves)
        # no gate failures recorded
        integ = kernel.emitter.read_integrity()
        self.assertFalse([r for r in integ if r["type"] == "GATE_FAILURE"])
