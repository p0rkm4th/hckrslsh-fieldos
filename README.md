# Hckrslsh FieldOS

FieldOS is an offline capable x86-64 field computer built on Ubuntu Desktop
and [Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad).
It bundles the container images, local AI models, a 100-article Wikipedia
fixture, zoom-5 basemaps, and a small attributed CDC water/food source pack for
offline use. The owner uses N.O.M.A.D. as the main interface. This is still an
engineering prototype, not a complete emergency or navigation appliance.

This repository contains the installer source, service configuration, hardware
selection logic, payload manifests, tests, and release instructions. ISOs,
package archives, container images, model weights, maps, and VM disks are local
build outputs and are excluded from Git.

## Current status

Last validated source revision: `f9c10ec170c2b33000a287a0ee8ef38d6e2b0f50`. The
working tree adds native N.O.M.A.D. Knowledge Base ingestion for bundled CDC
documents. Its first fresh E2E run failed because the new indexer was omitted
from the ISO staging list; the run report and logs are retained, the staging
and verifier lists are corrected, and a fresh E2E rerun is required before
replacing the candidate below.

The clean-source offline E2E passed with no virtual NIC, including firstboot,
seven services, local chat and embeddings, Kiwix retrieval, Firefox map and
reference-library rendering, the bundled CDC starter pack, and two reboots.
The separate interactive customer-mode installation completed on a blank
disposable UEFI disk and booted to the branded desktop. In this run the installer
media-removal prompt powered off QEMU after Enter, so a host-side `virsh start`
was needed to boot the installed disk; the installer handoff gate remains
partial. The test and customer-mode reports are retained under
`/mnt/shared/fieldos-e2e/`; see [`docs/RELEASE.md`](docs/RELEASE.md).

Current customer-mode engineering candidate:
`/mnt/shared/fieldos-releases/fieldos-customer-test-corepack-f9c10ec.iso`
(11,987,386,368 bytes), SHA-256
`95503d257465087b723ba1eb0725dbf63ac6cf2ac83383f4e35cd63af7738c8d`. This is
not an approved release. The CDC pack covers only emergency water treatment
and food safety after a power outage; the Kiwix archive has 100 articles, maps
stop at zoom 5, and the local model gave a misleading uncited answer to a
food-safety question. Do not use AI output as emergency authority. Physical
USB, GPU, broader content, LAN security, and redistribution remain unvalidated.

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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-test-corepack-f9c10ec.iso
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
