import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from build.verify_payload import verify_payload


class OfflinePayloadVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.catalog = self.root / "manifests/content-packs.json"
        self.manifest = self.root / "content-packs/core/manifest.json"
        self.manifest.parent.mkdir(parents=True)
        self.catalog.parent.mkdir(parents=True)
        self.manifest.write_text(json.dumps({"id": "core", "version": "1.2.3"}))
        self.catalog.write_text(json.dumps({"core_packs": ["../content-packs/core/manifest.json"]}))
        self.payload = self.root / "offline-payload.tar.zst"

    def make_payload(self, members):
        staging = self.root / "staging"
        for member in members:
            path = staging / member
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture")
        subprocess.run(
            ["tar", "--use-compress-program=zstd", "-cf", str(self.payload), "-C", str(staging), *members],
            check=True, capture_output=True,
        )

    def test_accepts_payload_with_all_declared_core_pack_files(self):
        members = [
            "content-packs/core-1.2.3.tar.zst",
            "content-packs/core-1.2.3.tar.zst.sha256",
        ]
        self.make_payload(members)
        self.assertEqual(verify_payload(self.payload, self.catalog), members)

    def test_rejects_stale_payload_missing_core_pack(self):
        self.make_payload(["content/ollama/models/fixture"])
        with self.assertRaisesRegex(ValueError, "missing required core pack files"):
            verify_payload(self.payload, self.catalog)


if __name__ == "__main__":
    unittest.main()
