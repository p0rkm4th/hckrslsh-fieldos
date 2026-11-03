# Release status and process

The opening status and readiness table are the latest results. Dated entries
later in this file are historical snapshots and may describe the then-current
ISO or storage state; use the opening status and the latest dated sections for
present decisions.

The latest validated implementation is public at `origin/main`, source commit
`dc48319a4e29ea8a3c7412f113855f1b51734b1e`. `make check` and `make test`
passed all 49 tests on this implementation; log:
`/mnt/shared/fieldos-e2e/status-file-admin-readability-tests.log` (SHA-256
`346d7fc272e54c4375ea64262a5539aeb1815d45703be4292cbe53f725c9376f`). Firstboot
and embedded acceptance assertion syntax also passed; evidence:
`/mnt/shared/fieldos-e2e/status-admin-readability-syntax.log` (SHA-256
`e60e20ab5bb62b3cf5719e0ae4467b5dfb3552d6a79b82343d9f5840119860a3`). A fresh
Gitleaks scan through this commit found no findings; report:
`/mnt/shared/fieldos-e2e/gitleaks-dc48319.json` (SHA-256
`37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`). These
source checks do not establish installation behavior. A fresh ISO/guest
acceptance is still required for the diagnostics permission change.

On source commit `670b1a3`, `make check` and `make test` passed with 49 tests.
The captured log is
`/mnt/shared/fieldos-e2e/firstboot-log-permissions-tests.log` (SHA-256
`50048dfea09c614251a3f34479e5650c10ba320c11be2d994a5c6d169c4d3fe2`). Hardware
fixtures and workstation Vulkan detection are covered, but the existing
offline payload predates `vulkan-tools`, so installed-system Vulkan reporting
remains unverified. The earlier hardware evidence is in
`/mnt/shared/fieldos-e2e/vulkan-memory-d8fbc55-tests.log` and
`/mnt/shared/fieldos-e2e/hardware-vulkan-d8fbc55.json`.

Firstboot now writes the nonsecret provisioning status atomically as
`root:adm` mode `0640`, and makes `/var/lib/fieldos` searchable by `adm` at
mode `0710` without allowing directory listing. The acceptance check verifies
that the desktop account can read the status but cannot list the state
directory. The firstboot log remains `root:adm` mode `0640`; generated Compose
credentials remain `root:root` mode `0600`. These changes are not yet built
into an ISO or verified on a newly installed guest.

The most recent clean unattended VM acceptance remains the report below at
source `6c64ffd` plus a harness-only fix committed as `0b2fd8c`; it is not a
fresh acceptance of current source. The interactive customer ISO likewise
predates current source. `/mnt/shared` has 18 GiB free, below the 50 GiB E2E
preflight, so no current-source ISO or VM run was started. Existing VM disks
were preserved. Historical passes remain evidence only for their tested
source and environment; current-source release acceptance is open.

### Existing installed guest live recheck — 2026-11-03

The retained `20261103T102308Z` guest was started from its existing qcow2 and
rechecked through QEMU Guest Agent; no new disk or ISO was created. The guest
has no virtual NIC or default route. Provisioning status remained `complete`,
Docker and all seven Compose services were active, and checks passed for the
N.O.M.A.D. health endpoint, a generated Ollama response, a 768-dimensional
embedding, Kiwix catalog and search retrieval, regional-map registration, and
a 127-byte HTTP 206 map-tile range. Two further guest reboots produced changed
boot IDs; the same essential checks passed after each reboot. Evidence:
`/mnt/shared/fieldos-e2e/live-reboots-102308.txt` (SHA-256
`67155ba0984e480f3ae3c7d78ab62798ab11936d60a2cd5a94d47a928625d084`). This is
a follow-up on the prior installed guest from source `6c64ffd` with its
harness-only dirty-tree fix. It is not a fresh install or current-source
acceptance. The retained screenshot
`/mnt/shared/fieldos-e2e/20261103T102308Z-2314063/map-render.png` (SHA-256
`e17468e85fb8b98316205d34025183a8561213d54b1533adb6185360b9bcb83b`) was
visually inspected: Firefox shows the U.S. regional map at
`http://127.0.0.1:8080/maps`, with map controls, labels, and attribution. The
live follow-up itself did not capture a new browser render.

A separate, reversible QEMU SLIRP check on that guest confirmed the guest
could access the internet while the five published service ports refused
connections on its `10.0.2.15` interface and container egress remained blocked.
The temporary NIC was removed, and the guest returned to no external link or
default route with all services running. Evidence and limitations are in
[`docs/SECURITY.md`](SECURITY.md).

The active `fieldos-auto-test4` guest is not accepted: its firstboot unit is
failed with `ExecMainStatus=7`, Docker is active, and the N.O.M.A.D. endpoints
on ports 8080 and 8090 refuse connections. The unprivileged test account can
confirm the unit result but cannot read its root-only log, and no guest agent
is available; the cause is therefore unresolved. No repair was attempted.
The guest and its disk were preserved. Screenshot evidence of the unit status
and exit code is `/mnt/shared/fieldos-e2e/auto-test4-exit-status.png` (SHA-256
`d628b213c89f15a71481a2d89064d294a6ec46b73aa4230fd98f571bea5583a9`). This
failed run must not be counted as an automated acceptance pass.

At this checkpoint `/mnt/shared` has 18 GiB free (99% used), below the
50-GiB clean-E2E preflight. No additional ISO or VM disk was created. Existing
active VM disks were retained.

The public Git history was scrubbed because earlier release notes contained a
local username path and unrelated infrastructure labels. The one published
branch was rewritten with a lease; its tip tree is byte-for-byte unchanged.
The audit of rewritten history found no remaining username or
infrastructure-specific markers, no Gitleaks findings in its scan through
`df3566e`, no binary blobs, and no blobs larger than 10 MiB. Gitleaks report:
`/mnt/shared/fieldos-e2e/gitleaks-df3566e.json`. Historical commit IDs in
the dated records below refer to the pre-scrub graph and no longer resolve;
their retained reports, artifact hashes, and test results remain the evidence
for those historical runs. This scan does not substitute for licensing review.

Public history review at source commit `22ebcff396d4aeb948797591cd0742dec1f0e156`
scanned all 105 commits with Gitleaks and found no leaks. The redacted report
is `/mnt/shared/fieldos-e2e/gitleaks-22ebcff.json`. This check covers detected
credential patterns in Git history; it does not replace the separate review
for private infrastructure details or licensing.

That scan was refreshed through source commit
`3e7e0574883e04efa200a010bf42aeccd043564a`: Gitleaks scanned 109 public
commits and found no leaks. Redacted report:
`/mnt/shared/fieldos-e2e/gitleaks-3e7e057.json`.

The public-history scan was refreshed through source commit
`9b6c6b3a9e157d1cf44d888243b999ad046e6dcd`. Gitleaks scanned 113 commits and
found no leaks. Redacted report:
`/mnt/shared/fieldos-e2e/gitleaks-9b6c6b3.json`. `git ls-remote` confirmed this
was the public `main` head at scan time.

At source commit `bc47bb968714a89bc65e67ece25b79f17534cb28`, `make check` and
`make test` passed on the development workstation on 2026-11-03. The latter
ran all 46 unit tests, including content-pack safety, simulated hardware
profiles, image-license metadata, and test-disk retirement safeguards. Log:
`/mnt/shared/fieldos-e2e/source-bc47bb9-checks.log`. These checks do not build
or install an ISO and do not establish runtime or physical hardware acceptance.

At source commit `5c2349f4c65916d58b75ef113b28512c998dbbc4`, `make check` and
`make test` passed after adding a guard that prevents CPU fallback for models
whose manifest does not list CPU support. All 47 tests passed, including the
new GPU-only-model fixture. Log:
`/mnt/shared/fieldos-e2e/hardware-backend-compat-5c2349f.log`. This is simulated
selector coverage; it does not validate GPU inference or install a new ISO.

The same `make check` and 47-test suite passed on clean source commit
`bc1681f5a53c532ba5a1a5370388486ba9e9ccca` on 2026-11-03. The run recorded
`worktree_dirty=false`; its log is
`/mnt/shared/fieldos-e2e/source-bc1681f-checks.log`. Runtime ISO acceptance is
still separate and has not been repeated for this source.

