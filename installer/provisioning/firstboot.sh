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
trap '[[ -z "${env_tmp:-}" ]] || rm -f -- "$env_tmp"' EXIT

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

echo "Installing offline content source and license notes for local users..."
content_docs=/usr/share/doc/fieldos
install -d -m 0755 "$content_docs"
cp -an "$ROOT/payload/licenses/CONTENT-SOURCES.md" "$content_docs/CONTENT-SOURCES.md"
cp -an "$ROOT/payload/licenses/CC-BY-SA-4.0.txt" "$content_docs/CC-BY-SA-4.0.txt"
cp -an "$ROOT/payload/licenses/ODbL-1.0.txt" "$content_docs/ODbL-1.0.txt"
if [[ -d "$PAYLOAD/licenses" ]]; then
  cp -an "$PAYLOAD/licenses/." "$content_docs/"
fi
chmod -R a+rX "$content_docs"

echo "Installing bundled packages without network access..."
python3 "$ROOT/installer/provisioning/build_local_apt_index.py" "$PAYLOAD/debs" "$PAYLOAD/Packages"
printf 'deb [trusted=yes] file:%s ./\n' "$PAYLOAD" > /etc/apt/sources.list.d/fieldos-offline.list
apt_offline=(
  -o APT::Sandbox::User=root
  -o Dir::Etc::sourcelist=/etc/apt/sources.list.d/fieldos-offline.list
  -o Dir::Etc::sourceparts=-
  -o APT::Get::List-Cleanup=0
)
apt-get "${apt_offline[@]}" update
apt-get "${apt_offline[@]}" --yes --no-install-recommends install \
  docker.io docker-compose-v2 curl zstd qemu-guest-agent
rm -f /etc/apt/sources.list.d/fieldos-offline.list
systemctl enable --now qemu-guest-agent.service

