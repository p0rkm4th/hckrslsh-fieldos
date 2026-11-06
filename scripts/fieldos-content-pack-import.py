#!/usr/bin/env python3
"""GNOME file-picker and authenticated installer for offline FieldOS packs."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ZENITY = "/usr/bin/zenity"
PKEXEC = "/usr/bin/pkexec"
ROOT_HELPER = "/usr/libexec/fieldos-content-pack-import-root"
INSTALLER = "/opt/fieldos/scripts/fieldos-content-packs.py"
INDEXER = "/opt/fieldos/scripts/fieldos-nomad-index-references.py"


def install_as_root() -> int:
    if os.geteuid() != 0:
        print("This helper must be started through the FieldOS authorization prompt.", file=sys.stderr)
        return 1
    if len(sys.argv) != 3:
        print("Expected one offline content pack path.", file=sys.stderr)
        return 2
    supplied = Path(sys.argv[2])
    try:
        if supplied.is_symlink():
            raise ValueError("The selected archive must not be a symbolic link.")
        archive = supplied.resolve(strict=True)
    except (OSError, ValueError) as exc:
        print(f"Cannot open the selected archive: {exc}", file=sys.stderr)
        return 2
    if not archive.is_file() or not archive.name.endswith(".tar.zst"):
        print("Choose a FieldOS .tar.zst content pack.", file=sys.stderr)
        return 2

    result = subprocess.run(
        [INSTALLER, "install", str(archive)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n", flush=True)
    if result.returncode:
        return result.returncode

    if "activated reference documents" in result.stdout:
        indexed = subprocess.run(
            ["/usr/bin/python3", INDEXER],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if indexed.stdout:
            print(indexed.stdout, end="" if indexed.stdout.endswith("\n") else "\n", flush=True)
        return indexed.returncode
    return 0


def show_dialog(kind: str, title: str, message: str) -> None:
    subprocess.run(
        [ZENITY, f"--{kind}", "--no-markup", f"--title={title}", f"--text={message}", "--width=560"],
        check=False,
    )


def run_gui() -> int:
    if not all(Path(path).is_file() for path in (ZENITY, PKEXEC, ROOT_HELPER)):
        print("FieldOS content import is missing zenity, pkexec, or its root helper.", file=sys.stderr)
        return 1
    choice = subprocess.run(
        [
            ZENITY,
            "--file-selection",
            "--title=Choose an offline FieldOS content pack",
            "--file-filter=FieldOS content packs | *.tar.zst",
            "--file-filter=All files | *",
            "--filename=/media/",
            "--width=720",
            "--height=520",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if choice.returncode:
        return 0
    archive = Path(choice.stdout.strip())
    if not archive.is_file() or not archive.name.endswith(".tar.zst"):
        show_dialog("error", "FieldOS Content Packs", "Choose a .tar.zst FieldOS content pack.")
        return 2
    if not Path(f"{archive}.sha256").is_file():
        show_dialog(
            "error",
            "FieldOS Content Packs",
            "The pack's matching .sha256 file is missing. Copy both files from the trusted source and try again.",
        )
        return 2

    # Authentication is required for the fixed, root-owned helper. The pack
    # path remains an untrusted input and is validated by the existing installer.
    worker = subprocess.Popen(
        [PKEXEC, ROOT_HELPER, str(archive)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    progress = subprocess.Popen(
        [
            ZENITY,
            "--progress",
            "--pulsate",
            "--no-cancel",
            "--auto-close",
            "--title=Installing offline content",
            "--text=Approve the administrator prompt, then wait while FieldOS verifies and activates the pack.",
            "--width=520",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    output: list[str] = []
    reference_activated = False
    map_activated = False
    zim_activated = False
    assert worker.stdout is not None
    try:
        for line in worker.stdout:
            line = line.rstrip()
            reference_activated |= "activated reference documents" in line
            map_activated |= "activated map" in line
            zim_activated |= "Kiwix ZIM archives" in line
            output.append(line)
            if len(output) > 40:
                output.pop(0)
            if progress.stdin is not None:
                try:
                    progress.stdin.write(f"#{line}\n")
                    progress.stdin.flush()
                except BrokenPipeError:
                    pass
        code = worker.wait()
    finally:
        if progress.stdin is not None:
            try:
                progress.stdin.write("100\n")
                progress.stdin.close()
            except BrokenPipeError:
                pass
        progress.wait()

    details = "\n".join(output)[-2800:]
    if code:
        show_dialog(
            "error",
            "Content pack not installed",
            "FieldOS could not install this pack. Check the checksum sidecar, available disk space, and pack compatibility.\n\n"
            + (details or "The administrator authorization was cancelled or installation failed."),
        )
        return code

    if reference_activated:
        message = "Reference documents were installed and indexed. Open FieldOS Source Library to read the originals."
    elif map_activated:
        message = "The map pack was installed. Open or reload Maps to select the new region."
    elif zim_activated:
        message = "The offline archive was installed and registered with Kiwix. Open or reload the offline reference library."
    else:
        message = "The pack passed validation and was installed. Its manifest may require a compatible FieldOS application."
    show_dialog("info", "Offline content ready", message)
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--install-as-root":
        return install_as_root()
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