At clean source commit `d8fbc5588afcae3dec5db439059aa7424d5bd22b`, `make check`
and all 49 tests passed on 2026-11-03. Coverage includes Vulkan device-local
memory-budget parsing, software GPU exclusion, and the rule that Vulkan
selection still requires explicit runtime validation. The live development
workstation detector reported 15.57 GiB for its NVIDIA GPU and a 7.06 GiB
device-local budget for Intel integrated graphics; CPU-only selection remained
in effect. Combined evidence is
`/mnt/shared/fieldos-e2e/hardware-vulkan-d8fbc55.json`; test log is
`/mnt/shared/fieldos-e2e/vulkan-memory-d8fbc55-tests.log`. This host run did
not validate model inference on either GPU. The existing payload predates the
`vulkan-tools` package request in this source, so installation-time detection
from the rebuilt payload remains unverified.

Latest verified gates (2026-11-03): a clean unattended offline acceptance run
passed, followed by a separate fresh-disk interactive customer ISO test. Both
UEFI QEMU guests had no virtual NIC and passed service, inference, retrieval,
map, and two-reboot checks. The interactive guest also rendered the regional
map in Firefox. Its installer displayed Ubuntu's media-removal prompt and
powered off; the test ejected the ISO and started the installed disk. This
interactive media handoff is an operator action. The automated installer
handoff is handled by `make test-e2e` and passed without manual guest input.

Unattended report, retained test guest, logs, and Firefox screenshot:
`/mnt/shared/fieldos-e2e/20261103T102308Z-2314063/`. Test ISO SHA-256 was
`c9f27ff1316bc5ca26a77eedb32053ebc14de694e744216897ed717fc6c4cfd7`. That run
used source commit `6c64ffd` with a dirty harness-only Wayland readiness fix;
the fix was committed in `0b2fd8c` immediately afterward. The harness removed
its temporary ISO and credentials.

The interactive customer candidate is
`/mnt/shared/fieldos-releases/fieldos-test-customer-0b2fd8c.iso`, SHA-256
`5295eeee5ec93098b1b71274e79991e5aeae44b9672deda46441db4fe37c52b8`, built
from clean source commit `0b2fd8c5de4f80ebad144a55e5b06e142115059c`.
`make iso-test` verified structure, BIOS/UEFI boot records, interactive
account/disk setup, and payload. Fresh 80 GiB `vda`, ISO on `sda`, 8 GiB RAM,
no NIC. Only the disposable qcow2 was selected for erase. Full evidence is at
`/mnt/shared/fieldos-e2e/customer-interactive-0b2fd8c-20261103/`.
On 2026-11-03, `make verify ISO=...` was rerun against this retained candidate;
BIOS/UEFI entries, interactive installer defaults, offline APT settings, and
required payload paths passed. Hash remained
`5295eeee5ec93098b1b71274e79991e5aeae44b9672deda46441db4fe37c52b8`. Output:
`/mnt/shared/fieldos-e2e/customer-iso-verify-0b2fd8c-20261103.txt`. This is a
read-only structural check of the old candidate and is not current-source
build or installation evidence.

Interactive runtime results: firstboot and all seven services passed;
N.O.M.A.D. health was `{"status":"ok"}`; Qwen returned
`FIELDOS_CUSTOMER_INSTALL_OK`; embedding output was 768 dimensions; Kiwix
retrieved the bundled New York reference; regional map registration, PMTiles
tile and HTTP range checks passed. Firefox rendered the regional United States
map in `map-render.png`. The service `.env` was `600 root:root`, Kiwix's
`/data` mount was read-only, and the desktop user was outside the Docker group.
Both `acceptance-reboot-*.txt` reports show the full checks passed after
changed boot IDs. No guest repair or password reset occurred; the ephemeral
test password was removed after validation.

The candidate is not a release binary and no ISO is published. QEMU results do
not establish physical hardware or GPU support. Physical customer installation
is not yet recommended. Open gates include complete Canonical and third-party
redistribution review, bridged-LAN reachability, physical hardware coverage,
content-pack licensing/attribution, and field recovery documentation. The map
fixture is a regional sample plus a world pack limited to zoom 5, not complete
customer cartography. Hardware support and expanded field content are
incomplete.

At this checkpoint `/mnt/shared` has about 18 GiB available. Do not create
another VM disk or ISO until capacity is increased or an evidence-retained,
stopped disposable disk is deliberately retired. The 78 GiB in
`<WORKSPACE>/build/out/` consists of the
`fieldos-auto-test2`, `fieldos-auto-test3`, and `fieldos-auto-test4` disks;
libvirt reports all three domains running, so they were preserved.

A public-history Gitleaks scan of all 85 commits through `42b6b8e` found no
credentials. A fresh scan of all 103 public-history commits through source
commit `71ade26` found no leaks; its redacted report is
`/mnt/shared/fieldos-e2e/gitleaks-71ade26.json`.

### Redis license correction — 2026-11-03

- The local image digest matches the pinned Redis digest and its image config
  reports `REDIS_VERSION=7.4.12`. The official Redis licensing notice says
  versions starting with 7.4 are RSALv2 or SSPLv1, not BSD-3-Clause. The
  manifest and [`CONTAINER-IMAGES.md`](CONTAINER-IMAGES.md) now record that
  version and license family. Read-only inspection evidence:
  `/mnt/shared/fieldos-e2e/redis-license-image-inspect-20261103.txt`.
- A regression test guards the image version, digest, Compose reference, and
  license metadata. `make check` and all 46 unit tests pass; output is at
  `/mnt/shared/fieldos-e2e/redis-license-review-tests.log`.
- The existing offline payload and customer ISO predate this correction and
  still contain the earlier manifest. The ISO remains private test material.
  Review RSALv2/SSPLv1 against the intended FieldOS distribution model or
  select a compatible replacement, then rebuild and rerun offline acceptance.

### E2E security assertions added — 2026-11-03

- Source commit `7d8b054576f9fdd53bbd26f15d4b68342391c757` extends each
  installed-guest acceptance run to reject privileged containers, added Linux
  capabilities, host networking/PID, non-loopback published ports, unexpected
  Docker socket consumers, a writable Dozzle socket mount, or credentials
  outside `0600 root:root`.
- The embedded guest-side Python was parsed and `make check` plus all 45 unit
  tests passed. A read-only execution of those assertions against the existing
  accepted E2E guest passed; evidence is
  `/mnt/shared/fieldos-e2e/security-runtime-followup-20261103.txt`. This is not
  a fresh current-source E2E run and does not cover a LAN peer scan.
- `/mnt/shared` has 18.6 GB free, below the 50 GiB clean-E2E preflight. All
  large test disks are active or retained by acceptance records; no candidate
  disk or release ISO was removed. A current-source ISO/VM acceptance run is
  still required.

### Diagnostics command runtime check — 2026-11-03

- The updated `fieldos-diagnostics.sh` was run read-only through the QEMU guest
  agent on the existing accepted disposable guest
  `fieldos-e2e-20261103t070244z`. It exited successfully and reported
  firstboot `Result=success`, recent journal/log output, Compose service state,
  storage usage, and N.O.M.A.D., Ollama, and Kiwix as healthy.
- Output is retained at
  `/mnt/shared/fieldos-e2e/fieldos-diagnostics-existing-guest-20261103.txt`
  (SHA-256 `a0ce935d218f4471d927409640e60d8e8a35b2c53bba21fa5976897158045656`).
  The guest disk was not changed. This verifies the diagnostics commands on an
  existing installation; the current source has not yet been installed in a
  fresh VM.

### Content-pack source milestone — 2026-11-03

- Source HEAD `43a1620a6192080152d138f98d34aa06611ad680` adds independent
  content-pack archives and an installed-system verification/storage command.
  All 46 unit tests and `make check` pass. The fixture suite exercises archive
  build, checksum and manifest validation, safe extraction, idempotent install,
  refusal to replace an existing version, symlink-path rejection, and exclusion
  of unlisted files from generated archives. Test
  output is retained at
  `/mnt/shared/fieldos-e2e/content-pack-tests-current.log`.
