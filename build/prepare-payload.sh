#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
OUT=${FIELDOS_PAYLOAD_ROOT:-"$ROOT/build/payload"}
ARCHIVE="$OUT/offline-payload.tar.zst"
[[ ! -e "$ARCHIVE" ]] || { echo "Payload already exists; move it aside explicitly before rebuilding: $ARCHIVE" >&2; exit 1; }
mkdir -p "$OUT"
WORK_ROOT=${FIELDOS_WORK_ROOT:-"$ROOT/build"}
mkdir -p "$WORK_ROOT"
require_free_space() {
  local path="$1" available_kib
  available_kib=$(df -Pk "$path" | awk 'NR == 2 { print $4 }')
  if [[ -z "$available_kib" ]] || (( available_kib < 50 * 1024 * 1024 )); then
    echo "Need at least 50 GiB free for payload staging and archive output on $path" >&2
    exit 1
  fi
}
require_free_space "$OUT"
require_free_space "$WORK_ROOT"
STAGE=$(mktemp -d "$WORK_ROOT/work-payload.XXXXXX")
trap 'docker rm -f "$MODEL_CONTAINER" >/dev/null 2>&1 || true; rm -rf "$STAGE"' EXIT
MODEL_CONTAINER="fieldos-model-seed-$$"

for tool in docker git curl python3 zstd sha256sum tar; do
  command -v "$tool" >/dev/null || { echo "Missing payload build tool: $tool" >&2; exit 2; }
done

mkdir -p "$STAGE"/{debs,oci,content/zim,content/maps/pmtiles,content/maps/basemaps-assets,content/ollama,licenses,manifests}
install -m 0644 "$ROOT/payload/manifests/content-pack.schema.json" \
  "$STAGE/manifests/content-pack.schema.json"
python3 "$ROOT/build/build_content_packs.py" \
  --core-only --catalog "$ROOT/payload/manifests/content-packs.json" --output-root "$STAGE/core-pack-build"
if [[ -d "$STAGE/core-pack-build/content-packs" ]]; then
  mv "$STAGE/core-pack-build/content-packs" "$STAGE/content-packs"
  rmdir "$STAGE/core-pack-build"
fi
mkdir -p "$STAGE/content-packs"

echo "Fetching checksum-pinned corresponding source for identified AGPL components..."
python3 - "$ROOT/payload/manifests/source-offers.json" "$STAGE/licenses/source-offers" <<'PY'
import hashlib, json, subprocess, sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text())
root = Path(sys.argv[2])
for offer in manifest["source_offers"]:
    target_dir = root / offer["name"]
    target_dir.mkdir(parents=True, exist_ok=True)
    for item in offer["files"]:
        target = target_dir / item["name"]
        temporary = target.with_name(target.name + ".download")
        subprocess.run([
            "curl", "--fail", "--location", "--silent", "--show-error",
            "--connect-timeout", "15", "--max-time", "180",
            "--retry", "3", "--retry-all-errors", "--retry-delay", "2",
            "--happy-eyeballs-timeout-ms", "1500", "--output", str(temporary),
            item["url"],
        ], check=True)
        data = temporary.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != item["size_bytes"] or digest != item["sha256"]:
            raise SystemExit(f"Source archive integrity mismatch: {target}")
        temporary.replace(target)
PY

python3 - "$ROOT/payload/manifests/images.json" <<'PY' > "$STAGE/manifests/images.tsv"
import json, sys
for image in json.load(open(sys.argv[1]))["images"]:
    print(image["name"], image["ref"], image["digest"], sep="\t")
PY

echo "Downloading the pinned Ubuntu package closure in an Ubuntu 26.04 environment..."
docker run --rm --platform linux/amd64 \
  -v "$STAGE/debs:/out" \
  ubuntu:26.04@sha256:6a06111c3b0a8600feadb270aec771dc239bf407b25625f93f44ab00e11f4d3c \
  bash -euxc 'apt-get update; apt-get install --download-only --yes --no-install-recommends docker.io docker-compose-v2 curl zstd qemu-guest-agent vulkan-tools zenity; cp /var/cache/apt/archives/*.deb /out/'

