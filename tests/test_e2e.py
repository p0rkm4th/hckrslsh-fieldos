#!/usr/bin/env python3
"""Install and accept FieldOS in a fresh, network-disconnected libvirt VM."""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
import secrets
import string
import struct
import subprocess
import sys
import time
import zlib
from pathlib import Path
from shutil import disk_usage


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UBUNTU_ISO = Path("/mnt/shared/ISO Library/ubuntu-26.04.1-desktop-amd64.iso")


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


class AcceptanceRun:
    def __init__(self) -> None:
        self.stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        evidence_root = Path(os.environ.get("FIELDOS_E2E_ROOT", ROOT / "build" / "e2e"))
        evidence_root.parent.mkdir(parents=True, exist_ok=True)
        if disk_usage(evidence_root.parent).free < 50 * 1024**3:
            raise TestFailure(f"Need at least 50 GiB free for isolated ISO and VM evidence on {evidence_root.parent}")
        work_root = Path(os.environ.get("FIELDOS_WORK_ROOT", evidence_root))
        work_root.parent.mkdir(parents=True, exist_ok=True)
        if disk_usage(work_root.parent).free < 8 * 1024**3:
            raise TestFailure(f"Need at least 8 GiB free for temporary ISO build work on {work_root.parent}")
        self.run_dir = evidence_root / f"{self.stamp}-{os.getpid()}"
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.vm_name = f"fieldos-e2e-{self.stamp.lower()}"
        self.disk = self.run_dir / "guest.qcow2"
        self.iso = self.run_dir / "test.iso"
        self.user_data = self.run_dir / "user-data"
        self.results: list[dict[str, str]] = []
        self.agent_ready = False
        self.temporary_password = ""
        self.memory_mib = int(os.environ.get("FIELDOS_TEST_MEMORY_MIB", "12288"))
        if self.memory_mib < 8192:
            raise TestFailure("The full offline acceptance requires at least 8192 MiB guest RAM")
        self.source_revision, self.source_dirty = git_source_state()

    def command(self, args: list[str], *, env: dict[str, str] | None = None,
                check: bool = True, timeout: int = 120) -> subprocess.CompletedProcess[str]:
        proc = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, env=env, timeout=timeout)
        if check and proc.returncode:
            raise TestFailure(f"Command failed ({proc.returncode}): {' '.join(args)}\n{proc.stdout[-5000:]}")
        return proc

    def prepare_iso(self) -> None:
        ubuntu_iso = Path(os.environ.get("UBUNTU_ISO", DEFAULT_UBUNTU_ISO))
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
    - mkdir -p /target/usr/share/applications
    - mkdir -p /target/usr/share/doc/fieldos
    - mkdir -p /target/home/fieldos/.config
    - mkdir -p /target/home/fieldos/.config/gnome-initial-setup
    - touch /target/home/fieldos/.config/gnome-initial-setup-done
    - touch /target/home/fieldos/.config/gnome-initial-setup/upgrade-26.04-done
    - chown -R 1000:1000 /target/home/fieldos/.config
    - cp -a /cdrom/fieldos/. /target/opt/fieldos/
    - cp /cdrom/fieldos/installer/provisioning/fieldos.desktop /target/usr/share/applications/fieldos-nomad.desktop
    - cp /cdrom/fieldos/installer/provisioning/fieldos-sources.desktop /target/usr/share/applications/fieldos-sources.desktop
    - curtin in-target --target=/target -- chmod 0755 /opt/fieldos/installer/provisioning/firstboot.sh
    - cp /target/opt/fieldos/installer/provisioning/fieldos-firstboot.service /target/etc/systemd/system/fieldos-firstboot.service
    - curtin in-target --target=/target -- systemctl enable fieldos-firstboot.service
    - systemd-run --unit=fieldos-e2e-poweroff --on-active=90s /usr/bin/systemctl poweroff
