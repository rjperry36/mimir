"""Structured state emission - the dashboard's data contract.

The kernel continuously writes four ledgers under an engagement's
``runtime-state/`` dir. These are exactly the four artifacts the Framework
Console brief (console-brief-v0.1.0) maps its views onto:

  * ``wave-status.yaml``        -> Console view 1 (wave board): per-wave state
                                   machine (PENDING/RUNNING/COMPLETE/DEAD/...).
  * ``metrics-ledger.jsonl``    -> Console view 2 (agent metrics timeline):
                                   one line per agent run.
  * ``integrity-register.jsonl``-> Console view 4 (integrity log): gate
                                   failures, dead agents, budget pauses.
  * ``decisions-queue.yaml``    -> Console view 5 (decision inbox): human gates
                                   awaiting approval.

Views 3/6/7 (learning-over-time, RAG, RAID) are deterministic *derivations* of
these ledgers + existing instance files, so they need nothing new here.

Also provides :class:`IdIssuer` - monotonic, lock-guarded ID issuance (RSB-05),
so concurrent appends cannot collide on IDs the way the pilot's learning-log did.
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import yaml


class WaveState(str, Enum):
    PENDING = "PENDING"          # not yet started
    RUNNING = "RUNNING"          # dispatched, executor active
    COMPLETE = "COMPLETE"        # finished, gate (if any) passed
    GATE_BLOCKED = "GATE_BLOCKED"  # finished but its gate failed
    BLOCKED = "BLOCKED"          # a dependency did not release it
    DEAD = "DEAD"                # heartbeats stopped (silent death)
    TIMED_OUT = "TIMED_OUT"      # blew past the hard deadline
    PAUSED = "PAUSED"            # halted at a budget ceiling, resumable
    AWAITING_APPROVAL = "AWAITING_APPROVAL"  # human gate pending


class IdIssuer:
    """Thread-safe monotonic ID issuance (RSB-05).

    The pilot produced duplicate learning-log IDs under concurrent appends
    because IDs were assigned by hand. This hands out strictly increasing,
    collision-free IDs behind a lock.
    """

    def __init__(self, prefix: str = "ID", start: int = 0) -> None:
        self._prefix = prefix
        self._n = start
        self._lock = threading.Lock()

    def next(self) -> str:
        with self._lock:
            self._n += 1
            return f"{self._prefix}-{self._n:05d}"


class StateEmitter:
    """Writes and continuously updates the four dashboard ledgers.

    wave-status and decisions-queue are full-state snapshots (rewritten on every
    change); metrics-ledger and integrity-register are append-only JSONL.
    Writes are atomic (temp file + os.replace) so a crash mid-write cannot leave
    a half-written ledger the dashboard would choke on.
    """

    def __init__(self, state_dir: str) -> None:
        self.state_dir = state_dir
        os.makedirs(state_dir, exist_ok=True)
        self.wave_status_path = os.path.join(state_dir, "wave-status.yaml")
        self.metrics_path = os.path.join(state_dir, "metrics-ledger.jsonl")
        self.integrity_path = os.path.join(state_dir, "integrity-register.jsonl")
        self.decisions_path = os.path.join(state_dir, "decisions-queue.yaml")
        self._lock = threading.Lock()
        self._metrics_ids = IdIssuer("MET")
        self._integrity_ids = IdIssuer("INT")

    # --- wave-status.yaml -------------------------------------------------
    def write_wave_status(self, engagement: str, waves: Dict[str, dict]) -> None:
        doc = {
            "engagement": engagement,
            "schema": "wave-status/v1",
            "waves": waves,
        }
        self._atomic_write_yaml(self.wave_status_path, doc)

    # --- decisions-queue.yaml --------------------------------------------
    def write_decisions_queue(self, engagement: str, items: List[dict]) -> None:
        doc = {
            "engagement": engagement,
            "schema": "decisions-queue/v1",
            "open_items": items,
        }
        self._atomic_write_yaml(self.decisions_path, doc)

    # --- metrics-ledger.jsonl (append) -----------------------------------
    def append_metrics(self, record: dict) -> str:
        with self._lock:
            record = {"id": self._metrics_ids.next(), **record}
            self._append_jsonl(self.metrics_path, record)
            return record["id"]

    # --- integrity-register.jsonl (append) -------------------------------
    def append_integrity(self, record: dict) -> str:
        with self._lock:
            record = {"id": self._integrity_ids.next(), **record}
            self._append_jsonl(self.integrity_path, record)
            return record["id"]

    # --- readers (for tests / dashboard) ---------------------------------
    def read_wave_status(self) -> dict:
        return self._read_yaml(self.wave_status_path)

    def read_decisions_queue(self) -> dict:
        return self._read_yaml(self.decisions_path)

    def read_metrics(self) -> List[dict]:
        return self._read_jsonl(self.metrics_path)

    def read_integrity(self) -> List[dict]:
        return self._read_jsonl(self.integrity_path)

    # --- internals --------------------------------------------------------
    @staticmethod
    def _atomic_write_yaml(path: str, doc: dict) -> None:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            yaml.safe_dump(doc, fh, sort_keys=False, default_flow_style=False)
        os.replace(tmp, path)

    @staticmethod
    def _append_jsonl(path: str, record: dict) -> None:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=False) + "\n")

    @staticmethod
    def _read_yaml(path: str) -> dict:
        if not os.path.exists(path):
            return {}
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    @staticmethod
    def _read_jsonl(path: str) -> List[dict]:
        if not os.path.exists(path):
            return []
        out: List[dict] = []
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out
