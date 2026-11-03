import subprocess
import unittest
from unittest.mock import patch

from test_e2e import git_source_state


class E2ESourceStateTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
