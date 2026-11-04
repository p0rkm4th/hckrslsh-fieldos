# Release readiness and evidence

**Status: engineering test candidate; not approved for customer or emergency use.**

The current source revision passed the fresh unattended offline E2E test and a
separate interactive customer-mode installation to a disposable UEFI VM disk.
The installed system booted, firstboot completed, local services worked without
a virtual NIC, and key data and services survived two guest reboots. The fresh
customer-mode handoff did not complete unattended: after the media-removal
prompt and Enter, the VM powered off and needed a host-side `virsh start` to
boot the installed disk. The candidate therefore does not yet pass the
seamless installer handoff gate.

The installed desktop is useful for offline prototyping. Its local AI gave a
generic, misleading response to a food-safety question and did not cite the
CDC source pack. The Kiwix archive has only 100 articles; the maps stop at zoom
level 5. Field readiness remains **FAIL**.

## Current source and artifacts

The last validated build remains `f9c10ec170c2b33000a287a0ee8ef38d6e2b0f50`.
The working source now adds a small adapter that uploads checksum-verified
FieldOS reference-pack PDFs and text files into N.O.M.A.D.'s existing RAG
Knowledge Base and waits for indexed chunks. Unit tests pass, but this change
has not yet been built into an ISO or verified in a fresh guest. The existing
candidate and reports below still describe the previously tested source.

- Last validated source: `f9c10ec170c2b33000a287a0ee8ef38d6e2b0f50`.
- Latest unattended E2E report:
  `/mnt/shared/fieldos-e2e/corepack-f9c10ec/20261104T034230Z-3056023/report.md`
  (PASS). The test ISO SHA-256 is
  `2d7ab741cdad4ab654400a1b657c8eb9f14a311aad8e9535ca5340c365163255`.
  It verified no-NIC Ubuntu install, offline firstboot, seven services, chat,
  embeddings, Kiwix retrieval, Firefox map and reference-library rendering,
  the bundled CDC pack, and two reboots. A separate removable-media content
  pack import was skipped; the core CDC pack was already bundled and activated.
- Customer-mode engineering candidate:
  `/mnt/shared/fieldos-releases/fieldos-customer-test-corepack-f9c10ec.iso`
  (11,987,386,368 bytes), SHA-256
  `95503d257465087b723ba1eb0725dbf63ac6cf2ac83383f4e35cd63af7738c8d`.
  `make verify` passed BIOS/UEFI structure, interactive customer setup, offline
  APT, and payload checks.
- Fresh customer-mode test report and evidence:
  `/mnt/shared/fieldos-e2e/customer-interactive-corepack-f9c10ec/20261104T040000Z/report.md`.
  The guest used a blank 80 GiB virtual disk, 4 vCPU, 8 GiB RAM, UEFI, and no
  virtual NIC. It completed interactive account and disk configuration,
  booted the installed EFI disk, completed firstboot, rendered the branded
  desktop, and passed two reboots. The report records the installer handoff
  caveat and the observed field-use limitations. After report review the VM was
  shut down and undefined; the unattached 33 GiB qcow2 was retired with the
  cleanup helper. `disk-retirement.txt`, logs, and selected screenshots remain.
- Offline payload:
  `/mnt/shared/fieldos-payload-core-f9c10ec/offline-payload.tar.zst` (5.2 GiB),
  SHA-256
  `75fe6c6961ee906995866e93814717b03cc3974913b8a8b79c3b9d33a1821998`.
- Unit tests: 57 passed on this source revision. The current E2E and customer
  report logs are preserved under `/mnt/shared/fieldos-e2e/`.

