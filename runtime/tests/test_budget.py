"""RSB-02 budget awareness: pause gracefully at the ceiling, then resume."""

from runtime.budget import BudgetGuard
from runtime.executor import MockExecutor, MockScenario, TerminationCause
from runtime.kernel import EngagementSpec, RunStatus, WaveSpec
from runtime.state import WaveState

from .helpers import KernelTestCase


def _eng():
    return EngagementSpec("eng-budget", [
        WaveSpec("w1", "a1", est_cost=10),
        WaveSpec("w2", "a2", depends_on=["w1"], est_cost=10),
        WaveSpec("w3", "a3", depends_on=["w2"], est_cost=10),
    ])


class TestBudget(KernelTestCase):
    def test_pause_at_ceiling_then_resume(self):
        # ceiling 25 affords w1 (10) + w2 (20) but not w3 (would be 30).
        exec1 = MockExecutor(
            default=MockScenario(behaviour="complete", duration=4.0))
        kernel1 = self.make_kernel(exec1, subdir="shared")
        res1 = kernel1.run(_eng(), budget=BudgetGuard(ceiling=25))

        self.assertEqual(res1.status, RunStatus.PAUSED)
        self.assertEqual(res1.wave_states["w3"], WaveState.PAUSED.value)
        self.assertEqual(res1.wave_causes["w3"],
                         TerminationCause.BUDGET_PAUSED.value)
        # w3 was never dispatched (paused BEFORE spending, not mid-wave)
        self.assertNotIn("w3", exec1.submitted_waves)
        # resumable checkpoint recorded the consumed budget
        self.assertEqual(kernel1.checkpoint.budget_consumed, 20.0)
        # the pause is in the integrity register
        integ = kernel1.emitter.read_integrity()
        self.assertTrue(any(r["type"] == "BUDGET_PAUSED" for r in integ))

        # Resume: fresh kernel, SAME state dir, higher ceiling.
        exec2 = MockExecutor(
            default=MockScenario(behaviour="complete", duration=4.0))
        kernel2 = self.make_kernel(exec2, subdir="shared")
        res2 = kernel2.run(_eng(), budget=BudgetGuard(ceiling=1000))

        self.assertEqual(res2.status, RunStatus.COMPLETED)
        self.assertEqual(exec2.submitted_waves, ["w3"])  # w1/w2 not re-run
        self.assertEqual(res2.wave_states["w3"], WaveState.COMPLETE.value)
