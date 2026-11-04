# Release readiness and evidence

**Status: engineering test candidate; not approved for customer or emergency use.**

## Current source and artifacts

- Tested source revision: `3054c59fe38295d54a316b4da22088582a23d3bc`.
- `make check test` passed at this revision: 69 unit tests, content-pack
  validation, Python compilation, and shell syntax checks.
- Fresh clean-source unattended E2E report:
  `/mnt/shared/fieldos-e2e/20261104T112428Z-3477254/report.md`.
  Test ISO SHA-256:
  `94489885144d6a1285c24b7850c426a0072a8f95623da4a9eb82f7417c58310e`.
  The guest had no virtual NIC; provisioning, seven services, local chat and
  embeddings, Kiwix retrieval, high-risk guard cases, a zoom-13 Middle
  Tennessee map in Firefox, and service checks after two reboots passed.
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

## Follow-up content-pack integration test (not accepted)

A later fresh run attempted to import the optional weather pack from removable
media. Its report is
`/mnt/shared/fieldos-e2e/20261104T123346Z-3513131/report.md`. Offline Ubuntu
installation and firstboot passed; the weather archive checksum passed, all
three documents were installed and indexed in N.O.M.A.D., and the source
library opened. The overall run **failed** before map rendering or reboot
checks because the installed guest did not register the required Middle
Tennessee map.

The failure was traced to a stale `/mnt/shared/fieldos-payload/offline-payload.tar.zst`:
its embedded `maps.json` described only the zoom-5 U.S. sample, while the
current source manifest also requires Middle Tennessee. The report records a
dirty worktree at source `442db6c`, so it does not establish acceptance for a
clean revision. `build-iso.sh` now compares embedded map manifests and required
map files against current source before producing another ISO. A rebuilt
payload and clean rerun are still required; this failure is not a release pass.
The failed VM disk and report are retained for diagnosis until the rerun passes.

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

The documentation update is committed as `331bcffc8d3767e1c1c388eecb0c21ceeed88308`
and pushed to `git@github.com:p0rkm4th/hckrslsh-fieldos.git` on `main`. The
push advanced the previously verified remote head `da61a84`; `git ls-remote`
then confirmed remote `main` at `c4cf2e85fb48855572ab4390527737946cb3712b`.
No ISO, model weights, container archives, or test disks are committed.

The current regional customer ISO and its report/screenshots are retained under
`/mnt/shared`. The disposable customer guest disk was retired after acceptance,
reclaiming
34,972,631,040 host-allocated bytes; its report, logs, and selected screenshots
remain. The superseded `fieldos-customer-safety-7981801.iso` (11,987,386,368
bytes) was removed after checksum, open-handle, and libvirt-reference checks;
its sidecar and audit are retained at
`/mnt/shared/fieldos-releases/fieldos-artifact-retirement-20261104-regional-customer.txt`.
Redundant debug screenshots reclaimed another 597,363 bytes. `/mnt/shared`
now has 636 GiB free. The unrelated stopped `fieldos-stock-ubuntu-20261102`
VM and its disk were preserved.

No public release is approved. Do not recommend physical customer use until the
blocked gates above are resolved.
