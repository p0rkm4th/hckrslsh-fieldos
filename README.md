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
`43ec3f9faed73632c13a8113b546ade9b5bf488e`. It completed unattended Ubuntu
installation with no virtual NIC, local package and image provisioning,
N.O.M.A.D. health, a real Ollama response, embeddings, Kiwix retrieval, and
browser rendering of the separately transferred Middle Tennessee map at zoom
13. It verified truthful information-library descriptions and passed two
reboots with services and map content intact. Evidence is at
`/mnt/shared/fieldos-e2e/20261103T222621Z-2749281/report.md`; the test ISO SHA-256
is `c4fc27bc3722509d525049b5fe5b8e56396852854a49f9e65cafe1de8276b373`, and the
browser screenshot is `map-render.png`. The 80 GiB disposable disk was retired
after PASS; logs, report, screenshot, and retirement audit remain. This does
not certify the separate customer installer.

The current customer-mode engineering candidate is
`/mnt/shared/fieldos-releases/fieldos-customer-branded-b7f25b0.iso` (11.2 GiB),
SHA-256 `a6af2e66c1042f517747b0ef02b07ef7f1bc9cfdfe93ea90bb55836c799246c1`,
built from `b7f25b033fd7c7aabfd17fe686c303b4be0814b1` (documentation-only changes atop
tested code revision `43ec3f9faed73632c13a8113b546ade9b5bf488e`). Its structure and offline payload verified. A fresh no-NIC
interactive install completed to a disposable disk; firstboot, all seven
services, local AI/embeddings, Kiwix retrieval, and two guest reboots passed.
The guest reached the installer again after Restart because the USB media was
not removed promptly in this run; a tester detached it and reset the VM to boot
the installed disk. Thus the current image's automatic USB handoff remains
unverified, and this was not a clean customer-install PASS. A browser test
rendered the bundled U.S. overview, but it was blank at 10 km zoom. Kiwix
contains one 100-article fixture, and an ice-storm chat answer was generic and
not grounded in identifiable references. FieldOS is not ready for customer or
emergency use. See [release evidence](docs/RELEASE.md) and the current run at
`/mnt/shared/fieldos-e2e/customer-interactive-b7f25b0-20261103/report.md`.

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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-branded-b7f25b0.iso
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
