import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RegionalMapManifestTests(unittest.TestCase):
    def test_bundled_tennessee_map_is_bounded_and_checksum_pinned(self):
        manifest = json.loads((ROOT / "payload/manifests/maps.json").read_text())
        region = next(item for item in manifest["regions"] if item["id"] == "middle-tennessee")
        self.assertEqual(region["file"], "middle-tennessee-20261102-z13.pmtiles")
        self.assertEqual(region["bbox"], "-88.5,35.4,-85.7,36.7")
        self.assertEqual((region["minzoom"], region["maxzoom"]), (0, 13))
        self.assertEqual(region["source"], "pinned-build")
        self.assertEqual(region["expected_size_bytes"], 19_609_616)
        self.assertEqual(
            region["expected_sha256"],
            "d3f059ebe098d058dde9c7a1ee046cef80dff8df061e4846d61e262cdff50a66",
        )
        self.assertEqual(manifest["license"], "ODbL-1.0")
        self.assertIn("OpenStreetMap contributors", manifest["attribution"])


if __name__ == "__main__":
    unittest.main()
