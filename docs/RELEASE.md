# Release status and process

FieldOS has passed unattended offline acceptance and separate interactive R4
and R5 installations in disposable QEMU/KVM guests. R5's installation,
firstboot, services, local inference, reference retrieval, map endpoints, and
two reboots passed. Both R4 and R5 powered off after the remove-media prompt
and required a host start to boot the installed target; automatic interactive
restart remains a release blocker. FieldOS is not yet
recommended for physical customer installation. A LAN peer scan, physical GPU
validation, Canonical's modified Ubuntu trademark requirement, and exact
third-party redistribution review remain open. Do not publish release binaries.

## Acceptance evidence

### Current-source R5 interactive installation — 2026-11-03

- Candidate ISO: `/mnt/shared/fieldos-releases/fieldos-test-customer-r5.iso`;
  SHA-256 `8b121916cd13af315d268cae16643eab06244a5b3a256662767650cbf2b52ee2`.
  `make verify` confirmed ISO structure, BIOS/UEFI boot records, installer
  configuration, and bundled payload. Extracted NoCloud data contains
  `shutdown: reboot` and keeps identity/storage interactive.
- Fresh 80 GiB UEFI QEMU guest, no network adapter. The installer review
  identified only disposable target `vda`; interactive user and disk setup
  completed. Firstboot reached `status=complete`; all seven Compose services
  ran; N.O.M.A.D. health returned `{"status":"ok"}`; Qwen generated
  `FIELDOS_R5_OK`; embeddings returned 768 values; Kiwix retrieved the bundled
  New York article; the regional map API listed the U.S. PMTiles pack and the
  world PMTiles archive returned a 66,795-byte tile. No default route existed.
- Two in-guest reboots changed the boot ID. After each, all seven containers,
  N.O.M.A.D. health, and local inference recovered; `.env`, bundled ZIM, and
  regional map SHA-256 values were unchanged. See `service-checks.txt` and
  `reboot-checks.txt` in `/mnt/shared/fieldos-e2e/customer-r5-20261103/`.
- Handoff remains PARTIAL: “Restart now” reached the remove-media prompt;
  after the medium was absent and Enter was pressed, the VM powered off despite
  the explicit reboot setting. A host start booted the installed target to
  GDM. This is an interrupted handoff and is not a clean automated installer
  PASS. R5's map was checked at the service/API layer; the actual browser render
  evidence remains the R4 Firefox screenshot below.
- Test screenshots and reports are retained under
  `/mnt/shared/fieldos-e2e/customer-r5-20261103/`. The test account password
  was generated temporarily and was not saved in the evidence directory.

### Modular content-pack validation — 2026-11-03

- Added a standard-library validator for staged pack manifests, source IDs,
  artifact path containment, exact sizes and SHA-256 values, geography bounds,
  and emergency-reference review metadata. `make check` runs it against the
  repository catalog; fixture tests also reject bad hashes, traversal paths,
  undeclared sources, and unreviewed emergency packs.
- `make check`, `make validate-content-packs`, and all 28 unit tests passed.
  The catalog remains intentionally empty; no customer pack data or new runtime
  dependencies were added.

### Current-source unattended acceptance — 2026-11-03

- Run report: `/mnt/shared/fieldos-e2e/20261103T002115Z-2083709/report.md`.
- Source: commit `945751325ab80b1acadb870f0754f3fc7a378fab`, clean worktree.
  Test ISO SHA-256: `78c96f8d37fe6d08804de62d0fd8c69dd01801e0e1a0382e6ea9493b1a2174e1`.
- A fresh 80 GiB UEFI qcow2 installed unattended with no virtual NIC. Offline
  provisioning completed; all seven containers ran; N.O.M.A.D. returned
  `{"status":"ok"}`; Qwen generated `FIELDOS_ACCEPTANCE_OK`; the embedding
  endpoint returned a vector; Kiwix retrieved the bundled New York article;
  and the world plus bundled U.S. regional PMTiles were served. Firefox
  rendered the regional map over the offline basemap. Container egress was
  blocked. Service, inference, retrieval, and tile checks passed after two
  reboots.
