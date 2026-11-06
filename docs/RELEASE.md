# Release readiness and evidence

The tested installer source revision is `aedc5705915d4ff57bad18e535b602eace7310b8`, clean at build. Subsequent public repository changes only update documentation and acceptance evidence; installer/runtime code is unchanged. `make check test` passed 127 tests; all 12 content-pack manifests validated.

**Current private customer-mode engineering candidate:**
`/mnt/shared/fieldos-releases/fieldos-customer-test-aedc570.iso`
SHA-256: `538ad22a3f024a173196bd9d18953b4a16c492cecc2338bf90d0bd028cccfab6`
Payload SHA-256:
`a257d4e4113254411b56e072fe301d35cb90dc4e6dceb2e002fdfb0f6d720614` (6.6 GiB).
The embedded manifest is clean and pins the source revision, Ubuntu ISO, and
payload checksum. Structural verification passed. A fresh interactive customer
install passed in a disposable no-NIC UEFI VM; firstboot completed; the branded
desktop, actual local CPU inference and embeddings, Kiwix article, indexed
references, and visible zoom-13 Nashville map worked. Two reboots preserved
services and a local data marker. Evidence:
`/mnt/shared/fieldos-e2e/customer-aedc570-interactive/customer-acceptance.md`.
At Ubuntu's standard remove-media prompt, Enter powered the guest off after the
virtual CD had been ejected; a normal power-on with only the installed disk
booted without repair. Physical USB handoff is untested.

The fresh unattended no-NIC E2E separately passed all eight Tennessee browser
map renders, local AI and reference checks, container egress blocking, and two
reboots. Its report is
`/mnt/shared/fieldos-e2e/current-31a244c/20261106T111141Z-909878/report.md`.
The test ISO was built before documentation-only corrections were committed as
`aedc570`; runtime and installer code did not change. Its optional pack
transfer test was skipped. The customer-mode and unattended tests are distinct.

**Not release approved.** This is a private engineering candidate, not a
redistribution-cleared customer release. Wikipedia 100 and the ten indexed
source documents are limited. Physical hardware/USB, GPU/GPS, and
attached-network security behavior remain unverified; final redistribution
review is incomplete. Do not publish the ISO as a customer release until these
gates pass.

## Earlier customer ISO acceptance: `cc4aa38`

- Source revision: `cc4aa38f3debd078b877589355221e94821bd160` (`main`, clean at test start).
- Customer ISO: `/mnt/shared/fieldos-releases/fieldos-customer-cc4aa38.iso`.
- SHA-256: `0319a069a4874d0522f660c6d69027e6ab9c4aaf86f2f8c995efb9d359a1e139`.
- `make check test`: PASS, 87 unit tests; 10 content-pack manifests validated.
- `make verify ISO=...`: PASS; BIOS/UEFI boot records, customer setup, offline APT, and payload presence verified.
- Follow-up source change: the Southeastern vegetable handbook attribution was corrected from the official publisher record, which names seven authors and permits public use/reprint/citation with author and institutional credit. Pack version `2026.1.1` and portable archive `/mnt/shared/fieldos-content-packs/content-packs/us-southeastern-vegetable-growers-2026.1.1.tar.zst` now carry that metadata (SHA-256 `67ba6be8136afcdfbe14642675520369fc04b8f5a44bbf39d36da31a69a175a9`). The current ISO above predates this source update and still contains the older `2026.1` manifest; build and validate a successor ISO before claiming the corrected attribution is present in the installer.
- Interactive UEFI install to a disposable 80 GiB disk: target and identity were selected and destructive install confirmed. Ubuntu reached “Please remove the installation medium, then press ENTER”; the guest tray was open. Enter caused a normal shutdown; ordinary `virsh start` booted installed `vda` with no ISO source. No reset or repair was used. Interactive installation and installed-disk boot pass in this VM; automatic restart and physical USB handoff remain unverified.
- Post-install operations: all seven services started; selected CPU model generated text after reboot 2; 768-dimensional embeddings returned; nine reference documents/689 chunks indexed; Firefox Source Library search returned three flood-related documents; Kiwix article search succeeded; Firefox visibly rendered zoom-13 maps at Nashville in the clean retest and all eight Tennessee test locations in a separate installation of the exact same ISO checksum; two reboots preserved a user-data marker, map bytes, services, inference, embeddings, and Kiwix search.
- N.O.M.A.D. answer quality remains limited: local chat attached a source but did not answer a soil-pH query from it. A separate harmless UI prompt received an overbroad refusal and irrelevant weather references. Direct reference access is more reliable than model answers.
- Full current report and evidence: [`VALIDATION-CURRENT.md`](VALIDATION-CURRENT.md), `/mnt/shared/fieldos-e2e/customer-cc4aa38-handoff-20261105/`, and the same-checksum statewide map run `/mnt/shared/fieldos-e2e/customer-cc4aa38-20261105/`.
- Remaining gates: physical USB and hardware tests, connected-network exposure review, useful broad content, semantic quality, and redistribution clearance.

