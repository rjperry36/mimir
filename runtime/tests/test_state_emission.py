"""Structured state emission: the four dashboard ledgers exist and are well-formed."""

import json
import os

import yaml

from runtime.executor import MockExecutor, MockScenario
from runtime.gates import Gate
from runtime.kernel import EngagementSpec, WaveSpec
from runtime.state import IdIssuer

from .helpers import KernelTestCase


def _fail_gate(_r):
    return False, "boom"


class TestStateEmission(KernelTestCase):
    def test_all_four_ledgers_exist_and_are_well_formed(self):
        executor = MockExecutor(
            scenarios={"w_gate": MockScenario(behaviour="complete", duration=4.0,
                                              metrics={"tokens": 1200,
                                                       "tool_uses": 7})},
            default=MockScenario(behaviour="complete", duration=4.0,
                                 metrics={"tokens": 900, "tool_uses": 4}))
        kernel = self.make_kernel(executor, approver=lambda w: False)
        eng = EngagementSpec("eng-state", [
            WaveSpec("w1", "pm_agent"),
            WaveSpec("w_gate", "sec_agent", depends_on=["w1"],
                     gate=Gate("g", _fail_gate)),
            WaveSpec("w_human", "release_agent", human_gate=True),
        ])
        kernel.run(eng)

        sd = kernel.state_dir
        # 1. files exist
        for name in ("wave-status.yaml", "metrics-ledger.jsonl",
                     "integrity-register.jsonl", "decisions-queue.yaml"):
            self.assertTrue(os.path.exists(os.path.join(sd, name)),
                            f"missing {name}")

        # 2. wave-status.yaml well-formed state machine
        ws = yaml.safe_load(open(os.path.join(sd, "wave-status.yaml")))
        self.assertEqual(ws["schema"], "wave-status/v1")
        self.assertIn("w1", ws["waves"])
        self.assertIn("state", ws["waves"]["w1"])

        # 3. metrics-ledger.jsonl: one JSON object per line, monotonic ids
        lines = [l for l in open(os.path.join(sd, "metrics-ledger.jsonl"))
                 if l.strip()]
        recs = [json.loads(l) for l in lines]
        self.assertTrue(recs)
        for r in recs:
            self.assertIn("agent_id", r)
            self.assertIn("termination_cause", r)
            self.assertTrue(r["id"].startswith("MET-"))
        ids = [r["id"] for r in recs]
        self.assertEqual(ids, sorted(ids))  # monotonic, no collisions

        # 4. integrity-register.jsonl has the gate failure
        integ = [json.loads(l) for l in
                 open(os.path.join(sd, "integrity-register.jsonl"))
                 if l.strip()]
        self.assertTrue(any(r["type"] == "GATE_FAILURE" for r in integ))

        # 5. decisions-queue.yaml has the pending human gate
        dq = yaml.safe_load(open(os.path.join(sd, "decisions-queue.yaml")))
        self.assertEqual(dq["schema"], "decisions-queue/v1")
        self.assertTrue(any(i["wave"] == "w_human"
                            for i in dq["open_items"]))

    def test_id_issuer_is_monotonic_and_unique(self):
        issuer = IdIssuer("MET")
        ids = [issuer.next() for _ in range(100)]
        self.assertEqual(len(set(ids)), 100)      # no duplicates (RSB-05)
        self.assertEqual(ids, sorted(ids))         # monotonic

    def test_id_issuer_threadsafe_no_collisions(self):
        import threading
        issuer = IdIssuer("X")
        out = []
        lock = threading.Lock()

        def worker():
            local = [issuer.next() for _ in range(200)]
            with lock:
                out.extend(local)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(out), len(set(out)))  # 1600 unique ids
