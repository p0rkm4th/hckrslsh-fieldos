#!/usr/bin/env bash
set -Eeuo pipefail

ISO=${1:?usage: verify-iso.sh image.iso [customer|test]}
MODE=${2:-customer}
case "$MODE" in customer|test) ;; *) echo "Unknown ISO verification mode: $MODE" >&2; exit 2 ;; esac
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
  /fieldos/hardware/nomad_initial_model.py \
  /fieldos/models/manifest.json \
  /fieldos/installer/provisioning/patch-nomad-fieldos-copy.sh \
  /fieldos/installer/provisioning/patch-nomad-fieldos-copy.js \
  /fieldos/installer/provisioning/patch-nomad-rag-policy.sh \
  /fieldos/installer/provisioning/patch_nomad_rag_policy.py \
  /fieldos/scripts/fieldos-nomad-index-references.py \
  /fieldos/scripts/fieldos-content-pack-import.py \
  /fieldos/installer/provisioning/fieldos-content-pack-import.desktop \
  /fieldos/installer/provisioning/fieldos-content-pack-import-root \
  /fieldos/installer/provisioning/fieldos-content-pack-import.policy \
  /fieldos/installer/provisioning/fieldos-sources.desktop \
  /fieldos/installer/provisioning/fieldos-start-here.desktop \
  /fieldos/installer/provisioning/fieldos-start-here.html \
  /fieldos/installer/provisioning/install-branding.sh \
  /fieldos/installer/provisioning/assets/fieldos-wallpaper.svg \
  /fieldos/installer/provisioning/assets/fieldos.svg \
  /fieldos/payload/licenses/CONTENT-SOURCES.md \
  /fieldos/payload/licenses/CC-BY-SA-4.0.txt \
  /fieldos/payload/licenses/ODbL-1.0.txt \
  /nocloud/user-data /nocloud/meta-data; do
  dest="$TMP/$(basename "$(dirname "$path")")-$(basename "$path")"
  xorriso -osirrox on -indev "$ISO" -extract "$path" "$dest" >/dev/null 2>&1
  [[ -s "$dest" ]] || { echo "Missing required ISO path: $path" >&2; exit 1; }
done
python3 - "$TMP/fieldos-build-manifest.json" "$MODE" <<'PY'
import json
import re
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text())
if not re.fullmatch(r"[0-9a-f]{40,64}", manifest.get("source_revision", "")):
    raise SystemExit("ISO manifest is missing a valid Git source revision")
if not isinstance(manifest.get("source_dirty"), bool):
    raise SystemExit("ISO manifest is missing the source cleanliness flag")
if sys.argv[2] == "customer" and manifest["source_dirty"]:
    raise SystemExit("Customer candidate was built from uncommitted or untracked source")
PY
grep -q 'START-HERE.html' "$TMP/provisioning-fieldos-start-here.desktop" \
  || { echo "FieldOS offline welcome launcher is incomplete" >&2; exit 1; }
grep -q 'Ready offline in this edition' "$TMP/provisioning-fieldos-start-here.html" \
  || { echo "FieldOS offline content guide is missing its bundled-content section" >&2; exit 1; }
grep -q 'separate internet-connected update session' "$TMP/provisioning-fieldos-start-here.html" \
  || { echo "FieldOS offline content guide is missing its update boundary" >&2; exit 1; }
grep -q 'NIOSH heat-illness first-aid reference' "$TMP/provisioning-fieldos-start-here.html" \
  || { echo "FieldOS offline content guide omits the bundled heat-illness reference" >&2; exit 1; }
grep -q '2026 Southeastern vegetable crop handbook' "$TMP/provisioning-fieldos-start-here.html" \
  || { echo "FieldOS offline content guide omits the bundled agriculture reference" >&2; exit 1; }
grep -q 'FieldOS Install Content Pack' "$TMP/provisioning-fieldos-start-here.html" \
  || { echo "FieldOS offline content guide is missing the pack installer workflow" >&2; exit 1; }
grep -q "picture-uri='file:///usr/share/backgrounds/fieldos/fieldos-wallpaper.svg'" \
  "$TMP/provisioning-install-branding.sh" \
  || { echo "FieldOS wallpaper defaults are missing" >&2; exit 1; }
xorriso -osirrox on -indev "$ISO" -extract /boot/grub/grub.cfg "$TMP/grub.cfg" >/dev/null 2>&1
grep -q 'Install Hckrslsh FieldOS (interactive)' "$TMP/grub.cfg" \
  || { echo "FieldOS installer boot entry is missing" >&2; exit 1; }
grep -q 'set default="Install Hckrslsh FieldOS (interactive)"' "$TMP/grub.cfg" \
  || { echo "FieldOS interactive installer is not the default boot selection" >&2; exit 1; }
grep -Eq '^  apt:$' "$TMP/nocloud-user-data" \
  || { echo "Offline APT configuration is missing" >&2; exit 1; }
grep -Eq '^    geoip: false$' "$TMP/nocloud-user-data" \
  || { echo "Installer geo-IP lookup must be disabled" >&2; exit 1; }
grep -Eq '^    fallback: offline-install$' "$TMP/nocloud-user-data" \
  || { echo "Installer must fall back to the local offline source" >&2; exit 1; }
if [[ "$MODE" == customer ]]; then
  grep -Eq '^  interactive-sections:$' "$TMP/nocloud-user-data" \
    || { echo "Customer installer must leave identity and storage interactive" >&2; exit 1; }
  grep -Eq '^    - identity$' "$TMP/nocloud-user-data" \
    || { echo "Customer installer identity configuration must remain interactive" >&2; exit 1; }
  grep -Eq '^    - storage$' "$TMP/nocloud-user-data" \
    || { echo "Customer installer disk selection must remain interactive" >&2; exit 1; }
  if grep -Eq '^  identity:|^    (username|password|hashed-password):' "$TMP/nocloud-user-data"; then
    echo "Customer ISO must not configure user credentials unattended" >&2
    exit 1
  fi
else
  grep -Eq '^  shutdown: poweroff$' "$TMP/nocloud-user-data" \
    || { echo "Test installer must power off for deterministic media handoff" >&2; exit 1; }
  grep -Eq '^  identity:$' "$TMP/nocloud-user-data" \
    || { echo "Test ISO must configure its disposable test identity" >&2; exit 1; }
  grep -Eq '^    username: fieldos$' "$TMP/nocloud-user-data" \
    || { echo "Test ISO identity must use the isolated acceptance account" >&2; exit 1; }
fi

echo "ISO structure, BIOS/UEFI boot records, $MODE setup, offline APT, and payload presence verified."
sha256sum "$ISO"
