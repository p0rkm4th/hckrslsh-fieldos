#!/usr/bin/env bash
set -Eeuo pipefail

STATE=/var/lib/fieldos
printf 'Hckrslsh FieldOS diagnostics\n\n'
for path in provisioning-status.json hardware.json model-selection.json; do
  printf '%s\n' "--- $path"
  if [[ -r "$STATE/$path" ]]; then cat "$STATE/$path"; else echo 'not available yet'; fi
  printf '\n'
done

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
