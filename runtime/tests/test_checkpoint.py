"""RSB-01 checkpointing: a killed/restarted run resumes without redoing waves."""

from runtime.executor import MockExecutor, MockScenario
from runtime.kernel import EngagementSpec, WaveSpec
from runtime.state import WaveState

from .helpers import KernelTestCase


def _eng():
    return EngagementSpec("eng-resume", [
        WaveSpec("w1", "pm_agent"),
        WaveSpec("w2", "ba_agent", depends_on=["w1"]),
        WaveSpec("w3", "backend_agent", depends_on=["w2"]),
    ])


class TestCheckpointResume(KernelTestCase):
    def test_crash_then_resume_is_idempotent(self):
        # Run 1: w1, w2 complete; w3 hard-crashes (poll raises) mid-run.
        exec1 = MockExecutor(
            scenarios={"w3": MockScenario(behaviour="crash")},
            default=MockScenario(behaviour="complete", duration=4.0))
        kernel1 = self.make_kernel(exec1, subdir="shared")
        with self.assertRaises(RuntimeError):
            kernel1.run(_eng())

        # The checkpoint on disk shows w1 and w2 completed before the crash.
        self.assertEqual(sorted(kernel1.checkpoint.completed_waves()),
                         ["w1", "w2"])
        self.assertEqual(exec1.submitted_waves, ["w1", "w2", "w3"])

        # Run 2: fresh kernel, SAME state dir, an executor that would re-run
        # everything if asked. Only w3 should actually be submitted.
        exec2 = MockExecutor(
            default=MockScenario(behaviour="complete", duration=4.0))
        kernel2 = self.make_kernel(exec2, subdir="shared",
                                   clock=self.clock)
        result = kernel2.run(_eng())

        # completed waves were NOT re-run
        self.assertEqual(exec2.submitted_waves, ["w3"])
        self.assertEqual(result.wave_states["w1"], WaveState.COMPLETE.value)
        self.assertEqual(result.wave_states["w2"], WaveState.COMPLETE.value)
        self.assertEqual(result.wave_states["w3"], WaveState.COMPLETE.value)
