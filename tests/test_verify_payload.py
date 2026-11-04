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

    def test_rejects_generated_ollama_key_files(self):
        members = [
            "content-packs/core-1.2.3.tar.zst",
            "content-packs/core-1.2.3.tar.zst.sha256",
            "content/ollama/id_ed25519.pub",
        ]
        self.make_payload(members)
        with self.assertRaisesRegex(ValueError, "generated Ollama keys"):
            verify_payload(self.payload, self.catalog)

    def test_rejects_ollama_recommendation_cache(self):
        members = [
            "content-packs/core-1.2.3.tar.zst",
            "content-packs/core-1.2.3.tar.zst.sha256",
            "content/ollama/cache/library/qwen3.json",
        ]
        self.make_payload(members)
        with self.assertRaisesRegex(ValueError, "generated Ollama keys or recommendation cache"):
            verify_payload(self.payload, self.catalog)

    def test_rejects_payload_with_stale_map_manifest(self):
        maps_manifest = self.root / "maps.json"
        maps_manifest.write_text(json.dumps({"regions": [{"id": "current"}]}))
        members = [
            "content-packs/core-1.2.3.tar.zst",
            "content-packs/core-1.2.3.tar.zst.sha256",
            "manifests/maps.json",
        ]
        staging = self.root / "staging"
        for member in members:
            path = staging / member
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"regions": [{"id": "stale"}]})
                            if member == "manifests/maps.json" else "fixture")
        subprocess.run(
            ["tar", "--use-compress-program=zstd", "-cf", str(self.payload),
             "-C", str(staging), *members], check=True, capture_output=True,
        )
        with self.assertRaisesRegex(ValueError, "map manifest is stale"):
            verify_payload(self.payload, self.catalog, maps_manifest)

    def test_rejects_payload_missing_source_map_files(self):
        expected_hash = "a" * 64
        maps_manifest = self.root / "maps.json"
        current_maps = {"regions": [{
            "id": "region", "file": "region.pmtiles",
            "expected_size_bytes": 12, "expected_sha256": expected_hash,
        }]}
        maps_manifest.write_text(json.dumps(current_maps))
        map_payload = {"regions": [{
            "id": "region", "file": "region.pmtiles",
            "derived_file": {"bytes": 12, "sha256": expected_hash},
        }]}
        members = [
            "content-packs/core-1.2.3.tar.zst",
            "content-packs/core-1.2.3.tar.zst.sha256",
            "manifests/maps.json",
            "manifests/map-payload.json",
            "content/maps/pmtiles/world.pmtiles",
        ]
        staging = self.root / "staging"
        for member in members:
            path = staging / member
            path.parent.mkdir(parents=True, exist_ok=True)
            if member == "manifests/maps.json":
                content = json.dumps(current_maps)
            elif member == "manifests/map-payload.json":
                content = json.dumps(map_payload)
            else:
                content = "fixture"
            path.write_text(content)
        subprocess.run(
            ["tar", "--use-compress-program=zstd", "-cf", str(self.payload),
             "-C", str(staging), *members], check=True, capture_output=True,
        )
        with self.assertRaisesRegex(ValueError, "missing source map files"):
            verify_payload(self.payload, self.catalog, maps_manifest)


if __name__ == "__main__":
    unittest.main()
