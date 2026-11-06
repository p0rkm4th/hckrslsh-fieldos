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

The latest tested source revision is `d04f450`. `make check test` passes 126 tests and the
content-pack validator accepts 11 catalog entries. The CDC private-well pack
has a checksum-verified portable archive and passed in the clean-source
no-network test ISO below. It is not yet in the separately tested interactive
customer ISO.

The latest customer-mode test candidate is
`/mnt/shared/fieldos-releases/fieldos-customer-5abae15.iso` (SHA-256
`8cd07f41cf34b0606553364b89acf5689ee531d150446a1d5551b41694550f67`). A fresh
interactive no-NIC UEFI installation, installed-disk boot, firstboot, and two
reboots passed. Local chat, embeddings, Tennessee map rendering, Source Library
search, and Kiwix article retrieval were also exercised. Exact evidence and
limitations are in [current validation](docs/VALIDATION-CURRENT.md). This ISO
predates the private-well pack and remains an engineering candidate, not a
redistribution-cleared release.

A clean-source unattended no-NIC E2E from `d04f450` passed installation,
firstboot, CPU chat and embeddings, Kiwix retrieval, the FieldOS Source Library
including the new private-well entry, Firefox renders at eight Tennessee
locations, and two reboots. Test ISO SHA-256:
`6a3fef4deba8b8ade1f1e04df15b2da97665a777fb19c120fc4bcea97e81a624`;
payload SHA-256:
`ad0e28863afbddd94b65ecd9d0cc8101ee0119cdfe7a1a33b9054f895f63eae`.
Evidence is `/mnt/shared/fieldos-e2e/20261106T072733Z-566287/report.md`.
The test ISO was removed by the runner; physical-device qualification and the
separate customer-mode installation remain distinct gates.

Physical hardware, GPU acceleration, GPS, connected-network/LAN exposure,
broader offline references, AI retrieval quality, and redistribution clearance
remain open. FieldOS is not an emergency or medical appliance; do not rely on
the local model for safety-critical decisions.

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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-5abae15.iso
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