This current snapshot supersedes status claims in the revision-specific historical records below.

## Historical source changes after the `cc4aa38` ISO

Pushed source revision `bd719c8` includes the map-style patch linking
OpenStreetMap contributors, Protomaps, and the ODbL; a full pinned MIT notice
for Tangrams-derived sprites; pinned PMTiles CLI, container, source, and
extraction metadata; and eight core content packs. The PMTiles CLI version is
1.30.2. The source catalog now promotes the CDC emergency-kit checklist and
MedlinePlus first-aid overview. This does not change the accepted `cc4aa38` ISO
listed above.

A new payload was built from that source at
`/mnt/shared/fieldos-payload/offline-payload.tar.zst` (6.56 GiB), SHA-256
`a02a94515c463a21797b8f0718dd939fbd8567a56fbdaeecdd8ec31c86c875e8`.
`zstd -t`, `build/verify_payload.py`, and an independent read-only inventory
check passed. The archive contains all eight declared core packs; its
Tennessee PMTiles file matches the pinned 145,267,908-byte source checksum and
zoom 0–13 metadata. Attribution links and the ODbL/Tangrams notices are in the
archive. The archive itself has no source-commit marker; its checksum is bound
to the ISO through the ISO build manifest. The map's visible attribution still
needs browser verification.

The first interactive successor ISO composition from `bd719c8` wrote
`fieldos-customer-bd719c8.iso`, then failed `build/verify-iso.sh` because the
Start Here guide called the bundled 2023 NIOSH item a “heat-illness reference”
without the verifier's “first-aid” descriptor. The source guide now uses the
accurate phrase “NIOSH heat-illness first-aid reference”; the verifier was not
relaxed. All 96 unit tests and source checks pass after the correction. That
failed ISO is not accepted evidence; rebuild from the corrected, committed
source before running customer installation acceptance. The precise failed
attempt and cleanup are recorded in
`/mnt/shared/fieldos-e2e/payload-build-20261105-bd719c8.md`.

The exact artwork revision behind the modified sprites remains unresolved.
Physical USB insertion/navigation is also unverified; prior content-pack import
testing used read-only optical media.

## Historical source-specific acceptance records (prior revisions)

