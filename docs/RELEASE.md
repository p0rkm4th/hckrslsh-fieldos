# Release readiness and evidence

**Status: engineering test candidate; not approved for customer or emergency use.**

## Latest source and acceptance evidence

- Source base: `1fb68063c82c12ba9fc9504ba90fbbbc2a8f876f` (`1fb6806`). The
  latest E2E was run from this revision with uncommitted changes (`source
  worktree dirty: true`). Its result is useful engineering evidence, but is
  not yet attributable to a clean published source revision.
- Latest automated no-NIC E2E report:
  `/mnt/shared/fieldos-e2e/20261104T094150Z-3342937/report.md`.
  Test ISO SHA-256:
  `04beb5d2467d59fac9448ad14b23ed3a2a7bae9995c051674ce37cef4e05b61b`.
  Report, installation/firstboot logs, map and source-library screenshots are
  retained. The disposable guest disk and test ISO were removed after the run.
- The latest run passed unattended Ubuntu installation, offline provisioning,
  all seven containers, local Ollama generation and embeddings, indexed CDC
  and NWS source retrieval, Kiwix search, actual Firefox map and source-library
  rendering, and essential checks after two reboots. The guest had no virtual
  NIC and container egress was blocked.
- The new deterministic chat guard returned the fixed safety notice without
  citations for five tested high-risk categories through both normal and
  streaming API paths. This only establishes those test cases; the keyword
  guard can miss differently phrased requests and is not a general safety
  system.
- Optional content-pack transfer was **SKIPPED** in this latest run because
  its fixture duplicated a pack already bundled. A separate prior run at
  source `1fb6806` passed offline transfer and Firefox rendering of the
  Middle Tennessee pack at zoom 13. That optional pack is not in the current
  baseline ISO.
- `make check test` passed after the latest source changes: 68 unit tests,
  content-pack validation, Python compilation, and shell syntax checks.
- The customer ISO currently retained at
  `/mnt/shared/fieldos-releases/fieldos-customer-1fb6806-nws.iso` is an older
  candidate (SHA-256
  `d312bbf785f23a9b0b909ca683ce02a884cc0a707dec532bef2e94d82e25f288`). It
  predates the server-side safety guard and must not be mistaken for an image
  containing the latest changes. Keep it until a replacement customer-mode
  install is tested.
- An interactive customer-mode installation passed earlier on the 1fb6806
  baseline: the operator selected the virtual disk and account, installation
  completed, the media handoff powered down, and the installed disk booted and
  passed service checks. Evidence:
  `/mnt/shared/fieldos-e2e/customer-nws-1fb6806/report.md`. It does not test the
  latest uncommitted safety changes.
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
| Fresh unattended offline installation | PASS, dirty source | Latest report above; rerun from clean commit for release provenance. |
| Offline provisioning and local services | PASS, dirty source | Firstboot complete; seven containers and local APT/images checked. |
| Chat and embedding inference | PASS, dirty source | Local generation and embedding endpoint passed. |
| High-risk chat guard | PASS for tested phrases only | Five categories plus streaming returned fixed notice/no citations; incomplete keyword coverage remains a release limitation. |
| Reference retrieval and Kiwix | PASS, limited | CDC/NWS indexed sources and Kiwix search; content breadth is small. |
| Offline map rendering | PASS at overview level | Firefox screenshot; bundled PMTiles max zoom 5. |
| Optional regional pack | PASS in prior run; SKIP latest | Prior zoom-13 transfer/render evidence; pack not included in current ISO. |
| Two-reboot persistence | PASS, dirty source | Services, model inventory, references and state checked after both reboots. |
| Interactive customer install | PASS on older baseline only | Earlier disposable QEMU installation; latest guard not yet included or tested. |
| Hardware adaptation | PARTIAL | CPU-only 8 GiB VM profile tested; no physical GPU validation. |
| Connected/LAN security | PARTIAL | Loopback bind and QEMU user-mode checks exist; peer LAN scan remains unverified. N.O.M.A.D. and Dozzle mount the Docker socket. |
| Content breadth | FAIL for field-readiness | Miniature Wikipedia, narrow emergency sources, and zoom-5 overview map are starter fixtures. |
| Redistribution review | BLOCKED | Complete review of software, model, map, and reference rights before any public binary distribution. |
| Clean-source release candidate | NOT YET TESTED | Commit current changes; rerun E2E and interactive customer installation from that exact clean revision. |

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

The repository branch currently contains three local commits beyond its public
remote and has uncommitted source/documentation changes. Publish only after
reviewing the exact commit range for secrets and private infrastructure data.
Do not publish an ISO until the clean-source E2E and separate customer-mode
installation gates pass. Current test and release storage is on `/mnt/shared`;
the latest report and screenshots are retained, and its disposable VM disk is
retired. Keep the existing older customer ISO until the replacement has passed
interactive installation, then retire that exact superseded file and record
the reclaimed space.

Never infer successful operation from an ISO build or container startup alone.
The current candidate is not a customer-ready emergency appliance.
