"""Tool-resilience layer: timeout, retry, fallback, circuit-breaker.

All deterministic - a ManualClock (no real sleeps) and, where jitter is used, a
seeded RNG. These prove the layer the ASA flagged as missing.
"""

import random
import unittest

from runtime.clock import ManualClock
from runtime.resilience import (
    BreakerState,
    CallTimeout,
    CircuitBreaker,
    CircuitOpen,
    ResilientTool,
    RetryPolicy,
    resilient_call,
)


class TestTimeout(unittest.TestCase):
    def test_timeout_trips_on_slow_call(self):
        clock = ManualClock()

        def slow():
            clock.sleep(5.0)  # tool takes 5s on the injected clock
            return "done"

        with self.assertRaises(CallTimeout):
            resilient_call(slow, clock=clock, timeout=1.0,
                           retry=RetryPolicy(max_attempts=1))

    def test_fast_call_under_budget_returns(self):
        clock = ManualClock()

        def fast():
            clock.sleep(0.2)
            return "ok"

        self.assertEqual(
            resilient_call(fast, clock=clock, timeout=1.0,
                           retry=RetryPolicy(max_attempts=1)),
            "ok")

    def test_timeout_then_fallback(self):
        clock = ManualClock()

        def slow():
            clock.sleep(9.0)
            return "never"

        out = resilient_call(slow, clock=clock, timeout=1.0,
                             retry=RetryPolicy(max_attempts=2, base_delay=0.5),
                             fallback="fallback-value")
        self.assertEqual(out, "fallback-value")


class TestRetry(unittest.TestCase):
    def test_retry_succeeds_on_nth_attempt(self):
        clock = ManualClock()
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise ConnectionError("transient")
            return "recovered"

        out = resilient_call(
            flaky, clock=clock,
            retry=RetryPolicy(max_attempts=5, base_delay=0.1, factor=2.0))
        self.assertEqual(out, "recovered")
        self.assertEqual(calls["n"], 3)  # failed twice, succeeded on the 3rd

    def test_backoff_delays_are_deterministic_no_jitter(self):
        clock = ManualClock()
        calls = {"n": 0}

        def always_fail():
            calls["n"] += 1
            raise ValueError("boom")

        # 3 attempts -> 2 backoff sleeps: 0.1, 0.2 -> total 0.3s on the clock
        with self.assertRaises(ValueError):
            resilient_call(
                always_fail, clock=clock,
                retry=RetryPolicy(max_attempts=3, base_delay=0.1, factor=2.0))
        self.assertEqual(calls["n"], 3)
        self.assertAlmostEqual(clock.now(), 0.3, places=9)

    def test_backoff_respects_cap(self):
        rng = random.Random(0)
        policy = RetryPolicy(base_delay=1.0, factor=10.0, max_delay=5.0)
        # attempt 3 would be 1*10^2 = 100, capped to 5.0
        self.assertEqual(policy.backoff(3, rng), 5.0)

    def test_retry_exhausts_then_fallback_used(self):
        clock = ManualClock()
        calls = {"n": 0}

        def always_fail():
            calls["n"] += 1
            raise RuntimeError("still broken")

        out = resilient_call(
            always_fail, clock=clock,
            retry=RetryPolicy(max_attempts=3, base_delay=0.1),
            fallback=lambda exc: f"fell back after {exc}")
        self.assertEqual(calls["n"], 3)
        self.assertTrue(out.startswith("fell back after"))

    def test_non_retryable_exception_raises_immediately(self):
        clock = ManualClock()
        calls = {"n": 0}

        def fail_type():
            calls["n"] += 1
            raise KeyError("not retryable")

        with self.assertRaises(KeyError):
            resilient_call(
                fail_type, clock=clock,
                retry=RetryPolicy(max_attempts=5, retry_on=(ValueError,)))
        self.assertEqual(calls["n"], 1)  # no retries for a non-matching type


class TestCircuitBreaker(unittest.TestCase):
    def test_opens_after_threshold_blocks_then_half_opens_then_closes(self):
        clock = ManualClock()
        breaker = CircuitBreaker(fail_threshold=3, reset_timeout=10.0,
                                 clock=clock)
        calls = {"n": 0}

        def failing():
            calls["n"] += 1
            raise ConnectionError("down")

        # 3 failing calls (each single-attempt) -> breaker opens.
        for _ in range(3):
            out = resilient_call(
                failing, clock=clock, breaker=breaker,
                retry=RetryPolicy(max_attempts=1), fallback="fb")
            self.assertEqual(out, "fb")
        self.assertEqual(breaker.state, BreakerState.OPEN)
        self.assertEqual(calls["n"], 3)

        # While OPEN, calls are blocked - fn is NOT invoked, fallback returned.
        out = resilient_call(failing, clock=clock, breaker=breaker,
                             retry=RetryPolicy(max_attempts=1), fallback="fb")
        self.assertEqual(out, "fb")
        self.assertEqual(calls["n"], 3)  # unchanged: call was blocked

        # After the cooldown, the breaker half-opens and lets a probe through.
        clock.advance(10.0)
        good = {"n": 0}

        def ok():
            good["n"] += 1
            return "recovered"

        out = resilient_call(ok, clock=clock, breaker=breaker,
                             retry=RetryPolicy(max_attempts=1))
        self.assertEqual(out, "recovered")
        self.assertEqual(good["n"], 1)             # probe actually ran
        self.assertEqual(breaker.state, BreakerState.CLOSED)  # closed on success

    def test_open_without_fallback_raises_circuit_open(self):
        clock = ManualClock()
        breaker = CircuitBreaker(fail_threshold=1, reset_timeout=10.0,
                                 clock=clock)

        def failing():
            raise ConnectionError("down")

        # First failure opens the breaker (threshold 1), fallback catches it.
        resilient_call(failing, clock=clock, breaker=breaker,
                       retry=RetryPolicy(max_attempts=1), fallback="fb")
        self.assertEqual(breaker.state, BreakerState.OPEN)

        # Now a call with no fallback fails fast with CircuitOpen.
        with self.assertRaises(CircuitOpen):
            resilient_call(failing, clock=clock, breaker=breaker,
                           retry=RetryPolicy(max_attempts=1))

    def test_half_open_probe_failure_reopens(self):
        clock = ManualClock()
        breaker = CircuitBreaker(fail_threshold=2, reset_timeout=5.0,
                                 clock=clock)

        def failing():
            raise ConnectionError("down")

        for _ in range(2):
            resilient_call(failing, clock=clock, breaker=breaker,
                           retry=RetryPolicy(max_attempts=1), fallback="fb")
        self.assertEqual(breaker.state, BreakerState.OPEN)

        clock.advance(5.0)  # cooldown elapsed -> next allow() half-opens
        # the probe fails -> breaker re-opens with a fresh cooldown
        resilient_call(failing, clock=clock, breaker=breaker,
                       retry=RetryPolicy(max_attempts=1), fallback="fb")
        self.assertEqual(breaker.state, BreakerState.OPEN)


class TestResilientTool(unittest.TestCase):
    def test_wrapper_binds_policy_and_passes_args(self):
        clock = ManualClock()
        calls = {"n": 0}

        def tool(x, y):
            calls["n"] += 1
            if calls["n"] < 2:
                raise ConnectionError("transient")
            return x + y

        wrapped = ResilientTool(tool, clock=clock,
                                retry=RetryPolicy(max_attempts=3, base_delay=0.1))
        self.assertEqual(wrapped(2, 3), 5)
        self.assertEqual(calls["n"], 2)


if __name__ == "__main__":
    unittest.main()
