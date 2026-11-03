#!/usr/bin/env python3
"""Select a resource profile and bundled models using local JSON inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PROFILE_BANDS = ((8, "minimal"), (16, "lightweight"), (32, "standard"), (64, "accelerated"))


def profile_for(memory_gib: float) -> str:
    for threshold, profile in PROFILE_BANDS:
        if memory_gib < threshold:
            return profile
    return "high_performance"


def usable_vram(hardware: dict, backend: str | None = None) -> float:
    vendors = {"cuda": {"nvidia"}, "rocm": {"amd"}}
    compatible = [gpu for gpu in hardware.get("gpus", [])
                  if (backend is None or gpu.get("driver_available"))
                  and (backend not in vendors or gpu.get("vendor") in vendors[backend])]
    if backend == "vulkan":
        values = (gpu.get("vulkan_memory_budget_gib") or gpu.get("vram_gib", 0) for gpu in compatible)
    elif backend is None:
        values = (max(float(gpu.get("vram_gib") or 0),
                      float(gpu.get("vulkan_memory_budget_gib") or 0)) for gpu in compatible)
    else:
        values = (gpu.get("vram_gib", 0) for gpu in compatible)
    return max((float(value or 0) for value in values), default=0.0)


def select(hardware: dict, manifest: dict, available_ids: set[str] | None = None,
           validated_backends: set[str] | None = None, manual_model: str | None = None,
           available_embedding_ids: set[str] | None = None) -> dict:
    ram = float(hardware.get("memory_gib") or 0)
    reserve = float(manifest.get("system_memory_reserve_gib", 4))
    usable_ram = max(0.0, ram - reserve)
    vram = usable_vram(hardware)
    validated_backends = validated_backends or {"cpu"}
    if available_ids is None:
        available_ids = {
            model["id"] for model in manifest.get("chat_models", []) if model.get("bundled_in_test_iso")
        }
    if available_embedding_ids is None:
        available_embedding_ids = {
            model["id"] for model in manifest.get("embedding_models", []) if model.get("bundled_in_test_iso")
        }

    candidates = []
    for model in manifest.get("chat_models", []):
        if model["id"] not in available_ids:
            continue
        if manual_model and model["id"] != manual_model:
            continue
        if model.get("license") not in {"Apache-2.0", "MIT", "BSD-3-Clause", "CC0-1.0"}:
            continue
        needs_ram = float(model.get("ram_gib", 0))
        needs_vram = float(model.get("vram_gib", 0))
        # A GPU is used only when the backend is both present and explicitly validated.
        gpu_backend = next((backend for backend in ("cuda", "rocm", "vulkan")
                            if backend in validated_backends and backend in model.get("backends", [])
                            and any(gpu.get("driver_available") and
                                    (backend == "vulkan" or
                                     gpu.get("vendor") == {"cuda": "nvidia", "rocm": "amd"}.get(backend))
                                    for gpu in hardware.get("gpus", []))), None)
        fits_cpu = "cpu" in model.get("backends", []) and usable_ram >= needs_ram
        backend_vram = usable_vram(hardware, gpu_backend) if gpu_backend else 0.0
        fits_gpu = gpu_backend is not None and backend_vram >= needs_vram and usable_ram >= min(needs_ram, 1.0)
        if fits_cpu or fits_gpu:
            candidates.append((int(model.get("quality_priority", 0)), model, gpu_backend if fits_gpu else "cpu"))
    candidates.sort(key=lambda item: (item[0], item[1]["id"]), reverse=True)

    embedding_candidates = [model for model in manifest.get("embedding_models", [])
                            if model["id"] in available_embedding_ids and
                            model.get("license") in {"Apache-2.0", "MIT", "BSD-3-Clause", "CC0-1.0"}]
    embedding = embedding_candidates[0] if embedding_candidates and usable_ram >= float(embedding_candidates[0].get("ram_gib", 0)) else None
    result = {
        "profile": profile_for(ram),
        "memory_gib": ram,
        "usable_memory_gib": round(usable_ram, 2),
        "gpu_memory_gib": vram,
        "chat_model": candidates[0][1]["id"] if candidates else None,
        "chat_backend": candidates[0][2] if candidates else None,
        "embedding_model": embedding["id"] if embedding else None,
        "fallback_model_ids": [entry[1]["id"] for entry in candidates[1:]],
        "manual_override": manual_model is not None,
        "reason": "highest-priority bundled model fitting available memory and a validated backend" if candidates else "no bundled model fits; reference-only mode",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hardware", type=Path, required=True, help="Hardware JSON from detect.py")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "models/manifest.json")
    parser.add_argument("--available", type=Path, help="JSON array of model IDs present in local payload")
    parser.add_argument("--validated-backends", default="cpu", help="Comma-separated runtime-validated backend names")
    parser.add_argument("--model", help="Optional model ID override; still checked for fit and payload presence")
    args = parser.parse_args()
    hardware = json.loads(args.hardware.read_text())
    manifest = json.loads(args.manifest.read_text())
    available_record = json.loads(args.available.read_text()) if args.available else None
    if isinstance(available_record, dict):
        available = set(available_record.get("chat", []))
        available_embeddings = set(available_record.get("embedding", []))
    else:
        available = set(available_record) if available_record is not None else None
        available_embeddings = None
    backends = {value.strip() for value in args.validated_backends.split(",") if value.strip()}
    print(json.dumps(select(hardware, manifest, available, backends, args.model, available_embeddings), indent=2))


if __name__ == "__main__":
    main()
