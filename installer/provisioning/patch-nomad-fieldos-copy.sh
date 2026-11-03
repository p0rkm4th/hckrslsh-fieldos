#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT=/opt/fieldos
SERVICES=/opt/fieldos/services
ENV_FILE="$SERVICES/.env"
description='Search installed offline archives. Coverage depends on the content packs installed on this system.'
client_env=
trap '[[ -z "$client_env" ]] || rm -f -- "$client_env"' EXIT

echo "Correcting N.O.M.A.D. information-library copy for FieldOS content..."
docker exec --interactive --user 0 nomad_admin node - \
  < "$ROOT/installer/provisioning/patch-nomad-fieldos-copy.js"

[[ -s "$ENV_FILE" ]] || { echo "Missing FieldOS service credentials: $ENV_FILE" >&2; exit 1; }
db_root_password=$(sed -n 's/^DB_ROOT_PASSWORD=//p' "$ENV_FILE")
[[ "$db_root_password" =~ ^[[:xdigit:]]{64}$ ]] || {
  echo "FieldOS database root credential has an unexpected format." >&2
  exit 1
}
client_env=$(mktemp /run/fieldos-mysql-client.XXXXXX)
printf 'MYSQL_PWD=%s\n' "$db_root_password" > "$client_env"
unset db_root_password
chmod 0600 "$client_env"

mysql() {
  docker exec --env-file "$client_env" nomad_mysql \
    mysql --user=root --database=nomad --batch --skip-column-names "$@"
}

user_modified=$(mysql --execute "SELECT COALESCE(is_user_modified,0) FROM services WHERE service_name='nomad_kiwix_server' LIMIT 1;")
[[ "$user_modified" == 0 || "$user_modified" == 1 ]] || {
  echo "N.O.M.A.D. Kiwix service row was not found or has an invalid user-modified flag." >&2
  exit 1
}
if [[ "$user_modified" == 0 ]]; then
  mysql --execute "UPDATE services SET description='$description' WHERE service_name='nomad_kiwix_server' AND COALESCE(is_user_modified,0)=0;"
  actual=$(mysql --execute "SELECT description FROM services WHERE service_name='nomad_kiwix_server' LIMIT 1;")
  [[ "$actual" == "$description" ]] || { echo "N.O.M.A.D. library description did not update." >&2; exit 1; }
  echo "N.O.M.A.D. information-library description now reflects installed content."
else
  echo "Preserving the operator-modified N.O.M.A.D. library description."
fi
