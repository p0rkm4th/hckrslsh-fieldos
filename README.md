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
`/mnt/shared/fieldos-releases/fieldos-customer-handoff-c744e52.iso`, SHA-256
`c8b09f678351b87a2d3784c4bd91949b6add9a7bb6ad5a9a8a5401a059f762f7`, built
from `c744e52`. A fresh interactive QEMU install selected identity and disk,
but the guest powered off after Enter at the media-removal prompt. The host had
to start the installed disk. The system then passed provisioning, local
service, inference, and two-reboot checks. End-user testing also found that the
one-book Wikipedia fixture and zoom-5 map are inadequate for field emergencies,
and the local AI can label unsourced generic guidance “Verified.” FieldOS is
not ready for customer or emergency use. Installer handoff, practical licensed
content, LAN peer isolation, physical GPU inference, broader hardware coverage,
and redistribution review remain open. The persistent owner-only Kasm lab now
stages the branded system on VM 913, but owner-authenticated desktop launch is
not yet verified. See
[release evidence](docs/RELEASE.md) for the current gate matrix.

The current source has a guarded correction for N.O.M.A.D.'s information
library descriptions: the home card and Easy Setup now describe only archives
installed on the device. That correction passed the clean-source E2E above.
The `c744e52` customer ISO above predates this change and still contains the
misleading upstream wording; a new customer-mode ISO must be built and tested.

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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-handoff-c744e52.iso
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
