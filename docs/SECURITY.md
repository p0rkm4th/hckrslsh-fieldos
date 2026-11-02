# Security boundaries

## Host and management access

`services/compose.yaml` grants the Project N.O.M.A.D. container access to
`/var/run/docker.sock`. A process with this socket can control the host Docker
daemon, including starting privileged containers and mounting host files. The
socket is required by the upstream N.O.M.A.D. container-management feature;
removing it would break that feature. Treat the N.O.M.A.D. interface as a local
host administrator interface and do not expose it to untrusted users.

Dozzle also receives the Docker socket so it can display container logs. Its
actions and shell are disabled. A read-only bind mount does not make Docker's
HTTP API read-only, so this is defense in depth, not a privilege boundary.
Removing Dozzle or replacing its socket access with a narrowly allow-listed
socket proxy would reduce exposure. A proxy is not currently included because
it adds another service and has not been shown necessary for the default
single-user field computer.

The Compose services do not request `privileged: true`, host networking, host
PID, or added Linux capabilities. They use Docker's default capability set;
future capability changes should be justified against upstream behavior and
tested. Persistent host paths are limited to `/var/lib/fieldos/storage`,
`mysql`, `redis`, and `qdrant`. Credentials are generated on first boot in the
root-owned Compose environment file and are not part of the ISO payload.

## Network exposure

Published HTTP ports bind to host loopback: N.O.M.A.D. `8080`, Kiwix `8090`,
Dozzle `9999`, Ollama `11434`, and Qdrant `6333`. MySQL and Redis are not
published to the host. The main Compose bridge is internal; the UI bridge has
IP masquerading disabled. Acceptance tests have verified no-NIC operation and
blocked external egress from the N.O.M.A.D. container. A separate guest test
with QEMU user-mode networking enabled confirmed that the guest received an
address, N.O.M.A.D. remained healthy, all five published ports were bound to
`127.0.0.1`, and the same ports refused connections on the guest's NIC address.
An outbound fetch from N.O.M.A.D. was blocked. This is not an inbound scan from
a separate LAN peer; that remains unverified because this workstation's
libvirt session cannot create a host bridge. Remote access is not configured.
Do not change loopback binds to `0.0.0.0` without adding an explicit
access-control and firewall plan.

## Operational checks

After installation, verify listeners with `sudo ss -lntp` and inspect actual
container settings with `sudo docker compose -f /opt/fieldos/services/compose.yaml
--project-directory /opt/fieldos/services config` and `sudo docker inspect`.
The Compose source and acceptance report should agree before a release. Keep
the generated `/etc/fieldos/services.env` readable only by root, and exclude
its contents, SSH keys, VM credentials, and private machine identifiers from
support bundles and Git history.

The firstboot-generated credentials are stored in `/opt/fieldos/services/.env`
with mode `0600` and root ownership. The N.O.M.A.D. Docker socket permission is
the one known privilege that cannot reasonably be removed while retaining its
upstream container-management feature. This is a single-user appliance
assumption, not a multi-user security boundary.