while IFS=$'\t' read -r name ref digest; do
  [[ -n "$ref" ]] || continue
  echo "Pulling $ref@$digest"
  docker pull --platform linux/amd64 "$ref@$digest"
  docker image tag "$ref@$digest" "$ref"
  docker image save --output "$STAGE/oci/${name}.tar" "$ref"
done < "$STAGE/manifests/images.tsv"

echo "Collecting candidate license and notice files from pinned container layers..."
python3 "$ROOT/build/collect_image_notices.py" \
  --manifest "$ROOT/payload/manifests/images.json" \
  --archive-dir "$STAGE/oci" \
  --output-dir "$STAGE/licenses/container-images"

NOMAD_IMAGE=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["extractor"]["image"])' \
  "$ROOT/payload/manifests/maps.json")
EXPECTED_PMTILES_VERSION=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["extractor"]["version_output"])' \
  "$ROOT/payload/manifests/maps.json")
docker run --rm --network none --entrypoint /usr/local/bin/pmtiles \
  "$NOMAD_IMAGE" version > "$STAGE/manifests/pmtiles-version.txt"
ACTUAL_PMTILES_VERSION=$(cat "$STAGE/manifests/pmtiles-version.txt")
[[ "$ACTUAL_PMTILES_VERSION" == "$EXPECTED_PMTILES_VERSION" ]] || {
  echo "Pinned PMTiles extractor version mismatch: expected '$EXPECTED_PMTILES_VERSION', got '$ACTUAL_PMTILES_VERSION'" >&2
  exit 1
}

echo "Fetching source-pinned Project N.O.M.A.D. reference and map styling..."
git clone --depth 1 --branch v1.35.1 https://github.com/Crosstalk-Solutions/project-nomad.git "$STAGE/project-nomad"
git clone https://github.com/Crosstalk-Solutions/project-nomad-maps.git "$STAGE/project-nomad-maps"
git -C "$STAGE/project-nomad-maps" checkout --detach 5b444051914fbf4960be2e64c0fb11f507db7efd
EXPECTED_NOMAD_COMMIT=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["archives"][0]["source"]["commit"])' \
  "$ROOT/payload/manifests/references.json")
ACTUAL_NOMAD_COMMIT=$(git -C "$STAGE/project-nomad" rev-parse HEAD)
[[ "$ACTUAL_NOMAD_COMMIT" == "$EXPECTED_NOMAD_COMMIT" ]] || {
  echo "Project N.O.M.A.D. source commit mismatch: expected $EXPECTED_NOMAD_COMMIT, got $ACTUAL_NOMAD_COMMIT" >&2
  exit 1
}
cp "$STAGE/project-nomad/install/wikipedia_en_100_mini_2026-01.zim" "$STAGE/content/zim/"
python3 - "$ROOT/payload/manifests/references.json" "$STAGE/content/zim/wikipedia_en_100_mini_2026-01.zim" \
  > "$STAGE/manifests/references.json" <<'PY'
import hashlib, json, sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text())
artifact = Path(sys.argv[2])
record = manifest["archives"][0]
digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
size = artifact.stat().st_size
if digest != record["sha256"] or size != record["size_bytes"]:
    raise SystemExit(
        f"Reference archive mismatch: expected {record['size_bytes']} bytes/{record['sha256']}, "
        f"got {size} bytes/{digest}"
    )
