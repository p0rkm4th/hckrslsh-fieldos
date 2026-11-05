# Release readiness and evidence

**Status: verified engineering test candidate; not approved for public binary distribution, emergency use, or medical use.**

## Current source and customer candidate

- Source revision: `9c59a5f63cf6a2b35b7489a45cf53c0fc93d2f19` (`main`, clean and pushed before validation).
- Customer-mode ISO candidate: `/mnt/shared/fieldos-releases/fieldos-customer-offline-9c59a5f.iso`
- Customer ISO SHA-256: `4e9800fc6facf698d2408579b42375e9d6fc31fbd38896ff2e68ada6d2654c74`
- Customer-mode validation: `/mnt/shared/fieldos-e2e/customer-offline-9c59a5f-20261105/validation.md`
- Fresh unattended E2E report: `/mnt/shared/fieldos-e2e/20261105T031700Z-1734990/report.md`

The customer-mode candidate completed interactive account and disk selection
and installed to the disposable UEFI VM's `vda` disk with no virtual NIC. The
The installer reached Ubuntu's standard “Please remove the installation
medium, then press ENTER” prompt. In a fresh repeat run, the ISO was detached
at that prompt and Enter was pressed. The VM then powered off; a normal host
power-on booted the installed disk to GDM without repair. The user logged into
the branded GNOME desktop in the earlier candidate validation. This verifies
the installation and installed-disk boot, but the installer handoff remains
**PARTIAL** because the VM did not restart itself after the prompt. Physical USB
firmware behavior remains untested. Repeat handoff evidence:
`/mnt/shared/fieldos-e2e/customer-handoff-9c59a5f-20261105/validation.md`.

Firstboot reached `complete` at `2026-11-05T04:17:38Z`; all six bundled
reference packs activated, and N.O.M.A.D. indexed nine documents as 689 chunks.
All seven containers returned after two consecutive reboots. N.O.M.A.D. health,
Kiwix catalogue/search, and no-default-route checks passed after each reboot.
Before reboot, CPU chat generated `FIELDOS_CUSTOMER_OK`; after reboot 1 it
generated `PERSISTENCE_OK`. The embedding model returned a 768-dimensional
vector. Firefox visibly rendered Nashville streets, labels, parks, and
waterways at zoom 13 in the customer-mode install. Screenshot and diagnostics
are beside the customer validation report.

The clean-source unattended E2E at the same source commit also passed. Its
no-NIC report records offline installation and provisioning, local chat and
embeddings, indexed references, Kiwix retrieval, safety refusal checks,
eight visibly rendered Tennessee locations, container-egress blocking, and
two reboot/persistence cycles. It uses a separate test-only ISO and is not a
substitute for customer installer validation.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh unattended offline install | PASS | Same source revision; report and test ISO hash in the E2E report above. |
| Interactive customer install | PARTIAL | Interactive account and `vda` selection completed; at Ubuntu's media-removal prompt, ejecting the ISO and pressing Enter powered off the VM. A normal power-on booted the installed disk without repair. Physical USB behavior and automatic VM restart remain open. |
| Offline firstboot and services | PASS | Firstboot `complete`; seven containers returned after the second reboot. |
| Local chat and embeddings | PASS | Customer VM generated `FIELDOS_CUSTOMER_OK`, then `PERSISTENCE_OK` after reboot 1; embedding vector length 768. CPU path tested; physical GPU acceleration is unverified. |
| Kiwix and source retrieval | PASS, narrow collection | Customer VM searched and returned `The_New_York_Times`; nine local documents reached indexed state. The included English Wikipedia archive is a 100-article fixture, not a comprehensive library. |
| Tennessee maps | PASS in VMs | Customer Firefox visibly rendered Nashville; unattended E2E visibly rendered eight urban/rural locations. Map display is not routing or navigation; GPS is unverified. |
| Reboot persistence | PASS, two consecutive reboots | Provisioning marker, all seven containers, N.O.M.A.D., Kiwix, reference index, and no-default-route state persisted after each reboot; chat also generated after reboot 1. E2E passed two reboot cycles. |
| Network disconnected operation | PASS in VM | No virtual NIC, no guest physical interface, zero default routes. Docker internal bridges remain for local services. |
| Hardware adaptation | PARTIAL | CPU and fixture profiles tested. Physical hardware, GPU driver compatibility, and varied storage systems are unverified. |
| Network-connected security | PARTIAL | Disconnected operation and container egress blocking tested; LAN-connected peer exposure test remains open. Docker socket consumers retain powerful host access. |
| Field reference breadth | FAIL for broad field readiness | The optional household communications planner has a validated archive and host-side install/index result, but has not been tested in a running guest. The core library remains limited and Kiwix is a small fixture; broad medical, wildlife, outdoor, and technical coverage is incomplete. |
| Redistribution review | BLOCKED | Exact Ubuntu, software, model, maps, and content license/attribution review is incomplete. Keep candidate binaries unpublished. |
| Physical customer readiness | BLOCKED | Physical installation/hardware, LAN exposure, content breadth, and rights review remain. |

## Current offline capabilities

FieldOS provides a local assistant and embeddings, Kiwix, a small source
library, and an offline statewide Tennessee map viewer. The customer-mode
installer has been installed interactively in a no-NIC UEFI VM and tested
through two reboots; its media handoff still needs a clean hands-off test. Kasm
and Proxmox remain development tools, not product requirements.

The local model is not an authority for emergency or medical decisions. It
fails closed for configured safety-sensitive categories. The bundled sources
remain limited; open original documents and follow current official guidance.
The map is a geographic reference, not turn-by-turn navigation. GPS and routing
are unverified. See [`FIELD-USE-ASSESSMENT.md`](FIELD-USE-ASSESSMENT.md) and
[`CONTENT-PACKS.md`](CONTENT-PACKS.md).

## Security, licensing, and release hygiene

The tested guest had no network adapter. This confirms disconnected operation,
not safe behavior on a LAN. Complete a connected-peer exposure review before
recommending networked use. Upstream N.O.M.A.D. components with Docker socket
access have powerful host administration permissions.

The ISO remains unpublished engineering test material. Complete redistribution
and attribution review, including Ubuntu image/trademark requirements, before
publishing binaries. Do not put ISO files, model weights, container archives,
VM disks, credentials, or generated private keys in public Git.
