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

The current customer-mode engineering candidate is `/mnt/shared/fieldos-releases/fieldos-customer-offline-9c59a5f.iso`, built from clean source commit `9c59a5f63cf6a2b35b7489a45cf53c0fc93d2f19`; SHA-256 `4e9800fc6facf698d2408579b42375e9d6fc31fbd38896ff2e68ada6d2654c74`. In fresh no-NIC UEFI VMs, interactive account and disk selection completed, firstboot completed, all six packs indexed as nine documents/689 chunks, and the branded desktop appeared. Chat, embeddings, Kiwix retrieval, a zoom-13 Nashville map render, and two reboots passed. A repeat install reached Ubuntu's expected media-removal prompt; after ISO removal and Enter, the VM powered off, and a normal power-on booted the installed disk without repair. The customer installer gate remains **PARTIAL** because the VM did not restart itself; physical USB behavior is untested. A separate clean unattended no-NIC E2E from the same commit passed, including eight visible map locations and container-egress checks. Reports and screenshots are listed in [`docs/RELEASE.md`](docs/RELEASE.md) and retained at `/mnt/shared/fieldos-e2e/customer-offline-9c59a5f-20261105/`, `/mnt/shared/fieldos-e2e/customer-handoff-9c59a5f-20261105/`, and `/mnt/shared/fieldos-e2e/20261105T031700Z-1734990/`.

Current source `5720321` also passed a freshly rebuilt no-NIC E2E with the optional household communications pack transferred from read-only media. The guest installed and indexed the pack, opened the Source Library in Firefox, rendered all eight Tennessee map locations, and passed two reboots. The test ISO was removed after the run; the report, payload checksum, and screenshots remain in `/mnt/shared/fieldos-e2e/20261105T051319Z-2105879/` and `/mnt/shared/fieldos-payload-5720321/`. The customer ISO above has not been rebuilt from this newer source commit.

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
