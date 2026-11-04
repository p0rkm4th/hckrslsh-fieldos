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

### Guest-side route and firewall checks

On a guest that uses a management interface, IPv6 router advertisements can
install a default route even when IPv4 has none. Disable route acceptance
persistently for the management interface, its default template, and the
system-wide setting (substitute the guest's interface name):

```ini
# /etc/sysctl.d/90-fieldos-kasm-isolation.conf
net.ipv6.conf.all.accept_ra=0
net.ipv6.conf.default.accept_ra=0
net.ipv6.conf.<management-interface>.accept_ra=0
# Optional when the management path does not require IPv6:
net.ipv6.conf.<management-interface>.disable_ipv6=1
```

Apply the settings, remove any already installed IPv6 default route, and check
both route families, DNS configuration, and the firewall after reboot:

```sh
sudo sysctl --system
sudo ip -6 route del default   # only if one exists
ip -4 route show default
ip -6 route show default
resolvectl status
sudo ufw status verbose
```

The management firewall should allow the required desktop port only from the
Kasm host, deny other incoming connections, and deny general outbound/routed
traffic. Test from the Kasm node that the desktop port is reachable while
FieldOS application ports are blocked. A guest firewall on a shared bridge is
still not layer-2 isolation; keep that limitation explicit and prefer a
dedicated isolated bridge or secured console tunnel when available.

On 2026-11-04, a live check of the existing lab guest found an IPv6 default
route learned by router advertisement. Persistent RA acceptance was disabled
on the guest, its IPv6 management address was disabled, and the route was
removed. Afterward, the guest had no IPv4 or IPv6 default route and no global
IPv6 address on its management interface; UFW denied incoming, outgoing, and
routed traffic by default, with RDP allowed only from the Kasm node and local
Docker bridge exceptions. A connection check from the Kasm node reached RDP
and was blocked on the FieldOS UI, Kiwix, logs, Ollama, and Qdrant ports. This
hardens the existing lab guest but does not establish layer-2 isolation or
verify the replacement desktop through an authenticated Kasm session.

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