- The content-pack catalog remains empty. No customer pack is built or
  approved. The archive builder emits separate `.tar.zst` files under
  `/mnt/shared/fieldos-payload/content-packs/`; the core ISO contains the schema
  and command but not optional packs. Installed packs are stored immutably in
  `/var/lib/fieldos/content-packs/<id>/<version>`. Import into N.O.M.A.D.,
  Kiwix, maps, and GIS is not implemented, so this storage milestone does not
  satisfy field-content readiness.
- The existing customer ISO and its interactive acceptance predate this source
  commit; no ISO was rebuilt or tested with the content-pack command. The last
  clean unattended acceptance remains the earlier report at
  `/mnt/shared/fieldos-e2e/20261103T102308Z-2314063/report.md`, and the customer
  optical-media handoff remains partial. Do not infer ISO-level acceptance
  from unit tests.
- No large artifact was created. `/mnt/shared` has 18 GiB free (99% used);
  require the documented build headroom before rebuilding an ISO or starting a
  fresh disposable installation. Current E2E report and customer candidate
  paths and hashes are recorded above.

The specifically named legacy `fieldos-auto-test4` guest was rechecked on
2026-11-03 and is failed: `fieldos-firstboot.service` reports `failed`, Docker
is active but its local N.O.M.A.D. and Kiwix endpoints refuse connections, and
the root-only firstboot log cannot be read from its unprivileged terminal. Its
guest agent is unresponsive and an ACPI shutdown request did not stop it. The
VM and disk were left intact. This failed legacy run is not counted as the
separate clean E2E acceptance PASS. Diagnostic screenshots and limitations are
recorded in `/mnt/shared/fieldos-e2e/fieldos-auto-test4-diagnostic.md`. A
read-only follow-up screenshot on 2026-11-03 again showed the failed unit,
active Docker, unavailable service endpoints, and denied Docker socket access
for the guest user; evidence is
`/mnt/shared/fieldos-e2e/fieldos-auto-test4-followup-20261103.png`.
On a further read-only check, libvirt confirmed the guest has no NIC and the
guest agent is not connected. The displayed terminal again showed the failed
firstboot unit and refused N.O.M.A.D. and Kiwix probes. This session cannot
read the root-only firstboot log from the guest or authenticate for sudo, so
the provisioning cause remains undetermined and the guest was left unchanged.
Captured display evidence is
`/mnt/shared/fieldos-e2e/auto-test4-current-view.png` (PNG view) and
`/mnt/shared/fieldos-e2e/auto-test4-current.ppm` (QEMU capture).

### Earlier clean E2E rerun — 2026-11-03

- `make test-e2e` built test ISO SHA-256
  `5c123c4ef136f7f44ff4bcc7866e361bb51b72a5cca4318773fdbec0cd5a273a`, then
  installed Ubuntu unattended to a fresh 80 GiB qcow2 guest with 12 GiB RAM and
  no virtual NIC. Installer shutdown was detected and the installed disk
  booted through the guest agent without manual installer input or repair.
- Offline provisioning and all seven pinned images passed. N.O.M.A.D. health
  returned `{"status":"ok"}`; Ollama generated `FIELDOS_ACCEPTANCE_OK`; the
  embedding endpoint responded; Kiwix reference search, archive attribution
  and checksum, local map tiles, and regional map inventory passed. External
  container egress remained blocked.
- Firefox rendered the offline PMTiles map at 1280x800; the captured
  `map-render.png` had 69,563 sampled water pixels and 3,993 sampled colors.
  After each of two reboots, the boot ID changed and services, local inference,
  retrieval, and map checks passed again.
- Report, installer/firstboot logs, screenshot, and retained test guest disk:
  `/mnt/shared/fieldos-e2e/20261103T070244Z-2240395/`. The temporary ISO and
  test credentials were removed by the harness. This is a clean unattended
  QEMU acceptance pass. The separate fresh-disk interactive USB customer test
  is recorded below; CD-ROM behavior remains unresolved.

### USB customer handoff and persistence follow-up — 2026-11-03

- Candidate ISO: `/mnt/shared/fieldos-releases/fieldos-test-customer-280fda2.iso`,
  SHA-256 `f3b8f5c2ff5cb9bf98e3e07c98b1fce219195d7bb4fe4490a38351cb145c751d`.
  The ISO was attached as USB install media to a disposable UEFI QEMU guest;
  target `vda` was a qcow2 under `/mnt/shared` and there was no virtual NIC.
- The initial blank-disk install completed but, with USB media still attached,
  firmware returned to the installer. We then explicitly selected “Erase
  Ubuntu and install” on the same disposable target. The installer media was
  detached during its restart request. The guest remained running and booted
  the installed system to GDM without a host-side VM start. The target disk
  selection and installer-media block-device details are in `review.png`,
  `block-devices.txt`, and `usb-removal.txt`.
- This is useful evidence for the expected USB removal handoff, but it is not
  reported as a clean fresh-disk pass: the successful handoff followed an
  erase-and-reinstall on the already-installed test disk, and media removal
  was an explicit test action. CD-ROM behavior remains different and unresolved.
- On the installed guest, firstboot completed and seven services ran. N.O.M.A.D.
  returned `{"status":"ok"}`; Qwen generated
  `FIELDOS_CUSTOMER_INSTALL_OK`; the embedding endpoint returned 768 values;
  Kiwix search retrieved the New York reference; world and regional PMTiles
  checks passed, including an HTTP byte range. No external NIC/default route
  was present. After two in-guest reboots, the boot IDs changed and the same
  health, inference, embedding, retrieval, and map checks passed. The user was
  outside the Docker group, Kiwix content was mounted read-only, and the
  generated service environment file was mode 0600 root:root.
- Full evidence, including screenshots and guest disk:
  `/mnt/shared/fieldos-e2e/customer-usb-280fda2-20261103/`. Runtime output is in
  `acceptance-after-usb-boot.txt`, `acceptance-reboot-1.txt`, and
  `acceptance-reboot-2.txt`. Browser map rendering evidence remains from the
  clean automated run at
  `/mnt/shared/fieldos-e2e/20261103T060129Z-2217020/map-render.png`; this USB
  guest verified map APIs and tile delivery but did not independently repeat
  the browser screenshot test.

### Fresh blank-disk customer USB installation — 2026-11-03

- The same unpublished customer ISO was installed to a newly created blank
  80 GiB qcow2 target (`vda`) in UEFI QEMU with 8 GiB RAM and no virtual NIC.
  Interactive account configuration used an ephemeral test credential; the
  password was never retained. Installer review showed only `vda` would be
  erased and both USB-media partitions on `sda` would remain unchanged.
- After “Restart now,” the USB installer media was removed at the prompted
  media-removal stage. The VM stayed running and booted the installed target
  to GDM; no host start or guest repair was required. This passes the fresh
  blank-disk USB customer install/handoff gate with the expected operator
  media-removal action. It does not establish CD-ROM handoff behavior.
- Firstboot completed; all seven containers ran. N.O.M.A.D. returned
  `{"status":"ok"}`; Qwen generated `FIELDOS_CUSTOMER_INSTALL_OK`; embeddings
  returned 768 values; Kiwix search retrieved the bundled New York reference;
  world and regional PMTiles API/tile/range checks passed. The guest had no
  external NIC/default route. After two consecutive reboots, the same full
  checks passed with changed boot IDs. Browser map rendering passed in the
  clean E2E run above, not in this interactive guest.
- Full test report, screenshots, firstboot/runtime logs, scripts, QEMU records,
  and guest disk: `/mnt/shared/fieldos-e2e/customer-usb-clean-20261103/`.
  Candidate ISO SHA-256 remains
  `f3b8f5c2ff5cb9bf98e3e07c98b1fce219195d7bb4fe4490a38351cb145c751d`.
- This is a QEMU customer-install test, not physical hardware validation.
  No release binary was published.

### Fresh clean E2E after payload manifest repair — 2026-11-03

