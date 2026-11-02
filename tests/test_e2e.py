#!/usr/bin/env python3
"""Install and accept FieldOS in a fresh, network-disconnected libvirt VM."""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UBUNTU_ISO = Path("/mnt/shared/ISO Library/ubuntu-26.04.1-desktop-amd64.iso")


class TestFailure(RuntimeError):
    pass


class AcceptanceRun:
    def __init__(self) -> None:
        self.stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.run_dir = ROOT / "build" / "e2e" / f"{self.stamp}-{os.getpid()}"
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.vm_name = f"fieldos-e2e-{self.stamp.lower()}"
        self.disk = self.run_dir / "guest.qcow2"
        self.iso = self.run_dir / "test.iso"
        self.user_data = self.run_dir / "user-data"
        self.results: list[dict[str, str]] = []
        self.agent_ready = False

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
        temporary_password = secrets.token_urlsafe(24)
        hash_proc = subprocess.run(["openssl", "passwd", "-6", "-stdin"],
                                   input=temporary_password, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        del temporary_password
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
  storage:
    layout:
      name: lvm
  shutdown: poweroff
  late-commands:
    - mkdir -p /target/opt/fieldos
    - mkdir -p /target/usr/share/applications
    - cp -a /cdrom/fieldos/. /target/opt/fieldos/
    - cp /cdrom/fieldos/installer/provisioning/fieldos.desktop /target/usr/share/applications/fieldos-nomad.desktop
    - curtin in-target --target=/target -- chmod 0755 /opt/fieldos/installer/provisioning/firstboot.sh
    - cp /target/opt/fieldos/installer/provisioning/fieldos-firstboot.service /target/etc/systemd/system/fieldos-firstboot.service
    - curtin in-target --target=/target -- systemctl enable fieldos-firstboot.service
""", encoding="utf-8")
        os.chmod(self.user_data, 0o600)
        build_env = os.environ.copy()
        build_env.update({
            "FIELDOS_AUTOINSTALL_FILE": str(self.user_data),
            "FIELDOS_OUTPUT_PATH": str(self.iso),
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
            "virt-install", "--name", self.vm_name, "--memory", "12288", "--vcpus", "6",
            "--disk", f"path={self.disk},format=qcow2,bus=virtio",
            "--cdrom", str(self.iso), "--network", "none", "--boot", "uefi",
            "--osinfo", "ubuntu26.04",
            "--graphics", "none", "--channel", "unix,target.type=virtio,target.name=org.qemu.guest_agent.0",
            "--noautoconsole", "--wait", "0",
        ], timeout=180)
        self.record("disposable VM", "PASS", f"{self.vm_name}; 80 GiB qcow2; no virtual NIC")

    def wait_for_install_shutdown(self, timeout: int = 2400) -> None:
        deadline = time.monotonic() + timeout
        log_file = self.run_dir / "install-state.log"
        while time.monotonic() < deadline:
            state = self.command(["virsh", "domstate", self.vm_name], check=False, timeout=15).stdout.strip()
            if state.lower() in {"shut off", "shutdown"}:
                self.record("Ubuntu unattended installation", "PASS", "Installer powered off after disk install")
                return
            if state.lower() == "running" and self.ping_agent(tries=1):
                self.agent_ready = True
                try:
                    text = self.guest("cat /var/log/installer/curtin-install.log 2>/dev/null | tail -20", timeout=20)
                    log_file.write_text(text, encoding="utf-8")
                except Exception:
                    pass
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
                self.command(["virsh", "change-media", self.vm_name, dev, "--eject", "--config"], check=False)

    def boot_guest(self) -> None:
        self.eject_installer()
        self.command(["virsh", "start", self.vm_name])
        if not self.wait_for_agent(timeout=900):
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

    def run_checks(self, reboot: bool = False) -> None:
        self.check("provisioning status", "grep -q '" + '"status":"complete"' + "' /var/lib/fieldos/provisioning-status.json && cat /var/lib/fieldos/provisioning-status.json")
        self.check("disconnected guest", "test -z \"$(ip -4 route show default)\" && ip -brief link")
        ps = self.check("container set", "docker compose --project-directory /opt/fieldos/services -f /opt/fieldos/services/compose.yaml ps --format json", 500)
        try:
            services = [json.loads(line) for line in ps.splitlines() if line.strip()]
            if len(services) < 7 or any(service.get("State") != "running" for service in services):
                raise TestFailure(f"Expected 7 running services; got {ps}")
        except json.JSONDecodeError as exc:
            raise TestFailure(f"Could not parse Compose service state: {exc}: {ps}")
        health = self.check("N.O.M.A.D. API", "curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8080/api/health")
        if not health:
            raise TestFailure("N.O.M.A.D. health endpoint returned no body")
        tags = self.check("Ollama model inventory", "curl --fail --silent http://127.0.0.1:11434/api/tags")
        if "qwen3:0.6b-q4_K_M" not in tags or "nomic-embed-text:v1.5" not in tags:
            raise TestFailure("Bundled chat and embedding models are not both present in Ollama")
        infer = self.check("local inference", "curl --fail --silent --max-time 180 http://127.0.0.1:11434/api/generate -H 'Content-Type: application/json' -d '{\"model\":\"qwen3:0.6b-q4_K_M\",\"prompt\":\"Reply exactly FIELDOS_ACCEPTANCE_OK\",\"stream\":false,\"think\":false}'", 500)
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
        search = self.check("reference search", "curl --fail --silent --show-error --max-time 15 --get --data-urlencode 'pattern=New York' --data-urlencode 'books=wikipedia_en_100_mini_2026-01' http://127.0.0.1:8090/search", 350)
        if 'href="/content/wikipedia_en_100_mini_2026-01/The_New_York_Times"' not in search:
            raise TestFailure("Kiwix search did not retrieve the bundled New York Times article")
        pmtiles = self.check("offline map tile", "docker exec nomad_admin /usr/local/bin/pmtiles show /app/storage/maps/pmtiles/world.pmtiles --header-json && bytes=$(docker exec nomad_admin /usr/local/bin/pmtiles tile /app/storage/maps/pmtiles/world.pmtiles 0 0 0 2>/dev/null | wc -c); test \"$bytes\" -gt 0; echo TILE_BYTES=$bytes", 350)
        if "TILE_BYTES=" not in pmtiles:
            raise TestFailure("Could not read a real world basemap tile from the bundled PMTiles archive")
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
        selected = self.check("hardware model selection", "python3 -c 'import json; d=json.load(open(\"/var/lib/fieldos/model-selection.json\")); assert d[\"chat_model\"] and d[\"chat_backend\"] == \"cpu\"; print(json.dumps({k:d[k] for k in (\"profile\",\"chat_model\",\"chat_backend\",\"embedding_model\")}))", 180)
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
        self.run_checks(reboot=True)

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
