#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
OUT="$ROOT/build/payload"
ARCHIVE="$OUT/offline-payload.tar.zst"
[[ ! -e "$ARCHIVE" ]] || { echo "Payload already exists; move it aside explicitly before rebuilding: $ARCHIVE" >&2; exit 1; }
mkdir -p "$OUT"
STAGE=$(mktemp -d "$OUT/stage.XXXXXX")
trap 'docker rm -f "$MODEL_CONTAINER" >/dev/null 2>&1 || true; rm -rf "$STAGE"' EXIT
MODEL_CONTAINER="fieldos-model-seed-$$"

for tool in docker git curl python3 zstd sha256sum tar; do
  command -v "$tool" >/dev/null || { echo "Missing payload build tool: $tool" >&2; exit 2; }
done

mkdir -p "$STAGE"/{debs,oci,content/zim,content/maps/pmtiles,content/maps/basemaps-assets,content/ollama,licenses,manifests}

python3 - "$ROOT/payload/manifests/images.json" <<'PY' > "$STAGE/manifests/images.tsv"
import json, sys
for image in json.load(open(sys.argv[1]))["images"]:
    print(image["ref"], image["digest"], sep="\t")
PY

echo "Downloading the pinned Ubuntu package closure in an Ubuntu 26.04 environment..."
docker run --rm --platform linux/amd64 \
  -v "$STAGE/debs:/out" \
  ubuntu:26.04@sha256:6a06111c3b0a8600feadb270aec771dc239bf407b25625f93f44ab00e11f4d3c \
  bash -euxc 'apt-get update; apt-get install --download-only --yes --no-install-recommends docker.io docker-compose-v2 curl zstd qemu-guest-agent; cp /var/cache/apt/archives/*.deb /out/'

while IFS=$'\t' read -r ref digest; do
  [[ -n "$ref" ]] || continue
  echo "Pulling $ref@$digest"
  docker pull --platform linux/amd64 "$ref@$digest"
  docker image tag "$ref@$digest" "$ref"
  name=$(python3 - "$ref" <<'PY'
import sys
name = sys.argv[1].split('/')[-1].split(':')[0]
print(name.replace('/', '_'))
PY
)
  docker image save "$ref" --output "$STAGE/oci/${name}.tar"
done < "$STAGE/manifests/images.tsv"

NOMAD_REF=ghcr.io/crosstalk-solutions/project-nomad:v1.35.1
NOMAD_DIGEST=sha256:1445a3eaba19801ce27435b7edc57fce74d9543601808d719b432e3bc7468ea1
docker run --rm --network none --entrypoint /usr/local/bin/pmtiles "$NOMAD_REF@$NOMAD_DIGEST" --help >/dev/null

echo "Fetching source-pinned Project N.O.M.A.D. reference and map styling..."
git clone --depth 1 --branch v1.35.1 https://github.com/Crosstalk-Solutions/project-nomad.git "$STAGE/project-nomad"
git clone https://github.com/Crosstalk-Solutions/project-nomad-maps.git "$STAGE/project-nomad-maps"
git -C "$STAGE/project-nomad-maps" checkout --detach 5b444051914fbf4960be2e64c0fb11f507db7efd
cp "$STAGE/project-nomad/install/wikipedia_en_100_mini_2026-01.zim" "$STAGE/content/zim/"
cp "$STAGE/project-nomad-maps/nomad-base-styles.json" "$STAGE/content/maps/"
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
printf '%s\n' \
  'Wikipedia content is © its contributors and licensed under the applicable Creative Commons Attribution-ShareAlike terms.' \
  'The miniature ZIM comes from Project N.O.M.A.D. v1.35.1 source: install/wikipedia_en_100_mini_2026-01.zim.' \
  'Display attribution and the applicable license in the installed information library.' \
  > "$STAGE/licenses/wikipedia-zim-attribution.txt"

