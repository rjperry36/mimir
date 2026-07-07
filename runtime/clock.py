"""Injectable clock abstraction.

The kernel never calls ``time.time()`` / ``time.monotonic()`` directly. All
timekeeping goes through a :class:`Clock` so that tests are deterministic (no
wall-clock flakiness) and production uses a real monotonic clock.

Two implementations:
  * :class:`MonotonicClock` - wraps ``time.monotonic``; used in real runs.
  * :class:`ManualClock`    - time only advances when ``sleep`` / ``advance`` is
    called; used in tests to drive the kernel's monitor loop deterministically.
"""

from __future__ import annotations

import time
from typing import Protocol


class Clock(Protocol):
    """A monotonic time source, in floating-point seconds."""

    def now(self) -> float:  # pragma: no cover - protocol
        ...

    def sleep(self, seconds: float) -> None:  # pragma: no cover - protocol
        ...


class MonotonicClock:
    """Real clock backed by ``time.monotonic`` (never goes backwards)."""

    def now(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        if seconds > 0:
            time.sleep(seconds)


class ManualClock:
    """Deterministic test clock.

    Time starts at ``start`` and only moves forward when ``sleep`` / ``advance``
    is called. This lets a test walk the kernel's monitor loop step by step with
    no dependence on the host machine's speed.
    """

    def __init__(self, start: float = 0.0) -> None:
        self._t = float(start)

    def now(self) -> float:
        return self._t

    def sleep(self, seconds: float) -> None:
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("time cannot move backwards")
        self._t += seconds
