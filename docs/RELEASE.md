# Release readiness and evidence

**Status: engineering test candidate; not approved for customer installation.**
Clean-source offline E2E passed on implementation revision `43ec3f9`. The
current customer candidate (`b7f25b0`, documentation-only source change) passed
structural verification and a fresh interactive installation to a disposable
no-NIC VM. Firstboot and functional service checks passed, and the installed disk
booted after the tester detached the still-attached USB and reset the VM. That
manual recovery means this run does **not** clear the customer handoff gate.
Two guest reboots passed. The actual desktop showed the corrected Information
Library copy and rendered the bundled map overview, which was blank at 10 km
zoom. Kiwix has one 100-article fixture; the tested ice-storm response was
generic and lacked identifiable source citations. FieldOS is not ready for
customer or emergency use. Redistribution review, LAN peer isolation, physical
GPU validation, and broad hardware coverage remain open. The persistent Kasm
lab is separate and is not release acceptance.

## Current source and artifacts

- Latest clean-source E2E implementation source:
  `43ec3f9faed73632c13a8113b546ade9b5bf488e`.
- Latest clean-source E2E run:
  `/mnt/shared/fieldos-e2e/20261103T222621Z-2749281/report.md` (PASS). Test ISO
  SHA-256: `c4fc27bc3722509d525049b5fe5b8e56396852854a49f9e65cafe1de8276b373`.
  It verified offline provisioning, N.O.M.A.D. copy correction, local chat and
  embeddings, Kiwix retrieval, Middle Tennessee pack activation and Firefox map
  rendering, and two reboots. The disposable disk was retired after PASS; the
  report, logs, screenshot, and disk-retirement audit remain.
- Current customer candidate source revision:
  `b7f25b033fd7c7aabfd17fe686c303b4be0814b1` (code matches tested
  `43ec3f9faed73632c13a8113b546ade9b5bf488e`; docs-only follow-up does not alter
  the image contents).
- Current customer ISO:
  `/mnt/shared/fieldos-releases/fieldos-customer-branded-b7f25b0.iso`
  (11,984,044,032 bytes). SHA-256:
  `a6af2e66c1042f517747b0ef02b07ef7f1bc9cfdfe93ea90bb55836c799246c1`.
  ISO structure, BIOS/UEFI boot records, customer setup, local APT repository,
  and bundled payload verified by `make verify`.
- Fresh customer-mode interactive run:
  `/mnt/shared/fieldos-e2e/customer-interactive-b7f25b0-20261103/report.md`.
  Identity and only the blank disposable `vda` target were selected; installer
  completed with no virtual NIC. The USB remained attached through restart, and
  the VM returned to installer media. Tester detached it and reset the VM to
  reach the installed disk; handoff is therefore PARTIAL, not PASS. Subsequent
  firstboot, seven services, local chat/embeddings, Kiwix retrieval, no-NIC
  network state, and two reboots passed. The report preserves UI screenshots,
  firstboot evidence, acceptance logs, and actual user-interface checks.
- Earlier E2E results remain in their dated run directories; the current
  authoritative E2E evidence is the `43ec3f9` run listed above.
- The older `c744e52` CD-ROM run and the `280fda2` USB-removal run remain
  historical evidence, not substitutes for testing the current candidate's
  handoff. The new candidate was installed on virtual USB media; the test missed
  the media-removal timing and required a reset. Do not report a clean customer
  install PASS until a fresh run handles that transition without recovery.
- The actual installed desktop launched N.O.M.A.D.; local chat and embeddings
  generated successfully. Kiwix exposed one “Top hundred Wikipedia articles”
  archive: water-purification search returned no results and a first-aid search
  returned unrelated titles. The bundled map rendered the U.S. at low zoom but
  showed no useful roads after zooming in. The optional zoom-13 regional pack
  is not part of this ISO. An emergency-preparedness chat prompt returned
  generic, unsourced advice and labeled practices “Verified”; do not rely on it
  for safety-critical guidance. Browser screenshots and logs are in the run
  evidence directory above.
- Persistent Kasm lab staging VM 913 uses the installed customer-mode test
  system. See [FieldOS Lab operations](FIELDOS-LAB.md); owner-authenticated
  desktop launch remains unconfirmed.

