"""RSB-01: liveness + timeout + dead-agent detection.

The fix for the 41h silent death: a wave that stops emitting heartbeats is
marked DEAD within the timeout and recorded - never left silently pending.
"""

from runtime.executor import MockExecutor, MockScenario, TerminationCause
from runtime.kernel import EngagementSpec, WaveSpec
from runtime.state import WaveState

from .helpers import KernelTestCase


class TestLiveness(KernelTestCase):
    def test_silent_death_detected_within_timeout(self):
        # w2 stops heartbeating at t=5; hard timeout is 30s away.
        executor = MockExecutor(
            scenarios={"w2": MockScenario(behaviour="die", die_at=5.0,
                                          heartbeat_interval=1.0)},
            default=MockScenario(behaviour="complete", duration=4.0))
        kernel = self.make_kernel(executor)
        eng = EngagementSpec("eng-death", [
            WaveSpec("w1", "pm_agent"),
            WaveSpec("w2", "backend_agent", depends_on=["w1"]),
            WaveSpec("w3", "frontend_agent", depends_on=["w2"]),
        ])

        result = kernel.run(eng)

        # w2 is DEAD (not pending), detected before the 30s hard timeout.
        self.assertEqual(result.wave_states["w2"], WaveState.DEAD.value)
        self.assertEqual(result.wave_causes["w2"], TerminationCause.DIED.value)
        # detection happened while the clock was still well under the timeout
        self.assertLess(self.clock.now(), self.config.wave_timeout)
        # the dead agent is recorded in the integrity register as CRITICAL
        integ = kernel.emitter.read_integrity()
        died = [r for r in integ if r["type"] == "DIED"]
        self.assertEqual(len(died), 1)
        self.assertEqual(died[0]["wave"], "w2")
        self.assertEqual(died[0]["severity"], "CRITICAL")
        # downstream did NOT silently proceed
        self.assertEqual(result.wave_states["w3"], WaveState.BLOCKED.value)

    def test_alive_but_stuck_wave_times_out(self):
        # heartbeats stay fresh but the wave never finishes -> hard timeout.
        executor = MockExecutor(
            scenarios={"w1": MockScenario(behaviour="hang_timeout",
                                          heartbeat_interval=1.0)})
        kernel = self.make_kernel(executor)
        eng = EngagementSpec("eng-hang", [WaveSpec("w1", "stuck_agent")])

        result = kernel.run(eng)

        self.assertEqual(result.wave_states["w1"], WaveState.TIMED_OUT.value)
        self.assertEqual(result.wave_causes["w1"],
                         TerminationCause.TIMED_OUT.value)
        integ = kernel.emitter.read_integrity()
        self.assertTrue(any(r["type"] == "TIMED_OUT" for r in integ))
