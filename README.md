# Hckrslsh FieldOS

FieldOS is an offline capable x86-64 field computer built on Ubuntu Desktop
and [Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad).
It bundles the container images, local AI models, a 100-article Wikipedia
fixture, low-zoom overview maps, a zoom-13 statewide Tennessee map, and eight
core source packs. These include CDC water and food references, NWS-derived
tornado, flood, hurricane, and winter-storm summaries, a narrow NIOSH
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

Current source is `1e4627c` on `main` and synced to GitHub. `make check test`
passes 125 tests. The payload verifier now requires exactly the catalog's core
content-pack archive versions, so stale versions fail closed.

The last customer-mode ISO remains the separately tested candidate
`/mnt/shared/fieldos-releases/fieldos-customer-8c81d64.iso` (SHA-256
`3dd16528cde1cbbfa7dac9f8a4cea325a09857eb58a5c9b079d5917ab5c6147d`). It
passed interactive no-NIC UEFI installation and two reboot checks, but it was
not built from the current source revision. See [release readiness](docs/RELEASE.md)
and the [customer validation report](docs/VALIDATION-CURRENT.md).

A test-only unattended ISO from `c13ac18` (`c84037360019afa1dec09c70eeadf905969dcfa41e6c9af5348429bdc7114880`)
completed an offline installation, all eight Firefox map renders, GUI ZIM
import and retrieval, local chat and embeddings, source search, and two reboots.
The automated report says PASS, but a qualification note records duplicate
superseded packs in its payload; it is diagnostic evidence, not clean-payload
release acceptance. The corrected current-catalog payload is now at
`/mnt/shared/fieldos-payload/offline-payload.tar.zst` (SHA-256
`751c923846d3c3bf6e15e63e7680f351ca27d51f7030a75b818321845ffd3aa9`) and has
passed payload verification. It still needs a fresh E2E install.

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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-8c81d64.iso
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
[content-pack architecture](docs/CONTENT-PACKS.md) documents the eight core
reference packs in the tested candidate, additional optional packs, and planned
categories.
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
