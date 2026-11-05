# Release readiness and evidence

**Status: verified engineering test candidate; not approved for public binary distribution, emergency use, or medical use.**

## Current source and customer candidate

- Customer ISO build source revision: `ac319b3aa1c458295bd2672f7608f146870a2df8`.
- Latest clean-source E2E tested source revision: `82c7786c8086fe0f7d8aa3855cdd304de3be95c8` (clean worktree at test time).
- Latest customer candidate source revision: `ac319b3aa1c458295bd2672f7608f146870a2df8`.
- Latest customer-mode ISO candidate: `/mnt/shared/fieldos-releases/fieldos-customer-offline-ac319b3.iso`
- Latest customer ISO SHA-256: `1d01fd5aedb7e408d856ab87c0e884202c5e78382ba75aab817ea9f84faa9432`
- Structural verification: PASS (`make verify`); fresh interactive UEFI VM installation, firstboot, services, and two reboots: PASS. The guest continued after the test detached the virtual ISO at Ubuntu's media-removal prompt and pressed Enter. Physical USB behavior remains unverified. Evidence: `/mnt/shared/fieldos-e2e/customer-ac319b3-20261105/validation.md`.
- Previous customer-mode candidate `fieldos-customer-offline-9c59a5f.iso` was retired after `ac319b3` passed; its SHA-256 sidecar and interactive install evidence remain. The binary retirement audit is `/mnt/shared/fieldos-releases/fieldos-artifact-retirement-20261105-customer-isos.txt`.
- Current-source unattended E2E report: `/mnt/shared/fieldos-e2e/20261105T063912Z-2352718/report.md`
- Current-source test ISO SHA-256: `339989c4224b0bc9735e8eaf7349d9a7a4caba6e27d224bf894c462081b99aa7` (test harness removed the ISO after the run).
- Current-source offline payload: `/mnt/shared/fieldos-payload-29ff87b/offline-payload.tar.zst`, SHA-256 `41194c0e16015c10ed41d6b49cc9fb12684ebf39882a1878a188b3d7a33f18d9`; payload verification passed against current pack and map manifests.
- Optional communications pack: `/mnt/shared/fieldos-content-packs/content-packs/us-household-communications-1.0.0.tar.zst`, SHA-256 `3f5e60f956a8604cb8ee4d08e37993191af745e9484d4d36aab7d2bb6b28c812`.

### Pending hardware-adaptive model update

The source tree now pins Qwen3 1.7B Q4_K_M as a bundled candidate, with the
0.6B model retained as fallback. A same-context CPU comparison is recorded at
`/mnt/shared/fieldos-model-eval-20261105/benchmark.json`. On the Tennessee
handbook date task, 1.7B returned the correct East/West spring and fall ranges
and refused two facts absent from the excerpt; 0.6B omitted the West dates in
the same focused check. The initial prompt showed that 1.7B can still format
answers poorly, and this test did not exercise N.O.M.A.D.'s retrieval, visible
citations, the selected VM profile, or a FieldOS installation. The current ISO
above still contains only 0.6B. The updated model payload and clean no-NIC E2E
must pass before this model can be described as accepted in FieldOS.

**Update (2026-11-05):** The exact `adc8551` source passed a clean no-NIC
automated E2E at `/mnt/shared/fieldos-e2e/qwen17-model-20261105/20261105T091345Z-2568109/report.md`.
The 6.6 GiB offline payload is
`/mnt/shared/fieldos-payload-qwen17-20261105/offline-payload.tar.zst`, SHA-256
`d29645ff8f4b8d2aaf30c498fc8b517ac5bf00c514a706aa6906911be481c430`.
Installation, CPU inference smoke, embeddings, Kiwix, statewide map views, and
two reboots passed. A post-run real N.O.M.A.D. query against the selected
1.7B model failed semantic grounding: it returned incorrect tomato dates and
the Qdrant top matches were unrelated crop passages. The automated PASS is
operational only. Do not use AI as a trusted answer source. This source has
not yet produced a replacement customer-mode ISO.

**Searchable-source update (2026-11-05):** Source
`dc6d823bd8427c9193588e5460c28a7e4b20aad8` passed `make check`, 85 unit tests,
payload verification, and a new clean-source no-NIC E2E. Report:
`/mnt/shared/fieldos-e2e/searchable-sidecars-20261105/20261105T095217Z-2608514/report.md`.
The test ISO SHA-256 was `77a7408739d302f312ea2a16e1beb875469bb1a55936c149715d55733681ea25`
(temporary ISO removed after test); payload SHA-256 is
`b8f798477aae21468d86afd4d44df9cbf1d8cbc16463e358d5fc98aac0787403`. All eight
Tennessee Firefox screenshots are saved beside the report and visibly show
the map. Two reboots passed. A post-run guest check confirmed five handbook
text ranges installed; the Source Library page contains the tomato date rows
and frost-free-date qualification, and no searchable companion was uploaded
to N.O.M.A.D. The optional content-transfer branch was skipped. This is
test-only evidence, not a rebuilt customer-mode ISO or semantic AI grounding
acceptance. The earlier AI/RAG failure remains open.

An earlier `9c59a5f` customer candidate required a host power-on after the
media-removal prompt; that predecessor's handoff remains partial. The newer
`ac319b3` candidate below completed the virtual-media handoff and booted from
the installed disk without repair. Physical USB firmware behavior remains
untested.

