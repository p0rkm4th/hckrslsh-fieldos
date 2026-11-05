#!/usr/bin/env python3
"""Verify, list, and install immutable FieldOS offline content-pack bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import html
from urllib.parse import quote
from pathlib import Path, PurePosixPath

SCRIPT_DIR = Path(__file__).resolve().parent
for module_dir in (SCRIPT_DIR, SCRIPT_DIR.parent / "payload"):
    if (module_dir / "validate_content_packs.py").is_file():
        sys.path.insert(0, str(module_dir))
        break
from validate_content_packs import PackError, validate_catalog, validate_manifest  # noqa: E402

DEFAULT_ROOT = Path("/var/lib/fieldos")
DEFAULT_SCHEMA = Path("/opt/fieldos/payload/manifests/content-pack.schema.json")
RESERVE_BYTES = 256 * 1024 * 1024
MAX_SOURCE_LIBRARY_TEXT_BYTES = 1024 * 1024
MAX_FILES = 100_000


class InstallError(RuntimeError):
    pass


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_bundle_checksum(archive: Path) -> str:
    sidecar = Path(f"{archive}.sha256")
    try:
        fields = sidecar.read_text(encoding="ascii").strip().split()
    except OSError as exc:
        raise InstallError(f"required checksum sidecar is unavailable: {sidecar}") from exc
    if len(fields) != 2 or fields[1] != archive.name or len(fields[0]) != 64:
        raise InstallError("checksum sidecar must contain SHA-256 and the exact archive filename")
    actual = file_sha256(archive)
    if actual != fields[0]:
        raise InstallError(f"bundle SHA-256 mismatch: expected {fields[0]}, got {actual}")
    return actual


def safe_member(member: tarfile.TarInfo) -> PurePosixPath:
    name = member.name
    path = PurePosixPath(name)
    if not name or "\\" in name or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise InstallError(f"unsafe archive path: {name!r}")
    if len(path.parts) < 2 or path.parts[0] != "content-packs":
        raise InstallError(f"bundle path must be beneath content-packs/<id>: {name!r}")
    if member.issym() or member.islnk() or member.isdev() or not (member.isdir() or member.isfile()):
        raise InstallError(f"bundle contains a non-regular filesystem entry: {name!r}")
    return path


def scan_bundle(archive: Path) -> tuple[str, int, int]:
    process = subprocess.Popen(["zstd", "--decompress", "--stdout", str(archive)], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    assert process.stdout is not None
    ids: set[str] = set()
    seen: set[str] = set()
    total = count = 0
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as tar:
            for member in tar:
                path = safe_member(member)
                ids.add(path.parts[1])
                if member.name in seen:
                    raise InstallError(f"duplicate archive entry: {member.name}")
                seen.add(member.name)
                count += 1
                if count > MAX_FILES:
                    raise InstallError(f"bundle exceeds {MAX_FILES} filesystem entries")
                total += member.size
        stderr = process.stderr.read() if process.stderr else b""
        result = process.wait()
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stdout.close()
        if process.stderr:
            process.stderr.close()
    if result:
        raise InstallError(f"zstd could not read bundle: {stderr.decode(errors='replace')}")
    if len(ids) != 1:
        raise InstallError("bundle must contain exactly one content-pack ID")
    return ids.pop(), total, count


def extract_bundle(archive: Path, stage: Path, expected_id: str) -> None:
    process = subprocess.Popen(["zstd", "--decompress", "--stdout", str(archive)], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    assert process.stdout is not None
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as tar:
            for member in tar:
                path = safe_member(member)
                if path.parts[1] != expected_id:
                    raise InstallError("bundle pack ID changed between inspection and extraction")
                target = stage.joinpath(*path.parts)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True, mode=0o755)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
                source = tar.extractfile(member)
                if source is None:
                    raise InstallError(f"cannot extract archive member: {member.name}")
                with source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
                target.chmod(0o644)
        stderr = process.stderr.read() if process.stderr else b""
        result = process.wait()
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stdout.close()
        if process.stderr:
            process.stderr.close()
    if result:
        raise InstallError(f"zstd failed during extraction: {stderr.decode(errors='replace')}")


def verify_extracted_pack(stage: Path, pack_id: str, schema: Path) -> tuple[Path, dict]:
    pack_root = stage / "content-packs" / pack_id
    manifest_path = pack_root / "manifest.json"
    if not manifest_path.is_file():
        raise InstallError(f"bundle is missing content-packs/{pack_id}/manifest.json")
    schema_target = stage / "manifests" / "content-pack.schema.json"
    schema_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(schema, schema_target)
    catalog_path = stage / "manifests" / "content-packs.json"
    catalog_path.write_text(json.dumps({
        "schema_version": 1,
        "manifest_schema": "content-pack.schema.json",
        "status": "ready",
        "packs": [f"../content-packs/{pack_id}/manifest.json"],
    }, indent=2) + "\n", encoding="utf-8")
    try:
        ids = validate_catalog(catalog_path)
        if ids != [pack_id]:
            raise InstallError("bundle catalog validation returned an unexpected pack ID")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (PackError, json.JSONDecodeError, OSError) as exc:
        raise InstallError(f"content-pack manifest validation failed: {exc}") from exc
    if manifest["installation"]["target"] == "storage/references/documents":
        artifacts = manifest["artifacts"]
        if not artifacts or any(Path(item["path"]).suffix.lower() not in {".pdf", ".txt"} for item in artifacts):
            raise InstallError("reference-document packs may contain only PDF and TXT artifacts")
    return pack_root, manifest


def installed_pack_valid(path: Path, manifest: dict) -> bool:
    manifest_path = path / "manifest.json"
    try:
        installed = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if installed != manifest:
        return False
    for artifact in manifest["artifacts"]:
        artifact_path = path / artifact["path"]
        if (not artifact_path.is_file() or artifact_path.is_symlink() or
                artifact_path.stat().st_size != artifact["size_bytes"] or
                file_sha256(artifact_path) != artifact["sha256"]):
            return False
    return True


def activate_map_pack(pack_root: Path, manifest: dict, root: Path) -> str | None:
    """Atomically publish a single PMTiles artifact to N.O.M.A.D.'s map inventory."""
    target = manifest["installation"]["target"]
    if target != "storage/maps/pmtiles":
        return None
    artifacts = manifest["artifacts"]
    map_artifacts = [item for item in artifacts if Path(item["path"]).suffix.lower() == ".pmtiles"]
    if len(map_artifacts) != 1:
        raise InstallError("maps-pmtiles packs must contain exactly one .pmtiles artifact")
    artifact = map_artifacts[0]

    source = pack_root / artifact["path"]
    if source.is_symlink() or not source.is_file():
        raise InstallError("map artifact must be a regular file")
    maps_root = root / "storage" / "maps"
    target_root = maps_root / "pmtiles"
    if maps_root.is_symlink() or target_root.is_symlink():
        raise InstallError("map storage directories must not be symbolic links")
    target_root.mkdir(mode=0o750, parents=True, exist_ok=True)
    destination = target_root / source.name
    if destination.exists():
        if destination.is_file() and file_sha256(destination) == artifact["sha256"]:
            return f"map already active: {destination}"
        raise InstallError(f"refusing to replace existing map content: {destination}")

    # Stage on the destination filesystem, then link into place without ever
    # replacing a user's existing map. A crash leaves at most a hidden temp file.
    fd, temporary_name = tempfile.mkstemp(prefix=".fieldos-map-", dir=target_root)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as output, source.open("rb") as input_stream:
            shutil.copyfileobj(input_stream, output, length=1024 * 1024)
            output.flush()
            os.fsync(output.fileno())
        if file_sha256(temporary) != artifact["sha256"]:
            raise InstallError("map artifact changed while activating")
        try:
            os.link(temporary, destination)
        except FileExistsError:
            if destination.is_file() and file_sha256(destination) == artifact["sha256"]:
                return f"map already active: {destination}"
            raise InstallError(f"refusing to replace existing map content: {destination}")
        return f"activated map: {destination}"
    finally:
        temporary.unlink(missing_ok=True)


