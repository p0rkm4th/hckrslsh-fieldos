#!/usr/bin/env python3
"""Collect license and notice files from every layer of pinned Docker saves."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import tarfile
from pathlib import Path
from typing import Any

MAX_NOTICE_BYTES = 5 * 1024 * 1024


def clean_member(name: str) -> str:
    name = name.replace("\\", "/")
    while name.startswith("./") or name.startswith("/"):
        name = name[1:] if name.startswith("/") else name[2:]
    return posixpath.normpath(name)


def is_notice_path(name: str) -> bool:
    path = clean_member(name).lower()
    leaf = path.rsplit("/", 1)[-1]
    if path.startswith(("usr/share/licenses/", "usr/share/common-licenses/")):
        return True
    return leaf.startswith(
        ("license", "licence", "notice", "copyright", "copying", "third-party", "third_party")
    )


def collect_image_archive(
    archive_path: Path,
    image: dict[str, Any],
    output_dir: Path,
    max_notice_bytes: int = MAX_NOTICE_BYTES,
) -> dict[str, Any]:
    """Extract candidate notice text by content hash, indexing source paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    files_dir = output_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    contents: dict[str, dict[str, Any]] = {}
    skipped: list[dict[str, Any]] = []
    non_regular: list[dict[str, Any]] = []

    with tarfile.open(archive_path, mode="r:*") as outer:
        manifest_stream = outer.extractfile("manifest.json")
        if manifest_stream is None:
            raise ValueError(f"Docker save archive has no manifest.json: {archive_path}")
        docker_manifest = json.load(manifest_stream)
        if len(docker_manifest) != 1:
            raise ValueError(f"Expected one image in Docker save archive: {archive_path}")
        docker_image = docker_manifest[0]
        repo_tags = docker_image.get("RepoTags") or []
        if image["ref"] not in repo_tags:
            raise ValueError(
                f"Image archive tag mismatch: expected {image['ref']!r}, found {repo_tags!r}"
            )
        layers = docker_image.get("Layers") or []
        if not layers:
            raise ValueError(f"Image archive has no layers: {archive_path}")

        for layer_number, layer_name in enumerate(layers):
            try:
                layer_member = outer.getmember(layer_name)
            except KeyError as exc:
                raise ValueError(f"Image layer is missing from archive: {layer_name}") from exc
            layer = outer.extractfile(layer_member)
            if layer is None:
                raise ValueError(f"Unable to read image layer: {layer_name}")
            with layer, tarfile.open(fileobj=layer, mode="r:*") as inner:
                for member in inner:
                    if not is_notice_path(member.name):
                        continue
                    path = clean_member(member.name)
                    if not member.isfile():
                        non_regular.append(
                            {"path": path, "layer": layer_number, "type": repr(member.type), "link": member.linkname}
                        )
                        continue
                    if member.size > max_notice_bytes:
                        skipped.append(
                            {"path": path, "layer": layer_number, "size": member.size, "reason": "over size limit"}
                        )
                        continue
                    stream = inner.extractfile(member)
                    if stream is None:
                        continue
                    with stream:
                        data = stream.read(max_notice_bytes + 1)
                    if len(data) > max_notice_bytes:
                        skipped.append(
                            {"path": path, "layer": layer_number, "size": member.size, "reason": "over read limit"}
                        )
                        continue
                    digest = hashlib.sha256(data).hexdigest()
                    record = contents.setdefault(
                        digest, {"sha256": digest, "bytes": len(data), "occurrences": []}
                    )
                    record["occurrences"].append({"path": path, "layer": layer_number})
                    target = files_dir / f"{digest}.txt"
                    if not target.exists():
                        target.write_bytes(data)

    report = {
        "schema_version": 1,
        "image": image["ref"],
        "digest": image["digest"],
        "declared_license": image.get("license"),
        "repo_tags": repo_tags,
        "layer_count": len(layers),
        "unique_notice_files": len(contents),
        "unique_notice_bytes": sum(item["bytes"] for item in contents.values()),
        "occurrences": sum(len(item["occurrences"]) for item in contents.values()),
        "skipped": skipped,
        "non_regular_candidates": non_regular,
        "files": sorted(contents.values(), key=lambda item: item["sha256"]),
    }
    (output_dir / "index.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def collect_manifest(manifest_path: Path, archive_dir: Path, output_dir: Path) -> list[dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("platform") != "linux/amd64":
        raise ValueError("Only the declared linux/amd64 image set is supported")
    reports = []
    for image in manifest["images"]:
        archive_path = archive_dir / f"{image['name']}.tar"
        report = collect_image_archive(archive_path, image, output_dir / image["name"])
        reports.append(report)
        print(
            f"{image['name']}: {report['layer_count']} layers, "
            f"{report['unique_notice_files']} unique notice files, "
            f"{report['occurrences']} occurrences"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "README.md").write_text(
        "# Container image license and notice files\n\n"
        "These candidate notices were extracted from every layer of each pinned image. "
        "Files are stored under `files/` by SHA-256; `index.json` records their original "
        "image paths and layer numbers. This preserves notices that may be hidden by a "
        "later whiteout. Images with zero matching files still have an index.\n\n"
        "Extraction is filename-based and does not establish complete license coverage. "
        "Review each image SBOM, all notices, source obligations, and any entries listed "
        "as skipped or non-regular before redistribution.\n"
    )
    (output_dir / "index.json").write_text(json.dumps(reports, indent=2) + "\n")
    return reports


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--archive-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    collect_manifest(args.manifest, args.archive_dir, args.output_dir)


if __name__ == "__main__":
    main()