- Browser screenshot: `/mnt/shared/fieldos-e2e/20261103T002115Z-2083709/map-render.png`.
  Installer, firstboot, service, and test evidence remain beside the report;
  the temporary ISO and test credentials were removed by the harness.

### Reproducibility and source hygiene update

- Source commit `d8c50306af0c305403b08f100201800c743b74dd` pins the Protomaps
  source build metadata and verifies both bundled Ollama manifests and exact
  model-layer SHA-256/size before preparing a payload. The pins were checked
  against `/mnt/shared/fieldos-payload/offline-payload.tar.zst`; no new payload
  or ISO was built for this source-only change.
- `make check` and all 13 unit tests passed after the change. Gitleaks scanned
  all 17 reachable commits with no findings; the tree is clean and `main` is
  synchronized with `origin/main`.
- Offline APT archive inventory for payload SHA-256
  `5927727201adcaa0da822975fa76d65f08046f3d0625b018a1c24e0689aae273` is at
  `/mnt/shared/fieldos-e2e/package-license-audit-20261102/`. It covers 61
  packages and includes 59 extracted notice texts with per-file hashes. Two
  packages contain no bundled copyright file; same-source notice tracing is
  recorded separately, with the GCC descriptor signature explicitly unverified.
  This is not a license/SBOM clearance. The extracted package cache was removed
  after recording the inventory and notice bundle.

### Hardware inventory update

- The detector now reports physical CPU cores where Linux exposes topology
  and reports `MemAvailable` separately from installed memory. Model-selection
  budgeting is unchanged: it reserves the configured amount from installed
  RAM; the added available-memory field is diagnostic.
- `make check` and all 19 unit tests passed after the follow-up updates. A physical development-laptop
  spot-check observed the NVIDIA driver and GPU, Intel integrated graphics,
  NVMe, battery, CPU, and RAM. The evidence is
  `/mnt/shared/fieldos-e2e/hardware-detection-20261102/`. The latest detector
  source also ran successfully inside the existing installed, NIC-free E2E
  guest via QEMU guest agent; it reported only the 80 GiB `vda` disk and
  excluded Snap loop devices and the virtual DVD. This is a detector smoke
  check, not a fresh installation test. GPU inference remains unvalidated
  because Docker has no NVIDIA runtime/toolkit configured.
- The 2026-11-03 current-source E2E below rebuilt the test ISO from this
  detector revision and confirmed the CPU profile in a fresh disconnected
  install. This validates the CPU path only; simulated hardware fixtures are
  not physical GPU validation.
- The acceptance harness now records the source commit and dirty/clean
  worktree state in new reports; unit tests cover both Git-query success and
  unavailable-Git behavior. Existing reports were generated before that
  reporting improvement.

### Offline unattended installation

- Prior passing report:
  `/mnt/shared/fieldos-e2e/20261102T214900Z-2020461/report.md`.
- Test ISO SHA-256:
  `c2177b7554ad69b13c88f4db28a88aafbdc536b5a78f1aaa175a21b5f80f9422`.
- A fresh 80 GiB qcow2 installed in UEFI mode without a virtual NIC.
  Offline APT, seven local containers, N.O.M.A.D., local chat and embedding,
  Kiwix, PMTiles serving, Firefox map render, blocked external egress, and two
  reboots passed.

### Current-source unattended acceptance

- Run report: `/mnt/shared/fieldos-e2e/20261102T232645Z-2057919/report.md`.
- Test ISO SHA-256:
  `cc74e925baaab29390eeaee48a677c4a3eccad58cc8d71e109a88a9db0e40de0`.
- A fresh 80 GiB UEFI qcow2 installed unattended with no virtual NIC. N.O.M.A.D.
  returned `{"status":"ok"}`; Qwen generated `FIELDOS_ACCEPTANCE_OK`; the
  embedding endpoint returned a vector; Kiwix catalog and reference search
  succeeded; PMTiles tile/range requests succeeded and Firefox rendered the
  map. Container egress was blocked. The report records PASS after two reboots.
- Screenshot: `/mnt/shared/fieldos-e2e/20261102T232645Z-2057919/map-render.png`.

### Interactive customer installation and clean restart

- R2 ISO:
  `/mnt/shared/fieldos-releases/fieldos-test-customer-r2.iso`.
