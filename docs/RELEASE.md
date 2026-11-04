# Release readiness and evidence

**Status: engineering test candidate; not approved for customer or emergency use.**

## Current source and artifacts

The latest fully tested application/payload source is
`b5d6f748c9efdb0f4345c5fe92533b882c7e2856`. The statewide customer ISO below
was built from documentation-only commit `bc7e4c1c3d0ec79519cc41b7c6ce1cd3a702b10c`
and separately installed in customer mode. The current source adds an
optional NIOSH text pack and its activation evidence; that pack is not in the
ISO, and the change did not require rebuilding it.

### Current customer-mode test candidate

- ISO: `/mnt/shared/fieldos-releases/fieldos-customer-statewide-bc7e4c1.iso`
- SHA-256: `bdfbe5c01f9960634f275e230c3a3957623f778c511c36a73ddf992a2f4e85bd`
- Customer install evidence: `/mnt/shared/fieldos-e2e/customer-statewide-bc7e4c1/report.md`
- VM: disposable UEFI guest, 6 vCPU, 12 GiB RAM, 80 GiB disk, no virtual NIC.
- Interactive disk and account selection completed; Ubuntu installed to the
  disposable `vda` disk and booted from `/dev/vda2` after the ISO was ejected.
  Firstboot completed with status `complete`; all seven N.O.M.A.D. containers
  ran. Local chat returned `FIELDOS_CUSTOMER_OK`, embeddings returned a
  768-dimensional vector, and Kiwix retrieved a bundled article. Firefox
  visibly rendered zoom-13 Tennessee maps at Memphis, Nashville, Knoxville,
  Chattanooga, Clarksville, Jackson, Johnson City, and a rural Big South Fork
  location. Screenshots, VM XML, firstboot logs, and two reboot checks are
  retained with the report.
- On the first post-install restart the virtual installation media remained
  in the VM's boot path. The ISO was ejected and the guest was powered on again;
  the installed OS then booted normally. This verifies disk boot after media
  removal, but not physical USB behavior. The customer install used interactive
  choices; it is distinct from the unattended E2E acceptance image.

The previous customer-mode candidate remains preserved at
`/mnt/shared/fieldos-releases/fieldos-customer-core4-21ad4fc.iso`, SHA-256
`38acf9bda9d62b328e5baf117895d25affa78688730cf9da1be7b4769791f9bd`. It is
retained as a rollback/reference image and is not the current statewide build.

### Latest full offline E2E run

- Report: `/mnt/shared/fieldos-e2e/20261104T215624Z-1056575/report.md`
- Test ISO SHA-256: `71821434553d6b0b26b0f87cfa6f857ed6a38b97e80e8b357d69f966e4e4217a`
- A clean no-NIC UEFI install completed firstboot, ran seven services, generated
  `FIELDOS_ACCEPTANCE_OK` with CPU Ollama, returned an embedding vector, served
  Kiwix, visibly rendered the eight Tennessee map locations, and passed two
  reboot/persistence cycles. Container egress checks passed.
- `make check && make test` passed all 74 tests on the current worktree after
  adding the optional pack to the catalog and its catalog expectation.

### Offline content artifacts

- Statewide map:
  `/mnt/shared/fieldos-map-review-20261104/tennessee-20261102-z13.pmtiles`;
  145,267,908 bytes, SHA-256
  `0d123132839b77e627c4f4f103bf7a78925099c57319e759757be3207cb89525`;
  zoom 0–13, bounds `-90.9,34.5,-81.0,37.25`. The current customer ISO
  rendered the map at all eight locations above. Map attribution is included;
  full redistribution review remains open.
- Optional Southeastern vegetable growers archive tested separately:
  `us-southeastern-vegetable-growers-2026.1.tar.zst`, SHA-256
  `e7dd06a657973a15bd75a1d9986ec774aef7f0b86c1f88ce4e4b25416cac7e30`.
  N.O.M.A.D. indexed it as 678 chunks after offline transfer; it is not in the
  customer ISO.
