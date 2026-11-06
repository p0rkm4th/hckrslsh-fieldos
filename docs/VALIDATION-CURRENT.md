# Current validation status — 2026-11-06

## Latest customer-mode candidate — interactive installation PASS in VM

The current private engineering candidate is
`/mnt/shared/fieldos-releases/fieldos-customer-test-f250cc1.iso`, SHA-256
`26789db27ec52c683893d7cf1644782b83490e845339ada854538b7f1facebc2`. Its
embedded manifest records clean source revision
`f250cc175ccfac137bb6bf1236497e16b3f4cbd3`, Ubuntu source SHA-256
`601e30fbf5d97759367c632e2c33630665039b7e2158fd068403da3ccf1bda1f`, payload
SHA-256 `c1741d5ab506f47d307e6da57ae7b2ba16caaeefad41df874a0fb198d36f4724`,
and Project N.O.M.A.D. `v1.35.1`. `make verify ISO=...` passed structural,
BIOS/UEFI, customer setup, offline APT, and payload checks.

A fresh interactive installation of this exact ISO passed in a disposable
UEFI VM (4 vCPU, 8 GiB RAM, 80 GiB qcow2, no virtual NIC). The installer
allowed local identity and disk selection, confirmed erasure of `vda`,
installed Ubuntu, and completed the standard media handoff. The guest booted
from its installed disk after the ISO was ejected. Firstboot succeeded; all
seven services ran; the N.O.M.A.D. health API returned `{"status":"ok"}`;
CPU chat generation and 768-dimensional embeddings worked; Kiwix search and an
article opened; Source Library located and opened the CDC private-well source;
and Firefox rendered statewide map detail at Nashville, Memphis, and Johnson
City. The guest completed two reboots. After reboot 2, services, inference,
embeddings, Kiwix retrieval, the source document, a Nashville z13 map tile,
the no-NIC state, and the unchanged user-data marker hash all passed.

Evidence is preserved at
`/mnt/shared/fieldos-e2e/customer-f250cc1-interactive/`; the human-readable
run record is `report.md` in that directory. Screenshots include installer
disk/erase selection, handoff, desktop, Command Center, map views, Kiwix,
Start Here, Source Library, and a real AI response. Reboot evidence is in
`post-reboot-1.txt`, `post-reboot-2.txt`, and `reboot-acceptance.txt`.

This demonstrates offline operation and installation in this VM profile, not
physical hardware compatibility or a public release. The bundled Wikipedia
100 archive remains a test fixture. The CDC source is searchable/openable in
Source Library but is not indexed for AI retrieval. The desktop's “Index your
10 existing files” banner persists even though firstboot indexed the bundled
documents; investigate that confusing prompt. Physical USB installation,
GPU/GPS, connected-network exposure testing, broad content coverage, and full
redistribution clearance remain unverified.

The prior `5abae15` candidate record below is historical and is superseded by
this exact-source customer-mode acceptance.

## Historical customer-mode candidate

The current customer candidate is `/mnt/shared/fieldos-releases/fieldos-customer-5abae15.iso`, SHA-256 `8cd07f41cf34b0606553364b89acf5689ee531d150446a1d5551b41694550f67`. It was built cleanly from public source `5abae15ac13fe001178c01e8dd31b255d5714500` with the pinned Ubuntu source and payload checksums recorded in its embedded manifest. The ISO structure and payload verifier passed. This remains an engineering test image, not a redistribution-cleared release.

A fresh no-NIC interactive customer install from this exact ISO completed, booted from the installed disk, finished firstboot, and passed two reboot checks. Detailed steps, outcomes, and screenshots are at `/mnt/shared/fieldos-e2e/customer-5abae15-interactive/validation.md`.

## Latest clean-source unattended E2E

