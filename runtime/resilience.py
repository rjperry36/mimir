"""Tool-resilience layer: timeout, retry, fallback, circuit-breaker.

The ASA flagged that tool/API calls in the pilot had **no** timeout, retry, or
fallback - a single slow or flaky tool could stall or kill a wave. This module
wraps any callable with those four protections, all **deterministic** and driven
by the kernel's injectable :class:`~runtime.clock.Clock` so tests never touch the
wall clock and never sleep for real.

The four protections
--------------------
* **timeout**   - a per-call budget (in the clock's seconds). Cooperative: the
  wrapped call is measured against the injected clock, so a "slow" tool that
  advances the clock (``clock.sleep``) past the budget trips ``CallTimeout``.
  For a genuinely-hung *real* call, layer :func:`run_with_hard_timeout` (a real
  thread watchdog) - documented but not used in the deterministic tests.
* **retry**     - exponential backoff + jitter, configurable factor and a cap,
  a bounded number of attempts. The backoff sleeps go through ``clock.sleep``.
* **fallback**  - a value or callable returned when every attempt is exhausted
  (or the breaker is open), instead of raising.
* **circuit-breaker** - opens after N consecutive failures, blocks calls while
  open, half-opens for a single probe after a cooldown, and closes on success.

Everything is a pure function of (inputs, injected clock, injected RNG), so the
tests are fully deterministic with no flakiness.
"""

from __future__ import annotations

import random
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Tuple, Type

from .clock import Clock, MonotonicClock


class CallTimeout(Exception):
    """A wrapped call exceeded its per-call time budget (cooperative timeout)."""


class CircuitOpen(Exception):
    """The circuit breaker is open and no fallback was supplied."""


# Sentinel so ``fallback=None`` is distinguishable from "no fallback given".
class _Unset:
    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return "<unset>"


_UNSET = _Unset()


# ---------------------------------------------------------------------------
# Retry policy
# ---------------------------------------------------------------------------


@dataclass
class RetryPolicy:
    """Exponential-backoff-with-jitter retry configuration.

    ``backoff(attempt)`` for a 1-based attempt number returns the delay to sleep
    *after* that attempt failed (before the next one). With ``jitter == 0`` the
    delay is exactly ``base_delay * factor**(attempt-1)`` capped at ``max_delay``
    - deterministic, so a test can assert the exact cumulative sleep. With
    ``jitter > 0`` the delay is spread uniformly by +/- that fraction using the
    injected RNG (still deterministic under a seeded RNG).
    """

    max_attempts: int = 3
    base_delay: float = 0.1
    factor: float = 2.0
    max_delay: float = 30.0
    jitter: float = 0.0  # fraction in [0, 1]
    retry_on: Tuple[Type[BaseException], ...] = (Exception,)

    def backoff(self, attempt: int, rng: random.Random) -> float:
        raw = self.base_delay * (self.factor ** (attempt - 1))
        raw = min(raw, self.max_delay)
        if self.jitter:
            spread = raw * self.jitter
            low = max(0.0, raw - spread)
            high = min(self.max_delay, raw + spread)
            raw = rng.uniform(low, high)
        return raw


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------


class BreakerState(str, Enum):
    CLOSED = "CLOSED"        # calls flow normally
    OPEN = "OPEN"            # calls are blocked (fail fast)
    HALF_OPEN = "HALF_OPEN"  # one probe is allowed through


