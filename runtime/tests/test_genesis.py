"""Genesis-proposal plumbing: proposal -> decisions queue, human-only decision."""

from __future__ import annotations

import shutil
import tempfile
import unittest

from runtime.genesis import (GENESIS_KIND, enqueue_genesis_proposal,
                             make_genesis_item)
from runtime.state import StateEmitter


def _item(**over):
    base = dict(
        roster_id="roster-recruitment",
        discipline="Recruitment",
        proposal_document="roster-genesis-proposal-recruitment.yaml",
        drafted_by="ecl_orchestrator_agent + ai_manager_agent",
        ladder_conclusion="pipeline/compliance/contract-drafting is an un-homed discipline.",
        created_iso="2026-07-07T09:00:00Z",
    )
    base.update(over)
    return make_genesis_item(**base)


class TestGenesis(unittest.TestCase):
    def setUp(self) -> None:
        self.workdir = tempfile.mkdtemp(prefix="runtime-genesis-")
        self.emitter = StateEmitter(self.workdir)

    def tearDown(self) -> None:
        shutil.rmtree(self.workdir, ignore_errors=True)

    def test_item_shape_matches_queue_schema(self):
        it = _item()
        self.assertEqual(it["kind"], GENESIS_KIND)
        self.assertEqual(it["id"], "GEN-roster-recruitment")
        self.assertEqual(it["linked_document"],
                         "roster-genesis-proposal-recruitment.yaml")
        # every field the dashboard inbox renders is present
        for key in ("title", "context", "options", "requested_by", "owner",
                    "created", "aom_class", "aom_timeout_hours"):
            self.assertIn(key, it)
        # no approve path in code: options are for the HUMAN
        self.assertIn("Approve", it["options"][0])

    def test_enqueue_writes_v1_snapshot(self):
        enqueue_genesis_proposal(self.emitter, "eng-demo", _item())
        doc = self.emitter.read_decisions_queue()
        self.assertEqual(doc["schema"], "decisions-queue/v1")
        self.assertEqual(doc["engagement"], "eng-demo")
        self.assertEqual(len(doc["open_items"]), 1)
        self.assertEqual(doc["open_items"][0]["kind"], GENESIS_KIND)

    def test_enqueue_is_idempotent(self):
        enqueue_genesis_proposal(self.emitter, "eng-demo", _item())
        enqueue_genesis_proposal(self.emitter, "eng-demo", _item())
        doc = self.emitter.read_decisions_queue()
        self.assertEqual(len(doc["open_items"]), 1)

    def test_enqueue_preserves_existing_items(self):
        other = {"id": "DQ-001", "kind": "HUMAN_GATE", "status": "PENDING"}
        self.emitter.write_decisions_queue("eng-demo", [other])
        items = enqueue_genesis_proposal(self.emitter, "eng-demo", _item())
        self.assertEqual([i["id"] for i in items],
                         ["DQ-001", "GEN-roster-recruitment"])

    def test_rejects_item_without_linked_document(self):
        it = _item()
        it["linked_document"] = None
        with self.assertRaises(ValueError):
            enqueue_genesis_proposal(self.emitter, "eng-demo", it)

    def test_rejects_non_genesis_kind(self):
        it = _item()
        it["kind"] = "HUMAN_GATE"
        with self.assertRaises(ValueError):
            enqueue_genesis_proposal(self.emitter, "eng-demo", it)


if __name__ == "__main__":
    unittest.main()
