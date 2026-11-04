#!/usr/bin/env python3
"""Index installed FieldOS reference-pack documents in N.O.M.A.D.'s RAG KB."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import time
import re
import secrets
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_ROOT = Path("/var/lib/fieldos")
DEFAULT_URL = "http://127.0.0.1:8080/"
COLLECTION = "FieldOS Core References"
SUPPORTED_TYPES = {".pdf", ".txt"}


class IndexError(RuntimeError):
    pass


def request_json(url: str, method: str = "GET", body: bytes | None = None,
                 headers: dict[str, str] | None = None, timeout: int = 30) -> dict:
    request = Request(url, data=body, method=method, headers=headers or {})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        detail = exc.read().decode("utf-8", "replace") if isinstance(exc, HTTPError) else str(exc)
        raise IndexError(f"N.O.M.A.D. request failed: {detail[:400]}") from exc
    try:
        decoded = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IndexError("N.O.M.A.D. returned invalid JSON") from exc
    if not isinstance(decoded, dict):
        raise IndexError("N.O.M.A.D. returned an unexpected response")
    return decoded


def list_documents(storage_root: Path) -> list[tuple[str, Path, str]]:
    found: list[tuple[str, Path, str]] = []
    packs_root = storage_root / "content-packs"
    if packs_root.is_symlink():
        raise IndexError(f"Content-pack root must not be a symbolic link: {packs_root}")
    for manifest_path in sorted(packs_root.glob("*/*/manifest.json")):
        if manifest_path.is_symlink():
            raise IndexError(f"Pack manifest must not be a symbolic link: {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("installation", {}).get("target") != "storage/references/documents":
            continue
        pack_id, version = manifest.get("id"), manifest.get("version")
        if manifest_path.parent != packs_root / str(pack_id) / str(version):
            raise IndexError(f"Pack manifest location does not match its identity: {manifest_path}")
        for artifact in manifest.get("artifacts", []):
            rel = Path(artifact.get("path", ""))
            if rel.is_absolute() or ".." in rel.parts or rel.suffix.lower() not in SUPPORTED_TYPES:
                continue
            path = manifest_path.parent / rel
            if any(part.is_symlink() for part in [manifest_path.parent, *path.parents[:-1], path]):
                raise IndexError(f"Reference artifact path contains a symbolic link: {path}")
            try:
                path.resolve(strict=True).relative_to(manifest_path.parent.resolve(strict=True))
            except (OSError, ValueError) as exc:
                raise IndexError(f"Reference artifact escapes its installed pack: {path}") from exc
            if not path.is_file():
                raise IndexError(f"Reference artifact is missing or unsafe: {path}")
            digest_hash = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest_hash.update(chunk)
            digest = digest_hash.hexdigest()
            if path.stat().st_size != artifact.get("size_bytes") or digest != artifact.get("sha256"):
                raise IndexError(f"Reference artifact failed manifest validation: {path.name}")
            safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", f"fieldos-{pack_id}-{version}-{path.name}")
            found.append((safe_name, path, digest))
    return found


def stored_files(base_url: str) -> list[dict]:
    result = request_json(urljoin(base_url, "api/rag/files"))
    files = result.get("files")
    if not isinstance(files, list):
        raise IndexError("N.O.M.A.D. did not return its knowledge-base file list")
    return [row for row in files if isinstance(row, dict)]


def upload(base_url: str, name: str, path: Path) -> None:
    boundary = f"----FieldOSReferencePack{secrets.token_hex(12)}"
    content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
    data = path.read_bytes()
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"collection\"\r\n\r\n{COLLECTION}\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\nContent-Type: {content_type}\r\n\r\n".encode(),
        data,
        f"\r\n--{boundary}--\r\n".encode(),
    ])
    request_json(
        urljoin(base_url, "api/rag/upload"), "POST", body,
        {"Content-Type": f"multipart/form-data; boundary={boundary}"}, timeout=120,
    )


def wait_until_indexed(base_url: str, name: str, timeout: int, interval: float) -> dict:
    deadline = time.monotonic() + timeout
    last_error = ""
    while time.monotonic() < deadline:
        try:
            row = next((item for item in stored_files(base_url)
                        if str(item.get("fileName", "")).startswith(name + "-")), None)
            last_error = ""
        except IndexError as exc:
            last_error = str(exc)
            time.sleep(interval)
            continue
        if row and row.get("state") == "indexed" and int(row.get("chunksEmbedded") or 0) > 0:
            return row
        if row and row.get("state") in {"failed", "error"}:
            raise IndexError(f"N.O.M.A.D. failed to index {name}; inspect its Knowledge Base status")
        time.sleep(interval)
    detail = f" ({last_error})" if last_error else ""
    raise IndexError(f"Timed out waiting for N.O.M.A.D. to index {name}{detail}")


def index_references(storage_root: Path, base_url: str, timeout: int = 900,
                     interval: float = 5.0) -> list[tuple[str, int]]:
    documents = list_documents(storage_root)
    if not documents:
        return []
    base_url = base_url.rstrip("/") + "/"
    deadline = time.monotonic() + timeout
    last_error = ""
    while True:
        try:
            existing = stored_files(base_url)
            break
        except IndexError as exc:
            last_error = str(exc)
            if time.monotonic() >= deadline:
                raise IndexError(f"Timed out waiting for N.O.M.A.D. Knowledge Base{': ' + last_error}") from exc
            time.sleep(min(interval, max(0, deadline - time.monotonic())))
    results = []
    for name, path, _digest in documents:
        match = next((row for row in existing
                      if str(row.get("fileName", "")).startswith(name + "-")), None)
        if not match:
            upload(base_url, name, path)
        indexed = wait_until_indexed(base_url, name, timeout, interval)
        results.append((name, int(indexed.get("chunksEmbedded", 0))))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    try:
        indexed = index_references(args.storage_root, args.url, args.timeout)
        if not indexed:
            print("No installed reference documents need N.O.M.A.D. indexing.")
            return 0
        for name, chunks in indexed:
            print(f"Indexed {name}: {chunks} chunks")
        return 0
    except (IndexError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FieldOS reference indexing failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
