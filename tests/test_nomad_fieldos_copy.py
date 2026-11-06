import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "installer/provisioning/patch-nomad-fieldos-copy.js"


class FieldOSNomadCopyPatchTests(unittest.TestCase):
    def test_maps_home_tile_opens_at_useful_tennessee_overview_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            asset = Path(temporary) / "home.js"
            asset.write_text(
                'const ge={label:"Maps",to:"/maps",target:"",description:"View offline maps"};'
                'Offline access to Wikipedia, medical references, how-to guides, and encyclopedias;'
                'Complete Wikipedia offline;Medical references and first aid guides;'
                'DIY repair guides and how-to content;Project Gutenberg books and literature;',
                encoding="utf-8",
            )

            first = subprocess.run(
                ["node", str(PATCH), temporary], capture_output=True, text=True, check=True
            )
            patched = asset.read_text(encoding="utf-8")
            self.assertIn('to:"/maps?lat=35.86&lng=-86.35&zoom=7"', patched)
            self.assertNotIn('to:"/maps"', patched)

            second = subprocess.run(
                ["node", str(PATCH), temporary], capture_output=True, text=True, check=True
            )
            self.assertIn("already patched", second.stdout)
            self.assertEqual(asset.read_text(encoding="utf-8"), patched)


if __name__ == "__main__":
    unittest.main()
