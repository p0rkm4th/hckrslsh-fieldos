# Release readiness and evidence

**Status: engineering test candidate; not approved for customer installation.**
The clean offline E2E passed for the source and test image below. Customer-mode
installation, content redistribution review, LAN peer isolation, and physical
GPU validation remain release blockers. The persistent Kasm lab is a separate
interactive test environment and is not release acceptance.

## Current source and artifacts

- Tested implementation source: `8b0bda34f4dc3da993eed8663fffc15653d11679` (`main` at the time of test; subsequent changes are documentation only).
- Customer-mode candidate:
  `/mnt/shared/fieldos-releases/fieldos-customer-test-branded-8b0bda3.iso`
- Customer ISO SHA-256:
  `fbec9104316cf0407acc7a5e218a26922ea1849dc3a97d52a45fef09da5db7b1`.
- Fresh unattended E2E test ISO SHA-256:
  `2052d8f22f526425e0ea77ee59eba1016e573fb265a74342cf95345baf4f2ba4`.
- E2E evidence:
  `/mnt/shared/fieldos-e2e/20261103T174505Z-2544533/report.md`, with logs
  and `map-render.png` in the same directory.
- Persistent Kasm test guest: see [FieldOS Lab operations](FIELDOS-LAB.md).

These images and evidence are local test artifacts, not public release assets.
Do not commit them or represent structural ISO verification as an installation
pass.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh Ubuntu installation, offline | PASS | Current-source unattended VM installation in E2E report |
| Offline provisioning and local images | PASS | Firstboot complete; seven Compose services; external access blocked |
| N.O.M.A.D. | PASS | `/api/health` returned `{"status":"ok"}` |
| Local chat inference | PASS | Bundled `qwen3:0.6b-q4_K_M` generated `FIELDOS_ACCEPTANCE_OK` |
| Embeddings | PASS | Bundled model returned a 768-element embedding |
| Kiwix retrieval | PASS | Search/article retrieval recorded in E2E report |
| Offline map | PASS for test fixture | Firefox rendered the map in the no-NIC E2E guest; regional coverage and zoom remain limited |
| Branded installed desktop | PASS | Fresh guest session checked wallpaper/theme and launchers |
| Two-reboot persistence | PASS | Essential service checks repeated after both guest reboots |
| Customer interactive installation | PARTIAL | Candidate structure verified; fresh interactive disk/account selection, handoff, and boot still need testing |
| Kasm FieldOS Lab replacement | PARTIAL | Replacement VM passes service/reboot checks; owner-authenticated browser launch and interaction remain unconfirmed |
| Hardware adaptation | PARTIAL | Configuration/fixture tests exist; physical GPU acceleration and broad machine coverage unverified |
| Security/network isolation | PARTIAL | E2E had no NIC; Lab has management NIC with no route/DNS and guest firewall. Shared-bridge peer isolation is unverified |
| Content redistribution | BLOCKED | Exact Ubuntu and all bundled third-party content/license attribution need final release review |

## Customer installation gate

A customer release requires a separate fresh install from the customer-mode ISO
with interactive identity and disk selection, no network, successful installed
disk boot without manual repair, firstboot completion, branded desktop, and
service/persistence checks. The unattended E2E does not satisfy this gate.
The current candidate has not passed that test. Test only on a disposable VM
with a virtual disk; never target a physical or production disk during
acceptance.

## Content and hardware limitations

The bundled Wikipedia ZIM and low-zoom map are test-sized fixtures, not a
comprehensive field library or navigation-grade regional map. No broad medical,
emergency, agricultural, or survival coverage is claimed. Optional N.O.M.A.D.
content acquisition and activation workflow remains incomplete. Before
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