print(json.dumps(manifest, indent=2) + "\n")
PY
cp "$STAGE/project-nomad-maps/nomad-base-styles.json" "$STAGE/content/maps/"
"$PYTHON" "$ROOT/build/patch_map_attribution.py" "$STAGE/content/maps/nomad-base-styles.json"
cp -a "$STAGE/project-nomad-maps/basemaps-assets/." "$STAGE/content/maps/basemaps-assets/"
mkdir -p "$STAGE/licenses/project-nomad" "$STAGE/licenses/project-nomad-maps"
cp "$STAGE/project-nomad/LICENSE" "$STAGE/licenses/project-nomad/"
cp "$STAGE/project-nomad-maps/README.md" "$STAGE/licenses/project-nomad-maps/UPSTREAM-README.md"
cat > "$STAGE/licenses/project-nomad-maps/LICENSE.txt" <<'EOF'
Project N.O.M.A.D. Maps v1.35.1 source documents the repository default as MIT,
with fonts separately under SIL OFL and sprites derived from MIT-licensed
tangrams/icons. The map data is a Protomaps Basemap Produced Work derived from
OpenStreetMap and subject to ODbL 1.0. See UPSTREAM-README.md and the separate
font license for the upstream notices and attribution.
EOF
cp "$STAGE/project-nomad-maps/basemaps-assets/fonts/OFL.txt" "$STAGE/licenses/project-nomad-maps/"
cp "$ROOT/payload/licenses/TANGRAMS-ICONS-MIT.txt" "$STAGE/licenses/project-nomad-maps/"
printf '%s\n' \
  'Wikipedia content is © its contributors and licensed under the applicable Creative Commons Attribution-ShareAlike terms.' \
  'The miniature ZIM comes from Project N.O.M.A.D. v1.35.1 source: install/wikipedia_en_100_mini_2026-01.zim.' \
  'Display attribution and the applicable license in the installed information library.' \
  > "$STAGE/licenses/wikipedia-zim-attribution.txt"
cp "$ROOT/payload/licenses/CONTENT-SOURCES.md" "$STAGE/licenses/"
cp "$ROOT/payload/licenses/CC-BY-SA-4.0.txt" "$STAGE/licenses/"
cp "$ROOT/payload/licenses/ODbL-1.0.txt" "$STAGE/licenses/"

echo "Resolving the current Protomaps build and extracting a low-zoom offline world map..."
MAPS_METADATA_URL=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["source_build"]["metadata_url"])' \
  "$ROOT/payload/manifests/maps.json")
curl --fail --silent --show-error "$MAPS_METADATA_URL" -o "$STAGE/manifests/protomaps-builds.json"
python3 - "$STAGE/manifests/protomaps-builds.json" "$ROOT/payload/manifests/maps.json" > "$STAGE/manifests/protomaps-build.json" <<'PY'
import json, sys
items = json.load(open(sys.argv[1]))
manifest = json.load(open(sys.argv[2]))
expected = manifest["source_build"]
matches = [item for item in items if item.get("key") == expected["key"]]
if len(matches) != 1:
    raise SystemExit(f"Pinned Protomaps source build not found: {expected['key']}")
actual = matches[0]
for field in ("version", "size", "md5sum", "b3sum", "uploaded"):
    if actual.get(field) != expected[field]:
        raise SystemExit(f"Pinned Protomaps metadata changed for {field}: {actual.get(field)!r}")
expected_url = f"https://build.protomaps.com/{expected['key']}"
if expected.get("url") != expected_url:
    raise SystemExit(f"Pinned Protomaps source URL does not match build key: {expected.get('url')!r}")
actual["url"] = expected["url"]
actual["metadata_url"] = expected["metadata_url"]
print(json.dumps(actual, indent=2))
PY
MAP_SOURCE_URL=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["url"])' \
  "$STAGE/manifests/protomaps-build.json")
docker run --rm --network bridge \
  -v "$STAGE/content/maps/pmtiles:/maps" \
  --entrypoint /usr/local/bin/pmtiles \
  "$NOMAD_IMAGE" \
  extract "$MAP_SOURCE_URL" /maps/world.pmtiles --bbox=-180,-85,180,85 --maxzoom=5
docker run --rm --network none -v "$STAGE/content/maps/pmtiles:/maps" \
  --entrypoint /usr/local/bin/pmtiles "$NOMAD_IMAGE" show /maps/world.pmtiles \
  > "$STAGE/manifests/world-map-metadata.txt"
