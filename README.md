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

The current private customer-mode candidate is
`/mnt/shared/fieldos-releases/fieldos-customer-test-valkey-129da89.iso`
(source `129da89fff0bd769b85f42b541bf195eedb70b31`, SHA-256 `ddd9015cbc56dad3635f5453f8d0f6b5ff6a834610394cf3d2fab38dd2d796e2`). Structural verification passed. A fresh
interactive install to a disposable 80 GiB UEFI VM disk with no NIC passed;
firstboot completed; FieldOS desktop, local CPU chat and embeddings, Kiwix,
source indexing, and maps were exercised; and services and user data persisted
across two reboots. At Ubuntu's standard virtual-media prompt the guest powered
off after Enter/eject, then booted normally from the installed disk on power-on.
Physical USB handoff is untested. Detailed evidence is in
[`docs/VALIDATION-CURRENT.md`](docs/VALIDATION-CURRENT.md) and
`/mnt/shared/fieldos-e2e/customer-valkey-129da89-interactive/customer-acceptance.md`.

The exact-source unattended E2E also passed: offline installation, local
inference/embeddings, Kiwix, source indexing, eight actual Firefox Tennessee
map views, egress isolation, and two reboots. Report:
`/mnt/shared/fieldos-e2e/valkey-129da89/20261106T092845Z-735158/report.md`.
These are VM results, not physical-device validation. This is not a public
release: redistribution clearance, attached-network security testing, physical
hardware, useful broad reference coverage, and AI retrieval quality remain
open. Wikipedia 100 remains a fixture; do not use the local model as a
safety-critical authority.

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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-test-valkey-129da89.iso
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
