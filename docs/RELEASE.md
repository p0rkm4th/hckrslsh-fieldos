# Release readiness and evidence

**Status: engineering test candidate; not approved for customer/emergency use.**
The latest unattended offline E2E passed on source `0085b7ac2989dc684776ae0910fe5c77dd829c0c`.
A separate customer-mode UEFI install on the same source completed interactively
with no NIC, media handoff to the installed disk, firstboot, and two guest
restarts. Actual browser checks confirmed local N.O.M.A.D. chat and the branded
desktop. The field-use content check failed: Kiwix has only a 100-article
Wikipedia fixture, the map has no useful local detail at a 10 km scale, and
chat guidance was generic and unsourced. Physical hardware, LAN peer isolation,
GPU acceleration, and redistribution approval remain open.

## Current source and artifacts

- Current source and latest pushed commit: `0085b7ac2989dc684776ae0910fe5c77dd829c0c`.
- Latest clean-source E2E report:
  `/mnt/shared/fieldos-e2e/20261104T001739Z-2874470/report.md` (PASS). Test ISO
  SHA-256: `5a6a5e78df0abe6b238b0d9fbfc48638bcb63e5192b67467237e5ed995db61ba`.
  It verified offline install/provisioning, seven services, chat, embeddings,
  Kiwix retrieval, bundled map rendering, two reboots, and no NIC. The optional
  Middle Tennessee content-pack archive was not available in this run; its
  separate earlier test is documented in `CONTENT-PACKS.md`.
- Current customer-mode candidate:
  `/mnt/shared/fieldos-releases/fieldos-customer-test-0085b7a.iso`, 11,984,044,032
  bytes. SHA-256:
  `4d1b7ed6ed6c8089fbb0cdb416743fed2f917f9ae899d6bf6aa45de92915ba22`.
  BIOS/UEFI structure and offline payload were verified by `make verify`.
- Fresh customer-mode install and end-user report:
  `/mnt/shared/fieldos-e2e/customer-interactive-0085b7a-20261104/report.md`.
  The interactive install used a blank disposable 80 GiB target in UEFI QEMU
  with `-net none`. At the restart prompt, the media was ejected and Enter
  continued to the installed OS without resetting the VM. Firstboot completed,
  seven containers were visible through `sudo docker ps`, Firefox loaded the
  local Command Center, and the desktop/assistant remained accessible after two
  restarts. The firstboot journal was not exported from this guest; the separate
  unattended E2E has fuller provisioning logs.
- The disposable customer VM disk and two superseded failed-run disks were
  retired after validation. The report, compressed screenshots, ISO, and prior
  small diagnostic reports remain. See `artifact-retirement.md` in the customer
  run directory for exact paths and reclaimed space.
- These are local engineering artifacts, not public release assets. The E2E
  result and QEMU customer install do not constitute physical-machine or
  redistribution approval.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh offline Ubuntu installation | PASS | Latest E2E report; no NIC; local APT and images. |
| Offline provisioning | PASS | E2E logs and customer VM `sudo docker ps`; seven services. |
| N.O.M.A.D. browser access | PASS | Customer Firefox displayed Command Center and chat at `localhost:8080`. |
| Local chat inference | PASS, function only | Bundled `qwen3:0.6b-q4_K_M` generated a response in the disconnected customer VM. Response quality and sourcing failed field-readiness review. |
| Embeddings | PASS | E2E report records a 768-element embedding from the bundled model. |
| Kiwix service | PASS | Browser loaded the local Kiwix server. |
| Useful reference coverage | FAIL | Only one “Top hundred Wikipedia articles” archive; “water purification” returned no result. |
| Bundled offline map rendering | PASS at overview | Firefox rendered the U.S. basemap. |
| Local map usefulness | FAIL | Nashville at 10 km scale displayed mostly blank background and sparse linework; the separately tested zoom-13 pack is not bundled. |
| Branded desktop | PASS | Customer install showed wallpaper, dock, and N.O.M.A.D. launcher. |
| Customer interactive install and media handoff | PASS in QEMU | Fresh interactive account/disk setup; USB ejected at prompt; same VM booted installed OS with no reset. Physical USB workflow remains untested. |
| Two-reboot persistence | PASS in QEMU | Guest returned to branded desktop twice; N.O.M.A.D. chat/history loaded after both restarts. Full service checks after both reboots are covered by unattended E2E. |
| Prepper safety/readiness | FAIL | Chat provided generic, uncited water-storage guidance, omitted usable quantities/procedure, and included questionable advice. Do not use for emergency decisions. |
| Physical hardware / GPU | NOT TESTED | No physical laptop or GPU runtime validation. |
| Security / LAN isolation | PARTIAL | Offline VM had no NIC; Kasm management network peer isolation remains unverified. |
| Redistribution | BLOCKED | Exact software/content redistribution terms and attribution require final review. |
| Overall customer release | BLOCKED | Content adequacy, source-grounded safety guidance, redistribution, hardware, and LAN security gates remain. |

## Customer installation gate

The current ISO has passed a fresh interactive UEFI QEMU installation with
account and target-disk selection, no virtual NIC, prompt-time media removal,
automatic installed-disk boot, firstboot, branded desktop, and two guest
restarts. The full evidence is in the customer run report above. This does not
prove physical USB behavior or support for customer hardware. Repeat on a spare
physical machine only after content, licensing, hardware, and security gates are
reviewed. Never target a physical or production disk during automated tests.
The unattended `make test-e2e` image remains a separate test artifact.

## Content and hardware limitations

The bundled Kiwix ZIM contains only 100 Wikipedia articles. Its local service
works, but basic water-purification lookup returned no result. The bundled map
is low zoom: it renders a broad U.S. overview, then lacks useful street detail
near Nashville at a 10 km scale. A separately tested Middle Tennessee PMTiles
pack has zoom-13 detail but is not included in this ISO or approved for public
redistribution. The current chat model responds offline but did not provide
identifiable references or reliable actionable water-storage guidance. Do not
represent the AI as authoritative medical, emergency, or technical reference.

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