while IFS=$'\t' read -r region_id region_file region_bbox minzoom maxzoom source expected_bytes expected_sha256; do
  [[ -n "$region_id" ]] || continue
  echo "Extracting bundled map region $region_id ($region_file), zoom $minzoom-$maxzoom..."
  if [[ "$source" == "world" ]]; then
    MAP_SOURCE=/maps/world.pmtiles
    MAP_NETWORK=none
  elif [[ "$source" == "pinned-build" ]]; then
    MAP_SOURCE="$MAP_SOURCE_URL"
    MAP_NETWORK=bridge
  else
    echo "Unknown map source mode for $region_id: $source" >&2
    exit 1
  fi
  docker run --rm --network "$MAP_NETWORK" \
    -v "$STAGE/content/maps/pmtiles:/maps" \
    --entrypoint /usr/local/bin/pmtiles \
    "$NOMAD_IMAGE" \
    extract "$MAP_SOURCE" "/maps/$region_file" \
    --bbox="$region_bbox" --minzoom="$minzoom" --maxzoom="$maxzoom"
  docker run --rm --network none -v "$STAGE/content/maps/pmtiles:/maps" \
    --entrypoint /usr/local/bin/pmtiles "$NOMAD_IMAGE" show "/maps/$region_file" \
    > "$STAGE/manifests/$(basename "$region_file" .pmtiles)-metadata.txt"
done < <(python3 - "$ROOT/payload/manifests/maps.json" <<'PY'
import json, sys
for region in json.load(open(sys.argv[1]))["regions"]:
    print("\t".join(str(region.get(key, "")) for key in (
        "id", "file", "bbox", "minzoom", "maxzoom", "source",
        "expected_size_bytes", "expected_sha256")))
PY
)
python3 - "$STAGE/content/maps/pmtiles" \
  "$ROOT/payload/manifests/maps.json" "$STAGE/manifests/protomaps-build.json" \
  > "$STAGE/manifests/map-payload.json" <<'PY'
import hashlib
import json
import pathlib
import sys

map_root, manifest, build_manifest = map(pathlib.Path, sys.argv[1:])
record = json.loads(manifest.read_text())
build = json.loads(build_manifest.read_text())
source_url = record["source_build"]["url"]
extractor = record["extractor"]
def file_record(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"file": path.name, "bytes": path.stat().st_size, "sha256": digest.hexdigest()}

regions = []
for item in record["regions"]:
    result = file_record(map_root / item["file"])
    if item.get("expected_size_bytes") and result["bytes"] != item["expected_size_bytes"]:
        raise SystemExit(f"Map size mismatch for {item['id']}: {result['bytes']}")
    if item.get("expected_sha256") and result["sha256"] != item["expected_sha256"]:
        raise SystemExit(f"Map SHA-256 mismatch for {item['id']}: {result['sha256']}")
    source_archive = "world.pmtiles" if item["source"] == "world" else build["key"]
    input_source = "/maps/world.pmtiles" if item["source"] == "world" else source_url
    command = ["pmtiles", "extract", input_source, f"/maps/{item['file']}",
               f"--bbox={item['bbox']}", f"--minzoom={item['minzoom']}",
               f"--maxzoom={item['maxzoom']}"]
    regions.append({
        **item,
        "source_archive": source_archive,
        "source_url": input_source,
        "extraction_command": command,
        "derived_file": result,
        "license": record["license"],
        "attribution": record["attribution"],
    })

print(json.dumps({
    "schema_version": 1,
    "source_build": build,
    "extractor": extractor,
    "world_extraction_command": [
        "pmtiles", "extract", source_url, "/maps/world.pmtiles",
        "--bbox=-180,-85,180,85", "--maxzoom=5",
    ],
    "license": record["license"],
    "attribution": record["attribution"],
    "regions": regions,
}, indent=2))
PY
cat > "$STAGE/licenses/protomaps-odbl-attribution.txt" <<'EOF'
The world.pmtiles dataset is a low-zoom extract of the Protomaps Basemap, a Produced Work derived from OpenStreetMap data. The fieldos-sample-us.pmtiles file is an extract from that bundled world archive. The tennessee-20261102-z13.pmtiles file is an extract of the pinned Protomaps build for the Tennessee statewide bounds and zoom range. Attribution: © OpenStreetMap contributors; Protomaps Basemap. Data license: Open Database License (ODbL) 1.0. The source build key, date, size, checksum metadata, and geographic bounds are in manifests/protomaps-build.json and manifests/map-payload.json. Preserve this attribution in the map interface and any redistributed derivative.
EOF

