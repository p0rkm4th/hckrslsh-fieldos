#!/usr/bin/env bash
set -Eeuo pipefail

MODE=${1:?usage: build-iso.sh test|full UBUNTU_ISO [AUTOINSTALL_FILE]}
SOURCE_ISO=${2:?usage: build-iso.sh test|full UBUNTU_ISO [AUTOINSTALL_FILE]}
AUTOINSTALL_FILE=${3:-${FIELDOS_AUTOINSTALL_FILE:-}}
VERIFY_MODE=${FIELDOS_VERIFY_MODE:-customer}
case "$MODE" in test|full) ;; *) echo "Unknown image mode: $MODE" >&2; exit 2 ;; esac
case "$VERIFY_MODE" in customer|test) ;; *) echo "Unknown ISO verification mode: $VERIFY_MODE" >&2; exit 2 ;; esac

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
SOURCE_ISO=$(realpath "$SOURCE_ISO")
EXPECTED=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["sha256"])' \
  "$ROOT/payload/manifests/ubuntu-26.04.1-desktop-amd64.json")
ACTUAL=$(sha256sum "$SOURCE_ISO" | awk '{print $1}')
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "Ubuntu source ISO checksum mismatch: expected $EXPECTED, got $ACTUAL" >&2
  exit 1
fi

PAYLOAD_ROOT=${FIELDOS_PAYLOAD_ROOT:-"$ROOT/build/payload"}
PAYLOAD="$PAYLOAD_ROOT/offline-payload.tar.zst"
if [[ ! -s "$PAYLOAD" || ! -s "$PAYLOAD.sha256" ]]; then
  echo "Offline payload is not prepared. Run build/prepare-payload.sh first." >&2
  exit 1
fi
(cd "$(dirname "$PAYLOAD")" && sha256sum -c "$(basename "$PAYLOAD").sha256")
python3 "$ROOT/build/verify_payload.py" "$PAYLOAD" \
  --catalog "$ROOT/payload/manifests/content-packs.json" \
  --maps-manifest "$ROOT/payload/manifests/maps.json"

OUT_DIR=${FIELDOS_OUTPUT_ROOT:-"$ROOT/build/out"}
mkdir -p "$OUT_DIR"
OUTPUT="$OUT_DIR/fieldos-${MODE}.iso"
OUTPUT=${FIELDOS_OUTPUT_PATH:-$OUTPUT}
mkdir -p "$(dirname "$OUTPUT")"
if [[ -e "$OUTPUT" ]]; then
  echo "Refusing to overwrite existing artifact: $OUTPUT" >&2
  exit 1
fi
WORK_ROOT=${FIELDOS_WORK_ROOT:-"$ROOT/build"}
mkdir -p "$WORK_ROOT"
require_free_bytes() {
  local path="$1" needed="$2" available
  available=$(df -Pk "$path" | awk 'NR == 2 { print $4 * 1024 }')
  if [[ -z "$available" ]] || (( available < needed )); then
    echo "Insufficient free space at $path: need $needed bytes, have ${available:-unknown}" >&2
    exit 1
  fi
}
source_bytes=$(stat -c %s "$SOURCE_ISO")
payload_bytes=$(stat -c %s "$PAYLOAD")
payload_link_possible=0
if [[ "$(stat -c %d "$PAYLOAD")" == "$(stat -c %d "$WORK_ROOT")" && \
      "$(stat -c %a "$PAYLOAD")" == 644 ]]; then
  payload_link_possible=1
fi
# xorriso writes a complete new ISO; staging also copies the compressed payload.
output_dir=$(dirname "$OUTPUT")
output_need=$((source_bytes + 1024 * 1024 * 1024))
if (( payload_link_possible )); then
  work_need=$((1024 * 1024 * 1024))
else
  work_need=$((payload_bytes + 1024 * 1024 * 1024))
fi
output_device=$(df -P "$output_dir" | awk 'NR == 2 { print $1 }')
work_device=$(df -P "$WORK_ROOT" | awk 'NR == 2 { print $1 }')
if [[ -n "$output_device" && "$output_device" == "$work_device" ]]; then
  require_free_bytes "$output_dir" "$((output_need + work_need))"
else
  require_free_bytes "$output_dir" "$output_need"
  require_free_bytes "$WORK_ROOT" "$work_need"
