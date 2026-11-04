# Release readiness and evidence

**Status: engineering test candidate; not approved for customer or emergency use.**

## Current source and artifacts

The tested implementation is clean source commit
`7e2674e285be158f56b556f048ad3c785d8b0cb9`. `make check test` passed 73 tests,
content-pack validation, Python compilation, and shell syntax checks. Log
SHA-256 `e3224426e80c8244180cbe3f083405b9184e65a0c02d8f88c9947cccae8907a7`:
`/mnt/shared/fieldos-e2e/test-suite-7e2674e.txt`.

- Latest clean-source offline E2E report:
  `/mnt/shared/fieldos-e2e/20261104T152431Z-3714447/report.md`; test ISO
  SHA-256 `0fcb81e0f5e7043024486a6caa11ca31a7e85c2ae17054e4649c1d8f7b3c5fc6`.
  Ubuntu installed in a fresh UEFI VM with no virtual NIC. Offline firstboot,
  all seven containers, CPU inference (`FIELDOS_ACCEPTANCE_OK`), embeddings,
  N.O.M.A.D. indexing of all four core packs, Kiwix, Firefox rendering of the
  source library and zoom-13 Middle Tennessee map, and checks after two reboots
  passed.
- Exact sanitized payload used by that run:
  `/mnt/shared/fieldos-payload-weather-flood-core/offline-payload.tar.zst`;
  SHA-256 `fb4ad0e04144edd4e914263fb9279833cd1ce7e716a10817e79762824b28a73e`.
  Its sidecar, current map metadata, core pack archives, and exclusion of
  generated Ollama keys/cache passed validation.
- Separate weather and flood pack archives were tested as removable media in
  earlier no-NIC runs. The new E2E run exercises their core-install path;
  secondary-media import was skipped.
- Previous customer-mode ISO, built from clean source commit
  `85a33f866f1b929762e47cc5462b16cbbd84c43c`:
  `/mnt/shared/fieldos-releases/fieldos-customer-regional-85a33f8.iso`;
  12,007,178,240 bytes; SHA-256
  `5c238570a7b2b9ff4fc9277692af618d0379f0edbd4ce989db3c963008cad4a0`.
  A fresh interactive installation to an 80 GiB disposable no-NIC UEFI VM
  completed offline provisioning; real N.O.M.A.D. chat, embeddings, Kiwix
  browser search, and Nashville zoom-13 map rendering passed. Two reboots
  preserved services and user data. Detailed report and screenshots:
  `/mnt/shared/fieldos-e2e/customer-85a33f8/report.md`.
  It predates promotion of the weather and flood packs into the core payload;
  rebuild and interactive retest are required before it represents current
  source.
- Customer media-handoff caveat reproduced: Ubuntu prompted to remove media
  and press Enter, then powered off the VM. Starting the VM again booted the
  installed EFI disk without repair. Physical USB handoff remains untested.
- The desktop showed FieldOS branding and N.O.M.A.D. The chat UI generated a
  real local response; Firefox showed Kiwix's Wikipedia 100 fixture and 19
  results for “New York,” the FieldOS source library, and Nashville streets at
  zoom 13. Screenshots and installer/firstboot logs remain beside the report.
  Temporary credentials are excluded from evidence.
## Content-pack integration and stale-payload failure

The first optional-pack integration run failed before map rendering because an
old cached payload contained only the zoom-5 U.S. sample map. Its report is
`/mnt/shared/fieldos-e2e/20261104T123346Z-3513131/report.md`. Ubuntu install,
offline provisioning, and the weather-pack import/indexing passed, but the
overall E2E result was FAIL; it did not reach map rendering or reboot checks.

The build now compares the payload's embedded map manifest, region metadata,
checksums, and required map files against current source before producing an
ISO. A clean payload rebuild at commit `d865333` passed that check. The fresh
E2E report above confirms that both maps were installed, Nashville rendered at
zoom 13 in Firefox, the three weather documents were indexed and served, and
the content persisted across two reboots. The earlier failed report is retained
as diagnostic history; it is not counted as a pass.

## What works offline

The tested installer had no virtual network adapter. Firstboot completed from
local APT packages, container images, and models. N.O.M.A.D. API health passed;
all seven Compose services ran; local Ollama returned `FIELDOS_ACCEPTANCE_OK`;
the embedding model returned a vector; Kiwix retrieved the bundled Wikipedia
fixture; and the Middle Tennessee map served and rendered zoom-13 tiles. The
N.O.M.A.D. containers could not reach an external URL. Service health and
persistent reference/map data passed after two consecutive reboots.

The map build manifest describes Middle Tennessee bounds, source, zoom range,
size, and checksum. The global overview and sample U.S. map stop at zoom 5.
Only Middle Tennessee has a useful zoom-13 regional map in this candidate; there
is no validated GPS, routing, trail, or navigation feature.

## Field-use and safety assessment

