# Hckrslsh FieldOS

FieldOS is an offline capable x86-64 field computer built on Ubuntu Desktop
and [Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad).
It bundles the container images, local AI models, a 100-article Wikipedia
fixture, low-zoom overview maps, a zoom-13 statewide Tennessee map, and a
starter set of source packs. These include CDC water and food references,
NWS-derived tornado, flood, hurricane, and winter-storm summaries, a narrow NIOSH
heat-illness reference, a Southeastern vegetable crop handbook, a CDC emergency
kit checklist, and a MedlinePlus first-aid overview. The owner uses
N.O.M.A.D. as the main interface.
This is still an engineering prototype, not a complete emergency or navigation
appliance.

This repository contains the installer source, service configuration, hardware
selection logic, payload manifests, tests, and release instructions. ISOs,
package archives, container images, model weights, maps, and VM disks are local
build outputs and are excluded from Git.

## Current status

The latest customer candidate is
`/mnt/shared/fieldos-releases/fieldos-customer-test-f250cc1.iso` (source
`f250cc175ccfac137bb6bf1236497e16b3f4cbd3`, SHA-256
`26789db27ec52c683893d7cf1644782b83490e845339ada854538b7f1facebc2`). It
passed structural verification and a fresh interactive install in a disposable
no-NIC UEFI VM, followed by firstboot and two reboots. The test exercised local
CPU chat, embeddings, Kiwix, Source Library, and real browser map views. Full
results and limits are in [current validation](docs/VALIDATION-CURRENT.md) and
`/mnt/shared/fieldos-e2e/customer-f250cc1-interactive/report.md`. This remains
a private engineering candidate, not a redistribution-cleared public release.

The separate clean-source unattended E2E from `d04f450` passed no-NIC install,
firstboot, AI, embeddings, Kiwix, Source Library, eight Tennessee browser map
views, and two reboots. Evidence:
`/mnt/shared/fieldos-e2e/20261106T072733Z-566287/report.md`. Its test ISO and
payload are distinct from the interactive customer candidate.

Physical installation/hardware, GPU acceleration, GPS, network-connected
exposure, broader reference coverage, AI retrieval quality, and redistribution
clearance remain open. Wikipedia 100 is a fixture; do not rely on the local
model for safety-critical decisions. FieldOS is not release approved.

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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-test-f250cc1.iso
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
[content-pack architecture](docs/CONTENT-PACKS.md) documents the tested
candidate's core references, a pending CDC private-well addition, optional
packs, and planned categories.
Review [security boundaries](docs/SECURITY.md)
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
