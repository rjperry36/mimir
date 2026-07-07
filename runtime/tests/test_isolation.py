"""RSB-03 workspace isolation: concurrent agents get non-colliding workspaces."""

import os
import tempfile
import unittest

from runtime.isolation import WorkspaceManager


class TestIsolation(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ws-test-")

    def test_two_concurrent_agents_get_distinct_workspaces_and_ports(self):
        mgr = WorkspaceManager(self.root, port_base=8100)
        a = mgr.allocate("agent-a", needs_port=True)
        b = mgr.allocate("agent-b", needs_port=True)

        # distinct directories, both real, non-colliding
        self.assertNotEqual(a.path, b.path)
        self.assertTrue(os.path.isdir(a.path))
        self.assertTrue(os.path.isdir(b.path))
        # distinct ports
        self.assertIsNotNone(a.port)
        self.assertIsNotNone(b.port)
        self.assertNotEqual(a.port, b.port)

    def test_released_port_is_reusable(self):
        mgr = WorkspaceManager(self.root, port_base=8100)
        a = mgr.allocate("agent-a", needs_port=True)
        port_a = a.port
        mgr.release(a)
        b = mgr.allocate("agent-b", needs_port=True)
        # freed port can be reused now that agent-a is gone
        self.assertEqual(b.port, port_a)

    def test_double_allocation_same_id_raises(self):
        mgr = WorkspaceManager(self.root)
        mgr.allocate("dup", needs_port=False)
        with self.assertRaises(ValueError):
            mgr.allocate("dup", needs_port=False)


if __name__ == "__main__":
    unittest.main()
