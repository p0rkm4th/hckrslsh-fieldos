# Release readiness and evidence

**Status: engineering test candidate; not approved for customer installation.**
The clean offline E2E passed for the source and test image below. Customer-mode
installation, content redistribution review, LAN peer isolation, and physical
GPU validation remain release blockers. The persistent Kasm lab is a separate
interactive test environment and is not release acceptance.

## Current source and artifacts

- Latest clean-source E2E source: `ec57fed731e915c4c0585dc1e6c648d71d338566`.
- E2E test ISO SHA-256: `c775083ba8538dd282bc20efd82851ec2c2ddb747327f2fa5a1a33d7dc38ad42`.
- E2E report and retained logs/screenshots:
  `/mnt/shared/fieldos-e2e/20261103T194719Z-2651472/report.md`.
  Browser screenshot: `map-render.png`; the map visibly renders Nashville roads,
  labels, parks, and river at zoom 13.
- The E2E guest had no virtual NIC. It installed the map pack from separate
  read-only media, checked local chat and embeddings, reference retrieval, and
  services, and passed checks after two reboots. The 80 GiB guest disk was
  retired only after PASS; its retirement record is retained beside the report.
- Latest customer-mode candidate is stale, built from `8b0bda3`:
  `/mnt/shared/fieldos-releases/fieldos-customer-test-branded-8b0bda3.iso`.
  SHA-256: `fbec9104316cf0407acc7a5e218a26922ea1849dc3a97d52a45fef09da5db7b1`.
  A current-source rebuild and independent interactive install remain pending.
- Persistent Kasm Lab details: [FieldOS Lab operations](FIELDOS-LAB.md).

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
| Customer interactive installation | PARTIAL | Fresh install with interactive identity/disk selection booted from installed disk and passed services plus two reboots. After media eject, the VM powered off and required a host start from disk; automatic handoff and physical behavior remain unverified. See the customer-mode report. |
| Kasm FieldOS Lab replacement | PARTIAL | Replacement VM passes service/reboot checks; owner-authenticated browser launch and interaction remain unconfirmed |
| Hardware adaptation | PARTIAL | Configuration/fixture tests exist; physical GPU acceleration and broad machine coverage unverified |
| Security/network isolation | PARTIAL | E2E had no NIC; Lab has management NIC with no route/DNS and guest firewall. Shared-bridge peer isolation is unverified |
| Content redistribution | BLOCKED | Exact Ubuntu and all bundled third-party content/license attribution need final release review |

## Customer installation gate

A customer release requires a separate fresh install from the customer-mode ISO
with interactive identity and disk selection, no network, successful installed
disk boot without guest repair, firstboot completion, branded desktop, and
service/persistence checks. The unattended E2E does not satisfy this gate. The
current candidate completed these checks in QEMU, but the VM powered off after
the media-removal prompt and was explicitly started from its installed disk.
Automatic handoff and physical-media behavior remain unverified, so this gate
is PARTIAL. Test only on a disposable VM
with a virtual disk; never target a physical or production disk during
acceptance.

## Content and hardware limitations

The bundled Wikipedia ZIM and zoom-5 map fixtures are test-sized. The separately tested Middle Tennessee pack provides roads through zoom 13, but is not included in the core ISO and is not a comprehensive field library or navigation-grade map. No broad medical,
emergency, agricultural, or survival coverage is claimed. The upstream
N.O.M.A.D. Command Center landing page uses generic copy that overstates the
reference packs present in this image; the FieldOS Start Here guide describes
the actual fixture limits, but the discrepancy should be corrected before
public release. One optional PMTiles map pack transfers, installs, registers, renders, and persists offline. The pack is a locally staged test artifact, not bundled or publicly released; other pack types remain storage-only. Before
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
