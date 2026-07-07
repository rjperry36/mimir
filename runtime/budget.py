"""Budget / quota awareness with graceful pause (RSB-02).

The pilot's PT-05: a session usage ceiling terminated agents mid-flight; the
pause was graceful only by luck of commit hygiene. The kernel makes it
deliberate: a pre-dispatch quota check. When the next wave's estimated cost
would breach the ceiling, the run PAUSES (state is checkpointed) rather than
dying mid-wave, and can resume later (with a raised ceiling or a new session).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BudgetGuard:
    """Tracks consumed units against a ceiling.

    Units are deliberately abstract (tokens, or a session-quota unit). The guard
    is a pre-dispatch gate, not an in-wave killer - the whole point is to stop
    BEFORE spending, not halfway through.
    """

    ceiling: float
    consumed: float = 0.0

    def can_afford(self, estimate: float) -> bool:
        """True iff dispatching a wave estimated at ``estimate`` stays under."""
        return (self.consumed + estimate) <= self.ceiling

    def charge(self, amount: float) -> None:
        self.consumed += amount

    def remaining(self) -> float:
        return self.ceiling - self.consumed

    def raise_ceiling(self, new_ceiling: float) -> None:
        """Used on resume (fresh session / owner-approved higher budget)."""
        self.ceiling = new_ceiling
