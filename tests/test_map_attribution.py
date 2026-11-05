import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / "build" / "patch_map_attribution.py"
UPSTREAM = (
    '<a href="https://github.com/protomaps/basemaps">Protomaps</a> '
    '© <a href="https://openstreetmap.org">OpenStreetMap</a>'
)
FIELDOS = (
    '<a href="https://www.openstreetmap.org/copyright">'
    '© OpenStreetMap contributors</a> · '
    '<a href="https://github.com/protomaps/basemaps">Protomaps Basemaps</a> · '
    '<a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a>'
)


class MapAttributionTests(unittest.TestCase):
    def run_patcher(self, style):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "style.json"
            path.write_text(json.dumps(style, ensure_ascii=False, indent=2) + "\n")
            result = subprocess.run(
                [sys.executable, str(PATCHER), str(path)],
                text=True,
                capture_output=True,
            )
            content = path.read_text(encoding="utf-8")
            return result, content

    def test_patches_all_protomaps_sources_and_is_idempotent(self):
        style = {
            "sources": {
                "protomaps": {"url": "pmtiles://./tn.pmtiles", "attribution": UPSTREAM},
                "other": {"url": "https://example.invalid/tiles", "attribution": "Other"},
            },
            "nested": [{
                "sources": {
                    "protomaps-extra": {"url": "pmtiles://./world.pmtiles", "attribution": UPSTREAM}
                }
            }],
        }
        result, patched = self.run_patcher(style)
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = json.loads(patched)
        self.assertEqual(parsed["sources"]["protomaps"]["attribution"], FIELDOS)
        self.assertEqual(parsed["nested"][0]["sources"]["protomaps-extra"]["attribution"], FIELDOS)
        self.assertEqual(parsed["sources"]["other"]["attribution"], "Other")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "style.json"
            path.write_text(patched, encoding="utf-8")
            second = subprocess.run([sys.executable, str(PATCHER), str(path)], capture_output=True)
            self.assertEqual(second.returncode, 0, second.stderr.decode())
            self.assertEqual(path.read_text(encoding="utf-8"), patched)

    def test_fails_closed_on_unknown_attribution(self):
        style = {"sources": {"protomaps": {"url": "pmtiles://./tn.pmtiles", "attribution": "unknown"}}}
        result, _ = self.run_patcher(style)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unexpected upstream", result.stderr)

    def test_fails_when_no_protomaps_source_exists(self):
        style = {"sources": {"other": {"url": "https://example.invalid/tiles", "attribution": "Other"}}}
        result, _ = self.run_patcher(style)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No Protomaps sources", result.stderr)

    def test_sprite_mit_notice_is_bundled_by_payload_build(self):
        notice = (ROOT / "payload" / "licenses" / "TANGRAMS-ICONS-MIT.txt").read_text()
        builder = (ROOT / "build" / "prepare-payload.sh").read_text()
        self.assertIn("Copyright (c) 2017 Mapzen", notice)
        self.assertIn("permission notice shall be included", notice)
        self.assertIn("TANGRAMS-ICONS-MIT.txt", builder)


if __name__ == "__main__":
    unittest.main()
