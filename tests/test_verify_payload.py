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

    def make_map_payload(self, map_payload):
        maps_manifest = json.loads((Path(__file__).resolve().parents[1] / "payload/manifests/maps.json").read_text())
        members = [
            "content-packs/core-1.2.3.tar.zst",
            "content-packs/core-1.2.3.tar.zst.sha256",
            "manifests/maps.json",
            "manifests/map-payload.json",
            "content/maps/pmtiles/world.pmtiles",
        ]
        members.extend(f"content/maps/pmtiles/{item['file']}" for item in maps_manifest["regions"])
        staging = self.root / "map-staging"
        for member in members:
            path = staging / member
            path.parent.mkdir(parents=True, exist_ok=True)
            if member == "manifests/maps.json":
                content = json.dumps(maps_manifest)
            elif member == "manifests/map-payload.json":
                content = json.dumps(map_payload)
            else:
                content = "fixture"
            path.write_text(content)
        subprocess.run(
            ["tar", "--use-compress-program=zstd", "-cf", str(self.payload),
             "-C", str(staging), *members], check=True, capture_output=True,
        )
        return maps_manifest

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

    def test_rejects_superseded_core_pack_archive_when_current_version_exists(self):
        self.make_payload([
            "content-packs/core-1.2.3.tar.zst",
            "content-packs/core-1.2.3.tar.zst.sha256",
            "content-packs/core-1.2.2.tar.zst",
            "content-packs/core-1.2.2.tar.zst.sha256",
        ])
        with self.assertRaisesRegex(ValueError, "stale or unapproved content-pack files"):
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

    def test_map_payload_records_pinned_extractor_and_commands(self):
        maps_manifest = json.loads((Path(__file__).resolve().parents[1] / "payload/manifests/maps.json").read_text())
        regions = []
        for item in maps_manifest["regions"]:
            source = "/maps/world.pmtiles" if item["source"] == "world" else maps_manifest["source_build"]["url"]
            regions.append({
                **item,
                "extraction_command": [
                    "pmtiles", "extract", source, f"/maps/{item['file']}",
                    f"--bbox={item['bbox']}", f"--minzoom={item['minzoom']}",
                    f"--maxzoom={item['maxzoom']}",
                ],
                "derived_file": {
                    "bytes": item.get("expected_size_bytes", 10),
                    "sha256": item.get("expected_sha256", "b" * 64),
                },
            })
        map_payload = {
            "source_build": maps_manifest["source_build"],
            "extractor": maps_manifest["extractor"],
            "world_extraction_command": [
                "pmtiles", "extract", maps_manifest["source_build"]["url"],
                "/maps/world.pmtiles", "--bbox=-180,-85,180,85", "--maxzoom=5",
            ],
            "regions": regions,
        }
        embedded_manifest = self.root / "maps.json"
        embedded_manifest.write_text(json.dumps(maps_manifest))
        self.make_map_payload(map_payload)
        self.assertEqual(
            verify_payload(self.payload, self.catalog, embedded_manifest),
            ["content-packs/core-1.2.3.tar.zst", "content-packs/core-1.2.3.tar.zst.sha256"],
        )

    def test_rejects_map_payload_with_stale_extraction_command(self):
        maps_manifest = json.loads((Path(__file__).resolve().parents[1] / "payload/manifests/maps.json").read_text())
        regions = []
        for item in maps_manifest["regions"]:
            source = "/maps/world.pmtiles" if item["source"] == "world" else maps_manifest["source_build"]["url"]
            regions.append({
                **item,
                "extraction_command": ["pmtiles", "extract", source, f"/maps/{item['file']}",
                                       f"--bbox={item['bbox']}", f"--minzoom={item['minzoom']}",
                                       "--maxzoom=999"],
                "derived_file": {
                    "bytes": item.get("expected_size_bytes", 10),
                    "sha256": item.get("expected_sha256", "b" * 64),
                },
            })
        map_payload = {
            "source_build": maps_manifest["source_build"],
            "extractor": maps_manifest["extractor"],
            "world_extraction_command": [
                "pmtiles", "extract", maps_manifest["source_build"]["url"],
                "/maps/world.pmtiles", "--bbox=-180,-85,180,85", "--maxzoom=5",
            ],
            "regions": regions,
        }
        embedded_manifest = self.root / "maps.json"
        embedded_manifest.write_text(json.dumps(maps_manifest))
        self.make_map_payload(map_payload)
        with self.assertRaisesRegex(ValueError, "stale extraction command"):
            verify_payload(self.payload, self.catalog, embedded_manifest)


if __name__ == "__main__":
    unittest.main()
