#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT=/opt/fieldos
STATE=/var/lib/fieldos
PAYLOAD_ARCHIVE="$ROOT/payload/offline-payload.tar.zst"
PAYLOAD="$STATE/payload"
LOG=/var/log/fieldos-firstboot.log
exec > >(tee -a "$LOG") 2>&1

fail() {
  local rc=$?
  echo "FieldOS provisioning failed (exit $rc). Logs: $LOG"
  install -d -m 0755 "$STATE"
  printf '{"status":"failed","exit_code":%s,"log":"%s"}\n' "$rc" "$LOG" > "$STATE/provisioning-status.json"
  exit "$rc"
}
trap fail ERR

if [[ -e "$STATE/provisioning-status.json" ]] && grep -q '"status":"complete"' "$STATE/provisioning-status.json"; then
  echo "FieldOS provisioning is already complete."
  exit 0
fi

exec 9>/run/lock/fieldos-firstboot.lock
flock -n 9 || { echo "Another FieldOS provisioning process is active."; exit 0; }

echo "Checking offline payload checksums..."
test -s "$PAYLOAD_ARCHIVE"
cd "$(dirname "$PAYLOAD_ARCHIVE")"
sha256sum -c offline-payload.tar.zst.sha256

echo "Installing bundled packages without network access..."
echo "Extracting bundled runtime and content..."
install -d -m 0750 "$STATE"
install -d -m 0750 "$PAYLOAD"
zstd --decompress --stdout "$PAYLOAD_ARCHIVE" | tar --extract --directory="$PAYLOAD" --no-same-owner

echo "Installing bundled packages without network access..."
if compgen -G "$PAYLOAD/debs/*.deb" >/dev/null; then
  apt-get --no-download --yes install "$PAYLOAD"/debs/*.deb
fi

install -d -m 0750 "$STATE/storage/zim" "$STATE/storage/maps/pmtiles" "$STATE/storage/maps/basemaps-assets" "$STATE/storage/ollama" "$STATE/mysql" "$STATE/redis" "$STATE/qdrant"

if [[ -d "$PAYLOAD/content/zim" ]]; then
  cp -an "$PAYLOAD/content/zim/." "$STATE/storage/zim/"
fi
if [[ -d "$PAYLOAD/content/maps/pmtiles" ]]; then
  cp -an "$PAYLOAD/content/maps/pmtiles/." "$STATE/storage/maps/pmtiles/"
fi
if [[ -d "$PAYLOAD/content/maps/basemaps-assets" ]]; then
  cp -an "$PAYLOAD/content/maps/basemaps-assets/." "$STATE/storage/maps/basemaps-assets/"
fi
if [[ -f "$PAYLOAD/content/maps/nomad-base-styles.json" ]]; then
  install -m 0644 "$PAYLOAD/content/maps/nomad-base-styles.json" "$STATE/storage/maps/nomad-base-styles.json"
fi
if [[ -d "$PAYLOAD/content/ollama" ]]; then
  cp -an "$PAYLOAD/content/ollama/." "$STATE/storage/ollama/"
fi

echo "Loading pinned container images..."
for archive in "$PAYLOAD"/oci/*.tar; do
  [[ -e "$archive" ]] || continue
  docker load --input "$archive"
done

if [[ -f "$PAYLOAD/content/zim/wikipedia_en_100_mini_2026-01.zim" ]]; then
  library="$STATE/storage/zim/kiwix-library.xml"
  [[ -e "$library" ]] || printf '<?xml version="1.0" encoding="UTF-8"?>\n<library version="20110515"></library>\n' > "$library"
  docker run --rm --network none \
    -v "$STATE/storage/zim:/data" \
    --entrypoint kiwix-manage \
    ghcr.io/kiwix/kiwix-serve:3.8.1@sha256:a80b64909744930d79be14542048d1fbf11f1fdd9ffe6712ef8c9cd3aa1740dd \
    /data/kiwix-library.xml add /data/wikipedia_en_100_mini_2026-01.zim
fi

echo "Generating per-install credentials..."
cd /opt/fieldos/services
if [[ ! -s .env ]]; then
  {
    printf 'APP_KEY=%s\n' "$(openssl rand -hex 32)"
    printf 'DB_PASSWORD=%s\n' "$(openssl rand -hex 32)"
    printf 'DB_ROOT_PASSWORD=%s\n' "$(openssl rand -hex 32)"
  } > .env
  chmod 0600 .env
fi

echo "Starting the local N.O.M.A.D. service set without pulling images..."
docker compose --project-directory /opt/fieldos/services -f compose.yaml up --detach --pull never

echo "Waiting for N.O.M.A.D. and local inference endpoints..."
for attempt in $(seq 1 90); do
  if curl --fail --silent http://127.0.0.1:8080/api/health >/dev/null; then break; fi
  sleep 2
done
curl --fail --silent http://127.0.0.1:8080/api/health >/dev/null
curl --fail --silent http://127.0.0.1:11434/api/version >/dev/null
curl --fail --silent http://127.0.0.1:8090 >/dev/null

echo "Selecting a model from the local payload and detected hardware..."
python3 "$ROOT/hardware/detect/detect.py" > "$STATE/hardware.json"
python3 "$ROOT/hardware/select_profile.py" \
  --hardware "$STATE/hardware.json" \
  --available "$PAYLOAD/model-ids.json" \
  --validated-backends cpu > "$STATE/model-selection.json"
model_ref=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("chat_model") or "")' "$STATE/model-selection.json")
if [[ -z "$model_ref" ]]; then
  echo "No usable bundled chat model was selected." >&2
  exit 1
fi
if [[ -n "$model_ref" ]]; then
  ollama_ref=$(python3 - "$ROOT/models/manifest.json" "$model_ref" <<'PY'
import json, sys
manifest = json.load(open(sys.argv[1]))
print(next(model["ollama_ref"] for model in manifest["chat_models"] if model["id"] == sys.argv[2]))
PY
)
  curl --fail --silent http://127.0.0.1:11434/api/generate \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"$ollama_ref\",\"prompt\":\"Reply with FIELDOS_OK\",\"stream\":false,\"think\":false}" \
    > "$STATE/inference-smoke.json"
  grep -q FIELDOS_OK "$STATE/inference-smoke.json"
fi
curl --fail --silent http://127.0.0.1:11434/api/embed \
  -H 'Content-Type: application/json' \
  -d '{"model":"nomic-embed-text:v1.5","input":"offline embedding smoke test"}' \
  > "$STATE/embedding-smoke.json"
grep -q 'embeddings' "$STATE/embedding-smoke.json"

printf '{"status":"complete","completed_at":"%s"}\n' "$(date --iso-8601=seconds)" > "$STATE/provisioning-status.json"
echo "FieldOS services are available at http://localhost:8080."
