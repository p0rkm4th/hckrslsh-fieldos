#!/usr/bin/env python3
"""Reject offline payloads missing required core content-pack archives."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def verify_payload(payload: Path, catalog_path: Path) -> list[str]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    expected: list[str] = []
    for entry in catalog.get("core_packs", []):
        manifest_path = (catalog_path.parent / entry).resolve(strict=True)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected.extend((
            f"content-packs/{manifest['id']}-{manifest['version']}.tar.zst",
            f"content-packs/{manifest['id']}-{manifest['version']}.tar.zst.sha256",
        ))
    if not expected:
        raise ValueError("content-pack catalog declares no required core packs")
    listing = subprocess.run(
        ["tar", "--use-compress-program=zstd", "-tf", str(payload)],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    missing = sorted(set(expected) - set(listing))
    if missing:
        raise ValueError("offline payload is missing required core pack files: " + ", ".join(missing))
    return expected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path)
    parser.add_argument("--catalog", type=Path, required=True)
    args = parser.parse_args()
    try:
        paths = verify_payload(args.payload, args.catalog)
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"Offline payload validation failed: {exc}", file=sys.stderr)
        return 1
    print("Offline payload contains required core packs: " + ", ".join(paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
