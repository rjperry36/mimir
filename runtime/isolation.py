"""Workspace + port isolation for concurrent agents (RSB-03).

The pilot's PT-06: concurrent agents clobbered a shared ``.next`` build because
they had no isolation. The kernel gives every agent run its own directory and,
if it needs to serve, a distinct port drawn from a pool - so parallel waves
cannot collide on shared build state.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Set


@dataclass(frozen=True)
class Workspace:
    """An isolated working area for one agent run."""

    run_id: str
    path: str
    port: Optional[int]


class WorkspaceManager:
    """Allocates non-colliding workspaces (and ports) under a root dir."""

    def __init__(self, root: str, port_base: int = 8100, port_span: int = 900):
        self.root = root
        self._port_base = port_base
        self._port_span = port_span
        self._used_paths: Set[str] = set()
        self._used_ports: Set[int] = set()
        os.makedirs(root, exist_ok=True)

    def allocate(self, run_id: str, needs_port: bool = True) -> Workspace:
        path = os.path.join(self.root, run_id)
        if path in self._used_paths:
            raise ValueError(f"workspace already allocated for {run_id!r}")
        os.makedirs(path, exist_ok=True)
        self._used_paths.add(path)

        port: Optional[int] = None
        if needs_port:
            port = self._next_free_port()
            self._used_ports.add(port)
        return Workspace(run_id=run_id, path=path, port=port)

    def release(self, workspace: Workspace) -> None:
        self._used_paths.discard(workspace.path)
        if workspace.port is not None:
            self._used_ports.discard(workspace.port)

    def _next_free_port(self) -> int:
        for offset in range(self._port_span):
            candidate = self._port_base + offset
            if candidate not in self._used_ports:
                return candidate
        raise RuntimeError("no free ports left in the isolation pool")
