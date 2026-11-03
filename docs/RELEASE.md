# Release readiness and evidence

**Status: engineering test candidate; not approved for customer installation.**
The clean offline E2E passed on its recorded revision. A fresh customer-mode
installation from `c744e52` also installed to the selected disposable disk and
ran offline after a host start, with firstboot, local services, inference,
references, maps, and two guest reboots checked. The installer powered off at
the media-removal prompt after Enter, so customer installation acceptance is
still partial. A prepper-oriented desktop review also found that the bundled
reference and map content are not adequate for emergency use, and the AI can
present generic unsourced statements as verified. This image is not ready for
customer or emergency use. Redistribution review, LAN peer isolation, and
physical GPU validation also remain open. The persistent Kasm lab is a
separate interactive environment and is not release acceptance.

## Current source and artifacts

- Latest clean-source E2E implementation source: `ec57fed731e915c4c0585dc1e6c648d71d338566`.
- Customer candidate source revision: `c744e5275ec2f5002244c92cef5101b603e53195`.
- Current customer-mode test ISO:
  `/mnt/shared/fieldos-releases/fieldos-customer-handoff-c744e52.iso` (11.2 GiB).
  SHA-256: `c8b09f678351b87a2d3784c4bd91949b6add9a7bb6ad5a9a8a5401a059f762f7`.
- E2E test ISO SHA-256: `c775083ba8538dd282bc20efd82851ec2c2ddb747327f2fa5a1a33d7dc38ad42`.
- E2E report and retained logs/screenshots:
  `/mnt/shared/fieldos-e2e/20261103T194719Z-2651472/report.md`.
  Browser screenshot: `map-render.png`; the map visibly renders Nashville roads,
  labels, parks, and river at zoom 13.
- The E2E guest had no virtual NIC. It installed the map pack from separate
  read-only media, checked local chat and embeddings, reference retrieval, and
  services, and passed checks after two reboots. The 80 GiB guest disk was
  retired only after PASS; its retirement record is retained beside the report.
- The current customer-mode test ISO passed structural verification and keeps
  interactive identity and storage selection. In a fresh no-NIC UEFI QEMU
  install, the user-selected disposable `vda` disk was installed successfully.
  After “Restart now,” Casper displayed its media-removal prompt. Enter caused
  the guest to power off with no host stop/start command; the host then started
  the installed disk. This reproduces the handoff failure and is not a clean
  customer-install PASS. Full evidence is at
  `/mnt/shared/fieldos-e2e/customer-interactive-c744e52-20261103/report.md`.
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
| Fresh Ubuntu installation, offline | PASS | ec57fed E2E report; no virtual NIC; installer log retained |
| Offline provisioning and local images | PASS | Firstboot complete; seven Compose services; external access blocked |
| N.O.M.A.D. | PASS | `/api/health` returned `{"status":"ok"}` |
| Local chat inference | PASS | Bundled `qwen3:0.6b-q4_K_M` generated `FIELDOS_ACCEPTANCE_OK` |
| Embeddings | PASS | Bundled model returned a 768-element embedding |
| Kiwix retrieval | PASS | Search/article retrieval recorded in E2E report |
| Offline map | PASS for tested optional pack | Browser rendered Nashville at zoom 13 from offline Middle Tennessee pack; screenshot retained |
| Branded installed desktop | PASS | Fresh guest session checked wallpaper/theme and launchers |
| Two-reboot persistence | PASS | Essential service checks repeated after both guest reboots |
| Customer interactive installation | PARTIAL | `c744e52` interactive account/disk install completed. Enter at media prompt led to guest poweroff; host-start from disk was needed. Installed services and two guest reboots passed. See fresh customer-mode report. |
| Prepper-oriented content and safety | FAIL | Current UI advertises medical references/how-to guides, but Kiwix contains only the 100-article fixture; practical water/first-aid searches were empty or irrelevant. Map detail is absent at local zoom, and chat answers are unsourced and may imply verification. |
| Kasm FieldOS Lab replacement | PARTIAL | VM 913 is staged behind the retained owner-only workspace; guest services, inference, Kiwix, map endpoint, restricted RDP reachability, and blocked app ports checked. Owner-authenticated browser launch and desktop interaction remain unconfirmed |
| Hardware adaptation | PARTIAL | Configuration/fixture tests exist; physical GPU acceleration and broad machine coverage unverified |
| Security/network isolation | PARTIAL | E2E had no NIC; Lab has management NIC with no route/DNS and guest firewall. Shared-bridge peer isolation is unverified |
| Content redistribution | BLOCKED | Exact Ubuntu and all bundled third-party content/license attribution need final release review |

## Customer installation gate

A customer release requires a separate fresh install from the customer-mode ISO
with interactive identity and disk selection, no network, automatic installed
disk boot, firstboot completion, branded desktop, and service/persistence
checks. The unattended E2E does not satisfy this gate. The `c744e52` candidate
passed disk/account selection and installed Ubuntu. The media-removal prompt
then led to guest poweroff after Enter; a host start was required. The installed
system subsequently passed firstboot, service, inference, Kiwix, map, and
two-reboot checks, but this does not clear the installer handoff. Test only on
a disposable VM with a virtual disk; never target a physical or production disk
during acceptance.

## Content and hardware limitations

The bundled Wikipedia ZIM and zoom-5 map fixtures are test-sized. The separately tested Middle Tennessee pack provides roads through zoom 13, but is not included in the core ISO and is not a comprehensive field library or navigation-grade map. No broad medical,
emergency, agricultural, or survival coverage is claimed. The upstream
N.O.M.A.D. Command Center landing page advertises medical references and how-to
guides that were not present in this test image; correct this before release.
An emergency-prompt UI test also showed generic, unsourced AI text marked as
“Verified”; source-grounded emergency guidance remains unimplemented. One
optional PMTiles map pack transfers, installs, registers, renders, and persists
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
