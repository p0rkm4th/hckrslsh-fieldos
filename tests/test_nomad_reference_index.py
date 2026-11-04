import hashlib
import importlib.util
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fieldos_nomad_reference_index", ROOT / "scripts/fieldos-nomad-index-references.py"
)
INDEXER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INDEXER)


class FakeNomadHandler(BaseHTTPRequestHandler):
    files = []
    uploads = 0

    def log_message(self, *_args):
        pass

    def _json(self, status, value):
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/rag/files":
            return self._json(200, {"files": self.files})
        self._json(404, {})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("latin1")
        if self.path != "/api/rag/upload" or 'name="file"' not in body:
            return self._json(404, {})
        marker = 'filename="'
        name = body.split(marker, 1)[1].split('"', 1)[0]
        type(self).uploads += 1
        self.files.append({
            "fileName": f"{name}-{type(self).uploads:012d}.pdf",
            "source": f"/app/storage/kb_uploads/{name}-{type(self).uploads:012d}.pdf",
            "state": "indexed",
            "chunksEmbedded": 3,
            "collection": INDEXER.COLLECTION,
        })
        self._json(202, {"message": "queued"})


class NomadReferenceIndexTests(unittest.TestCase):
    def setUp(self):
        FakeNomadHandler.files = []
        FakeNomadHandler.uploads = 0
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeNomadHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/"
        self.temporary = TemporaryDirectory()
        self.root = Path(self.temporary.name)
        pack = self.root / "content-packs/test-pack/1.0.0"
        pack.mkdir(parents=True)
        document = pack / "guide.pdf"
        document.write_bytes(b"%PDF-1.4 fixture source text")
        manifest = {
            "id": "test-pack",
            "version": "1.0.0",
            "installation": {"target": "storage/references/documents"},
            "artifacts": [{
                "path": "guide.pdf",
                "size_bytes": document.stat().st_size,
                "sha256": hashlib.sha256(document.read_bytes()).hexdigest(),
            }],
        }
        (pack / "manifest.json").write_text(json.dumps(manifest))

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary.cleanup()

    def test_indexes_pack_document_and_is_idempotent(self):
        expected_name = "fieldos-test-pack-1.0.0-guide.pdf"
        first = INDEXER.index_references(self.root, self.url, timeout=2, interval=0.01)
        second = INDEXER.index_references(self.root, self.url, timeout=2, interval=0.01)
        self.assertEqual(first, [(expected_name, 3)])
        self.assertEqual(second, first)
        self.assertEqual(FakeNomadHandler.uploads, 1)
        self.assertEqual(FakeNomadHandler.files[0]["collection"], INDEXER.COLLECTION)

    def test_refuses_manifest_checksum_mismatch(self):
        manifest_path = self.root / "content-packs/test-pack/1.0.0/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["artifacts"][0]["sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(INDEXER.IndexError, "manifest validation"):
            INDEXER.list_documents(self.root)
        self.assertEqual(FakeNomadHandler.uploads, 0)


if __name__ == "__main__":
    unittest.main()
