#!/usr/bin/env python3
"""Build the guarded N.O.M.A.D. initial chat-model preference statement."""

import json
import sys
from pathlib import Path


def model_reference(manifest_path: Path, model_id: str) -> str:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for model in manifest.get("chat_models", []):
        if model.get("id") == model_id:
            reference = model.get("ollama_ref")
            if isinstance(reference, str) and reference:
                return reference
            break
    raise ValueError(f"Selected model ID is missing from the chat-model manifest: {model_id}")


def seed_statement(reference: str) -> str:
    """Insert the validated default only if N.O.M.A.D. has no saved choice."""
    if not reference:
        raise ValueError("Model reference must not be empty")
    key_hex = "636861742e6c6173744d6f64656c"  # chat.lastModel
    value_hex = reference.encode("utf-8").hex()
    return (
        "INSERT INTO kv_store (`key`, `value`, created_at, updated_at) "
        f"VALUES (CONVERT(0x{key_hex} USING utf8mb4), "
        f"CONVERT(0x{value_hex} USING utf8mb4), NOW(), NOW()) "
        "ON DUPLICATE KEY UPDATE `value` = "
        "IF(`value` IS NULL OR `value` = '', VALUES(`value`), `value`); "
        f"SELECT `value` FROM kv_store WHERE `key`=CONVERT(0x{key_hex} USING utf8mb4);"
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: nomad_initial_model.py MANIFEST MODEL_ID")
    try:
        print(seed_statement(model_reference(Path(sys.argv[1]), sys.argv[2])))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