This build is not ready to rely on for disaster response. Bundled references are
small: two CDC water/food documents, one NWS tornado guide, and a 100-article
Wikipedia sample. These are not a complete medical, agricultural, mechanical,
wildfire, or survival library. Kiwix's Wikipedia fixture is useful for smoke
testing search, not broad preparedness research.

The bundled `qwen3:0.6b-q4_K_M` model answered a general offline-help prompt in
N.O.M.A.D. UI. Five tested high-risk categories (food outage, tornado shelter,
chemical water treatment, wildfire evacuation, and severe bleeding) were
blocked by the fixed source-library notice with no citations; the streaming
wildfire check also passed. Alternate phrasing can bypass the keyword guard.
This is not a general safety system or medical/emergency guidance. Consult the
original source documents and qualified help for high-consequence decisions.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Clean unattended offline install | PASS | Exact source/test ISO and report above. |
| Interactive customer installation | PASS in disposable VM, with handoff caveat | Current customer ISO, interactive `vda` and account selection, installed-disk boot after manual VM start, two reboots; report above. Physical USB behavior untested. |
| Offline firstboot and services | PASS | Local APT and OCI images; seven Compose services; firstboot status `complete`. |
| Local chat and embeddings | PASS | Real Ollama output and embedding vector before and after both reboots; UI chat also rendered. |
| Kiwix retrieval | PASS, narrow archive | Browser search returned 19 results for “New York” from the 100-article fixture. Broader collection needed. |
| Offline maps | PASS for bounded region | Firefox visibly rendered Nashville at zoom 13. Other regions remain zoom-5 overviews; GPS/navigation unverified. |
| Reboot persistence | PASS | Installed services, reference data, model operation, and regional map checked after two consecutive reboots. |
| Hardware adaptation | PARTIAL | CPU-only 8 GiB VM selected bundled CPU model; simulated profiles only. No physical GPU validation. |
| Security boundaries | PARTIAL | No-NIC isolation, loopback service binds, container egress block, and secret permissions passed. N.O.M.A.D. and Dozzle still access Docker socket; LAN peer testing remains open. |
| Field content breadth | FAIL for field readiness | Current reference set and geographic coverage are inadequate for broad disaster preparation. |
| Redistribution and attribution | BLOCKED | Ubuntu branding/permission, all package/image/model/map/data licenses, notices and source offers still require complete review. |
| Physical customer readiness | BLOCKED | Physical hardware, media handoff, GPU, LAN exposure, comprehensive content, and redistribution gates remain. |

## End-user disaster scenario review

A scenario-by-scenario field-use assessment is recorded in [`FIELD-USE-ASSESSMENT.md`](FIELD-USE-ASSESSMENT.md). The no-NIC desktop tests pass for their stated VM scope, but the preparedness usefulness assessment remains **FAIL**: coverage is narrow, safety-critical AI requests are refused (and the keyword guard is bypassable), and offline navigation is absent. The previous customer ISO predates promotion of weather and flood material into the core test payload; its replacement still needs interactive validation. Functional services do not establish disaster readiness.

## Security and redistribution

Published interfaces bind to loopback, Compose separates internal and local UI
networks, and the tested application container had no external egress. The VM
had no network adapter during acceptance. A LAN-connected peer isolation test
has not been performed. `nomad_admin` requires Docker socket access for upstream
management features; `nomad_dozzle` also mounts the socket read-only. Treat this
as privileged host access.

The ISO remains private test material. Ubuntu branding is present and no
Canonical redistribution permission or complete debranding is recorded. A
complete notice, trademark, source-offer, package, image, model, map, archive,
and document-level licensing review remains outstanding. See
[`REDISTRIBUTION.md`](REDISTRIBUTION.md); passing offline tests does not establish
redistribution rights.

## Source synchronization and artifact handling

The new four-pack core implementation and payload passed clean-source E2E at
`7e2674e285be158f56b556f048ad3c785d8b0cb9`, pushed to public `main`. The
previously tested interactive customer ISO remains built from source
`85a33f866f1b929762e47cc5462b16cbbd84c43c` and does not include the new content.
No ISO, model weights, container archives, or test disks are committed.

The previous customer ISO, report, logs, and selected screenshots remain under
`/mnt/shared`. Its disposable VM `fieldos-customer-85a33f8` was stopped and
undefined after acceptance evidence was recorded; its 35.0 GB allocated qcow2
disk was removed. The new passing E2E VM was shut down, undefined, and its
33 GiB disk retired after preserving its report, logs, and browser screenshots.
The
superseded 3054c59 ISO (12.0 GB), the completed customer guest disk, a 5.3 GiB
unpacked payload staging copy, and 11.4 MiB of redundant screenshots were
removed in earlier cleanup, reclaiming about 49.1 GiB then. This latest disk
retirement freed about 32 GiB more. `/mnt/shared` now has 637 GiB free; the new
E2E evidence directory uses about 1.6 MiB and `/mnt/shared/fieldos-releases`
about 12 GiB. No FieldOS VM is running. The prior customer ISO and both
checksum-verified payload archives remain until the updated customer image is
built and tested.
No public release is approved. Do not recommend physical customer use until the
blocked gates above are resolved.
