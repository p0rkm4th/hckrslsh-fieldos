# Release status and process

FieldOS has passed the unattended offline test ISO and interactive customer ISO
installation gates in disposable virtual machines. It is not yet recommended
for physical customer installation. Network-enabled exposure, physical GPU
validation, complete redistribution review, and a clean interactive Restart
handoff observation remain open. Do not publish release binaries before the
reviews are complete.

## Acceptance evidence — 2026-11-02

### Unattended offline installation

- Run report: `/mnt/shared/fieldos-e2e/20261102T214900Z-2020461/report.md`.
- Test ISO SHA-256:
  `c2177b7554ad69b13c88f4db28a88aafbdc536b5a78f1aaa175a21b5f80f9422`.
- Ubuntu installed to a fresh 80 GiB qcow2 in UEFI mode, without a virtual
  NIC. Installation and handoff to the installed disk completed unattended.
- Offline APT provisioning, seven local containers, N.O.M.A.D. health,
  Ollama chat and embedding, Kiwix, PMTiles tile serving, and blocked
  container egress passed. Firefox rendered the map in the guest. Services
  and checks passed after two consecutive reboots.
- Screenshot:
  `/mnt/shared/fieldos-e2e/20261102T214900Z-2020461/map-render.png`.

### Interactive customer ISO

- Candidate:
  `/mnt/shared/fieldos-releases/fieldos-test-customer-r2.iso`.
- SHA-256:
  `2155fb0b6b498d053bdad98147e0d846ef84b87fb9107d1727e7f1c6b9b3d0f7`.
- Installed interactively to a separate fresh 80 GiB qcow2, with temporary
  test identity and no virtual NIC. Installed desktop and firstboot succeeded.
  All seven containers, N.O.M.A.D., local chat (`FIELDOS_REBOOT1_OK` and
  `FIELDOS_REBOOT2_OK`), the embedding model (768 dimensions), Kiwix catalog
  and search, map archive, and blocked external container egress were checked.
- Firefox rendered the regional U.S. map:
  `/mnt/shared/fieldos-e2e/customer-iso-r2-20261102/maps-browser.png`.
- After two consecutive reboots, services restarted and remained usable.
  `.env`, ZIM, and PMTiles checksums matched the pre-reboot baseline; a test
  marker survived. Full evidence:
  `/mnt/shared/fieldos-e2e/customer-iso-r2-20261102/report.md`.
- QMP input events sent as a batch had been dropped, causing a false initial
  diagnosis that the installer Next button was disabled. Sending position,
  button-down, and button-up as separate events with a delay advanced the
  installer. The installer configuration was not changed to fix this harness
  behavior.
- During the interactive run, the test harness ejected the virtual CD before
  pressing Restart. The live session then reported missing SquashFS media.
  Resetting the VM and booting from the installed target disk succeeded. This
  is a harness ordering issue; the interactive Restart control was not cleanly
  observed and should be retested with the CD attached through handoff.
- The first reboot report contains an initial false-negative network
  assertion. Subsequent inspection confirmed no emulated Ethernet device or
  default route, and the corrected assertion passed on reboot 2. Keep the
  initial log as diagnostic evidence; see `reboot-1.txt` and
  `reboot-2-verified.txt` in the run directory.

## Current readiness

| Component | Status | Evidence |
|---|---|---|
| Automated offline OS installation | PASS | Unattended report; automatic install and handoff |
| Interactive customer ISO installation | PASS | R2 installed and booted; Restart-button sequence needs a clean retest |
| Offline provisioning | PASS | Local APT and firstboot success in both runs |
| N.O.M.A.D. | PASS | `127.0.0.1:8080/api/health` returned `{"status":"ok"}` |
| Local inference | PASS | Local Qwen generation markers after install and reboot |
| Embedding model | PASS | `nomic-embed-text:v1.5`, 768-dimensional vectors |
| Knowledge library | PASS | Kiwix catalog and New York reference search |
| Offline maps | PASS | Firefox render and regional PMTiles tile/API checks |
| Reboot persistence | PASS | Two consecutive reboots in both test runs; payload hashes preserved |
| Hardware adaptation | PARTIAL | CPU inference verified; profile fixtures simulated; no physical GPU test |
| Network-enabled exposure | NOT TESTED | Loopback bindings reviewed; routed guest/LAN reachability pending |
| Redistribution and attribution | PENDING | Artifact inventory exists; per-artifact release review incomplete |
| Public Git history | REVIEWED | No tracked historical blobs over 1 MB or committed binary payload paths found in prior review |
| Content packs | ARCHITECTURE READY | Schema/catalog documented; no customer packs approved |

## Remaining release gates

1. Retest the interactive ISO with the virtual CD left attached through the
   installer Restart handoff, then confirm boot from the installed disk.
2. Test a guest with a virtual NIC. Verify services remain locally usable and
   management interfaces are not reachable from another LAN guest; remote
   access must remain disabled unless configured.
3. Review redistribution and attribution for every Ubuntu package, container,
   model, map, and reference artifact in the candidate ISO. Record source,
   license, notices, version, and checksum in the release manifest.
4. Document tested CPU, RAM, and storage support and unsupported accelerators.
   Fixture-based hardware selection is simulated evidence; no physical GPU
   backend has been tested.
5. Keep installation, troubleshooting, and recovery instructions synchronized
   with implementation. Preserve source revision, build inputs, test reports,
   ISO checksums, and known limitations.

The expanded/full ISO must wait until the test and customer-facing release
gates pass. Candidate ISOs are local, unpublished, and must remain out of Git.
