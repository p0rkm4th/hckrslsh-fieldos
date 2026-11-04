# Hckrslsh FieldOS

FieldOS is an offline capable x86-64 field computer built on Ubuntu Desktop
and [Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad).
It bundles the container images, local AI models, a 100-article Wikipedia
fixture, low-zoom overview maps plus a bounded zoom-13 Middle Tennessee map,
CDC water/food references, and attributed FieldOS-edited NWS tornado, flood,
hurricane, and winter-storm summaries for offline use. The owner uses
N.O.M.A.D. as the main interface.
This is still an engineering prototype, not a complete emergency or navigation
appliance.

This repository contains the installer source, service configuration, hardware
selection logic, payload manifests, tests, and release instructions. ISOs,
package archives, container images, model weights, maps, and VM disks are local
build outputs and are excluded from Git.

## Current status

Latest clean-source unattended E2E: commit `7e2674e285be158f56b556f048ad3c785d8b0cb9`.
`make check test` passed 73 tests at that revision. The no-NIC test installed
Ubuntu, activated/indexed all four core reference packs, generated local
inference, loaded embeddings, rendered the zoom-13 Middle Tennessee map in
Firefox, and passed two reboots. Report:
`/mnt/shared/fieldos-e2e/20261104T152431Z-3714447/report.md`; test ISO SHA-256:
`0fcb81e0f5e7043024486a6caa11ca31a7e85c2ae17054e4649c1d8f7b3c5fc6`.

The latest customer-mode candidate was built from clean source commit
`85a33f866f1b929762e47cc5462b16cbbd84c43c`:
`/mnt/shared/fieldos-releases/fieldos-customer-regional-85a33f8.iso` (SHA-256
`5c238570a7b2b9ff4fc9277692af618d0379f0edbd4ce989db3c963008cad4a0`). A fresh
interactive no-NIC UEFI installation selected the 80 GiB virtual disk, completed
offline firstboot, launched N.O.M.A.D., generated a real local response, loaded
embeddings, retrieved Kiwix content in Firefox, rendered the Nashville zoom-13
map, and passed two reboots with persistent user data. At the media-removal
prompt the VM powered off; its installed disk booted on the next manual start.
Physical USB handoff remains untested. Screenshots and the detailed report are
in `/mnt/shared/fieldos-e2e/customer-85a33f8/`. This is an engineering test
candidate, not a release approval.

The previous customer-mode candidate used the sanitized payload
`/mnt/shared/fieldos-payload/offline-payload.tar.zst` (SHA-256
`188d0692cb6bb6c15d2bcb89335c80b75447cf4cd4f844c51e2e4e6a4c5e1a52`); generated
Ollama registry keys and cache are excluded. A new payload containing the four
core packs, also excluding generated keys and cache, is
`/mnt/shared/fieldos-payload-weather-flood-core/offline-payload.tar.zst` (SHA-256
`fb4ad0e04144edd4e914263fb9279833cd1ce7e716a10817e79762824b28a73e`). The
current customer-mode ISO has not yet been rebuilt with this updated baseline.
FieldOS is not disaster-ready: its reference set and map coverage remain
limited, AI safety behavior is not comprehensive, physical GPU and LAN isolation
remain unverified, and redistribution review is incomplete. See
[docs/RELEASE.md](docs/RELEASE.md) and the [field-use assessment](docs/FIELD-USE-ASSESSMENT.md)
for remaining gates and scenario findings.
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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-regional-85a33f8.iso
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