echo "Fetching model license texts and pinned Ollama model payloads..."
mkdir -p "$STAGE/licenses/models/qwen3" "$STAGE/licenses/models/nomic-embed-text"
curl --fail --silent --show-error https://huggingface.co/Qwen/Qwen3-0.6B/raw/main/LICENSE -o "$STAGE/licenses/models/qwen3/LICENSE"
cat > "$STAGE/licenses/models/nomic-embed-text/LICENSE.txt" <<'EOF'
nomic-embed-text-v1.5 is distributed under Apache License 2.0. The upstream
model card and license are available from https://huggingface.co/nomic-ai/nomic-embed-text-v1.5.
EOF
docker run --detach --name "$MODEL_CONTAINER" --network bridge \
  -v "$STAGE/content/ollama:/root/.ollama" \
  ollama/ollama:0.33.3@sha256:32931b46719f673c05fdbaa81ccb26da18ea4a1c57590a754874ab28ba269eb2 serve >/dev/null
for attempt in $(seq 1 60); do
  docker exec "$MODEL_CONTAINER" ollama list >/dev/null 2>&1 && break
  sleep 2
done
mapfile -t BUNDLED_CHAT_MODELS < <(python3 - "$ROOT/models/manifest.json" <<'PY'
import json
import sys
manifest = json.load(open(sys.argv[1], encoding="utf-8"))
for model in manifest["chat_models"]:
    if model.get("bundled_in_test_iso"):
        print(model["ollama_ref"])
PY
)
for model_ref in "${BUNDLED_CHAT_MODELS[@]}"; do
  docker exec "$MODEL_CONTAINER" ollama pull "$model_ref"
done
docker exec "$MODEL_CONTAINER" ollama pull nomic-embed-text:v1.5
docker exec "$MODEL_CONTAINER" ollama list > "$STAGE/manifests/ollama-models.txt"
python3 - "$STAGE/content/ollama" "$ROOT/models/manifest.json" > "$STAGE/manifests/model-payload.json" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
models = json.load(open(sys.argv[2]))
records = []
for item in models["chat_models"] + models["embedding_models"]:
    if not item.get("bundled_in_test_iso"):
        continue
    model_name, model_tag = item["ollama_ref"].rsplit(":", 1)
    model_path = root / "models/manifests/registry.ollama.ai/library" / model_name / model_tag
    manifest_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if manifest_hash != item["ollama_manifest_sha256"]:
        raise SystemExit(f"Ollama manifest SHA-256 mismatch for {item['id']}: {manifest_hash}")
    blob = root / "models/blobs" / f"sha256-{item['model_blob_sha256']}"
    digest = hashlib.sha256()
    with blob.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != item["model_blob_sha256"] or blob.stat().st_size != item["model_blob_bytes"]:
        raise SystemExit(f"Ollama model layer verification failed for {item['id']}")
    records.append({"id": item["id"], "ollama_ref": item["ollama_ref"], "manifest_sha256": manifest_hash,
                    "model_blob_sha256": digest.hexdigest(), "model_blob_bytes": blob.stat().st_size})
print(json.dumps({"schema_version": 1, "models": records}, indent=2))
PY
docker exec "$MODEL_CONTAINER" ollama show qwen3:0.6b-q4_K_M --license > "$STAGE/licenses/models/qwen3/Ollama-LICENSE.txt"
docker exec "$MODEL_CONTAINER" ollama show nomic-embed-text:v1.5 --license > "$STAGE/licenses/models/nomic-embed-text/Ollama-LICENSE.txt"
docker rm -f "$MODEL_CONTAINER" >/dev/null
MODEL_CONTAINER="fieldos-model-seed-$$"
OLLAMA_REF=ollama/ollama:0.33.3
OLLAMA_DIGEST=sha256:32931b46719f673c05fdbaa81ccb26da18ea4a1c57590a754874ab28ba269eb2
# The Ollama CLI creates a registry key pair and recommendation cache.
# These runtime-generated files do not belong in the distributable payload.
docker run --rm --network none \
  -v "$STAGE/content/ollama:/data" \
  --entrypoint /bin/sh "$OLLAMA_REF@$OLLAMA_DIGEST" \
  -c 'rm -rf /data/cache /data/id_ed25519 /data/id_ed25519.pub; chmod -R a+rX /data/models'
