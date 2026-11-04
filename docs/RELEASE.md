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
- Current interactive customer-mode ISO, built from clean source commit
  `21ad4fcdb882998ca1c3bd47333b1139c162651c`:
  `/mnt/shared/fieldos-releases/fieldos-customer-core4-21ad4fc.iso`;
  12,007,178,240 bytes; SHA-256
  `38acf9bda9d62b328e5baf117895d25affa78688730cf9da1be7b4769791f9bd`.
  Fresh interactive install selected virtual disk `vda`, created a test user,
  installed with no NIC, booted the installed EFI disk, completed local
  firstboot, and passed local AI, embeddings, Kiwix, visible Nashville map, and
  two reboot checks. Full report and screenshots:
  `/mnt/shared/fieldos-e2e/customer-core4-21ad4fc/report.md`.
- Media handoff caveat: Ubuntu asked to remove media and press Enter; after
  virtual media ejection the VM powered off. A subsequent VM power-on booted
  the installed disk without repair. Physical USB handoff remains untested.
- The desktop showed FieldOS wallpaper and dock. Firefox visibly rendered
  Nashville streets at zoom 13 and opened the one-book Wikipedia 100 fixture.
  The in-app emergency query returned the fixed source-library notice with no
  citations. Temporary credentials are excluded from evidence.

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

This build is not ready to rely on for disaster response. The current candidate
includes four core source packs (two CDC water/food documents and NWS-derived
tornado, flood, hurricane, and winter references) plus a 100-article Wikipedia
sample. These are not a complete medical, agricultural, mechanical, wildfire,
or survival library. Kiwix's Wikipedia fixture is useful for smoke testing
search, not broad preparedness research.

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
| Local chat and embeddings | PASS | Real Ollama output and embedding vector before and after reboot two; services were Up and health returned OK after each reboot. The in-app emergency query rendered the fixed source-library notice. |
| Kiwix retrieval | PASS, narrow archive | Current candidate showed the one-book Wikipedia 100 fixture in Firefox; a “water” search returned results. Broader collection needed. |
| Offline maps | PASS for bounded region | Firefox visibly rendered Nashville at zoom 13. Other regions remain zoom-5 overviews; GPS/navigation unverified. |
| Reboot persistence | PASS | Services, firstboot state, and persistent map/ZIM checksums were checked after each reboot; chat, embeddings, and Kiwix search passed again after reboot two. |
| Hardware adaptation | PARTIAL | CPU-only QEMU profile selected the bundled CPU model; simulated profile fixtures only. No physical GPU validation. |
| Security boundaries | PARTIAL | No NIC/default route, loopback service binds, Docker internal-network and egress checks passed. N.O.M.A.D. and Dozzle still access Docker socket; LAN peer testing remains open. |
| Field content breadth | FAIL for field readiness | Current reference set and geographic coverage are inadequate for broad disaster preparation. |
| Redistribution and attribution | BLOCKED | Ubuntu branding/permission, all package/image/model/map/data licenses, notices and source offers still require complete review. |
| Physical customer readiness | BLOCKED | Physical hardware, media handoff, GPU, LAN exposure, comprehensive content, and redistribution gates remain. |

## End-user disaster scenario review

A scenario-by-scenario field-use assessment is recorded in [`FIELD-USE-ASSESSMENT.md`](FIELD-USE-ASSESSMENT.md). The no-NIC desktop tests pass for their stated VM scope, but the preparedness usefulness assessment remains **FAIL**: coverage is narrow, safety-critical AI requests are refused (and the keyword guard is bypassable), and offline navigation is absent. The current customer candidate includes and indexes the four core packs.
Functional services do not establish disaster readiness.

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

The four-pack core implementation passed unattended E2E at
`7e2674e285be158f56b556f048ad3c785d8b0cb9`, pushed to public `main`. The
interactive customer candidate above was built from commit `21ad4fc`, which
includes that implementation, and passed its separate fresh VM test. No ISO,
model weights, container archives, or test disks are committed.

The previous customer ISO is superseded; its report and screenshots remain as
historical evidence. The disposable customer VM disk is retired after its
report is recorded; screenshots and report remain under
`/mnt/shared/fieldos-e2e/customer-core4-21ad4fc/`. After retiring the 34.8 GB allocated qcow2, superseded 12.0 GB customer ISO,
and 5.52 GB stale payload archive, `/mnt/shared` has 642 GiB free. The current
candidate ISO and validated payload remain; the 3.5 MiB report/screenshots are
retained. Retirement hashes and paths are recorded in
`/mnt/shared/fieldos-releases/fieldos-artifact-retirement-20261104-customer-85a33f8.txt`.
No VM disk or temporary credentials belong in Git.
No public release is approved. Do not recommend physical customer use until the
blocked gates above are resolved.
