# Release readiness and evidence

**Status: verified engineering test candidate; not approved for public binary distribution, emergency use, or medical use.**

## Current source and customer candidate

- Current repository revision: `605a631` (`main`, clean and pushed).
- Latest E2E tested source revision: `5720321b362c99fc7d86935c5e4bd1da9d91cb02`; `605a631` only updates documentation and preserves that evidence.
- Customer candidate source revision: `9c59a5f63cf6a2b35b7489a45cf53c0fc93d2f19` (the customer ISO below has not been rebuilt from current `main`).
- Customer-mode ISO candidate: `/mnt/shared/fieldos-releases/fieldos-customer-offline-9c59a5f.iso`
- Customer ISO SHA-256: `4e9800fc6facf698d2408579b42375e9d6fc31fbd38896ff2e68ada6d2654c74`
- Customer-mode validation: `/mnt/shared/fieldos-e2e/customer-offline-9c59a5f-20261105/validation.md`
- Current-source unattended E2E report: `/mnt/shared/fieldos-e2e/20261105T051319Z-2105879/report.md`
- Current-source test ISO SHA-256: `15b459ffbdc4540f3676785cfde0a9e854cada02c6fbd4a278dcec22c25d91da` (test harness removed the ISO after the run).
- Current-source offline payload: `/mnt/shared/fieldos-payload-5720321/offline-payload.tar.zst`, SHA-256 `4ebf8f18e838f686862f53da22112781077cca87d24177f2951a1d91a2ea6429`.
- Optional communications pack: `/mnt/shared/fieldos-content-packs/content-packs/us-household-communications-1.0.0.tar.zst`, SHA-256 `3f5e60f956a8604cb8ee4d08e37993191af745e9484d4d36aab7d2bb6b28c812`.

The customer-mode candidate completed interactive account and disk selection
and installed to the disposable UEFI VM's `vda` disk with no virtual NIC. The
installer reached Ubuntu's standard “Please remove the installation
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

The current-source E2E at `5720321` passed from a freshly rebuilt payload in a
no-NIC UEFI VM. It records offline installation and provisioning, local chat
and embeddings, Kiwix retrieval, safety refusal checks, all eight visible
Tennessee locations, container-egress blocking, and two reboot/persistence
cycles. The optional household communications archive was transferred from
read-only media, activated in the Source Library, indexed as three chunks, and
persisted through both reboots. The Source Library opened in Firefox. Its ISO
was test-only and removed after the run; this does not replace customer-mode
installer validation.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh unattended offline install | PASS | Tested source `5720321`; report and test ISO SHA-256 above. |
| Interactive customer install | PARTIAL | Interactive account and `vda` selection completed; at Ubuntu's media-removal prompt, ejecting the ISO and pressing Enter powered off the VM. A normal power-on booted the installed disk without repair. Physical USB behavior and automatic VM restart remain open. |
| Offline firstboot and services | PASS | Firstboot `complete`; seven containers returned after the second reboot. |
| Local chat and embeddings | PASS | Customer VM generated `FIELDOS_CUSTOMER_OK`, then `PERSISTENCE_OK` after reboot 1; embedding vector length 768. CPU path tested; physical GPU acceleration is unverified. |
| Kiwix and source retrieval | PASS, narrow collection | Customer VM searched and returned `The_New_York_Times`; nine local documents reached indexed state. The included English Wikipedia archive is a 100-article fixture, not a comprehensive library. |
| Tennessee maps | PASS in VMs | Customer Firefox visibly rendered Nashville; unattended E2E visibly rendered eight urban/rural locations. Map display is not routing or navigation; GPS is unverified. |
| Optional offline content-pack import | PASS in VM | `us-household-communications` transferred, checksum-verified, installed, shown in the Source Library, indexed, and persisted across two reboots; semantic retrieval query not tested. |
| Reboot persistence | PASS, two consecutive reboots | Provisioning marker, all seven containers, N.O.M.A.D., Kiwix, reference index, and no-default-route state persisted after each reboot; chat also generated after reboot 1. E2E passed two reboot cycles. |
| Network disconnected operation | PASS in VM | No virtual NIC, no guest physical interface, zero default routes. Docker internal bridges remain for local services. |
| Hardware adaptation | PARTIAL | CPU and fixture profiles tested. Physical hardware, GPU driver compatibility, and varied storage systems are unverified. |
| Network-connected security | PARTIAL | Disconnected operation and container egress blocking tested; LAN-connected peer exposure test remains open. Docker socket consumers retain powerful host access. |
| Field reference breadth | FAIL for broad field readiness | The optional household planner now passes guest install, index, Source Library, and reboot checks, but its semantic retrieval query is untested. The core library remains limited and Kiwix is a small fixture; broad medical, wildlife, outdoor, and technical coverage is incomplete. |
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
