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

The latest clean-source offline acceptance passed on revision
`ec57fed731e915c4c0585dc1e6c648d71d338566`. The run completed unattended
Ubuntu installation with no virtual NIC, local package and image provisioning,
N.O.M.A.D. health, a real Ollama response, embeddings, Kiwix retrieval, and
browser rendering of the separately transferred Middle Tennessee map at zoom
13. The map and services persisted across two guest reboots. Evidence is at
`/mnt/shared/fieldos-e2e/20261103T194719Z-2651472/`; its test ISO SHA-256 is
`c775083ba8538dd282bc20efd82851ec2c2ddb747327f2fa5a1a33d7dc38ad42`, and the
browser screenshot is `map-render.png`. The disposable 80 GiB disk was retired
after the PASS; installer/firstboot logs, report, screenshot, and retirement
audit remain. This does not certify the separate customer installer.

The most recent previously tested customer ISO is
`/mnt/shared/fieldos-releases/fieldos-customer-test-branded-8b0bda3.iso`,
SHA-256 `fbec9104316cf0407acc7a5e218a26922ea1849dc3a97d52a45fef09da5db7b1`.
It is stale relative to the accepted source. Its interactive installation
selected identity and disk, booted from installed storage and passed service
checks across reboots, but the guest powered off at media handoff and required
a host start from disk. A current-source customer ISO rebuild and separate
interactive test remain required. FieldOS is not approved for physical customer
installation. LAN peer isolation, physical GPU inference, broader hardware
coverage, and redistribution review also remain open. See
[release evidence](docs/RELEASE.md) for the current gate matrix.

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
make verify ISO=build/out/fieldos-test.iso
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