Source `d04f450b0d520a0e92a08c4862f7373406234a05` passed a fresh, clean-worktree
unattended installation with no virtual NIC. The test ISO SHA-256 is
`6a3fef4deba8b8ade1f1e04df15b2da97665a777fb19c120fc4bcea97e81a624`; its
prepared payload SHA-256 is
`ad0e28863afbddd94b65ecd9d0cc8101ee0119cdfe7a1a33b9054f895f63eae`. The run
report, firstboot logs, and screenshots are in
`/mnt/shared/fieldos-e2e/20261106T072733Z-566287/`. The Source Library browser
screenshot shows the private-well entry and CDC attribution. A direct guest-
loopback HTTP retrieval after reboot 2 matched the manifest SHA-256; details
are in `private-well-source-retrieval.txt`. The runner removed the test ISO
after completion; its guest disk is retained and shut off. This is unattended
test-ISO evidence and does not replace the separate customer-mode installation
result above.

| Area | Current result | Evidence and limits |
|---|---|---|
| Source checks | PASS | `make check test`: 126 tests passed; `payload/validate_content_packs.py` accepts 11 catalog packs on source `d04f450`. |
| Fresh unattended no-NIC E2E | PASS | Clean worktree, source `d04f450`, test ISO SHA-256 above. Offline install and provisioning, seven services, local chat and embeddings, references, Kiwix, all eight Tennessee Firefox map renders, and two reboots passed. The CDC private-well core pack is present in the Source Library. Optional transfer-media check was skipped because the pack was already bundled as core. |
| Clean-source customer ISO | PASS, structural | Full customer ISO built from clean source; BIOS/UEFI boot records, interactive customer setup, offline APT, and payload checks passed. ISO hash above. |
| Customer interactive install and disk boot | PASS in disposable UEFI VM | Identity and target `vda` were selected; erase confirmed; install completed. At the standard handoff prompt, the guest ejected the CD and shut down on Enter; an ordinary power-on booted the installed disk with the ISO detached. Physical USB handoff and automatic restart remain unverified. |
| Offline provisioning | PASS | Firstboot status `complete`, systemd result success / exit 0; seven service containers running; ten source documents indexed (690 chunks). |
| Offline operation | PASS for no-NIC guest | `virsh domiflist` empty, zero non-loopback guest adapters, zero default routes. This does not validate LAN-connected exposure. |
| Branded desktop and Command Center | PASS in VM | Fresh GNOME desktop, wallpaper, dark appearance, orange accent, dock, and Command Center rendered. |
| N.O.M.A.D. | PASS for tested local endpoints | `/api/health` returned `{"status":"ok"}` and seven containers ran after reboot 2. |
| Local inference | PASS, CPU | Bundled `qwen3:0.6b-q4_K_M` generated a real response after reboot 2. Physical GPU acceleration is unverified. |
| Embeddings | PASS | Bundled embedding model returned a 768-dimensional vector after reboot 2. |
| Tennessee maps | PASS, actual browser click/render | The Command Center Maps card opened a statewide Tennessee view with visible roads, towns, and waterways at zoom 7. The click and visible map rendering repeated after reboot 2. Zoom-13 detail and eight-location screenshots are verified in earlier same-payload browser runs; see the historical evidence below. The map is not routing or GPS navigation. |
| Kiwix | PASS, fixture limited | From the Kiwix catalog, Firefox opened the bundled `Wikipedia 100` ZIM, searched its contents for “United States” (59 results), and opened “List of states and territories of the United States” offline. Screenshot evidence: `/mnt/shared/fieldos-e2e/customer-5abae15-interactive/kiwix-search-united-states-article.png` and `kiwix-article-united-states.png`. This 100-article archive is only a test fixture, not a substantial encyclopedia. |
| Source Library | PASS, limited corpus | On customer ISO `5abae15`, Start Here’s link opened the local library; 19 entries appeared and “flood” returned three attributed matches. On E2E test ISO `d04f450`, the new private-well entry appeared with CDC attribution, and the offline document endpoint returned the manifest-matching SHA-256 after reboot 2. Screenshots and supplemental retrieval evidence are in the run folders above. |
| Persistence | PASS, two post-install reboot cycles | All seven containers, N.O.M.A.D. health, generation, embeddings, map, and local data were checked after the second reboot. The user-data marker SHA-256 remained identical across three boot IDs. See the exact IDs and hash in the run report. |
| Connected-network security | NOT TESTED | No NIC was attached during this run. LAN exposure and outbound egress with a NIC remain open. |
| Physical hardware / GPU / GPS | NOT TESTED | Disposable VM only. |
| Redistribution clearance | BLOCKED / INCOMPLETE | Ubuntu, software, model, map, and source-material review remains incomplete. Do not publish this ISO. |