The customer ISO from `ac319b3` was installed interactively to the disposable no-NIC 80 GiB UEFI VM. The user selected `vda`, created a local account, reviewed the install plan, and reached Ubuntu's installation-complete screen. The virtual ISO was ejected at the normal media-removal prompt; after Enter, the guest booted from the installed disk to GDM without repair or a host power cycle. Firstboot reached `complete`, loaded the CPU model and embeddings, indexed nine reference documents, and started all seven containers. The user logged into the FieldOS-branded desktop and used N.O.M.A.D., Kiwix, and maps in Firefox. Two consecutive reboots retained the services, model files, map packs, and reference files. Eight Tennessee locations visibly rendered in the actual browser. The exact installer selection, completion, handoff, service output, and screenshots are in `/mnt/shared/fieldos-e2e/customer-ac319b3-20261105/validation.md` and adjacent files. This verifies the VM installation flow; physical USB and hardware behavior remain untested.

The same customer VM exposed an AI retrieval quality failure: the local
assistant's streamed answer to a tomato question invented planting dates and
mixed in snap-bean instructions despite retrieving the 2026 Vegetable Crop
Handbook. The response completed in 18.34 seconds with 428 completion tokens;
the stream ended normally and sent the handbook source title in its final
`sources` event. The captured Firefox view showed no visible citation, and the
answer contradicted itself by later saying the context lacked the requested
details. Treat semantic answer quality and user-visible attribution as
unresolved; direct source access works, but the model must not be treated as an
authoritative field reference. The API stream evidence is summarized in the
customer validation report.

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
| Interactive customer install | PASS in UEFI VM | `ac319b3` installed interactively to disposable `vda`, booted from disk after virtual media ejection, and reached the branded desktop. Physical USB behavior remains unverified. Evidence: `/mnt/shared/fieldos-e2e/customer-ac319b3-20261105/validation.md`. |
| Offline firstboot and services | PASS | Firstboot `complete`; seven containers returned after the second reboot. |
| Local chat and embeddings | PASS for the current ISO | Customer VM generated `FIELDOS_CUSTOMER_OK`, then `PERSISTENCE_OK` after reboot 1; embedding vector length 768. CPU path tested; physical GPU acceleration is unverified. The source-tree 1.7B candidate awaits a rebuilt offline installation test. |
| Kiwix and source retrieval | PASS for direct source access; AI semantic answer PARTIAL | Customer Firefox opened the New York Times article from the 100-article fixture; all nine local documents reached indexed state. A crop-handbook chat returned unrelated snap-bean instructions without visible citations. The fixture is not a comprehensive library. |
| Offline Source Library search | PASS, limited formats | Current-source guest rendered search and nine-document inventory; Node-backed test verifies matching and excerpts. Plain text up to 1 MiB is searchable on the page; PDFs and larger documents require browser Find. This is source discovery, not verified semantic Q&A. |
| Tennessee maps | PASS in customer VM | Firefox visibly rendered Nashville, Memphis, Knoxville, Chattanooga, Clarksville, Jackson, Johnson City, and rural West Tennessee from the regional archive. Map display is not routing or navigation; GPS is unverified. |
| Optional offline content-pack import | PASS in VM; semantic retrieval FAIL | `us-household-communications` transferred, checksum-verified, installed, shown in the Source Library, indexed, and persisted across two reboots. A later isolated query test cited the planner but failed to extract its clearly printed primary-contact fields; see the supplemental report below. |
| New optional CDC preparedness pack | PASS in isolated VM | The 2013 CDC two-page checklist is item-recorded Public Domain and has a checksum-pinned 109,922-byte archive. A separate no-NIC copy-on-write guest imported it from read-only media; Firefox showed the Source Library entry and rendered the PDF, N.O.M.A.D. indexed one chunk, and both survived two reboots. It remains outside the ISO. Evidence and screenshots: `/mnt/shared/fieldos-e2e/20261105T051319Z-2105879/cdc-pack-20261105T140000Z/validation.md`. |
| Reboot persistence | PASS, two consecutive reboots | Provisioning marker, all seven containers, N.O.M.A.D., Kiwix, reference index, and no-default-route state persisted after each reboot; chat also generated after reboot 1. E2E passed two reboot cycles. |
| Network disconnected operation | PASS in VM | No virtual NIC, no guest physical interface, zero default routes. Docker internal bridges remain for local services. |
| Hardware adaptation | PARTIAL | CPU and fixture profiles tested. Physical hardware, GPU driver compatibility, and varied storage systems are unverified. |
| Network-connected security | PARTIAL | Disconnected operation and container egress blocking tested; LAN-connected peer exposure test remains open. Docker socket consumers retain powerful host access. |
| Field reference breadth and grounded AI answers | FAIL for broad field readiness | The installed 0.6B model failed questions about indexed content. An isolated same-context 1.7B model check improved exact handbook extraction but does not verify N.O.M.A.D. retrieval or user-visible citations. Kiwix is a small fixture; broad medical, wildlife, outdoor, and technical coverage is incomplete. |
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

FieldOS provides a local assistant and embeddings, Kiwix, a small searchable
source library, and an offline statewide Tennessee map viewer. The current
customer-mode ISO has been installed interactively in a no-NIC UEFI VM and
tested through two reboots. The virtual-media handoff completed after the ISO
was ejected and Enter pressed; physical USB behavior remains untested. Kasm and
Proxmox remain development tools, not product requirements.

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
