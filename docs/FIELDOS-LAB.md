# FieldOS Lab operations

FieldOS Lab is the owner-only interactive staging workspace used to explore a
persistent FieldOS desktop. It is separate from disposable no-network
acceptance VMs and from the customer installer.

This repository is public. Deployment-specific host names, management addresses,
VM identifiers, snapshot names, account names, and credentials belong in the
operator's private infrastructure records, not here.

## Access boundary

Use a Kasm Server workspace connected to the FieldOS guest over a restricted
remote-desktop protocol. Assign it only to the dedicated owner access group.
Do not expose RDP/VNC, N.O.M.A.D., Ollama, or Kiwix to the public internet.

If the guest must remain offline, prefer a secured hypervisor console bridge.
If the deployment uses a management NIC, configure no default route or DNS,
deny outbound traffic, and permit only the Kasm host to reach the required
remote-desktop port. Keep application listeners on guest loopback. A shared
bridge with host firewall rules is not equivalent to layer-2 isolation; test
peer access before relying on that boundary. Keep remote access disabled on
customer installations unless an operator explicitly configures it.

Store the actual Kasm workspace name, guest endpoint, authorized account/group,
credential file location, hypervisor node, VM identifier, resource allocation,
and snapshot reference in private operator documentation. Do not put these
values in Git, build output, screenshots, or support logs.

## Verification

From the authorized Kasm account, verify that the workspace is visible and
launches, the desktop renders, and the FieldOS applications work in that
session. Check N.O.M.A.D., local inference, Kiwix content, and maps. A healthy
RDP port or running guest is not proof of a working authenticated desktop.

For network-enabled management, verify the guest has no general internet route,
only the intended management connection is reachable, and application/admin
ports are not accessible from the LAN. Record the test date and results in the
private operations record; publish only a sanitized summary.

## Snapshot, reset, and recovery

Keep one known-good snapshot while validating a replacement. Record its
hypervisor-specific reference privately. Before restore, confirm the guest is
stopped and the snapshot belongs to the intended FieldOS VM. A rollback discards
changes made after that snapshot.

Example Proxmox commands; replace placeholders only from the private operations
record and review the target before running them:

```sh
ssh <hypervisor-admin>@<hypervisor> 'qm status <VMID>'
ssh <hypervisor-admin>@<hypervisor> 'qm stop <VMID>'
ssh <hypervisor-admin>@<hypervisor> 'qm rollback <VMID> <known-good-snapshot>'
ssh <hypervisor-admin>@<hypervisor> 'qm start <VMID>'
```

To rebuild, create a new disposable guest, install a validated customer-mode
candidate, and complete offline service and desktop checks before changing the
Kasm workspace target. Keep the previous working guest and snapshot until the
owner confirms the replacement workspace launches and functions. Retire only
the specifically identified superseded guest after that confirmation.

Keep ISO files, VM disks, credentials, and operational evidence outside Git.
Use `make test-e2e` and `make verify` for release checks; a persistent lab guest
is interactive staging and is not a substitute for clean acceptance runs.