python3 - "$ROOT/models/manifest.json" "$STAGE/manifests/model-payload.json" \
  > "$STAGE/model-ids.json" <<'PY'
import json
import sys
manifest = json.load(open(sys.argv[1], encoding="utf-8"))
payload = json.load(open(sys.argv[2], encoding="utf-8"))
present = {record["id"] for record in payload["models"]}
print(json.dumps({
    "chat": [model["id"] for model in manifest["chat_models"] if model["id"] in present],
    "embedding": [model["id"] for model in manifest["embedding_models"] if model["id"] in present],
}, indent=2))
PY

cat > "$STAGE/licenses/CONTAINER-IMAGES.md" <<'EOF'
# Container image notices

The image references and registry manifest digests are listed in
`manifests/images.json`. The test payload includes the linux/amd64 image
objects for private evaluation. Upstream source and license locations:

| Component | License | Source |
|---|---|---|
| Project N.O.M.A.D. | Apache-2.0 | https://github.com/Crosstalk-Solutions/project-nomad/tree/v1.35.1 |
| MySQL | GPL-2.0 | https://github.com/mysql/mysql-server |
| Redis | BSD-3-Clause | https://github.com/redis/redis |
| Dozzle | MIT | https://github.com/amir20/dozzle |
| Ollama | MIT | https://github.com/ollama/ollama |
| Qdrant | Apache-2.0 | https://github.com/qdrant/qdrant |
| Kiwix Serve | GPL-3.0-or-later | https://github.com/kiwix/kiwix-tools |

Candidate license/copyright files from all image layers are stored under
`container-images/`; per-image indexes map content hashes back to original
paths and layers. This filename-based extraction does not establish complete
coverage. Review all SBOM entries, notices, and corresponding-source or offer
obligations before distribution. The pinned N.O.M.A.D. image includes Debian
Ghostscript packages whose copyright metadata identifies AGPL-3+; verify and
provide the exact corresponding source package as required. The payload
includes its checksum-pinned Debian source package under
`licenses/source-offers/ghostscript/`, described in
`manifests/source-offers.json`. No image is cleared for public redistribution
by this automated inventory.
EOF

cp "$ROOT/payload/manifests/images.json" "$STAGE/manifests/"
cp "$ROOT/payload/manifests/source-offers.json" "$STAGE/manifests/"
cp "$ROOT/payload/manifests/source-offers.json" "$STAGE/licenses/source-offers.json"
cp "$ROOT/payload/manifests/maps.json" "$STAGE/manifests/"
cp "$ROOT/payload/manifests/ubuntu-26.04.1-desktop-amd64.json" "$STAGE/manifests/"
printf '{"version":"26.04","base_image":"ubuntu:26.04@sha256:6a06111c3b0a8600feadb270aec771dc239bf407b25625f93f44ab00e11f4d3c","requested_packages":["docker.io","docker-compose-v2","curl","zstd","qemu-guest-agent","vulkan-tools","zenity"],"install_recommends":false,"required_base_packages":["zenity","pkexec"]}\n' \
  > "$STAGE/manifests/package-request.json"

echo "Creating deterministic compressed payload archive..."
tar --sort=name --mtime='UTC 2026-11-02' --owner=0 --group=0 --numeric-owner \
  -C "$STAGE" -cf - debs oci content content-packs licenses manifests model-ids.json \
  | zstd --threads=0 --ultra -12 -o "$ARCHIVE"
(
  cd "$OUT"
  sha256sum "$(basename "$ARCHIVE")" > "$(basename "$ARCHIVE").sha256"
)
# Restore host ownership so the EXIT trap can remove root-owned Ollama files.
docker run --rm --network none \
  -v "$STAGE:/stage" \
  --entrypoint /bin/sh "$OLLAMA_REF@$OLLAMA_DIGEST" \
  -c "chown -R $(id -u):$(id -g) /stage/content/ollama"
echo "Prepared payload: $ARCHIVE ($(du -h "$ARCHIVE" | awk '{print $1}'))"
