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
from pathlib import Path, PurePosixPath

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from validate_content_packs import PackError, validate_catalog, validate_manifest  # noqa: E402

DEFAULT_ROOT = Path("/var/lib/fieldos")
DEFAULT_SCHEMA = Path("/opt/fieldos/payload/manifests/content-pack.schema.json")
RESERVE_BYTES = 256 * 1024 * 1024
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
                return f"already installed: {pack_id} {version}"
            raise InstallError(f"refusing to replace existing pack data: {final}")

        (pack_root / ".bundle.sha256").write_text(bundle_hash + "\n", encoding="ascii")
        if not installed_pack_valid(pack_root, manifest):
            raise InstallError("staged pack integrity check failed")
        try:
            os.rename(pack_root, final)
        except FileExistsError as exc:
            raise InstallError(f"refusing to replace concurrently installed pack: {final}") from exc
        return f"installed: {pack_id} {version} at {final}"
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
