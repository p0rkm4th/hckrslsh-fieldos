# Hckrslsh FieldOS

FieldOS is an offline capable x86-64 field computer built on Ubuntu Desktop
and [Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad).
It bundles the container images, local AI models, a small Wikipedia library,
and an offline world basemap needed to use the core system without an internet
connection. The owner uses N.O.M.A.D. as the main interface.

This repository contains the installer source, service configuration, hardware
selection logic, payload manifests, tests, and release instructions. ISOs,
package archives, container images, model weights, maps, and VM disks are local
build outputs and are excluded from Git.

## Current status

The latest clean-source offline E2E acceptance passed on revision
`0085b7ac2989dc684776ae0910fe5c77dd829c0c`. It installed Ubuntu with no virtual
NIC, provisioned local packages and images, and verified N.O.M.A.D., local chat
and embeddings, Kiwix retrieval, map rendering, and persistence through two
reboots. The optional Middle Tennessee content pack was not present in this
run; its earlier independent activation test is recorded in
[`docs/CONTENT-PACKS.md`](docs/CONTENT-PACKS.md). See the retained report at
`/mnt/shared/fieldos-e2e/20261104T001739Z-2874470/report.md` and
[`docs/RELEASE.md`](docs/RELEASE.md).

The current customer-mode engineering candidate is
`/mnt/shared/fieldos-releases/fieldos-customer-test-0085b7a.iso` (11,984,044,032
bytes), SHA-256
`4d1b7ed6ed6c8089fbb0cdb416743fed2f917f9ae899d6bf6aa45de92915ba22`. Its
structure was verified and a fresh no-NIC, interactive UEFI install completed
on a disposable VM. Media removal led directly to the installed OS without a
host reset. Firstboot, seven containers, the branded desktop, local AI chat,
Kiwix, maps, and two guest restarts were checked. This validates the installer
flow in QEMU, not the appliance for field use: the only Kiwix archive has 100
articles, the bundled map lacks useful Nashville detail, and the AI answer was
generic and unsourced. Emergency and physical-hardware use remain unvalidated.
The VM disk was removed after testing; the report and screenshots remain at
`/mnt/shared/fieldos-e2e/customer-interactive-0085b7a-20261104/report.md`.

The current source has a guarded correction for N.O.M.A.D.'s information
library descriptions. That correction passed the clean-source E2E and was
visually confirmed in this customer candidate's Command Center. The older `c744e52` ISO binary was retired after the replacement candidate
was built; its checksum and historical test report remain for traceability.

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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-test-0085b7a.iso
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
[content-pack architecture](docs/CONTENT-PACKS.md) is defined with an empty
catalog pending source and license review. Review [security boundaries](docs/SECURITY.md)
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
