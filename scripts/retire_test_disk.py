#!/usr/bin/env python3
"""Safely retire one stopped disposable E2E disk while retaining its evidence."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence


class RetirementError(RuntimeError):
    pass


Runner = Callable[..., subprocess.CompletedProcess[str]]


def attached_file_disks(runner: Runner = subprocess.run) -> set[Path]:
    """Return file disks referenced by every domain in the current libvirt URI."""
    listed = runner(
        ["virsh", "list", "--all", "--name"],
        check=True, text=True, capture_output=True,
    )
    attached: set[Path] = set()
    for domain in (line.strip() for line in listed.stdout.splitlines()):
        if not domain:
            continue
        result = runner(
            ["virsh", "domblklist", domain, "--details"],
            check=True, text=True, capture_output=True,
        )
        for line in result.stdout.splitlines():
            fields = line.split(maxsplit=3)
            if len(fields) == 4 and fields[0] == "file":
                source = fields[3].strip()
                if source and source != "-":
                    attached.add(Path(source).resolve())
    return attached


def validate_candidate(
    disk_arg: Path,
    e2e_root_arg: Path,
    release_doc: Path,
    runner: Runner = subprocess.run,
) -> tuple[Path, Path]:
    """Fail closed unless this is a documented, stopped E2E guest disk."""
    if disk_arg.is_symlink():
        raise RetirementError("refusing a symlink disk path")
    try:
        disk = disk_arg.resolve(strict=True)
        e2e_root = e2e_root_arg.resolve(strict=True)
    except OSError as exc:
        raise RetirementError(f"disk or E2E root is unavailable: {exc}") from exc
    if disk.name != "guest.qcow2" or not disk.is_file():
        raise RetirementError("only a regular guest.qcow2 file may be retired")
    try:
        disk.relative_to(e2e_root)
    except ValueError as exc:
        raise RetirementError(f"disk must be inside E2E evidence root {e2e_root}") from exc

    report = disk.parent / "report.md"
    if report.is_symlink() or not report.is_file() or report.stat().st_size == 0:
        raise RetirementError("a non-empty report.md must remain beside the disk")
    if not release_doc.is_file():
        raise RetirementError(f"release record is unavailable: {release_doc}")
    release_text = release_doc.read_text(encoding="utf-8", errors="replace")
    if str(disk) in release_text:
        raise RetirementError("disk is referenced by docs/RELEASE.md; preserve it")

    if disk in attached_file_disks(runner):
        raise RetirementError("disk is attached to a libvirt domain; preserve it")

    try:
        info = runner(
            ["qemu-img", "info", "--output=json", str(disk)],
            check=True, text=True, capture_output=True,
        )
        image = json.loads(info.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise RetirementError(f"qemu-img could not safely inspect the disk: {exc}") from exc
    if image.get("format") != "qcow2":
        raise RetirementError("disk image format is not qcow2")
    return disk, report


def retire(disk: Path, reason: str, runner: Runner = subprocess.run) -> None:
    """Unlink only the exact checked disk and preserve a durable audit record."""
    if disk.is_symlink() or not disk.is_file():
        raise RetirementError("disk changed after validation; refusing retirement")
    disk = disk.resolve(strict=True)
    if disk in attached_file_disks(runner):
        raise RetirementError("disk became attached to a libvirt domain; preserve it")
    try:
        info = runner(
            ["qemu-img", "info", "--output=json", str(disk)],
            check=True, text=True, capture_output=True,
        )
        image = json.loads(info.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise RetirementError(f"qemu-img could not recheck the disk: {exc}") from exc
    if image.get("format") != "qcow2":
        raise RetirementError("disk format changed after validation; refusing retirement")
    record = disk.parent / "disk-retirement.txt"
    if record.is_symlink():
        raise RetirementError("refusing a symlink disk-retirement.txt")
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    event = (
        f"Retirement started: {timestamp}\nDisk: {disk}\nReason: {reason}\n"
    )
    fd = os.open(record, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        with os.fdopen(fd, "a", encoding="utf-8") as stream:
            stream.write(event)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        raise
    disk.unlink()
    with record.open("a", encoding="utf-8") as stream:
        stream.write(f"Result: removed {timestamp}\n\n")
        stream.flush()
        os.fsync(stream.fileno())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--disk", type=Path, required=True,
                        help="exact guest.qcow2 path beneath FIELDOS_E2E_ROOT")
    parser.add_argument("--e2e-root", type=Path,
                        default=Path(os.environ.get("FIELDOS_E2E_ROOT", "/mnt/shared/fieldos-e2e")))
    parser.add_argument("--release-doc", type=Path,
                        default=Path(__file__).resolve().parents[1] / "docs/RELEASE.md")
    parser.add_argument("--delete", action="store_true",
                        help="actually retire the checked disk; default is dry run")
    parser.add_argument("--reason", help="required audit reason when using --delete")
    args = parser.parse_args(argv)
    try:
        disk, report = validate_candidate(args.disk, args.e2e_root, args.release_doc)
        print(f"ELIGIBLE | {disk}")
        print(f"PRESERVE | {report} and all other run evidence")
        if not args.delete:
            print("DRY RUN | disk not changed; pass --delete and --reason to retire it")
            return 0
        if not args.reason or not args.reason.strip():
            raise RetirementError("--reason is required with --delete")
        retire(disk, args.reason.strip())
        print(f"RETIRED | {disk}; evidence retained in {disk.parent}")
        return 0
    except (RetirementError, OSError, subprocess.CalledProcessError) as exc:
        print(f"REFUSED | {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
