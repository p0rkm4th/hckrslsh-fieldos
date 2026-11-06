import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fieldos_e2e", ROOT / "tests/test_e2e.py")
E2E = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(E2E)


class E2EKiwixHelperTests(unittest.TestCase):
    def test_optional_zim_target_is_supported_without_changing_existing_targets(self):
        self.assertTrue(E2E.e2e_content_pack_target_supported("storage/zim"))
        self.assertTrue(E2E.e2e_content_pack_target_supported("storage/maps/pmtiles"))
        self.assertTrue(E2E.e2e_content_pack_target_supported("storage/references/documents"))
        self.assertFalse(E2E.e2e_content_pack_target_supported("storage/arbitrary"))

    def test_kiwix_name_and_content_url_follow_filename_rules(self):
        name = E2E.kiwix_zim_name("nested/Guide + Café.zim")
        self.assertEqual(name, "guide_plus_cafe")
        self.assertEqual(
            E2E.kiwix_content_url(name),
            "http://127.0.0.1:8090/content/guide_plus_cafe",
        )

    def test_library_and_opds_catalog_entries_match_id_or_title(self):
        library = (
            '<library><book id="urn:uuid:zim-1" title="Offline Field Guide" '
            'path="/data/field-guide.zim" /></library>'
        )
        identity = E2E.kiwix_library_identity(library, "field-guide.zim")
        self.assertEqual(identity, {
            "id": "urn:uuid:zim-1", "title": "Offline Field Guide", "path": "/data/field-guide.zim",
        })
        self.assertEqual(E2E.kiwix_library_ids(library), {"urn:uuid:zim-1"})
        catalog = (
            '<feed xmlns="http://www.w3.org/2005/Atom"><entry>'
            '<id>urn:uuid:zim-1</id><title>Offline Field Guide</title>'
            '</entry></feed>'
        )
        self.assertEqual(
            E2E.kiwix_catalog_entry(catalog, identity),
            {"id": "urn:uuid:zim-1", "title": "Offline Field Guide"},
        )

    def test_library_id_parser_handles_child_element_and_attribute_formats(self):
        library = (
            '<library><book id="urn:uuid:attribute-id" path="/data/a.zim">'
            '<id>urn:uuid:element-id</id></book></library>'
        )
        self.assertEqual(
            E2E.kiwix_library_ids(library),
            {"urn:uuid:attribute-id", "urn:uuid:element-id"},
        )

    def test_catalog_parser_supports_title_match_when_ids_are_not_exposed(self):
        catalog = (
            '<feed xmlns="http://www.w3.org/2005/Atom"><entry>'
            '<id>opds-entry</id><title>Offline Field Guide</title>'
            '</entry></feed>'
        )
        result = E2E.kiwix_catalog_entry(catalog, {"id": "different-id", "title": "Offline Field Guide"})
        self.assertEqual(result, {"id": "opds-entry", "title": "Offline Field Guide"})

    def test_library_parser_rejects_invalid_xml(self):
        with self.assertRaisesRegex(E2E.TestFailure, "invalid library XML"):
            E2E.kiwix_library_identity("<library>", "pack.zim")


if __name__ == "__main__":
    unittest.main()
