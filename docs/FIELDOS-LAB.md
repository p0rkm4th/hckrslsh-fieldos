# FieldOS Lab operations

FieldOS Lab is a persistent, owner-only Kasm workspace for interactive testing.
It is separate from the disposable no-network E2E acceptance guest and from the
customer installer. The Lab currently runs the branded test-only installer
built from implementation revision
`8b0bda34f4dc3da993eed8663fffc15653d11679`.

## Deployment

The replacement guest is Proxmox VM 912 (`fieldos-lab`) on Alexandra, allocated
4 vCPU, 8 GiB RAM, and a 120 GiB virtual disk. The existing Kasm Server/RDP
workspace named **FieldOS Lab** points to the guest, with access retained through
the dedicated owner-only operator group. RDP credentials are prompted at
launch; credentials and private infrastructure addresses are intentionally
kept out of this public runbook. The desktop account password is held in the
local private operations record, not in Git or the Kasm definition.

The guest needs a management NIC for the Kasm connection. Its static management
configuration has no default route, DNS, or IPv6. The guest firewall defaults
to deny inbound, outbound, and routed traffic, permits RDP only from the Kasm
host, and allows the required container traffic on local Docker networks. Guest
application ports are not published to the management network. A denied
external request and the missing route were checked on the guest. The NIC is on
a shared hypervisor bridge, however, so this is not a dedicated VLAN or
layer-2-isolated network; a guest-to-guest LAN assessment remains outstanding.

The test-only installer used for the guest has SHA-256
`72e79196a7db55b64a5fbb0d7a3c6088e5e55112c29ae66f8c52feda64d3e3f5`. It is
not the customer ISO and does not validate its interactive installation path.

## Verification and limits

VM 912 completed provisioning and two consecutive reboots. Checks after each
reboot confirmed firstboot completion, seven running Compose services,
N.O.M.A.D. health response `{"status":"ok"}`, generated Ollama chat output,
a 768-value embedding response, Kiwix search retrieval, map-region registration,
and persistence of a guest marker. The guest had no default route or DNS and
could not reach an external HTTPS endpoint. Evidence, including the console
verification transcript, is stored outside Git under
`/mnt/shared/fieldos-lab/evidence/20261103/`.

A separate clean no-NIC E2E install from the same revision rendered the regional
map in Firefox and verified the branded desktop defaults. This proves the
current image's browser map path in that guest, not that map rendering has been
observed in the Kasm session.

**Owner-visible Kasm interaction with the replacement is not yet confirmed.**
The Kasm workspace configuration and host-to-guest RDP reachability are in
place, but successful launch, desktop rendering, and application interaction
must be verified in an authenticated owner browser session before calling the
replacement complete or retiring the rollback guest. The old VM 911 remains
stopped as rollback, with its prior snapshot intact. It shares the guest
management address; never start it while VM 912 is running.

The current guest includes test-sized reference and map fixtures. The sample
Wikipedia archive and low-zoom map are demonstrations, not a complete field
library or detailed regional map. Additional N.O.M.A.D. content still requires
separate acquisition. No physical GPU validation has been performed.

## Maintenance and recovery

The known-good offline snapshot on VM 912 is
`fieldos-lab-known-good-8b0bda3-20261103`. It was taken after provisioning and
the service and reboot checks. For a reset, stop VM 912, restore that snapshot
using the Proxmox UI or `qm rollback 912 fieldos-lab-known-good-8b0bda3-20261103`,
then start VM 912. Snapshot rollback discards changes made after the snapshot;
export any wanted test data first. Keep VM 911 and its rollback snapshot until
the owner confirms the replacement works through Kasm.

To recover the old guest, stop VM 912 first, then start VM 911. Both images use
the same intended management address, so they must not run simultaneously.
VM 912's complete config, private address, rotated desktop credential file path,
and recovery details are in the host-local, mode-restricted record under
`/home/scootz/.local/share/fieldos-lab/`. The credential itself is stored there
with mode `0600`; shared NTFS storage is not used for secrets because its mount
does not enforce Unix mode changes.

To rebuild instead of reset, run `make iso-test UBUNTU_ISO=/path/to/verified-ubuntu.iso`
and `make verify ISO=/mnt/shared/fieldos-releases/fieldos-test.iso`. The E2E
runner (`make test-e2e`) creates its unattended test image automatically. Install
to a new disposable Proxmox guest and repeat the offline service/reboot checks
before changing the Kasm target.
Never attach the lab management NIC to an untrusted network. Keep Kasm and
GNOME RDP credentials out of shell history, logs, screenshots, and Git.

## Current state

- VM 912: running replacement from source `8b0bda3`, services and two reboots
  verified, owner-visible Kasm launch pending.
- VM 911: stopped rollback from `c61b553`; retained pending owner confirmation.
- Kasm workspace: existing owner-only **FieldOS Lab** entry retained and
  pointed at the replacement guest.
- Customer interactive install: unverified separately; see
  [release status](RELEASE.md).
