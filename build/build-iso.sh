#!/usr/bin/env bash
set -Eeuo pipefail

MODE=${1:?usage: build-iso.sh test|full UBUNTU_ISO}
SOURCE_ISO=${2:?usage: build-iso.sh test|full UBUNTU_ISO}
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

PAYLOAD="$ROOT/build/payload/offline-payload.tar.zst"
if [[ ! -s "$PAYLOAD" || ! -s "$PAYLOAD.sha256" ]]; then
  echo "Offline payload is not prepared. Run build/prepare-payload.sh first." >&2
  exit 1
fi
(cd "$(dirname "$PAYLOAD")" && sha256sum -c "$(basename "$PAYLOAD").sha256")

OUT_DIR="$ROOT/build/out"
mkdir -p "$OUT_DIR"
OUTPUT="$OUT_DIR/fieldos-${MODE}.iso"
if [[ -e "$OUTPUT" ]]; then
  echo "Refusing to overwrite existing artifact: $OUTPUT" >&2
  exit 1
fi
WORK=$(mktemp -d "$ROOT/build/work-${MODE}.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/fieldos/installer/provisioning" "$WORK/fieldos/hardware/detect" \
  "$WORK/fieldos/models" "$WORK/fieldos/services" "$WORK/fieldos/payload" \
  "$WORK/nocloud"

install -m 0644 "$ROOT/installer/provisioning/firstboot.sh" "$WORK/fieldos/installer/provisioning/firstboot.sh"
install -m 0644 "$ROOT/installer/provisioning/fieldos-firstboot.service" "$WORK/fieldos/installer/provisioning/fieldos-firstboot.service"
install -m 0644 "$ROOT/installer/provisioning/fieldos.desktop" "$WORK/fieldos/installer/provisioning/fieldos.desktop"
install -m 0644 "$ROOT/hardware/detect/detect.py" "$WORK/fieldos/hardware/detect/detect.py"
install -m 0644 "$ROOT/hardware/select_profile.py" "$WORK/fieldos/hardware/select_profile.py"
install -m 0644 "$ROOT/models/manifest.json" "$WORK/fieldos/models/manifest.json"
install -m 0644 "$ROOT/services/compose.yaml" "$WORK/fieldos/services/compose.yaml"
install -m 0644 "$PAYLOAD" "$WORK/fieldos/payload/offline-payload.tar.zst"
install -m 0644 "$PAYLOAD.sha256" "$WORK/fieldos/payload/offline-payload.tar.zst.sha256"
install -m 0644 "$ROOT/installer/autoinstall/user-data" "$WORK/nocloud/user-data"
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
Path(sys.argv[2]).write_text(source + entry)
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
