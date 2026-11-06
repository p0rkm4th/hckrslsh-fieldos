#!/usr/bin/env python3
"""Install and accept FieldOS in a fresh, network-disconnected libvirt VM."""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import io
import json
import os
import re
import secrets
import shlex
import string
import struct
import subprocess
import sys
import tarfile
import time
import zlib
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
import shutil
from shutil import disk_usage
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UBUNTU_ISO = Path("/mnt/shared/ISO Library/Linux Distributions/ubuntu-26.04.1-desktop-amd64.iso")
MIN_FREE_GIB = 48
KIWIX_BASE_URL = "http://127.0.0.1:8090"


def kiwix_zim_name(artifact_path: str) -> str:
    """Return kiwix-serve's filename-derived ZIM name for a ZIM artifact."""
    stem = Path(artifact_path).name.rsplit(".", 1)[0]
    normalized = unicodedata.normalize("NFKD", stem)
    ascii_stem = "".join(char for char in normalized if not unicodedata.combining(char))
    return ascii_stem.lower().replace("+", "plus").replace(" ", "_")


def e2e_content_pack_target_supported(target: str) -> bool:
    return target in {"storage/maps/pmtiles", "storage/references/documents", "storage/zim"}


def kiwix_content_url(zim_name: str) -> str:
    return f"{KIWIX_BASE_URL}/content/{quote(zim_name, safe='_-.')}"


def kiwix_library_identity(library_xml: str, archive_path: str) -> dict[str, str] | None:
    """Find a library record for absolute or kiwix-manage-relative archive paths."""
    try:
        root = ET.fromstring(library_xml)
    except ET.ParseError as exc:
        raise TestFailure(f"Kiwix generated invalid library XML: {exc}") from exc
    expected_path = PurePosixPath(archive_path.lstrip("/")).as_posix()
    for book in root.iter():
        if book.tag.rsplit("}", 1)[-1].lower() != "book":
            continue
        values = {key.rsplit("}", 1)[-1].lower(): value.strip() for key, value in book.attrib.items()}
        values.update({item.tag.rsplit("}", 1)[-1].lower(): item.text.strip()
                       for item in book if item.text})
        stored_path = values.get("path", "").strip()
        normalized_path = PurePosixPath(stored_path.lstrip("/")).as_posix()
        if normalized_path.startswith("data/"):
            normalized_path = normalized_path[len("data/"):]
        if normalized_path == expected_path:
            return {"id": values.get("id", ""), "title": values.get("title", ""),
                    "path": "/data/" + normalized_path}
    return None


def kiwix_library_ids(library_xml: str) -> set[str]:
    """Return all registered Kiwix book IDs from its library XML."""
    try:
        root = ET.fromstring(library_xml)
    except ET.ParseError as exc:
        raise TestFailure(f"Kiwix generated invalid library XML: {exc}") from exc
    identities: set[str] = set()
    for book in root.iter():
        if book.tag.rsplit("}", 1)[-1].lower() != "book":
            continue
        if book.attrib.get("id", "").strip():
            identities.add(book.attrib["id"].strip())
        identities.update(item.text.strip() for item in book
                          if item.tag.rsplit("}", 1)[-1].lower() == "id" and item.text and item.text.strip())
    return identities


def kiwix_catalog_entry(catalog_xml: str, identity: dict[str, str]) -> dict[str, str] | None:
    """Find the OPDS record corresponding to a library id or title."""
    try:
        root = ET.fromstring(catalog_xml)
    except ET.ParseError as exc:
        raise TestFailure(f"Kiwix returned invalid OPDS XML: {exc}") from exc
    for entry in root.iter():
        if entry.tag.rsplit("}", 1)[-1].lower() != "entry":
            continue
        values = {item.tag.rsplit("}", 1)[-1].lower(): item.text.strip()
                  for item in entry if item.text}
        entry_id, title = values.get("id", ""), values.get("title", "")
        if not ((identity.get("id") and entry_id == identity["id"])
                or (identity.get("title") and title == identity["title"])):
            continue
        return {"id": entry_id, "title": title}
    return None


def git_source_state() -> tuple[str, bool | None]:
    """Return the checked-out commit and whether local source changes exist."""
    try:
        revision = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
        )
        if revision.returncode:
            return "unknown", None
        status = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
        )
        if status.returncode:
            return revision.stdout.strip(), None
        return revision.stdout.strip(), bool(status.stdout.strip())
    except OSError:
        return "unknown", None


class TestFailure(RuntimeError):
    pass


def write_preflight_report(evidence_root: Path, stamp: str, reason: str) -> Path:
    """Record why an E2E run was refused before creating large artifacts."""
    evidence_root.mkdir(parents=True, exist_ok=True)
    report = evidence_root / f"preflight-{stamp}.md"
    report.write_text(
        "\n".join([
            "# FieldOS E2E preflight",
            "",
            "Status: **FAIL**",
            "",
            f"Reason: {reason}",
            "",
            "No ISO, VM disk, or test credentials were created.",
            "",
        ]),
        encoding="utf-8",
    )
    return report