- SHA-256:
  `2155fb0b6b498d053bdad98147e0d846ef84b87fb9107d1727e7f1c6b9b3d0f7`.
- Using the FieldOS GRUB entry, a fresh 80 GiB qcow2 installed interactively
  with a temporary user identity and no NIC. Firstboot completed, seven
  services ran, local chat and embedding worked, Kiwix retrieved the test
  article, and map requests succeeded. Firefox rendered the regional U.S. map.
- The installer reached its explicit “remove installation medium” prompt.
  Media was ejected only then; Enter booted the installed target disk to GDM.
- Services and data checks passed after two consecutive reboots. The generated
  `.env`, ZIM, and regional PMTiles hashes remained unchanged. Evidence:
  `/mnt/shared/fieldos-e2e/customer-correct-entry-20261102/report.md`.
- The first attempt at a service count used `json.load` on Docker Compose JSON
  Lines and falsely failed that single harness check. A direct corrected check
  found all seven containers running; details are in `compose-verified.txt`.

### GRUB default correction and R3

A separate installation through the upstream `Try or Install Ubuntu` entry
installed plain Ubuntu without `/opt/fieldos` or the FieldOS firstboot unit.
That identified a real customer boot-selection hazard. Source now makes
`Install Hckrslsh FieldOS (interactive)` the default GRUB choice while keeping
the upstream options available. After the countdown, the FieldOS installer
still presents interactive disk and account setup.

- R3 candidate:
  `/mnt/shared/fieldos-releases/fieldos-test-customer-r3.iso`.
- Size: 11.1 GiB (11,956,518,912 bytes).
- SHA-256:
  `e07f39a20e64fc1127086739afce39fbbffc12220f8cff126509072c32f7e899`.
- `build/verify-iso.sh` passed BIOS/UEFI boot records, payload, NoCloud
  configuration, FieldOS boot entry, and default selection; SHA-256 sidecar
  verified. A fresh 80 GiB disposable UEFI guest completed the R3 interactive
  install with account and disk selection. The clean remove-media/Enter handoff
  booted to the installed desktop. Offline firstboot loaded all seven local
  images, N.O.M.A.D., chat, embedding, Kiwix, and map endpoints passed, and
  Firefox rendered the regional map. Essential checks and content hashes
  passed after two reboots.
- Interactive install report and screenshots:
  `/mnt/shared/fieldos-e2e/customer-r3-bootcheck-20261102/report.md`.
- ISO and test evidence are local and unpublished.

### Current-source interactive customer installation and R4

- Candidate ISO: `/mnt/shared/fieldos-releases/fieldos-test-customer-r4.iso`.
- Size: 11,956,518,912 bytes. SHA-256:
  `89584420e6d8b78ff63db650bb9eca22cdfc61e19502c71b510e9f5a516036c1`.
- Built from clean source commit
  `fa972ec7ac6069069db9db24baba27efd5c9f79f`. ISO verification passed the
  BIOS/UEFI boot record, interactive installer configuration, and payload
  checks.
- A fresh 80 GiB no-NIC UEFI guest completed interactive target disk and
  account setup, offline firstboot, and boot to GDM. At the remove-media prompt
  the virtual CD was already empty; pressing Enter powered off the guest, and
  an explicit host start was needed to boot the installed disk. The R4
  interactive automatic-reboot handoff is therefore partial.
  All seven services ran; N.O.M.A.D., Qwen inference, 768-dimensional
  embeddings, Kiwix retrieval, and Firefox rendering of the U.S. regional map
  passed. The same service, inference, retrieval, map-tile, and persistence
  checks passed after two reboots; `.env`, ZIM, and regional-map hashes remained
  unchanged.
- Report and evidence: `/mnt/shared/fieldos-e2e/customer-r4-20261103/report.md`.
  Browser screenshot: `/mnt/shared/fieldos-e2e/customer-r4-20261103/map-browser.png`.
- R4's binary was removed after R5 superseded it. Older R2/R3 and pre-R4 test
  ISO binaries were also removed; their historical checksums and test reports
  remain documented. R5 is the only current ISO candidate, and it is not a
  distribution release.

## Readiness