- Optional NIOSH heat-illness pack `us-niosh-heat-first-aid` version `2024.1`
  was transferred from read-only optical media to the no-NIC interactive
  customer test guest. N.O.M.A.D. indexed its 6,593-byte text transcription as
  3 chunks; the Source Library returned the document over local HTTP (200),
  and both activation and indexing persisted across a reboot. The graphical
  display was inactive during the separate visual check, so this pack's
  browser presentation is not verified. It remains optional and is not in the
  customer ISO. Full evidence:
  `/mnt/shared/fieldos-e2e/customer-statewide-bc7e4c1/niosh-pack-activation.md`.
- The core reference library currently contains a small set of emergency,
  weather, water, and food sources plus a 100-article Wikipedia fixture. This
  is not a comprehensive first-aid, medical, agricultural, wildlife, or
  technical field library.

## Acceptance matrix

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Fresh unattended offline install | PASS, test-only image | Exact source, ISO hash, and no-NIC report above. |
| Interactive customer install | PASS in disposable UEFI VM | Current statewide candidate installed with interactive identity and disk selection; booted from installed disk after media ejection. Physical USB behavior remains untested. |
| Offline firstboot and services | PASS | Customer VM provisioning status complete; seven N.O.M.A.D. containers running. |
| Local chat and embeddings | PASS | Actual local response `FIELDOS_CUSTOMER_OK`; embedding vector length 768. Physical GPU acceleration remains unverified. |
| Kiwix and source retrieval | PASS, narrow collection | Kiwix search returned a bundled article; seven core source documents indexed. Library breadth remains limited. |
| Optional NIOSH heat first-aid pack | PASS, local activation; visual view PARTIAL | No-NIC import, checksum validation, 3 indexed chunks, local source document HTTP 200, and post-reboot persistence. Browser view of this new pack was not confirmed. |
| Tennessee maps | PASS in customer VM | Firefox visibly rendered eight zoom-13 locations; map is not routing or navigation. GPS is unverified. |
| Reboot persistence | PASS | Two customer-VM reboots preserved provisioning state, a user-data sentinel, map availability, Kiwix retrieval, and service availability. |
| Hardware adaptation | PARTIAL | CPU model selection exercised; simulated profiles pass. No physical CPU/GPU validation. |
| Network/security boundary | PARTIAL | Customer and E2E VMs had no NIC; container egress checks passed in E2E. LAN-connected peer test remains open; Docker-socket consumers retain privileged host access. |
| Field reference breadth | FAIL for field readiness | Current core is small; optional vegetable handbook is separate. First-aid procedures, wildlife, broader agriculture, and practical technical references remain incomplete. |
| Redistribution review | BLOCKED | Exact Ubuntu image, software, model, map, and document license/attribution review is incomplete. |
| Physical customer readiness | BLOCKED | Physical installation and hardware, LAN exposure, content breadth, and rights review remain. |

## Customer-facing limits

FieldOS provides a local assistant and embeddings, a statewide Tennessee map
viewer, Kiwix, and a small source library. It does not provide routing, GPS
positioning, navigation-grade maps, or a comprehensive emergency/medical
reference. The local model is not an authority for emergency or medical
decisions. Users should open and follow cited source material; unsupported
answers must not be treated as instructions. See
[`FIELD-USE-ASSESSMENT.md`](FIELD-USE-ASSESSMENT.md) and
[`CONTENT-PACKS.md`](CONTENT-PACKS.md).

## Security, licensing, and release hygiene

The tested guests had no network adapter; this demonstrates offline operation,
not safe behavior on a LAN. Complete a connected-peer exposure and egress review
before recommending installation on a networked system. Upstream N.O.M.A.D.
components that use `/var/run/docker.sock` have powerful host administration
access.

The ISO remains unpublished engineering test material. Complete redistribution
and attribution review, including Ubuntu trademark and branding requirements,
before publishing binaries. Do not put ISO files, model weights, container
archives, VM disks, credentials, or generated private keys in public Git.
