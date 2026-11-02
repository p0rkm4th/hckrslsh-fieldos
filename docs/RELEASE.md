# Release status and process

FieldOS has passed the automated offline test-ISO acceptance gate. It is not
yet ready for a physical customer installation. The separate interactive
customer ISO installation, network-enabled exposure check, physical hardware
validation, and full redistribution/attribution review remain release gates.
Do not publish release binaries before those reviews are complete.

## Latest acceptance evidence — 2026-11-02

- Run report: `/mnt/shared/fieldos-e2e/20261102T214900Z-2020461/report.md`.
- Generated unattended test ISO SHA-256:
  `c2177b7554ad69b13c88f4db28a88aafbdc536b5a78f1aaa175a21b5f80f9422`.
- Ubuntu installed to a fresh 80 GiB qcow2 disk in UEFI mode. The VM had no
  virtual NIC, and the installer powered off without manual input.
- Offline APT provisioning, all seven local containers, N.O.M.A.D. health,
  Ollama chat and embedding, Kiwix library and search, PMTiles tile serving,
  and disabled container egress passed. Chat returned
  `FIELDOS_ACCEPTANCE_OK`; N.O.M.A.D. returned `{"status":"ok"}`.
- Firefox rendered the regional U.S. map in the installed guest. Screenshot:
  `/mnt/shared/fieldos-e2e/20261102T214900Z-2020461/map-render.png`.
- After each of two consecutive reboots, the runner waited for application
  readiness and repeated the service, inference, reference, map tile, and
  egress checks. Both reboots passed.
- This verifies only the no-NIC configuration. The Compose ports are bound to
  loopback and security boundaries are documented in `SECURITY.md`; a separate
  network-enabled guest and LAN reachability test remains outstanding.
- The regional/world map fixtures end at zoom level 5. They are broad
  orientation fixtures, not field-level navigation. See `CONTENT-PACKS.md`.

Earlier failed runs remain under `/mnt/shared/fieldos-e2e/` with their reports,
logs, and screenshots. Their reports record FAIL and any removed guest disk;
they are not part of the passing evidence above.

## Current readiness table

| Component | Status | Evidence |
|---|---|---|
| Automated offline OS install | PASS | Latest report; automatic installer power-off |
| Offline provisioning | PASS | Local APT and firstboot smoke checks in report |
| N.O.M.A.D. | PASS | `http://127.0.0.1:8080/api/health` returned `{"status":"ok"}` |
| Local inference | PASS | Qwen3 returned `FIELDOS_ACCEPTANCE_OK` |
| Embeddings | PASS | `nomic-embed-text:v1.5` returned an embedding vector |
| Knowledge library | PASS | Kiwix catalog and New York Times reference search |
| Offline maps | PASS | Firefox map screenshot and PMTiles tile response |
| Reboot persistence | PASS | Two boot-ID changes and service checks after both |
| Hardware adaptation | PARTIAL | CPU inference verified; simulated profiles pass; GPU physical validation absent |
| Interactive customer ISO | FAIL / BLOCKED | `/mnt/shared/fieldos-e2e/customer-iso-20261102-2149/`; disk setup never enables Next; no installation attempted |
| Network-enabled exposure | NOT TESTED | Loopback bindings reviewed; separate routed guest check pending |
| Redistribution and attribution | PENDING | Inventory exists; per-artifact release review incomplete |
| Public Git history | REVIEWED | No tracked historical blobs over 1 MB or binary payload paths found; generated secret code reviewed |
| Content packs | ARCHITECTURE READY | Schema and empty catalog; no customer packs approved |

## Remaining release gates

1. Keep `make test-e2e` passing with the final source and retain the report,
   logs, and screenshot.
2. Repair the customer ISO installer handoff. The ISO currently boots into the
   interactive installer, detects the disposable target disk, but the Next
   button stays disabled. The installer log records
   `Mirror/apply_autoinstall_config/waiting: FAIL`. No disk was modified; only
   `guest.qcow2` is attached as a target. Retest the rebuilt customer ISO in a
   fresh disposable VM and complete the full interactive install before any
   customer-readiness recommendation.
4. Test with a virtual network interface attached. Confirm public-facing
   addresses cannot reach the loopback-only management/service ports and that
   remote access remains disabled.
5. Review redistribution and attribution for every Ubuntu package, container,
   model, map, and reference artifact included in the candidate ISO. Record
   source, license, notices, version, and checksum in the release manifest.
6. Document tested CPU/RAM/storage support and unsupported accelerators.
   Fixture-based hardware selection is simulated evidence; no physical GPU
   backend has been tested.
7. Publish installation, troubleshooting, and recovery instructions, then
   preserve source revision, build inputs, test report, ISO checksum, and
   known limitations. Keep release binaries private until explicitly approved.

The expanded/full ISO must wait until the test and customer-facing release
gates pass. Do not describe simulated hardware tests or an ISO build as
physical-installation validation.
