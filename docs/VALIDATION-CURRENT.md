# Current customer ISO validation

**Run date:** 2026-11-05  
**Source:** `cc4aa38f3debd078b877589355221e94821bd160` (`main`, clean at test start; same commit as `origin/main`)  
**Customer ISO:** `/mnt/shared/fieldos-releases/fieldos-customer-cc4aa38.iso`  
**ISO SHA-256:** `0319a069a4874d0522f660c6d69027e6ab9c4aaf86f2f8c995efb9d359a1e139`  
**Detailed evidence:** `/mnt/shared/fieldos-e2e/customer-cc4aa38-20261105/`

## Result

The current customer ISO is structurally valid and its installed system works
offline in a disposable UEFI VM. The interactive installation completed after
selecting the disposable virtual disk and confirming the erase. However, the
installer's **Restart Now** did not hand off automatically: the VM remained
black/idle until a diagnostic `virsh reset`. The installed OS then booted from
the virtual disk, with the ISO detached, and completed provisioning. Because
of this intervention, this run is **not a clean customer-installer PASS**.
Resolve or reproduce the handoff behavior before making a customer-readiness
claim.

## VM and offline state

- UEFI VM: 6 vCPU, 12 GiB RAM, 80 GiB disposable qcow2 disk.
- No virtual network adapter (`virsh domiflist` empty); guest had no physical
  network interface and no default route. Docker bridges remained available
  for local services.
- Target disk selection, destructive-action confirmation, identity setup,
  installation completion, media ejection, and subsequent installed-disk boot
  were observed. The media was absent from the boot device list after install.
- Firstboot status: `complete` at `2026-11-05T17:31:22Z`.
- All seven containers were running: `nomad_admin`, `nomad_redis`,
  `nomad_qdrant`, `nomad_kiwix_server`, `nomad_mysql`, `nomad_dozzle`, and
  `nomad_ollama`.

## Functional results

| Area | Result | Evidence |
|---|---|---|
| Build validation | PASS | `make check test`: 87 unit tests passed; 10 content pack manifests validated. `make verify ISO=...`: BIOS/UEFI boot records, customer setup, offline APT, and payload passed. |
| Provisioning | PASS after diagnostic reset | `firstboot-status.json`, `firstboot.log`, `guest-services.txt`; installed OS reports firstboot complete. |
| Local AI inference | PASS | Selected Qwen3 1.7B Q4_K_M CPU model returned `FIELDOS_OFFLINE_CHAT_OK`; after reboot 2 it returned `FIELDOS_REBOOT2_OK`. See `functional-checks-pre-reboot.json` and `reboot-2.json`. |
| Embeddings | PASS | `nomic-embed-text:v1.5` returned a 768-dimensional vector before and after reboots. |
| N.O.M.A.D. retrieval | PARTIAL | API and Firefox chat returned a local Southeastern Vegetable Crop Handbook source. A soil-pH query did not recover the requested detail; another harmless UI prompt received an overbroad status refusal with irrelevant weather references. Do not treat generated answers or citations as authoritative. |
| Kiwix | PASS, fixture limited | Firefox opened the bundled Wikipedia 100 ZIM and its in-book search returned 19 results for “new york,” including “The New York Times.” See `kiwix-wikipedia-book.png` and `kiwix-article-search-ui.png`. This is a test fixture, not a useful broad encyclopedia. |
| Tennessee maps | PASS in browser | Firefox visibly rendered zoom-13 detail at Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Jackson, Johnson City, and Big South Fork. Screenshots: `map-memphis.png`, `map-nashville.png`, `map-knoxville.png`, `map-chattanooga.png`, `map-clarksville.png`, `map-jackson-clean.png`, `map-johnson-city-clean.png`, and `map-rural-clean.png`. `map-memphis-after-reboot.png` also confirms rendering after reboot. |
| Branding and desktop | PASS in VM | FieldOS wallpaper remained visible after reboot; Project N.O.M.A.D. Command Center and AI Assistant opened in Firefox. See `desktop-after-two-reboots-unlocked.png`, `nomad-home-after-reboot.png`, and `nomad-chat-generated.png`. |
| Persistence | PASS, two post-install reboots | Boot IDs changed twice. A user-created test marker SHA-256 stayed `0a133e633924da56e5abfc415afecb19e34d87744a081975daac0e4f021d42e6`; the 145,267,908-byte Tennessee PMTiles SHA-256 stayed `0d123132839b77e627c4f4f103bf7a78925099c57319e759757be3207cb89525`; firstboot, all seven services, health, model generation, embeddings, and Kiwix search persisted. See `persistence-baseline.json`, `reboot-1.json`, and `reboot-2.json`. |

## Limits and release blockers

- Installer restart/handoff was manually recovered. The current customer-mode
  install gate remains **PARTIAL** pending a clean run.
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

- ISO: 13,523,091,456 bytes.
- Active test disk: `/mnt/shared/fieldos-e2e/customer-cc4aa38-20261105/guest.qcow2`,
  39,412,826,112 allocated bytes (80 GiB virtual capacity). The VM remains
  available for handoff diagnosis and is intentionally retained.
- Run directory: about 37 GiB including the disk and evidence. `/mnt/shared`
  had about 435 GiB free when this report was written.

