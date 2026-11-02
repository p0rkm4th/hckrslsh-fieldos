# Release status and process

FieldOS has passed the unattended offline acceptance run against the current
source and a separate interactive customer installation in disposable QEMU/KVM
guests. It is not yet recommended for physical customer installation. The
current R3 ISO's default entry reaches interactive disk setup without input;
the full interactive installation was completed on R2. Network-enabled
exposure tests and complete redistribution review remain open. Do not publish
release binaries.

## Acceptance evidence — 2026-11-02

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
  verified. A disposable VM booted the default selection automatically into
  interactive disk setup without input. The installer was not run to
  completion on R3; full interactive install evidence is from R2's same
  FieldOS entry and payload.
- Boot report and screenshots:
  `/mnt/shared/fieldos-e2e/customer-r3-bootcheck-20261102/report.md`.
- ISO and test evidence are local and unpublished.

## Readiness

| Component | Status | Evidence |
|---|---|---|
| Unattended offline OS installation | PASS | Current-source E2E report and test ISO hash |
| Interactive customer installation | PASS | R2 FieldOS entry; `customer-correct-entry-20261102/report.md` |
| Clean installer media/restart handoff | PASS | Prompt, post-prompt eject, Enter, installed disk boot |
| R3 default installer selection | PASS | No-input GRUB countdown reached disk setup |
| Offline provisioning and services | PASS | Firstboot complete; seven containers; local service tests |
| N.O.M.A.D. and inference | PASS | Health response and local generation markers |
| Knowledge library and maps | PASS | Kiwix retrieval; PMTiles; real Firefox screenshot |
| Reboot persistence | PASS | Two consecutive reboots; hashes and service checks |
| Hardware adaptation | PARTIAL | CPU validation; fixtures simulated; no physical GPU test |
| Network-enabled exposure | NOT TESTED | Loopback bindings reviewed; isolated LAN peer test pending |
| Redistribution and attribution | PENDING | Per-artifact legal/source review incomplete |
| Public Git history | REVIEWED | Prior scan found no committed payload binaries or credentials |
| Content packs | ARCHITECTURE READY | Manifest schema/catalog; no customer content packs approved |

## Remaining release gates

1. Attach a test VM to an isolated virtual network and test local usability,
   LAN reachability, and remote-access defaults. Do not bridge it to production infrastructure or
   other production networks.
2. Review redistribution and attribution for each Ubuntu package, container,
   model, map, and reference artifact in the candidate ISO. Record sources,
   licenses, notices, versions, and checksums.
3. Document tested CPU, memory, storage, and unsupported accelerators. GPU
   fixture tests do not establish physical driver/backend support.
4. Synchronize installation, troubleshooting, and recovery instructions with
   the final implementation. Preserve source revision, build inputs, test
   reports, checksums, and known limitations.

The expanded/full ISO must wait until these release gates pass. Never commit
ISOs, model weights, credentials, VM disks, or downloaded image archives.
