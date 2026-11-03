# FieldOS Lab operations

FieldOS Lab is a persistent, owner-only Kasm workspace used for interactive
integration testing. It is separate from disposable E2E guests and from the
customer installer acceptance gate. It is built from the test-only unattended
installer and is not a customer release image.

## Current validated deployment

As of 2026-11-03, the lab VM was installed from source revision `c61b553` and
the test-only ISO whose SHA-256 is
`b245f6654cf84fedd86b2f14ca16b5414ca5e358cacec30d490ae5267d298339`. The
ISO is retained outside Git under the shared E2E test artifacts. The installed
VM has 4 vCPU, 8 GiB RAM, and a 120 GiB virtual disk. The exact hypervisor,
management addresses, VM identifier, and account identifiers are kept in the
private local operations record, not in this public repository.

The Kasm entry is named **FieldOS Lab** and is a **Server** workspace using an
RDP connection to the guest's GNOME Remote Desktop service. Kasm stores the
desktop credential in its server configuration; it is not published here.
Access is mapped to a dedicated operator group containing only the owner's
Kasm account. The workspace is not mapped to the default all-users group.
Kasm proxies the browser session; the guest does not expose its application
ports to Kasm users or the public network. RDP is configured for NLA
(CredSSP-over-TLS), with a locally generated certificate whose identity Kasm
is configured to ignore. Certificate validation is therefore not provided by
the current connection record.

The VM requires one management NIC for Kasm. This is not the no-NIC offline
acceptance configuration: the NIC is attached to the existing hypervisor
bridge. The guest has no default route or DNS, disables IPv6, and uses a
default-deny firewall for inbound, outbound, and routed traffic. DHCP is
allowed, and inbound RDP is allowed only from the Kasm host. This blocks
ordinary external access in the tested guest configuration, but a shared
bridge is not a separate VLAN or physical layer-2 isolation. A guest-to-guest
LAN scan has not been performed. Do not describe this lab as physically or
layer-2 isolated.

## Verification record

The installed system completed provisioning and remained functional through
two consecutive guest reboots. Checks against the running guest after each
reboot reported:

- Firstboot status `complete`; Docker and GNOME Remote Desktop active; seven
  Compose containers running.
- N.O.M.A.D. health endpoint returned `{"status":"ok"}`.
- Ollama generated `FIELDOS_LAB_REBOOT_OK` from bundled
  `qwen3:0.6b-q4_K_M`; the bundled `nomic-embed-text:v1.5` endpoint returned
  a 768-element embedding.
- Kiwix search for `New York` returned the bundled New York Times reference.
- The regional map API listed `fieldos-sample-us.pmtiles`; the style endpoint
  returned the world style, and the PMTiles range request returned HTTP 206
  with 127 bytes.
- The guest reported no IPv4 or IPv6 default route, no DNS server, and blocked
  external access. A desktop persistence marker survived both reboots.

These checks prove the map service and tile data are available, not that the
map rendered visibly in the Kasm browser. A diagnostic headless Firefox
capture at `/mnt/shared/fieldos-lab/evidence/20261103/map-headless.png` showed
the map page chrome with a blank canvas. The owner reached the guest login
screen through Kasm, but successful desktop login and visible map interaction
remain **PARTIAL / unverified**.
Earlier Firefox map rendering in a separate E2E guest is not evidence for this
Kasm session.

The current test ISO and VM disk are test artifacts. The VM disk remains on
the hypervisor; do not remove it during local artifact cleanup. A Proxmox
snapshot was created after the two-reboot checks:
`fieldos-lab-known-good-20261103`. The snapshot description records that map
browser rendering remains incomplete. The interactive customer installer
uses a different ISO path and has a separate handoff/release gate; this lab
does not satisfy that requirement.

The post-snapshot two-reboot transcript is retained at
`/mnt/shared/fieldos-lab/evidence/20261103/post-snapshot-two-reboots.txt`.
It records both changed boot IDs and the checks above after each reboot.

## Kasm RDP troubleshooting

On 2026-11-03, Kasm authorized the owner's session, but the guest logged
`HYBRID_REQUIRED_BY_SERVER` during RDP negotiation while the Kasm server
record was set to `security=tls`. GNOME Remote Desktop requires NLA for this
connection. The FieldOS Lab server record has been changed to `security=nla`;
an existing Kasm session may continue using its old connection settings, so
close that workspace session and launch it again. The guest desktop password
was later shortened at the owner's request and synchronized across the Linux
`labdesk` account, GNOME Remote Desktop, and Kasm's static server credential.
Read-back confirmed the Kasm record uses NLA/static credentials, the guest
account has a set password, and the RDP service is active. The Kasm website
password was not changed. Neither password is recorded in this document.