echo "Resolving the current Protomaps build and extracting a low-zoom offline world map..."
curl --fail --silent --show-error https://build-metadata.protomaps.dev/builds.json -o "$STAGE/manifests/protomaps-builds.json"
python3 - "$STAGE/manifests/protomaps-builds.json" > "$STAGE/manifests/protomaps-build.json" <<'PY'
import json, sys
items = json.load(open(sys.argv[1]))
latest = max(items, key=lambda item: item["uploaded"])
print(json.dumps(latest, indent=2))
PY
MAP_KEY=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["key"])' "$STAGE/manifests/protomaps-build.json")
docker run --rm --network bridge \
  -v "$STAGE/content/maps/pmtiles:/maps" \
  --entrypoint /usr/local/bin/pmtiles \
  "$NOMAD_REF@$NOMAD_DIGEST" \
  extract "https://build.protomaps.com/$MAP_KEY" /maps/world.pmtiles --bbox=-180,-85,180,85 --maxzoom=5
docker run --rm --network none -v "$STAGE/content/maps/pmtiles:/maps" \
  --entrypoint /usr/local/bin/pmtiles "$NOMAD_REF@$NOMAD_DIGEST" show /maps/world.pmtiles \
  > "$STAGE/manifests/world-map-metadata.txt"
cat > "$STAGE/licenses/protomaps-odbl-attribution.txt" <<'EOF'
The world.pmtiles dataset is a low-zoom extract of the Protomaps Basemap, a Produced Work derived from OpenStreetMap data. Attribution: © OpenStreetMap contributors; Protomaps Basemap. Data license: Open Database License (ODbL) 1.0. The source build key, date, size, and checksum metadata are in manifests/protomaps-build.json. Preserve this attribution in the map interface and any redistributed derivative.
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
docker exec "$MODEL_CONTAINER" ollama pull qwen3:0.6b-q4_K_M
docker exec "$MODEL_CONTAINER" ollama pull nomic-embed-text:v1.5
docker exec "$MODEL_CONTAINER" ollama list > "$STAGE/manifests/ollama-models.txt"
docker exec "$MODEL_CONTAINER" ollama show qwen3:0.6b-q4_K_M --license > "$STAGE/licenses/models/qwen3/Ollama-LICENSE.txt"
docker exec "$MODEL_CONTAINER" ollama show nomic-embed-text:v1.5 --license > "$STAGE/licenses/models/nomic-embed-text/Ollama-LICENSE.txt"
docker rm -f "$MODEL_CONTAINER" >/dev/null
MODEL_CONTAINER="fieldos-model-seed-$$"
OLLAMA_REF=ollama/ollama:0.33.3
OLLAMA_DIGEST=sha256:32931b46719f673c05fdbaa81ccb26da18ea4a1c57590a754874ab28ba269eb2
# The Ollama CLI creates a private registry key and a recommendation cache.
# Neither belongs in the offline model payload; only public model blobs do.
docker run --rm --network none \
  -v "$STAGE/content/ollama:/data" \
  --entrypoint /bin/sh "$OLLAMA_REF@$OLLAMA_DIGEST" \
  -c 'rm -rf /data/cache /data/id_ed25519; chmod -R a+rX /data/models'
cat > "$STAGE/model-ids.json" <<'EOF'
{
  "chat": ["qwen3-0.6b-q4_k_m"],
  "embedding": ["nomic-embed-text-v1.5"]
}
EOF

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

Before public release, inspect each image SBOM and all transitive license
notices, include corresponding source/offers where required, and verify
compatibility with the exact registry layers. Do not describe an image as
cleared for public redistribution until that review is complete.
EOF

cp "$ROOT/payload/manifests/images.json" "$STAGE/manifests/"
cp "$ROOT/payload/manifests/ubuntu-26.04.1-desktop-amd64.json" "$STAGE/manifests/"
printf '{"version":"26.04","base_image":"ubuntu:26.04@sha256:6a06111c3b0a8600feadb270aec771dc239bf407b25625f93f44ab00e11f4d3c","requested_packages":["docker.io","docker-compose-v2","curl","zstd","qemu-guest-agent"],"install_recommends":false}\n' \
  > "$STAGE/manifests/package-request.json"

echo "Creating deterministic compressed payload archive..."
tar --sort=name --mtime='UTC 2026-11-02' --owner=0 --group=0 --numeric-owner \
  -C "$STAGE" -cf - debs oci content licenses manifests model-ids.json \
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
