#!/usr/bin/env bash
set -Eeuo pipefail

MODE=${1:?usage: build-iso.sh test|full UBUNTU_ISO [AUTOINSTALL_FILE]}
SOURCE_ISO=${2:?usage: build-iso.sh test|full UBUNTU_ISO [AUTOINSTALL_FILE]}
AUTOINSTALL_FILE=${3:-${FIELDOS_AUTOINSTALL_FILE:-}}
case "$MODE" in test|full) ;; *) echo "Unknown image mode: $MODE" >&2; exit 2 ;; esac

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
WORK=$(mktemp -d "$WORK_ROOT/work-${MODE}.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/fieldos/installer/provisioning" "$WORK/fieldos/hardware/detect" \
  "$WORK/fieldos/models" "$WORK/fieldos/services" "$WORK/fieldos/payload/licenses" \
  "$WORK/fieldos/scripts" \
  "$WORK/nocloud"

install -m 0644 "$ROOT/installer/provisioning/firstboot.sh" "$WORK/fieldos/installer/provisioning/firstboot.sh"
install -m 0644 "$ROOT/installer/provisioning/build_local_apt_index.py" "$WORK/fieldos/installer/provisioning/build_local_apt_index.py"
install -m 0644 "$ROOT/installer/provisioning/fieldos-firstboot.service" "$WORK/fieldos/installer/provisioning/fieldos-firstboot.service"
install -m 0644 "$ROOT/installer/provisioning/fieldos.desktop" "$WORK/fieldos/installer/provisioning/fieldos.desktop"
install -m 0644 "$ROOT/installer/provisioning/fieldos-sources.desktop" "$WORK/fieldos/installer/provisioning/fieldos-sources.desktop"
install -m 0644 "$ROOT/payload/licenses/CONTENT-SOURCES.md" "$WORK/fieldos/payload/licenses/CONTENT-SOURCES.md"
install -m 0644 "$ROOT/payload/licenses/CC-BY-SA-4.0.txt" "$WORK/fieldos/payload/licenses/CC-BY-SA-4.0.txt"
install -m 0644 "$ROOT/payload/licenses/ODbL-1.0.txt" "$WORK/fieldos/payload/licenses/ODbL-1.0.txt"
install -m 0644 "$ROOT/hardware/detect/detect.py" "$WORK/fieldos/hardware/detect/detect.py"
install -m 0644 "$ROOT/hardware/select_profile.py" "$WORK/fieldos/hardware/select_profile.py"
install -m 0644 "$ROOT/models/manifest.json" "$WORK/fieldos/models/manifest.json"
install -m 0644 "$ROOT/services/compose.yaml" "$WORK/fieldos/services/compose.yaml"
install -m 0755 "$ROOT/scripts/fieldos-diagnostics.sh" "$WORK/fieldos/scripts/fieldos-diagnostics.sh"
install -m 0644 "$PAYLOAD" "$WORK/fieldos/payload/offline-payload.tar.zst"
install -m 0644 "$PAYLOAD.sha256" "$WORK/fieldos/payload/offline-payload.tar.zst.sha256"
if [[ -n "$AUTOINSTALL_FILE" ]]; then
  AUTOINSTALL_FILE=$(realpath "$AUTOINSTALL_FILE")
else
  AUTOINSTALL_FILE="$ROOT/installer/autoinstall/user-data"
fi
install -m 0644 "$AUTOINSTALL_FILE" "$WORK/nocloud/user-data"
install -m 0644 "$ROOT/installer/autoinstall/meta-data" "$WORK/nocloud/meta-data"

cat > "$WORK/fieldos/build-manifest.json" <<EOF
{
  "product": "Hckrslsh FieldOS",
  "edition": "$MODE",
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

"$ROOT/build/verify-iso.sh" "$OUTPUT"
sha256sum "$OUTPUT" > "$OUTPUT.sha256"
echo "Created $OUTPUT"
