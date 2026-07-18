"""The PraisonAI executor adapter, proven against scripted runners.

Covers the same outcome->termination-cause surface the Claude adapter's tests
cover — completion (+ tool-use metrics and output), runner error -> DIED,
rate limit -> BUDGET_PAUSED, silent hang -> kernel-detectable frozen
heartbeat, external cancel -> CANCELLED — plus a real-threads kernel drop-in
engagement (MonotonicClock, tight timings) proving PraisonAIExecutor is
swap-for-swap compatible with MockExecutor/ClaudeSubagentExecutor.

No praisonaiagents import is needed for these tests: the adapter is proven
against the injectable PraisonRunner seam, mirroring how the Claude adapter
is proven against FakeTransport. BYOK failure (no key -> loud CredentialError)
is asserted against the REAL default runner's key resolution, which fires
before any praisonaiagents import.
"""

import threading
import time
import unittest

from runtime.clock import ManualClock, MonotonicClock
from runtime.credentials import CredentialError, Credentials
from runtime.executor import TerminationCause, WaveTask
from runtime.isolation import Workspace
from runtime.kernel import EngagementSpec, KernelConfig, WaveSpec
from runtime.praison_executor import PraisonAIExecutor, default_praison_runner
from runtime.state import WaveState

from .helpers import KernelTestCase


def _workspace():
    return Workspace(run_id="w", path="/tmp/w", port=None)


def _task(wave_id="w1", agent_id="pm_agent", payload=None):
    return WaveTask(wave_id=wave_id, agent_id=agent_id, agent_version="1.0.0",
                    payload=payload or {})


