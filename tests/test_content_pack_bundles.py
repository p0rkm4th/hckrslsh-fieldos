import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from build.build_content_packs import build_archives

SPEC = importlib.util.spec_from_file_location(
    "fieldos_content_packs", Path(__file__).resolve().parents[1] / "scripts/fieldos-content-packs.py"
)
CONTENT_PACKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTENT_PACKS)


@unittest.skipUnless(shutil.which("zstd") and shutil.which("tar"), "tar and zstd are build dependencies")
class ContentPackBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.payload = self.base / "payload"
        self.pack = self.payload / "content-packs" / "fixture-reference"
        self.pack.mkdir(parents=True)
        manifests = self.payload / "manifests"
        manifests.mkdir()
        self.schema = manifests / "content-pack.schema.json"
        self.schema.write_text(
            (Path(__file__).resolve().parents[1] / "payload/manifests/content-pack.schema.json").read_text(),
            encoding="utf-8",
        )
        artifact = self.pack / "guide.txt"
        artifact.write_text("offline fixture guide\n", encoding="utf-8")
        manifest = {
            "schema_version": 1,
            "id": "fixture-reference",
            "version": "1.0.0",
            "title": "Fixture field reference",
            "description": "A test-only reference fixture.",
            "category": "agriculture",
            "sources": [{
                "id": "fixture-source", "name": "Fixture source",
                "url": "https://example.invalid/reference", "license": "CC0-1.0",
                "attribution": "Test fixture",
            }],
            "artifacts": [{
                "path": "guide.txt", "size_bytes": artifact.stat().st_size,
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "source": "fixture-source", "license": "CC0-1.0",
            }],
            "geographic_coverage": None,
            "installation": {"target": "storage/content-packs", "requirements": [], "optional": True},
            "authority": "community-reference",
        }
        (self.pack / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (manifests / "content-packs.json").write_text(json.dumps({
            "schema_version": 1,
            "manifest_schema": "content-pack.schema.json",
            "status": "ready",
            "packs": ["../content-packs/fixture-reference/manifest.json"],
        }), encoding="utf-8")
        self.output = self.base / "output"
        self.install_root = self.base / "installed"

    def tearDown(self):
        self.temp.cleanup()

    def test_independent_bundle_build_install_list_and_idempotence(self):
        archives = build_archives(self.payload / "manifests/content-packs.json", self.output)
        self.assertEqual(len(archives), 1)
        archive = archives[0]
        self.assertEqual(archive.name, "fixture-reference-1.0.0.tar.zst")
        self.assertTrue(Path(f"{archive}.sha256").is_file())

        first = CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        self.assertIn("installed:", first)
        installed = self.install_root / "content-packs/fixture-reference/1.0.0"
        self.assertEqual((installed / "guide.txt").read_text(), "offline fixture guide\n")
        self.assertEqual(CONTENT_PACKS.list_packs(self.install_root), [
            ("fixture-reference", "1.0.0", installed)
        ])
        second = CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        self.assertIn("already installed:", second)

    def test_builder_refuses_overwriting_existing_bundle(self):
        build_archives(self.payload / "manifests/content-packs.json", self.output)
        with self.assertRaises(FileExistsError):
            build_archives(self.payload / "manifests/content-packs.json", self.output)

    def test_install_rejects_corrupt_bundle_checksum(self):
        archive = build_archives(self.payload / "manifests/content-packs.json", self.output)[0]
        archive.write_bytes(archive.read_bytes() + b"corrupt")
        with self.assertRaisesRegex(CONTENT_PACKS.InstallError, "SHA-256 mismatch"):
            CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)

    def test_install_refuses_to_overwrite_existing_version(self):
        archive = build_archives(self.payload / "manifests/content-packs.json", self.output)[0]
        CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        installed = self.install_root / "content-packs/fixture-reference/1.0.0"
        (installed / ".bundle.sha256").write_text("wrong\n", encoding="ascii")
        with self.assertRaisesRegex(CONTENT_PACKS.InstallError, "refusing to replace existing pack data"):
            CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)

    def test_install_refuses_a_symlink_at_the_version_path(self):
        archive = build_archives(self.payload / "manifests/content-packs.json", self.output)[0]
        outside = self.base / "outside"
        outside.mkdir()
        id_root = self.install_root / "content-packs/fixture-reference"
        id_root.mkdir(parents=True)
        (id_root / "1.0.0").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(CONTENT_PACKS.InstallError, "symlink as installed pack data"):
            CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
