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


def available_memory_gib() -> float:
    match = re.search(r"^MemAvailable:\s+(\d+)\s+kB", read_text("/proc/meminfo"), re.M)
    return round(int(match.group(1)) / 1024 / 1024, 2) if match else 0.0


def cpu_facts() -> dict:
    model = ""
    flags: set[str] = set()
    physical_cores: set[tuple[str, str]] = set()
    physical_id = core_id = None
    for line in read_text("/proc/cpuinfo").splitlines():
        if not line.strip():
            if physical_id is not None and core_id is not None:
                physical_cores.add((physical_id, core_id))
            physical_id = core_id = None
            continue
        if not model and (line.startswith("model name") or line.startswith("Hardware")):
            model = line.split(":", 1)[-1].strip()
        if line.startswith("flags") or line.startswith("Features"):
            flags.update(line.split(":", 1)[-1].split())
        if line.startswith("physical id"):
            physical_id = line.split(":", 1)[-1].strip()
        elif line.startswith("core id"):
            core_id = line.split(":", 1)[-1].strip()
    if physical_id is not None and core_id is not None:
        physical_cores.add((physical_id, core_id))
    return {
        "architecture": platform.machine(),
        "model": model,
        "logical_cores": os.cpu_count() or 1,
        "physical_cores": len(physical_cores) or None,
        "instruction_sets": sorted(flags & {"avx", "avx2", "avx512f", "fma", "sse4_2", "neon"}),
    }


def vulkan_device_memory(text: str) -> list[dict]:
    """Read per-device local-memory budgets from optional vulkaninfo output."""
    devices = []
    sections = re.split(r"(?m)^GPU\d+:\s*$", text)
    for section in sections[1:]:
        vendor = re.search(r"(?m)^\s*vendorID\s*=\s*(0x[0-9a-fA-F]+)", section)
        device = re.search(r"(?m)^\s*deviceID\s*=\s*(0x[0-9a-fA-F]+)", section)
        name = re.search(r"(?m)^\s*deviceName\s*=\s*(.+?)\s*$", section)
        kind = re.search(r"(?m)^\s*deviceType\s*=\s*(PHYSICAL_DEVICE_TYPE_[A-Z_]+)", section)
        driver = re.search(r"(?m)^\s*driverName\s*=\s*(.+?)\s*$", section)
        if not vendor or (kind and kind.group(1) == "PHYSICAL_DEVICE_TYPE_CPU"):
            continue
        memory = section.split("VkPhysicalDeviceMemoryProperties:", 1)
        if len(memory) != 2:
            continue
        heaps = re.split(r"memoryHeaps\[\d+\]:", memory[1])[1:]
        budgets = []
        usages = []
        for heap in heaps:
            if "MEMORY_HEAP_DEVICE_LOCAL_BIT" not in heap:
                continue
            budget = re.search(r"(?m)^\s*budget\s*=\s*(\d+)", heap)
            usage = re.search(r"(?m)^\s*usage\s*=\s*(\d+)", heap)
            if budget and int(budget.group(1)) > 0:
                budgets.append(int(budget.group(1)))
                usages.append(int(usage.group(1)) if usage else 0)
        if not budgets:
            continue
        total_budget = sum(budgets)
        devices.append({
            "vendor_id": vendor.group(1).lower(),
            "device_id": device.group(1).lower() if device else None,
            "model": name.group(1) if name else None,
            "device_type": kind.group(1).removeprefix("PHYSICAL_DEVICE_TYPE_").lower() if kind else None,
            "driver": driver.group(1) if driver else None,
            "memory_budget_gib": round(total_budget / 1024**3, 2),
            "memory_usage_gib": round(sum(usages) / 1024**3, 2),
        })
    return devices


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

    for device in vulkan_device_memory(run(["vulkaninfo"])):
        vendor_id = device["vendor_id"]
        matches = [gpu for gpu in gpus
                   if gpu.get("vendor_id", "").lower() == vendor_id and
                   (not gpu.get("device_id") or not device["device_id"] or
                    gpu["device_id"].lower() == device["device_id"])]
        if matches:
            gpu = matches[0]
            if not gpu.get("model") or re.fullmatch(r"0x[0-9a-fA-F]+", gpu["model"]):
                gpu["model"] = device["model"]
        else:
            vendor_name = {"0x10de": "nvidia", "0x1002": "amd", "0x8086": "intel"}.get(vendor_id, "unknown")
            gpu = {"vendor": vendor_name, "vendor_id": vendor_id,
                   "device_id": device["device_id"], "model": device["model"],
                   "vram_gib": 0.0, "vram_total_gib": 0.0, "cuda": False,
                   "driver_available": bool(device["driver"]), "runtime_validated": False}
            gpus.append(gpu)
        gpu["vulkan_device_type"] = device["device_type"]
        gpu["vulkan_driver"] = device["driver"]
        gpu["vulkan_memory_budget_gib"] = device["memory_budget_gib"]
        gpu["vulkan_memory_usage_gib"] = device["memory_usage_gib"]
        gpu["driver_available"] = gpu.get("driver_available", False) or bool(device["driver"])
    return gpus


def storage_facts() -> list[dict]:
    raw = run(["lsblk", "--json", "-b", "-d", "-o", "NAME,SIZE,ROTA,TRAN,MODEL,TYPE"])
    try:
        devices = json.loads(raw).get("blockdevices", []) if raw else []
        return [device for device in devices
                if device.get("type") == "disk"
                and not str(device.get("name", "")).startswith(("loop", "zram", "ram"))]
    except json.JSONDecodeError:
        return []


def root_storage_facts() -> dict:
    try:
        usage = shutil.disk_usage("/")
    except OSError:
        return {"total_bytes": 0, "used_bytes": 0, "available_bytes": 0}
    return {"total_bytes": usage.total, "used_bytes": usage.used, "available_bytes": usage.free}


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
        "available_memory_gib": available_memory_gib(),
        "gpus": gpu_facts(),
        "storage": storage_facts(),
        "root_filesystem": root_storage_facts(),
        "batteries": battery_facts(),
        "gps_device_present": gps_present(),
    }


if __name__ == "__main__":
    print(json.dumps(detect(), indent=2, sort_keys=True))
