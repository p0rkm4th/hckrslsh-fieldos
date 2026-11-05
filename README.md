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

Candidate ISO source revision: `cc4aa38f3debd078b877589355221e94821bd160`.
The repository includes newer documentation and content metadata updates that
are not yet present in this ISO; check release notes before using it.

Current customer-mode candidate: `/mnt/shared/fieldos-releases/fieldos-customer-cc4aa38.iso`, SHA-256 `0319a069a4874d0522f660c6d69027e6ab9c4aaf86f2f8c995efb9d359a1e139`. A fresh no-NIC UEFI VM installation passed interactive target/account selection, destructive confirmation, firstboot, installed-disk boot, functional checks, and two reboots. Ubuntu displayed its standard media-removal prompt; Enter shut the guest down normally, and an ordinary VM power-on booted from the installed disk without reset or repair. This verifies customer installation and disk boot in a VM; seamless automatic restart and physical USB/hardware behavior remain unverified. The ISO is still an unpublished test candidate.

The installed system selected Qwen3 1.7B Q4_K_M on CPU and generated a response after the second reboot; the embedding model returned 768-dimensional vectors. Kiwix opened and searched its bundled 100-article Wikipedia fixture. Firefox visibly rendered zoom-13 Tennessee maps at Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Jackson, Johnson City, and Big South Fork. Nine installed reference files (689 chunks) were indexed and the Source Library returned three flood-related matches, but semantic answers and citations remain unreliable. Rural map detail is sparse; routing and GPS positioning are not provided.

`make check test` passed 87 tests, and `make verify ISO=...` confirmed BIOS/UEFI boot records, customer setup, offline APT, and payload presence. See the [current validation report](docs/VALIDATION-CURRENT.md) and [release readiness](docs/RELEASE.md). Clean handoff evidence is under `/mnt/shared/fieldos-e2e/customer-cc4aa38-handoff-20261105/`; the eight-location map screenshots are in `/mnt/shared/fieldos-e2e/customer-cc4aa38-20261105/`.

Physical installation and varied hardware, GPU acceleration, GPS, connected-LAN exposure, broader reference coverage, semantic retrieval quality, and redistribution clearance remain open. FieldOS is not an emergency or medical appliance; do not rely on the local model for safety-critical decisions.
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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-cc4aa38.iso
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