- Prior E2E source revision recorded here: `8c9870ba6994cf3bdb78c769cccf8e3b3290f2fe` (clean worktree during E2E; report below).
- Customer ISO source revision: `562fee9b93c53679f57fd25af49fd79fc61a2d95` (clean, embedded build manifest).
- Prior customer-mode build recorded here: `/mnt/shared/fieldos-releases/fieldos-customer-searchable-562fee9.iso`, SHA-256 `4d9ccf3f3e7d9b30bc0b7f645303bb97e683a7eb79a9ffcd570edcbb2111ccfe`.
- Fresh interactive customer install: **PASS in a disposable VM**. The installer allowed selection of target `vda`, destructive-action confirmation, and local account setup; installation and media handoff completed, and the guest booted from the installed disk with the ISO detached. Firstboot completed offline; the branded desktop and apps worked; two consecutive guest reboots preserved user data and services. The initial apparent “disabled Next button/no target” report was a GUI interaction error; a correctly delivered click advanced the installer. Full evidence: `/mnt/shared/fieldos-e2e/customer-searchable-562fee9/validation.md`.
- VM limits: UEFI, 6 vCPU, 12 GiB RAM, 80 GiB disposable qcow2, no NIC. This does not validate physical USB firmware behavior or general physical hardware compatibility.
- Prior customer-mode candidate `ac319b3aa1c458295bd2672f7608f146870a2df8` remains preserved as historical baseline: `/mnt/shared/fieldos-releases/fieldos-customer-offline-ac319b3.iso`, SHA-256 `1d01fd5aedb7e408d856ab87c0e884202c5e78382ba75aab817ea9f84faa9432`; report: `/mnt/shared/fieldos-e2e/customer-ac319b3-20261105/validation.md`.
- Prior clean-source unattended E2E: source `8c9870ba6994cf3bdb78c769cccf8e3b3290f2fe`; test ISO SHA-256 `6824a8ab41da257bfa4a98661aaf4ce2a332315111f8577802bf5d4f8eb7c10b`; report `/mnt/shared/fieldos-e2e/20261105T155548Z-3200639/report.md`. The fresh no-NIC install passed provisioning, local inference and embeddings, Kiwix, source indexing, container egress blocking, eight Firefox map views, GUI pack import and attribution checks, and two reboot cycles.
- Previous customer-mode candidate `fieldos-customer-offline-9c59a5f.iso` was retired after `ac319b3` passed; its SHA-256 sidecar and interactive install evidence remain. The binary retirement audit is `/mnt/shared/fieldos-releases/fieldos-artifact-retirement-20261105-customer-isos.txt`.
- These E2E reports are historical evidence; the current customer-mode result is recorded above and in `VALIDATION-CURRENT.md`.
- Four later GUI-import attempts on sources `41573f2`, `0d3a2b3`, `ed21454`,
  and `327488c` completed offline installation and rendered all eight Tennessee
  browser views, then failed the automated content-import gate before reboot
  checks. The harness had started the importer through QEMU Guest Agent instead
  of GNOME's logged-in session. On the `ed21454` guest, a manual desktop launch
  authenticated and installed the pack, but this was an intervened diagnostic,
  not a clean E2E PASS. The `327488c` run launched via GNOME search, authenticated,
  showed the success dialog, and verified the imported pack files and checksums;
  it then failed because the verifier expected command output from the GUI
  process. The current harness relies on Source Library and file-integrity
  checks instead. The correction passed a fresh no-NIC run on `8c9870b` (report
  above). Earlier failed reports remain in
  `/mnt/shared/fieldos-e2e/20261105T133000Z-2879177/`,
  `/mnt/shared/fieldos-e2e/20261105T140417Z-2934923/`, and
  `/mnt/shared/fieldos-e2e/20261105T142957Z-3004889/`, and
  `/mnt/shared/fieldos-e2e/20261105T152842Z-3096889/`.
