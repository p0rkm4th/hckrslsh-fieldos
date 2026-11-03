#!/usr/bin/env bash
set -Eeuo pipefail

STATE=/var/lib/fieldos
printf 'Hckrslsh FieldOS diagnostics\n\n'
for path in provisioning-status.json hardware.json model-selection.json; do
  printf '%s\n' "--- $path"
  if [[ -r "$STATE/$path" ]]; then cat "$STATE/$path"; else echo 'not available yet'; fi
  printf '\n'
done

printf '%s\n' '--- firstboot unit'
systemctl show fieldos-firstboot.service \
  --property=LoadState --property=ActiveState --property=SubState \
  --property=Result --property=ExecMainStatus --no-pager 2>&1 || true
printf '\n%s\n' '--- firstboot journal (last 40 lines)'
journalctl --unit=fieldos-firstboot.service --no-pager --lines=40 2>&1 || true
if [[ -r /var/log/fieldos-firstboot.log ]]; then
  printf '\n%s\n' '--- firstboot log (last 80 lines)'
  tail --lines=80 /var/log/fieldos-firstboot.log
else
  printf '\n%s\n' 'firstboot log: unavailable (run diagnostics with sudo)'
fi

printf '\n%s\n' '--- storage'
df -h / /var/lib/fieldos 2>&1 || true

printf '\n%s\n' '--- Compose services'
if systemctl is-active --quiet docker; then
  docker compose --project-directory /opt/fieldos/services \
    --file /opt/fieldos/services/compose.yaml ps 2>&1 || true
else
  echo 'Docker service: inactive'
fi

printf '%s\n' '--- services'
for item in 'N.O.M.A.D.|8080/api/health' 'Ollama|11434/api/version' 'Kiwix|8090'; do
  name=${item%%|*}
  endpoint=${item#*|}
  if curl --fail --silent --max-time 3 "http://127.0.0.1:$endpoint" >/dev/null 2>&1; then
    printf '%s: healthy\n' "$name"
  else
    printf '%s: unavailable\n' "$name"
  fi
done
