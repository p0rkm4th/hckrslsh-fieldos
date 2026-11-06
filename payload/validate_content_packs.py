#!/usr/bin/env python3
"""Validate FieldOS content-pack manifests and staged artifact hashes."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse


CATEGORIES = {
    "agriculture",
    "wildlife-overlanding",
    "water-food",
    "first-aid-emergency",
    "weather-disaster",
    "communications",
    "maps-gis",
}
INSTALL_TARGETS = {
    "storage/maps/pmtiles",
    "storage/references/documents",
    "storage/zim",
    "storage/content-packs",
}
AUTHORITIES = {"authoritative-reference", "community-reference", "fieldos-authored", "ai-generated", "mixed"}
PACK_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PACK_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")


class PackError(ValueError):
    pass


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PackError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PackError(f"expected an object in {path}")
    return value


def required(value: dict, names: set[str], label: str) -> None:
    missing = sorted(names - value.keys())
    if missing:
        raise PackError(f"{label} is missing required fields: {', '.join(missing)}")


def nonempty(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PackError(f"{label} must be a non-empty string")
    return value.strip()


def date_value(value: object, label: str) -> None:
    text = nonempty(value, label)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise PackError(f"{label} must be an ISO date (YYYY-MM-DD)")
    try:
        dt.date.fromisoformat(text)
    except PackError:
        raise
    except ValueError as exc:
        raise PackError(f"{label} must be an ISO date (YYYY-MM-DD)") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def within(path: Path, root: Path, label: str) -> Path:
    try:
        base = root.resolve(strict=True)
        unresolved = path.absolute()
        unresolved.relative_to(base)
        cursor = base
        for part in unresolved.relative_to(base).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise PackError(f"{label} must not use symbolic links: {path}")
        resolved = path.resolve(strict=True)
        resolved.relative_to(base)
    except ValueError as exc:
        raise PackError(f"{label} escapes its allowed directory: {path}") from exc
    except OSError as exc:
        raise PackError(f"{label} does not exist or cannot be read: {path}") from exc
    return resolved


def validate_manifest(manifest_path: Path, payload_root: Path) -> str:
    payload_root = payload_root.resolve(strict=True)
    allowed_packs = (payload_root / "content-packs").resolve(strict=True)
    manifest_path = within(manifest_path, allowed_packs, "pack manifest")
    pack_root = manifest_path.parent
    manifest = read_json(manifest_path)

    required(manifest, {
        "schema_version", "id", "version", "title", "description", "category",
        "sources", "artifacts", "geographic_coverage", "installation", "authority",
    }, "pack manifest")
    if not isinstance(manifest["schema_version"], int) or isinstance(manifest["schema_version"], bool) or manifest["schema_version"] != 1:
        raise PackError(f"unsupported schema_version in {manifest_path}")
    pack_id = nonempty(manifest["id"], "pack id")
    if not PACK_ID.fullmatch(pack_id) or pack_id != pack_root.name:
        raise PackError(f"pack id must be a lowercase slug matching directory {pack_root.name!r}")
    version = nonempty(manifest["version"], "pack version")
    if not PACK_VERSION.fullmatch(version):
        raise PackError(f"pack version must be a safe filename component in {manifest_path}")
    nonempty(manifest["title"], "pack title")
    nonempty(manifest["description"], "pack description")
    if "geographic_scope" in manifest:
        nonempty(manifest["geographic_scope"], "geographic_scope")
    category = manifest["category"]
    if not isinstance(category, str) or category not in CATEGORIES:
        raise PackError(f"unsupported category in pack {pack_id}")

    sources = manifest["sources"]
    if not isinstance(sources, list) or not sources:
        raise PackError(f"pack {pack_id} must declare at least one source")
    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        label = f"source {index} in {pack_id}"
        if not isinstance(source, dict):
            raise PackError(f"{label} must be an object")
        required(source, {"id", "name", "url", "license", "attribution"}, label)
        if source.keys() - {"id", "name", "url", "license", "attribution", "accessed"}:
            raise PackError(f"{label} has unknown fields")
        source_id = nonempty(source["id"], f"{label} id")
        if not PACK_ID.fullmatch(source_id) or source_id in source_ids:
            raise PackError(f"{label} id must be a unique lowercase slug")
        source_ids.add(source_id)
        nonempty(source["name"], f"{label} name")
        url = urlparse(nonempty(source["url"], f"{label} URL"))
        if url.scheme not in {"http", "https"} or not url.netloc:
            raise PackError(f"{label} URL must be an absolute HTTP or HTTPS URL")
        nonempty(source["license"], f"{label} license")
        nonempty(source["attribution"], f"{label} attribution")
        if "accessed" in source:
            date_value(source["accessed"], f"{label} accessed date")

    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        raise PackError(f"pack {pack_id} must declare at least one artifact")
    artifact_paths: set[str] = set()
    for index, artifact in enumerate(artifacts):
        label = f"artifact {index} in {pack_id}"
        if not isinstance(artifact, dict):
            raise PackError(f"{label} must be an object")
        required(artifact, {"path", "size_bytes", "sha256", "source", "license"}, label)
        if artifact.keys() - {"path", "size_bytes", "sha256", "source", "sources", "license", "title", "index_with_ai"}:
            raise PackError(f"{label} has unknown fields")
        relative = Path(nonempty(artifact["path"], f"{label} path"))
        if relative.is_absolute() or ".." in relative.parts:
            raise PackError(f"{label} path must stay inside its pack directory")
        if relative.as_posix() in artifact_paths:
            raise PackError(f"duplicate artifact path in pack {pack_id}: {relative}")
        artifact_paths.add(relative.as_posix())
        source_ref = nonempty(artifact["source"], f"{label} source")
        if source_ref not in source_ids:
            raise PackError(f"{label} references undeclared source {source_ref!r}")
        if "sources" in artifact:
            related_sources = artifact["sources"]
            if (not isinstance(related_sources, list) or not related_sources or
                    any(not isinstance(item, str) or not item.strip() for item in related_sources)):
                raise PackError(f"{label} sources must be a non-empty array of source IDs")
            if len(related_sources) != len(set(related_sources)):
                raise PackError(f"{label} sources must not contain duplicates")
            undeclared = sorted(set(related_sources) - source_ids)
            if undeclared:
                raise PackError(f"{label} references undeclared sources: {', '.join(undeclared)}")
            if source_ref not in related_sources:
                raise PackError(f"{label} primary source must be included in sources")
        nonempty(artifact["license"], f"{label} license")
        if "title" in artifact:
            nonempty(artifact["title"], f"{label} title")
        if "index_with_ai" in artifact and not isinstance(artifact["index_with_ai"], bool):
            raise PackError(f"{label} index_with_ai must be a boolean")
        expected_size = artifact["size_bytes"]
        if not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size < 0:
            raise PackError(f"{label} size_bytes must be a non-negative integer")
        expected_hash = artifact["sha256"]
        if not isinstance(expected_hash, str) or not SHA256.fullmatch(expected_hash):
            raise PackError(f"{label} sha256 must be 64 lowercase hexadecimal characters")
        artifact_path = within(pack_root / relative, pack_root, f"{label} path")
        if not artifact_path.is_file():
            raise PackError(f"{label} is not a regular file")
        if artifact_path.stat().st_size != expected_size:
            raise PackError(f"{label} size mismatch: expected {expected_size}, got {artifact_path.stat().st_size}")
        actual_hash = sha256_file(artifact_path)
        if actual_hash != expected_hash:
            raise PackError(f"{label} SHA-256 mismatch")

    coverage = manifest["geographic_coverage"]
    if coverage is not None:
        if not isinstance(coverage, dict):
            raise PackError(f"geographic_coverage in {pack_id} must be an object or null")
        required(coverage, {"name", "bbox", "minzoom", "maxzoom"}, f"coverage in {pack_id}")
        if coverage.keys() - {"name", "bbox", "minzoom", "maxzoom", "crs"}:
            raise PackError(f"coverage in {pack_id} has unknown fields")
        nonempty(coverage["name"], f"coverage name in {pack_id}")
        bbox = coverage["bbox"]
        if (not isinstance(bbox, list) or len(bbox) != 4 or
                any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in bbox)):
            raise PackError(f"coverage bbox in {pack_id} must be [west, south, east, north]")
        if "crs" in coverage:
            nonempty(coverage["crs"], f"coverage CRS in {pack_id}")
        west, south, east, north = bbox
        if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
            raise PackError(f"coverage bbox in {pack_id} is outside EPSG:4326 bounds")
        minzoom, maxzoom = coverage["minzoom"], coverage["maxzoom"]
        if (not isinstance(minzoom, int) or isinstance(minzoom, bool) or
                not isinstance(maxzoom, int) or isinstance(maxzoom, bool) or
                not 0 <= minzoom <= maxzoom <= 30):
            raise PackError(f"coverage zoom range in {pack_id} is invalid")

    installation = manifest["installation"]
    if not isinstance(installation, dict):
        raise PackError(f"installation in {pack_id} must be an object")
    required(installation, {"target", "requirements"}, f"installation in {pack_id}")
    if installation.keys() - {"target", "requirements", "optional"}:
        raise PackError(f"installation in {pack_id} has unknown fields")
    target = Path(nonempty(installation["target"], f"installation target in {pack_id}"))
    if target.is_absolute() or ".." in target.parts:
        raise PackError(f"installation target in {pack_id} must be a relative path without traversal")
    if installation["target"] not in INSTALL_TARGETS:
        raise PackError(f"unsupported installation target in {pack_id}: {installation['target']!r}")
    requirements = installation["requirements"]
    if not isinstance(requirements, list) or any(not isinstance(item, str) or not item.strip() for item in requirements):
        raise PackError(f"installation requirements in {pack_id} must be an array of non-empty strings")
    if "optional" in installation and not isinstance(installation["optional"], bool):
        raise PackError(f"installation optional in {pack_id} must be boolean")

    authority = manifest["authority"]
    if manifest.keys() - {
        "schema_version", "id", "version", "title", "description", "category",
        "sources", "artifacts", "geographic_coverage", "geographic_scope",
        "installation", "authority", "review",
    }:
        raise PackError(f"pack {pack_id} has unknown fields")
    if authority is not None and (not isinstance(authority, str) or authority not in AUTHORITIES):
        raise PackError(f"unsupported authority classification in pack {pack_id}")
    if category in {"first-aid-emergency", "weather-disaster"}:
        if authority != "authoritative-reference":
            raise PackError(f"safety-critical pack {pack_id} must identify authoritative references")
        review = manifest.get("review")
        if not isinstance(review, dict):
            raise PackError(f"safety-critical pack {pack_id} requires a review record")
        required(review, {"reviewer", "reviewed_at", "content_revision"}, f"review record in {pack_id}")
        if review.keys() - {"reviewer", "reviewed_at", "content_revision"}:
            raise PackError(f"review record in {pack_id} has unknown fields")
        nonempty(review["reviewer"], f"reviewer in {pack_id}")
        date_value(review["reviewed_at"], f"review date in {pack_id}")
        date_value(review["content_revision"], f"content revision date in {pack_id}")

    return pack_id


def validate_catalog(catalog_path: Path) -> list[str]:
    catalog_path = catalog_path.resolve(strict=True)
    payload_root = catalog_path.parent.parent
    catalog = read_json(catalog_path)
    required(catalog, {"schema_version", "manifest_schema", "status", "packs"}, "content-pack catalog")
    if catalog.keys() - {"schema_version", "manifest_schema", "status", "packs", "core_packs", "planned_categories"}:
        raise PackError("content-pack catalog has unknown fields")
    if not isinstance(catalog["schema_version"], int) or isinstance(catalog["schema_version"], bool) or catalog["schema_version"] != 1:
        raise PackError("unsupported content-pack catalog schema_version")
    if catalog["manifest_schema"] != "content-pack.schema.json":
        raise PackError("catalog references an unknown pack manifest schema")
    schema_path = catalog_path.parent / catalog["manifest_schema"]
    if not schema_path.is_file():
        raise PackError(f"catalog schema is missing: {schema_path}")
    schema = read_json(schema_path)
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise PackError("content-pack schema must use JSON Schema draft 2020-12")
    if not isinstance(catalog["status"], str) or catalog["status"] not in {"architecture-only", "ready"}:
        raise PackError("catalog status must be architecture-only or ready")
    entries = catalog["packs"]
    if not isinstance(entries, list):
        raise PackError("catalog packs must be an array of relative manifest paths")
    planned = catalog.get("planned_categories", [])
    if not isinstance(planned, list) or any(
        not isinstance(category, str) or category not in CATEGORIES for category in planned
    ):
        raise PackError("planned_categories must list supported pack categories")
    pack_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, str) or not entry:
            raise PackError("each catalog pack entry must be a relative manifest path")
        relative = Path(entry)
        if relative.is_absolute():
            raise PackError(f"catalog manifest path must be relative: {entry}")
        try:
            manifest_path = (catalog_path.parent / relative).resolve(strict=True)
        except OSError as exc:
            raise PackError(f"catalog manifest does not exist: {entry}") from exc
        pack_id = validate_manifest(manifest_path, payload_root)
        if pack_id in pack_ids:
            raise PackError(f"duplicate pack ID in catalog: {pack_id}")
        pack_ids.add(pack_id)
    core_packs = catalog.get("core_packs", [])
    if (not isinstance(core_packs, list) or
            any(not isinstance(item, str) for item in core_packs) or
            len(core_packs) != len(set(core_packs))):
        raise PackError("core_packs must be an array of unique manifest paths")
    if any(item not in entries for item in core_packs):
        raise PackError("every core pack must also be listed in packs")
    for entry in core_packs:
        manifest = read_json(catalog_path.parent / entry)
        if manifest.get("installation", {}).get("optional", True):
            raise PackError(f"core pack must declare installation.optional=false: {entry}")
    if catalog["status"] == "architecture-only" and entries:
        raise PackError("architecture-only catalog must not list distributable packs")
    return sorted(pack_ids)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path,
                        default=Path(__file__).resolve().parent / "manifests/content-packs.json")
    args = parser.parse_args()
    try:
        pack_ids = validate_catalog(args.catalog)
    except PackError as exc:
        parser.error(str(exc))
    if pack_ids:
        print(f"Validated {len(pack_ids)} content pack(s): {', '.join(pack_ids)}")
    else:
        print("Content-pack catalog is valid and empty; no customer packs are approved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