- Test-only ISO SHA-256: `fdac92a70988cc975e8486ad5da27666123cacde1183dede1abf56c88467ab33` (removed by the harness after the run).
- Offline payload used by that prior E2E: `/mnt/shared/fieldos-payload-aeeeadd/offline-payload.tar.zst`, SHA-256 `f7bc22211c3e442c4ba56eb44ec8cce56bbd2c8a9e6d39af4e37b2dde12cd7e1` (6.6 GiB).
- Optional MedlinePlus pack archive: `/mnt/shared/fieldos-content-packs/content-packs/us-medlineplus-first-aid-2026.07.22.tar.zst`, SHA-256 `2670511092fb5796fef918a9468062bf24691b9ca3bee917f947046c17f94745`.
- Historical optional communications archive: `/mnt/shared/fieldos-content-packs/content-packs/us-household-communications-1.0.0.tar.zst`, SHA-256 `3f5e60f956a8604cb8ee4d08e37993191af745e9484d4d36aab7d2bb6b28c812`. Its internal checksum is valid, but its manifest metadata is stale (`weather-disaster` / `authoritative-reference`) and does not match the current tracked manifest. Do not transfer it. The current-manifest archive used for the manual GUI add-on check is retained in the customer run directory and has SHA-256 `114e846643edf5b4d196bc0e6ef4e33167e90e494efba84c2ed90ddea43ded63`.

### Historical adaptive model update (CPU tested; semantic quality unresolved)

That source tree pinned Qwen3 1.7B Q4_K_M as the selected bundled CPU model, with the
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

**Historical clean-source unattended acceptance (2026-11-05):** Clean revision
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

## Historical acceptance matrix (prior revisions; see latest result above)

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh unattended offline install | PASS | Clean source `aeeeadd`; report and test ISO SHA-256 above. |
| Interactive customer install | PASS in disposable VM | Fresh 80 GiB no-NIC UEFI install from `562fee9`; target/user selection, erase confirmation, normal media handoff, installed-disk boot, and branded desktop verified. Physical USB behavior remains unverified. |
| Offline firstboot and services | PASS in customer VM | Firstboot status `complete`; all seven containers started. After two guest reboots, N.O.M.A.D. health returned `{"status":"ok"}` and services, references, maps, and user data persisted. Physical GPU acceleration is unverified. |
| Local chat and embeddings | PASS in customer VM; AI quality limited | Selected Qwen3 1.7B CPU model returned `FIELDOS_CUSTOMER_BOOT_OK` after reboot 2. Embeddings returned a nonempty 768-dimensional vector. N.O.M.A.D. chat returned `FIELDOS_NOMAD_OK`, but attached weather references to a generic phrase; grounded citations remain unreliable. |
| Kiwix and source retrieval | PASS for direct retrieval; limited library | Firefox opened a locally served New York Times article from the 100-article fixture. N.O.M.A.D. indexed all nine local reference documents (689 embedded chunks). The fixture is not comprehensive and AI semantic retrieval remains unreliable. |
| Offline Source Library search | PASS, limited formats | New guest rendered the Source Library; 16 files were listed. Five handbook text ranges and selected CDC companions are searchable up to the 1 MiB limit, with original PDFs linked. Guest check verified handbook dates/qualification in page text and no companion AI uploads; Node test verifies search matching/excerpts. This is source discovery, not verified semantic Q&A. |
| Tennessee maps | PASS in current test VM and earlier customer VM | Eight current-source Firefox screenshots visibly rendered Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Jackson, Johnson City, and Big South Fork at zoom 13. Rural detail is sparse. Map display is not routing or navigation; GPS is unverified. |
| Optional offline content-pack import | PASS through GNOME GUI installer | `us-medlineplus-first-aid` transferred from read-only media, authenticated through the desktop flow, checksum-verified, installed, indexed, listed and linked in the Source Library, and persisted through two reboots. This pack is intentionally excluded from AI indexing. Prior communications-pack semantic retrieval remains unreliable; see the supplemental report below. |
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

## Historical offline capabilities (older candidate)

The current `cc4aa38` customer-mode candidate has been installed in a no-NIC
UEFI VM. The installer reached the standard media-removal prompt and shut down
cleanly after Enter; an ordinary VM power-on booted the installed disk without
reset or repair. Local AI generation, embeddings, Kiwix, the Tennessee map,
Source Library, and branded Command Center were exercised after installation;
two guest reboots preserved services and data. This validates the interactive
install and disk boot in this VM profile. Seamless automatic restart, physical
USB behavior, and compatibility across hardware remain untested. Kasm and
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