- The first rerun from the previously prepared payload failed because its
  archive predated the reference manifest added to source; the installed
  guest lacked `/var/lib/fieldos/payload/manifests/references.json`. That FAIL
  report, logs, and screenshots are retained at
  `/mnt/shared/fieldos-e2e/20261103T054638Z-2209484/`.
  After review and a successful clean rerun, its stopped disposable qcow2 was
  removed to reclaim space; no active VM or test evidence was removed.
- Rebuilt payload SHA-256:
  `1ff46b13ae6fb2beefa039f69ba6f7852d17bfcd7d87b1e83b650c891c76a8ce`.
  The prior stale payload and its matching hash are retained under
  `20261103T054638Z-2209484/stale-payload/` for reproducibility. The rebuilt
  archive includes and verifies `manifests/references.json`.
- A new clean-source `make test-e2e` run passed all checks, including archive
  size/SHA-256, N.O.M.A.D. health, Qwen generation, 768-dimension embeddings,
  Kiwix retrieval, all 7 image digests, 1,174 image notice files, 3 source
  offers, PMTiles, real Firefox map rendering, blocked container egress, and
  service/model/content/map persistence after two reboots.
- Report:
  `/mnt/shared/fieldos-e2e/20261103T060129Z-2217020/report.md`. The test ISO
  and temporary credentials were removed by the harness; the stopped 33 GiB
  disposable qcow2 and logs remain. No release binary was published.

### Earlier customer installer rerun — R2, 2026-11-03

- Candidate ISO: `/mnt/shared/fieldos-releases/fieldos-test-customer-sourceoffer-709c893.iso`,
  SHA-256 `b3baf28dfb6be78f9f701fb53fd37e9cc083a205e05705da0bb2abfa123e7dc4`.
- Fresh 80 GiB UEFI qcow2 guest, no virtual NIC. Interactive account entry
  produced the intended `fieldos` user, `fieldos-r2` hostname, and selected
  only disposable `vda`. The installer reached its remove-media prompt and
  opened the virtual CD tray. Pressing Enter powered off the guest again;
  `virsh start` was required to boot the installed disk. This repeats the
  unresolved customer handoff issue. Do not count this as a clean unattended
  installer PASS.
- After the host start, firstboot completed. Seven containers ran; N.O.M.A.D.
  health, local Qwen generation, 768-value embeddings, Kiwix search, real
  PMTiles tile retrieval, regional map registration, and Firefox map rendering
  passed. The installed guest had no external NIC or default route. The
  repeated post-reboot run passed all essential checks after two changed boot
  IDs. The earlier exact-marker inference check on reboot 2 failed because the
  model paraphrased the prompt; the test now uses temperature zero and an
  explicit exact-token request, which passed on retry. No guest repair was
  performed between that failure and the passing retry.
- Installed payload integrity check matched all 7 image digests, 1,174
  candidate notice files, and 3 source-offer files by size and SHA-256.
- Evidence, screenshots, logs, and retained VM disk:
  `/mnt/shared/fieldos-e2e/customer-sourceoffer-709c893-r2/`. The VM is a
  disposable test guest; no test credentials are retained. The candidate ISO
  and guest disk are not published.

### Network-enabled service boundary check — 2026-11-03

- A QEMU user-network clone of the shut-off customer guest received DHCP and
  a default route. Guest HTTPS egress worked; N.O.M.A.D. container egress to
  the same public endpoint remained blocked.
- `8080`, `9999`, `6333`, `8090`, and `11434` were published only on guest
  loopback. Requests to those ports through the guest NIC address failed,
  while local N.O.M.A.D. health succeeded. The captured socket inventory had
  no FieldOS service listener on `0.0.0.0` or the guest NIC.
- This is a guest self-address test under QEMU user networking, not a bridged
  LAN or guest-to-guest scan. Creating a temporary libvirt bridge was denied
  by host permissions (`Operation not permitted`), so actual LAN reachability
  remains open. Evidence: `/mnt/shared/fieldos-e2e/customer-sourceoffer-709c893-r2/network-review.md`
  and `network-review.txt`.

### Container notice and corresponding-source follow-up — 2026-11-03

- The seven pinned OCI images were exported from the local Docker daemon to
  temporary archives under `/mnt/shared`, scanned layer by layer, and the
  temporary image archives removed after collection. The retained candidate
  index contains 1,174 unique filename-matched notice files across 2,367
  image-layer/path occurrences (11,449,948 bytes). Redis, Dozzle, and Kiwix
  produced zero filename matches; that does not clear their notice or source
  obligations. SBOM and extracted notice evidence is at
  `/mnt/shared/fieldos-e2e/repository-review-233b980/`.
- The exact pinned Project N.O.M.A.D. image contains Debian Ghostscript,
  libgs10, and libgs10-common `10.0.0~dfsg-11+deb12u8`; its bundled copyright
  text identifies AGPL-3+. The exact Debian source descriptor and source
  archives were downloaded, signature-checked as cryptographically good, and
  matched against the descriptor's archive sizes and hashes. Local trust-chain
  validation for that signing key remains open; evidence is under
  `sources/ghostscript/` in the repository-review directory.
- Source now pins those three source-package files by HTTPS URL, size, and
  SHA-256 and bundles them in future payload builds. The all-layer notice
  collector also adds path/hash indexes to future payloads. These changes are
  source-only: no new ISO or payload was built, and the existing ISO does not
  contain the new source offer or indexes.
- `make check`, `make test` (33 tests), JSON manifest parsing, and
  `git diff --check` passed. Gitleaks scanned the 52-commit public Git history
  through source commit `f9f4200` with zero findings; the only later change in
  this follow-up is this release-note entry. No ISO or payload was published.
- `/mnt/shared` had 69 GiB available after the temporary image archives were
  removed. The current test ISO remains
  `/mnt/shared/fieldos-releases/fieldos-test-customer-main-a4eebb8.iso`; no new
  release candidate was created.

### Latest clean automated acceptance — 2026-11-03

- Source: clean commit `4d4fccc76ac8fd1f559374694a38a2c682c2dc5a`.
- Test ISO SHA-256:
  `6cf0086fb215989d7bf75caf7a4719fecfb3fa1ce62076df4e9a77a86b449526`.
- Fresh 80 GiB UEFI qcow2 guest, no virtual NIC. Ubuntu installed
  unattended and the installer powered off normally. Offline APT provisioning
  loaded all declared local images; firstboot completed. N.O.M.A.D. returned
  `{"status":"ok"}`; Qwen generated `FIELDOS_ACCEPTANCE_OK`; embeddings,
  Kiwix library/search, source and archive checks, world and regional PMTiles,
  blocked container egress, and CPU model selection passed.
- Firefox rendered the bundled regional U.S. map in a 1280x800 screenshot
  (`map-render.png`); 69,563 water pixels and 3,993 sampled colors passed the
  viewport check. Essential service, inference, content, and tile checks passed
  after two reboots with changed boot IDs.
- Full report, installation/firstboot logs, screenshots, and stopped guest disk
  remain at `/mnt/shared/fieldos-e2e-4d4fccc/20261103T025413Z-2144474/`.

### Earlier current-source interactive customer ISO acceptance — 2026-11-03

- Candidate ISO: `/mnt/shared/fieldos-releases/fieldos-test-customer-main-a4eebb8.iso`;
  SHA-256 `47fdf3f07773bb61f2bca321513f875ade39f6a01bf51afba98fb282529c3b28`.
  The source tree matches the code used in the clean unattended acceptance
  above; the intervening source commits changed only these release/installation
  documents. ISO structure, BIOS/UEFI boot records, installer configuration,
  and bundled payload were verified when built.
- Fresh 80 GiB UEFI QEMU guest with no virtual NIC, a disposable `vda`, and the
  ISO on virtual `sda`. Interactive disk and account setup completed. At the
  remove-media prompt, the virtual ISO was ejected and Enter pressed; firmware
  booted the installed target to GDM without a host-side VM start. Firstboot
  reached `status=complete` and loaded all seven local images without registry
  access.
- N.O.M.A.D. `/api/health` returned `{"status":"ok"}`; bundled Qwen generated
  `FIELDOS_CUSTOMER_INSTALL_OK`; the bundled embedding model returned a
  768-element vector; Kiwix catalog and New York article search succeeded;
  world PMTiles returned a 66,795-byte tile; the regional pack appeared in the
  map API and served a valid HTTP range. Firefox rendered the regional map in
  the clean unattended run above, built from identical application, payload,
  and provisioning code. The installed guest was isolated from external
  networking; Docker's internal bridges/veth devices are present as expected.
