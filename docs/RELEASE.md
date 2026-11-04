# Release readiness and evidence

**Status: engineering test candidate; not approved for customer or emergency use.**

## Current source and artifacts

Latest tested source is clean commit
`b5d6f748c9efdb0f4345c5fe92533b882c7e2856`, published to `main`.

- Latest full no-NIC E2E report:
  `/mnt/shared/fieldos-e2e/20261104T215624Z-1056575/report.md`. It records a
  clean worktree at the exact source commit. Test ISO SHA-256:
  `71821434553d6b0b26b0f87cfa6f857ed6a38b97e80e8b357d69f966e4e4217a`.
  The disposable UEFI VM installed Ubuntu offline with no virtual NIC,
  completed firstboot, ran seven services, generated `FIELDOS_ACCEPTANCE_OK`
  with CPU Ollama, returned an embedding vector, served Kiwix, and passed two
  reboot/persistence cycles. Container egress checks passed.
- The E2E imported the optional
  `us-southeastern-vegetable-growers-2026.1.tar.zst` from separate read-only
  transfer media. Archive SHA-256:
  `e7dd06a657973a15bd75a1d9986ec774aef7f0b86c1f88ce4e4b25416cac7e30`.
  N.O.M.A.D. indexed the handbook as 678 chunks, the local Source Library
  served the source PDF, and the pack survived both reboots.
- Firefox visibly rendered zoom-13 maps at Memphis, Nashville, Knoxville,
  Chattanooga, Clarksville, Jackson, Johnson City, and Big South Fork. Screenshots,
  reference-library view, logs, VM XML, and report are retained in
  `/mnt/shared/fieldos-e2e/20261104T215624Z-1056575/`.
- Statewide map artifact:
  `/mnt/shared/fieldos-map-review-20261104/tennessee-20261102-z13.pmtiles`;
  145,267,908 bytes; SHA-256
  `0d123132839b77e627c4f4f103bf7a78925099c57319e759757be3207cb89525`.
  It uses the pinned Protomaps 2026-11-02 build, zoom 0–13, bounds
  `-90.9,34.5,-81.0,37.25`. Redistribution review remains open.
- The old interactive customer ISO remains intact at
  `/mnt/shared/fieldos-releases/fieldos-customer-core4-21ad4fc.iso`, SHA-256
  `38acf9bda9d62b328e5baf117895d25affa78688730cf9da1be7b4769791f9bd`.
  Its separate interactive VM installation passed, but the ISO has only the
  former Middle Tennessee detailed map and does not include the optional
  handbook. It is not evidence for the current statewide payload.
- `make check && make test` passed 74 tests. The new test covers the long
  guest-command timeout required for large PDF indexing.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh unattended offline install | PASS, test-only image | Exact clean source, test ISO hash, and report above; not the customer ISO. |
| Interactive customer install | PASS for older image; current image untested | Build and test a new customer-mode ISO separately. |
| Offline firstboot and services | PASS in latest unattended test | Local packages/images; seven services and completed firstboot. |
| Local chat and embeddings | PASS in latest unattended test | Actual CPU response and embedding vector. Physical GPU acceleration is unverified. |
| Kiwix/reference retrieval | PASS, narrow collection | Wikipedia fixture and core sources work; optional handbook imported offline and indexed as 678 chunks. Library breadth remains limited. |
| Tennessee maps | PASS in latest unattended test | Eight visible Firefox views and persistence. New customer ISO still required; GPS, routing, trails, and navigation are unverified. |
| Reboot persistence | PASS in latest unattended test | Services, map, and optional pack passed two reboots. |
| Hardware adaptation | PARTIAL | CPU test and simulated fixtures only; no physical CPU/GPU validation. |
| Network/security boundary | PARTIAL | No-NIC test and container egress checks passed. LAN peer test remains open; Docker socket grants privileged host access to upstream admin components. |
| Field reference breadth | FAIL for field readiness | Optional 2026 vegetable handbook is validated; CDC checklist is not first aid, and wildlife, agriculture beyond vegetables, and broad practical references remain limited. |
| Redistribution review | BLOCKED | Full software, image, model, map, and document attribution/license review incomplete. |
| Physical customer readiness | BLOCKED | Physical install/hardware, LAN exposure, content breadth, and rights review remain. |

## Offline content status

The statewide map renders at zoom 0–13 across the tested Tennessee locations.
It is a map viewer, not routing or emergency navigation. The optional CDC
emergency-health pack contains a checklist, not first-aid procedures. The
Southeastern vegetable handbook is a separate optional pack and is not in the
core/customer ISO. Wikipedia remains a 100-article test fixture. Do not
describe FieldOS as a comprehensive preparedness, medical, agriculture,
wildlife, or technical reference library. See
[`FIELD-USE-ASSESSMENT.md`](FIELD-USE-ASSESSMENT.md) and
[`CONTENT-PACKS.md`](CONTENT-PACKS.md).

The latest test image is a clean-source build from `b5d6f74`. The statewide map
and pack were acceptance-tested in that unattended image, but not yet in a new
interactive customer ISO. Keep the existing customer candidate until its
statewide replacement passes a separate customer-mode installation.

## Earlier failed run and retained evidence

The first handbook transfer run at
`/mnt/shared/fieldos-e2e/20261104T214216Z-1034272/` failed because the test
harness accidentally treated its requested 950-second command timeout as an
output-truncation limit and used the 180-second default. The guest subsequently
completed indexing; the local N.O.M.A.D. API showed 678 chunks in
`handbook-index-post-timeout.json`. That run is not counted as a PASS. The
harness fix is included in the passing clean-source run above. Failed
intermediate map runs are retained as diagnostics, not passes.

## Security, licensing, and release hygiene

The latest acceptance guest had no virtual NIC; container egress checks also
passed. This does not establish safety when attached to a LAN. A LAN-connected
peer test remains required. N.O.M.A.D.'s upstream management components retain
Docker socket access; treat it as privileged host access.

The ISO remains test material. Complete redistribution and attribution review,
including Ubuntu branding/trademark requirements, before publishing binaries.
No ISO, model weights, container archives, VM disks, credentials, or generated
private keys belong in public Git. Preserve the old customer ISO until the
statewide customer image passes a separate interactive installation test.
