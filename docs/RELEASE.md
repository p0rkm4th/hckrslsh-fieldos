# Release readiness and evidence

**Status: verified engineering test candidate; not approved for public binary distribution, emergency use, or medical use.**

## Current source and customer candidate

- Source revision: `1851e3491d6f7e28d53b73a6e02239d2ff681121` (`main`, clean and pushed).
- Customer-mode ISO: `/mnt/shared/fieldos-releases/fieldos-customer-offline-1851e34.iso`
- Customer ISO SHA-256: `9d43df4be724a9937eb931347279660226976d1a6914c235fcba9244e418a4a6`
- Customer-mode acceptance report: `/mnt/shared/fieldos-e2e/customer-offline-1851e34/report.md`
- Fresh unattended E2E report: `/mnt/shared/fieldos-e2e/20261105T010513Z-1550530/report.md`

The customer-mode candidate completed an interactive account and disk-selection
installation to a disposable UEFI VM with no virtual NIC. After installation,
the virtual ISO was ejected at Ubuntu's standard media-removal prompt and the
system booted from its installed disk. This confirms the virtual-disk handoff;
physical USB firmware behavior remains untested. The test user logged into the
branded GNOME desktop and completed the first-login welcome flow.

Firstboot reached `complete`. After two consecutive reboots, the account and a
user-owned persistence sentinel remained, all seven N.O.M.A.D. containers
returned, and the local APIs still worked. After the second reboot, N.O.M.A.D.
health returned `ok`; CPU chat generated `FIELDOS_REBOOT2_OK`; the embedding
model returned a 768-dimensional vector; Kiwix search returned a local article;
and N.O.M.A.D. exposed a nonempty zoom-13 Tennessee tile. Firefox visibly
rendered Nashville street, park, and waterway detail in the customer-mode
install. Screenshots and diagnostics are beside the customer report.

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
| Interactive customer install | PASS in disposable UEFI VM | Account and `vda` selected interactively; normal media-removal prompt handled by ejecting the test ISO; installed disk booted. Physical USB test remains open. |
| Offline firstboot and services | PASS | Firstboot `complete`; seven containers returned after the second reboot. |
| Local chat and embeddings | PASS | Customer VM after reboot 2: `FIELDOS_REBOOT2_OK`; embedding vector length 768. CPU path tested; physical GPU acceleration is unverified. |
| Kiwix and source retrieval | PASS, narrow collection | Browser search displayed a bundled local result. The included English Wikipedia archive is a 100-article fixture, not a comprehensive library. |
| Tennessee maps | PASS in VMs | Customer Firefox visibly rendered Nashville; unattended E2E visibly rendered eight urban/rural locations. Map display is not routing or navigation; GPS is unverified. |
| Reboot persistence | PASS, two consecutive reboots | Customer account and test sentinel persisted; APIs, containers, chat, embeddings, Kiwix, and map tile passed after reboot 2. E2E also passed two reboot cycles. |
| Network disconnected operation | PASS in VM | No virtual NIC, no guest physical interface, zero default routes. Docker internal bridges remain for local services. |
| Hardware adaptation | PARTIAL | CPU and fixture profiles tested. Physical hardware, GPU driver compatibility, and varied storage systems are unverified. |
| Network-connected security | PARTIAL | Disconnected operation and container egress blocking tested; LAN-connected peer exposure test remains open. Docker socket consumers retain powerful host access. |
| Field reference breadth | FAIL for broad field readiness | Core library remains limited and Kiwix is a small fixture. Optional packs are available; broad agriculture, medical, wildlife, and technical coverage is incomplete. |
| Redistribution review | BLOCKED | Exact Ubuntu, software, model, maps, and content license/attribution review is incomplete. Keep candidate binaries unpublished. |
| Physical customer readiness | BLOCKED | Physical installation/hardware, LAN exposure, content breadth, and rights review remain. |

## Current offline capabilities

FieldOS provides a local assistant and embeddings, Kiwix, a small source
library, and an offline statewide Tennessee map viewer. The customer-mode
installer has now been installed interactively in a no-NIC UEFI VM and tested
through two reboots. Kasm and Proxmox remain development tools, not product
requirements.

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
