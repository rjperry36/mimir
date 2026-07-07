"""RSB-04 termination-cause attribution: every cause distinguishable and accurate.

COMPLETED / TIMED_OUT / DIED / BUDGET_PAUSED / GATE_BLOCKED - a crash is DIED,
never "user-stopped".
"""

from runtime.budget import BudgetGuard
from runtime.executor import MockExecutor, MockScenario, TerminationCause
from runtime.gates import Gate
from runtime.kernel import EngagementSpec, WaveSpec

from .helpers import KernelTestCase


def _fail_gate(_r):
    return False, "fail"


class TestTerminationCauses(KernelTestCase):
    def test_completed_died_timedout_gateblocked_in_one_run(self):
        executor = MockExecutor(
            scenarios={
                "w_ok": MockScenario(behaviour="complete", duration=4.0),
                "w_die": MockScenario(behaviour="die", die_at=5.0,
                                      heartbeat_interval=1.0),
                "w_hang": MockScenario(behaviour="hang_timeout",
                                       heartbeat_interval=1.0),
                "w_gate": MockScenario(behaviour="complete", duration=4.0),
            })
        kernel = self.make_kernel(executor)
        eng = EngagementSpec("eng-causes", [
            WaveSpec("w_ok", "a"),
            WaveSpec("w_die", "b"),
            WaveSpec("w_hang", "c"),
            WaveSpec("w_gate", "d", gate=Gate("g", _fail_gate)),
            WaveSpec("w_after_gate", "e", depends_on=["w_gate"]),
        ])
        result = kernel.run(eng)

        self.assertEqual(result.wave_causes["w_ok"],
                         TerminationCause.COMPLETED.value)
        self.assertEqual(result.wave_causes["w_die"],
                         TerminationCause.DIED.value)
        self.assertEqual(result.wave_causes["w_hang"],
                         TerminationCause.TIMED_OUT.value)
        # a gate failure blocks the dependent -> attributed GATE_BLOCKED
        self.assertEqual(result.wave_causes["w_after_gate"],
                         TerminationCause.GATE_BLOCKED.value)

        # each distinct cause is present and distinguishable
        causes = set(result.wave_causes.values())
        self.assertIn(TerminationCause.COMPLETED.value, causes)
        self.assertIn(TerminationCause.DIED.value, causes)
        self.assertIn(TerminationCause.TIMED_OUT.value, causes)
        self.assertIn(TerminationCause.GATE_BLOCKED.value, causes)

        # and each is faithfully mirrored in the metrics ledger
        ledger = kernel.emitter.read_metrics()
        by_wave = {r["wave"]: r["termination_cause"] for r in ledger}
        self.assertEqual(by_wave["w_ok"], "COMPLETED")
        self.assertEqual(by_wave["w_die"], "DIED")
        self.assertEqual(by_wave["w_hang"], "TIMED_OUT")

    def test_budget_paused_cause(self):
        executor = MockExecutor(
            default=MockScenario(behaviour="complete", duration=4.0))
        kernel = self.make_kernel(executor)
        eng = EngagementSpec("eng-bp", [
            WaveSpec("w1", "a", est_cost=10),
            WaveSpec("w2", "b", depends_on=["w1"], est_cost=10),
        ])
        result = kernel.run(eng, budget=BudgetGuard(ceiling=10))
        self.assertEqual(result.wave_causes["w2"],
                         TerminationCause.BUDGET_PAUSED.value)
