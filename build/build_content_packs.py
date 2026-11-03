#!/usr/bin/env python3
"""Build independently checksummed offline archives from approved pack entries."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "payload"))
from validate_content_packs import PackError, validate_catalog  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_catalog(catalog_path: Path) -> tuple[Path, list[tuple[str, str, Path]]]:
    payload_root = catalog_path.resolve(strict=True).parent.parent
    pack_ids = validate_catalog(catalog_path)
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entries: list[tuple[str, str, Path]] = []
    for entry in catalog["packs"]:
        manifest_path = (catalog_path.parent / entry).resolve(strict=True)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries.append((manifest["id"], manifest["version"], manifest_path.parent))
    if len(entries) != len(pack_ids):
        raise PackError("catalog pack count changed after validation")
    return payload_root, entries


def build_archives(catalog_path: Path, output_root: Path) -> list[Path]:
    payload_root, entries = read_catalog(catalog_path)
    if not entries:
        return []
    output = output_root / "content-packs"
    output.mkdir(parents=True, exist_ok=True)
    built: list[Path] = []
    for pack_id, version, pack_dir in entries:
        manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
        relative_pack = pack_dir.relative_to(payload_root)
        members = [relative_pack / "manifest.json"] + [
            relative_pack / Path(artifact["path"]) for artifact in manifest["artifacts"]
        ]
        archive = output / f"{pack_id}-{version}.tar.zst"
        checksum = Path(f"{archive}.sha256")
        if archive.exists() or checksum.exists():
            raise FileExistsError(f"refusing to overwrite existing content pack output: {archive}")
        source_bytes = sum((payload_root / member).stat().st_size for member in members)
        free_bytes = shutil.disk_usage(output).free
        required_bytes = source_bytes + 256 * 1024 * 1024
        if free_bytes < required_bytes:
            raise OSError(
                f"insufficient space for {pack_id}: need up to {required_bytes} bytes, have {free_bytes}"
            )
        temp_fd, temp_name = tempfile.mkstemp(prefix=f".{archive.name}.", suffix=".tmp", dir=output)
        os.close(temp_fd)
        temp = Path(temp_name)
        temp.unlink()
        try:
            tar = subprocess.Popen(
                ["tar", "--sort=name", "--mtime=UTC 1970-01-01", "--owner=0", "--group=0",
                 "--numeric-owner", "-C", str(payload_root), "-cf", "-", "--",
                 *[member.as_posix() for member in members]],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            assert tar.stdout is not None
            zstd = subprocess.run(
                ["zstd", "--quiet", "--threads=0", "-12", "-o", str(temp)],
                stdin=tar.stdout, capture_output=True,
            )
            tar.stdout.close()
            tar_stderr = tar.stderr.read() if tar.stderr else b""
            if tar.stderr:
                tar.stderr.close()
            tar_code = tar.wait()
            if tar_code or zstd.returncode:
                raise RuntimeError(
                    f"failed to build {pack_id}: tar={tar_stderr.decode(errors='replace')} "
                    f"zstd={zstd.stderr.decode(errors='replace')}"
                )
            digest = sha256_file(temp)
            os.replace(temp, archive)
            checksum.write_text(f"{digest}  {archive.name}\n", encoding="ascii")
            built.append(archive)
        finally:
            if temp.exists():
                temp.unlink()
    return built


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=ROOT / "payload/manifests/content-packs.json")
    parser.add_argument("--output-root", type=Path, default=Path("/mnt/shared/fieldos-payload"))
    args = parser.parse_args()
    try:
        archives = build_archives(args.catalog, args.output_root)
    except (OSError, ValueError, PackError, subprocess.SubprocessError, RuntimeError) as exc:
        print(f"Content-pack build failed: {exc}", file=sys.stderr)
        return 2
    if archives:
        for archive in archives:
            print(f"Built independent content pack: {archive} ({sha256_file(archive)})")
    else:
        print("No approved content packs are listed; no pack archives created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
