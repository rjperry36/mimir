"""Per-sub-milestone checkpointing (RSB-01 checkpointing).

State is persisted after every wave so a killed / restarted run RESUMES without
redoing completed waves (idempotent). This is the design-level fix for the
pilot's L-appdev-011, where recovery worked only by code hygiene, not by design.

The checkpoint is a small YAML file recording, per wave, its terminal state and
result plus the budget consumed so far. On restart the kernel loads it and skips
any wave already ``COMPLETE``.
"""

from __future__ import annotations

import os
from typing import Dict

import yaml


class Checkpointer:
    def __init__(self, path: str) -> None:
        self.path = path
        self._data: Dict = {"schema": "checkpoint/v1", "waves": {}, "budget_consumed": 0.0}
        if os.path.exists(path):
            self._data = self._load()

    def _load(self) -> Dict:
        with open(self.path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {"waves": {}, "budget_consumed": 0.0}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            yaml.safe_dump(self._data, fh, sort_keys=False)
        os.replace(tmp, self.path)  # atomic: crash mid-write can't corrupt it

    # --- queries ----------------------------------------------------------
    def is_complete(self, wave_id: str) -> bool:
        rec = self._data["waves"].get(wave_id)
        return bool(rec and rec.get("state") == "COMPLETE")

    def wave_record(self, wave_id: str) -> dict:
        return self._data["waves"].get(wave_id, {})

    def completed_waves(self) -> list:
        return [w for w, r in self._data["waves"].items()
                if r.get("state") == "COMPLETE"]

    @property
    def budget_consumed(self) -> float:
        return float(self._data.get("budget_consumed", 0.0))

    # --- mutations (each persists immediately) ---------------------------
    def record_wave(self, wave_id: str, state: str, result: dict | None = None,
                    gate: dict | None = None) -> None:
        self._data["waves"][wave_id] = {
            "state": state,
            "result": result or {},
            "gate": gate or {},
        }
        self._save()

    def set_budget_consumed(self, amount: float) -> None:
        self._data["budget_consumed"] = float(amount)
        self._save()
