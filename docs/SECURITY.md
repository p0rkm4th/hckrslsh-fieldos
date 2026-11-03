# Security boundaries

## Host and management access

`services/compose.yaml` grants the Project N.O.M.A.D. container access to
`/var/run/docker.sock`. A process with this socket can control the host Docker
daemon, including starting privileged containers and mounting host files. The
socket is required by the upstream N.O.M.A.D. container-management feature;
removing it would break that feature. Treat the N.O.M.A.D. interface as a local
host administrator interface and do not expose it to untrusted users.
Upstream documents the Docker-outside-of-Docker management design and includes
the socket bind in its pinned management Compose template:
[v1.35.1 FAQ](https://github.com/Crosstalk-Solutions/project-nomad/blob/v1.35.1/FAQ.md),
[v1.35.1 management Compose](https://github.com/Crosstalk-Solutions/project-nomad/blob/v1.35.1/install/management_compose.yaml).

Dozzle also receives the Docker socket so it can display container logs. Its
actions and shell are disabled. A read-only bind mount does not make Docker's
HTTP API read-only, so this is defense in depth, not a privilege boundary.
Removing Dozzle or replacing its socket access with a narrowly allow-listed
socket proxy would reduce exposure. A proxy is not currently included because
it adds another service and has not been shown necessary for the default
single-user field computer. Upstream marks Dozzle optional and says its
Service Logs & Metrics link will not work if Dozzle is omitted; see the
[pinned v1.35.1 Compose template](https://github.com/Crosstalk-Solutions/project-nomad/blob/v1.35.1/install/management_compose.yaml).

The Compose services do not request `privileged: true`, host networking, host
PID, or added Linux capabilities. They use Docker's default capability set;
future capability changes should be justified against upstream behavior and
tested. Kiwix receives the reference directory read-only: the admin service
retains the writable `/app/storage` mount required to manage content, while
the serving container needs to read it only. Persistent host paths are limited to `/var/lib/fieldos/storage`,
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
libvirt session cannot create a host bridge. Remote access is not configured
in the customer FieldOS installation. The separate owner-only Kasm staging VM
uses a management NIC and GNOME Remote Desktop behind Kasm; its RDP and
firewall settings are documented in [`FIELDOS-LAB.md`](FIELDOS-LAB.md). That
staging exception is not enabled by the customer installer and is not a
layer-2 isolated network.
Do not change loopback binds to `0.0.0.0` without adding an explicit
access-control and firewall plan. Detailed retained evidence for the user-mode
network test is `/mnt/shared/fieldos-e2e/customer-correct-entry-20261102/`
(`security-network-report.md` and `security-network-check.txt`). Its SLIRP
network did not expose the guest to a LAN peer, so the customer-LAN gate remains
partial.

## Operational checks

After installation, verify listeners with `sudo ss -lntp` and inspect actual
container settings with `sudo docker compose -f /opt/fieldos/services/compose.yaml
--project-directory /opt/fieldos/services config` and `sudo docker inspect`.
The Compose source and acceptance report should agree before a release. Keep
the generated `/opt/fieldos/services/.env` readable only by root, and exclude
its contents, SSH keys, VM credentials, and private machine identifiers from
support bundles and Git history.

The firstboot-generated credentials are stored in `/opt/fieldos/services/.env`
with mode `0600` and root ownership. The N.O.M.A.D. Docker socket permission is
the one known privilege that cannot reasonably be removed while retaining its
upstream container-management feature. This is a single-user appliance
assumption, not a multi-user security boundary.

The runtime inspection from the offline, no-NIC acceptance guest is retained
at `/mnt/shared/fieldos-e2e/security-runtime-20261102.txt`. It confirmed no
container used `privileged`, `cap_add`, host PID, or host networking; all five
published application ports bound to `127.0.0.1`; the generated `.env` was
`0600 root:root`; and only N.O.M.A.D. and Dozzle mounted the Docker socket.
Dozzle's bind was read-only, which does not itself restrict Docker API methods.
The Kiwix content mount was tested read-only on that disposable guest. Kiwix
search and N.O.M.A.D. health continued to work, and the guest was restored to
its original mount after the experiment. Evidence:
`/mnt/shared/fieldos-e2e/kiwix-readonly-experiment-20261102.md`. New automated
acceptance runs also assert Kiwix's `/data` mount is read-only. A separate
guest-to-guest LAN reachability scan remains pending.

The automated E2E harness now checks these host-side container boundaries on
the installed guest: no privileged mode, added capabilities, host networking,
or host PID namespace; only N.O.M.A.D. and Dozzle mount the Docker socket;
Dozzle's socket mount remains read-only; every published port binds to
`127.0.0.1`; and the generated Compose credential file remains `0600 root:root`.
The source check was syntax-validated and the repository unit suite passed. A
read-only execution of the same assertions against the existing accepted E2E
guest passed: seven containers, only N.O.M.A.D. and Dozzle using the Docker
socket, loopback-only published ports, and root-only credentials. Evidence is
`/mnt/shared/fieldos-e2e/security-runtime-followup-20261103.txt`. This does not
replace a fresh current-source E2E run or a guest-to-guest LAN scan.

The current Compose source was also rendered with synthetic credentials using
`docker compose config` and checked for service count, published-port bindings,
privileged mode, added capabilities, and Docker socket consumers. It rendered
seven services; all five published ports bind to `127.0.0.1`, no service is
privileged or requests added capabilities, and only N.O.M.A.D. and Dozzle
mount the Docker socket (Dozzle's mount is marked read-only). The retained
source-level result is
`/mnt/shared/fieldos-e2e/compose-source-security-607a697.json`. This does not
inspect a running current-source deployment or prove isolation from a LAN
peer.

The Compose configuration was rendered and rechecked again at source commit
`0436069e99f972f25ae424597fa00d7337de9c60`. The seven services remained
unprivileged with no added capabilities; all five host ports bound to
`127.0.0.1`; and only N.O.M.A.D. and Dozzle mounted the Docker socket. The
Dozzle mount is marked read-only, which does not constrain Docker API methods.
Ephemeral synthetic credentials were supplied only to the command environment
and are absent from the saved result. Evidence:
`/mnt/shared/fieldos-e2e/compose-source-security-0436069.json` (SHA-256
`2c8331bcaf29930a381769ca3299ee4c9b78d63432495a0a7bb75a8b0f450d41`). This
is a source configuration check, not a fresh installation or LAN peer test.

## Live runtime recheck — 2026-11-03

After two additional reboots of the retained no-NIC guest from the 10:23 E2E
run, runtime inspection again found no privileged containers, added
capabilities, host PID/network namespaces, or non-loopback published ports.
Only N.O.M.A.D. and Dozzle mounted the Docker socket; Dozzle's mount was
read-only. The root-owned `.env` was `0600`, Kiwix `/data` remained read-only,
and a container egress attempt failed. The installed Compose file's SHA-256
matched current `services/compose.yaml` at
`d7ddb44c832263ff98f491a0f4aeebf84cfb2360d4eaca10ec0feb74773c09c3`.
Evidence is `/mnt/shared/fieldos-e2e/live-security-102308.txt` (SHA-256
`5c44f34eac4ae9b1de60896cc9794833c7a352d50dec6461dfd4748225ec7839`). This
was a no-NIC guest, so it does not replace the earlier user-mode-network test
or a guest-to-guest LAN scan, and it is not a fresh current-source installation.

## Temporary network-enabled check — 2026-11-03

A QEMU user-mode SLIRP NIC was temporarily hot-plugged into the same existing
installed guest; it received `10.0.2.15/24` and a default route, and the guest
could reach `https://example.com` (HTTP 200). N.O.M.A.D. remained healthy.
Connections to all five published service ports (`8080`, `8090`, `9999`,
`11434`, `6333`) were refused on the guest NIC address, while an egress
attempt from N.O.M.A.D. was blocked. The temporary NIC was removed; QMP
reported it absent, libvirt showed no interface, the guest had no external
link/default route, and N.O.M.A.D. plus all seven containers remained running.
The installed Compose file hash matched current source. Evidence:
`/mnt/shared/fieldos-e2e/network-enabled-live-102308.txt` (SHA-256
`71432edc42a786cc9b1a6d0a0aaa6d8e619a0f487cebbec622b86249f025ffdc`) and
`/mnt/shared/fieldos-e2e/network-detach-live-102308.txt` (SHA-256
`6d2b529f73c90cce058668994b3e123c98ada20b1ec22d349542831728acf53e`). This
uses QEMU user networking, not a physical LAN or guest-to-guest peer scan; it
is also not a fresh install of current source.
