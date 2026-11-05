# Hckrslsh FieldOS

FieldOS is an offline capable x86-64 field computer built on Ubuntu Desktop
and [Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad).
It bundles the container images, local AI models, a 100-article Wikipedia
fixture, low-zoom overview maps, and a zoom-13 statewide Tennessee map,
CDC water/food references, and attributed FieldOS-edited NWS tornado, flood,
hurricane, and winter-storm summaries for offline use. The owner uses
N.O.M.A.D. as the main interface.
An optional, separately transferable 2026 Southeastern vegetable-growing
handbook is cataloged and transfer/index tested; it is not part of the core or
customer ISO.
This is still an engineering prototype, not a complete emergency or navigation
appliance.

This repository contains the installer source, service configuration, hardware
selection logic, payload manifests, tests, and release instructions. ISOs,
package archives, container images, model weights, maps, and VM disks are local
build outputs and are excluded from Git.

## Current status

FieldOS remains an engineering test candidate, not an approved emergency or
navigation appliance. The latest interactive customer-mode ISO is
`/mnt/shared/fieldos-releases/fieldos-customer-statewide-bc7e4c1.iso`, built
from clean commit `bc7e4c1c3d0ec79519cc41b7c6ce1cd3a702b10c`; SHA-256
`bdfbe5c01f9960634f275e230c3a3957623f778c511c36a73ddf992a2f4e85bd`. In a
disposable no-NIC UEFI VM, interactive disk/account selection, installation,
offline firstboot, local AI, embeddings, Kiwix, statewide Tennessee map views,
and two reboot checks passed. The latest clean-source unattended E2E also
passed at source `b5d6f748c9efdb0f4345c5fe92533b882c7e2856`. Exact logs,
screenshots, source revision and remaining limitations are recorded in
[`docs/RELEASE.md`](docs/RELEASE.md).

The detailed Tennessee map covers the state and a neighboring-state buffer at
zoom 0–13. The core reference library is still limited. An optional 2026
Southeastern vegetable handbook and a narrow NIOSH heat-illness reference have
been transferred and indexed in test guests; neither optional pack is in the
current ISO. The NIOSH reference survived a reboot, but its new browser view
has not been visually confirmed. Physical hardware, GPS, LAN-connected
security, broader field references, and redistribution clearance remain
unverified or incomplete. Do not rely on the local model for medical or
emergency decisions.
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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-statewide-bc7e4c1.iso
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
[content-pack architecture](docs/CONTENT-PACKS.md) includes a small bundled
water/food source pack and planned categories. Review [security boundaries](docs/SECURITY.md)
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