These are local engineering artifacts, not published release binaries. No
physical USB installation, physical GPU, or customer laptop has been validated.
After retiring the customer test disk and duplicate installer screenshots,
`/mnt/shared` has 625 GiB free (46% used). The 12 GiB candidate ISO, 5.2 GiB
payload, current E2E evidence, and interactive-install logs/screenshots remain.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh offline Ubuntu installation | PASS in unattended and interactive QEMU | E2E and customer report; no virtual NIC; local APT and container images. |
| Offline provisioning | PASS | Firstboot status is `complete`; firstboot log and seven-container inventory are retained. |
| N.O.M.A.D. local UI | PASS | FieldOS desktop launcher opened Command Center and chat in Firefox. |
| Local chat inference | PASS, function only | Bundled Qwen model generated real text; its practical food-safety answer was misleading and uncited. Not safe as emergency guidance. |
| Embeddings | PASS | Bundled embedding endpoint returned a 768-element vector, including after reboot two. |
| Kiwix | PASS, limited | Browser loaded one bundled “Wikipedia 100” archive and retrieved a matching article. |
| Core source references | PASS, limited | Two CDC PDFs (water treatment and food safety after power outage) are bundled, attributed, served locally, and persist after reboot. They are not indexed in N.O.M.A.D.'s semantic retrieval. |
| Offline map rendering | PASS at overview only | Firefox visibly rendered the U.S. basemap. Bundled data stops at zoom 5; no street/trail navigation detail. |
| Two-reboot persistence | PASS in disposable QEMU | Both boot IDs changed; containers, models, CDC references, Kiwix, and map endpoint were checked after reboot two. |
| Installer Restart/media handoff | PARTIAL | Customer installer reached its media-removal prompt, but after ejection and Enter the VM powered off; host `virsh start` was needed to boot the installed disk. Retest and fix this transition. |
| Hardware selection | PARTIAL | 8 GiB/4-vCPU virtual profile selected the smallest bundled CPU model. Physical device and GPU acceleration remain untested. |
| Field-use safety and content breadth | FAIL | Only two CDC source documents, a 100-article ZIM, and zoom-5 maps; tested chat response was poor and uncited. |
| Security and LAN exposure | PARTIAL | This guest had no NIC. LAN peer isolation and exposed-port behavior on a connected system still need review. N.O.M.A.D. admin/Dozzle retain Docker-socket access. |
| Redistribution review | BLOCKED | Final license and attribution review is still required for all software, container images, models, maps, and content. |
| Physical/customer release | BLOCKED | Handoff, content adequacy, physical hardware, security, redistribution, and user recovery gates remain. |

## Field-use limitations

The built-in Source Library identifies its contents as original source
documents and warns that the set is not comprehensive. The core set covers
emergency drinking-water treatment and food safety after power loss. It does
not provide substantive first-aid, wildfire, severe-weather, agriculture,
mechanical, or navigation references. The two PDFs are available to read
locally but are not added to N.O.M.A.D.'s semantic search.

Kiwix serves a single 100-article test ZIM. The bundled world and sample U.S.
PMTiles archives top out at zoom 5. A Middle Tennessee zoom-13 candidate was
validated separately but is not in the ISO and is not approved for public
redistribution. GPS/GIS integration and physical hardware adaptation remain
unverified. Treat untested devices as unsupported.

The small local model can produce plausible but irrelevant or unsafe text. It
does not reliably follow prompts or identify its sources. Consult the original
documents and current local authority guidance. Do not use AI output as medical,
emergency, navigation, or technical authority.

## Customer installation gate

The customer ISO keeps disk choice, identity, and credentials interactive; the
unattended `make test-e2e` installer is a separate test image. The current ISO
completed interactive setup and booted from its installed EFI disk in a blank,
disposable UEFI VM with no NIC. However, the current candidate's Restart flow
required an extra host-side start after the media-removal prompt. Repeat the
handoff test after resolving that behavior. Physical USB installation and
supported hardware testing remain outstanding. Never point automated tests at
physical or production disks.

## Security, content, and artifact handling

The disconnected test confirms the software works without an external network
adapter; it does not prove LAN isolation when a NIC is enabled. Recheck Compose
published ports and management access before connected-lab use. `nomad_admin`
and `nomad_dozzle` use the Docker socket, which grants powerful host control.

Review `REDISTRIBUTION.md`, `OFFLINE-CONTENT.md`, and `CONTAINER-IMAGES.md`
before any public release. The current candidate is not approved for customer
distribution. Keep the ISO, payload inputs, reports, and useful screenshots on
the configured artifact volume. Delete a disposable guest disk only after the
VM is shut down, the report is saved, and the retirement helper confirms no
process is using it.
