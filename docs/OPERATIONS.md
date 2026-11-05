# Operations and troubleshooting

FieldOS services and application data run locally. The installed system does
not need external network access to start the bundled assistant, reference
library, or maps.

## First boot

The `fieldos-firstboot.service` unit checks and extracts the bundled payload,
installs packages from the local APT repository, loads local container images,
seeds runtime files, selects and validates a model, and starts the Compose
services. Firstboot is guarded by a lock and a completion marker. Check its
result before retrying:

On a fresh installation, GNOME waits until firstboot succeeds. Setup took
about 11 minutes in the 6-vCPU acceptance VM while the 5+ GiB offline payload
was checked and loaded, models were validated, and reference files were
indexed. Slower CPUs can take longer. If the desktop does not appear, use
Ctrl+Alt+F3 at the local console to reach a text login and inspect the status
and logs below. A failed firstboot intentionally keeps the graphical session
closed so the assistant cannot be opened before model validation completes.

The generated Compose credentials are written to a temporary file and
renamed atomically. Each provisioning attempt enforces root ownership and
mode `0600` on the existing `.env` file without replacing its contents.

```sh
systemctl status fieldos-firstboot.service --no-pager
cat /var/lib/fieldos/provisioning-status.json
tail -n 150 /var/log/fieldos-firstboot.log
```

If it failed, the status file records the exit code and log location. Correct
the reported cause, then rerun the idempotent unit:

```sh
sudo systemctl reset-failed fieldos-firstboot.service
sudo systemctl start fieldos-firstboot.service
sudo systemctl reset-failed graphical.target
sudo systemctl start graphical.target
```

Run the last two commands only after firstboot reports success. Alternatively,
reboot after the service completes; the normal graphical boot then proceeds.

On a minimal-memory system where no bundled chat model fits the configured
reserve, provisioning completes in reference-only mode and records that result
in `/var/lib/fieldos/model-selection.json`. A compatible bundled embedding
model is still smoke-tested independently. Systems with a selected chat model
must pass a local generation smoke test before firstboot completes.

Do not remove `/var/lib/fieldos` to force a retry: it contains user data and
persistent application state. A completed marker makes subsequent service
starts skip provisioning. Review the log and status after any retry.

## Health checks

Run the installed diagnostics script for hardware and provisioning summaries,
firstboot failure details, container state, and storage capacity:

```sh
sudo /opt/fieldos/scripts/fieldos-diagnostics.sh
```

The script prints only the last 40 firstboot journal lines and last 80 lines
from `/var/log/fieldos-firstboot.log`; it does not print the generated Compose
credentials. The log and nonsecret provisioning status are `root:adm` mode
`0640`, and `/var/lib/fieldos` is `root:adm` mode `0710`, allowing local admins
to read the status and log without listing persistent application data.
`/opt/fieldos/services/.env` remains `root:root` mode `0600`. Run the script
with `sudo` to access the full journal and container inspection. Review output
before sharing because it may contain local file paths and hardware
information.

Inspect service state and the local application health endpoint:

```sh
cd /opt/fieldos/services
sudo docker compose ps
curl --fail http://127.0.0.1:8080/api/health
```

The N.O.M.A.D. UI is at `http://localhost:8080`. Service ports bind to
loopback by default. Do not expose them to another network unless the operator
has explicitly configured and secured that access.

## Persistent data

Persistent application state is under `/var/lib/fieldos/`, including N.O.M.A.D.
storage, MySQL, Redis, Ollama model files, Qdrant, and Kiwix data. Provisioning
does not intentionally replace existing service data. Back up this directory
using an application-consistent procedure before storage maintenance or
reinstallation.

The global basemap and sample region are copied from the bundled payload into
`/var/lib/fieldos/storage/maps/pmtiles` and served by N.O.M.A.D.'s map service.
The test edition's sample region is a low-zoom United States extract; see
[offline content](OFFLINE-CONTENT.md) for coverage and attribution details.

## Backup and recovery

The following procedure makes a consistent backup of FieldOS application
state. Use an external drive with enough free space, formatted to preserve
Linux ownership and permissions. The archive includes `/opt/fieldos/services/.env`,
which contains live service credentials. Write it only to encrypted removable
storage, keep that storage physically secure, and do not attach the archive to
a support ticket or commit it to Git.

Stop the Compose services before copying databases and indexes. Replace the
example backup path with the mounted encrypted drive:

```sh
BACKUP=/media/fieldos-backup/fieldos-backup.tar
cd /opt/fieldos/services
sudo docker compose stop
sudo tar --numeric-owner --acls --xattrs -cpf "$BACKUP" \
  /var/lib/fieldos /opt/fieldos/services/.env
sync
sudo docker compose start
```

For recovery, install the same FieldOS version on a replacement disk and let
firstboot complete once. Connect the encrypted backup, stop the services, and
restore the archive as root. Use a matching Compose/image version because
database formats may change between releases:

```sh
cd /opt/fieldos/services
sudo docker compose stop
sudo tar --numeric-owner --same-owner --acls --xattrs -xpf \
  /media/fieldos-backup/fieldos-backup.tar -C /
sudo chown root:root /opt/fieldos/services/.env
sudo chmod 600 /opt/fieldos/services/.env
sudo docker compose up --detach --pull never
```

Do not erase or reformat the original disk until the restored machine has
passed the health, reference, model, and map checks in this guide. This backup
and restore procedure is documented but has not yet been exercised on a
physical FieldOS computer; test it on a spare system before relying on it for
field recovery.

## Offline behavior

The initial system is designed for operation without a network interface.
APT dependencies, container images, models, reference content, and map data
must already be present in the ISO payload. An operator may later choose to
connect temporarily to obtain updates or additional content, but that is not
part of firstboot or the offline acceptance test.
