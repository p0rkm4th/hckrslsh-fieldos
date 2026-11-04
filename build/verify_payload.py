#!/usr/bin/env python3
"""Reject offline payloads missing required core content-pack archives."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def verify_payload(payload: Path, catalog_path: Path,
                   maps_manifest_path: Path | None = None) -> list[str]:
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
    if maps_manifest_path is not None:
        source_maps = json.loads(maps_manifest_path.read_text(encoding="utf-8"))
        embedded_maps = _archive_json(payload, "manifests/maps.json")
        if embedded_maps != source_maps:
            raise ValueError("offline payload map manifest is stale; rebuild it from current source")

        map_payload = _archive_json(payload, "manifests/map-payload.json")
        regions = map_payload.get("regions")
        if not isinstance(regions, list):
            raise ValueError("offline payload map metadata does not describe the current region list")
        by_id = {item.get("id"): item for item in regions if isinstance(item, dict)}
        required_map_files = {"content/maps/pmtiles/world.pmtiles"}
        for source_region in source_maps.get("regions", []):
            region_id = source_region["id"]
            region_file = source_region["file"]
            required_map_files.add(f"content/maps/pmtiles/{region_file}")
            built_region = by_id.get(region_id)
            if not built_region or built_region.get("file") != region_file:
                raise ValueError(f"offline payload map data is missing source region {region_id}")
            derived = built_region.get("derived_file", {})
            if (source_region.get("expected_size_bytes") and
                    derived.get("bytes") != source_region["expected_size_bytes"]):
                raise ValueError(f"offline payload map size does not match source for {region_id}")
            if (source_region.get("expected_sha256") and
                    derived.get("sha256") != source_region["expected_sha256"]):
                raise ValueError(f"offline payload map checksum does not match source for {region_id}")
        missing_maps = sorted(required_map_files - set(listing))
        if missing_maps:
            raise ValueError("offline payload is missing source map files: " + ", ".join(missing_maps))
    return expected


def _archive_json(payload: Path, member: str) -> dict:
    proc = subprocess.run(
        ["tar", "--use-compress-program=zstd", "-xOf", str(payload), member],
        check=True, capture_output=True, text=True,
    )
    value = json.loads(proc.stdout)
    if not isinstance(value, dict):
        raise ValueError(f"offline payload member is not a JSON object: {member}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--maps-manifest", type=Path)
    args = parser.parse_args()
    try:
        paths = verify_payload(args.payload, args.catalog, args.maps_manifest)
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"Offline payload validation failed: {exc}", file=sys.stderr)
        return 1
    print("Offline payload contains required core packs: " + ", ".join(paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