**Assessment:** The exact current-source customer ISO passes the tested offline installation, local AI, embedding, default-map interaction, Source Library search, Kiwix in-book retrieval, and two-reboot VM gates. FieldOS is not release-ready: physical hardware, connected-network security, content breadth, and redistribution review remain open.

## Historical customer ISO validation: `cc4aa38`

This section preserves the historical `cc4aa38` report. Its following
paragraphs reflect what was known at the time and are superseded by the current
validation summary above. In particular, the initial concern about the later
`8c81d64` installer's disabled Next button was disproven: the customer-mode
installation completed, booted from its installed disk, and passed two reboot
cycles in the VM described above.

**Run date:** 2026-11-05  
**Source:** `cc4aa38f3debd078b877589355221e94821bd160` (`main`, clean at test start; same commit as `origin/main`)  
**Customer ISO:** `/mnt/shared/fieldos-releases/fieldos-customer-cc4aa38.iso`  
**ISO SHA-256:** `0319a069a4874d0522f660c6d69027e6ab9c4aaf86f2f8c995efb9d359a1e139`  
**Detailed evidence:** `/mnt/shared/fieldos-e2e/customer-cc4aa38-handoff-20261105/` (clean handoff retest) and `/mnt/shared/fieldos-e2e/customer-cc4aa38-20261105/` (eight-location statewide map run)

## Result

The current customer ISO installed successfully in a fresh, disposable UEFI VM
with no virtual NIC. The user selected the virtual target disk and confirmed
the destructive action. At the standard “Please remove the installation
medium, then press ENTER” prompt, the guest had already opened its virtual CD
tray. Pressing Enter caused a normal guest shutdown; a normal VM power-on then
booted the installed disk. No reset, repair, or ISO-present boot was used.
Firstboot and two subsequent guest reboots passed. This is a **PASS for
interactive installation and installed-disk boot in this UEFI VM**, including
the standard virtual-media handoff. A seamless automatic restart without the
ordinary power-on after the prompt was not demonstrated, and physical USB
behavior remains unverified.

## VM and offline state

- UEFI VM: 6 vCPU, 12 GiB RAM, 80 GiB disposable qcow2 disk; domain
  `fieldos-customer-cc4aa38-handoff2`.
- No virtual network adapter (`virsh domiflist` empty); guest had no physical
  network interface and no default route. Docker bridges remained available
  for local services.
- Target disk selection (`vda`), destructive-action confirmation, identity
  setup, installation completion, the installer media-removal prompt, clean
  guest shutdown, and subsequent installed-disk boot were observed. After the
  prompt the guest tray was open; `vda` was the only boot device on power-on.
- Firstboot status: complete at `2026-11-05T18:51:16Z`.
- All seven containers were running: `nomad_admin`, `nomad_redis`,
  `nomad_qdrant`, `nomad_kiwix_server`, `nomad_mysql`, `nomad_dozzle`, and
  `nomad_ollama`.

## Functional results