- After each of two in-guest reboots, all seven containers returned and the
  health endpoint, chat generation, embeddings, Kiwix search, and map tile/API
  checks passed. On the second boot an immediate API probe raced container
  startup and got a connection reset; the endpoint became healthy moments
  later, and the full post-reboot check passed on retry with no repair or data
  change. The mounted Kiwix content is read-only, `/opt/fieldos/services/.env`
  is `0600 root:root`, and desktop user `fieldos` is not in the Docker group.
- Report, QGA acceptance logs, screenshots, and guest disk are under
  `/mnt/shared/fieldos-e2e/customer-iso-current-main-a4eebb8/`. The guest disk
  is retained and the VM remains running for inspection. ISO and VM disk are
  test artifacts, not published release binaries. This pass validates the
  customer installer path in a disposable VM, not a physical machine or a
  network-enabled LAN configuration.

### Earlier customer ISO attempt — offline R1, 2026-11-03

- Candidate: `/mnt/shared/fieldos-releases-03b6552/fieldos-test-customer-offline-r1.iso`
  (11,956,584,448 bytes), SHA-256
  `1bedf8286bfa825ddd5a35dba727a27b332beee2fad4e30d043f1fd90131f8cf`.
- `make check`, 28 unit tests, ISO build, and ISO structure/BIOS/UEFI
  verification passed. The candidate contains the same installer config now
  committed in `4d4fccc`, setting `apt.geoip: false` and
  `apt.fallback: offline-install`; the current verifier confirms both keys.
- Initial navigation batched QMP pointer movement, press, and release. Later
  input testing showed separate press and release calls were needed. The earlier
  “disabled Next” observations therefore do not establish a FieldOS, storage,
  network, or stock-Ubuntu installer defect. Those comparisons are
  inconclusive; their reports have been amended with this limitation.
- A later corrected interactive run with this candidate completed installation;
  see R2 below. The candidate remains a local test artifact, not an approved
  distribution binary.

### Earlier interactive customer ISO diagnostic — R2, 2026-11-03

- Candidate: `/mnt/shared/fieldos-releases-03b6552/fieldos-test-customer-offline-r1.iso`,
  SHA-256 `1bedf8286bfa825ddd5a35dba727a27b332beee2fad4e30d043f1fd90131f8cf`.
- A fresh UEFI QEMU guest had no network interface and only a disposable target
  disk (`vda`) plus installer media. With separate QMP pointer press/release
  events, interactive disk and account setup completed, followed by the
  installer’s “Installation complete” screen. At the remove-media prompt, the
  virtual CD was ejected and Enter pressed; the VM powered off. A host start
  booted the installed target to GDM. The install and target-disk boot are
  observed, but automatic handoff is not verified and needed host action.
- The guest agent did not connect at GDM. The temporary password was not
  retained; services, local inference, and browser map rendering were not
  checked in this run. This recovered VM is not a clean automated customer
  acceptance pass. Evidence and retained guest disk:
  `/mnt/shared/fieldos-e2e/customer-iso-ui-r2/`.
- The reason the remove-media/Enter step powers the guest off is unresolved.
  Treat eject timing only as a hypothesis; this run does not verify a fix.

### Earlier artifacts and storage snapshot — 2026-11-03 (superseded)

This snapshot predates the latest customer ISO, fresh-disk USB test, and clean
E2E rerun documented at the top of this file.

- Clean unattended E2E report and screenshots: `/mnt/shared/fieldos-e2e-4d4fccc/20261103T025413Z-2144474/` (32 GiB sparse guest disk retained).
- Interactive customer ISO evidence and recovered guest disk:
  `/mnt/shared/fieldos-e2e/customer-iso-ui-r2/` (about 33 GiB, including the
  31 GiB sparse qcow2). The VM reached GDM after host start and was then
  gracefully shut down; the qcow2 remains preserved as diagnostic evidence.
- Current local customer ISO candidate:
  `/mnt/shared/fieldos-releases-03b6552/fieldos-test-customer-offline-r1.iso`,
  SHA-256 `1bedf8286bfa825ddd5a35dba727a27b332beee2fad4e30d043f1fd90131f8cf`.
  It is an unpublished test candidate, not a release binary.
- Bundled test payload: `/mnt/shared/fieldos-payload-34f9604/` (5.1 GiB);
  current build temporary root `/mnt/shared/fieldos-build-03b6552/` (empty).
- At this documentation update, `/mnt/shared` had 49 GiB free (96% used).
  Check available space before creating further ISOs or VM disks. Active host
  VMs and unrelated storage were left untouched.
- Source and documentation are maintained in the public Git repository; no
  ISO, model weight, VM disk, or container archive is published there.

## Acceptance evidence

### Earlier current-source R5 interactive installation — 2026-11-03

- Candidate ISO: `/mnt/shared/fieldos-releases/fieldos-test-customer-r5.iso`;
  SHA-256 `8b121916cd13af315d268cae16643eab06244a5b3a256662767650cbf2b52ee2`.
  `make verify` confirmed ISO structure, BIOS/UEFI boot records, installer
  configuration, and bundled payload. Extracted NoCloud data contains
  `shutdown: reboot` and keeps identity/storage interactive.
- Fresh 80 GiB UEFI QEMU guest, no network adapter. The installer review
  identified only disposable target `vda`; interactive user and disk setup
  completed. Firstboot reached `status=complete`; all seven Compose services
  ran; N.O.M.A.D. health returned `{"status":"ok"}`; Qwen generated
  `FIELDOS_R5_OK`; embeddings returned 768 values; Kiwix retrieved the bundled
  New York article; the regional map API listed the U.S. PMTiles pack and the
  world PMTiles archive returned a 66,795-byte tile. No default route existed.
- Two in-guest reboots changed the boot ID. After each, all seven containers,
  N.O.M.A.D. health, and local inference recovered; `.env`, bundled ZIM, and
  regional map SHA-256 values were unchanged. See `service-checks.txt` and
  `reboot-checks.txt` in `/mnt/shared/fieldos-e2e/customer-r5-20261103/`.
- Handoff remains PARTIAL: “Restart now” reached the remove-media prompt;
  after the medium was absent and Enter was pressed, the VM powered off despite
  the explicit reboot setting. A host start booted the installed target to
  GDM. This is an interrupted handoff and is not a clean automated installer
  PASS. R5's map was checked at the service/API layer; the actual browser render
  evidence remains the R4 Firefox screenshot below.
- Test screenshots and reports are retained under
  `/mnt/shared/fieldos-e2e/customer-r5-20261103/`. The test account password
  was generated temporarily and was not saved in the evidence directory.

### Modular content-pack validation — 2026-11-03

- Added a standard-library validator for staged pack manifests, source IDs,
  artifact path containment, exact sizes and SHA-256 values, geography bounds,
  and emergency-reference review metadata. `make check` runs it against the
  repository catalog; fixture tests also reject bad hashes, traversal paths,
  undeclared sources, and unreviewed emergency packs.
- `make check`, `make validate-content-packs`, and all 28 unit tests passed.
  The catalog remains intentionally empty; no customer pack data or new runtime
  dependencies were added.

### Earlier current-source unattended acceptance — 2026-11-03

- Run report: `/mnt/shared/fieldos-e2e/20261103T002115Z-2083709/report.md`.
- Source: commit `945751325ab80b1acadb870f0754f3fc7a378fab`, clean worktree.
  Test ISO SHA-256: `78c96f8d37fe6d08804de62d0fd8c69dd01801e0e1a0382e6ea9493b1a2174e1`.
- A fresh 80 GiB UEFI qcow2 installed unattended with no virtual NIC. Offline
  provisioning completed; all seven containers ran; N.O.M.A.D. returned
  `{"status":"ok"}`; Qwen generated `FIELDOS_ACCEPTANCE_OK`; the embedding
  endpoint returned a vector; Kiwix retrieved the bundled New York article;
  and the world plus bundled U.S. regional PMTiles were served. Firefox
  rendered the regional map over the offline basemap. Container egress was
  blocked. Service, inference, retrieval, and tile checks passed after two
  reboots.