These are local engineering artifacts, not public release assets. The accepted
E2E result is not customer installer acceptance.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh Ubuntu installation, offline | PASS | `43ec3f9` E2E report; no virtual NIC; install and firstboot logs retained |
| Offline provisioning and local images | PASS | Firstboot complete; seven Compose services; external access blocked |
| N.O.M.A.D. | PASS | `/api/health` returned `{"status":"ok"}` |
| Truthful information-library UI copy | PASS | Current-source E2E confirmed the database and Easy Setup copy after install and two reboots; the `b7f25b0` customer desktop also displayed accurate installed-archive coverage. The older `c744e52` ISO binary was retired; its checksum and test report remain. |
| Local chat inference | PASS | Bundled `qwen3:0.6b-q4_K_M` generated `FIELDOS_ACCEPTANCE_OK` |
| Embeddings | PASS | Bundled model returned a 768-element embedding |
| Kiwix retrieval | PASS | Search/article retrieval recorded in E2E report |
| Offline map | PASS for tested optional pack | Browser rendered Nashville at zoom 13 from offline Middle Tennessee pack; screenshot retained |
| Branded installed desktop | PASS | Fresh guest session checked wallpaper/theme and launchers |
| Two-reboot persistence | PASS | Essential service checks repeated after both guest reboots |
| Customer interactive installation | PARTIAL | Current `b7f25b0` fresh install selected identity and disposable disk, completed, then returned to USB installer because test media remained attached. Tester detached media and reset to boot installed disk. Services and two reboots passed, but this is not a clean handoff PASS. See current report. |
| Prepper-oriented content and safety | FAIL | Current installed UI copy is accurate, but Kiwix exposes only a 100-article Wikipedia fixture. The bundled U.S. map renders only as a broad overview and is blank at 10 km zoom. The actual ice-storm chat response was generic and gave no identifiable installed references; do not use as emergency guidance. |
| Kasm FieldOS Lab replacement | PARTIAL | VM 913 is staged behind the retained owner-only workspace; guest services, inference, Kiwix, map endpoint, restricted RDP reachability, and blocked app ports checked. Owner-authenticated browser launch and desktop interaction remain unconfirmed |
| Hardware adaptation | PARTIAL | Configuration/fixture tests exist; physical GPU acceleration and broad machine coverage unverified |
| Security/network isolation | PARTIAL | E2E had no NIC; Lab has management NIC with no route/DNS and guest firewall. Shared-bridge peer isolation is unverified |
| Content redistribution | BLOCKED | Exact Ubuntu and all bundled third-party content/license attribution need final release review |

## Customer installation gate

A customer release requires a separate fresh install from the current
customer-mode ISO with interactive identity and disk selection, no network,
automatic installed-disk boot after the expected USB removal step, firstboot
completion, branded desktop, and service/persistence checks. The unattended E2E
does not satisfy this gate. The `b7f25b0` candidate installed Ubuntu and its
disk was confirmed bootable after the tester detached the USB and reset the VM,
but the current test did not demonstrate the expected unattended-by-engineer
handoff. Repeat the fresh install with media removal captured at the prompt;
never target a physical or production disk during acceptance.

## Content and hardware limitations

The bundled Wikipedia ZIM and zoom-5 map fixtures are test-sized. The separately tested Middle Tennessee pack provides roads through zoom 13, but is not included in the core ISO and is not a comprehensive field library or navigation-grade map. No broad medical,
emergency, agricultural, or survival coverage is claimed. The upstream
N.O.M.A.D. Command Center landing page advertises medical references and how-to
guides that were not present in the older `c744e52` customer test ISO. The
current source contains a guarded firstboot correction for the N.O.M.A.D. home-card
database description and pinned Easy Setup frontend strings. It preserves an
operator-modified service description and fails if the pinned UI copy changes
unexpectedly. The `43ec3f9` offline acceptance verified the corrected database
description and frontend strings after install and after both reboots. The older `c744e52` ISO binary was retired after the `b7f25b0` candidate was
built; its checksum and test report remain. The current image includes the
guarded copy correction, visually verified in the installed Command Center.
The current customer UI ice-storm test produced generic advice with no
identifiable retrieval citation. Source-grounded emergency guidance remains
unimplemented. One optional PMTiles map pack transfers, installs, registers, renders, and persists
offline. The pack is a locally staged test artifact, not bundled or publicly
released; other pack types remain storage-only. Before
redistribution, review the exact content sources, licenses, attribution, and
Ubuntu image terms in `docs/REDISTRIBUTION.md` and `docs/OFFLINE-CONTENT.md`.

CPU inference is the validated baseline. Hardware selection is covered by
fixtures and local detection code; no physical GPU runtime has been validated.
Documented untested devices must be treated as unsupported until checked.

## Evidence handling

Keep test reports, checksums, and diagnostic screenshots in the configured
external storage root (`/mnt/shared` by default). Retain the current candidate,
active payload inputs, meaningful E2E evidence, and one lab rollback point.
Remove only specifically audited superseded artifacts after confirming no
active VM, build, checksum, or Kasm process uses them. See
[testing and cleanup](TESTING.md) and [Lab recovery](FIELDOS-LAB.md).