| Area | Result | Evidence |
|---|---|---|
| Build validation | PASS | `make check test`: 87 unit tests passed; 10 content-pack manifests validated. `make verify ISO=...`: BIOS/UEFI boot records, customer setup, offline APT, and payload passed. |
| Interactive install and disk boot | PASS in disposable UEFI VM | Fresh customer installation reached the standard media-removal prompt, cleanly shut down after Enter, then booted from `vda` on ordinary `virsh start`; no reset or repair. See `reboot-stage-1.png`, `disk-boot.png`, and this report's run directory. Seamless automatic restart was not demonstrated. |
| Provisioning | PASS | Firstboot status complete at `2026-11-05T18:51:16Z`; all seven containers running. Reboot evidence is in `persistence-baseline-second-install.txt`, `reboot-1-second-install.txt`, and `reboot-2-second-install.txt`. |
| Local AI inference | PASS, CPU | Bundled Qwen3 1.7B Q4_K_M returned `FIELDOS_AFTER_REBOOT2_OK` after reboot 2; evidence `inference-after-reboot2.txt`. Hardware selector chose CPU; no GPU validation. |
| Embeddings | PASS | Bundled `nomic-embed-text:v1.5` returned a 768-dimensional vector after reboot 2; same evidence file. |
| N.O.M.A.D. retrieval | PARTIAL | API health and browser UI work. Firefox Source Library search for “flood” returned three local document matches (`source-search-current-install.png`); indexing reported 9 files/689 chunks. A safety-sensitive chat query produced the configured refusal and directed the user to original sources. Semantic answer quality and citations remain unreliable. |
| Kiwix | PASS, fixture limited | Firefox opened the bundled 100-article Wikipedia ZIM and in-book search returned “The New York Times” (`kiwix-current-install.png`, `kiwix-search-current-install.png`). This is not a broad encyclopedia. |
| Tennessee maps | PASS in browser, same ISO checksum | Current clean-install Firefox showed readable zoom-13 Nashville streets (`map-current-install.png`). The separate installation of this exact ISO SHA visually rendered all eight required points; see the eight `map-*.png` screenshots in `/mnt/shared/fieldos-e2e/customer-cc4aa38-20261105/`. The map is a geographic reference, not routing or GPS. |
| Branding and desktop | PASS in VM | Fresh installed GNOME desktop and N.O.M.A.D. Command Center, AI Assistant, and Source Library opened; screenshots `desktop-ready.png`, `nomad-current-install.png`, `nomad-ai-current-install.png`, and `source-library-current-install.png`. |
| Persistence | PASS, two post-install reboots | Boot IDs changed from `517fa702-62cf-44e2-9641-c181886c0add` to `6a855656-f217-4bd4-bf37-090785b44fef` to `0a2ca040-42ff-4e99-acd3-da6ddcf32a7a`. User marker SHA-256 remained `9bf000f4d7b03b01e24f81a836257cf973898c90eb5ba0265b66ce22892329b6`; PMTiles SHA-256 remained `0d123132839b77e627c4f4f103bf7a78925099c57319e759757be3207cb89525`. All seven containers, N.O.M.A.D. health, Kiwix search, reference index, inference, and embeddings worked after reboot 2. |

## Limits and release blockers

- Installer's normal virtual-media removal prompt and subsequent installed-disk
  boot passed in a VM. The guest shut down at the prompt and required an ordinary
  power-on; fully automatic restart and physical USB handoff remain unverified.
- VM validation is not physical USB/firmware or broad hardware validation.
  Physical GPU acceleration, GPS, and connected-LAN exposure have not been
  validated by this run.
- The Kiwix archive is only 100 articles. The nine indexed source files (689
  chunks) do not amount to a comprehensive field, medical, emergency, or
  agricultural library. Retrieval quality is limited.
- Map rendering and offline availability are verified; routing and GPS
  positioning are not.
- Redistribution clearance for the exact Ubuntu image, third-party software,
  models, map data, and source documents remains open. Do not publish this ISO.
- This run proves operation with no network adapter; it does not prove safety
  when a network adapter is enabled.

## Storage retained for this run

- ISO: 13,523,091,456 bytes; SHA-256 above.
- Retained test disks: the original accepted-services run at
  `/mnt/shared/fieldos-e2e/customer-cc4aa38-20261105/guest.qcow2` and the clean
  handoff retest at
  `/mnt/shared/fieldos-e2e/customer-cc4aa38-handoff-20261105/guest.qcow2`.
  Both VMs remain available and are intentionally retained as test evidence.
- At report time `/mnt/shared` had 399 GiB free (745 GiB used of 1.2 TiB).
