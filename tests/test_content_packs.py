import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from payload.validate_content_packs import PackError, validate_catalog


ROOT = Path(__file__).resolve().parents[1]


class ContentPackValidationTests(unittest.TestCase):
    def test_repository_catalog_validates_the_reviewed_reference_pack(self):
        self.assertEqual(
            validate_catalog(ROOT / "payload/manifests/content-packs.json"),
            ["us-water-food-emergency"],
        )

    def fixture(self, category="agriculture", coverage=None, authority=None, review=None):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        payload = Path(temp.name) / "payload"
        manifests = payload / "manifests"
        pack = payload / "content-packs/fixture-reference"
        artifacts = pack / "documents"
        manifests.mkdir(parents=True)
        artifacts.mkdir(parents=True)
        (manifests / "content-pack.schema.json").write_text(
            json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema"}),
            encoding="utf-8",
        )
        content = b"Offline reference fixture\n"
        (artifacts / "reference.txt").write_bytes(content)
        manifest = {
            "schema_version": 1,
            "id": "fixture-reference",
            "version": "1.0.0",
            "title": "Fixture reference",
            "description": "A test-only content pack.",
            "category": category,
            "sources": [{
                "id": "fixture-source",
                "name": "Fixture source",
                "url": "https://example.invalid/reference",
                "license": "CC0-1.0",
                "attribution": "Fixture source attribution",
                "accessed": "2026-11-03",
            }],
            "artifacts": [{
                "path": "documents/reference.txt",
                "size_bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
                "source": "fixture-source",
                "license": "CC0-1.0",
            }],
            "geographic_coverage": coverage,
            "installation": {"target": "references/fixture-reference", "requirements": []},
            "authority": authority or "community-reference",
        }
        if review is not None:
            manifest["review"] = review
        (pack / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        catalog = {
            "schema_version": 1,
            "manifest_schema": "content-pack.schema.json",
            "status": "ready",
            "packs": ["../content-packs/fixture-reference/manifest.json"],
            "planned_categories": ["agriculture"],
        }
        catalog_path = manifests / "content-packs.json"
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        return catalog_path, manifest, pack

    def test_valid_manifest_checks_artifact_and_metadata(self):
        catalog, _, _ = self.fixture(coverage={
            "name": "Test region", "bbox": [-74.1, 40.5, -73.7, 40.9],
            "minzoom": 5, "maxzoom": 12, "crs": "EPSG:4326",
        })
        self.assertEqual(validate_catalog(catalog), ["fixture-reference"])

    def test_artifact_hash_and_size_must_match(self):
        catalog, _, pack = self.fixture()
        (pack / "documents/reference.txt").write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(PackError, "size mismatch|SHA-256 mismatch"):
            validate_catalog(catalog)

    def test_artifact_paths_cannot_escape_pack_directory(self):
        catalog, manifest, _ = self.fixture()
        manifest["artifacts"][0]["path"] = "../../outside.txt"
        (catalog.parent.parent / "content-packs/fixture-reference/manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        with self.assertRaisesRegex(PackError, "stay inside"):
            validate_catalog(catalog)

    def test_artifact_must_reference_a_declared_source(self):
        catalog, manifest, _ = self.fixture()
        manifest["artifacts"][0]["source"] = "unknown-source"
        (catalog.parent.parent / "content-packs/fixture-reference/manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        with self.assertRaisesRegex(PackError, "undeclared source"):
            validate_catalog(catalog)

    def test_emergency_pack_requires_authority_and_review_record(self):
        catalog, _, _ = self.fixture(category="first-aid-emergency")
        with self.assertRaisesRegex(PackError, "authoritative references"):
            validate_catalog(catalog)

        catalog, _, _ = self.fixture(
            category="first-aid-emergency",
            authority="authoritative-reference",
            review={"reviewer": "Field editor", "reviewed_at": "2026-11-03",
                    "content_revision": "2026-10-15"},
        )
        self.assertEqual(validate_catalog(catalog), ["fixture-reference"])

    def test_invalid_geographic_bounds_are_rejected(self):
        catalog, _, _ = self.fixture(coverage={
            "name": "Invalid", "bbox": [-200, 40, -73, 41],
            "minzoom": 3, "maxzoom": 5,
        })
        with self.assertRaisesRegex(PackError, "bbox"):
            validate_catalog(catalog)

    def test_installation_target_cannot_escape_pack_storage(self):
        catalog, manifest, _ = self.fixture()
        manifest["installation"]["target"] = "../../etc"
        (catalog.parent.parent / "content-packs/fixture-reference/manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        with self.assertRaisesRegex(PackError, "target.*relative path"):
            validate_catalog(catalog)

    def test_dates_use_extended_iso_format(self):
        catalog, manifest, _ = self.fixture()
        manifest["sources"][0]["accessed"] = "20261103"
        (catalog.parent.parent / "content-packs/fixture-reference/manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        with self.assertRaisesRegex(PackError, "YYYY-MM-DD"):
            validate_catalog(catalog)


if __name__ == "__main__":
    unittest.main()
