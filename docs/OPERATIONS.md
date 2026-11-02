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

```sh
systemctl status fieldos-firstboot.service --no-pager
sudo cat /var/lib/fieldos/provisioning-status.json
sudo tail -n 150 /var/log/fieldos-firstboot.log
```

If it failed, the status file records the exit code and log location. Correct
the reported cause, then rerun the idempotent unit:

```sh
sudo systemctl reset-failed fieldos-firstboot.service
sudo systemctl start fieldos-firstboot.service
```

Do not remove `/var/lib/fieldos` to force a retry: it contains user data and
persistent application state. A completed marker makes subsequent service
starts skip provisioning. Review the log and status after any retry.

## Health checks

Run the installed diagnostics script for hardware and provisioning summaries:

```sh
sudo /opt/fieldos/scripts/fieldos-diagnostics.sh
```

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

## Offline behavior

The initial system is designed for operation without a network interface.
APT dependencies, container images, models, reference content, and map data
must already be present in the ISO payload. An operator may later choose to
connect temporarily to obtain updates or additional content, but that is not
part of firstboot or the offline acceptance test.
