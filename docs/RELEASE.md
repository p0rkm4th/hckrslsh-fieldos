# Release readiness and evidence

**Status: engineering test candidate; not approved for customer or emergency use.**

## Current source and artifacts

- Latest clean-source offline E2E revision:
  `702102c95fae0731315a2afcc211e412ec15e1fd`.
- `make check test` passed at this revision: 73 tests, content-pack validation,
  Python compilation, and shell syntax checks. The latest recorded test output
  is retained at `/mnt/shared/fieldos-e2e/test-suite-20261104-contentpack.txt`;
  that file predates the last two key-exclusion tests.
- Fresh clean-source unattended E2E report:
  `/mnt/shared/fieldos-e2e/20261104T135401Z-3631878/report.md`. Source worktree
  was clean; test ISO SHA-256:
  `6f6beeaf0ffc1e30f2ab045c68103f33eb4ec584da92bc065b468fb0cf0e30a7`.
  Ubuntu installed from the no-NIC test ISO; provisioning, all seven containers,
  actual CPU inference (`FIELDOS_ACCEPTANCE_OK`), embeddings, N.O.M.A.D. source
  indexing, Kiwix, and real Firefox rendering of the zoom-13 Middle Tennessee
  map passed. Services, models, content, and map checks passed after two
  reboots. The optional-content import step was skipped in this run; separate
  optional-pack evidence is listed below.
- Optional weather pack: `us-weather-safety` 1.0.1, archive SHA-256
  `/mnt/shared/fieldos-payload/content-packs/us-weather-safety-1.0.1.tar.zst`,
  SHA-256 `9be415ad975ef8ef5ef2bd483254dac6ca2b400bfc594ec4309db6205e3b1e1c`.
  It is separate removable-media content and is not in the customer ISO.
- Optional flood pack: `us-flood-safety` 1.0.0 archive at
  `/mnt/shared/fieldos-payload/content-packs/us-flood-safety-1.0.0.tar.zst`,
  SHA-256 `a8540ec40b5964f46c5fb0a2b3ff9f73afa601b96194a621bb91280605dbd470`.
  Its fresh no-NIC transfer/index/browser/reboot test passed at
  `/mnt/shared/fieldos-e2e/20261104T132809Z-3606267/report.md`. The test used
  a dirty worktree based on commit `3553391`; it is not a clean-source release
  acceptance. The pack is optional and is not in the customer ISO.
- Current sanitized offline payload:
  `/mnt/shared/fieldos-payload/offline-payload.tar.zst`, 5,524,961,523 bytes;
  SHA-256 `188d0692cb6bb6c15d2bcb89335c80b75447cf4cd4f844c51e2e4e6a4c5e1a52`.
  Its sidecar and content-pack/map manifests passed verification. This exact
  archive passed the clean-source E2E and excludes generated Ollama registry
  keys and recommendation cache. The superseded 5,524,968,361-byte archive
  (SHA-256 `e6d344324813c444541fe2b4396ffe0670ff29951cbddf466aa9af74d27f1486`)
  and duplicate older map payload (SHA-256
  `fa460aea7b482b8f7b881c20c524a807084ac8394d8df627a16422e237b0adf8`) were
  retired after successful validation; see the artifact retirement record.
- Latest customer-mode ISO, built from clean source commit
  `85a33f866f1b929762e47cc5462b16cbbd84c43c`:
  `/mnt/shared/fieldos-releases/fieldos-customer-regional-85a33f8.iso`;
  12,007,178,240 bytes; SHA-256
  `5c238570a7b2b9ff4fc9277692af618d0379f0edbd4ce989db3c963008cad4a0`.
  A fresh interactive installation to an 80 GiB disposable no-NIC UEFI VM
  completed offline provisioning; real N.O.M.A.D. chat, embeddings, Kiwix
  browser search, and Nashville zoom-13 map rendering passed. Two reboots
  preserved services and user data. Detailed report and screenshots:
  `/mnt/shared/fieldos-e2e/customer-85a33f8/report.md`.
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

A scenario-by-scenario field-use assessment is recorded in [`FIELD-USE-ASSESSMENT.md`](FIELD-USE-ASSESSMENT.md). The no-NIC desktop tests pass for their stated VM scope, but the preparedness usefulness assessment is **FAIL**: coverage is narrow, safety-critical AI requests are refused (and the keyword guard is bypassable), offline navigation is absent, and optional weather material is not in the customer ISO. This distinction is intentional; functional services do not establish disaster readiness.

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

The customer ISO above was built from clean source commit
`85a33f866f1b929762e47cc5462b16cbbd84c43c`, pushed to public `main`. The latest
clean unattended E2E was run at `702102c95fae0731315a2afcc211e412ec15e1fd`;
`85a33f8` updates documentation only. No ISO, model weights, container archives,
or test disks are committed.

The latest customer ISO, report, logs, and selected screenshots remain under
`/mnt/shared`. Its disposable VM `fieldos-customer-85a33f8` was stopped and
undefined after acceptance evidence was recorded; its 35.0 GB allocated qcow2
disk was removed. The fresh unattended E2E VM was also retired after PASS. The
superseded 3054c59 ISO (12.0 GB), the completed customer guest disk, a 5.3 GiB
unpacked payload staging copy, and 11.4 MiB of redundant screenshots were
removed, reclaiming about 49.1 GiB in total. `/mnt/shared` now has 642 GiB free;
the current test evidence directory uses about 3.5 MiB and
`/mnt/shared/fieldos-releases` about 12 GiB. No FieldOS VM is running. The
checksum-verified payload archive and current ISO remain retained.
No public release is approved. Do not recommend physical customer use until the
blocked gates above are resolved.
