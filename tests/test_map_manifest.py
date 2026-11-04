import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RegionalMapManifestTests(unittest.TestCase):
    def test_bundled_tennessee_map_covers_state_and_is_checksum_pinned(self):
        manifest = json.loads((ROOT / "payload/manifests/maps.json").read_text())
        region = next(item for item in manifest["regions"] if item["id"] == "tennessee-statewide")
        self.assertEqual(region["file"], "tennessee-20261102-z13.pmtiles")
        self.assertEqual(region["bbox"], "-90.9,34.5,-81.0,37.25")
        self.assertEqual((region["minzoom"], region["maxzoom"]), (0, 13))
        self.assertEqual(region["source"], "pinned-build")
        self.assertEqual(region["expected_size_bytes"], 145_267_908)
        self.assertEqual(
            region["expected_sha256"],
            "0d123132839b77e627c4f4f103bf7a78925099c57319e759757be3207cb89525",
        )
        self.assertEqual(manifest["license"], "ODbL-1.0")
        self.assertIn("OpenStreetMap contributors", manifest["attribution"])


if __name__ == "__main__":
    unittest.main()
