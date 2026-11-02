import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).parents[1] / "installer/provisioning/build_local_apt_index.py"
SPEC = importlib.util.spec_from_file_location("build_local_apt_index", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LocalAptIndexTests(unittest.TestCase):
    def test_index_points_into_payload_package_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            deb_dir = root / "debs"
            deb_dir.mkdir()
            (deb_dir / "curl_1_amd64.deb").write_bytes(b"deb")
            fields = {
                "Package": "curl",
                "Version": "1",
                "Architecture": "amd64",
                "Depends": "libcurl4 (= 1)",
            }

            def fake_field(command, text):
                return fields.get(command[-1], "")

            with patch.object(MODULE.subprocess, "check_output", side_effect=fake_field):
                MODULE.build_index(deb_dir, root / "Packages")

            index = (root / "Packages").read_text()
            self.assertIn("Package: curl\n", index)
            self.assertIn("Filename: debs/curl_1_amd64.deb\n", index)
            self.assertIn("Depends: libcurl4 (= 1)\n", index)


if __name__ == "__main__":
    unittest.main()
