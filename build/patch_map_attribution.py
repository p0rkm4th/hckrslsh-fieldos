#!/usr/bin/env python3
"""Apply FieldOS's explicit OpenStreetMap/ODbL attribution to N.O.M.A.D.'s style."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


UPSTREAM = (
    '<a href="https://github.com/protomaps/basemaps">Protomaps</a> '
    '© <a href="https://openstreetmap.org">OpenStreetMap</a>'
)
FIELDOS = (
    '<a href="https://www.openstreetmap.org/copyright">'
    '© OpenStreetMap contributors</a> · '
    '<a href="https://github.com/protomaps/basemaps">Protomaps Basemaps</a> · '
    '<a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a>'
)


def collect_attribution_nodes(value: Any, found: list[dict[str, Any]]) -> None:
    if isinstance(value, dict):
        sources = value.get("sources")
        if isinstance(sources, dict):
            for source_name, source in sources.items():
                if isinstance(source, dict) and (
                    "protomaps" in str(source_name).lower()
                    or source.get("attribution") in {UPSTREAM, FIELDOS}
                ):
                    found.append(source)
        for child in value.values():
            collect_attribution_nodes(child, found)
    elif isinstance(value, list):
        for child in value:
            collect_attribution_nodes(child, found)


def main(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    data = json.loads(original)
    sources: list[dict[str, Any]] = []
    collect_attribution_nodes(data, sources)
    if not sources:
        raise SystemExit("No Protomaps sources found in map style JSON")

    values = {source.get("attribution") for source in sources}
    if values - {UPSTREAM, FIELDOS}:
        raise SystemExit(f"Unexpected upstream Protomaps attribution(s): {values!r}")
    # Keep the upstream file's formatting when only the attribution strings
    # change. This keeps the generated diff and payload churn small.
    if all(value == FIELDOS for value in values):
        return

    # The pinned upstream JSON is pretty-printed with two-space indentation.
    # Replace only the JSON-escaped old attribution literal, preserving every
    # other byte in the style file.
    old_json = json.dumps(UPSTREAM, ensure_ascii=False)
    new_json = json.dumps(FIELDOS, ensure_ascii=False)
    old_sources = sum(source.get("attribution") == UPSTREAM for source in sources)
    count = original.count(old_json)
    if count != old_sources:
        raise SystemExit(
            f"Expected {old_sources} upstream attribution strings, found {count}; refusing style rewrite"
        )
    updated = original.replace(old_json, new_json)
    for source in sources:
        source["attribution"] = FIELDOS
    if json.loads(updated) != data:
        raise SystemExit("Attribution replacement changed unexpected style content")

    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(updated)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_map_attribution.py STYLE.json")
    main(Path(sys.argv[1]))
