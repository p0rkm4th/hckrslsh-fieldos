# Release readiness and evidence

**Status: engineering test candidate; not approved for customer or emergency use.**

## Latest source and acceptance evidence

- Validated source revision: `7981801280e3552ce7efa3d8aa2fdc03fa1e23a7`
  (`7981801`), clean worktree at E2E start. The commit includes the pinned
  upstream RAG prompt correction and deterministic high-risk chat guard.
- Latest clean-source automated no-NIC E2E report:
  `/mnt/shared/fieldos-e2e/20261104T100029Z-3363576/report.md`.
  Test ISO SHA-256:
  `66c436752c281786a227029c827d502f8fd52e3ad29ff83937ab361d8a039d23`.
  Report, installation/firstboot logs, map and source-library screenshots are
  retained. The disposable guest disk and test ISO were removed after the run.
- The latest run passed unattended Ubuntu installation, offline provisioning,
  all seven containers, local Ollama generation and embeddings, indexed CDC
  and NWS source retrieval, Kiwix search, actual Firefox map and source-library
  rendering, and essential checks after two reboots. The guest had no virtual
  NIC and container egress was blocked.
- The deterministic chat guard returned the fixed safety notice without
  citations for five tested high-risk categories through both normal and
  streaming API paths. This only establishes those test cases; the keyword
  guard can miss differently phrased requests and is not a general safety
  system.
- Optional content-pack transfer was **SKIPPED** in this latest run because
  its fixture duplicated a pack already bundled. A separate prior run at
  source `1fb6806` passed offline transfer and Firefox rendering of the
  Middle Tennessee pack at zoom 13. That optional pack is not in the current
  baseline ISO.
- `make check test` passed at commit `7981801`: 68 unit tests,
  content-pack validation, Python compilation, and shell syntax checks.
- The latest customer candidate is
  `/mnt/shared/fieldos-releases/fieldos-customer-safety-7981801.iso` (SHA-256
  `10f55a4293f2d8659895e3358091b2b5bc4e99841b75d02e9b25552baa48ea9f`), built
  from clean source `c642fac`. Its fresh interactive install and two-reboot
  test passed; detailed evidence is at
  `/mnt/shared/fieldos-e2e/customer-safety-7981801-r2-20261104/report.md`.
- The earlier interactive installation on the 1fb6806 baseline is historical.
  The latest `c642fac` customer candidate was independently installed with
  interactive disk and account selection; the installer media handoff required
  detaching the ISO after its power-off, then the installed EFI disk booted
  normally. Desktop branding, map rendering, local AI, references, no-NIC
  operation, and two reboots passed. See the report above.
- The payload input is `/mnt/shared/fieldos-payload` (about 5.2 GiB); it is
  required to build the next customer candidate.

## AI safety finding

Prepper-style probes of the bundled `qwen3:0.6b-q4_K_M` model showed that the
upstream N.O.M.A.D. prompt alone did not keep unsupported emergency answers
within retrieved sources. The model claimed boiling makes chemically
contaminated water safe and invented wildfire advice. These outputs are
retained in `/mnt/shared/fieldos-e2e/20261104T092055Z-3331284/rag-policy-acceptance.json`.

The current work patches the pinned upstream prompt and adds a deterministic
server-side keyword guard for emergency, medical, water-treatment, food-safety,
and evacuation questions. Tested requests receive a fixed message directing
users to original offline sources, with no citations attached. Alternative
wording can bypass the keyword guard. FieldOS must not be represented as safe
for emergency, medical, navigation, or other high-consequence decisions; users
must consult original authoritative material and suitable trained help.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh unattended offline installation | PASS, clean source | Exact source commit and test ISO hash above. |
| Offline provisioning and local services | PASS, clean source | Firstboot complete; seven containers and local APT/images checked. |
| Chat and embedding inference | PASS, clean source | Local generation and embedding endpoint passed after each reboot. |
| High-risk chat guard | PASS for tested phrases only | Five categories plus streaming returned fixed notice/no citations; incomplete keyword coverage remains a release limitation. |
| Reference retrieval and Kiwix | PASS, limited | CDC/NWS indexed sources and Kiwix search; content breadth is small. |
| Offline map rendering | PASS at overview level | Firefox screenshot; bundled PMTiles max zoom 5. |
| Optional regional pack | PASS in prior run; SKIP latest | Prior zoom-13 transfer/render evidence; pack not included in current ISO. |
| Two-reboot persistence | PASS, clean source | Services, model inventory, references and state checked after both reboots. |
| Interactive customer install | PASS in disposable VM | Fresh `c642fac` candidate, interactive disk/account, installed-disk boot, branded desktop, and two reboot checks; report above. |
| Hardware adaptation | PARTIAL | CPU-only 8 GiB VM profile tested; no physical GPU validation. |
| Connected/LAN security | PARTIAL | Loopback bind and QEMU user-mode checks exist; peer LAN scan remains unverified. N.O.M.A.D. and Dozzle mount the Docker socket. |
| Content breadth | FAIL for field-readiness | Miniature Wikipedia, narrow emergency sources, and zoom-5 overview map are starter fixtures. |
| Redistribution review | BLOCKED | Complete review of software, model, map, and reference rights before any public binary distribution. |
| Customer ISO install and persistence | PASS in disposable VM | Candidate checksum and evidence report above; physical-machine and redistribution gates remain. |

## Field-use limits

The baseline has two CDC water/food documents, one NWS tornado guide, a
100-article Wikipedia archive, and low-zoom world/sample U.S. map data. The
bundled map stops at zoom 5 and is not suitable for street or trail navigation.
It lacks substantial agriculture, first aid, wildfire, mechanical repair, and
regional topographic collections. The separately tested Middle Tennessee pack
is not included in the current ISO. GPS/QGIS and physical GPU acceleration are
unverified. The emergency-chat keyword guard is bypassable and does not make the
small model an authority.

## Build, evidence, and artifact handling

The latest clean E2E passed at `7981801`. Gitleaks scanned all 203 Git commits
and the working tree with no findings. Seven reviewed commits are local ahead
of public `origin/main` at `da61a84`. The latest push attempt was rejected with
`Permission denied (publickey)`; GitHub repository metadata reports push
permission, but connected GitHub write endpoints previously returned 403.
Remote read access timed out during the latest recheck, so the remote head has
not been freshly confirmed. No release binaries are part of Git. The customer-mode
VM acceptance gate passed, but the ISO is still a test candidate, not an
approved public release. The superseded 1fb6806 ISO and its checksum sidecar
were retired after confirming no process used them; their SHA-256 and reason
are recorded in `fieldos-artifact-retirement-20261104-customer-nws.txt`. Test
and release data live on `/mnt/shared`; preserve the current candidate, reports,
and screenshots, and retire only superseded
VM disks and ISO candidates after verifying they are not in use.

Never infer successful operation from an ISO build or container startup alone.
The current candidate is not a customer-ready emergency appliance.
