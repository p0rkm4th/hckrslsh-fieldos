# Release readiness and evidence

**Status: engineering test candidate; not approved for customer or emergency use.**

## Current source and artifacts

The statewide-map work is based on source `7e6fa24` and a dirty working tree;
the exact source changes are not yet committed. A clean-source release build
has not been made from these changes.

- Latest full no-NIC E2E report:
  `/mnt/shared/fieldos-e2e/20261104T210719Z-896057/report.md`.
  The test ISO SHA-256 recorded by the report is
  `c0e2578509cde5522400cdd2969e8793f2278ac4e11f50900728a79acd6c2f09`.
  It passed unattended Ubuntu installation, offline firstboot, seven Compose
  services, local CPU Ollama generation (`FIELDOS_ACCEPTANCE_OK`), embeddings,
  Kiwix retrieval, and visible Firefox map rendering at eight Tennessee
  locations. The guest had no virtual NIC. Services and persistent data passed
  two reboots. Optional removable-media pack import was skipped.
- The eight map screenshots, logs, VM XML, and report are retained in
  `/mnt/shared/fieldos-e2e/20261104T210719Z-896057/`. The screenshots were
  visually inspected and showed streets/labels in Memphis, Nashville,
  Knoxville, Chattanooga, Clarksville, Jackson, Johnson City, and roads,
  waterways, and terrain features in the Big South Fork rural area.
- Statewide map candidate:
  `/mnt/shared/fieldos-map-review-20261104/tennessee-20261102-z13.pmtiles`;
  145,267,908 bytes; SHA-256
  `0d123132839b77e627c4f4f103bf7a78925099c57319e759757be3207cb89525`.
  It uses the pinned Protomaps 2026-11-02 build, zoom 0–13, bounds
  `-90.9,34.5,-81.0,37.25`, and ODbL/OSM attribution. Its map content is a
  candidate pending the complete redistribution review in
  [`REDISTRIBUTION.md`](REDISTRIBUTION.md).
- Rebuilt offline payload:
  `/mnt/shared/fieldos-payload/offline-payload.tar.zst`, 5,650,331,542 bytes;
  SHA-256 `cdc90ea60a517bcc3217f8630a1fdfcceb3d208acaa54bead1f81260bb5351b6`.
- The prior interactive customer ISO remains intact at
  `/mnt/shared/fieldos-releases/fieldos-customer-core4-21ad4fc.iso`, SHA-256
  `38acf9bda9d62b328e5baf117895d25affa78688730cf9da1be7b4769791f9bd`.
  It passed its own interactive VM installation and two-reboot checks, but it
  contains only the former Middle Tennessee detailed map. It does **not**
  contain the statewide candidate and is not evidence for the new map build.
- Local validation previously passed 73 tests. The current documentation and
  final Tennessee label edits still need a fresh `make check && make test`
  before source publication.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh unattended offline install | PASS, test-only image | E2E report above; this is not the customer ISO. |
| Interactive customer install | PASS for older image; statewide image untested | Prior ISO/report above. Build and test a new customer-mode ISO separately. |
| Offline firstboot and services | PASS in latest unattended test | Local APT/images; seven services and completed firstboot. |
| Local chat and embeddings | PASS in latest unattended test | Actual CPU response and embedding vector in report. Physical acceleration is unverified. |
| Kiwix/reference retrieval | PASS, narrow collection | Wikipedia fixture and installed source documents work; optional pack transfer was skipped. |
| Tennessee maps | PASS in latest unattended test | Eight Firefox views and persisted map checks. New customer ISO still required. GPS, routing, trail and navigation are not implemented/validated. |
| Reboot persistence | PASS in latest unattended test | Two consecutive reboots; service/data checks in report. |
| Hardware adaptation | PARTIAL | CPU test and simulated fixtures only; no physical CPU/GPU compatibility survey or GPU validation. |
| Network/security boundary | PARTIAL | No-NIC test and container egress checks passed. LAN peer exposure test remains open; Docker socket grants privileged host access to upstream admin components. |
| Field reference breadth | FAIL for field readiness | Core sources remain limited. The optional CDC checklist is not a first-aid manual; agriculture and wildlife coverage are absent. |
| Redistribution review | BLOCKED | Exact software, image, model, map and document licensing/attribution review is incomplete. |
| Physical customer readiness | BLOCKED | Physical installation, hardware coverage, LAN testing, content breadth and rights review remain. |

## Offline content status

The new statewide map renders at zoom levels 0–13 in the tested no-NIC guest,
including the eight locations listed above. The low-zoom world overview remains
available. This is a map viewer, not routing or emergency navigation. The
optional `us-basic-emergency-health` pack contains one CDC checklist, not
procedural first-aid guidance, and was not transferred in the latest E2E.
Wikipedia remains a small test fixture. Do not describe the current library as
a comprehensive preparedness, medical, agriculture, wildlife, or technical
reference collection. See [`FIELD-USE-ASSESSMENT.md`](FIELD-USE-ASSESSMENT.md)
and [`CONTENT-PACKS.md`](CONTENT-PACKS.md).

The latest map and payload were built from a worktree based on `7e6fa24`; the
report is valid test evidence for the recorded image and worktree state, but
not a clean-source reproducibility result. Do not replace the existing
customer ISO until a committed source revision has passed a rebuild and the
new customer-mode installation has been tested independently.

## Older evidence

Earlier passing reports document the four-pack core, weather-pack transfer,
and interactive installation of the older customer ISO. They remain useful
historical evidence but do not validate the statewide-map payload. Failed
intermediate runs are retained as diagnostics and are not counted as passes.
See the individual reports under `/mnt/shared/fieldos-e2e/`.

## Security, licensing, and release hygiene

The latest acceptance guest had no virtual NIC; container egress checks also
failed as expected. This does not establish safety when attached to a LAN. A
LAN-connected peer test is still required. N.O.M.A.D.'s upstream management
components retain Docker socket access; treat it as privileged host access.

The ISO remains test material. Complete redistribution and attribution review,
including Ubuntu branding/trademark requirements, before publishing binaries.
No ISO, model weights, container archives, VM disks, credentials, or generated
private keys belong in public Git. Keep the previous known-good customer ISO
until its statewide replacement passes the separate customer installation
gate.