root_lv=$(findmnt --noheadings --output SOURCE /)
if [[ "$root_lv" == /dev/mapper/* ]] && command -v lvextend >/dev/null && command -v vgs >/dev/null; then
  root_vg=$(lvs --noheadings --options vg_name "$root_lv" | xargs)
  if [[ -n "$root_vg" ]]; then
    vg_free_bytes=$(vgs --noheadings --units b --nosuffix --options vg_free "$root_vg" | tr -d ' ' | cut -d. -f1)
    if [[ "$vg_free_bytes" =~ ^[0-9]+$ ]] && (( vg_free_bytes > 0 )); then
      echo "Extending the FieldOS root filesystem into unused installer-created volume-group space..."
      lvextend --resizefs --extents +100%FREE "$root_lv"
    fi
  fi
fi

install -d -m 0755 "$STATE/storage/zim"
install -d -m 0750 "$STATE/storage/maps/pmtiles" "$STATE/storage/maps/basemaps-assets" "$STATE/storage/ollama" "$STATE/mysql" "$STATE/redis" "$STATE/qdrant"

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
  zim_name=$(basename "$PAYLOAD/content/zim/wikipedia_en_100_mini_2026-01.zim")
  if [[ -s "$library" ]] && python3 -c 'import sys,xml.etree.ElementTree as ET; ET.parse(sys.argv[1])' "$library"; then
    if ! grep -Fq "$zim_name" "$library"; then
      docker run --rm --network none --user 0:0 \
        -v "$STATE/storage/zim:/data" \
        --entrypoint kiwix-manage \
        ghcr.io/kiwix/kiwix-serve:3.8.1@sha256:a80b64909744930d79be14542048d1fbf11f1fdd9ffe6712ef8c9cd3aa1740dd \
        /data/kiwix-library.xml add "/data/$zim_name"
    fi
  else
    if [[ -e "$library" ]]; then
      mv "$library" "$library.invalid.$(date +%s)"
    fi
    docker run --rm --network none --user 0:0 \
      -v "$STATE/storage/zim:/data" \
      --entrypoint kiwix-manage \
      ghcr.io/kiwix/kiwix-serve:3.8.1@sha256:a80b64909744930d79be14542048d1fbf11f1fdd9ffe6712ef8c9cd3aa1740dd \
      /data/kiwix-library.xml.new add "/data/$zim_name"
    mv "$library.new" "$library"
  fi
  chmod 0644 "$library"
fi

echo "Generating per-install credentials..."
cd /opt/fieldos/services
if [[ ! -s .env ]]; then
  env_tmp=$(mktemp .env.XXXXXX)
  {
    printf 'APP_KEY=%s\n' "$(openssl rand -hex 32)"
    printf 'DB_PASSWORD=%s\n' "$(openssl rand -hex 32)"
    printf 'DB_ROOT_PASSWORD=%s\n' "$(openssl rand -hex 32)"
  } > "$env_tmp"
  chmod 0600 "$env_tmp"
  mv "$env_tmp" .env
  env_tmp=
fi
chown root:root .env
chmod 0600 .env

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
model_args=()
if [[ -s /etc/fieldos/model-override ]]; then
  read -r model_override < /etc/fieldos/model-override
  if [[ -n "$model_override" ]]; then
    model_args+=(--model "$model_override")
    echo "Validating operator model override: $model_override"
  fi
fi
python3 "$ROOT/hardware/select_profile.py" \
  --hardware "$STATE/hardware.json" \
  --available "$PAYLOAD/model-ids.json" \
  --validated-backends cpu "${model_args[@]}" > "$STATE/model-selection-candidate.json"
model_ref=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("chat_model") or "")' "$STATE/model-selection-candidate.json")
if [[ -z "$model_ref" ]]; then
  echo "No usable bundled chat model was selected." >&2
  exit 1
fi
mapfile -t model_candidates < <(python3 - "$STATE/model-selection-candidate.json" <<'PY'
import json, sys
selection = json.load(open(sys.argv[1]))
print(selection["chat_model"])
print("\n".join(selection.get("fallback_model_ids", [])))
PY
)
selected_id=""
for candidate_id in "${model_candidates[@]}"; do
  [[ -n "$candidate_id" ]] || continue
  ollama_ref=$(python3 - "$ROOT/models/manifest.json" "$candidate_id" <<'PY'
import json, sys
manifest = json.load(open(sys.argv[1]))
print(next(model["ollama_ref"] for model in manifest["chat_models"] if model["id"] == sys.argv[2]))
PY
  )
  smoke_output="$STATE/inference-smoke-$candidate_id.json"
  echo "Validating bundled model $candidate_id with a local generation request..."
  if curl --fail --silent --show-error --max-time 180 http://127.0.0.1:11434/api/generate \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"$ollama_ref\",\"prompt\":\"Reply with FIELDOS_OK\",\"stream\":false,\"think\":false}" \
    > "$smoke_output" && grep -q FIELDOS_OK "$smoke_output"; then
    selected_id="$candidate_id"
    break
  fi
  echo "Model $candidate_id failed its inference smoke check; trying the next compatible bundled model." >&2
done
if [[ -z "$selected_id" ]]; then
  echo "No compatible bundled chat model passed the inference smoke check." >&2
  exit 1
fi
python3 - "$STATE/model-selection-candidate.json" "$STATE/model-selection.json" "$selected_id" <<'PY'
import json, sys
from pathlib import Path
selection = json.loads(Path(sys.argv[1]).read_text())
selected = sys.argv[3]
selection["chat_model"] = selected
selection["fallback_model_ids"] = [item for item in selection.get("fallback_model_ids", []) if item != selected]
selection["validation"] = "local chat generation passed"
Path(sys.argv[2]).write_text(json.dumps(selection, indent=2) + "\n")
PY
rm -f "$STATE/model-selection-candidate.json"
curl --fail --silent http://127.0.0.1:11434/api/embed \
  -H 'Content-Type: application/json' \
  -d '{"model":"nomic-embed-text:v1.5","input":"offline embedding smoke test"}' \
  > "$STATE/embedding-smoke.json"
grep -q 'embeddings' "$STATE/embedding-smoke.json"

printf '{"status":"complete","completed_at":"%s"}\n' "$(date --iso-8601=seconds)" > "$STATE/provisioning-status.json"
echo "FieldOS services are available at http://localhost:8080."
