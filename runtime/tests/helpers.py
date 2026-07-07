"""Shared test helpers."""

from __future__ import annotations

import shutil
import tempfile
import unittest

from runtime.clock import ManualClock
from runtime.kernel import Kernel, KernelConfig


class KernelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.workdir = tempfile.mkdtemp(prefix="runtime-test-")
        self.clock = ManualClock()
        # small, deterministic timings
        self.config = KernelConfig(heartbeat_grace=3.0, wave_timeout=30.0,
                                   poll_interval=0.5)

    def tearDown(self) -> None:
        shutil.rmtree(self.workdir, ignore_errors=True)

    def make_kernel(self, executor, subdir="eng", clock=None, config=None,
                    approver=None) -> Kernel:
        return Kernel(f"{self.workdir}/{subdir}", executor,
                      clock=clock or self.clock,
                      config=config or self.config, approver=approver)
