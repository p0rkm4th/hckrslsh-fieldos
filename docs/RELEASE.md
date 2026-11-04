# Release readiness and evidence

**Status: engineering test candidate; not approved for customer or emergency use.**

## Current source and artifacts

- Latest tested source revision: `d8653336ea4597df8eb386a83d364c9dca19d290`.
- `make check test` passed at this revision: 71 unit tests, content-pack
  validation, Python compilation, and shell syntax checks. Output is retained at
  `/mnt/shared/fieldos-e2e/test-suite-20261104-contentpack.txt`.
- Fresh clean-source unattended E2E report:
  `/mnt/shared/fieldos-e2e/20261104T125608Z-3534340/report.md`.
  Source worktree was clean; test ISO SHA-256:
  `0bd97610307320f5dd725b94eead0745ba61fbff69083d5d43d7f4ff473e2781`.
  The guest had no virtual NIC. Installation, local services, chat inference,
  embeddings, Kiwix, optional weather-pack import/indexing, visible zoom-13 map
  rendering, and two consecutive reboots passed.
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
- Rebuilt offline payload: `/mnt/shared/fieldos-payload/offline-payload.tar.zst`,
  5,524,968,361 bytes; SHA-256
  `e6d344324813c444541fe2b4396ffe0670ff29951cbddf466aa9af74d27f1486`. Its
  sidecar and embedded source/map manifests passed preflight; this is the exact
  payload used for the passing clean-source E2E.
- Current customer-mode test ISO:
  `/mnt/shared/fieldos-releases/fieldos-customer-regional-3054c59.iso`;
  12,007,178,240 bytes; SHA-256
  `522abcbc4ba04593ce7d1813af43c5c86110b22a41239c13c3e9800f017d1686`.
  Fresh interactive customer installation and two consecutive reboots passed
  in a separate disposable no-NIC UEFI VM. Detailed report and screenshots:
  `/mnt/shared/fieldos-e2e/customer-regional-3054c59-20261104/report.md`.
- Customer installer media handoff caveat: Ubuntu prompted to remove media and
  press Enter, opened the virtual CD tray, then powered off the VM. Starting the
  VM again booted the installed EFI disk without repair. Physical USB reboot
  behavior has not been tested.
- The customer VM showed the FieldOS wallpaper, N.O.M.A.D. Command Center,
  working UI chat, Kiwix search results, and Nashville streets at zoom 13.
  The screenshots are retained beside the report. The test credential was
  stored in protected runtime storage and is not included in evidence.

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
| Interactive customer installation | PASS in disposable VM, with handoff caveat | Fresh customer-mode ISO, interactive `vda` and account selection, installed-disk boot, report above. Physical USB behavior untested. |
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

The tested source commit `d8653336ea4597df8eb386a83d364c9dca19d290` was
pushed to public `main`; the remote was verified at that revision before this
documentation sync. No ISO, model weights, container archives, or test disks
are committed.

The current customer ISO and its interactive-install report/screenshots remain
under `/mnt/shared`. The old E2E payload cache was retired after its stale
embedded map manifest was proven to omit Middle Tennessee. The current
5,524,968,361-byte payload and checksum are retained at the default build path;
retirement hashes and rationale are in
`/mnt/shared/fieldos-releases/fieldos-artifact-retirement-20261104-stale-payload.txt`.
The failed and passing E2E reports, logs, screenshots, and per-disk retirement
records remain under `/mnt/shared/fieldos-e2e/`; both disposable guest disks
were removed after the repaired acceptance passed, reclaiming
68,950,827,008 host-allocated bytes. `/mnt/shared` has 637 GiB free after the completed flood-pack guest disk was retired; test reports and screenshots remain. No active
FieldOS E2E VM remains.

No public release is approved. Do not recommend physical customer use until the
blocked gates above are resolved.