- Browser screenshot: `/mnt/shared/fieldos-e2e/20261103T002115Z-2083709/map-render.png`.
  Installer, firstboot, service, and test evidence remain beside the report;
  the temporary ISO and test credentials were removed by the harness.

### Reproducibility and source hygiene update

- Source commit `d8c50306af0c305403b08f100201800c743b74dd` pins the Protomaps
  source build metadata and verifies both bundled Ollama manifests and exact
  model-layer SHA-256/size before preparing a payload. The pins were checked
  against `/mnt/shared/fieldos-payload/offline-payload.tar.zst`; no new payload
  or ISO was built for this source-only change.
- `make check` and all 13 unit tests passed after the change. Gitleaks scanned
  all 17 reachable commits with no findings; the tree is clean and `main` is
  synchronized with `origin/main`.
- Offline APT archive inventory for payload SHA-256
  `5927727201adcaa0da822975fa76d65f08046f3d0625b018a1c24e0689aae273` is at
  `/mnt/shared/fieldos-e2e/package-license-audit-20261102/`. It covers 61
  packages and includes 59 extracted notice texts with per-file hashes. Two
  packages contain no bundled copyright file; same-source notice tracing is
  recorded separately, with the GCC descriptor signature explicitly unverified.
  This is not a license/SBOM clearance. The extracted package cache was removed
  after recording the inventory and notice bundle.

### Hardware inventory update

- The detector now reports physical CPU cores where Linux exposes topology
  and reports `MemAvailable` separately from installed memory. Model-selection
  budgeting is unchanged: it reserves the configured amount from installed
  RAM; the added available-memory field is diagnostic.
- `make check` and all 19 unit tests passed after the follow-up updates. A physical development-laptop
  spot-check observed the NVIDIA driver and GPU, Intel integrated graphics,
  NVMe, battery, CPU, and RAM. The evidence is
  `/mnt/shared/fieldos-e2e/hardware-detection-20261102/`. The latest detector
  source also ran successfully inside the existing installed, NIC-free E2E
  guest via QEMU guest agent; it reported only the 80 GiB `vda` disk and
  excluded Snap loop devices and the virtual DVD. This is a detector smoke
  check, not a fresh installation test. GPU inference remains unvalidated
  because Docker has no NVIDIA runtime/toolkit configured.
- The 2026-11-03 current-source E2E below rebuilt the test ISO from this
  detector revision and confirmed the CPU profile in a fresh disconnected
  install. This validates the CPU path only; simulated hardware fixtures are
  not physical GPU validation.
- The acceptance harness now records the source commit and dirty/clean
  worktree state in new reports; unit tests cover both Git-query success and
  unavailable-Git behavior. Existing reports were generated before that
  reporting improvement.

### Offline unattended installation

- Prior passing report:
  `/mnt/shared/fieldos-e2e/20261102T214900Z-2020461/report.md`.
- Test ISO SHA-256:
  `c2177b7554ad69b13c88f4db28a88aafbdc536b5a78f1aaa175a21b5f80f9422`.
- A fresh 80 GiB qcow2 installed in UEFI mode without a virtual NIC.
  Offline APT, seven local containers, N.O.M.A.D., local chat and embedding,
  Kiwix, PMTiles serving, Firefox map render, blocked external egress, and two
  reboots passed.

### Earlier current-source unattended acceptance

- Run report: `/mnt/shared/fieldos-e2e/20261102T232645Z-2057919/report.md`.
- Test ISO SHA-256:
  `cc74e925baaab29390eeaee48a677c4a3eccad58cc8d71e109a88a9db0e40de0`.
- A fresh 80 GiB UEFI qcow2 installed unattended with no virtual NIC. N.O.M.A.D.
  returned `{"status":"ok"}`; Qwen generated `FIELDOS_ACCEPTANCE_OK`; the
  embedding endpoint returned a vector; Kiwix catalog and reference search
  succeeded; PMTiles tile/range requests succeeded and Firefox rendered the
  map. Container egress was blocked. The report records PASS after two reboots.
- Screenshot: `/mnt/shared/fieldos-e2e/20261102T232645Z-2057919/map-render.png`.

### Interactive customer installation and clean restart

- R2 ISO:
  `/mnt/shared/fieldos-releases/fieldos-test-customer-r2.iso`.
- SHA-256:
  `2155fb0b6b498d053bdad98147e0d846ef84b87fb9107d1727e7f1c6b9b3d0f7`.
- Using the FieldOS GRUB entry, a fresh 80 GiB qcow2 installed interactively
  with a temporary user identity and no NIC. Firstboot completed, seven
  services ran, local chat and embedding worked, Kiwix retrieved the test
  article, and map requests succeeded. Firefox rendered the regional U.S. map.
- The installer reached its explicit “remove installation medium” prompt.
  Media was ejected only then; Enter booted the installed target disk to GDM.
- Services and data checks passed after two consecutive reboots. The generated
  `.env`, ZIM, and regional PMTiles hashes remained unchanged. Evidence:
  `/mnt/shared/fieldos-e2e/customer-correct-entry-20261102/report.md`.
- The first attempt at a service count used `json.load` on Docker Compose JSON
  Lines and falsely failed that single harness check. A direct corrected check
  found all seven containers running; details are in `compose-verified.txt`.

### GRUB default correction and R3

A separate installation through the upstream `Try or Install Ubuntu` entry
installed plain Ubuntu without `/opt/fieldos` or the FieldOS firstboot unit.
That identified a real customer boot-selection hazard. Source now makes
`Install Hckrslsh FieldOS (interactive)` the default GRUB choice while keeping
the upstream options available. After the countdown, the FieldOS installer
still presents interactive disk and account setup.

- R3 candidate:
  `/mnt/shared/fieldos-releases/fieldos-test-customer-r3.iso`.
- Size: 11.1 GiB (11,956,518,912 bytes).
- SHA-256:
  `e07f39a20e64fc1127086739afce39fbbffc12220f8cff126509072c32f7e899`.
- `build/verify-iso.sh` passed BIOS/UEFI boot records, payload, NoCloud
  configuration, FieldOS boot entry, and default selection; SHA-256 sidecar
  verified. A fresh 80 GiB disposable UEFI guest completed the R3 interactive
  install with account and disk selection. The clean remove-media/Enter handoff
  booted to the installed desktop. Offline firstboot loaded all seven local
  images, N.O.M.A.D., chat, embedding, Kiwix, and map endpoints passed, and
  Firefox rendered the regional map. Essential checks and content hashes
  passed after two reboots.
- Interactive install report and screenshots:
  `/mnt/shared/fieldos-e2e/customer-r3-bootcheck-20261102/report.md`.
- ISO and test evidence are local and unpublished.

### Earlier current-source interactive customer installation and R4

- Candidate ISO: `/mnt/shared/fieldos-releases/fieldos-test-customer-r4.iso`.
- Size: 11,956,518,912 bytes. SHA-256:
  `89584420e6d8b78ff63db650bb9eca22cdfc61e19502c71b510e9f5a516036c1`.
- Built from clean source commit
  `fa972ec7ac6069069db9db24baba27efd5c9f79f`. ISO verification passed the
  BIOS/UEFI boot record, interactive installer configuration, and payload
  checks.
- A fresh 80 GiB no-NIC UEFI guest completed interactive target disk and
  account setup, offline firstboot, and boot to GDM. At the remove-media prompt
  the virtual CD was already empty; pressing Enter powered off the guest, and
  an explicit host start was needed to boot the installed disk. The R4
  interactive automatic-reboot handoff is therefore partial.
  All seven services ran; N.O.M.A.D., Qwen inference, 768-dimensional
  embeddings, Kiwix retrieval, and Firefox rendering of the U.S. regional map
  passed. The same service, inference, retrieval, map-tile, and persistence
  checks passed after two reboots; `.env`, ZIM, and regional-map hashes remained
  unchanged.
- Report and evidence: `/mnt/shared/fieldos-e2e/customer-r4-20261103/report.md`.
  Browser screenshot: `/mnt/shared/fieldos-e2e/customer-r4-20261103/map-browser.png`.
