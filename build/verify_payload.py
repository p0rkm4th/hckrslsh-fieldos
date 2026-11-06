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
    generated_ollama_files = {
        "content/ollama/id_ed25519",
        "content/ollama/id_ed25519.pub",
    }
    forbidden = sorted(
        name for name in listing
        if name in generated_ollama_files
        or name == "content/ollama/cache"
        or name.startswith("content/ollama/cache/")
    )
    if forbidden:
        raise ValueError(
            "offline payload contains generated Ollama keys or recommendation cache: "
            + ", ".join(forbidden)
        )
    missing = sorted(set(expected) - set(listing))
    if missing:
        raise ValueError("offline payload is missing required core pack files: " + ", ".join(missing))
    archived_packs = {
        name for name in listing
        if name.startswith("content-packs/")
        and (name.endswith(".tar.zst") or name.endswith(".tar.zst.sha256"))
    }
    extra = sorted(archived_packs - set(expected))
    if extra:
        raise ValueError(
            "offline payload contains stale or unapproved content-pack files: "
            + ", ".join(extra)
        )
    if maps_manifest_path is not None:
        source_maps = json.loads(maps_manifest_path.read_text(encoding="utf-8"))
        embedded_maps = _archive_json(payload, "manifests/maps.json")
        if embedded_maps != source_maps:
            raise ValueError("offline payload map manifest is stale; rebuild it from current source")

        map_payload = _archive_json(payload, "manifests/map-payload.json")
        regions = map_payload.get("regions")
        if not isinstance(regions, list):
            raise ValueError("offline payload map metadata does not describe the current region list")
        if "extractor" in source_maps:
            if map_payload.get("extractor") != source_maps["extractor"]:
                raise ValueError("offline payload map metadata has a stale extractor pin")
            embedded_build = map_payload.get("source_build", {})
            for field in ("key", "url", "metadata_url", "version", "size", "md5sum", "b3sum", "uploaded"):
                if embedded_build.get(field) != source_maps["source_build"].get(field):
                    raise ValueError(f"offline payload map metadata has stale source-build field: {field}")
            expected_world_command = [
                "pmtiles", "extract", source_maps["source_build"]["url"],
                "/maps/world.pmtiles", "--bbox=-180,-85,180,85", "--maxzoom=5",
            ]
            if map_payload.get("world_extraction_command") != expected_world_command:
                raise ValueError("offline payload map metadata has a stale world extraction command")
        by_id = {item.get("id"): item for item in regions if isinstance(item, dict)}
        required_map_files = {"content/maps/pmtiles/world.pmtiles"}
        for source_region in source_maps.get("regions", []):
            region_id = source_region["id"]
            region_file = source_region["file"]
            required_map_files.add(f"content/maps/pmtiles/{region_file}")
            built_region = by_id.get(region_id)
            if not built_region or built_region.get("file") != region_file:
                raise ValueError(f"offline payload map data is missing source region {region_id}")
            if "extractor" in source_maps:
                input_source = (
                    "/maps/world.pmtiles" if source_region.get("source") == "world"
                    else source_maps["source_build"]["url"]
                )
                expected_command = [
                    "pmtiles", "extract", input_source, f"/maps/{region_file}",
                    f"--bbox={source_region['bbox']}",
                    f"--minzoom={source_region['minzoom']}",
                    f"--maxzoom={source_region['maxzoom']}",
                ]
                if built_region.get("extraction_command") != expected_command:
                    raise ValueError(f"offline payload map metadata has a stale extraction command for {region_id}")
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
