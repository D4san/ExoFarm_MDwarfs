"""Signal guards tested without touching any live worker."""

import signal
import unittest
from unittest.mock import patch

import rebalance_proxima_a0_1000h_mpi5 as migration


class IdentitySafety(unittest.TestCase):
    def test_reused_pid_is_not_signaled(self):
        record = {"pid": 123, "start_ticks": "1", "command": "expected"}
        with patch.object(migration, "identity", return_value={**record, "start_ticks": "2"}), \
                patch.object(migration.os, "kill") as kill:
            with self.assertRaises(RuntimeError):
                migration.signal_exact(record, signal.SIGSTOP)
            kill.assert_not_called()

    def test_changed_command_is_not_signaled(self):
        record = {"pid": 123, "start_ticks": "1", "command": "expected"}
        with patch.object(migration, "identity", return_value={**record, "command": "other"}), \
                patch.object(migration.os, "kill") as kill:
            with self.assertRaises(RuntimeError):
                migration.signal_exact(record, signal.SIGKILL)
            kill.assert_not_called()

    def test_existing_recovery_cannot_launch(self):
        with patch.object(migration.Path, "exists", return_value=True), \
                patch.object(migration.os, "kill") as kill:
            with self.assertRaisesRegex(RuntimeError, "never duplicate"):
                migration.rebalance()
            kill.assert_not_called()


if __name__ == "__main__":
    unittest.main()
