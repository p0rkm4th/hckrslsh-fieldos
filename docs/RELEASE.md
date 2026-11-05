# Release readiness and evidence

**Status: verified engineering test candidate; not approved for public binary distribution, emergency use, or medical use.**

## Current source and customer candidate

- Current source revision: `c85efcd2243bf27a7f0978ef4c5ecddceeca4bdb` (`main`; this is a release-status documentation-only follow-up).
- Latest clean-source E2E tested source revision: `82c7786c8086fe0f7d8aa3855cdd304de3be95c8` (clean worktree at test time).
- Customer candidate source revision: `9c59a5f63cf6a2b35b7489a45cf53c0fc93d2f19` (the customer ISO below has not been rebuilt from current `main`).
- Customer-mode ISO candidate: `/mnt/shared/fieldos-releases/fieldos-customer-offline-9c59a5f.iso`
- Customer ISO SHA-256: `4e9800fc6facf698d2408579b42375e9d6fc31fbd38896ff2e68ada6d2654c74`
- Customer-mode validation: `/mnt/shared/fieldos-e2e/customer-offline-9c59a5f-20261105/validation.md`
- Current-source unattended E2E report: `/mnt/shared/fieldos-e2e/20261105T063912Z-2352718/report.md`
- Current-source test ISO SHA-256: `339989c4224b0bc9735e8eaf7349d9a7a4caba6e27d224bf894c462081b99aa7` (test harness removed the ISO after the run).
- Current-source offline payload: `/mnt/shared/fieldos-payload-29ff87b/offline-payload.tar.zst`, SHA-256 `41194c0e16015c10ed41d6b49cc9fb12684ebf39882a1878a188b3d7a33f18d9`; payload verification passed against current pack and map manifests.
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

The current-source E2E at `82c7786` passed in a fresh no-NIC UEFI VM using the
verified 5.7 GB payload above. It records unattended installation and complete
firstboot provisioning, seven services, local CPU chat, embeddings, Kiwix
catalogue/search, source indexing and AI safety refusals, eight actual Firefox
map screenshots, container-egress blocking, and two reboot/persistence cycles.
The installed Source Library page visibly rendered its offline search field and
nine-document inventory. Unit tests exercise the generated search JavaScript
for matching, excerpts, and empty results. The optional transfer-pack branch
was skipped in this run; the household communications and CDC packs each have
separate no-NIC transfer/index/browser/reboot evidence. The test-only ISO was
removed after the run, while its report, logs, screenshots, and stopped guest
disk remain in `/mnt/shared/fieldos-e2e/20261105T063912Z-2352718/`. This does not
replace customer-mode installer validation.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh unattended offline install | PASS | Clean source `82c7786`; report and test ISO SHA-256 above. |
| Interactive customer install | PARTIAL | Interactive account and `vda` selection completed; at Ubuntu's media-removal prompt, ejecting the ISO and pressing Enter powered off the VM. A normal power-on booted the installed disk without repair. Physical USB behavior and automatic VM restart remain open. |
| Offline firstboot and services | PASS | Firstboot `complete`; seven containers returned after the second reboot. |
| Local chat and embeddings | PASS | Customer VM generated `FIELDOS_CUSTOMER_OK`, then `PERSISTENCE_OK` after reboot 1; embedding vector length 768. CPU path tested; physical GPU acceleration is unverified. |
| Kiwix and source retrieval | PASS, narrow collection | Customer VM searched and returned `The_New_York_Times`; nine local documents reached indexed state. The included English Wikipedia archive is a 100-article fixture, not a comprehensive library. |
| Offline Source Library search | PASS, limited formats | Current-source guest rendered search and nine-document inventory; Node-backed test verifies matching and excerpts. Plain text up to 1 MiB is searchable on the page; PDFs and larger documents require browser Find. This is source discovery, not verified semantic Q&A. |
| Tennessee maps | PASS in VMs | Customer Firefox visibly rendered Nashville; unattended E2E visibly rendered eight urban/rural locations. Map display is not routing or navigation; GPS is unverified. |
| Optional offline content-pack import | PASS in VM; semantic retrieval FAIL | `us-household-communications` transferred, checksum-verified, installed, shown in the Source Library, indexed, and persisted across two reboots. A later isolated query test cited the planner but failed to extract its clearly printed primary-contact fields; see the supplemental report below. |
| New optional CDC preparedness pack | PASS in isolated VM | The 2013 CDC two-page checklist is item-recorded Public Domain and has a checksum-pinned 109,922-byte archive. A separate no-NIC copy-on-write guest imported it from read-only media; Firefox showed the Source Library entry and rendered the PDF, N.O.M.A.D. indexed one chunk, and both survived two reboots. It remains outside the ISO. Evidence and screenshots: `/mnt/shared/fieldos-e2e/20261105T051319Z-2105879/cdc-pack-20261105T140000Z/validation.md`. |
| Reboot persistence | PASS, two consecutive reboots | Provisioning marker, all seven containers, N.O.M.A.D., Kiwix, reference index, and no-default-route state persisted after each reboot; chat also generated after reboot 1. E2E passed two reboot cycles. |
| Network disconnected operation | PASS in VM | No virtual NIC, no guest physical interface, zero default routes. Docker internal bridges remain for local services. |
| Hardware adaptation | PARTIAL | CPU and fixture profiles tested. Physical hardware, GPU driver compatibility, and varied storage systems are unverified. |
| Network-connected security | PARTIAL | Disconnected operation and container egress blocking tested; LAN-connected peer exposure test remains open. Docker socket consumers retain powerful host access. |
| Field reference breadth | FAIL for broad field readiness | The optional household planner is directly readable offline, but the small model did not answer two direct questions about its indexed content. The core library remains limited and Kiwix is a small fixture; broad medical, wildlife, outdoor, and technical coverage is incomplete. |
| Redistribution review | BLOCKED | Exact Ubuntu, software, model, maps, and content license/attribution review is incomplete. Keep candidate binaries unpublished. |
| Physical customer readiness | BLOCKED | Physical installation/hardware, LAN exposure, content breadth, and rights review remain. |

### Supplemental semantic retrieval check

After the accepted `5720321` E2E, a disposable copy-on-write clone of that
no-NIC VM was used to check whether N.O.M.A.D. could answer two direct
questions about the optional household communications planner. Both answers
failed to extract the requested contact fields despite listing the planner
among their sources. This is a retrieval/answer-quality failure; indexing and
installation still pass. In the clone's Firefox session, the installed
planner document itself opened from the local Source Library document route
and visibly rendered its blank name, phone/contact, and city/state fields.
That confirms direct source access, not successful in-app search or reliable
AI retrieval. The original acceptance disk was not modified. Full observations
and artifact paths: `/mnt/shared/fieldos-e2e/20261105T051319Z-2105879/semantic-retrieval-report.md`.

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
