import json
import re
import unittest
from pathlib import Path


MANIFEST = Path(__file__).resolve().parents[1] / "payload" / "manifests" / "source-offers.json"


class SourceOfferManifestTests(unittest.TestCase):
    def test_source_offers_are_pinned_and_have_source_descriptors(self):
        manifest = json.loads(MANIFEST.read_text())
        self.assertEqual(manifest["schema_version"], 1)
        offers = manifest["source_offers"]
        self.assertTrue(offers)
        for offer in offers:
            self.assertTrue(offer["name"])
            self.assertTrue(offer["version"])
            self.assertTrue(offer["source"].startswith("https://"))
            files = offer["files"]
            self.assertTrue(any(item["name"].endswith(".dsc") for item in files))
            self.assertEqual(len({item["name"] for item in files}), len(files))
            for item in files:
                self.assertTrue(item["url"].startswith("https://"))
                self.assertGreater(item["size_bytes"], 0)
                self.assertRegex(item["sha256"], re.compile(r"^[0-9a-f]{64}$"))


if __name__ == "__main__":
    unittest.main()
