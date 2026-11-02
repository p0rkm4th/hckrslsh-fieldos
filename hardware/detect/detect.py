#!/usr/bin/env python3
"""Read local hardware facts without changing host state."""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path


def read_text(path: str | Path) -> str:
    try:
        return Path(path).read_text(errors="replace").strip()
    except OSError:
        return ""


def run(args: list[str]) -> str:
    if not shutil.which(args[0]):
        return ""
    try:
        proc = subprocess.run(args, check=False, text=True, capture_output=True, timeout=8)
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def memory_gib() -> float:
    match = re.search(r"^MemTotal:\s+(\d+)\s+kB", read_text("/proc/meminfo"), re.M)
    return round(int(match.group(1)) / 1024 / 1024, 2) if match else 0.0


def cpu_facts() -> dict:
    model = ""
    flags: set[str] = set()
    for line in read_text("/proc/cpuinfo").splitlines():
        if not model and (line.startswith("model name") or line.startswith("Hardware")):
            model = line.split(":", 1)[-1].strip()
        if line.startswith("flags") or line.startswith("Features"):
            flags.update(line.split(":", 1)[-1].split())
    return {
        "architecture": platform.machine(),
        "model": model,
        "logical_cores": os.cpu_count() or 1,
        "instruction_sets": sorted(flags & {"avx", "avx2", "avx512f", "fma", "sse4_2", "neon"}),
    }


def gpu_facts() -> list[dict]:
    gpus = []
    nvidia = run(["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"])
    for row in nvidia.splitlines():
        fields = [field.strip() for field in row.split(",")]
        if len(fields) == 3:
            try:
                total = round(float(fields[1]) / 1024, 2)
                available = round(float(fields[2]) / 1024, 2)
            except ValueError:
                total = available = 0
            gpus.append({"vendor": "nvidia", "vendor_id": "0x10de", "model": fields[0],
                         "vram_gib": available, "vram_total_gib": total,
                         "cuda": True, "driver_available": True, "runtime_validated": False})
    for device in sorted(Path("/sys/class/drm").glob("card[0-9]*/device")):
        vendor = read_text(device / "vendor")
        model = read_text(device / "device")
        if not vendor or (vendor.lower() == "0x10de" and gpus):
            continue
        total_raw = read_text(device / "mem_info_vram_total")
        used_raw = read_text(device / "mem_info_vram_used")
        try:
            total_bytes = int(total_raw)
            used_bytes = int(used_raw) if used_raw else 0
            total = round(total_bytes / 1024**3, 2)
            available = round(max(0, total_bytes - used_bytes) / 1024**3, 2)
        except ValueError:
            total = available = 0
        vendor_name = {"0x10de": "nvidia", "0x1002": "amd", "0x8086": "intel"}.get(vendor.lower(), "unknown")
        try:
            driver = (device / "driver").resolve(strict=True).name
        except OSError:
            driver = ""
        gpus.append({"vendor": vendor_name, "vendor_id": vendor, "device_id": model,
                     "model": model, "driver": driver or None, "driver_available": bool(driver),
                     "vram_gib": available, "vram_total_gib": total,
                     "cuda": False, "runtime_validated": False})
    return gpus


def storage_facts() -> list[dict]:
    raw = run(["lsblk", "--json", "-b", "-d", "-o", "NAME,SIZE,ROTA,TRAN,MODEL,TYPE"])
    try:
        return json.loads(raw).get("blockdevices", []) if raw else []
    except json.JSONDecodeError:
        return []


def battery_facts() -> list[dict]:
    results = []
    for battery in sorted(Path("/sys/class/power_supply").glob("BAT*")):
        state = read_text(battery / "status")
        capacity = read_text(battery / "capacity")
        results.append({"name": battery.name, "status": state or None, "capacity_percent": int(capacity) if capacity.isdigit() else None})
    return results


def gps_present() -> bool:
    return any(Path(path).exists() for path in ("/dev/ttyACM0", "/dev/ttyUSB0", "/dev/gnss0"))


def detect() -> dict:
    return {
        "cpu": cpu_facts(),
        "memory_gib": memory_gib(),
        "gpus": gpu_facts(),
        "storage": storage_facts(),
        "batteries": battery_facts(),
        "gps_device_present": gps_present(),
    }


if __name__ == "__main__":
    print(json.dumps(detect(), indent=2, sort_keys=True))