fi
WORK=$(mktemp -d "$WORK_ROOT/work-${MODE}.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/fieldos/installer/provisioning" "$WORK/fieldos/installer/provisioning/assets" "$WORK/fieldos/hardware/detect" \
  "$WORK/fieldos/models" "$WORK/fieldos/services" "$WORK/fieldos/payload/licenses" \
  "$WORK/fieldos/payload/manifests" "$WORK/fieldos/scripts" \
  "$WORK/nocloud"

install -m 0644 "$ROOT/installer/provisioning/firstboot.sh" "$WORK/fieldos/installer/provisioning/firstboot.sh"
install -m 0644 "$ROOT/installer/provisioning/patch-nomad-fieldos-copy.sh" "$WORK/fieldos/installer/provisioning/patch-nomad-fieldos-copy.sh"
install -m 0644 "$ROOT/installer/provisioning/patch-nomad-fieldos-copy.js" "$WORK/fieldos/installer/provisioning/patch-nomad-fieldos-copy.js"
install -m 0644 "$ROOT/installer/provisioning/patch-nomad-rag-policy.sh" "$WORK/fieldos/installer/provisioning/patch-nomad-rag-policy.sh"
install -m 0644 "$ROOT/installer/provisioning/patch_nomad_rag_policy.py" "$WORK/fieldos/installer/provisioning/patch_nomad_rag_policy.py"
install -m 0644 "$ROOT/installer/provisioning/build_local_apt_index.py" "$WORK/fieldos/installer/provisioning/build_local_apt_index.py"
install -m 0644 "$ROOT/installer/provisioning/fieldos-firstboot.service" "$WORK/fieldos/installer/provisioning/fieldos-firstboot.service"
install -m 0644 "$ROOT/installer/provisioning/fieldos.desktop" "$WORK/fieldos/installer/provisioning/fieldos.desktop"
install -m 0644 "$ROOT/installer/provisioning/fieldos-start-here.desktop" "$WORK/fieldos/installer/provisioning/fieldos-start-here.desktop"
install -m 0644 "$ROOT/installer/provisioning/fieldos-start-here.html" "$WORK/fieldos/installer/provisioning/fieldos-start-here.html"
install -m 0644 "$ROOT/installer/provisioning/fieldos-content-pack-import.desktop" "$WORK/fieldos/installer/provisioning/fieldos-content-pack-import.desktop"
install -m 0644 "$ROOT/installer/provisioning/fieldos-content-pack-import.policy" "$WORK/fieldos/installer/provisioning/fieldos-content-pack-import.policy"
install -m 0755 "$ROOT/installer/provisioning/fieldos-content-pack-import-root" "$WORK/fieldos/installer/provisioning/fieldos-content-pack-import-root"
install -m 0644 "$ROOT/installer/provisioning/fieldos-sources.desktop" "$WORK/fieldos/installer/provisioning/fieldos-sources.desktop"
install -m 0755 "$ROOT/installer/provisioning/install-branding.sh" "$WORK/fieldos/installer/provisioning/install-branding.sh"
install -m 0644 "$ROOT/installer/provisioning/assets/fieldos-wallpaper.svg" "$WORK/fieldos/installer/provisioning/assets/fieldos-wallpaper.svg"
install -m 0644 "$ROOT/installer/provisioning/assets/fieldos.svg" "$WORK/fieldos/installer/provisioning/assets/fieldos.svg"
install -m 0644 "$ROOT/payload/licenses/CONTENT-SOURCES.md" "$WORK/fieldos/payload/licenses/CONTENT-SOURCES.md"
install -m 0644 "$ROOT/payload/licenses/CC-BY-SA-4.0.txt" "$WORK/fieldos/payload/licenses/CC-BY-SA-4.0.txt"
install -m 0644 "$ROOT/payload/licenses/ODbL-1.0.txt" "$WORK/fieldos/payload/licenses/ODbL-1.0.txt"
install -m 0644 "$ROOT/hardware/detect/detect.py" "$WORK/fieldos/hardware/detect/detect.py"
install -m 0644 "$ROOT/hardware/select_profile.py" "$WORK/fieldos/hardware/select_profile.py"
install -m 0644 "$ROOT/models/manifest.json" "$WORK/fieldos/models/manifest.json"
install -m 0644 "$ROOT/services/compose.yaml" "$WORK/fieldos/services/compose.yaml"
install -m 0755 "$ROOT/scripts/fieldos-diagnostics.sh" "$WORK/fieldos/scripts/fieldos-diagnostics.sh"
install -m 0755 "$ROOT/scripts/fieldos-content-packs.py" "$WORK/fieldos/scripts/fieldos-content-packs.py"
install -m 0755 "$ROOT/scripts/fieldos-content-pack-import.py" "$WORK/fieldos/scripts/fieldos-content-pack-import.py"
install -m 0755 "$ROOT/scripts/fieldos-nomad-index-references.py" "$WORK/fieldos/scripts/fieldos-nomad-index-references.py"
install -m 0644 "$ROOT/payload/validate_content_packs.py" "$WORK/fieldos/scripts/validate_content_packs.py"
install -m 0644 "$ROOT/payload/manifests/content-pack.schema.json" \
  "$WORK/fieldos/payload/manifests/content-pack.schema.json"
if (( payload_link_possible )); then
  ln "$PAYLOAD" "$WORK/fieldos/payload/offline-payload.tar.zst"
else
  install -m 0644 "$PAYLOAD" "$WORK/fieldos/payload/offline-payload.tar.zst"
fi
install -m 0644 "$PAYLOAD.sha256" "$WORK/fieldos/payload/offline-payload.tar.zst.sha256"
if [[ -n "$AUTOINSTALL_FILE" ]]; then
  AUTOINSTALL_FILE=$(realpath "$AUTOINSTALL_FILE")
else
  AUTOINSTALL_FILE="$ROOT/installer/autoinstall/user-data"
fi
install -m 0644 "$AUTOINSTALL_FILE" "$WORK/nocloud/user-data"
install -m 0644 "$ROOT/installer/autoinstall/meta-data" "$WORK/nocloud/meta-data"

SOURCE_REVISION=$(git -C "$ROOT" rev-parse HEAD)
SOURCE_DIRTY=false
if [[ -n "$(git -C "$ROOT" status --porcelain --untracked-files=all)" ]]; then
  SOURCE_DIRTY=true
fi

cat > "$WORK/fieldos/build-manifest.json" <<EOF
{
  "product": "Hckrslsh FieldOS",
  "edition": "$MODE",
  "source_revision": "$SOURCE_REVISION",
  "source_dirty": $SOURCE_DIRTY,
  "ubuntu_source_sha256": "$ACTUAL",
  "project_nomad": "v1.35.1",
  "payload_sha256": "$(awk '{print $1}' "$PAYLOAD.sha256")",
  "build_date_utc": "$(date -u +%FT%TZ)",
  "architecture": "amd64"
}
EOF

xorriso -osirrox on -indev "$SOURCE_ISO" \
  -extract /boot/grub/grub.cfg "$WORK/grub.cfg"
python3 - "$WORK/grub.cfg" "$WORK/grub-fieldos.cfg" <<'PY'
from pathlib import Path
import os
import sys

source = Path(sys.argv[1]).read_text()
entry = '''\nmenuentry "Install Hckrslsh FieldOS (interactive)" {
    set gfxpayload=keep
    linux  /casper/vmlinuz autoinstall ds=nocloud\\;s=/cdrom/nocloud/ --- quiet splash
    initrd /casper/initrd
}
'''
if 'Install Hckrslsh FieldOS (interactive)' in source:
    raise SystemExit('source GRUB menu already contains FieldOS entry')
source = source.replace(
    'set timeout=30',
    'set timeout=30\nset default="Install Hckrslsh FieldOS (interactive)"',
    1,
)
Path(sys.argv[2]).write_text(source + entry)
if os.environ.get('FIELDOS_TEST_AUTOBOOT') == '1':
    test_source = Path(sys.argv[2]).read_text()
    test_source = test_source.replace('set timeout=30', 'set timeout=0', 1)
    test_source = test_source.replace('autoinstall ds=nocloud\\;s=/cdrom/nocloud/ --- quiet splash',
                                      'autoinstall ds=nocloud\\;s=/cdrom/nocloud/ console=ttyS0,115200n8 --- quiet')
    test_source = 'serial --unit=0 --speed=115200\nterminal_input console serial\nterminal_output console serial\n' + test_source
    Path(sys.argv[2]).write_text(test_source)
PY

echo "Composing $OUTPUT from checksum-verified Ubuntu media..."
xorriso -indev "$SOURCE_ISO" -outdev "$OUTPUT" \
  -map "$WORK/fieldos" /fieldos \
  -map "$WORK/nocloud" /nocloud \
  -map "$WORK/grub-fieldos.cfg" /boot/grub/grub.cfg \
  -boot_image any replay -commit

"$ROOT/build/verify-iso.sh" "$OUTPUT" "$VERIFY_MODE"
sha256sum "$OUTPUT" > "$OUTPUT.sha256"
echo "Created $OUTPUT"
