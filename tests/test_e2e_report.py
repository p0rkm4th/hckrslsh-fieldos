import subprocess
import unittest
from unittest.mock import Mock, patch

from test_e2e import AcceptanceRun, git_source_state, write_preflight_report


class E2ESourceStateTests(unittest.TestCase):
    def test_check_forwards_long_guest_command_timeout(self):
        run = AcceptanceRun.__new__(AcceptanceRun)
        run.results = []
        run.guest = Mock(return_value="index complete")

        result = run.check("reference indexing", "index-command", timeout=1200)

        self.assertEqual(result, "index complete")
        run.guest.assert_called_once_with("index-command", timeout=1200)

    @patch(
        "test_e2e.subprocess.run",
        side_effect=[
            subprocess.CompletedProcess([], 0, "abc123\n", ""),
            subprocess.CompletedProcess([], 0, " M hardware/detect/detect.py\n", ""),
        ],
    )
    def test_reports_commit_and_dirty_state(self, _run):
        self.assertEqual(git_source_state(), ("abc123", True))

    @patch(
        "test_e2e.subprocess.run",
        return_value=subprocess.CompletedProcess([], 1, "", "git unavailable"),
    )
    def test_failed_git_query_is_unknown(self, _run):
        self.assertEqual(git_source_state(), ("unknown", None))

    def test_preflight_failure_writes_small_report_only(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp:
            root = Path(temp) / "e2e"
            report = write_preflight_report(root, "fixed-stamp", "Need 48 GiB free")
            self.assertEqual(report.read_text(encoding="utf-8"),
                             "# FieldOS E2E preflight\n\nStatus: **FAIL**\n\n"
                             "Reason: Need 48 GiB free\n\n"
                             "No ISO, VM disk, or test credentials were created.\n")
            self.assertEqual(sorted(item.name for item in root.iterdir()), [report.name])


if __name__ == "__main__":
    unittest.main()