There are two sign-in stages: the Kasm server credential authenticates the
RDP connection; GNOME then presents its remote GDM greeter, where the operator
must sign in to guest account `labdesk` with the desktop password. The latest
retained diagnostic shows Guacamole selected NLA and GNOME sent its normal
server-redirection handoff. The guest still had a remote GDM greeter session
and no logged-in `labdesk` session at inspection; the handoff log also records
a transport close immediately afterward. The owner has seen the login screen,
but a stable post-login desktop is not yet verified. Diagnostic record:
`/mnt/shared/fieldos-lab/evidence/20261103/kasm-nla-greeter-check.txt`
(SHA-256 `b0c08f5978be942021c087d2a194fdcecdd6187aaf5b10ff92594e953285cb47`).
This two-stage flow is GNOME's documented [headless multi-user remote login
mode](https://github.com/GNOME/gnome-remote-desktop/blob/main/docs/configuration.md#headless-multi-user-remote-login).

If the issue returns, inspect the Kasm Guacamole log and the guest's
`gnome-remote-desktop.service` journal for `HYBRID_REQUIRED_BY_SERVER` or
`rdp_server_accept_nego`. Do not respond by resetting credentials unless the
logs show an authentication failure after successful security negotiation.
If the stream has closed, end the stale Kasm workspace session and launch
**FieldOS Lab** again; then enter `labdesk` and the desktop password at the
guest's GDM screen. Successful login and application interaction are still
awaiting confirmation.

## Launch and maintenance

1. Sign in to the existing Kasm deployment with the owner's account.
2. Select **FieldOS Lab** from the workspace catalog and launch it.
3. Use the desktop's **FieldOS** launcher to open N.O.M.A.D.; its local
   reference and map services are available from that interface.
4. The VM's application state is persistent across Kasm sessions and guest
   reboots. Keep test notes and disposable test datasets separate from release
   evidence.

The current VM allocation is 4 vCPU, 8 GiB RAM, and a 120 GiB virtual disk.
For routine checks, use the FieldOS diagnostics command and service checks in
[Operations](OPERATIONS.md). Do not run an installer against this persistent
VM disk. Use a disposable guest for installation or destructive tests.

## Snapshot and recovery

The known-good snapshot is
`fieldos-lab-known-good-20261103`. The exact VM identifier and hypervisor are
in the private local operations record. On the hypervisor, inspect snapshot
state with:

```sh
qm listsnapshot <FIELDOS_LAB_VMID>
qm config <FIELDOS_LAB_VMID>
```

Before restoring, save any user data created since the snapshot. Restore is
destructive to changes made after the snapshot. Stop the VM and explicitly
confirm the target snapshot before running:

```sh
qm shutdown <FIELDOS_LAB_VMID> --timeout 90
qm status <FIELDOS_LAB_VMID>
qm rollback <FIELDOS_LAB_VMID> fieldos-lab-known-good-20261103
qm start <FIELDOS_LAB_VMID>
qm status <FIELDOS_LAB_VMID>
```

Then repeat the health, inference, reference, map API, and network checks
above. This restores VM disk state; it does not restore Kasm database
configuration. Keep the owner-only group mapping and server record intact.

To rebuild, create a new disposable FieldOS VM from a validated installer,
complete offline installation and service checks, configure a restricted
management path, then update the Kasm Server workspace target. Do not overwrite
the existing VM or move the snapshot until the new VM has passed its own checks.

## Readiness limits

- The current lab image is test-only and unattended; it is not a customer ISO.
- The interactive customer install and media handoff remain separate release
  acceptance gates.
- The owner reached a graphical login screen, but successful desktop login
  and interaction with N.O.M.A.D., Kiwix, and rendered maps have not yet been
  confirmed; do not report those checks as PASS.
- The current management NIC shares a hypervisor bridge. The guest firewall
  restricts traffic, but a dedicated isolated bridge and peer-scan evidence
  are still needed for stronger isolation claims.
- The sample regional map is test content, not a complete customer map pack.
- No physical GPU validation has been performed.