def activate_reference_pack(pack_root: Path, manifest: dict, root: Path) -> str | None:
    """Publish readable PDF/text sources through a local, generated index."""
    if manifest["installation"]["target"] != "storage/references/documents":
        return None
    artifacts = manifest["artifacts"]
    references_root = root / "storage" / "references"
    if references_root.is_symlink():
        raise InstallError("reference index directory must not be a symbolic link")
    references_root.mkdir(mode=0o755, parents=True, exist_ok=True)
    index = references_root / "index.html"
    marker = "<!-- Generated by FieldOS content-pack installer -->"
    if index.is_symlink():
        raise InstallError("refusing to replace a symbolic-link reference index")
    if index.exists() and marker not in index.read_text(encoding="utf-8"):
        raise InstallError(f"refusing to replace a non-FieldOS reference index: {index}")

    packs_root = root / "content-packs"
    web_documents = references_root / "documents"
    entries = []
    for manifest_path in sorted(packs_root.glob("*/*/manifest.json")):
        try:
            installed = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if installed.get("installation", {}).get("target") != "storage/references/documents":
            continue
        pack_id, version = installed.get("id"), installed.get("version")
        if not pack_id or not version or manifest_path.parent != packs_root / pack_id / version:
            continue
        pack_title = html.escape(str(installed.get("title", pack_id)))
        description = html.escape(str(installed.get("description", "")))
        pack_metadata = [str(installed.get("title", pack_id)), str(installed.get("description", ""))]
        source_entries = []
        for source in installed.get("sources", []):
            name = html.escape(str(source.get("name", "Source")))
            url = html.escape(str(source.get("url", "")), quote=True)
            attribution = html.escape(str(source.get("attribution", "")))
            license_name = html.escape(str(source.get("license", "")))
            source_entries.append(f"<li>{name}: {attribution} <small>({license_name}; {url})</small></li>")
            pack_metadata.extend((str(source.get("name", "")), str(source.get("attribution", "")),
                                  str(source.get("license", ""))))
        entries.append(
            f'<section class="reference-pack"><h2>{pack_title}</h2><p>{description}</p>'
            f'<ul class="source-details">{"".join(source_entries)}</ul><ul class="document-list">'
        )
        for artifact in installed.get("artifacts", []):
            rel = PurePosixPath(artifact["path"])
            source_path = manifest_path.parent.joinpath(*rel.parts)
            target_path = web_documents / pack_id / version
            directories = [web_documents, web_documents / pack_id, target_path]
            for part in rel.parts[:-1]:
                target_path /= part
                directories.append(target_path)
            for directory in directories:
                if directory.is_symlink():
                    raise InstallError(f"reference document path must not contain symbolic links: {directory}")
                directory.mkdir(mode=0o755, parents=True, exist_ok=True)
            if not source_path.is_file() or source_path.is_symlink():
                raise InstallError(f"reference artifact must be a regular file: {source_path}")
            if (source_path.stat().st_size != artifact["size_bytes"] or
                    file_sha256(source_path) != artifact["sha256"]):
                raise InstallError(f"reference artifact does not match its declared size and checksum: {source_path}")
            destination = target_path / rel.name
            if destination.is_symlink():
                raise InstallError(f"refusing to replace a symbolic-link reference document: {destination}")
            if destination.exists():
                if not destination.is_file() or file_sha256(destination) != artifact["sha256"]:
                    raise InstallError(f"refusing to replace existing reference document: {destination}")
            else:
                fd, temporary_name = tempfile.mkstemp(prefix=".fieldos-reference-document-", dir=target_path)
                temporary = Path(temporary_name)
                try:
                    with os.fdopen(fd, "wb") as output, source_path.open("rb") as input_stream:
                        shutil.copyfileobj(input_stream, output, length=1024 * 1024)
                        output.flush()
                        os.fsync(output.fileno())
                    if file_sha256(temporary) != artifact["sha256"]:
                        raise InstallError(f"reference document changed while activating: {source_path}")
                    try:
                        os.link(temporary, destination)
                    except FileExistsError:
                        if not destination.is_file() or file_sha256(destination) != artifact["sha256"]:
                            raise InstallError(f"refusing to replace existing reference document: {destination}")
                finally:
                    temporary.unlink(missing_ok=True)
            href = "documents/" + quote(f"{pack_id}/{version}/{rel.as_posix()}", safe="/")
            label = html.escape(rel.name)
            body = ""
            if source_path.suffix.lower() == ".txt" and source_path.stat().st_size <= MAX_SOURCE_LIBRARY_TEXT_BYTES:
                body = source_path.read_text(encoding="utf-8", errors="replace")
            search_metadata = " ".join((*pack_metadata, rel.name, artifact.get("license", "")))
            entries.append(
                '<li class="source-document" data-search="{}" data-body="{}">'
                '<a href="{}">{}</a><p class="search-match" hidden></p></li>'.format(
                    html.escape(search_metadata, quote=True), html.escape(body, quote=True),
                    html.escape(href, quote=True), label,
                )
            )
        entries.append("</ul></section>")

    search_script = """<script>
(() => {
  const input = document.getElementById('source-search');
  const status = document.getElementById('source-search-status');
  const documents = [...document.querySelectorAll('.source-document')];
  const packs = [...document.querySelectorAll('.reference-pack')];
  const normalize = (value) => value.normalize('NFKC').toLowerCase();
  const update = () => {
    const terms = normalize(input.value).trim().split(/\\s+/).filter(Boolean);
    let visible = 0;
    for (const item of documents) {
      const body = item.dataset.body || '';
      const text = normalize(`${item.dataset.search || ''} ${body}`);
      const matches = terms.every((term) => text.includes(term));
      item.hidden = !matches;
      if (matches) visible += 1;
      const excerpt = item.querySelector('.search-match');
      excerpt.hidden = true;
      excerpt.textContent = '';
      if (matches && terms.length && body) {
        const words = body.split(/\\s+/);
        const position = words.findIndex((word) => terms.some((term) => normalize(word).includes(term)));
        if (position >= 0) {
          excerpt.textContent = `Match: ${words.slice(Math.max(0, position - 14), position + 36).join(' ')}`;
          excerpt.hidden = false;
        }
      }
    }
    for (const pack of packs) {
      pack.hidden = ![...pack.querySelectorAll('.source-document')].some((item) => !item.hidden);
    }
    status.textContent = terms.length ? `${visible} matching document${visible === 1 ? '' : 's'}` : `${visible} installed document${visible === 1 ? '' : 's'}`;
  };
  input.addEventListener('input', update);
  update();
})();
</script>"""

    page = "\n".join([
        "<!doctype html>", '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        "<title>FieldOS Source Library</title></head><body>", marker,
        "<h1>FieldOS Source Library</h1>",
        "<p>These are source documents, not AI-generated answers. Check each source's date and instructions.</p>",
        "<p>FieldOS is independent and is not endorsed by the publishers listed here. The original materials are reproduced unchanged and are available at no charge from their agencies; use current local authority guidance when it differs.</p>",
        '<label for="source-search">Search installed offline sources</label>',
        '<input id="source-search" type="search" size="48" autocomplete="off" aria-describedby="source-search-help" placeholder="Search topics, titles, or source names">',
        '<p id="source-search-help">Search checks titles, source details, and plain-text documents up to 1 MiB. Open PDFs and longer documents, then use the browser\'s Find command to search inside them.</p>',
        '<p id="source-search-status" role="status" aria-live="polite"></p>',
        *(entries or ["<p>No reference-document packs are installed.</p>"]),
        search_script,
        "</body></html>",
    ]) + "\n"
    fd, temporary_name = tempfile.mkstemp(prefix=".fieldos-reference-", dir=references_root)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            output.write(page)
            output.flush()
            os.fsync(output.fileno())
        temporary.chmod(0o644)
        os.replace(temporary, index)
    finally:
        temporary.unlink(missing_ok=True)
    return f"activated reference documents: {index}"