""", encoding="utf-8")
        os.chmod(self.user_data, 0o600)
        build_env = os.environ.copy()
        build_env.update({
            "FIELDOS_AUTOINSTALL_FILE": str(self.user_data),
            "FIELDOS_OUTPUT_PATH": str(self.iso),
            "FIELDOS_WORK_ROOT": os.environ.get("FIELDOS_WORK_ROOT", str(self.run_dir)),
            "FIELDOS_TEST_AUTOBOOT": "1",
        })
        self.command(["bash", str(ROOT / "build/build-iso.sh"), "test", str(ubuntu_iso)],
                     env=build_env, timeout=1800)
        self.record("test ISO build", "PASS", f"{self.iso.name}: {self.sha256(self.iso)}")

    def create_vm(self) -> None:
        if self.disk.exists():
            raise TestFailure(f"Refusing to overwrite VM disk: {self.disk}")
        self.command(["qemu-img", "create", "-f", "qcow2", str(self.disk), "80G"])
        self.command([
            "virt-install", "--name", self.vm_name, "--memory", str(self.memory_mib), "--vcpus", "6",
            "--disk", f"path={self.disk},format=qcow2,bus=virtio",
            "--cdrom", str(self.iso), "--network", "none", "--boot", "uefi",
            "--osinfo", "ubuntu26.04",
            "--graphics", "vnc,listen=127.0.0.1", "--video", "virtio",
            "--channel", "unix,target.type=virtio,target.name=org.qemu.guest_agent.0",
            "--noautoconsole", "--wait", "0",
        ], timeout=180)
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
        for target in root.findall("./devices/disk[@device='cdrom']/target"):
            dev = target.get("dev")
            if dev:
                self.command(["virsh", "change-media", self.vm_name, dev,
                              "--eject", "--config"], check=False)

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

    def check(self, name: str, command: str, evidence_limit: int = 300) -> str:
        output = self.guest(command)
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
        keymap.update({"/": "KEY_SLASH", ".": "KEY_DOT"})
        for char in text:
            if char == ":":
                self.send_key("KEY_LEFTSHIFT", "KEY_SEMICOLON")
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
        launch = (
            f"uid={uid}; runtime=/run/user/$uid; "
            "wayland=$(find \"$runtime\" -maxdepth 1 -type s -name 'wayland-*' -printf '%f\\n' | head -n 1); "
            "test -n \"$wayland\" && test -S \"$runtime/$wayland\"; "
            "runuser -u fieldos -- env \"XDG_RUNTIME_DIR=$runtime\" "
            "\"DBUS_SESSION_BUS_ADDRESS=unix:path=$runtime/bus\" \"WAYLAND_DISPLAY=$wayland\" "
            "GDK_BACKEND=wayland /usr/bin/firefox --new-window http://127.0.0.1:8080/maps "
            ">/tmp/fieldos-firefox.log 2>&1 </dev/null &"
        )
        self.guest(launch, timeout=30)
        self.guest(
            f"for i in $(seq 1 40); do pgrep -u {uid} -f '/snap/firefox/.*/firefox' >/dev/null "
            "&& exit 0; sleep 1; done; cat /tmp/fieldos-firefox.log; exit 1", timeout=50)
        time.sleep(20)
        screenshot = self.run_dir / "map-render.png"
        deadline = time.monotonic() + 120
        width = height = colors = water_pixels = 0
        while time.monotonic() < deadline:
            self.command(["virsh", "screenshot", self.vm_name, str(screenshot)], timeout=30)
            width, height, colors, water_pixels = self.screenshot_color_count(screenshot)
            if water_pixels >= 5000:
                break
            time.sleep(5)
        if water_pixels < 5000 or colors < 64:
            raise TestFailure(
                f"Map viewport did not render PMTiles water tiles: {water_pixels} water pixels, "
                f"{colors} sampled colors in {width}x{height} screenshot"
            )
        self.record("offline map rendering", "PASS",
                    f"Firefox rendered PMTiles tiles in {width}x{height} VNC screenshot; "
                    f"{water_pixels} sampled water pixels, {colors} colors; {screenshot.name}")

    def run_checks(self, reboot: bool = False) -> None:
        self.check("disconnected guest", "test -z \"$(ip -4 route show default)\" && ip -brief link")
        ps = self.check("container set", "docker compose --project-directory /opt/fieldos/services -f /opt/fieldos/services/compose.yaml ps --format json", 500)
        try:
            services = [json.loads(line) for line in ps.splitlines() if line.strip()]
            if len(services) < 7 or any(service.get("State") != "running" for service in services):
                raise TestFailure(f"Expected 7 running services; got {ps}")
        except json.JSONDecodeError as exc:
            raise TestFailure(f"Could not parse Compose service state: {exc}: {ps}")
        kiwix_mount = self.check(
            "Kiwix reference content is read-only",
            "docker inspect --format '{{range .Mounts}}{{if eq .Destination \"/data\"}}{{.RW}}{{end}}{{end}}' nomad_kiwix_server",
        )
        if kiwix_mount != "false":
            raise TestFailure(f"Kiwix content mount must be read-only; got {kiwix_mount!r}")
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
        catalog = self.check("Kiwix library", "curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8090/catalog/v2/entries", 350)
        if "wikipedia" not in catalog.lower():
            raise TestFailure("Kiwix catalog does not list bundled Wikipedia")
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
            self.run_checks()
            self.verify_map_render()
            self.do_reboot(1)
            self.do_reboot(2)
            self.record("acceptance run", "PASS", "Installation, offline services, inference, retrieval, map tile, and two reboots passed")
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
            for path in (self.iso, self.iso.with_suffix(self.iso.suffix + ".sha256"), self.user_data):
                if path.exists():
                    path.unlink()
        print(f"Report: {self.run_dir / 'report.md'}")
        return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(AcceptanceRun().run())
