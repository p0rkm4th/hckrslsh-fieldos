# Hckrslsh FieldOS

FieldOS is an offline capable x86-64 field computer built on Ubuntu Desktop
and [Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad).
It bundles the container images, local AI models, a 100-article Wikipedia
fixture, low-zoom overview maps, and a zoom-13 statewide Tennessee map,
six searchable reference packs, and attributed FieldOS-edited NWS tornado,
flood, hurricane, and winter-storm summaries for offline use. The core packs
also include a narrow NIOSH heat-illness reference and a Southeastern vegetable
crop handbook. The owner uses
N.O.M.A.D. as the main interface.
This is still an engineering prototype, not a complete emergency or navigation
appliance.

This repository contains the installer source, service configuration, hardware
selection logic, payload manifests, tests, and release instructions. ISOs,
package archives, container images, model weights, maps, and VM disks are local
build outputs and are excluded from Git.

## Current status

The latest customer-mode engineering candidate is `/mnt/shared/fieldos-releases/fieldos-customer-offline-ac319b3.iso`, built from source commit `ac319b3aa1c458295bd2672f7608f146870a2df8`; SHA-256 `1d01fd5aedb7e408d856ab87c0e884202c5e78382ba75aab817ea9f84faa9432`. ISO structural verification passed, but a fresh interactive no-NIC UEFI install did not proceed: the installer detected the disposable 80 GiB disk and allowed guided installation in its storage backend, while the visible Next button remained disabled. No install began; this customer candidate is **FAIL / not accepted**. Logs and screenshots are retained at `/mnt/shared/fieldos-e2e/customer-ac319b3-20261105/`. The previous `9c59a5f` ISO has separate evidence of installation, desktop, services, and two reboots, but the media handoff required host intervention and remains **PARTIAL**. The clean unattended E2E on current application source `82c7786` still passed independently. See [`docs/RELEASE.md`](docs/RELEASE.md) for exact evidence and blockers.

The latest clean-source E2E passed on commit `82c7786c8086fe0f7d8aa3855cdd304de3be95c8`. Its no-NIC UEFI install provisioned seven services, generated CPU chat output, loaded embeddings, indexed the six bundled reference packs, rendered all eight statewide Tennessee locations in Firefox, and passed two reboots. The installed Source Library showed the new offline title/source/plain-text search interface; Node-backed tests exercise search matching and snippets. Report, screenshots, logs, and the stopped guest disk are retained at `/mnt/shared/fieldos-e2e/20261105T063912Z-2352718/`. The test ISO was removed after the run; SHA-256 `339989c4224b0bc9735e8eaf7349d9a7a4caba6e27d224bf894c462081b99aa7`. The verified payload used for this run is `/mnt/shared/fieldos-payload-29ff87b/offline-payload.tar.zst`, SHA-256 `41194c0e16015c10ed41d6b49cc9fb12684ebf39882a1878a188b3d7a33f18d9`; it passed validation against the current pack and map manifests. Optional transfer-pack import was skipped in this run; CDC and communications-pack transfers have separate no-NIC reports.

This E2E does not update or validate the customer ISO above. The latest customer candidate remains the older `9c59a5f` image and its interactive installer remains PARTIAL at the VM media-removal handoff; physical USB behavior is untested. See [`docs/RELEASE.md`](docs/RELEASE.md) for the full gate matrix and unresolved content, security, licensing, and hardware work.

These results establish engineering test acceptance in VMs, not physical hardware support or release readiness. Physical USB behavior, hardware/GPU variety, LAN exposure review, broader field reference coverage, and redistribution clearance remain open. This is not an emergency or medical appliance; do not rely on the local model for safety-critical decisions. Detailed source revisions, checksums, reports, and limitations are in [`docs/RELEASE.md`](docs/RELEASE.md); the interactive install report and screenshots are at `/mnt/shared/fieldos-e2e/customer-offline-9c59a5f-20261105/`.

## Build and test

Build dependencies include Python 3, Bash, Docker Engine with Compose v2,
xorriso, QEMU/KVM, libvirt, `virt-install`, `virsh`, `qemu-img`, and the
checksum verified Ubuntu 26.04.1 Desktop ISO. The ISO path can be supplied via
`UBUNTU_ISO`.

```sh
make check
make test
make test-e2e UBUNTU_ISO="/path/to/ubuntu-26.04.1-desktop-amd64.iso"
make iso-test UBUNTU_ISO="/path/to/ubuntu-26.04.1-desktop-amd64.iso"
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-offline-9c59a5f.iso
```

`make test-e2e` creates a unique test directory, temporary credentials, an
80 GiB virtual disk, and a headless test ISO. The VM has no virtual NIC. The
test command preserves the guest disk, report, and logs for review; it removes
the temporary ISO and user data file at the end. It never targets physical
disks. Detailed behavior and safe cleanup notes are in
[`docs/TESTING.md`](docs/TESTING.md).

`make iso-test` builds the customer facing ISO with interactive Ubuntu account
and disk selection. `make iso-full` is reserved for a later expanded payload
release; it must not be built until test edition acceptance passes.

## Project map

- [`installer/`](installer/) — interactive customer autoinstall and
  idempotent offline firstboot provisioning.
- [`services/compose.yaml`](services/compose.yaml) — pinned N.O.M.A.D. and
  supporting containers. Published local interfaces bind to loopback.
- [`hardware/`](hardware/) and [`models/manifest.json`](models/manifest.json)
  — hardware facts and configuration driven local model selection.
- [`build/`](build/) — offline payload preparation, ISO assembly, and ISO
  structure verification.
- [`tests/`](tests/) — unit tests and the disposable VM acceptance runner.
- [`docs/`](docs/) — architecture, installation, hardware, content, test, and
  release records.

Start with the [documentation guide](docs/README.md), then read
[installation](docs/INSTALLATION.md), [architecture](docs/ARCHITECTURE.md),
[operations and troubleshooting](docs/OPERATIONS.md), [hardware support](docs/HARDWARE.md),
and [offline content/licensing](docs/OFFLINE-CONTENT.md). The
[content-pack architecture](docs/CONTENT-PACKS.md) documents the six core
reference packs and planned categories. Review [security boundaries](docs/SECURITY.md)
before changing exposed ports or Docker access.

## Security and redistribution

Use disposable qcow2 disks for installation tests. Review the target device in
the interactive installer before confirming erase. Do not enable remote
service access without an explicit owner decision. Keep test credentials,
private runtime keys, model files, downloaded archives, and VM disks out of
Git and public release artifacts. Third party software and content retain
their own license terms; see `payload/licenses/`,
[`docs/OFFLINE-CONTENT.md`](docs/OFFLINE-CONTENT.md), and the artifact-level
[`docs/REDISTRIBUTION.md`](docs/REDISTRIBUTION.md). The current customer ISO is
an unpublished test candidate until those checks pass.

## License

FieldOS project source is Apache-2.0. Bundled software, models, maps, and
reference data remain under their respective upstream licenses.
