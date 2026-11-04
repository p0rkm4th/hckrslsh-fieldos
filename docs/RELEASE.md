# Release readiness and evidence

**Status: engineering test candidate; not approved for customer/emergency use.**
The latest unattended offline E2E passed on source
`09501cb6e6fb4e049da585a610176937a5a52b94`, including a transferred optional
water/food reference pack, Firefox access to its source index and PDF, and two
reboots. A customer-mode ISO built from source `412883c` has now completed a
fresh interactive UEFI install in a no-NIC disposable VM and booted from its
installed disk. Local N.O.M.A.D. inference, Kiwix, and maps were checked in the
installed desktop, with two guest restarts. The installer Restart button/media
handoff was not confirmed because the harness ejected the ISO and cold-booted
the disk after a QMP reset. Field-use readiness remains failed: the core Kiwix
fixture has only 100 articles, the bundled map lacks useful local detail, and
an earthquake answer was generic, unsourced, and referred to calling 911.
Physical hardware, LAN peer isolation, GPU acceleration, and redistribution
approval remain open.

## Current source and artifacts

- Latest clean-source E2E source revision:
  `09501cb6e6fb4e049da585a610176937a5a52b94`.
- Latest clean-source E2E report:
  `/mnt/shared/fieldos-e2e/20261104T015835Z-2935466/report.md` (PASS). Test ISO
  SHA-256: `c71cdb00e180ac29edaa125751b996c71158a1c3478097b42582c9982b9d67c9`.
  It verified no-NIC installation/provisioning, seven services, chat, embeddings,
  Kiwix retrieval, map rendering, and two reboots. Optional reference pack
  `us-water-food-emergency-1.0.0` was transferred separately (archive SHA-256
  `c862c023e8999268be6d78692e4d3a01c95a3f5f840fa954b424b5604eb9518c`),
  installed offline, served through N.O.M.A.D.'s loopback static server, and
  persisted across both reboots. `reference-library-render.png` shows the source
  index; `reference-pdf-render.png` shows the CDC water-safety PDF opened in
  Firefox. The optional pack is not included in the customer ISO.
- Current customer-mode candidate, built from source `412883c`:
  `/mnt/shared/fieldos-releases/fieldos-customer-test-412883c.iso`,
  11,984,044,032 bytes. SHA-256:
  `81880d5afd13c44c76012df2ab02fc5b8eab598467ed7f4b0c9cee7f1185f7da`.
  BIOS/UEFI structure and offline payload were verified by `make verify`.
- Fresh customer install and end-user report:
  `/mnt/shared/fieldos-e2e/customer-interactive-412883c-20261104/report.md`.
  The interactive install used a blank disposable 80 GiB target in UEFI QEMU
  with `-net none`, including disk and account selection. Ubuntu reached its
  install-complete screen; after ISO ejection, the harness power-cycled and
  booted from the installed EFI disk. The branded desktop, N.O.M.A.D. chat,
  Kiwix, and ProtoMaps loaded locally. Two guest restarts returned to the
  desktop. The installer's own Restart button/media handoff is not verified.
  The bundled model generated answers, but the earthquake answer was generic
  and unsourced. Kiwix has one 100-article sample and the map lacks local detail.
  This run did not capture `docker ps` or embeddings; the separate unattended
  E2E report covers those checks.
- The disposable customer VM disk has been retired after confirming no QEMU
  process was using it. It had 34,974,863,360 allocated bytes (80 GiB virtual);
  `/mnt/shared` free space rose from 587 GiB to 619 GiB. Duplicate PPM files,
  unused GUI captures, QEMU control state, and the temporary credential were
  removed. The report, selected PNG screenshots, serial logs, ISO, and disk
  retirement record remain.
- These are local engineering artifacts, not public release assets. The E2E
  result and QEMU customer install do not constitute physical-machine or
  redistribution approval.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh offline Ubuntu installation | PASS | Latest E2E report; no NIC; local APT and images. |
