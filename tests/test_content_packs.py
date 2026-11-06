import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from payload.validate_content_packs import PackError, validate_catalog


ROOT = Path(__file__).resolve().parents[1]


class ContentPackValidationTests(unittest.TestCase):
    def test_repository_catalog_validates_reviewed_core_and_optional_packs(self):
        catalog_path = ROOT / "payload/manifests/content-packs.json"
        self.assertEqual(
            validate_catalog(catalog_path),
            ["us-basic-emergency-health", "us-cdc-keep-calm-prepared", "us-flood-safety",
             "us-household-communications", "us-medlineplus-first-aid",
             "us-niosh-heat-first-aid", "us-southeastern-vegetable-growers", "us-tornado-safety",
             "us-water-food-emergency", "us-weather-safety"],
        )
        catalog = json.loads(catalog_path.read_text())
        core = [catalog_path.parent.joinpath(entry).resolve().parent.name for entry in catalog["core_packs"]]
        self.assertCountEqual(
            core,
            [
                "us-flood-safety",
                "us-cdc-keep-calm-prepared",
                "us-medlineplus-first-aid",
                "us-niosh-heat-first-aid",
                "us-southeastern-vegetable-growers",
                "us-tornado-safety",
                "us-water-food-emergency",
                "us-weather-safety",
            ],
        )

    def fixture(self, category="agriculture", coverage=None, authority=None, review=None,
                geographic_scope=None):
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
            "installation": {"target": "storage/content-packs", "requirements": []},
            "authority": authority or "community-reference",
        }
        if geographic_scope is not None:
            manifest["geographic_scope"] = geographic_scope
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

    def test_artifact_can_link_all_declared_source_records(self):
        catalog, manifest, pack = self.fixture()
        manifest["sources"].append({
            "id": "fixture-source-two", "name": "Second source",
            "url": "https://example.invalid/second", "license": "CC0-1.0",
            "attribution": "Second source attribution",
        })
        manifest["artifacts"][0]["sources"] = ["fixture-source", "fixture-source-two"]
        (pack / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(validate_catalog(catalog), ["fixture-reference"])

    def test_artifact_multi_source_links_must_be_declared_and_include_primary(self):
        catalog, manifest, pack = self.fixture()
        manifest["artifacts"][0]["sources"] = ["fixture-source", "undeclared"]
        (pack / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(PackError, "undeclared sources"):
            validate_catalog(catalog)

    def test_explicit_text_geographic_scope_is_valid_without_a_map_bbox(self):
        catalog, manifest, pack = self.fixture(
            geographic_scope="Southeastern United States, including Tennessee"
        )
        self.assertIsNone(manifest["geographic_coverage"])
        (pack / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(validate_catalog(catalog), ["fixture-reference"])

    def test_core_pack_must_be_listed_and_nonoptional(self):
        catalog, _, _ = self.fixture()
        data = json.loads(catalog.read_text())
        data["core_packs"] = ["../content-packs/not-listed/manifest.json"]
        catalog.write_text(json.dumps(data))
        with self.assertRaisesRegex(PackError, "also be listed"):
            validate_catalog(catalog)

        data["core_packs"] = ["../content-packs/fixture-reference/manifest.json"]
        catalog.write_text(json.dumps(data))
        with self.assertRaisesRegex(PackError, "optional=false"):
            validate_catalog(catalog)

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
        catalog, _, _ = self.fixture(category="weather-disaster")
        with self.assertRaisesRegex(PackError, "authoritative references"):
            validate_catalog(catalog)

        catalog, _, _ = self.fixture(
            category="weather-disaster",
            authority="authoritative-reference",
            review={"reviewer": "Field editor", "reviewed_at": "2026-11-03",
                    "content_revision": "2026-10-15"},
        )
        self.assertEqual(validate_catalog(catalog), ["fixture-reference"])

    def test_cdc_checklist_metadata_pins_source_public_domain_and_artifact(self):
        manifest = json.loads(
            (ROOT / "payload/content-packs/us-cdc-keep-calm-prepared/manifest.json").read_text()
        )
        self.assertEqual(manifest["authority"], "authoritative-reference")
        self.assertIn("Public Domain", manifest["sources"][0]["license"])
        self.assertEqual(
            manifest["artifacts"][0]["sha256"],
            "d8d3ad68df32f5c069968e5f71d58e2e03bd3751e985877f28122a988388f319",
        )
        catalog = ROOT / "payload/manifests/content-packs.json"
        self.assertIn("us-cdc-keep-calm-prepared", validate_catalog(catalog))

    def test_medlineplus_pack_records_the_policy_basis_separately(self):
        manifest = json.loads(
            (ROOT / "payload/content-packs/us-medlineplus-first-aid/manifest.json").read_text()
        )
        policy = next(item for item in manifest["sources"] if item["id"] == "nlm-medlineplus-reuse-policy")
        self.assertEqual(policy["url"], "https://medlineplus.gov/about/using/usingcontent/")
        self.assertIn("not bundled", policy["license"])

    def test_flood_summary_links_both_underlying_nws_pages(self):
        manifest = json.loads(
            (ROOT / "payload/content-packs/us-flood-safety/manifest.json").read_text()
        )
        self.assertEqual(
            manifest["artifacts"][0]["sources"],
            ["nws-flood-before", "nws-flood-during"],
        )

    def test_handbook_records_its_regional_scope_without_claiming_a_map_bbox(self):
        manifest = json.loads(
            (ROOT / "payload/content-packs/us-southeastern-vegetable-growers/manifest.json").read_text()
        )
        self.assertIsNone(manifest["geographic_coverage"])
        self.assertIn("including Tennessee", manifest["geographic_scope"])

    def test_authored_communications_planner_is_not_mislabeled_as_authoritative(self):
        manifest = json.loads(
            (ROOT / "payload/content-packs/us-household-communications/manifest.json").read_text()
        )
        self.assertEqual(manifest["category"], "communications")
        self.assertEqual(manifest["authority"], "fieldos-authored")
        self.assertIn("Original FieldOS-authored text", manifest["artifacts"][0]["license"])
        catalog = ROOT / "payload/manifests/content-packs.json"
        self.assertIn("us-household-communications", validate_catalog(catalog))

    def test_vegetable_handbook_credits_publisher_listed_authors(self):
        manifest = json.loads(
            (ROOT / "payload/content-packs/us-southeastern-vegetable-growers/manifest.json").read_text()
        )
        self.assertEqual(manifest["version"], "2026.1.2")
        self.assertEqual(
            manifest["geographic_scope"],
            "Southeastern United States, including Tennessee; not a Tennessee-specific calendar",
        )
        source = manifest["sources"][0]
        for author in (
            "Mark S. Reiter", "Tom P. Kuhar", "Kemper Sutton", "Laura Strawn",
            "Douglas S. Higgins", "Steve L. Rideout", "Vijay Singh",
        ):
            with self.subTest(author=author):
                self.assertIn(author, source["attribution"])
        self.assertIn("Virginia Cooperative Extension", source["attribution"])
        self.assertIn("Virginia Tech", source["attribution"])
        self.assertIn("Virginia State University", source["attribution"])
        self.assertIn("public use, reprint, or citation", source["license"])
        self.assertIn("the author", source["license"])

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