@dataclass
class CircuitBreaker:
    """Consecutive-failure circuit breaker (clock-driven, thread-safe).

    * ``fail_threshold`` consecutive failures -> OPEN.
    * While OPEN, :meth:`allow` returns ``False`` (fail fast) until
      ``reset_timeout`` clock-seconds have elapsed, then it flips to HALF_OPEN
      and lets a single probe through.
    * A success in HALF_OPEN (or CLOSED) resets to CLOSED; a failure in
      HALF_OPEN re-opens with a fresh cooldown.
    """

    fail_threshold: int = 5
    reset_timeout: float = 30.0
    clock: Clock = field(default_factory=MonotonicClock)

    _state: BreakerState = field(default=BreakerState.CLOSED, init=False)
    _consec_failures: int = field(default=0, init=False)
    _opened_at: float = field(default=0.0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    @property
    def state(self) -> BreakerState:
        with self._lock:
            return self._state

    def allow(self) -> bool:
        """Return True if a call may proceed, advancing OPEN -> HALF_OPEN when
        the cooldown has elapsed."""
        with self._lock:
            if self._state is BreakerState.OPEN:
                if self.clock.now() - self._opened_at >= self.reset_timeout:
                    self._state = BreakerState.HALF_OPEN
                    return True  # single probe
                return False
            if self._state is BreakerState.HALF_OPEN:
                # a probe is already in flight; block others until it resolves
                return False
            return True  # CLOSED

    def on_success(self) -> None:
        with self._lock:
            self._consec_failures = 0
            self._state = BreakerState.CLOSED

    def on_failure(self) -> None:
        with self._lock:
            self._consec_failures += 1
            if (self._state is BreakerState.HALF_OPEN
                    or self._consec_failures >= self.fail_threshold):
                self._state = BreakerState.OPEN
                self._opened_at = self.clock.now()


# ---------------------------------------------------------------------------
# The resilient call
# ---------------------------------------------------------------------------


def _resolve_fallback(fallback: Any, exc: Optional[BaseException]) -> Any:
    if callable(fallback):
        try:
            return fallback(exc)
        except TypeError:
            return fallback()
    return fallback


def _invoke(fn: Callable[[], Any], timeout: Optional[float], clock: Clock) -> Any:
    """Run ``fn`` and enforce the cooperative timeout against ``clock``.

    ``fn`` is expected to be clock-cooperative for the timeout to bite: a slow
    tool advances the injected clock (e.g. via ``clock.sleep``) while it works,
    and if the elapsed budget is blown we raise :class:`CallTimeout`. This is
    the same cooperative-polling model the kernel's liveness monitor uses; it is
    deterministic under ManualClock. See :func:`run_with_hard_timeout` for the
    real-thread variant that can interrupt a genuinely-hung call.
    """
    if timeout is None:
        return fn()
    start = clock.now()
    result = fn()
    if clock.now() - start > timeout:
        raise CallTimeout(
            f"call exceeded timeout of {timeout}s "
            f"(took {clock.now() - start:.3f}s)")
    return result


def resilient_call(
    fn: Callable[[], Any],
    *,
    clock: Clock,
    retry: Optional[RetryPolicy] = None,
    breaker: Optional[CircuitBreaker] = None,
    timeout: Optional[float] = None,
    fallback: Any = _UNSET,
    rng: Optional[random.Random] = None,
    on_retry: Optional[Callable[[int, BaseException, float], None]] = None,
) -> Any:
    """Call ``fn`` with timeout + retry + fallback + circuit-breaker.

    Order of protections, per attempt:
      1. If a breaker is supplied and open (and past no cooldown) -> fail fast:
         return the fallback if given, else raise :class:`CircuitOpen`.
      2. Invoke ``fn`` under the cooperative ``timeout``.
      3. On success -> ``breaker.on_success()`` and return the value.
      4. On a *retryable* exception -> ``breaker.on_failure()``, sleep the
         backoff (through ``clock.sleep``), and try again until attempts run out.
         A non-retryable exception is recorded as a failure and re-raised.
    When attempts are exhausted (or the breaker trips mid-loop): return the
    fallback if one was given, else re-raise the last exception.
    """
    retry = retry or RetryPolicy()
    rng = rng or random.Random()

    if breaker is not None and not breaker.allow():
        if fallback is not _UNSET:
            return _resolve_fallback(fallback, CircuitOpen("circuit open"))
        raise CircuitOpen("circuit breaker is open")

    last_exc: Optional[BaseException] = None
    for attempt in range(1, retry.max_attempts + 1):
        try:
            result = _invoke(fn, timeout, clock)
        except retry.retry_on as exc:  # retryable failure
            last_exc = exc
            if breaker is not None:
                breaker.on_failure()
            if attempt < retry.max_attempts:
                delay = retry.backoff(attempt, rng)
                if on_retry is not None:
                    on_retry(attempt, exc, delay)
                clock.sleep(delay)
                # if the breaker just opened, stop retrying and fall through
                if breaker is not None and breaker.state is BreakerState.OPEN:
                    break
                continue
            # exhausted
            break
        except Exception:  # non-retryable failure
            if breaker is not None:
                breaker.on_failure()
            raise
        else:
            if breaker is not None:
                breaker.on_success()
            return result

    # every attempt failed (or breaker opened mid-loop)
    if fallback is not _UNSET:
        return _resolve_fallback(fallback, last_exc)
    assert last_exc is not None
    raise last_exc


@dataclass
class ResilientTool:
    """A reusable wrapper binding a fixed policy/breaker to a callable.

    Handy for wrapping a specific tool once and calling it many times::

        tool = ResilientTool(fetch_page, clock=clock,
                             retry=RetryPolicy(max_attempts=4),
                             breaker=CircuitBreaker(fail_threshold=3, clock=clock),
                             timeout=5.0, fallback="")
        html = tool(url)
    """

    fn: Callable[..., Any]
    clock: Clock
    retry: Optional[RetryPolicy] = None
    breaker: Optional[CircuitBreaker] = None
    timeout: Optional[float] = None
    fallback: Any = _UNSET
    rng: Optional[random.Random] = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return resilient_call(
            lambda: self.fn(*args, **kwargs),
            clock=self.clock,
            retry=self.retry,
            breaker=self.breaker,
            timeout=self.timeout,
            fallback=self.fallback,
            rng=self.rng,
        )


# ---------------------------------------------------------------------------
# Real-thread hard timeout (production only; NOT used in deterministic tests)
# ---------------------------------------------------------------------------


def run_with_hard_timeout(fn: Callable[[], Any], timeout: float) -> Any:
    """Run ``fn`` in a daemon thread and abandon it after ``timeout`` real
    seconds, raising :class:`CallTimeout`.

    This is the escape hatch for a genuinely-hung *real* call that never returns
    and cannot cooperate with the injected clock (e.g. a blocked socket read).
    It uses **wall-clock** time and a real thread, so it is intentionally kept
    out of the deterministic test path. The abandoned thread keeps running until
    the process exits - use it only where that is acceptable (a real adapter
    should also cancel the underlying request).
    """
    box: dict = {}

    def _target() -> None:
        try:
            box["value"] = fn()
        except BaseException as exc:  # noqa: BLE001 - propagate to caller
            box["error"] = exc

    worker = threading.Thread(target=_target, daemon=True)
    worker.start()
    worker.join(timeout)
    if worker.is_alive():
        raise CallTimeout(f"call exceeded hard timeout of {timeout}s")
    if "error" in box:
        raise box["error"]
    return box.get("value")