| Offline provisioning | PASS in unattended E2E; PARTIAL in customer run | Seven-container inventory is in the E2E report; not captured in the interactive customer VM. |
| N.O.M.A.D. browser access | PASS | Customer Firefox displayed Command Center and chat at `localhost:8080`. |
| Local chat inference | PASS, function only | Bundled `qwen3:0.6b-q4_K_M` generated responses in the disconnected customer VM. Earthquake answer was generic and unsourced. |
| Embeddings | PASS | E2E report records a 768-element embedding from the bundled model. |
| Kiwix service | PASS | Browser loaded the local Kiwix server. |
| Optional water/food source pack | PASS in E2E | Separate media transfer, validated install, loopback source index, direct Firefox PDF view, and two-reboot persistence; not in customer ISO or N.O.M.A.D. semantic search. |
| Useful reference coverage | FAIL | Only one “Top hundred Wikipedia articles” archive; a `water` search returned no result. |
| Bundled offline map rendering | PASS at overview | Firefox rendered the U.S. basemap. |
| Local map usefulness | FAIL | Nashville at 10 km scale displayed mostly blank background and sparse linework; the separately tested zoom-13 pack is not bundled. |
| Branded desktop | PASS | Customer install showed wallpaper, dock, and N.O.M.A.D. launcher. |
| Customer interactive install | PASS in QEMU | Fresh interactive account/disk setup and completed installation; installed EFI disk booted with ISO removed. Physical USB workflow remains untested. |
| Installer Restart/media handoff | PARTIAL | ISO was ejected; harness QMP reset/power-cycle and cold-booted installed disk. Installer Restart button itself was not confirmed. |
| Two-reboot persistence | PASS in QEMU | Guest returned to branded desktop twice; local map and Kiwix loaded and new chat inference worked after the second restart. Full container inventory/embeddings after reboot are covered by unattended E2E only. |
| Prepper safety/readiness | FAIL | Earthquake answer was generic, uncited, referred to 911/local guidelines, and is not reliable for disconnected emergency use. |
| Physical hardware / GPU | NOT TESTED | No physical laptop or GPU runtime validation. |
| Security / LAN isolation | PARTIAL | Offline VM had no NIC; Kasm management network peer isolation remains unverified. |
| Redistribution | BLOCKED | Exact software/content redistribution terms and attribution require final review. |
| Overall customer release | BLOCKED | Content adequacy, source-grounded safety guidance, redistribution, hardware, and LAN security gates remain. |

## Customer installation gate

The current ISO has passed a fresh interactive UEFI QEMU installation with
account and target-disk selection, no virtual NIC, installed-disk boot, branded
desktop, local applications, and two guest restarts. The ISO was ejected, but
the harness reset/power-cycled the guest to boot from disk; the installer's own
Restart button/media handoff remains unverified. See the customer run report
above. This does not prove physical USB behavior or support for customer
hardware. Repeat on a spare physical machine only after content, licensing,
hardware, and security gates are reviewed. Never target a physical or
production disk during automated tests. The unattended `make test-e2e` image
remains a separate test artifact.

## Content and hardware limitations

The bundled Kiwix ZIM contains only 100 Wikipedia articles. Its local service
works, but a `water` search returned no result. The bundled map renders a broad
U.S. overview, then lacks useful local street detail. A separately tested
Middle Tennessee PMTiles pack has zoom-13 detail but is not included in this ISO
or approved for public redistribution. The current chat model responds offline
but did not provide identifiable references; the earthquake response was
generic and referred to 911 and local guidelines. Do not represent the AI as
authoritative medical, emergency, navigation, or technical reference.

The test pack activation work is documented in `CONTENT-PACKS.md`; other pack
types and a customer content catalog remain incomplete. Review exact sources,
licenses, attribution, Ubuntu terms, and container-image licenses in
`REDISTRIBUTION.md`, `OFFLINE-CONTENT.md`, and `CONTAINER-IMAGES.md` before any
customer distribution. CPU inference is the validated baseline. Hardware
selection is covered by fixtures and local detection code; no physical GPU
runtime has been validated. Treat untested devices as unsupported.

## Evidence handling

Keep test reports, checksums, and diagnostic screenshots in the configured
external storage root (`/mnt/shared` by default). Retain the current candidate,
active payload inputs, meaningful E2E evidence, and one lab rollback point.
Remove only specifically audited superseded artifacts after confirming no
active VM, build, checksum, or Kasm process uses them. See
[testing and cleanup](TESTING.md) and [Lab recovery](FIELDOS-LAB.md).
