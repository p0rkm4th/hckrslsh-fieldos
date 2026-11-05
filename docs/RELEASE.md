# Release readiness and evidence

**Status: interactive customer installation and VM feature checks passed; not approved for public binary distribution, emergency use, or medical use. Physical-device testing and redistribution clearance remain open.**

## Current source and customer candidate

- Repository revision before this documentation update: `aeeeadd98d8fd7fb11baabb770028647e96cf1fb`.
- Customer ISO source revision: `562fee9b93c53679f57fd25af49fd79fc61a2d95` (clean, embedded build manifest).
- Latest customer-mode build: `/mnt/shared/fieldos-releases/fieldos-customer-searchable-562fee9.iso`, SHA-256 `4d9ccf3f3e7d9b30bc0b0bf645303bb97e683a7eb79a9ffcd570edcbb2111ccfe`.
- Fresh interactive customer install: **PASS in a disposable VM**. The installer allowed selection of target `vda`, destructive-action confirmation, and local account setup; installation and media handoff completed, and the guest booted from the installed disk with the ISO detached. Firstboot completed offline; the branded desktop and apps worked; two consecutive guest reboots preserved user data and services. The initial apparent “disabled Next button/no target” report was a GUI interaction error; a correctly delivered click advanced the installer. Full evidence: `/mnt/shared/fieldos-e2e/customer-searchable-562fee9/validation.md`.
- VM limits: UEFI, 6 vCPU, 12 GiB RAM, 80 GiB disposable qcow2, no NIC. This does not validate physical USB firmware behavior or general physical hardware compatibility.
- Prior customer-mode candidate `ac319b3aa1c458295bd2672f7608f146870a2df8` remains preserved as historical baseline: `/mnt/shared/fieldos-releases/fieldos-customer-offline-ac319b3.iso`, SHA-256 `1d01fd5aedb7e408d856ab87c0e884202c5e78382ba75aab817ea9f84faa9432`; report: `/mnt/shared/fieldos-e2e/customer-ac319b3-20261105/validation.md`.
- Latest clean-source E2E tested source revision: `aeeeadd98d8fd7fb11baabb770028647e96cf1fb` (clean worktree at test time).
- Previous customer-mode candidate `fieldos-customer-offline-9c59a5f.iso` was retired after `ac319b3` passed; its SHA-256 sidecar and interactive install evidence remain. The binary retirement audit is `/mnt/shared/fieldos-releases/fieldos-artifact-retirement-20261105-customer-isos.txt`.
- Latest current-source unattended E2E report: `/mnt/shared/fieldos-e2e/20261105T120618Z-2754929/report.md` (installation, local services, eight Firefox map views, optional offline pack import, and two reboots passed).
- Three later GUI-import attempts on sources `41573f2`, `0d3a2b3`, and
  `ed21454` completed offline installation and rendered all eight Tennessee
  browser views, then failed the automated content-import gate before reboot
  checks. The harness had started the importer through QEMU Guest Agent instead
  of GNOME's logged-in session. On the `ed21454` guest, a manual desktop launch
  authenticated and installed the pack, but this was an intervened diagnostic,
  not a clean E2E PASS. The local harness correction now opens the existing
  launcher through GNOME search and needs a fresh no-NIC run. Reports remain in
  `/mnt/shared/fieldos-e2e/20261105T133000Z-2879177/`,
  `/mnt/shared/fieldos-e2e/20261105T140417Z-2934923/`, and
  `/mnt/shared/fieldos-e2e/20261105T142957Z-3004889/`.
- Test-only ISO SHA-256: `fdac92a70988cc975e8486ad5da27666123cacde1183dede1abf56c88467ab33` (removed by the harness after the run).
- Latest verified offline payload: `/mnt/shared/fieldos-payload-aeeeadd/offline-payload.tar.zst`, SHA-256 `f7bc22211c3e442c4ba56eb44ec8cce56bbd2c8a9e6d39af4e37b2dde12cd7e1` (6.6 GiB).
- Optional MedlinePlus pack archive: `/mnt/shared/fieldos-content-packs/content-packs/us-medlineplus-first-aid-2026.07.22.tar.zst`, SHA-256 `2670511092fb5796fef918a9468062bf24691b9ca3bee917f947046c17f94745`.
- Optional communications pack: `/mnt/shared/fieldos-content-packs/content-packs/us-household-communications-1.0.0.tar.zst`, SHA-256 `3f5e60f956a8604cb8ee4d08e37993191af745e9484d4d36aab7d2bb6b28c812`.

### Adaptive model update (CPU tested; semantic quality unresolved)

The source tree now pins Qwen3 1.7B Q4_K_M as the selected bundled CPU model, with the
0.6B model retained as fallback. A same-context CPU comparison is recorded at
`/mnt/shared/fieldos-model-eval-20261105/benchmark.json`. On the Tennessee
handbook date task, 1.7B returned the correct East/West spring and fall ranges
and refused two facts absent from the excerpt; 0.6B omitted the West dates in
the same focused check. The initial prompt showed that 1.7B can still format
answers poorly, and this test did not exercise N.O.M.A.D.'s retrieval or visible
citations. The earlier passing `ac319b3` customer ISO contains only 0.6B; the
current candidate contains both models. Its installed VM selected 1.7B on CPU
and returned `FIELDOS_CUSTOMER_BOOT_OK` after reboot 2. Semantic retrieval
quality remains unresolved as described below.

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
test-only evidence, not semantic AI grounding acceptance. The newer customer
ISO from `562fee9` has now separately passed interactive VM installation and
post-install validation; see the customer-install report above. The earlier
AI/RAG failure remains open.