- R4's binary was removed after R5 superseded it. Older R2/R3 and pre-R4 test
  ISO binaries were also removed; their historical checksums and test reports
  remain documented. R5 is the only current ISO candidate, and it is not a
  distribution release.

### Latest source-only content provenance update — 2026-11-03

- Commit `34f96042e2b7ac3a59c5642f8574402a9f9a70c8` adds a pinned ZIM source,
  size and SHA-256 manifest, a user-visible offline source/limits guide, the
  CC BY-SA 4.0 text, and firstboot installation of those notices. A byte-for-byte
  comparison against the pinned upstream N.O.M.A.D. v1.35.1 file passed; evidence
  is `/mnt/shared/fieldos-e2e/zim-provenance-review-20261103.md`.
- The archive is still a test fixture. Per-entry and embedded-media license
  clearance is open. The clean `4d4fccc` E2E run checked that the installed
  source guide and bundled archive match their recorded checksum; it does not
  establish redistribution clearance.
- The working tree is clean and `main` is pushed to `origin/main`. The current
  repository audit is under `/mnt/shared/fieldos-e2e/repository-review-34f9604/`.

## Readiness

| Component | Status | Evidence |
|---|---|---|
| Unattended offline OS installation | PASS | Latest clean run `/mnt/shared/fieldos-e2e/20261103T070244Z-2240395/report.md`, source commit `ae1d18b` |
| Interactive customer installation | PASS (QEMU, USB) | Fresh blank 80 GiB target; report and evidence: `/mnt/shared/fieldos-e2e/customer-usb-clean-20261103/report.md` |
| Clean installer media/restart handoff | PASS (USB with prompted media removal) | Guest booted to GDM without host start after USB removal; CD-ROM handoff remains unresolved |
| Customer ISO default selection | PASS | FieldOS default selected; corrected QMP press/release input navigated UI |
| Offline provisioning and services | PASS | Current interactive guest: firstboot complete; all seven pinned containers loaded locally and ran |
| N.O.M.A.D. and inference | PASS | Current guest health response, chat generation marker, and 768-element embedding vector |
| Knowledge library and maps | PASS | Current Kiwix retrieval and PMTiles tile/range checks; Firefox render in matching-code clean E2E report |
| Reboot persistence | PASS | Fresh blank-disk customer USB guest passed the full service, inference, retrieval, and map API/tile checks after two consecutive reboots |
| ISO release | BLOCKED | Test candidate verified; distribution/attribution, physical hardware coverage, and LAN peer review remain; binary unpublished |
| Hardware adaptation | PARTIAL | CPU validation; fixtures simulated; no physical GPU test |
| Container privilege review | PARTIAL | Runtime inspect, loopback ports, root-only secrets; N.O.M.A.D. Docker socket is root-equivalent by upstream design |
| Network-enabled exposure | PARTIAL | User-mode NIC, local endpoint, blocked egress, and NIC-address port checks; LAN peer scan pending |
| Redistribution and attribution | BLOCKED | See `REDISTRIBUTION.md`: Ubuntu modification/trademark review and exact package/image/model/ZIM notices remain unresolved |
| Public Git history | PASS (Gitleaks) | Full history scan covered 67 commits with zero findings; evidence: `/mnt/shared/fieldos-e2e/repository-review-customer-20261103/gitleaks-history.json`. Earlier private infrastructure indicator review: `/mnt/shared/fieldos-e2e/repository-review-233b980/` |
| Content packs | PARTIAL | Independent archive builder and immutable verified storage command; 46 unit tests pass. Catalog empty; application activation, approved field content, and ISO-level test remain open |

## Remaining release gates

1. Resolve and complete the itemized clearance work in
   [`REDISTRIBUTION.md`](REDISTRIBUTION.md), including Canonical's modified
   Ubuntu trademark requirement, exact package and image SBOMs, and content
   attribution/checksums.
2. Validate supported physical hardware and document incompatibilities. GPU
   fixture tests and detector observations do not establish physical
   acceleration; the verified acceptance backend is CPU.
3. Complete guest-to-guest LAN reachability testing on an isolated virtual
   network, and preserve the already completed no-NIC and user-mode-network
   tests as distinct evidence.
4. Continue documenting and testing customer-facing troubleshooting/recovery
   instructions. Preserve source revision, build inputs, test reports,
   checksums, and known limitations.

The latest customer installer run is the partial R2 attempt documented below.
The current clean unattended acceptance and Firefox screenshot are under
`/mnt/shared/fieldos-e2e/20261103T060129Z-2217020/`. The expanded/full ISO must
wait until the remaining release gates pass. Never commit ISOs, model weights,
credentials, VM disks, or downloaded image archives.

### Latest clean automated acceptance and source-offer payload — 2026-11-03

This dated entry supersedes older “latest” claims above. Earlier records remain
as historical evidence, including interrupted runs; an interrupted or manually
recovered run is not counted as a clean PASS.

- Source commit: `709c8932ba39184be9a24e40df5939b958d62e79` (clean worktree;
  synchronized with `origin/main` at test time).
- Test report and retained evidence:
  `/mnt/shared/fieldos-e2e-sourceoffer-r2/20261103T044051Z-2183912/report.md`.
  After review, the stopped 80 GiB qcow2 was removed on 2026-11-03 to reclaim
  space; the report, logs, and Firefox `map-render.png` remain. Newer clean
  E2E guest disks remain at `20261103T070244Z-2240395/` and
  `20261103T074611Z-2255858/`. The ephemeral ISO and temporary user-data were
  removed after the run.
- The test-only ISO hash was
  `ffddec1fab1ba452684d1dca69eeb322bbe592320a397b09e8d8abaadad19b6d`.
  The installer powered off after unattended installation; the harness
  automatically booted the installed system and completed checks without
  keyboard/OCR handoff or manual repair.
- Ubuntu installation, local APT provisioning, all seven local container
  images, N.O.M.A.D. health (`{"status":"ok"}`), Qwen CPU generation
  (`FIELDOS_ACCEPTANCE_OK`), 768-value embeddings, Kiwix catalog/search, and
  offline world/regional map APIs passed with no virtual NIC. The regional map
  rendered in Firefox at 1280x800. Container egress was blocked. Essential
  service, inference, reference, and map checks passed after each of two
  reboots with changed boot IDs.
- Installed-image verification found seven image indexes, 1,174 candidate
  notice files, and three corresponding Ghostscript source files; source
  sizes and SHA-256 values matched the manifest. This is traceable source
  material, not a complete license clearance.
- The exact payload used by this run is
  `/mnt/shared/fieldos-payload-source-offer-69c48e7/offline-payload.tar.zst`,
  5.12 GiB, SHA-256
  `b42712b4544c583389e60eda5cb91d52f39c60a81516dc46ef994b5f31c18c67`.
  Payload archive validation confirmed 1,189 selected files, seven image
  indexes, and three exact source files.
- One preceding automated attempt reached the installer completion screen but
  did not hand off unattended; the harness interrupted it without manual
  intervention. It is explicitly not a PASS. The test-only autoinstall now
  schedules a system poweroff after installation, allowing the harness to
  detect shutdown and boot the installed target. Customer-facing installation
  configuration is unchanged.

### Earlier current-artifact snapshot — 2026-11-03 (superseded)

This snapshot predates the latest customer ISO, fresh-disk USB test, and clean
E2E rerun documented at the top of this file.

- Current unpublished test customer ISO (older payload; not cleared for
  distribution):
  `/mnt/shared/fieldos-releases/fieldos-test-customer-main-a4eebb8.iso`, SHA-256
  `47fdf3f07773bb61f2bca321513f875ade39f6a01bf51afba98fb282529c3b28`.
  The clean run above used an ephemeral test ISO that the harness removed; no
  new customer ISO was produced or published.
- Current payload and acceptance evidence are listed above. At the end of the
  run `/mnt/shared` had 42 GiB available (1.2 TiB total, 97% used). Check free
  space before creating large artifacts.
