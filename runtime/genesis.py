"""Genesis-proposal intake -> decisions queue (roster-genesis-protocol Stage 3).

When the ECL interview emits ``genesis_candidates`` (un-homed disciplines) and
the drafting parties (ECL Orchestrator + AI Manager) produce a proposal that
survived the Stage 0 right-sizing ladder at R3, the proposal must reach the
human owner for sign-off. This module is that plumbing: it turns a drafted
proposal into a ``GENESIS_PROPOSAL`` item on the engagement's decisions queue
(``decisions-queue.yaml``, schema ``decisions-queue/v1``) with the proposal
YAML as the linked document, so the owner reviews and decides it on the
dashboard's decision inbox exactly like any other gated document.

Deterministic software, no LLM: the protocol's Stage 3 rule ("a new roster is
always a human-signed decision") is enforced here by construction — the only
thing this module can do with a proposal is queue it for a human. There is no
approve path in code.
"""

from __future__ import annotations

from typing import List, Optional

from .state import StateEmitter

GENESIS_KIND = "GENESIS_PROPOSAL"
# Executive review window per AOM S3.3 (5 business days).
GENESIS_AOM_CLASS = "critical sign-off"
GENESIS_TIMEOUT_HOURS = 120


def make_genesis_item(*, roster_id: str, discipline: str, proposal_document: str,
                      drafted_by: str, ladder_conclusion: str,
                      created_iso: str, owner: str = "the owner (human)") -> dict:
    """Build a decisions-queue item for a drafted genesis proposal.

    ``proposal_document`` is the filename of the proposal YAML in the
    engagement's documents/ directory — the dashboard's "Open document"
    button renders it in the review surface. ``ladder_conclusion`` is the
    Stage 0 R3 conclusion, quoted so the owner sees WHY a new roster is
    proposed before opening the full document.
    """
    return {
        "id": f"GEN-{roster_id}",
        "kind": GENESIS_KIND,
        "title": f"New roster proposed: {roster_id} ({discipline}) — human sign-off required",
        "context": (
            f"A capability gap with no home in any existing roster survived the "
            f"right-sizing ladder at R3. Ladder conclusion: {ladder_conclusion} "
            f"Nothing is built until this decision is logged (roster-genesis-protocol Stage 3)."
        ),
        "options": ["Approve", "Amend (comment)", "Reject (comment with reason)"],
        "requested_by": drafted_by,
        "owner": owner,
        "created": created_iso,
        "aom_class": GENESIS_AOM_CLASS,
        "aom_timeout_hours": GENESIS_TIMEOUT_HOURS,
        "linked_document": proposal_document,
    }


def enqueue_genesis_proposal(emitter: StateEmitter, engagement: str, item: dict,
                             existing: Optional[List[dict]] = None) -> List[dict]:
    """Append a genesis item to the engagement's decisions queue (idempotent).

    ``existing`` defaults to the queue currently on disk, so repeated calls
    (e.g. a re-run after a crash) never duplicate the item. Returns the full
    open-items list as written.
    """
    if item.get("kind") != GENESIS_KIND:
        raise ValueError("enqueue_genesis_proposal only accepts GENESIS_PROPOSAL items")
    if not item.get("linked_document"):
        raise ValueError("a genesis proposal item must link its proposal document "
                         "— the owner decides on the document, not a summary")
    if existing is None:
        current = emitter.read_decisions_queue() or {}
        existing = list(current.get("open_items") or [])
    items = list(existing)
    if not any(i.get("id") == item["id"] for i in items):
        items.append(item)
    emitter.write_decisions_queue(engagement, items)
    return items