An earlier `9c59a5f` customer candidate required a host power-on after the
media-removal prompt; that predecessor's handoff remains partial. The newer
`ac319b3` candidate below completed the virtual-media handoff and booted from
the installed disk without repair. Physical USB firmware behavior remains
untested.

The previous `ac319b3` customer ISO's interactive install remains useful historical evidence at `/mnt/shared/fieldos-e2e/customer-ac319b3-20261105/validation.md`. The newer `562fee9` candidate has since been tested independently; do not conflate the two builds. Its results are recorded in `/mnt/shared/fieldos-e2e/customer-searchable-562fee9/validation.md` and summarized below. Physical USB and general hardware behavior remain untested.

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

A previous current-source E2E at `82c7786` also passed in a fresh no-NIC UEFI VM
with the optional transfer-pack branch skipped. Its report, logs, screenshots,
and stopped guest disk remain in `/mnt/shared/fieldos-e2e/20261105T063912Z-2352718/`.

**Latest-source unattended acceptance (2026-11-05):** Clean revision
`aeeeadd98d8fd7fb11baabb770028647e96cf1fb` passed a fresh unattended install in
a no-NIC UEFI VM. All seven services started; Ollama generation, embeddings,
Kiwix, reference indexing, external container-egress blocking, and Firefox map
rendering at Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Jackson,
Johnson City, and Big South Fork passed. The optional MedlinePlus pack was
mounted from read-only transfer media, checksum-verified, added to the Source
Library, served at its local document path, and persisted through two reboots.
The test called the pack installer directly, so it does not validate the
separate graphical file-picker interaction. Evidence, including screenshots
and logs: `/mnt/shared/fieldos-e2e/20261105T120618Z-2754929/report.md`.
After this run, `make check` and all 85 unit tests passed on the updated
worktree; the catalog test explicitly includes the new optional pack.
The test-only ISO (SHA-256
`fdac92a70988cc975e8486ad5da27666123cacde1183dede1abf56c88467ab33`) was
removed after the run. This acceptance is separate from the interactive
customer-install test above.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh unattended offline install | PASS | Clean source `aeeeadd`; report and test ISO SHA-256 above. |
| Interactive customer install | PASS in disposable VM | Fresh 80 GiB no-NIC UEFI install from `562fee9`; target/user selection, erase confirmation, normal media handoff, installed-disk boot, and branded desktop verified. Physical USB behavior remains unverified. |
| Offline firstboot and services | PASS in customer VM | Firstboot status `complete`; all seven containers started. After two guest reboots, N.O.M.A.D. health returned `{"status":"ok"}` and services, references, maps, and user data persisted. Physical GPU acceleration is unverified. |
| Local chat and embeddings | PASS in customer VM; AI quality limited | Selected Qwen3 1.7B CPU model returned `FIELDOS_CUSTOMER_BOOT_OK` after reboot 2. Embeddings returned a nonempty 768-dimensional vector. N.O.M.A.D. chat returned `FIELDOS_NOMAD_OK`, but attached weather references to a generic phrase; grounded citations remain unreliable. |
| Kiwix and source retrieval | PASS for direct retrieval; limited library | Firefox opened a locally served New York Times article from the 100-article fixture. N.O.M.A.D. indexed all nine local reference documents (689 embedded chunks). The fixture is not comprehensive and AI semantic retrieval remains unreliable. |
| Offline Source Library search | PASS, limited formats | New guest rendered the Source Library; 16 files were listed. Five handbook text ranges and selected CDC companions are searchable up to the 1 MiB limit, with original PDFs linked. Guest check verified handbook dates/qualification in page text and no companion AI uploads; Node test verifies search matching/excerpts. This is source discovery, not verified semantic Q&A. |
| Tennessee maps | PASS in fresh test VM and customer VM | Eight customer-VM Firefox screenshots visibly rendered Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Jackson, Johnson City, and Big South Fork at zoom 13. Rural detail is sparse. Map display is not routing or navigation; GPS is unverified. |
| Optional offline content-pack import | PASS through installer; GUI flow not separately tested | `us-medlineplus-first-aid` transferred from read-only media, checksum-verified, installed, listed and linked in the Source Library, and persisted through two reboots in the current E2E. This pack is intentionally excluded from AI indexing. The graphical picker was not exercised in this run. Prior communications-pack semantic retrieval remains unreliable; see the supplemental report below. |
| New optional CDC preparedness pack | PASS in isolated VM | The 2013 CDC two-page checklist is item-recorded Public Domain and has a checksum-pinned 109,922-byte archive. A separate no-NIC copy-on-write guest imported it from read-only media; Firefox showed the Source Library entry and rendered the PDF, N.O.M.A.D. indexed one chunk, and both survived two reboots. It remains outside the ISO. Evidence and screenshots: `/mnt/shared/fieldos-e2e/20261105T051319Z-2105879/cdc-pack-20261105T140000Z/validation.md`. |
| Reboot persistence | PASS, two consecutive reboots | On the customer VM, boot ID changed twice. A user-created file (SHA-256 `4a4f0732febf6de0ed7a32c8ff76dd0de3607e59795649af0ad70235e68a8b07`), maps, references, firstboot completion, and all seven services persisted; N.O.M.A.D. health recovered after each boot and selected-model generation passed after reboot 2. The VM's initial libvirt `on_reboot=destroy` setting was corrected to `restart` before the counted cycles. |
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

FieldOS has a fresh customer-mode install from the `562fee9` ISO with local
assistant, embeddings, Kiwix, searchable references, and statewide Tennessee
maps, tested through two reboots in a no-NIC UEFI VM. The exact ISO and VM
evidence are listed above. Physical USB behavior and compatibility across
hardware remain untested. Kasm and Proxmox remain development tools, not
product requirements.

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
