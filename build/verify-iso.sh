#!/usr/bin/env bash
set -Eeuo pipefail

ISO=${1:?usage: verify-iso.sh image.iso}
ISO=$(realpath "$ISO")
for tool in xorriso sha256sum; do
  command -v "$tool" >/dev/null || { echo "Missing required tool: $tool" >&2; exit 2; }
done
[[ -s "$ISO" ]] || { echo "ISO is missing or empty: $ISO" >&2; exit 1; }

REPORT=$(xorriso -indev "$ISO" -report_el_torito plain 2>&1)
grep -q 'BIOS' <<<"$REPORT" || { echo "ISO has no BIOS El Torito boot entry" >&2; exit 1; }
grep -q 'UEFI' <<<"$REPORT" || { echo "ISO has no UEFI El Torito boot entry" >&2; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
for path in /fieldos/build-manifest.json /fieldos/payload/offline-payload.tar.zst \
  /nocloud/user-data /nocloud/meta-data; do
  dest="$TMP/$(basename "$(dirname "$path")")-$(basename "$path")"
  xorriso -osirrox on -indev "$ISO" -extract "$path" "$dest" >/dev/null 2>&1
  [[ -s "$dest" ]] || { echo "Missing required ISO path: $path" >&2; exit 1; }
done
xorriso -osirrox on -indev "$ISO" -extract /boot/grub/grub.cfg "$TMP/grub.cfg" >/dev/null 2>&1
grep -q 'Install Hckrslsh FieldOS (interactive)' "$TMP/grub.cfg" \
  || { echo "FieldOS installer boot entry is missing" >&2; exit 1; }
grep -q 'set default="Install Hckrslsh FieldOS (interactive)"' "$TMP/grub.cfg" \
  || { echo "FieldOS interactive installer is not the default boot selection" >&2; exit 1; }

echo "ISO structure, BIOS/UEFI boot records, installer config, and payload presence verified."
sha256sum "$ISO"
