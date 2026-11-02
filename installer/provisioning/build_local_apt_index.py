#!/usr/bin/env python3
"""Write a minimal Packages index for the bundled offline .deb files."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


def field(package: Path, name: str) -> str:
    return subprocess.check_output(
        ["dpkg-deb", "--field", str(package), name], text=True
    ).strip()


def build_index(package_dir: Path, index_path: Path) -> None:
    records: list[str] = []
    for package in sorted(package_dir.glob("*.deb")):
        record = {
            "Package": field(package, "Package"),
            "Version": field(package, "Version"),
            "Architecture": field(package, "Architecture"),
            "Filename": f"{package_dir.name}/{package.name}",
            "Size": str(package.stat().st_size),
            "SHA256": hashlib.sha256(package.read_bytes()).hexdigest(),
        }
        for name in (
            "Depends",
            "Pre-Depends",
            "Conflicts",
            "Breaks",
            "Replaces",
            "Provides",
            "Multi-Arch",
            "Description",
        ):
            value = field(package, name)
            if value:
                record[name] = value
        records.append("\n".join(f"{key}: {value}" for key, value in record.items()))
    index_path.write_text("\n\n".join(records) + "\n", encoding="utf-8")


def main() -> None:
    build_index(Path(sys.argv[1]).resolve(), Path(sys.argv[2]))


if __name__ == "__main__":
    main()
