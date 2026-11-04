# Release readiness and evidence

**Status: engineering test candidate; not approved for customer or emergency use.**

## Current source and test artifacts

- Source revision: da61a843313c443c0e349a75b6395e48c0f73c20, pushed to origin/main.
- Source worktree was clean for the current acceptance build.
- make check and 61 unit tests passed.
- Fresh unattended no-NIC E2E report:
  /mnt/shared/fieldos-e2e/20261104T060325Z-3127648/report.md.
  It records test ISO SHA-256
  339970d3b5ca2a7440300647b7c460fc03b4d9b480447676169de30d3c938d3c.
  The temporary test ISO and guest disk were retired after review; report,
  logs, and screenshots remain.
- Current customer-mode candidate:
  /mnt/shared/fieldos-releases/fieldos-customer-da61a84.iso
  (11,987,386,368 bytes), SHA-256
  0325b6b244cbf3042a1787c85715e052f806bc432d455e512cc4dcb5e70b6931.
  It is a local engineering artifact, not a published release binary.
- Interactive customer installation report and selected evidence:
  /mnt/shared/fieldos-e2e/customer-da61a84/report.md.
- Current reusable offline payload:
  /mnt/shared/fieldos-payload (about 5.2 GiB). Do not remove while it is the
  input for the candidate rebuild.

## Verified behavior

The unattended E2E test installed Ubuntu into a disposable UEFI disk with no
virtual NIC. Offline firstboot completed; all seven containers started. Ollama
generated the acceptance marker, the embedding endpoint returned a 768-element
vector, and N.O.M.A.D. indexed both CDC reference PDFs. A real food-safety RAG
query returned the four-hour guidance with a CDC source. Kiwix served its
100-article archive and found a test article. Firefox visibly rendered the
bundled U.S. overview map. Essential service and content checks passed after
two consecutive reboots. The report records container egress blocking and the
absence of a guest uplink adapter.

The separate customer ISO was installed interactively to a blank 80 GiB UEFI
qcow2 disk with 4 vCPU, 8 GiB RAM, and no NIC. The installer displayed the
interactive disk and account steps, confirmed the selected vda disk, and
completed installation. At the final prompt, Ubuntu requested removal of the
installation medium and Enter. Ejecting the ISO and pressing Enter powered the
VM off; a subsequent power-on booted the installed EFI disk without repair or
changing guest state. This models a user removing USB and powering the computer
on again after the installer shuts it down; physical USB behavior is untested.

Customer firstboot completed with status complete. N.O.M.A.D. health returned
{"status":"ok"}; seven containers were running. Ollama generated
FIELDOS_CUSTOMER_INSTALL_OK; the embedding API returned 768 dimensions. The
knowledge interface retrieved two indexed CDC documents: a food-outage query
returned four-hour guidance, and a water-treatment query returned the one-minute
boil guidance plus the document's 6,500-foot/three-minute qualification, with
CDC citations. Kiwix returned its Wikipedia catalog and a search result. Firefox
visibly rendered the bundled U.S. map in
/mnt/shared/fieldos-e2e/customer-da61a84/customer-map.png. The guest had no
physical or virtual uplink NIC. After one OS reboot, the boot ID changed and
N.O.M.A.D., all seven containers, the two indexed documents, Kiwix, and model
inventory were present again. Runtime records and logs are retained beside the
report. E2E evidence covers two reboots on the same source revision.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh unattended offline installation | PASS | Exact source and test ISO hash above; no NIC; local APT and image loading. |
| Interactive customer installation | PASS in disposable QEMU | Interactive vda and user setup; installed EFI disk booted and services passed. |
| Installer media handoff | PASS with user power cycle | Remove medium, press Enter, then power on after Ubuntu shutdown. No guest repair; physical USB behavior not yet tested. |
| Offline provisioning | PASS | Firstboot status complete; runtime log and seven-container inventory retained. |
| N.O.M.A.D. and knowledge retrieval | PASS for bundled sources | API healthy; both included CDC PDFs indexed and retrieved with source titles. Scope is only these two PDFs. |
| Local chat and embeddings | PASS, functional check only | Chat generated exact test tokens; embedding returned 768 dimensions. Not a safety certification. |
| Kiwix | PASS, limited | Bundled Wikipedia 100 archive served and a search result opened. |
| Offline maps | PASS at overview level | Firefox screenshot visibly renders U.S. labels, roads, water, and attribution. Bundled maps top out at zoom 5. |
| Reboot persistence | PASS | Two reboots on unattended E2E; one reboot on interactive customer install; service and indexed content checks repeated. |
| No-network operation | PASS in QEMU | No guest NIC and no container egress in E2E. LAN behavior with a NIC is a separate open review. |
| Hardware selection | PARTIAL | The 8 GiB virtual guest selected the minimal CPU model and passed local generation. No physical GPU validation. |
| Content breadth and field readiness | FAIL | Two CDC PDFs, a 100-article ZIM, and zoom-5 maps are fixtures/starter content, not a complete preparedness library or navigation map. |
| Security and LAN exposure | PARTIAL | Disconnected guest validated. LAN exposure still needs testing. N.O.M.A.D. admin and Dozzle have Docker socket access. |
| Redistribution review | BLOCKED | Complete component/model/map/document licensing and attribution review before distribution. |
| Physical/customer release | BLOCKED | Physical USB, supported hardware, content breadth, LAN security, redistribution, and recovery validation remain. |

## Field-use limits

The bundled source pack covers emergency drinking-water treatment and food
safety after power loss. It does not provide substantive first aid, severe
weather, wildfire, agriculture, mechanical repair, or navigation guidance. The
Kiwix archive contains 100 articles. World and sample U.S. PMTiles top out at
zoom 5 and do not provide street/trail navigation detail. A Middle Tennessee
zoom-13 candidate was validated separately but is not included in this ISO and
is not approved for public redistribution. GPS/GIS integration is unverified.

The small local model can produce irrelevant or unsafe text. Even when a tested
retrieval answer cites a document, consult the original source before acting.
Do not use AI output as medical, emergency, navigation, or technical authority.

## Security, licensing, and release handling

The no-NIC test confirms disconnected operation, not isolation after enabling a
LAN adapter. Review published ports before connected use. nomad_admin and
nomad_dozzle mount the Docker socket, which grants powerful host control.
Review docs/REDISTRIBUTION.md, docs/OFFLINE-CONTENT.md, and
docs/CONTAINER-IMAGES.md before public release. Keep ISO and payload inputs,
VM disks, credentials, and evidence out of public Git. Retain the current ISO,
core payload, meaningful test reports/logs, and one recovery point during lab
replacement. Remove only exact superseded artifacts after verifying no active
process uses them.
