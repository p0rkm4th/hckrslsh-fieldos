#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=${FIELDOS_ROOT:-/opt/fieldos}
IMAGE='ghcr.io/crosstalk-solutions/project-nomad:v1.35.1@sha256:1445a3eaba19801ce27435b7edc57fce74d9543601808d719b432e3bc7468ea1'
PATCH_DIR=/var/lib/fieldos/patches
OUTPUT="$PATCH_DIR/nomad-ollama.js"
TEMP=$(mktemp /run/fieldos-nomad-ollama.XXXXXX)
TEMP_CONTROLLER=$(mktemp /run/fieldos-nomad-controller.XXXXXX)
CONTAINER="fieldos-rag-patch-$$"
cleanup() {
  docker rm "$CONTAINER" >/dev/null 2>&1 || true
  rm -f -- "$TEMP"
  rm -f -- "$TEMP_CONTROLLER"
}
trap cleanup EXIT

install -d -o root -g root -m 0755 "$PATCH_DIR"
docker create --name "$CONTAINER" --network none --entrypoint /bin/true "$IMAGE" >/dev/null
docker cp "$CONTAINER:/app/constants/ollama.js" "$TEMP" >/dev/null
python3 "$ROOT/installer/provisioning/patch_nomad_rag_policy.py" "$TEMP" "$OUTPUT"
docker cp "$CONTAINER:/app/app/controllers/ollama_controller.js" "$TEMP_CONTROLLER" >/dev/null
python3 "$ROOT/installer/provisioning/patch_nomad_rag_policy.py" \
  "$TEMP_CONTROLLER" "$PATCH_DIR/nomad-ollama-controller.js" --controller
chown root:root "$OUTPUT"
chmod 0644 "$OUTPUT"
chown root:root "$PATCH_DIR/nomad-ollama-controller.js"
chmod 0644 "$PATCH_DIR/nomad-ollama-controller.js"
grep -Fq 'Do not answer from general knowledge' "$OUTPUT"
grep -Fq 'do not give' "$OUTPUT"
grep -Fq 'FieldOS has disabled AI-generated instructions' "$PATCH_DIR/nomad-ollama-controller.js"
docker run --rm --network none \
  -v "$PATCH_DIR:/fieldos-patches:ro" \
  --entrypoint node "$IMAGE" \
  --check /fieldos-patches/nomad-ollama.js
docker run --rm --network none \
  -v "$PATCH_DIR:/fieldos-patches:ro" \
  --entrypoint node "$IMAGE" \
  --check /fieldos-patches/nomad-ollama-controller.js