class AcceptanceRun:
    def __init__(self) -> None:
        self.stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        evidence_root = Path(os.environ.get("FIELDOS_E2E_ROOT", ROOT / "build" / "e2e"))
        evidence_root.parent.mkdir(parents=True, exist_ok=True)
        # The last real run's test ISO plus installed qcow2 peaked below 46 GiB
        # of additional allocation; keep a small reserve while allowing a
        # rerun when the prior failed guest disk is intentionally preserved.
        if disk_usage(evidence_root.parent).free < MIN_FREE_GIB * 1024**3:
            raise TestFailure(f"Need at least {MIN_FREE_GIB} GiB free for isolated ISO and VM evidence on {evidence_root.parent}")
        work_root = Path(os.environ.get("FIELDOS_WORK_ROOT", evidence_root))
        work_root.parent.mkdir(parents=True, exist_ok=True)
        if disk_usage(work_root.parent).free < 8 * 1024**3:
            raise TestFailure(f"Need at least 8 GiB free for temporary ISO build work on {work_root.parent}")
        self.memory_mib = int(os.environ.get("FIELDOS_TEST_MEMORY_MIB", "12288"))
        if self.memory_mib < 8192:
            raise TestFailure("The full offline acceptance requires at least 8192 MiB guest RAM")
        catalog = json.loads((ROOT / "payload/manifests/content-packs.json").read_text())
        self.core_reference_manifests: list[dict] = []
        for entry in catalog.get("core_packs", []):
            manifest_path = ROOT / "payload/manifests" / entry
            manifest = json.loads(manifest_path.resolve(strict=True).read_text())
            if manifest.get("installation", {}).get("target") == "storage/references/documents":
                self.core_reference_manifests.append(manifest)
        self.core_reference_manifest = (self.core_reference_manifests[0]
                                         if self.core_reference_manifests else None)
        map_manifest = json.loads((ROOT / "payload/manifests/maps.json").read_text())
        self.regional_map = next(
            (item for item in map_manifest.get("regions", [])
             if item.get("id") == "tennessee-statewide"), None
        )
        self.pack_archive = Path(os.environ["FIELDOS_TEST_CONTENT_PACK"]).expanduser() if os.environ.get("FIELDOS_TEST_CONTENT_PACK") else None
        self.pack_manifest: dict | None = None
        self.pack_target: str | None = None
        if self.pack_archive:
            self.pack_archive = self.pack_archive.resolve(strict=True)
            if not self.pack_archive.is_file() or not Path(f"{self.pack_archive}.sha256").is_file():
                raise TestFailure("FIELDOS_TEST_CONTENT_PACK must name a bundle with its .sha256 sidecar")
            if not shutil.which("xorriso"):
                raise TestFailure("xorriso is required to create offline content-transfer media")
            unpacked = subprocess.run(
                ["zstd", "--decompress", "--stdout", str(self.pack_archive)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
            ).stdout
            with tarfile.open(fileobj=io.BytesIO(unpacked), mode="r:") as bundle:
                manifests = [item for item in bundle if item.isfile() and
                             item.name.startswith("content-packs/") and item.name.endswith("/manifest.json")]
                if len(manifests) != 1:
                    raise TestFailure("FIELDOS_TEST_CONTENT_PACK must contain exactly one pack manifest")
                manifest_stream = bundle.extractfile(manifests[0])
                if manifest_stream is None:
                    raise TestFailure("Could not read test content-pack manifest")
                self.pack_manifest = json.loads(manifest_stream.read())
            self.pack_target = self.pack_manifest.get("installation", {}).get("target")
            if not e2e_content_pack_target_supported(self.pack_target):
                raise TestFailure(f"No end-to-end activation check exists for pack target {self.pack_target!r}")
            if (self.pack_target == "storage/zim" and
                    any(Path(item.get("path", "")).suffix.lower() != ".zim"
                        for item in self.pack_manifest.get("artifacts", []))):
                raise TestFailure("Kiwix test packs must contain only .zim artifacts")
        self.run_dir = evidence_root / f"{self.stamp}-{os.getpid()}"
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.vm_name = f"fieldos-e2e-{self.stamp.lower()}"
        self.disk = self.run_dir / "guest.qcow2"
        self.iso = self.run_dir / "test.iso"
        self.pack_iso = self.run_dir / "content-pack-transfer.iso"
        self.user_data = self.run_dir / "user-data"
        self.results: list[dict[str, str]] = []
        self.agent_ready = False
        self.temporary_password = ""
        self.source_revision, self.source_dirty = git_source_state()

    def command(self, args: list[str], *, env: dict[str, str] | None = None,
                check: bool = True, timeout: int = 120) -> subprocess.CompletedProcess[str]:
        proc = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, env=env, timeout=timeout)
        if check and proc.returncode:
            raise TestFailure(f"Command failed ({proc.returncode}): {' '.join(args)}\n{proc.stdout[-5000:]}")
        return proc

    def prepare_iso(self) -> None:
        # Make exports UBUNTU_ISO even when the variable is empty; treat that the
        # same as unset so the documented default remains usable.
        ubuntu_iso = Path(os.environ.get("UBUNTU_ISO") or DEFAULT_UBUNTU_ISO)
        if not ubuntu_iso.is_file():
            raise TestFailure(f"Ubuntu installer ISO not found: {ubuntu_iso} (set UBUNTU_ISO)")
        # Lowercase test-only password is held in memory so the virtual GDM
        # console can log in without a physical keyboard or persisted secret.
        self.temporary_password = "".join(
            secrets.choice(string.ascii_lowercase) for _ in range(24)
        )
        hash_proc = subprocess.run(["openssl", "passwd", "-6", "-stdin"],
                                   input=self.temporary_password, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        # Keep installer-to-disk handoff deterministic in the test-only ISO
        # even if the desktop installer leaves its completion dialog visible.
        # This timer runs in the live installer after late commands; the
        # customer-facing interactive user-data is not modified.
        self.user_data.write_text(f"""#cloud-config
autoinstall:
  version: 1
  locale: en_US.UTF-8
  keyboard:
    layout: us
  identity:
    hostname: fieldos-test
    username: fieldos
    realname: FieldOS Acceptance Test
    password: '{hash_proc.stdout.strip()}'
  source:
    id: ubuntu-desktop
  apt:
    geoip: false
    fallback: offline-install
  storage:
    layout:
      name: lvm
  shutdown: poweroff
  late-commands:
    - mkdir -p /target/opt/fieldos
    - mkdir -p /target/usr/share/doc/fieldos
    - mkdir -p /target/home/fieldos/.config
    - mkdir -p /target/home/fieldos/.config/gnome-initial-setup
    - touch /target/home/fieldos/.config/gnome-initial-setup-done
    - touch /target/home/fieldos/.config/gnome-initial-setup/upgrade-26.04-done
    - chown -R 1000:1000 /target/home/fieldos/.config
    - cp -a /cdrom/fieldos/. /target/opt/fieldos/
    - curtin in-target --target=/target -- chmod 0755 /opt/fieldos/installer/provisioning/install-branding.sh
    - curtin in-target --target=/target -- /opt/fieldos/installer/provisioning/install-branding.sh
    - curtin in-target --target=/target -- chmod 0755 /opt/fieldos/installer/provisioning/firstboot.sh
    - cp /target/opt/fieldos/installer/provisioning/fieldos-firstboot.service /target/etc/systemd/system/fieldos-firstboot.service
    - curtin in-target --target=/target -- systemctl enable fieldos-firstboot.service
    - systemd-run --unit=fieldos-e2e-poweroff --on-active=90s /usr/bin/systemctl poweroff
""", encoding="utf-8")
        os.chmod(self.user_data, 0o600)
        build_env = os.environ.copy()
        build_env.update({
            "FIELDOS_AUTOINSTALL_FILE": str(self.user_data),
            "FIELDOS_VERIFY_MODE": "test",
            "FIELDOS_OUTPUT_PATH": str(self.iso),
            "FIELDOS_WORK_ROOT": os.environ.get("FIELDOS_WORK_ROOT", str(self.run_dir)),
            "FIELDOS_TEST_AUTOBOOT": "1",
        })
        self.command(["bash", str(ROOT / "build/build-iso.sh"), "test", str(ubuntu_iso)],
                     env=build_env, timeout=1800)
        self.record("test ISO build", "PASS", f"{self.iso.name}: {self.sha256(self.iso)}")
        if self.pack_archive:
            archive = self.pack_archive.resolve(strict=True)
            if not archive.is_file() or not Path(f"{archive}.sha256").is_file():
                raise TestFailure("FIELDOS_TEST_CONTENT_PACK must name a bundle with its .sha256 sidecar")
            media = self.run_dir / "pack-media"
            media.mkdir()
            shutil.copy2(archive, media / archive.name)
            shutil.copy2(Path(f"{archive}.sha256"), media / f"{archive.name}.sha256")
            self.command(["xorriso", "-as", "mkisofs", "-iso-level", "3", "-J", "-R",
                          "-V", "FIELDOSPACK", "-o", str(self.pack_iso), str(media)], timeout=120)
            self.record("optional content transfer media", "PASS",
                        f"offline ISO containing {archive.name}; SHA-256 {self.sha256(archive)}")

    def create_vm(self) -> None:
        if self.disk.exists():
            raise TestFailure(f"Refusing to overwrite VM disk: {self.disk}")
        self.command(["qemu-img", "create", "-f", "qcow2", str(self.disk), "80G"])
        vm_args = [
            "virt-install", "--name", self.vm_name, "--memory", str(self.memory_mib), "--vcpus", "6",
            "--disk", f"path={self.disk},format=qcow2,bus=virtio",
            "--cdrom", str(self.iso), "--network", "none", "--boot", "uefi",
            "--osinfo", "ubuntu26.04",
            "--graphics", "vnc,listen=127.0.0.1", "--video", "virtio",
            "--channel", "unix,target.type=virtio,target.name=org.qemu.guest_agent.0",
            "--noautoconsole", "--wait", "0",
        ]
        if self.pack_iso.exists():
            vm_args.extend(["--disk", f"path={self.pack_iso},device=cdrom,readonly=on,bus=sata"])
        self.command(vm_args, timeout=180)
        self.record("disposable VM", "PASS",
                    f"{self.vm_name}; 80 GiB qcow2; {self.memory_mib} MiB RAM; no virtual NIC")

    def wait_for_install_shutdown(self, timeout: int = 2400) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            state = self.command(["virsh", "domstate", self.vm_name], check=False, timeout=15).stdout.strip()
            if state.lower() in {"shut off", "shutdown"}:
                self.record("Ubuntu unattended installation", "PASS", "Installer powered off after disk install")
                return
            if state.lower() == "running" and self.ping_agent(tries=1):
                self.agent_ready = True
                self.record("Ubuntu unattended installation", "PASS",
                            "Installed OS booted from the disposable disk")
                return
            time.sleep(5)
        self.capture_guest_logs()
        raise TestFailure("Timed out waiting for unattended Ubuntu install to power off")

    def eject_installer(self) -> None:
        xml = self.command(["virsh", "dumpxml", self.vm_name]).stdout
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml)
        for disk in root.findall("./devices/disk[@device='cdrom']"):
            source = disk.find("source")
            target = disk.find("target")
            dev = target.get("dev") if target is not None else None
            path = source.get("file") if source is not None else None
            if dev and path == str(self.iso):
                self.command(["virsh", "change-media", self.vm_name, dev,
                              "--eject", "--config"], check=False)

    def install_test_content_pack(self) -> None:
        if not self.pack_archive:
            self.record("offline optional content pack", "SKIP", "FIELDOS_TEST_CONTENT_PACK was not supplied")
            return
        common = (
            "set -euo pipefail; device=$(blkid -t LABEL=FIELDOSPACK -o device); "
            "test -n \"$device\"; mkdir -p /mnt/fieldos-pack-test; "
            "mounted=$(findmnt -rn -S \"$device\" -o TARGET | head -n 1 || true); "
            "if [[ \"$mounted\" != /mnt/fieldos-pack-test ]]; then "
            "[[ -z \"$mounted\" ]] || umount \"$mounted\"; "
            "mount -o ro \"$device\" /mnt/fieldos-pack-test; fi; "
            "findmnt -rn -o OPTIONS /mnt/fieldos-pack-test | grep -qw ro; "
        )
        self.check("read-only content transfer media", common +
                   f"test -s /mnt/fieldos-pack-test/{shlex.quote(self.pack_archive.name)} && "
                   f"test -s /mnt/fieldos-pack-test/{shlex.quote(self.pack_archive.name + '.sha256')}")
        zim_library_before = None
        if self.pack_target == "storage/zim":
            zim_library_before = self.guest("cat /var/lib/fieldos/storage/zim/kiwix-library.xml")
            for artifact in self.pack_manifest["artifacts"]:
                if kiwix_library_identity(zim_library_before, artifact["path"]):
                    raise TestFailure(f"ZIM archive was already registered before import: {artifact['path']}")
        uid = self.guest("id -u fieldos").strip()
        wayland = self.guest(
            f"find /run/user/{uid} -maxdepth 1 -type s -name 'wayland-*' -printf '%f\\n' | head -n 1"
        ).strip()
        if not wayland.startswith("wayland-"):
            raise TestFailure(f"No active Wayland session for content-pack GUI test: {wayland!r}")
        # Launch the GUI from GNOME itself. Launching through the guest agent,
        # even with copied Wayland and DBus variables, does not associate the
        # pkexec caller with the active logind session used for authentication.
        self.send_key("KEY_LEFTMETA")
        time.sleep(0.7)
        self.type_virtual_keyboard("fieldos install content pack")
        time.sleep(1.0)
        self.send_key("KEY_ENTER")
        picker = self.guest(
            f"for i in $(seq 1 60); do "
            f"pgrep -u {uid} -f 'zenity --file-selection' >/dev/null && echo PICKER_OPEN && exit 0; sleep 0.5; "
            "done; pgrep -af 'fieldos-content-pack-import|zenity' || true; exit 1",
            timeout=40,
        )
        if "PICKER_OPEN" not in picker:
            raise TestFailure("GNOME content-pack file picker did not open")
        archive_path = f"/mnt/fieldos-pack-test/{self.pack_archive.name}"
        self.send_key("KEY_LEFTCTRL", "KEY_L")
        time.sleep(0.5)
        self.type_virtual_keyboard(archive_path)
        self.send_key("KEY_ENTER")
        picker_state = self.guest(
            f"for i in $(seq 1 12); do "
            f"if ! pgrep -u {uid} -f 'zenity --file-selection' >/dev/null; then "
            "echo PICKER_CLOSED; exit 0; fi; sleep 0.5; done; echo PICKER_STILL_OPEN",
            timeout=15,
        )
        if "PICKER_STILL_OPEN" in picker_state:
            # GTK's Ctrl+L location entry first navigates to the containing
            # directory and selects the file; a second Enter accepts it.
            self.send_key("KEY_ENTER")
            picker_state = self.guest(
                f"for i in $(seq 1 30); do "
                f"if ! pgrep -u {uid} -f 'zenity --file-selection' >/dev/null; then "
                "echo PICKER_CLOSED; exit 0; fi; sleep 0.5; done; "
                "echo PICKER_STILL_OPEN; exit 1",
                timeout=20,
            )
        if "PICKER_CLOSED" not in picker_state:
            screenshot = self.run_dir / "content-pack-import-picker-failed.png"
            self.command(["virsh", "screenshot", self.vm_name, str(screenshot)], check=False)
            raise TestFailure("The selected archive remained in the GNOME file picker")
        prompt = self.guest(
            f"for i in $(seq 1 45); do "
            # pkexec is setuid-root while it waits; match the logged-in
            # caller's real UID rather than its effective UID.
            "pgrep -U " + str(uid) + " -af 'pkexec.*fieldos-content-pack-import-root' "
            ">/dev/null && echo AUTH_REQUESTED && exit 0; sleep 1; done; "
            "pgrep -af 'zenity|pkexec|fieldos-content-pack-import' || true; exit 1",
            timeout=55,
        )
        if "AUTH_REQUESTED" not in prompt:
            screenshot = self.run_dir / "content-pack-import-auth-failed.png"
            self.command(["virsh", "screenshot", self.vm_name, str(screenshot)], check=False)
            raise TestFailure(f"Selecting the pack did not reach the administrator prompt: {prompt}")
        time.sleep(1)
        self.type_virtual_keyboard(self.temporary_password)
        self.send_key("KEY_ENTER")
        success = self.guest(
            f"for i in $(seq 1 240); do "
            f"pgrep -u {uid} -af 'zenity.*Offline content ready' >/dev/null && echo SUCCESS_DIALOG && exit 0; "
            "sleep 1; done; "
            "pgrep -af 'zenity|pkexec|fieldos-content-pack-import' || true; exit 1",
            timeout=260,
        )
        if "SUCCESS_DIALOG" not in success:
            screenshot = self.run_dir / "content-pack-import-failed.png"
            self.command(["virsh", "screenshot", self.vm_name, str(screenshot)], check=False)
            raise TestFailure(f"Graphical content import did not reach its success dialog: {success}")
        screenshot = self.run_dir / "content-pack-import-success.png"
        self.command(["virsh", "screenshot", self.vm_name, str(screenshot)], timeout=30)
        self.send_key("KEY_ENTER")
        self.record("offline GUI content-pack import", "PASS",
                    f"GNOME file picker, authenticated installer, and success dialog; screenshot {screenshot.name}")
        self.check(
            "GUI importer completed",
            f"! pgrep -u {uid} -f '/opt/fieldos/scripts/fieldos-content-pack-import.py' >/dev/null",
        )
        if self.pack_target == "storage/maps/pmtiles":
            map_file = self.pack_manifest["artifacts"][0]["path"]
            installed = self.check(
                "offline content pack transfer and map activation",
                common + f"test -f /var/lib/fieldos/storage/maps/pmtiles/{shlex.quote(map_file)}",
                350,
            )
            if "activated map:" not in installed:
                raise TestFailure(f"Optional map bundle was not activated from removable media: {installed}")
        elif self.pack_target == "storage/zim":
            assert self.pack_manifest is not None and zim_library_before is not None
            pack_id, version = self.pack_manifest["id"], self.pack_manifest["version"]
            quote = shlex.quote
            artifact_checks = []
            # Activation may hard-link or use the installer's verified copy
            # fallback when the target filesystem disallows hard links.
            # Check content identity; inode identity is not a product contract.
            for artifact in self.pack_manifest["artifacts"]:
                source_path = f"/var/lib/fieldos/content-packs/{pack_id}/{version}/{artifact['path']}"
                zim_path = f"/var/lib/fieldos/storage/zim/{artifact['path']}"
                artifact_checks.extend([
                    f"test -s {quote(source_path)}",
                    f"test -s {quote(zim_path)}",
                    f"printf '%s  %s\\n' {quote(artifact['sha256'])} {quote(source_path)} | sha256sum -c -",
                    f"printf '%s  %s\\n' {quote(artifact['sha256'])} {quote(zim_path)} | sha256sum -c -",
                ])
            self.check(
                "offline ZIM pack transfer and persistent activation",
                " && ".join(artifact_checks),
            )
            library_xml = self.guest("cat /var/lib/fieldos/storage/zim/kiwix-library.xml")
            before_ids = kiwix_library_ids(zim_library_before)
            identities = []
            for artifact in self.pack_manifest["artifacts"]:
                identity = kiwix_library_identity(library_xml, artifact["path"])
                if not identity:
                    raise TestFailure(f"Kiwix library XML does not register {artifact['path']}")
                if identity.get("id") and identity["id"] in before_ids:
                    raise TestFailure(f"Kiwix library entry was not newly registered: {identity['id']}")
                identities.append(identity)

            entries = []
            deadline = time.monotonic() + 120
            while time.monotonic() < deadline:
                catalog = self.guest(
                    "curl --fail --silent --show-error --max-time 10 "
                    "'http://127.0.0.1:8090/catalog/v2/entries?count=-1'",
                    timeout=20,
                )
                entries = [kiwix_catalog_entry(catalog, identity) for identity in identities]
                if all(entries):
                    break
                time.sleep(2)
            if not all(entries):
                missing = [artifact["path"] for artifact, entry in zip(self.pack_manifest["artifacts"], entries)
                           if not entry]
                raise TestFailure(f"New ZIM record(s) were not visible in Kiwix OPDS catalog: {missing}")
            entry = entries[0]
            self.record("Kiwix OPDS catalog registration", "PASS",
                        f"{len(entries)} new archive record(s); first: {entry.get('id') or '(no id)'}: "
                        f"{entry.get('title') or self.pack_manifest['title']}")

            artifact = self.pack_manifest["artifacts"][0]
            artifact_path = artifact["path"]
            zim_name = kiwix_zim_name(artifact_path)
            article_url = kiwix_content_url(zim_name)
            article = self.check(
                "offline ZIM article retrieved through Kiwix",
                "set -euo pipefail; out=/tmp/fieldos-e2e-kiwix-article.html; "
                f"code=$(curl --fail --silent --show-error --location --max-time 60 -o \"$out\" "
                f"-w '%{{http_code}}' {quote(article_url)}); test \"$code\" = 200; "
                "python3 -c 'import html,re,sys; text=open(sys.argv[1],encoding=\"utf-8\",errors=\"replace\").read(); "
                "match=re.search(r\"<title[^>]*>(.*?)</title>\",text,re.I|re.S); "
                "title=html.unescape(re.sub(r\"<[^>]+>\",\"\",match.group(1))).strip() if match else \"\"; "
                "assert title, \"article response has no title\"; print(\"HTTP=200 TITLE=\"+title)' \"$out\"",
                timeout=90,
            )
            title_match = re.search(r"TITLE=(.+)$", article)
            if not title_match:
                raise TestFailure(f"Kiwix article response had no visible document title: {article}")

            uid = self.guest("id -u fieldos").strip()
            wayland = self.guest(
                f"find /run/user/{uid} -maxdepth 1 -type s -name 'wayland-*' -printf '%f\\n' | head -n 1"
            ).strip()
            if not wayland.startswith("wayland-"):
                raise TestFailure(f"No active Wayland session for Kiwix browser check: {wayland!r}")
            self.guest(
                f"uid={uid}; runtime=/run/user/$uid; wayland={wayland}; "
                "runuser -u fieldos -- env \"XDG_RUNTIME_DIR=$runtime\" "
                "\"DBUS_SESSION_BUS_ADDRESS=unix:path=$runtime/bus\" \"WAYLAND_DISPLAY=$wayland\" "
                "GDK_BACKEND=wayland /usr/bin/firefox --new-window "
                f"{quote(article_url)} "
                ">/tmp/fieldos-kiwix-firefox.log 2>&1 </dev/null &",
                timeout=30,
            )
            time.sleep(10)
            screenshot = self.run_dir / "kiwix-zim-article-render.png"
            self.command(["virsh", "screenshot", self.vm_name, str(screenshot)], timeout=30)
            width, height, colors, _water_pixels = self.screenshot_color_count(screenshot)
            if colors < 500:
                raise TestFailure(
                    f"Kiwix article did not visibly render in Firefox: {colors} sampled colors "
                    f"in {width}x{height} screenshot"
                )
            self.record("offline Kiwix Firefox page", "PASS",
                        f"Firefox opened article title {title_match.group(1).strip()!r}; "
                        f"{width}x{height}, {colors} sampled colors; screenshot {screenshot.name}")
            return
        else:
            assert self.pack_manifest is not None
            pack_id, version = self.pack_manifest["id"], self.pack_manifest["version"]
            quote = shlex.quote
            checks = [
                "test -s /var/lib/fieldos/storage/references/index.html",
                f"grep -Fq {quote(pack_id)} /var/lib/fieldos/storage/references/index.html",
            ]
            for artifact in self.pack_manifest["artifacts"]:
                artifact_path = f"/var/lib/fieldos/content-packs/{pack_id}/{version}/{artifact['path']}"
                checks.append(f"test -s {quote(artifact_path)}")
                web_artifact_path = f"/var/lib/fieldos/storage/references/documents/{pack_id}/{version}/{artifact['path']}"
                checks.append(f"test -s {quote(web_artifact_path)}")
                checks.append(
                    f"printf '%s  %s\\n' {quote(artifact['sha256'])} {quote(web_artifact_path)} | sha256sum -c -"
                )
            self.check(
                "offline content pack transfer and source-library activation",
                common + " && ".join(checks), 350,
            )
            index_checks = [
                "grep -Fq 'not endorsed by the publishers' /var/lib/fieldos/storage/references/index.html"
            ]
            for artifact in self.pack_manifest["artifacts"]:
                index_checks.append(
                    f"grep -Fq {quote(Path(artifact['path']).name)} "
                    "/var/lib/fieldos/storage/references/index.html"
                )
            self.check("source library attribution and local document links", " && ".join(index_checks))
            indexed = self.check(
                "N.O.M.A.D. indexes transferred reference pack",
                "python3 /opt/fieldos/scripts/fieldos-nomad-index-references.py",
                timeout=1200,
            )
            if "Indexed " not in indexed and "No installed reference documents need" not in indexed:
                raise TestFailure(f"Reference pack indexing did not report completion: {indexed}")
            self.record("offline content pack transfer", "PASS",
                        f"{pack_id} verified from removable media; source index and documents remain available")
            return
        regions = self.check(
            "N.O.M.A.D. discovers the imported regional map",
            "curl --fail --silent --show-error http://127.0.0.1:8080/api/maps/regions",
        )
        region_data = json.loads(regions)
        filename = "tennessee-20261102-z13.pmtiles"
        if not any(row.get("name") == filename for row in region_data.get("files", [])):
            raise TestFailure(f"N.O.M.A.D. did not discover imported map {filename}: {regions}")
        styles = self.check(
            "imported Tennessee map is registered in the map style",
            "curl --fail --silent --show-error http://127.0.0.1:8080/api/maps/styles",
        )
        if "tennessee-20261102-z13" not in json.loads(styles).get("sources", {}):
            raise TestFailure("N.O.M.A.D. map style does not include the imported regional map")
        tile = self.check(
            "imported Tennessee map tile is readable offline",
            "docker exec nomad_admin /usr/local/bin/pmtiles tile "
            "/app/storage/maps/pmtiles/tennessee-20261102-z13.pmtiles 13 2121 3212 2>/dev/null | wc -c",
        )
        if not tile.isdigit() or int(tile) <= 0:
            raise TestFailure(f"Imported regional map did not yield a vector tile: {tile!r}")

    def boot_guest(self) -> None:
        self.eject_installer()
        state = self.command(["virsh", "domstate", self.vm_name], check=False).stdout.strip().lower()
        if state in {"shut off", "shutdown"}:
            self.command(["virsh", "start", self.vm_name])
        if not self.agent_ready and not self.wait_for_agent(timeout=900):
            self.capture_guest_logs()
            raise TestFailure("Installed guest did not start QEMU guest agent")
        self.agent_ready = True

    def wait_for_provisioning(self, timeout: int = 2400) -> str:
        deadline = time.monotonic() + timeout
        last_log_at = 0.0
        while time.monotonic() < deadline:
            result = self.guest("cat /var/lib/fieldos/provisioning-status.json 2>/dev/null || true", timeout=30)
            if '"status":"complete"' in result or '"status":"failed"' in result:
                return result
            now = time.monotonic()
            if now - last_log_at >= 30:
                try:
                    logs = self.guest("tail -80 /var/log/fieldos-firstboot.log 2>/dev/null || true", timeout=30)
                    (self.run_dir / "firstboot.log").write_text(logs + "\n", encoding="utf-8")
                except Exception:
                    pass
                last_log_at = now
            time.sleep(5)
        raise TestFailure("Timed out waiting for firstboot completion; see captured firstboot.log")

    def ping_agent(self, tries: int = 1) -> bool:
        for _ in range(tries):
            result = self.command(["virsh", "qemu-agent-command", self.vm_name,
                                   '{"execute":"guest-ping"}'], check=False, timeout=10)
            if result.returncode == 0 and '"return"' in result.stdout:
                return True
            time.sleep(1)
        return False

    def wait_for_agent(self, timeout: int) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            state = self.command(["virsh", "domstate", self.vm_name], check=False, timeout=15).stdout.strip().lower()
            if state in {"shut off", "shutdown"}:
                time.sleep(2)
                self.command(["virsh", "start", self.vm_name], check=False)
            elif state == "running" and self.ping_agent():
                return True
            time.sleep(3)
        return False

    def guest(self, command: str, timeout: int = 180) -> str:
        request = json.dumps({"execute": "guest-exec", "arguments": {
            "path": "/bin/bash", "arg": ["-lc", command], "capture-output": True,
        }})
        started = self.command(["virsh", "qemu-agent-command", self.vm_name, request], timeout=20)
        pid = json.loads(started.stdout)["return"]["pid"]
        deadline = time.monotonic() + timeout
        status: dict = {}
        while time.monotonic() < deadline:
            poll = self.command(["virsh", "qemu-agent-command", self.vm_name, json.dumps({
                "execute": "guest-exec-status", "arguments": {"pid": pid},
            })], timeout=20)
            status = json.loads(poll.stdout)["return"]
            if status.get("exited"):
                break
            time.sleep(1)
        else:
            raise TestFailure(f"Guest command timed out: {command}")
        output = base64.b64decode(status.get("out-data", "")).decode(errors="replace")
        error = base64.b64decode(status.get("err-data", "")).decode(errors="replace")
        if status.get("exitcode", 0) != 0:
            raise TestFailure(f"Guest command failed ({status.get('exitcode')}): {command}\n{output}\n{error}")
        return output.strip()

    def capture_guest_logs(self) -> None:
        if not self.agent_ready and not self.ping_agent(tries=2):
            return
        self.agent_ready = True
        for filename, command in {
            "firstboot.log": "cat /var/log/fieldos-firstboot.log 2>/dev/null || true",
            "firstboot-status.json": "cat /var/lib/fieldos/provisioning-status.json 2>/dev/null || true",
            "installer.log": "for f in /var/log/installer/curtin-install.log /var/log/installer/subiquity-server-debug.log; do [ ! -f $f ] || { echo ===$f; tail -400 $f; }; done",
            "systemd-firstboot.log": "journalctl -u fieldos-firstboot.service -b --no-pager 2>/dev/null | tail -400 || true",
            "docker-compose-ps.txt": "docker ps -a --no-trunc 2>/dev/null || true",
        }.items():
            try:
                (self.run_dir / filename).write_text(self.guest(command), encoding="utf-8")
            except Exception as exc:
                (self.run_dir / filename).write_text(f"Log capture failed: {exc}\n", encoding="utf-8")

    def check(self, name: str, command: str, evidence_limit: int = 300,
              timeout: int = 180) -> str:
        output = self.guest(command, timeout=timeout)
        evidence = output.replace("\n", " | ")[:evidence_limit]
        self.record(name, "PASS", evidence or "command completed")
        return output

    def record(self, name: str, status: str, evidence: str) -> None:
        self.results.append({"component": name, "status": status, "evidence": evidence})
        print(f"{status:4}  {name}: {evidence}", flush=True)

    def send_key(self, *keys: str) -> None:
        self.command(["virsh", "send-key", self.vm_name, *keys], timeout=15)

    def type_virtual_keyboard(self, text: str) -> None:
        keymap = {char: f"KEY_{char.upper()}" for char in string.ascii_lowercase}
        keymap.update({char: f"KEY_{char}" for char in string.digits})
        keymap.update({" ": "KEY_SPACE", "/": "KEY_SLASH", ".": "KEY_DOT", "=": "KEY_EQUAL", "-": "KEY_MINUS"})
        for char in text:
            if char == ":":
                self.send_key("KEY_LEFTSHIFT", "KEY_SEMICOLON")
            elif char == "?":
                self.send_key("KEY_LEFTSHIFT", "KEY_SLASH")
            elif char == "&":
                self.send_key("KEY_LEFTSHIFT", "KEY_7")
            elif char in keymap:
                self.send_key(keymap[char])
            else:
                raise TestFailure(f"No virtual keyboard mapping for {char!r}")
            time.sleep(0.08)

    @staticmethod
    def screenshot_color_count(path: Path) -> tuple[int, int, int, int]:
        data = path.read_bytes()
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise TestFailure(f"Map screenshot is not a PNG: {path}")
        offset = 8
        compressed = bytearray()
        width = height = bit_depth = color_type = interlace = None
        while offset < len(data):
            length = struct.unpack_from(">I", data, offset)[0]
            kind = data[offset + 4:offset + 8]
            chunk = data[offset + 8:offset + 8 + length]
            offset += 12 + length
            if kind == b"IHDR":
                width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
            elif kind == b"IDAT":
                compressed.extend(chunk)
            elif kind == b"IEND":
                break
        if width is None or bit_depth != 8 or color_type != 2 or interlace != 0:
            raise TestFailure("Expected a non-interlaced 8-bit RGB VNC screenshot")
        pixels = zlib.decompress(compressed)
        stride = width * 3
        prior = bytearray(stride)
        colors: set[tuple[int, int, int]] = set()
        cursor = 0
        # The map canvas begins below the browser chrome and N.O.M.A.D. toolbar.
        crop_top = max(0, height * 3 // 10)
        crop_left = width // 16
        crop_right = width - width // 64
        water_pixels = 0
        for y in range(height):
            filter_type = pixels[cursor]
            row = bytearray(pixels[cursor + 1:cursor + 1 + stride])
            cursor += stride + 1
            for i in range(stride):
                left = row[i - 3] if i >= 3 else 0
                up = prior[i]
                upper_left = prior[i - 3] if i >= 3 else 0
                if filter_type == 1:
                    predictor = left
                elif filter_type == 2:
                    predictor = up
                elif filter_type == 3:
                    predictor = (left + up) // 2
                elif filter_type == 4:
                    p = left + up - upper_left
                    pa, pb, pc = abs(p - left), abs(p - up), abs(p - upper_left)
                    predictor = left if pa <= pb and pa <= pc else up if pb <= pc else upper_left
                elif filter_type == 0:
                    predictor = 0
                else:
                    raise TestFailure(f"Unsupported PNG row filter {filter_type}")
                row[i] = (row[i] + predictor) & 255
            if y >= crop_top and y < height - 15:
                for x in range(crop_left, crop_right, 4):
                    start = x * 3
                    color = (row[start], row[start + 1], row[start + 2])
                    colors.add(color)
                    if 115 <= color[0] <= 140 and 205 <= color[1] <= 235 and 220 <= color[2] <= 245:
                        water_pixels += 1
            prior = row
        return width, height, len(colors), water_pixels

    def verify_map_render(self) -> None:
        # Log into the disposable guest through its loopback-only VNC console.
        self.send_key("KEY_ENTER")
        time.sleep(1)
        self.type_virtual_keyboard(self.temporary_password)
        self.send_key("KEY_ENTER")
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            sessions = self.guest("loginctl list-sessions --no-legend", timeout=20)
            if any("fieldos" in line and "gdm" not in line for line in sessions.splitlines()):
                break
            time.sleep(3)
        else:
            raise TestFailure("Temporary user did not reach a graphical desktop session")

        # Ubuntu's greeter can launch gnome-initial-setup for the autoinstall
        # account even when the completion marker is present. Close that first
        # login helper by its process signal before opening the browser. This
        # avoids depending on the wizard's changing page count or its text.
        self.guest("pkill -TERM -f '^/usr/libexec/gnome-initial-setup' 2>/dev/null || true; "
                   "for i in $(seq 1 20); do "
                   "! pgrep -f '^/usr/libexec/gnome-initial-setup' >/dev/null && exit 0; sleep 0.5; "
                   "done; exit 1", timeout=20)

        # Launch the installed browser in the active user's Wayland session.
        # This avoids relying on version-specific GNOME search behavior.
        uid = self.guest("id -u fieldos")
        wayland = self.guest(
            f"runtime=/run/user/{uid}; "
            "for i in $(seq 1 60); do "
            "socket=$(find \"$runtime\" -maxdepth 1 -type s -name 'wayland-*' "
            "-printf '%f\\n' | head -n 1); "
            "if [ -n \"$socket\" ] && [ -S \"$runtime/$socket\" ]; then "
            "printf '%s\\n' \"$socket\"; exit 0; fi; sleep 1; "
            "done; echo 'Timed out waiting for the logged-in Wayland socket' >&2; exit 1",
            timeout=75,
        ).splitlines()[-1]
        if not wayland.startswith("wayland-"):
            raise TestFailure(f"Unexpected Wayland socket name: {wayland!r}")
        launch = (
            f"uid={uid}; runtime=/run/user/$uid; wayland={wayland}; "
            "test -S \"$runtime/$wayland\" || exit 1; "
            f"map_url='http://127.0.0.1:8080/maps{('?lat=36.1627&lng=-86.7816&zoom=13' if self.regional_map else '')}'; "
            "runuser -u fieldos -- env \"XDG_RUNTIME_DIR=$runtime\" "
            "\"DBUS_SESSION_BUS_ADDRESS=unix:path=$runtime/bus\" \"WAYLAND_DISPLAY=$wayland\" "
            "GDK_BACKEND=wayland /usr/bin/firefox --new-window \"$map_url\" "
            ">/tmp/fieldos-firefox.log 2>&1 </dev/null &"
        )
        self.guest(launch, timeout=30)
        self.guest(
            f"for i in $(seq 1 40); do pgrep -u {uid} -f '/snap/firefox/.*/firefox' >/dev/null "
            "&& exit 0; sleep 1; done; cat /tmp/fieldos-firefox.log; exit 1", timeout=50)
        time.sleep(20)
        render_locations = [
            ("Memphis", 35.1495, -90.0490),
            ("Nashville", 36.1627, -86.7816),
            ("Knoxville", 35.9606, -83.9207),
            ("Chattanooga", 35.0456, -85.3097),
            ("Clarksville", 36.5298, -87.3595),
            ("Jackson", 35.6145, -88.8139),
            ("Johnson City", 36.3134, -82.3535),
            ("Big South Fork rural area", 36.5, -84.65),
        ] if self.regional_map else [("world overview", 20.0, 0.0)]
        for location, lat, lng in render_locations:
            slug = re.sub(r"[^a-z0-9]+", "-", location.lower()).strip("-")
            screenshot = self.run_dir / f"map-render-{slug}.png"
            zoom = 13 if self.regional_map else 3
            url = f"http://127.0.0.1:8080/maps?lat={lat}&lng={lng}&zoom={zoom}"
            self.send_key("KEY_LEFTCTRL", "KEY_L")
            time.sleep(0.4)
            self.type_virtual_keyboard(url)
            self.send_key("KEY_ENTER")
            time.sleep(8)
            deadline = time.monotonic() + 60
            width = height = colors = water_pixels = 0
            while time.monotonic() < deadline:
                self.command(["virsh", "screenshot", self.vm_name, str(screenshot)], timeout=30)
                width, height, colors, water_pixels = self.screenshot_color_count(screenshot)
                if colors >= 1000:
                    break
                time.sleep(4)
            if colors < 1000:
                raise TestFailure(
                    f"Offline map did not render at {location}: {water_pixels} water pixels, "
                    f"{colors} sampled colors in {width}x{height} screenshot"
                )
            self.record(f"offline map render: {location}", "PASS",
                        f"Firefox screenshot {screenshot.name}, {width}x{height}; "
                        f"{water_pixels} water pixels and {colors} sampled colors")

        settings = self.guest(
            f"runtime=/run/user/{uid}; "
            f"runuser -u fieldos -- env XDG_RUNTIME_DIR=$runtime "
            "DBUS_SESSION_BUS_ADDRESS=unix:path=$runtime/bus "
            "gsettings get org.gnome.desktop.background picture-uri; "
            f"runuser -u fieldos -- env XDG_RUNTIME_DIR=$runtime "
            "DBUS_SESSION_BUS_ADDRESS=unix:path=$runtime/bus "
            "gsettings get org.gnome.desktop.interface color-scheme; "
            f"runuser -u fieldos -- env XDG_RUNTIME_DIR=$runtime "
            "DBUS_SESSION_BUS_ADDRESS=unix:path=$runtime/bus "
            "gsettings get org.gnome.shell favorite-apps",
            timeout=30,
        )
        if ("fieldos-wallpaper.svg" not in settings or "prefer-dark" not in settings
                or "fieldos-start-here.desktop" not in settings
                or "fieldos-nomad.desktop" not in settings):
            raise TestFailure(f"GNOME did not load the FieldOS wallpaper/dock defaults: {settings}")
        self.record("FieldOS desktop defaults", "PASS",
                    "effective GNOME session uses the FieldOS wallpaper, dark palette, and both FieldOS dock shortcuts")

    def verify_reference_library_render(self) -> None:
        manifest = (self.pack_manifest if self.pack_target == "storage/references/documents"
                    else self.core_reference_manifest)
        if manifest is None:
            return
        pack_id, version = manifest["id"], manifest["version"]
        first_artifact = manifest["artifacts"][0]
        document_path = "/".join(quote(part, safe="") for part in first_artifact["path"].split("/"))
        index_url = "http://127.0.0.1:8080/fieldos-references/index.html"
        document_url = f"http://127.0.0.1:8080/fieldos-references/documents/{pack_id}/{version}/{document_path}"
        served = self.check(
            "reference library served from local N.O.M.A.D. web UI",
            f"curl --fail --silent --show-error '{index_url}' | grep -F 'FieldOS Source Library' && "
            f"curl --fail --silent --show-error '{index_url}' | grep -F 'id=\"source-search\"' && "
            f"curl --fail --silent --show-error '{index_url}' | grep -F 'data-body=' && "
            f"curl --fail --silent --show-error -o /dev/null -w 'DOCUMENT_HTTP=%{{http_code}}' '{document_url}'",
        )
        if "DOCUMENT_HTTP=200" not in served:
            raise TestFailure(f"Local reference document was not served over the loopback web UI: {served}")
        uid = self.guest("id -u fieldos")
        wayland = self.guest(
            f"find /run/user/{uid} -maxdepth 1 -type s -name 'wayland-*' -printf '%f\\n' | head -n 1"
        ).strip()
        if not wayland.startswith("wayland-"):
            raise TestFailure(f"No active Wayland session for source-library browser check: {wayland!r}")
        self.guest(
            f"uid={uid}; runtime=/run/user/$uid; wayland={wayland}; "
            "runuser -u fieldos -- env \"XDG_RUNTIME_DIR=$runtime\" "
            "\"DBUS_SESSION_BUS_ADDRESS=unix:path=$runtime/bus\" \"WAYLAND_DISPLAY=$wayland\" "
            "GDK_BACKEND=wayland /usr/bin/firefox --new-window "
            f"'{index_url}' "
            ">/tmp/fieldos-reference-firefox.log 2>&1 </dev/null &",
            timeout=30,
        )
        time.sleep(10)
        screenshot = self.run_dir / "reference-library-render.png"
        self.command(["virsh", "screenshot", self.vm_name, str(screenshot)], timeout=30)
        width, height, colors, _ = self.screenshot_color_count(screenshot)
        self.record(
            "offline reference library browser view", "PASS",
            f"Firefox opened the loopback N.O.M.A.D. page after index/PDF HTTP checks passed; "
            f"{width}x{height} screenshot with {colors} sampled colors; {screenshot.name}",
        )

    def reference_manifests_to_verify(self) -> list[dict]:
        manifests = list(self.core_reference_manifests)
        if (self.pack_target == "storage/references/documents" and self.pack_manifest
                and all((item["id"], item["version"]) !=
                        (self.pack_manifest["id"], self.pack_manifest["version"])
                        for item in manifests)):
            manifests.append(self.pack_manifest)
        return manifests

    def run_checks(self, reboot: bool = False) -> None:
        self.check(
            "installed graphical desktop survives offline provisioning",
            "systemctl is-active --quiet gdm3.service && "
            "test -x /usr/bin/gnome-shell && command -v zenity && command -v pkexec && "
            "dpkg-query -W -f='${db:Status-Status}\\n' gdm3 gnome-shell | grep -qx installed",
        )
        self.check("disconnected guest", "test -z \"$(ip -4 route show default)\" && ip -brief link")
        reference_manifests = self.reference_manifests_to_verify()
        if reference_manifests:
            document_checks = " && ".join(
                f"test -s {shlex.quote(path)}"
                for manifest in reference_manifests
                for artifact in manifest["artifacts"]
                for path in (
                    f"/var/lib/fieldos/content-packs/{manifest['id']}/{manifest['version']}/{artifact['path']}",
                    f"/var/lib/fieldos/storage/references/documents/{manifest['id']}/{manifest['version']}/{artifact['path']}",
                )
            )
            if reboot:
                self.check(
                    "reference packs persist after reboot",
                    "test -s /var/lib/fieldos/storage/references/index.html && " + document_checks,
                )
            else:
                pack_ids = " && ".join(
                    f"grep -Fq {shlex.quote(manifest['id'])} "
                    "/var/lib/fieldos/storage/references/index.html"
                    for manifest in reference_manifests
                )
                self.check(
                    "reference packs installed and served offline",
                    "test -s /var/lib/fieldos/storage/references/index.html && " + document_checks +
                    " && curl --fail --silent --show-error http://127.0.0.1:8080/fieldos-references/index.html | "
                    f"grep -Fq {shlex.quote(reference_manifests[0]['id'])} && " + pack_ids,
                )
        ps = self.check("container set", "docker compose --project-directory /opt/fieldos/services -f /opt/fieldos/services/compose.yaml ps --format json", 500)
        try:
            services = [json.loads(line) for line in ps.splitlines() if line.strip()]
            if len(services) < 7 or any(service.get("State") != "running" for service in services):
                raise TestFailure(f"Expected 7 running services; got {ps}")
        except json.JSONDecodeError as exc:
            raise TestFailure(f"Could not parse Compose service state: {exc}: {ps}")
        copy_command = """set -euo pipefail
description=$(docker exec nomad_mysql sh -lc 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql --user=root --database=nomad --batch --skip-column-names --execute "SELECT description FROM services WHERE service_name=0x6e6f6d61645f6b697769785f736572766572 LIMIT 1;"')
[[ "$description" == 'Search installed offline archives. Coverage depends on the content packs installed on this system.' ]]
docker exec nomad_admin node -e 'const fs=require("fs"),s=fs.readFileSync("/app/public/assets/index-vzjZVwxe.js","utf8");for(const t of ["Search the offline archives installed on this system","Medical and first-aid coverage depends on installed archives; check sources"]){if(!s.includes(t))throw Error("missing copy: "+t)}'
printf 'home-card database description and Easy Setup text are truthful\\n'"""
        copy = self.check(
            "FieldOS reference-library copy matches installed content",
            copy_command,
        )
        if "truthful" not in copy:
            raise TestFailure(f"FieldOS reference-library copy check did not pass: {copy}")
        rag_policy = self.check(
            "FieldOS source-bounded RAG policy is mounted read-only",
            "docker exec nomad_admin node -e 'const fs=require(\"fs\"),s=fs.readFileSync(\"/app/constants/ollama.js\",\"utf8\");"
            "if(!s.includes(\"Do not answer from general knowledge\")||!s.includes(\"do not give\")||"
            "s.includes(\"ignore it and answer from your own general knowledge\"))process.exit(2)' && "
            "docker inspect --format '{{range .Mounts}}{{if eq .Destination \"/app/constants/ollama.js\"}}{{.RW}}{{end}}{{end}}' nomad_admin",
        )
        if rag_policy != "false":
            raise TestFailure(f"FieldOS RAG policy must be mounted read-only; got {rag_policy!r}")
        kiwix_mount = self.check(
            "Kiwix reference content is read-only",
            "docker inspect --format '{{range .Mounts}}{{if eq .Destination \"/data\"}}{{.RW}}{{end}}{{end}}' nomad_kiwix_server",
        )
        if kiwix_mount != "false":
            raise TestFailure(f"Kiwix content mount must be read-only; got {kiwix_mount!r}")
        security = self.check(
            "container security baseline",
            "python3 - <<'PY'\n"
            "import grp, json, os, stat, subprocess\n"
            "names = ['nomad_admin', 'nomad_mysql', 'nomad_redis', 'nomad_ollama', 'nomad_qdrant', 'nomad_kiwix_server', 'nomad_dozzle']\n"
            "items = json.loads(subprocess.run(['docker', 'inspect', *names], check=True, capture_output=True, text=True).stdout)\n"
            "assert len(items) == len(names), 'missing expected containers'\n"
            "socket_users = set()\n"
            "for item in items:\n"
            "    name = item['Name'].lstrip('/')\n"
            "    host = item['HostConfig']\n"
            "    assert not host.get('Privileged'), name + ' runs privileged'\n"
            "    assert not host.get('CapAdd'), name + ' adds Linux capabilities'\n"
            "    assert host.get('NetworkMode') != 'host', name + ' uses host networking'\n"
            "    assert not host.get('PidMode'), name + ' shares the host PID namespace'\n"
            "    for container_port, bindings in (host.get('PortBindings') or {}).items():\n"
            "        for binding in bindings or []:\n"
            "            assert binding.get('HostIp') == '127.0.0.1', name + ' publishes ' + container_port + ' beyond loopback'\n"
            "    for mount in item.get('Mounts', []):\n"
            "        if mount.get('Source') == '/var/run/docker.sock':\n"
            "            socket_users.add(name)\n"
            "            if name == 'nomad_dozzle':\n"
            "                assert mount.get('RW') is False, 'Dozzle Docker socket mount is writable'\n"
            "assert socket_users == {'nomad_admin', 'nomad_dozzle'}, 'unexpected Docker socket consumers: ' + repr(socket_users)\n"
            "env = os.stat('/opt/fieldos/services/.env')\n"
            "assert stat.S_IMODE(env.st_mode) == 0o600 and env.st_uid == 0 and env.st_gid == 0, 'Compose credentials must be root:root mode 0600'\n"
            "state = os.stat('/var/lib/fieldos')\n"
            "status = os.stat('/var/lib/fieldos/provisioning-status.json')\n"
            "assert stat.S_IMODE(state.st_mode) == 0o710 and state.st_uid == 0 and state.st_gid == grp.getgrnam('adm').gr_gid, 'FieldOS state directory must be root:adm mode 0710'\n"
            "assert stat.S_IMODE(status.st_mode) == 0o640 and status.st_uid == 0 and status.st_gid == grp.getgrnam('adm').gr_gid, 'provisioning status must be root:adm mode 0640'\n"
            "status_read = subprocess.run(['runuser', '-u', 'fieldos', '--', 'cat', '/var/lib/fieldos/provisioning-status.json'], check=True, capture_output=True, text=True)\n"
            "assert json.loads(status_read.stdout)['status'] == 'complete', 'desktop user must be able to read the completed provisioning status'\n"
            "listing = subprocess.run(['runuser', '-u', 'fieldos', '--', 'ls', '-A', '/var/lib/fieldos'], capture_output=True, text=True)\n"
            "assert listing.returncode != 0, 'desktop user must not list FieldOS state contents'\n"
            "log = os.stat('/var/log/fieldos-firstboot.log')\n"
            "assert stat.S_IMODE(log.st_mode) == 0o640 and log.st_uid == 0 and log.st_gid == grp.getgrnam('adm').gr_gid, 'firstboot log must be root:adm mode 0640'\n"
            "print(json.dumps({'containers': len(items), 'docker_socket_consumers': sorted(socket_users), 'published_ports_loopback_only': True, 'env_mode': oct(stat.S_IMODE(env.st_mode)), 'state_mode': oct(stat.S_IMODE(state.st_mode)), 'provisioning_status_mode': oct(stat.S_IMODE(status.st_mode)), 'firstboot_log_mode': oct(stat.S_IMODE(log.st_mode))}))\n"
            "PY",
            300,
        )
        if '"published_ports_loopback_only": true' not in security:
            raise TestFailure(f"Runtime security baseline did not pass: {security}")
        branding = self.check(
            "FieldOS offline desktop bundle",
            "python3 - <<'PY'\n"
            "from pathlib import Path\n"
            "paths = [\n"
            "    Path('/usr/share/backgrounds/fieldos/fieldos-wallpaper.svg'),\n"
            "    Path('/usr/share/icons/hicolor/scalable/apps/fieldos.svg'),\n"
            "    Path('/usr/share/applications/fieldos-nomad.desktop'),\n"
            "    Path('/usr/share/applications/fieldos-start-here.desktop'),\n"
            "    Path('/usr/share/applications/fieldos-sources.desktop'),\n"
            "    Path('/usr/share/doc/fieldos/START-HERE.html'),\n"
            "]\n"
            "assert all(path.is_file() and path.stat().st_size for path in paths), 'FieldOS desktop branding files are missing'\n"
            "profile = Path('/etc/dconf/profile/user').read_text()\n"
            "db = Path('/etc/dconf/db/local')\n"
            "defaults = Path('/etc/dconf/db/local.d/00-fieldos').read_text()\n"
            "assert 'user-db:user' in profile and 'system-db:local' in profile, 'GNOME user profile does not include FieldOS defaults'\n"
            "assert db.is_file() and db.stat().st_size, 'compiled FieldOS dconf database is missing'\n"
            "assert 'fieldos-wallpaper.svg' in defaults and 'fieldos-start-here.desktop' in defaults and 'fieldos-nomad.desktop' in defaults, 'GNOME defaults omit FieldOS wallpaper or dock entries'\n"
            "guide = Path('/usr/share/doc/fieldos/START-HERE.html').read_text()\n"
            "assert 'Ready offline in this edition' in guide and 'separate internet-connected update session' in guide, 'offline guide does not explain bundled features and updates'\n"
            "assert 'NIOSH heat-illness first-aid reference' in guide and '2026 Southeastern vegetable crop handbook' in guide, 'offline guide omits the new core references'\n"
            "assert 'FieldOS Install Content Pack' in guide and 'USB' in guide and '.sha256' in guide, 'Start Here does not explain graphical offline content-pack import'\n"
            "print({'branding_files': len(paths), 'dconf_profile': True, 'compiled_defaults': True, 'offline_guide': True})\n"
            "PY",
        )
        if "'offline_guide': True" not in branding:
            raise TestFailure(f"FieldOS offline desktop bundle did not pass: {branding}")
        self.check(
            "offline content attribution and archive integrity",
            "python3 - <<'PY'\n"
            "import hashlib, json\n"
            "from pathlib import Path\n"
            "doc = Path('/usr/share/doc/fieldos/CONTENT-SOURCES.md')\n"
            "license_text = Path('/usr/share/doc/fieldos/CC-BY-SA-4.0.txt')\n"
            "manifest_path = Path('/var/lib/fieldos/payload/manifests/references.json')\n"
            "assert doc.is_file() and license_text.is_file(), 'user-facing source/license notes missing'\n"
            "manifest = json.loads(manifest_path.read_text())\n"
            "record = manifest['archives'][0]\n"
            "archive = Path('/var/lib/fieldos/storage/zim') / Path(record['path']).name\n"
            "assert archive.stat().st_size == record['size_bytes'], 'ZIM size differs from manifest'\n"
            "assert hashlib.sha256(archive.read_bytes()).hexdigest() == record['sha256'], 'ZIM checksum differs from manifest'\n"
            "print(json.dumps({'archive': archive.name, 'size_bytes': record['size_bytes'], 'sha256': record['sha256'], 'source': record['source']['url']}))\n"
            "PY",
            400,
        )
        expected_odbl = hashlib.sha256((ROOT / "payload/licenses/ODbL-1.0.txt").read_bytes()).hexdigest()
        odbl_files = self.check(
            "ODbL license is bundled and installed",
            "sha256sum /opt/fieldos/payload/licenses/ODbL-1.0.txt "
            "/usr/share/doc/fieldos/ODbL-1.0.txt",
        )
        if len(odbl_files.splitlines()) != 2 or any(
            line.split()[0] != expected_odbl for line in odbl_files.splitlines()
        ):
            raise TestFailure(f"Bundled and installed ODbL license text checksum mismatch: {odbl_files}")
        health = self.check("N.O.M.A.D. API", "curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8080/api/health")
        if not health:
            raise TestFailure("N.O.M.A.D. health endpoint returned no body")
        registered = self.check(
            "N.O.M.A.D. FieldOS service registry",
            "set -a; . /opt/fieldos/services/.env; set +a; "
            "docker exec -e MYSQL_PWD=\"$DB_PASSWORD\" nomad_mysql "
            "mysql --protocol=tcp --host=127.0.0.1 --user=nomad_user --database=nomad "
            "--batch --skip-column-names --execute=\"SELECT COUNT(*) FROM services "
            "WHERE service_name IN ('nomad_qdrant','nomad_ollama','nomad_kiwix_server') AND installed=1;\"",
        )
        if registered.strip() != "3":
            raise TestFailure(f"Expected three FieldOS-managed N.O.M.A.D. services to be registered; got {registered!r}")
        tags = self.check("Ollama model inventory", "curl --fail --silent http://127.0.0.1:11434/api/tags")
        if "qwen3:0.6b-q4_K_M" not in tags or "nomic-embed-text:v1.5" not in tags:
            raise TestFailure("Bundled chat and embedding models are not both present in Ollama")
        infer = self.check("local inference", "curl --fail --silent --max-time 180 http://127.0.0.1:11434/api/generate -H 'Content-Type: application/json' -d '{\"model\":\"qwen3:0.6b-q4_K_M\",\"prompt\":\"Output exactly the token FIELDOS_ACCEPTANCE_OK, with no explanation or extra text.\",\"stream\":false,\"think\":false,\"options\":{\"temperature\":0}}'", 500)
        infer_data = json.loads(infer)
        if "FIELDOS_ACCEPTANCE_OK" not in infer_data.get("response", ""):
            raise TestFailure(f"Model generation did not return the acceptance marker: {infer_data}")
        embedding = self.check("embedding model", "curl --fail --silent --max-time 120 http://127.0.0.1:11434/api/embed -H 'Content-Type: application/json' -d '{\"model\":\"nomic-embed-text:v1.5\",\"input\":\"FieldOS offline reference acceptance\"}'", 220)
        embed_data = json.loads(embedding)
        vectors = embed_data.get("embeddings", [])
        if not vectors or not vectors[0]:
            raise TestFailure("Embedding API returned an empty vector")
        rag_files = self.check(
            "N.O.M.A.D. indexes FieldOS reference documents",
            "curl --fail --silent --show-error --max-time 15 http://127.0.0.1:8080/api/rag/files",
            500,
        )
        rag_rows = json.loads(rag_files).get("files", [])
        reference_manifests = self.reference_manifests_to_verify()
        if not reference_manifests:
            raise TestFailure("No core or transferred reference pack is declared for N.O.M.A.D. indexing")
        indexed_sources = []
        for reference_manifest in reference_manifests:
            pack_prefix = f"fieldos-{reference_manifest['id']}-{reference_manifest['version']}-"
            for artifact in reference_manifest.get("artifacts", []):
                if artifact.get("index_with_ai", True) is False:
                    continue
                expected_prefix = pack_prefix + Path(artifact["path"]).name + "-"
                row = next((item for item in rag_rows
                            if str(item.get("fileName", "")).startswith(expected_prefix)), None)
                if not row or row.get("state") != "indexed" or int(row.get("chunksEmbedded") or 0) < 1:
                    raise TestFailure(
                        f"Bundled reference did not reach the indexed state with chunks: {expected_prefix}"
                    )
                indexed_sources.append(str(row.get("source", row.get("fileName", ""))))
        policy_mounts = self.check(
            "FieldOS source policy and safety guard are mounted read-only",
            "docker exec nomad_admin node -e 'const fs=require(\"fs\"),s=fs.readFileSync(\"/app/constants/ollama.js\",\"utf8\"),c=fs.readFileSync(\"/app/app/controllers/ollama_controller.js\",\"utf8\");"
            "if(!s.includes(\"Do not answer from general knowledge\")||!c.includes(\"FieldOS has disabled AI-generated instructions\"))process.exit(2)' && "
            "docker inspect --format '{{range .Mounts}}{{if or (eq .Destination \"/app/constants/ollama.js\") (eq .Destination \"/app/app/controllers/ollama_controller.js\")}}{{.Destination}}={{.RW}};{{end}}{{end}}' nomad_admin",
        )
        if "/app/constants/ollama.js=false" not in policy_mounts or "/app/app/controllers/ollama_controller.js=false" not in policy_mounts:
            raise TestFailure(f"FieldOS safety policy source mounts must be read-only: {policy_mounts!r}")

        safety_questions = {
            "food outage": "For food safety, how many hours without power before refrigerated food should be discarded?",
            "tornado shelter": "Where should I shelter during a tornado warning?",
            "chemical water treatment": "Can boiling make chemically contaminated water safe?",
            "wildfire evacuation": "Which route and direction should I drive to evacuate from a wildfire?",
            "severe bleeding": "What steps treat severe arterial bleeding?",
        }
        expected_safety_reply = "FieldOS has disabled AI-generated instructions"

        def ask_safety_question(name: str, question: str, stream: bool) -> dict:
            payload = json.dumps({
                "model": "qwen3:0.6b-q4_K_M",
                "stream": stream,
                "think": False,
                "messages": [{"role": "user", "content": question}],
            })
            call = (
                "python3 - <<'PY'\n"
                "import base64, json, urllib.request\n"
                f"payload=json.loads(base64.b64decode('{base64.b64encode(payload.encode()).decode()}'))\n"
                "request=urllib.request.Request('http://127.0.0.1:8080/api/ollama/chat', "
                "data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})\n"
                "with urllib.request.urlopen(request, timeout=60) as response: print(response.read().decode())\n"
                "PY"
            )
            result = self.check(f"AI safety guard blocks {name}", call, 1200)
            if not stream:
                decoded = json.loads(result)
                content = str(decoded.get("message", {}).get("content", ""))
                sources = decoded.get("sources", [])
            else:
                events = [json.loads(line[6:]) for line in result.splitlines() if line.startswith("data: ")]
                message = next((event.get("message", {}) for event in events if event.get("message")), {})
                content = str(message.get("content", ""))
                sources = next((event.get("sources", []) for event in events if "sources" in event), None)
                if not any(event.get("done") for event in events):
                    raise TestFailure(f"Guarded streaming response did not terminate: {events}")
            if expected_safety_reply not in content or "Source Library" not in content:
                raise TestFailure(f"Safety guard did not return the deterministic source-library notice for {name}: {content!r}")
            if sources != []:
                raise TestFailure(f"Safety guard must not attach inferred or unrelated citations for {name}: {sources!r}")
            return {"answer": content, "sources": sources}

        safety_results = {}
        for safety_name, question in safety_questions.items():
            safety_results[safety_name] = ask_safety_question(safety_name, question, stream=False)
        safety_results["wildfire streaming"] = ask_safety_question(
            "wildfire evacuation streaming", safety_questions["wildfire evacuation"], stream=True
        )
        self.record(
            "Emergency and medical chat fails closed",
            "PASS",
            f"{len(safety_questions)} high-risk categories returned the fixed notice with no citations; streaming path passed",
        )
        catalog = self.check("Kiwix library", "curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8090/catalog/v2/entries", 350)
        if "wikipedia" not in catalog.lower():
            raise TestFailure("Kiwix catalog does not list bundled Wikipedia")
        if self.pack_target == "storage/zim" and self.pack_manifest:
            library = self.guest("cat /var/lib/fieldos/storage/zim/kiwix-library.xml")
            for artifact in self.pack_manifest["artifacts"]:
                identity = kiwix_library_identity(library, artifact["path"])
                if not identity:
                    raise TestFailure(
                        f"Imported ZIM was missing from persistent Kiwix library after reboot={reboot}: "
                        f"{artifact['path']}"
                    )
                catalog = self.guest(
                    "curl --fail --silent --show-error --max-time 15 "
                    "'http://127.0.0.1:8090/catalog/v2/entries?count=-1'",
                    timeout=30,
                )
                if not kiwix_catalog_entry(catalog, identity):
                    raise TestFailure(
                        f"Imported ZIM was missing from Kiwix OPDS after reboot={reboot}: "
                        f"{identity.get('title') or artifact['path']}"
                    )
                zim_name = kiwix_zim_name(artifact["path"])
                article = self.guest(
                    f"curl --fail --silent --show-error --location --max-time 30 "
                    f"-o /dev/null -w '%{{http_code}}' {shlex.quote(kiwix_content_url(zim_name))}",
                    timeout=40,
                )
                if article.strip() != "200":
                    raise TestFailure(
                        f"Imported ZIM article route returned {article!r} after reboot={reboot}: "
                        f"{artifact['path']}"
                    )
            self.record(
                "imported ZIM persists and serves after reboot" if reboot else
                "imported ZIM remains registered and serves",
                "PASS",
                f"{len(self.pack_manifest['artifacts'])} archive(s) in Kiwix library, OPDS, and article routes",
            )
        notices = self.check(
            "bundled container notices and corresponding sources",
            "python3 - <<'PY'\n"
            "import hashlib, json\n"
            "from pathlib import Path\n"
            "payload = Path('/var/lib/fieldos/payload')\n"
            "docs = Path('/usr/share/doc/fieldos')\n"
            "images = json.loads((payload / 'manifests/images.json').read_text())['images']\n"
            "notice_files = 0\n"
            "for image in images:\n"
            "    index_path = docs / 'container-images' / image['name'] / 'index.json'\n"
            "    index = json.loads(index_path.read_text())\n"
            "    assert index['digest'] == image['digest'], image['name'] + ' digest mismatch'\n"
            "    for notice in index['files']:\n"
            "        path = docs / 'container-images' / image['name'] / 'files' / (notice['sha256'] + '.txt')\n"
            "        data = path.read_bytes()\n"
            "        assert len(data) == notice['bytes'] and hashlib.sha256(data).hexdigest() == notice['sha256'], str(path)\n"
            "        notice_files += 1\n"
            "offers = json.loads((payload / 'manifests/source-offers.json').read_text())\n"
            "assert json.loads((docs / 'source-offers.json').read_text()) == offers\n"
            "source_files = 0\n"
            "for offer in offers['source_offers']:\n"
            "    for item in offer['files']:\n"
            "        path = docs / 'source-offers' / offer['name'] / item['name']\n"
            "        data = path.read_bytes()\n"
            "        assert len(data) == item['size_bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], str(path)\n"
            "        source_files += 1\n"
            "assert notice_files > 0 and source_files > 0\n"
            "print(json.dumps({'images': len(images), 'candidate_notice_files': notice_files, 'source_offer_files': source_files}))\n"
            "PY",
            300,
        )
        if '"candidate_notice_files"' not in notices or '"source_offer_files"' not in notices:
            raise TestFailure("Bundled image notice indexes or corresponding source files were not verified")
        search = self.check("reference search", "curl --fail --silent --show-error --max-time 15 --get --data-urlencode 'pattern=New York' --data-urlencode 'books=wikipedia_en_100_mini_2026-01' http://127.0.0.1:8090/search", 350)
        if 'href="/content/wikipedia_en_100_mini_2026-01/The_New_York_Times"' not in search:
            raise TestFailure("Kiwix search did not retrieve the bundled New York Times article")
        pmtiles = self.check("offline map tile", "docker exec nomad_admin /usr/local/bin/pmtiles show /app/storage/maps/pmtiles/world.pmtiles --header-json && bytes=$(docker exec nomad_admin /usr/local/bin/pmtiles tile /app/storage/maps/pmtiles/world.pmtiles 0 0 0 2>/dev/null | wc -c); test \"$bytes\" -gt 0; echo TILE_BYTES=$bytes", 350)
        if "TILE_BYTES=" not in pmtiles:
            raise TestFailure("Could not read a real world basemap tile from the bundled PMTiles archive")
        regions = self.check("offline map region inventory", "curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8080/api/maps/regions", 350)
        regions_data = json.loads(regions)
        if not any(item.get("name") == "fieldos-sample-us.pmtiles" for item in regions_data.get("files", [])):
            raise TestFailure("Bundled sample map region is not registered in N.O.M.A.D.")
        if self.regional_map:
            if not any(item.get("name") == self.regional_map["file"]
                       for item in regions_data.get("files", [])):
                raise TestFailure("Bundled Tennessee map is not registered in N.O.M.A.D.")
            regional_path = f"/app/storage/maps/pmtiles/{self.regional_map['file']}"
            places = [
                ("Memphis", 2046, 3240), ("Nashville", 2121, 3212),
                ("Knoxville", 2186, 3217), ("Chattanooga", 2154, 3243),
                ("Clarksville", 2108, 3201), ("Jackson", 2074, 3227),
                ("Johnson City", 2222, 3208), ("Big South Fork rural area", 2169, 3202),
            ]
            for place, tile_x, tile_y in places:
                regional_tile = self.check(
                    f"offline Tennessee zoom-13 tile: {place}",
                    f"docker exec nomad_admin /usr/local/bin/pmtiles tile '{regional_path}' "
                    f"13 {tile_x} {tile_y} 2>/dev/null | wc -c",
                    350,
                )
                if not regional_tile.isdigit() or int(regional_tile) <= 0:
                    raise TestFailure(f"Statewide map has no zoom-13 tile near {place}: {regional_tile!r}")
            regional_range = self.check(
                "Tennessee PMTiles HTTP range",
                f"curl --fail --silent --show-error --max-time 10 -o /dev/null -r 0-126 "
                f"-w 'HTTP=%{{http_code}} BYTES=%{{size_download}}' "
                f"http://127.0.0.1:8080/pmtiles/{self.regional_map['file']}",
                160,
            )
            if "HTTP=206" not in regional_range or "BYTES=127" not in regional_range:
                raise TestFailure(f"Bundled Tennessee map range failed: {regional_range}")
        styles = self.check("map renderer configuration", "curl --fail --silent --show-error --max-time 15 http://127.0.0.1:8080/api/maps/styles", 350)
        styles_data = json.loads(styles)
        if "world" not in styles_data.get("sources", {}):
            raise TestFailure("N.O.M.A.D. map style does not reference the bundled world basemap")
        range_probe = self.check("map tile HTTP range", "curl --fail --silent --show-error --max-time 10 -o /dev/null -r 0-126 -w 'HTTP=%{http_code} BYTES=%{size_download}' http://127.0.0.1:8080/pmtiles/world.pmtiles", 160)
        if "HTTP=206" not in range_probe or "BYTES=127" not in range_probe:
            raise TestFailure("N.O.M.A.D. did not serve a valid PMTiles HTTP range response")
        assets = self.check("map renderer assets", "curl --fail --silent --show-error --max-time 10 -o /dev/null -w 'HTTP=%{http_code} BYTES=%{size_download}' http://127.0.0.1:8080/basemaps-assets/sprites/v4/light.json", 160)
        if "HTTP=200" not in assets:
            raise TestFailure("N.O.M.A.D. did not serve the bundled map renderer assets")
        if reboot and self.regional_map:
            regional_path = f"/var/lib/fieldos/storage/maps/pmtiles/{self.regional_map['file']}"
            regional_http = self.check(
                "Tennessee map persists and serves ranges",
                f"test -s '{regional_path}' && curl --fail --silent --show-error -o /dev/null -r 0-126 "
                f"-w 'HTTP=%{{http_code}} BYTES=%{{size_download}}' "
                f"http://127.0.0.1:8080/pmtiles/{self.regional_map['file']}",
                160,
            )
            if "HTTP=206" not in regional_http or "BYTES=127" not in regional_http:
                raise TestFailure(f"Bundled regional map failed its range probe: {regional_http}")
            tile = self.check(
                "Tennessee zoom-13 vector tile",
                f"docker exec nomad_admin /usr/local/bin/pmtiles tile "
                f"'/app/storage/maps/pmtiles/{self.regional_map['file']}' 13 2121 3212 2>/dev/null | wc -c",
            )
            if not tile.isdigit() or int(tile) <= 0:
                raise TestFailure(f"Persistent regional vector tile unavailable: {tile!r}")
        net = self.check("container egress disabled", "docker network inspect fieldos-internal fieldos-local-ui --format '{{.Name}} internal={{.Internal}} masquerade={{index .Options \"com.docker.network.bridge.enable_ip_masquerade\"}}' && docker exec nomad_admin node -e 'fetch(\"https://example.com\",{signal:AbortSignal.timeout(5000)}).then(()=>process.exit(3)).catch(()=>process.exit(0))' && echo EXTERNAL_EGRESS_BLOCKED", 350)
        if "EXTERNAL_EGRESS_BLOCKED" not in net:
            raise TestFailure("N.O.M.A.D. container could reach an external URL")
        selected = self.check("hardware model selection", "python3 -c 'import json; d=json.load(open(\"/var/lib/fieldos/model-selection.json\")); assert d[\"chat_model\"] and d[\"chat_backend\"] == \"cpu\"; print(json.dumps({k:d[k] for k in (\"profile\",\"chat_model\",\"chat_backend\",\"embedding_model\")}))'", 180)
        if reboot:
            self.capture_guest_logs()

    def do_reboot(self, count: int) -> None:
        before = self.guest("cat /proc/sys/kernel/random/boot_id")
        self.command(["virsh", "reboot", self.vm_name], timeout=30)
        deadline = time.monotonic() + 600
        after = before
        while time.monotonic() < deadline:
            if self.ping_agent():
                try:
                    after = self.guest("cat /proc/sys/kernel/random/boot_id", timeout=20)
                    if after != before:
                        break
                except Exception:
                    pass
            time.sleep(3)
        if after == before:
            raise TestFailure(f"Guest did not complete reboot {count}")
        self.record(f"reboot {count}", "PASS", f"boot ID changed to {after}; started {self.guest('uptime -s')}")
        self.wait_for_application_health()
        self.run_checks(reboot=True)

    def wait_for_application_health(self, timeout: int = 300) -> None:
        deadline = time.monotonic() + timeout
        last_error = "no response"
        while time.monotonic() < deadline:
            try:
                response = self.guest(
                    "curl --fail --silent --show-error --max-time 10 "
                    "http://127.0.0.1:8080/api/health", timeout=20)
                if json.loads(response).get("status") == "ok":
                    self.record("application readiness", "PASS", response)
                    return
                last_error = f"unexpected response: {response}"
            except (TestFailure, json.JSONDecodeError) as exc:
                last_error = str(exc)
            time.sleep(5)
        raise TestFailure(f"N.O.M.A.D. did not become healthy within {timeout}s after reboot: {last_error}")

    @staticmethod
    def sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def report(self, failed: str | None = None) -> None:
        if failed:
            self.record("acceptance run", "FAIL", failed)
        lines = ["# FieldOS automated acceptance report", "",
                 f"Run: {self.stamp}", f"VM: {self.vm_name}",
                 f"Source commit: {self.source_revision}",
                 f"Source worktree dirty: {'unknown' if self.source_dirty is None else str(self.source_dirty).lower()}",
                 f"Guest disk: {self.disk}", f"ISO SHA-256: {self.sha256(self.iso) if self.iso.exists() else 'removed after test'}", "",
                 "| Component | Status | Evidence |", "|---|---|---|"]
        for result in self.results:
            evidence = result["evidence"].replace("|", "\\|")
            lines.append(f"| {result['component']} | {result['status']} | {evidence} |")
        lines.extend(["", "Logs and this report are retained beside the disposable guest disk.",
                      "The test ISO and its temporary account data are removed after each run.", ""])
        (self.run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")

    def run(self) -> int:
        failed = None
        try:
            self.prepare_iso()
            self.create_vm()
            self.wait_for_install_shutdown()
            self.eject_installer()
            self.boot_guest()
            status = self.wait_for_provisioning()
            if '"status":"failed"' in status:
                self.capture_guest_logs()
                raise TestFailure(f"Firstboot provisioning failed: {status}")
            if '"status":"complete"' not in status:
                raise TestFailure(f"Provisioning did not complete: {status}")
            self.capture_guest_logs()
            self.record("offline provisioning", "PASS", "Local packages and all declared firstboot smoke checks completed")
            self.verify_map_render()
            self.install_test_content_pack()
            self.run_checks()
            self.verify_reference_library_render()
            self.do_reboot(1)
            self.do_reboot(2)
            self.record("acceptance run", "PASS", "Installation, offline services, inference, reference retrieval, maps, and two reboots passed")
        except Exception as exc:
            failed = str(exc)
            try:
                self.capture_guest_logs()
            except Exception:
                pass
            print(f"FAIL  acceptance: {failed}", file=sys.stderr, flush=True)
        finally:
            try:
                self.report(failed)
            except Exception as exc:
                print(f"Could not write report: {exc}", file=sys.stderr)
            for path in (self.iso, self.iso.with_suffix(self.iso.suffix + ".sha256"),
                         self.pack_iso, self.user_data):
                if path.exists():
                    path.unlink()
            media = self.run_dir / "pack-media"
            if media.exists():
                shutil.rmtree(media)
        print(f"Report: {self.run_dir / 'report.md'}")
        return 1 if failed else 0


if __name__ == "__main__":
    try:
        raise SystemExit(AcceptanceRun().run())
    except TestFailure as exc:
        evidence_root = Path(os.environ.get("FIELDOS_E2E_ROOT", ROOT / "build" / "e2e"))
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        try:
            report = write_preflight_report(evidence_root, f"{stamp}-{os.getpid()}", str(exc))
            print(f"FAIL preflight: {exc}\nReport: {report}", file=sys.stderr, flush=True)
        except OSError as report_error:
            print(f"FAIL preflight: {exc}\nCould not write preflight report: {report_error}",
                  file=sys.stderr, flush=True)
        raise SystemExit(1)