def install_bundle(archive: Path, root: Path = DEFAULT_ROOT,
                   schema: Path = DEFAULT_SCHEMA, reserve_bytes: int = RESERVE_BYTES) -> str:
    if archive.is_symlink():
        raise InstallError("bundle must be a regular file, not a symlink")
    archive = archive.resolve(strict=True)
    if not archive.is_file():
        raise InstallError("bundle must be a regular file, not a symlink")
    bundle_hash = verify_bundle_checksum(archive)
    pack_id, unpacked_bytes, _count = scan_bundle(archive)

    root.mkdir(parents=True, exist_ok=True)
    root = root.resolve(strict=True)
    packs_root = root / "content-packs"
    if packs_root.is_symlink():
        raise InstallError("content-pack storage root must not be a symlink")
    packs_root.mkdir(mode=0o755, exist_ok=True)
    id_root = packs_root / pack_id
    if id_root.is_symlink():
        raise InstallError("pack ID storage path must not be a symlink")
    id_root.mkdir(mode=0o755, exist_ok=True)
    free = shutil.disk_usage(id_root).free
    # The pack is extracted on this filesystem and then atomically renamed
    # into place, so only one unpacked copy is needed at peak.
    if free < unpacked_bytes + reserve_bytes:
        raise InstallError(
            f"insufficient free space: need {unpacked_bytes + reserve_bytes} bytes, have {free}"
        )

    stage_parent = Path(tempfile.mkdtemp(prefix=".fieldos-pack-verify-", dir=id_root))
    try:
        (stage_parent / "content-packs").mkdir()
        extract_bundle(archive, stage_parent, pack_id)
        pack_root, manifest = verify_extracted_pack(stage_parent, pack_id, schema.resolve(strict=True))
        version = manifest["version"]
        if manifest["id"] != pack_id:
            raise InstallError("pack directory and manifest IDs do not match")
        final = id_root / version
        if final.is_symlink():
            raise InstallError(f"refusing to use a symlink as installed pack data: {final}")
        if final.exists():
            recorded_hash = final / ".bundle.sha256"
            if (recorded_hash.is_file() and recorded_hash.read_text(encoding="ascii").strip() == bundle_hash
                    and installed_pack_valid(final, manifest)):
                activation = activate_map_pack(final, manifest, root)
                activation = activation or activate_reference_pack(final, manifest, root)
                suffix = f"; {activation}" if activation else ""
                return f"already installed: {pack_id} {version}{suffix}"
            raise InstallError(f"refusing to replace existing pack data: {final}")

        (pack_root / ".bundle.sha256").write_text(bundle_hash + "\n", encoding="ascii")
        if not installed_pack_valid(pack_root, manifest):
            raise InstallError("staged pack integrity check failed")
        try:
            os.rename(pack_root, final)
        except FileExistsError as exc:
            raise InstallError(f"refusing to replace concurrently installed pack: {final}") from exc
        activation = activate_map_pack(final, manifest, root)
        activation = activation or activate_reference_pack(final, manifest, root)
        suffix = f"; {activation}" if activation else ""
        return f"installed: {pack_id} {version} at {final}{suffix}"
    finally:
        shutil.rmtree(stage_parent, ignore_errors=True)


def list_packs(root: Path = DEFAULT_ROOT) -> list[tuple[str, str, Path]]:
    packs_root = root / "content-packs"
    if not packs_root.is_dir():
        return []
    entries: list[tuple[str, str, Path]] = []
    for manifest in sorted(packs_root.glob("*/*/manifest.json")):
        try:
            record = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if record.get("id") == manifest.parents[1].name and record.get("version") == manifest.parent.name:
            entries.append((record["id"], record["version"], manifest.parent))
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    install = sub.add_parser("install", help="verify and install an offline .tar.zst pack")
    install.add_argument("archive", type=Path)
    install.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                         help=argparse.SUPPRESS)
    install.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA,
                         help=argparse.SUPPRESS)
    listing = sub.add_parser("list", help="list installed content packs")
    listing.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                         help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        if args.command == "install":
            print(install_bundle(args.archive, args.root, args.schema))
        else:
            entries = list_packs(args.root)
            if not entries:
                print("No offline content packs are installed.")
            for pack_id, version, path in entries:
                print(f"{pack_id}\t{version}\t{path}")
    except (InstallError, OSError, subprocess.SubprocessError, PackError) as exc:
        print(f"FieldOS content-pack error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
