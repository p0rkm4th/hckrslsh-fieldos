import errno
import hashlib
import importlib.util
import io
import json
import re
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
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
            "installation": {"target": "storage/content-packs", "requirements": [], "optional": False},
            "authority": "community-reference",
        }
        (self.pack / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (self.pack / "unlisted-private.txt").write_text("must not ship\n", encoding="utf-8")
        (manifests / "content-packs.json").write_text(json.dumps({
            "schema_version": 1,
            "manifest_schema": "content-pack.schema.json",
            "status": "ready",
            "packs": ["../content-packs/fixture-reference/manifest.json"],
            "core_packs": ["../content-packs/fixture-reference/manifest.json"],
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
        listing = subprocess.run(
            ["zstd", "--decompress", "--stdout", str(archive)],
            capture_output=True, check=True,
        ).stdout
        with tarfile.open(fileobj=io.BytesIO(listing), mode="r:") as tar:
            members = tar.getnames()
        self.assertIn("content-packs/fixture-reference/manifest.json", members)
        self.assertIn("content-packs/fixture-reference/guide.txt", members)
        self.assertNotIn("content-packs/fixture-reference/unlisted-private.txt", members)

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

    def test_core_only_builder_includes_only_declared_core_packs(self):
        archives = build_archives(
            self.payload / "manifests/content-packs.json", self.output, core_only=True
        )
        self.assertEqual([archive.name for archive in archives], ["fixture-reference-1.0.0.tar.zst"])

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

    def test_map_pack_is_activated_atomically_for_nomad_inventory(self):
        artifact = self.pack / "middle-tennessee.pmtiles"
        artifact.write_bytes(b"PMTiles test fixture")
        manifest_path = self.pack / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["title"] = "Test map fixture"
        manifest["description"] = "Synthetic PMTiles activation test; not geographic data."
        manifest["category"] = "maps-gis"
        manifest["geographic_coverage"] = {
            "name": "Middle Tennessee (synthetic fixture)",
            "bbox": [-87.5, 35.5, -85.5, 36.5], "minzoom": 5, "maxzoom": 12,
        }
        manifest["installation"]["target"] = "storage/maps/pmtiles"
        manifest["artifacts"] = [{
            "path": artifact.name, "size_bytes": artifact.stat().st_size,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "source": "fixture-source", "license": "CC0-1.0",
        }]
        manifest_path.write_text(json.dumps(manifest))
        archive = build_archives(self.payload / "manifests/content-packs.json", self.output)[0]

        first = CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        published = self.install_root / "storage/maps/pmtiles/middle-tennessee.pmtiles"
        self.assertIn("activated map:", first)
        self.assertEqual(published.read_bytes(), artifact.read_bytes())
        second = CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        self.assertIn("map already active:", second)
        self.assertEqual(published.read_bytes(), artifact.read_bytes())

    def test_map_activation_refuses_to_replace_existing_map(self):
        artifact = self.pack / "existing.pmtiles"
        artifact.write_bytes(b"new map")
        manifest_path = self.pack / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["installation"]["target"] = "storage/maps/pmtiles"
        manifest["artifacts"] = [{
            "path": artifact.name, "size_bytes": artifact.stat().st_size,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "source": "fixture-source", "license": "CC0-1.0",
        }]
        manifest_path.write_text(json.dumps(manifest))
        archive = build_archives(self.payload / "manifests/content-packs.json", self.output)[0]
        maps = self.install_root / "storage/maps/pmtiles"
        maps.mkdir(parents=True)
        existing = maps / artifact.name
        existing.write_bytes(b"keep the user's data")

        with self.assertRaisesRegex(CONTENT_PACKS.InstallError, "refusing to replace existing map content"):
            CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        self.assertEqual(existing.read_bytes(), b"keep the user's data")

    def configure_zim_pack(self, artifact_names=("reference.zim",)):
        artifacts = []
        for name in artifact_names:
            artifact = self.pack / name
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_bytes(f"synthetic zim payload: {name}".encode())
            artifacts.append({
                "path": name, "size_bytes": artifact.stat().st_size,
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "source": "fixture-source", "license": "CC0-1.0",
            })
        manifest_path = self.pack / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["title"] = "Offline Kiwix fixture"
        manifest["description"] = "Synthetic ZIM activation test fixture."
        manifest["installation"]["target"] = "storage/zim"
        manifest["artifacts"] = artifacts
        manifest_path.write_text(json.dumps(manifest))
        return build_archives(self.payload / "manifests/content-packs.json", self.output)[0]

    def kiwix_manage_fake(self, fail_action=None):
        zim_root = self.install_root / "storage/zim"
        def run(command, text, capture_output, check):
            image_index = command.index(CONTENT_PACKS.KIWIX_IMAGE)
            library_path = zim_root / Path(command[image_index + 1]).name
            action = command[image_index + 2]
            if action == fail_action:
                return subprocess.CompletedProcess(command, 1, "", "synthetic kiwix-manage failure")
            if action == "add":
                if not library_path.exists():
                    library_path.write_text("<library/>", encoding="utf-8")
                tree = ET.parse(library_path)
                root = tree.getroot()
                paths = command[image_index + 3:]
                if len(paths) != 1:
                    return subprocess.CompletedProcess(command, 1, "", "expected one ZIM path")
                # Kiwix 3.8.1 records a path attribute relative to the library
                # directory, even when kiwix-manage receives /data/<archive>.
                relative_path = Path(paths[0]).relative_to("/data").as_posix()
                book = ET.SubElement(root, "book", path=relative_path)
                ET.SubElement(book, "id").text = Path(paths[0]).stem
                tree.write(library_path, encoding="unicode")
                return subprocess.CompletedProcess(command, 0, "", "")
            self.fail(f"unexpected kiwix-manage action: {action}")
        return run

    def test_zim_pack_activates_in_kiwix_library_and_is_idempotent(self):
        archive = self.configure_zim_pack(("reference.zim", "nested/second.zim"))
        with patch.object(CONTENT_PACKS.subprocess, "run", side_effect=self.kiwix_manage_fake()) as run:
            first = CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
            self.assertIn("activated Kiwix ZIM archives", first)
            zim_root = self.install_root / "storage/zim"
            zim_file = zim_root / "reference.zim"
            installed_file = self.install_root / "content-packs/fixture-reference/1.0.0/reference.zim"
            self.assertEqual(zim_file.read_bytes(), b"synthetic zim payload: reference.zim")
            self.assertEqual(zim_file.stat().st_mode & 0o777, 0o644)
            self.assertEqual(zim_file.stat().st_ino, installed_file.stat().st_ino,
                             "same-filesystem activation should hard-link, not duplicate, the ZIM")
            self.assertEqual((zim_root / "nested/second.zim").read_bytes(), b"synthetic zim payload: nested/second.zim")
            library = ET.parse(zim_root / "kiwix-library.xml").getroot()
            self.assertEqual(
                {book.attrib["path"] for book in library.findall("book")},
                {"reference.zim", "nested/second.zim"},
            )
            second = CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
            self.assertIn("Kiwix ZIM archives already active", second)
            add_calls = [call for call in run.call_args_list
                         if call.args[0][call.args[0].index(CONTENT_PACKS.KIWIX_IMAGE) + 2] == "add"]
            self.assertEqual(len(add_calls), 2)

    def test_zim_pack_activates_by_verified_copy_when_hardlinks_are_disallowed(self):
        archive = self.configure_zim_pack()
        zim_root = self.install_root / "storage/zim"
        real_link = CONTENT_PACKS.os.link

        def link_or_deny_pack_source(source, destination, *args, **kwargs):
            source, destination = Path(source), Path(destination)
            if source.name == "reference.zim" and destination == zim_root / "reference.zim":
                raise OSError(errno.EPERM, "hard links disabled by filesystem policy")
            return real_link(source, destination, *args, **kwargs)

        with patch.object(CONTENT_PACKS.os, "link", side_effect=link_or_deny_pack_source):
            with patch.object(CONTENT_PACKS.subprocess, "run", side_effect=self.kiwix_manage_fake()):
                result = CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)

        self.assertIn("activated Kiwix ZIM archives", result)
        source = self.install_root / "content-packs/fixture-reference/1.0.0/reference.zim"
        activated = zim_root / "reference.zim"
        self.assertEqual(CONTENT_PACKS.file_sha256(source), CONTENT_PACKS.file_sha256(activated))
        self.assertEqual(activated.stat().st_mode & 0o777, 0o644)
        self.assertNotEqual(source.stat().st_ino, activated.stat().st_ino)
        library = ET.parse(zim_root / "kiwix-library.xml").getroot()
        self.assertEqual([book.attrib["path"] for book in library.findall("book")], ["reference.zim"])

    def test_zim_pack_preserves_existing_library_and_refuses_filename_conflict(self):
        archive = self.configure_zim_pack()
        zim_root = self.install_root / "storage/zim"
        zim_root.mkdir(parents=True)
        library = zim_root / "kiwix-library.xml"
        library.write_text("<library><book><id>existing</id><path>/data/existing.zim</path></book></library>")
        original_library = library.read_bytes()
        (zim_root / "reference.zim").write_bytes(b"operator's existing archive")
        with patch.object(CONTENT_PACKS.subprocess, "run", side_effect=self.kiwix_manage_fake()):
            with self.assertRaisesRegex(CONTENT_PACKS.InstallError, "refusing to replace existing ZIM content"):
                CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        self.assertEqual(library.read_bytes(), original_library)
        self.assertEqual((zim_root / "reference.zim").read_bytes(), b"operator's existing archive")

    def test_zim_pack_failure_leaves_existing_library_unchanged_and_removes_new_archive(self):
        archive = self.configure_zim_pack()
        zim_root = self.install_root / "storage/zim"
        zim_root.mkdir(parents=True)
        library = zim_root / "kiwix-library.xml"
        original = b"<library><book><id>existing</id><path>/data/existing.zim</path></book></library>"
        library.write_bytes(original)
        with patch.object(CONTENT_PACKS.subprocess, "run", side_effect=self.kiwix_manage_fake(fail_action="add")):
            with self.assertRaisesRegex(CONTENT_PACKS.InstallError, "Kiwix library update failed"):
                CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        self.assertEqual(library.read_bytes(), original)
        self.assertFalse((zim_root / "reference.zim").exists())

    def test_zim_pack_rejects_non_zim_artifacts(self):
        artifact = self.pack / "not-a-zim.txt"
        artifact.write_text("not a ZIM archive", encoding="utf-8")
        manifest_path = self.pack / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["installation"]["target"] = "storage/zim"
        manifest["artifacts"] = [{
            "path": artifact.name, "size_bytes": artifact.stat().st_size,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "source": "fixture-source", "license": "CC0-1.0",
        }]
        manifest_path.write_text(json.dumps(manifest))
        archive = build_archives(self.payload / "manifests/content-packs.json", self.output)[0]
        with self.assertRaisesRegex(CONTENT_PACKS.InstallError, "Kiwix packs may contain only ZIM artifacts"):
            CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)

    def test_kiwix_library_paths_normalizes_real_relative_book_path_attributes(self):
        self.install_root.mkdir(parents=True, exist_ok=True)
        library = self.install_root / "kiwix-relative-library.xml"
        library.write_text(
            '<library><book id="fixture" path="nested/reference.zim" title="Fixture" />'
            '<book id="absolute" path="/data/absolute.zim" /></library>',
            encoding="utf-8",
        )
        self.assertEqual(
            CONTENT_PACKS.kiwix_library_paths(library),
            {"/data/nested/reference.zim", "/data/absolute.zim"},
        )

    def test_reference_documents_activate_in_local_source_index(self):
        artifact = self.pack / "water-guide.pdf"
        artifact.write_bytes(b"%PDF-1.4 synthetic test document")
        manifest_path = self.pack / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["title"] = "Emergency Water Reference"
        manifest["description"] = "Synthetic source-pack test, not safety guidance."
        manifest["category"] = "water-food"
        manifest["installation"]["target"] = "storage/references/documents"
        manifest["authority"] = "authoritative-reference"
        manifest["artifacts"] = [{
            "path": artifact.name, "size_bytes": artifact.stat().st_size,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "source": "fixture-source", "license": "Public Domain",
        }]
        manifest_path.write_text(json.dumps(manifest))
        archive = build_archives(self.payload / "manifests/content-packs.json", self.output)[0]

        first = CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        index = self.install_root / "storage/references/index.html"
        page = index.read_text()
        self.assertIn("activated reference documents:", first)
        self.assertIn("Emergency Water Reference", page)
        self.assertIn("Fixture source", page)
        self.assertIn("Test fixture", page)
        self.assertIn("water-guide.pdf", page)
        self.assertIn("documents/fixture-reference/1.0.0/water-guide.pdf", page)
        published = self.install_root / "storage/references/documents/fixture-reference/1.0.0/water-guide.pdf"
        self.assertEqual(published.read_bytes(), artifact.read_bytes())

        second = CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        self.assertIn("already installed:", second)
        self.assertIn("water-guide.pdf", index.read_text())
        self.assertEqual(published.read_bytes(), artifact.read_bytes())

    def test_source_library_search_filters_plain_text_documents_offline(self):
        artifact = self.pack / "communications-plan.txt"
        content = "Primary out-of-area contact: write down name, phone, and city/state.\n"
        artifact.write_text(content, encoding="utf-8")
        manifest_path = self.pack / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["title"] = "Household Communications Plan"
        manifest["description"] = "A local planning worksheet."
        manifest["installation"]["target"] = "storage/references/documents"
        manifest["artifacts"] = [{
            "path": artifact.name, "size_bytes": artifact.stat().st_size,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "source": "fixture-source", "license": "CC0-1.0",
            "title": "Searchable text companion", "index_with_ai": False,
        }]
        manifest_path.write_text(json.dumps(manifest))
        archive = build_archives(self.payload / "manifests/content-packs.json", self.output)[0]

        CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        page = (self.install_root / "storage/references/index.html").read_text()
        self.assertIn('<label for="source-search">Search installed offline sources</label>', page)
        self.assertIn('data-body="Primary out-of-area contact: write down name, phone, and city/state.', page)
        self.assertIn("Searchable text companion", page)
        self.assertIn("Open PDFs and longer documents", page)
        self.assertIn("documents/fixture-reference/1.0.0/communications-plan.txt", page)

        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable for the Source Library search behavior check")
        search_script = re.search(r"<script>\s*(.*?)\s*</script>", page, re.DOTALL).group(1)
        harness = r"""
const assert = require('node:assert/strict')
const documents = [
  { dataset: { search: 'Household Communications Plan', body: 'Primary out-of-area contact: write down name, phone, and city/state.' }, hidden: false, match: { hidden: true, textContent: '' }, querySelector() { return this.match } },
  { dataset: { search: 'Winter Storm Safety', body: 'Prepare for cold weather and power outages.' }, hidden: false, match: { hidden: true, textContent: '' }, querySelector() { return this.match } },
]
const packs = [{ hidden: false, querySelectorAll() { return documents } }]
const input = { value: '', addEventListener(event, handler) { this.handler = handler } }
const status = { textContent: '' }
global.document = {
  getElementById(id) { return id === 'source-search' ? input : status },
  querySelectorAll(selector) { return selector === '.source-document' ? documents : packs },
}
"""
        assertions = r"""
input.value = 'primary out-of-area contact'
input.handler()
assert.equal(status.textContent, '1 matching document')
assert.equal(documents[0].hidden, false)
assert.equal(documents[1].hidden, true)
assert.match(documents[0].match.textContent, /write down name, phone/)
input.value = 'winter'
input.handler()
assert.equal(status.textContent, '1 matching document')
assert.equal(documents[0].hidden, true)
assert.equal(documents[1].hidden, false)
input.value = 'no such local source'
input.handler()
assert.equal(status.textContent, '0 matching documents')
assert.equal(packs[0].hidden, true)
"""
        subprocess.run([node, "-e", harness + "\n;\n" + search_script + "\n" + assertions], check=True)

    def test_reference_activation_refuses_to_replace_operator_index(self):
        artifact = self.pack / "guide.pdf"
        artifact.write_bytes(b"%PDF-1.4 fixture")
        manifest_path = self.pack / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["installation"]["target"] = "storage/references/documents"
        manifest["artifacts"] = [{
            "path": artifact.name, "size_bytes": artifact.stat().st_size,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "source": "fixture-source", "license": "CC0-1.0",
        }]
        manifest_path.write_text(json.dumps(manifest))
        refs = self.install_root / "storage/references"
        refs.mkdir(parents=True)
        index = refs / "index.html"
        index.write_text("operator's own index")
        archive = build_archives(self.payload / "manifests/content-packs.json", self.output)[0]

        with self.assertRaisesRegex(CONTENT_PACKS.InstallError, "non-FieldOS reference index"):
            CONTENT_PACKS.install_bundle(archive, self.install_root, self.schema, reserve_bytes=0)
        self.assertEqual(index.read_text(), "operator's own index")


if __name__ == "__main__":
    unittest.main()
