import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ImageLicenseManifestTests(unittest.TestCase):
    def test_redis_74_digest_is_not_mislabeled_bsd(self):
        manifest = json.loads((ROOT / "payload/manifests/images.json").read_text())
        image = next(item for item in manifest["images"] if item["name"] == "redis")
        self.assertEqual(image["ref"], "redis:7-alpine")
        self.assertEqual(image["observed_version"], "7.4.12")
        self.assertEqual(image["digest"], "sha256:8da19c7399dca900c6822a1cf30f9d2285585e2c4b457ff4095b0f4500054d3f")
        self.assertEqual(image["license"], "RSALv2 OR SSPLv1")
        self.assertIn("redis-adopts-dual-source-available-licensing", image["license_url"])

        compose = (ROOT / "services/compose.yaml").read_text()
        self.assertIn("redis:7-alpine@" + image["digest"], compose)


if __name__ == "__main__":
    unittest.main()
