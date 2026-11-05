# Historical customer ISO validation: `cc4aa38`

This file records the historical `cc4aa38` run and is not the latest customer
candidate. Candidate `8c81d64` is newer, but its fresh no-NIC interactive
installation is blocked at Subiquity storage setup: `/dev/vda` is visible and
Next remains disabled. No installed OS, firstboot, service, or reboot result
exists for that candidate. Diagnostics are at
`/mnt/shared/fieldos-e2e/customer-8c81d64-20261105/diagnostics.md`. The last
completed install test, `8020fd3`, passed VM install and two reboots but its UI
selected Qwen3 0.6B while firstboot validated 1.7B. Current model handoff and
graphical-startup changes are not validated by either ISO.

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
