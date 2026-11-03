# Release status and process

FieldOS has passed the unattended offline acceptance run against the current
source and a separate interactive R4 customer installation in disposable
QEMU/KVM guests. R4's default selection, full install, clean media handoff,
firstboot, services, map rendering, and two reboots passed. It is not yet
recommended for physical customer installation. A LAN peer scan, physical GPU
validation, Canonical's modified Ubuntu trademark requirement, and exact
third-party redistribution review remain open. Do not publish release binaries.

## Acceptance evidence

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
  account setup, the remove-media handoff, offline firstboot, and boot to GDM.
  All seven services ran; N.O.M.A.D., Qwen inference, 768-dimensional
  embeddings, Kiwix retrieval, and Firefox rendering of the U.S. regional map
  passed. The same service, inference, retrieval, map-tile, and persistence
  checks passed after two reboots; `.env`, ZIM, and regional-map hashes remained
  unchanged.
- Report and evidence: `/mnt/shared/fieldos-e2e/customer-r4-20261103/report.md`.
  Browser screenshot: `/mnt/shared/fieldos-e2e/customer-r4-20261103/map-browser.png`.
- The R4 binary is a local test candidate, not a distribution release. Older
  R2/R3 and pre-R4 test ISO binaries were removed after R4 superseded them;
  their historical checksums and test reports remain documented.

## Readiness

| Component | Status | Evidence |
|---|---|---|
| Unattended offline OS installation | PASS | Current-source E2E report and test ISO hash |
| Interactive customer installation | PASS | Current-source R4 report: interactive disk/account, firstboot, and service checks |
| Clean installer media/restart handoff | PASS | R4 remove-media prompt and installed target boot |
| Customer ISO default selection | PASS | R4 no-input GRUB countdown selected FieldOS and reached interactive setup |
| Offline provisioning and services | PASS | Firstboot complete; seven containers; local service tests |
| N.O.M.A.D. and inference | PASS | Health response and local generation markers |
| Knowledge library and maps | PASS | R4 Kiwix retrieval; regional PMTiles; real Firefox screenshot |
| Reboot persistence | PASS | R4 plus current-source E2E: two reboots, hashes and service checks |
| ISO release | BLOCKED | R4 verified and installed locally; redistribution/attribution clearance incomplete; binary unpublished |
| Hardware adaptation | PARTIAL | CPU validation; fixtures simulated; no physical GPU test |
| Container privilege review | PARTIAL | Runtime inspect, loopback ports, root-only secrets; N.O.M.A.D. Docker socket is root-equivalent by upstream design |
| Network-enabled exposure | PARTIAL | User-mode NIC, local endpoint, blocked egress, and NIC-address port checks; LAN peer scan pending |
| Redistribution and attribution | BLOCKED | See `REDISTRIBUTION.md`: Ubuntu modification/trademark review and exact package/image/model/ZIM notices remain unresolved |
| Public Git history | PASS | Gitleaks clean across reachable commits and tracked source; no private IPv4 matches or blobs over 1 MiB |
| Content packs | ARCHITECTURE READY | Manifest schema/catalog; no customer content packs approved |

## Remaining release gates

1. Test inbound service reachability from a separate guest on an isolated
   virtual network. Current user-mode networking evidence verifies loopback
   bindings and NIC-address refusal but is not a LAN peer scan. This host
   session cannot create a libvirt bridge; do not bridge it to any production
   network.
2. Resolve and complete the itemized clearance work in
   [`REDISTRIBUTION.md`](REDISTRIBUTION.md), including Canonical's modified
   Ubuntu trademark requirement, exact package and image SBOMs, and content
   attribution/checksums.
3. Document tested CPU, memory, storage, and unsupported accelerators. GPU
   fixture tests do not establish physical driver/backend support.
4. Synchronize installation, troubleshooting, and recovery instructions with
   the final implementation. Preserve source revision, build inputs, test
   reports, checksums, and known limitations.

The 2026-11-02 Git history review scanned all reachable commits with Gitleaks
(no findings), scanned a snapshot of tracked source including current
documentation (no findings), and found no Git blobs over 1 MiB. Scan reports
are preserved under `/mnt/shared/fieldos-e2e/`.

The expanded/full ISO must wait until these release gates pass. Never commit
ISOs, model weights, credentials, VM disks, or downloaded image archives.