- Removed two superseded, unattached ISO binaries after checking that no VM
  referenced them: `fieldos-test-customer-r5.iso` and
  `fieldos-test-customer-offline-r1.iso`. Their checksum sidecars and release
  records were retained; the current ISO and all VM disks were preserved.
- Remaining physical-customer gates include third-party redistribution and
  attribution clearance, Ubuntu trademark/branding resolution, network-enabled
  LAN peer exposure review, physical hardware validation, and fuller content
  pack licensing/requirements. GPU acceleration is not physically validated;
  the acceptance guest passed with CPU inference. The content-pack architecture
  is present, while the catalog intentionally has no customer packs. The
  current miniature archive and zoom-5 world map remain fixtures.
- Do not recommend physical installation or publish release binaries until the
  documented customer-readiness gates are satisfied. The interactive installer
  has previously completed in QEMU; the latest acceptance run above validates
  the new payload through the unattended test-only path.

### Source-offer customer ISO candidate acceptance — 2026-11-03

- Built the customer-facing interactive test candidate from clean source commit
  `709c8932ba39184be9a24e40df5939b958d62e79` and the validated payload
  containing the image notices and corresponding-source offer. ISO:
  `/mnt/shared/fieldos-releases/fieldos-test-customer-sourceoffer-709c893.iso`,
  11,983,912,960 bytes, SHA-256
  `b3baf28dfb6be78f9f701fb53fd37e9cc083a205e05705da0bb2abfa123e7dc4`.
  `make verify`, ISO sidecar verification, and BIOS/UEFI boot-record checks
  passed. The embedded build manifest pins payload SHA-256
  `b42712b4544c583389e60eda5cb91d52f39c60a81516dc46ef994b5f31c18c67`.
- The interactive installer completed on a fresh 80 GiB disposable UEFI qcow2
  with no virtual NIC. The review screen showed only target `vda`. At the
  remove-media prompt, Enter powered off the guest; a host-side `virsh start`
  was required to boot the installed target. The customer account QMP sequence
  was accidentally run twice concurrently, producing unintended display-name
  and hostname values. A temporary password was reset in the isolated guest to
  reach the desktop and verify the browser. These actions make the interactive
  install/handoff test **PARTIAL**, not a clean PASS. No guest application data
  was manually repaired.
- After target boot, firstboot reached `status=complete` using local APT and
  container payloads. Seven services ran; N.O.M.A.D. returned `{"status":"ok"}`;
  Qwen generated `FIELDOS_CUSTOMER_INSTALL_OK`; embeddings returned 768 values;
  Kiwix search retrieved the New York article; installed image indexes and
  corresponding-source files matched all pinned hashes. The guest had no
  external NIC/default route. The regional map appeared in Firefox at
  1280x800 (3,993 sampled colors, 69,563 water pixels); screenshot SHA-256 is
  `0f860b1c952ee86573f1829f21c4ca253584589c9e445425dcfa47e9a9fbfb4e`.
- Two in-guest reboots changed boot IDs. After each, the complete service,
  inference, embedding, retrieval, and map API checks passed following an
  explicit readiness wait. The first immediate health probe after reboot one
  hit a transient connection reset while containers started; it recovered
  without data changes. The initial failed probe and successful retry are both
  preserved. This validates persistence after reboot, while the transient is
  retained as evidence rather than hidden.
- Full report, screenshots, logs, source-offer verification, listener and
  secret-file metadata, and the stopped guest disk remain under
  `/mnt/shared/fieldos-e2e/customer-sourceoffer-709c893/`. The local artifact
  manifest is
  `/mnt/shared/fieldos-releases/fieldos-test-customer-sourceoffer-709c893.manifest.json`.
  This candidate is unpublished and not redistribution-cleared.

### FieldOS test-disk cleanup — 2026-11-03

- Removed nine stopped, superseded disposable test qcow2 disks and their stale
  libvirt domain definitions after confirming each exact domain was shut off
  and referenced its matching disk. The removed guests were older customer
  installer attempts and superseded/aborted E2E runs. Their reports, logs, and
  screenshots were retained and each available report records that its disk
  was removed. No active VM, the current customer inspection VM, the latest
  clean E2E guest disk, physical drive, or unrelated host service was touched.
- `/mnt/shared` free space rose from 42 GiB to 254 GiB after cleanup. Building
  the new ISO and retaining its stopped test disk/screenshot evidence used
  some of that space; the later observed free space was 210 GiB. Recheck before
  starting another full-size guest. Build, payload, and evidence paths remain
  configurable through the `FIELDOS_*_ROOT` Make variables documented in
  `TESTING.md`.

### Acceptance and release continuation — 2026-11-03 (historical snapshot)

The status and storage figures in this snapshot predate the current acceptance
results at the top of this document and in the readiness table below.

- The clean unattended offline acceptance from source commit `0eb3d24`
  passed. Full evidence and the stopped disposable VM disk are at
  `/mnt/shared/fieldos-e2e/20261103T060129Z-2217020/`; the current payload is
  `/mnt/shared/fieldos-payload/offline-payload.tar.zst` (5.2 GiB,
  SHA-256 `1ff46b13ae6fb2beefa039f69ba6f7852d17bfcd7d87b1e83b650c891c76a8ce`).
- The previous clean automated attempt failed on a stale payload without the
  reference manifest. It remains recorded as FAIL at
  `/mnt/shared/fieldos-e2e/20261103T054638Z-2209484/`. The payload was rebuilt
  and the next fresh run passed; no manual guest repair occurred in the PASS
  run. The test ISO and temporary credentials were removed automatically.
- Customer-facing installer handoff remains PARTIAL: the latest interactive
  attempt powered off at the media-removal prompt and required a host-side
  start. The customer ISO has not yet been rebuilt with the current payload.
- Offline service, AI generation, embedding, Kiwix retrieval, regional PMTiles,
  and real Firefox map rendering passed in the clean acceptance guest. Two
  guest reboots preserved essential services and data. A no-NIC guest check
  passed. With networking enabled, QEMU user-mode testing confirmed guest
  internet access and blocked N.O.M.A.D. container egress; no FieldOS service
  bound to the guest NIC, but bridged guest-to-guest/LAN scanning remains
  unverified because isolated bridge creation was denied by host permissions.
- Hardware adaptation is CPU-validated; fixture profiles are simulated and
  no physical GPU backend has been validated. Docker socket access in the
  upstream N.O.M.A.D. architecture is privileged host access. LAN isolation,
  redistribution clearance, modified-Ubuntu trademark review, and physical
  hardware coverage remain release gates. Content-pack schema/validator is
  present; no customer packs have been approved or populated. Zoom-5 world
  maps and the miniature archive remain test fixtures.
- A refreshed, unpublished interactive customer test ISO was built from the
  repaired payload and verified. ISO:
  `/mnt/shared/fieldos-releases/fieldos-test-customer-280fda2.iso`, 11,983,912,960
  bytes, SHA-256
  `f3b8f5c2ff5cb9bf98e3e07c98b1fce219195d7bb4fe4490a38351cb145c751d`.
  Its test report and screenshots are at
  `/mnt/shared/fieldos-e2e/customer-280fda2-20261103/report.md`. Interactive
  installation reached completion, but media removal and Enter again shut
  down the VM; target boot required host recovery. Runtime and two reboots
  passed after that recovery, so installer handoff remains PARTIAL. This
  candidate has not been released.
- `/mnt/shared` has 64 GiB free (1.2 TiB total); the new customer test evidence
  directory occupies about 33 GiB, the prepared payload 5.2 GiB, and the
  releases directory 34 GiB. Preserve this headroom and use `/mnt/shared` for
  additional large artifacts.
- Gitleaks scanned the complete public Git history through commit `280fda2`
  (61 commits) with zero findings. This is a secret-pattern scan; the separate
  infrastructure-indicator review remains the evidence linked in the table.
- `make check`, all 33 unit tests, and `git diff --check` passed after the
  release documentation update. The latest source/docs commit and push status
  are recorded after that commit is created.
- Documentation now describes the configurable acceptance VM memory, payload
  staging free-space requirement, and the rule that manually recovered runs
  are not clean automated passes. After the documentation update, `make check`,
  `git diff --check`, and all 33 unit tests passed. The docs were committed and
  pushed as `37433d8` to public `main`.