def _wait_for(predicate, timeout=5.0):
    """Bounded real-time wait for a worker-thread condition."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = predicate()
        if result is not None:
            return result
        time.sleep(0.01)
    raise AssertionError("condition not reached within timeout")


class _RateLimitError(Exception):
    status_code = 429


class TestOutcomeMapping(unittest.TestCase):
    def test_completion_yields_completed_with_output_and_tool_uses(self):
        clock = ManualClock()

        def runner(task, heartbeat, tool_use):
            heartbeat()
            tool_use()
            heartbeat()
            return {"response": "deliverable text"}

        handle = PraisonAIExecutor(runner=runner).submit(_task(), _workspace(), clock)
        result = _wait_for(handle.poll)

        self.assertEqual(result.cause, TerminationCause.COMPLETED)
        self.assertEqual(result.output, {"response": "deliverable text"})
        self.assertEqual(result.metrics["tool_uses"], 1)

    def test_runner_error_maps_to_died(self):
        clock = ManualClock()

        def runner(task, heartbeat, tool_use):
            raise RuntimeError("provider exploded")

        handle = PraisonAIExecutor(runner=runner).submit(_task(), _workspace(), clock)
        result = _wait_for(handle.poll)

        self.assertEqual(result.cause, TerminationCause.DIED)
        self.assertIn("provider exploded", result.detail)

    def test_rate_limit_maps_to_budget_paused(self):
        clock = ManualClock()

        def runner(task, heartbeat, tool_use):
            raise _RateLimitError("quota exhausted")

        handle = PraisonAIExecutor(runner=runner).submit(_task(), _workspace(), clock)
        result = _wait_for(handle.poll)

        self.assertEqual(result.cause, TerminationCause.BUDGET_PAUSED)

    def test_silent_hang_freezes_heartbeat_and_cancel_maps_cause(self):
        clock = ManualClock()
        release = threading.Event()
        beat_once = threading.Event()

        def runner(task, heartbeat, tool_use):
            heartbeat()
            beat_once.set()
            release.wait(timeout=5.0)  # hang: no further heartbeats
            return {}

        handle = PraisonAIExecutor(runner=runner).submit(_task(), _workspace(), clock)
        self.assertIsNone(handle.poll())  # starts the worker
        self.assertTrue(beat_once.wait(timeout=5.0))

        frozen = handle.last_heartbeat()
        clock.advance(60.0)  # a minute of silence on the injected clock
        self.assertEqual(handle.last_heartbeat(), frozen)  # kernel would see death

        handle.cancel(TerminationCause.DIED)  # what the kernel does about it
        result = _wait_for(handle.poll)
        self.assertEqual(result.cause, TerminationCause.DIED)
        release.set()

    def test_external_cancel_maps_to_cancelled(self):
        clock = ManualClock()
        release = threading.Event()

        def runner(task, heartbeat, tool_use):
            release.wait(timeout=5.0)
            return {}

        handle = PraisonAIExecutor(runner=runner).submit(_task(), _workspace(), clock)
        self.assertIsNone(handle.poll())
        handle.cancel(TerminationCause.CANCELLED)
        result = _wait_for(handle.poll)
        self.assertEqual(result.cause, TerminationCause.CANCELLED)
        release.set()

    def test_late_result_after_close_is_discarded(self):
        clock = ManualClock()
        release = threading.Event()
        finished = threading.Event()

        def runner(task, heartbeat, tool_use):
            release.wait(timeout=5.0)
            finished.set()
            return {"response": "too late"}

        executor = PraisonAIExecutor(runner=runner)
        handle = executor.submit(_task(), _workspace(), clock)
        self.assertIsNone(handle.poll())
        handle.cancel(TerminationCause.TIMED_OUT)
        first = _wait_for(handle.poll)
        self.assertEqual(first.cause, TerminationCause.TIMED_OUT)

        release.set()
        self.assertTrue(finished.wait(timeout=5.0))
        # the settled result must not be overwritten by the orphaned turn
        self.assertEqual(handle.poll().cause, TerminationCause.TIMED_OUT)


class TestByok(unittest.TestCase):
    def test_no_key_configured_fails_loud(self):
        # The REAL runner resolves the key before touching praisonaiagents, so
        # the operator-fixable error wins regardless of installed packages.
        creds = Credentials(environ={})  # empty environment, no injected config
        with self.assertRaises(CredentialError):
            default_praison_runner(_task(), lambda: None, lambda: None,
                                   credentials=creds)


class TestKernelDropIn(KernelTestCase):
    def test_praison_executor_runs_a_kernel_engagement_with_real_threads(self):
        # Real worker threads + MonotonicClock (tight timings): the same
        # kernel logic that drives MockExecutor runs a two-wave engagement
        # against PraisonAIExecutor unchanged.
        def runner(task, heartbeat, tool_use):
            for _ in range(3):
                time.sleep(0.01)
                heartbeat()
            if task.wave_id == "w1":
                tool_use()
            return {"response": f"{task.wave_id} done"}

        executor = PraisonAIExecutor(runner=runner)
        clock = MonotonicClock()
        config = KernelConfig(heartbeat_grace=2.0, wave_timeout=10.0,
                              poll_interval=0.02)
        kernel = self.make_kernel(executor, clock=clock, config=config)
        eng = EngagementSpec("eng-praison", [
            WaveSpec("w1", "pm_agent"),
            WaveSpec("w2", "backend_agent", depends_on=["w1"]),
        ])

        result = kernel.run(eng)

        self.assertEqual(result.wave_states["w1"], WaveState.COMPLETE.value)
        self.assertEqual(result.wave_states["w2"], WaveState.COMPLETE.value)
        self.assertEqual(result.wave_causes["w1"],
                         TerminationCause.COMPLETED.value)
        self.assertEqual(executor.submitted_waves, ["w1", "w2"])

        by_wave = {r["wave"]: r for r in kernel.emitter.read_metrics()}
        self.assertEqual(by_wave["w1"]["termination_cause"], "COMPLETED")
        self.assertEqual(by_wave["w1"]["tool_uses"], 1)


if __name__ == "__main__":
    unittest.main()