| Component | Status | Evidence |
|---|---|---|
| Unattended offline OS installation | PASS (prior revision) | `/mnt/shared/fieldos-e2e/20261103T002115Z-2083709/report.md`, built from `945751325ab80b1acadb870f0754f3fc7a378fab` |
| Interactive customer installation | PASS | R5 fresh no-NIC guest: interactive disk/account, firstboot, and service checks |
| Clean installer media/restart handoff | PARTIAL | R5 with explicit `shutdown: reboot`: Enter powered off VM; host start reached GDM |
| Customer ISO default selection | PASS | R4 no-input GRUB countdown selected FieldOS and reached interactive setup |
| Offline provisioning and services | PASS | Firstboot complete; seven containers; local service tests |
| N.O.M.A.D. and inference | PASS | Health response and local generation markers |
| Knowledge library and maps | PASS | R4 Kiwix retrieval; regional PMTiles; real Firefox screenshot |
| Reboot persistence | PASS (prior revision) | R5 plus the E2E run above: two in-guest reboots, hashes and service checks |
| ISO release | BLOCKED | R5 verified and installed locally; interactive handoff and redistribution/attribution gates remain; binary unpublished |
| Hardware adaptation | PARTIAL | CPU validation; fixtures simulated; no physical GPU test |
| Container privilege review | PARTIAL | Runtime inspect, loopback ports, root-only secrets; N.O.M.A.D. Docker socket is root-equivalent by upstream design |
| Network-enabled exposure | PARTIAL | User-mode NIC, local endpoint, blocked egress, and NIC-address port checks; LAN peer scan pending |
| Redistribution and attribution | BLOCKED | See `REDISTRIBUTION.md`: Ubuntu modification/trademark review and exact package/image/model/ZIM notices remain unresolved |
| Public Git history | PASS | Gitleaks clean across 29 commits and tracked source as of `fa0a203`; zero Git blobs over 1 MiB; see `/mnt/shared/fieldos-e2e/repository-review-r5-20261103/` |
| Content packs | ARCHITECTURE READY | Manifest schema and validator; 28 tests pass; catalog empty and no customer packs approved |

## Remaining release gates

1. Test inbound service reachability from a separate guest on an isolated
   virtual network. Current user-mode networking evidence verifies loopback
   bindings and NIC-address refusal but is not a LAN peer scan. This host
   session cannot create a libvirt bridge; do not bridge it to any production
   network.
2. Resolve the interactive remove-media handoff. R5 explicitly requests
   `shutdown: reboot`, but Enter at the remove-media prompt still powered off
   the VM; a host start was required to boot the installed target. R3 did boot
   after the virtual CD was ejected at the prompt, while R4/R5 entered the
   prompt with the tray already empty. This difference makes eject timing a
   hypothesis to test, not a confirmed cause. Demonstrate a normal install
   boots the target without host-side repair.
3. Resolve and complete the itemized clearance work in
   [`REDISTRIBUTION.md`](REDISTRIBUTION.md), including Canonical's modified
   Ubuntu trademark requirement, exact package and image SBOMs, and content
   attribution/checksums.
4. Document tested CPU, memory, storage, and unsupported accelerators. GPU
   fixture tests do not establish physical driver/backend support.
5. Synchronize installation, troubleshooting, and recovery instructions with
   the final implementation. Preserve source revision, build inputs, test
   reports, checksums, and known limitations.

The current checkout is `e7b85de9aebdac8adca7ecdb3ce32b4fc56c6f06`. Since the
automated E2E run at `945751325ab80b1acadb870f0754f3fc7a378fab`, changes added
the content-pack manifest validator and tests, build-path defaults, and the
customer installer `shutdown: reboot` setting. `make check` and all 28 unit
tests pass on the current checkout. The exact current checkout still needs a
fresh E2E run before the release record can claim that source revision has
passed operational acceptance.

The 2026-11-02 Git history review scanned all reachable commits with Gitleaks
(no findings), scanned a snapshot of tracked source including current
documentation (no findings), and found no Git blobs over 1 MiB. Scan reports
are preserved under `/mnt/shared/fieldos-e2e/`.

The expanded/full ISO must wait until these release gates pass. Never commit
ISOs, model weights, credentials, VM disks, or downloaded image archives.
