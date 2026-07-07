"""Deterministic gate-runner (fires between waves).

A gate is a deterministic predicate evaluated after a wave completes. A FAILED
gate BLOCKS every wave that depends on the gated wave and is recorded in the
integrity-register; a PASSED gate releases them. No LLM is involved - this is
exactly the kind of rule-based logic the ASA said should be deterministic code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class GateResult:
    gate_id: str
    passed: bool
    detail: str = ""


@dataclass
class Gate:
    """A named, deterministic check run against a wave's result/output.

    ``predicate`` receives the wave's :class:`~runtime.executor.AgentResult` and
    returns ``(passed: bool, detail: str)``. ``human_gate`` marks gates that
    additionally require a human decision (they surface in the decisions-queue).
    """

    gate_id: str
    predicate: Callable[[object], "tuple[bool, str]"]
    human_gate: bool = False
    description: str = ""


def run_gate(gate: Gate, result: object) -> GateResult:
    passed, detail = gate.predicate(result)
    return GateResult(gate_id=gate.gate_id, passed=bool(passed), detail=detail)


# A couple of ready-made predicates for the demo / common cases.

def always_pass(_result: object) -> "tuple[bool, str]":
    return True, "no-op gate"


def require_no_defects(result: object) -> "tuple[bool, str]":
    """Gate fails if the wave reported any unresolved defects."""
    metrics = getattr(result, "metrics", {}) or {}
    defects = metrics.get("defects_found", 0)
    if defects and defects > metrics.get("defects_resolved", 0):
        return False, f"{defects} unresolved defect(s)"
    return True, "no unresolved defects"
