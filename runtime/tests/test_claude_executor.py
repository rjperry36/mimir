"""The real executor adapter, proven against a deterministic FakeTransport.

Covers the outcome->termination-cause mapping the kernel depends on:
normal completion, silent hang (heartbeat stops -> DIED-eligible), simulated
429 -> BUDGET_PAUSED, repeated API error -> DIED, and cancel -> CANCELLED. Also
enforces the BYOK requirement: with no key configured the executor fails loud
and clear rather than crashing or silently skipping.
"""

import unittest

from runtime.clock import ManualClock
from runtime.credentials import Credentials, CredentialError, mask
from runtime.claude_executor import (
    ClaudeSubagentExecutor,
    FakeEvent,
    FakeTransport,
    TransportStatus,
)
from runtime.executor import TerminationCause, WaveTask
from runtime.isolation import Workspace


def _make_executor(clock, events, **fake_kwargs):
    """An executor whose transport is a scripted FakeTransport (deterministic)."""
    def factory(task, workspace, ck):
        return FakeTransport(ck, events, **fake_kwargs)
    return ClaudeSubagentExecutor(transport_factory=factory)


def _workspace():
    return Workspace(run_id="w", path="/tmp/w", port=None)


class TestNormalCompletion(unittest.TestCase):
    def test_completion_yields_completed_with_metrics(self):
        clock = ManualClock()
        events = [
            FakeEvent(1.0, "token", {"tokens": 50}),
            FakeEvent(2.0, "tool_use"),
            FakeEvent(3.0, "token", {"tokens": 70}),
            FakeEvent(4.0, "complete"),
        ]
        ex = _make_executor(clock, events, output={"answer": 42})
        handle = ex.submit(WaveTask("w1", "agent", "v1"), _workspace(), clock)

        # runs until the terminal event fires at t=4
        self.assertIsNone(handle.poll())
        clock.advance(4.0)
        result = handle.poll()

        self.assertIsNotNone(result)
        self.assertEqual(result.cause, TerminationCause.COMPLETED)
        self.assertEqual(result.metrics["tokens"], 120)
        self.assertEqual(result.metrics["tool_uses"], 1)
        self.assertEqual(result.metrics["duration_ms"], 4000)
        self.assertEqual(result.output, {"answer": 42})

    def test_heartbeat_advances_with_streamed_events(self):
        clock = ManualClock()
        events = [FakeEvent(1.0, "token"), FakeEvent(2.0, "token"),
                  FakeEvent(5.0, "complete")]
        ex = _make_executor(clock, events)
        handle = ex.submit(WaveTask("w1", "a", "v1"), _workspace(), clock)
        start_hb = handle.last_heartbeat()
        clock.advance(2.0)
        self.assertGreater(handle.last_heartbeat(), start_hb)


class TestSilentHang(unittest.TestCase):
    def test_heartbeat_freezes_so_kernel_can_detect_death(self):
        clock = ManualClock()
        # heartbeats up to t=3, then silence and no terminal event -> a hang.
        events = [FakeEvent(1.0, "token"), FakeEvent(2.0, "token"),
                  FakeEvent(3.0, "token")]
        ex = _make_executor(clock, events)
        handle = ex.submit(WaveTask("w1", "a", "v1"), _workspace(), clock)

        clock.advance(3.0)
        frozen = handle.last_heartbeat()
        self.assertIsNone(handle.poll())  # never self-completes
        clock.advance(10.0)
        # heartbeat has NOT advanced past t=3 - the silence the kernel detects
        self.assertEqual(handle.last_heartbeat(), frozen)
        self.assertIsNone(handle.poll())

        # the kernel, seeing the silence, cancels it as DIED
        handle.cancel(TerminationCause.DIED)
        self.assertEqual(handle.poll().cause, TerminationCause.DIED)


class TestRateLimit(unittest.TestCase):
    def test_429_maps_to_budget_paused(self):
        clock = ManualClock()
        events = [FakeEvent(1.0, "token"),
                  FakeEvent(2.0, "rate_limit", {"detail": "HTTP 429 quota"})]
        ex = _make_executor(clock, events)
        handle = ex.submit(WaveTask("w1", "a", "v1"), _workspace(), clock)
        clock.advance(2.0)
        result = handle.poll()
        self.assertEqual(result.cause, TerminationCause.BUDGET_PAUSED)
        self.assertIn("429", result.detail)


class TestApiError(unittest.TestCase):
    def test_repeated_error_after_retries_maps_to_died(self):
        clock = ManualClock()
        # the transport models an error that persisted after its own retries
        events = [FakeEvent(1.0, "token"),
                  FakeEvent(2.0, "error",
                            {"detail": "500 API error after retries"})]
        ex = _make_executor(clock, events)
        handle = ex.submit(WaveTask("w1", "a", "v1"), _workspace(), clock)
        clock.advance(2.0)
        result = handle.poll()
        self.assertEqual(result.cause, TerminationCause.DIED)
        self.assertIn("after retries", result.detail)


class TestCancel(unittest.TestCase):
    def test_external_cancel_maps_to_cancelled(self):
        clock = ManualClock()
        events = [FakeEvent(1.0, "token"), FakeEvent(10.0, "complete")]
        ex = _make_executor(clock, events)
        handle = ex.submit(WaveTask("w1", "a", "v1"), _workspace(), clock)
        clock.advance(1.0)
        self.assertIsNone(handle.poll())
        handle.cancel(TerminationCause.CANCELLED)
        self.assertEqual(handle.poll().cause, TerminationCause.CANCELLED)


class TestByok(unittest.TestCase):
    def test_no_key_configured_raises_clear_error(self):
        clock = ManualClock()
        # empty environ + no injected key -> the real factory must fail loud.
        creds = Credentials(overrides={}, environ={})
        ex = ClaudeSubagentExecutor(credentials=creds)
        with self.assertRaises(CredentialError) as ctx:
            ex.submit(WaveTask("w1", "a", "v1"), _workspace(), clock)
        msg = str(ctx.exception)
        self.assertIn("ANTHROPIC_API_KEY", msg)
        self.assertIn("bring-your-own-key", msg)

    def test_injected_key_takes_priority_over_env(self):
        creds = Credentials(overrides={"ANTHROPIC_API_KEY": "sk-injected-1234"},
                            environ={"ANTHROPIC_API_KEY": "sk-env-9999"})
        self.assertEqual(creds.require("ANTHROPIC_API_KEY"), "sk-injected-1234")

    def test_mask_redacts_to_last_four(self):
        self.assertEqual(mask("sk-supersecret-ABCD"), "***************ABCD")
        self.assertEqual(mask(""), "<unset>")
        self.assertEqual(mask("ab"), "**")

    def test_known_service_lookup_by_name(self):
        creds = Credentials(overrides={"PAYMENT_PROVIDER_API_KEY": "sk-pay-9999"},
                            environ={})
        self.assertEqual(creds.require_service("payment_provider"), "sk-pay-9999")
        with self.assertRaises(CredentialError):
            creds.require_service("neon")  # not configured -> loud failure


if __name__ == "__main__":
    unittest.main()
