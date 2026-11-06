import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ImageLicenseManifestTests(unittest.TestCase):
    def test_valkey_image_is_pinned_and_uses_a_bsd_license(self):
        manifest = json.loads((ROOT / "payload/manifests/images.json").read_text())
        image = next(item for item in manifest["images"] if item["name"] == "valkey")
        self.assertEqual(image["ref"], "valkey/valkey:8.0-alpine")
        self.assertEqual(image["observed_version"], "8.0.12")
        self.assertEqual(image["digest"], "sha256:19f0b3d350f5e6de618086d79ecdc9c474ab159bebb16ed95a92e4211562fee5")
        self.assertEqual(image["license"], "BSD-3-Clause")
        self.assertIn("github.com/valkey-io/valkey", image["license_url"])

        compose = (ROOT / "services/compose.yaml").read_text()
        self.assertIn("valkey/valkey:8.0-alpine@" + image["digest"], compose)
        self.assertIn("/var/lib/fieldos/valkey:/data", compose)
        self.assertIn("container_name: nomad_valkey", compose)


if __name__ == "__main__":
    unittest.main()
