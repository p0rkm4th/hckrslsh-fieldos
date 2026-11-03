# FieldOS Lab operations

FieldOS Lab is a persistent, owner-only Kasm Server workspace for interactive
testing. It is separate from disposable no-network acceptance VMs and from the
customer installer. The existing Kasm workspace and its dedicated owner-only
FieldOS Lab Operators group are retained.

## Active deployment

The active staging guest is Proxmox VM 913 (`fieldos-lab-d9d459b`) on
Alexandra. It has 4 vCPU, 8 GiB RAM, a 120 GiB virtual disk, UEFI boot, and
autostarts. It runs a customer-mode test installation built from source
`d9d459b`; this is a test candidate, not an approved customer release. The
existing **FieldOS Lab** Kasm Server/RDP entry uses the guest's private
management address on TCP 3389. Its owner-only access group was retained.
Kasm prompts for the guest RDP credentials and opens the `fieldos` desktop
account. The rotated guest/RDP password is a lowercase, hyphen-separated
five-word passphrase for easier manual entry. It is kept in the host-local,
mode-0600 operations file, not in this repository. It is unique to the guest
and is not the Kasm website password. See [credential guidance](SECURITY.md).

The guest's management NIC is on the existing hypervisor bridge. It has no
default route, DNS, or IPv6. Guest UFW defaults to deny inbound, outbound, and
routed traffic, with RDP allowed only from the Kasm host. Application ports
remain bound to guest loopback and are not reachable from Kasm. Compose's
service network is internal, and the local UI bridge has IP masquerading
disabled. Kasm-to-RDP and blocked application-port connections were checked.
External access from the guest has no route. This is host firewall filtering
on a shared bridge, not a dedicated VLAN; peer isolation on the bridge remains
unverified. Do not attach this management interface to an untrusted network.

## Verification and limits

VM 913 completed firstboot. All seven Compose services were running;
N.O.M.A.D. returned `{"status":"ok"}`; Ollama generated a response; the
embedding model returned 768 values; Kiwix served its catalog; and the bundled
map endpoint returned tile data. The guest has no default route or DNS. RDP
port 3389 is reachable from the Kasm host, while application ports 8080,
11434, 8090, 6333, and 9999 are blocked there. The source customer-mode
installation passed service, inference, reference, map, and two-reboot checks
after the installer powered off at its media-removal prompt and the host
started the installed disk. The automatic installer handoff is still a
customer-release blocker.

The new guest's actual authenticated desktop launch from an owner's Kasm
browser has **not** been observed with this tooling. Kasm entry, guest RDP
listener, and network reachability are configured and checked, but workspace
launch, rendered desktop, and in-session application interaction remain
PARTIAL until an owner session verifies them. The old VM 912 remains stopped
as the rollback deployment and must not be removed until that confirmation.

The guest contains test-sized reference and low-zoom map fixtures. The optional
Middle Tennessee zoom-13 pack was tested separately in the no-NIC acceptance
VM, but is not installed in this lab guest or bundled in the ISO. No
comprehensive medical, emergency, agricultural, or survival library is
claimed. Physical GPU validation has not been performed.

Evidence:

- No-NIC E2E report: `/mnt/shared/fieldos-e2e/20261103T194719Z-2651472/report.md`.
- Customer install and staging evidence:
  `/mnt/shared/fieldos-e2e/customer-interactive-d9d459b-20261103/report.md`.
- Customer candidate SHA-256:
  `4e41822852d9e911f186ab1f3659a904eedddef48154c9ca6d955cd2de7ddcd2`.

## Snapshot, reset, and recovery

VM 913's known-good staging snapshot is
`fieldos-lab-known-good-d9d459b-20261103`. It preserves the firstboot-complete
state and lab configuration; VM 913's service, inference, reference, map, and
network checks were run before snapshotting. To restore it, which discards
changes made after the snapshot:

```sh
ssh root@192.168.10.2 'qm stop 913'
ssh root@192.168.10.2 'qm rollback 913 fieldos-lab-known-good-d9d459b-20261103'
ssh root@192.168.10.2 'qm start 913'
```

The previous Lab VM 912 is stopped and retains its snapshot
`fieldos-lab-known-good-8b0bda3-20261103`. To recover it, stop VM 913 first,
then start VM 912. Both use the same intended management address; never run
them simultaneously. Keep VM 912 and its snapshot until the replacement is
confirmed usable from the owner's Kasm browser. Older VM 911 remains stopped
as a separate legacy rollback and is not part of the current workspace.

For a newer build, create a new disposable guest, install and validate it, then
change the Kasm Server workspace target only after the new guest is ready.
Keep test evidence and release artifacts under `/mnt/shared`; do not store
credentials, ISO binaries, or VM disks in Git. Use the repository's
`make test-e2e` and `make verify` instructions for acceptance and ISO checks.

## Current state

- VM 913: active staged guest, source `d9d459b`, snapshot above; guest checks
  passed, owner-authenticated Kasm launch pending.
- VM 912: stopped previous Lab and rollback snapshot retained.
- VM 911: stopped legacy rollback, unchanged.
- Kasm: existing owner-only **FieldOS Lab** Server/RDP entry and dedicated
  access group retained; it uses the replacement guest's management endpoint.
- Customer installer: partial; interactive disk/account selection and installed
  system checks passed, but automatic handoff powered the VM off at the media
  prompt. See [release readiness](RELEASE.md).
