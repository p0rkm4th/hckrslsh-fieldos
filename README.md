# Hckrslsh FieldOS

FieldOS is an offline capable x86-64 field computer built on Ubuntu Desktop
and [Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad).
It bundles the container images, local AI models, a 100-article Wikipedia
fixture, low-zoom overview maps plus a bounded zoom-13 Middle Tennessee map,
CDC water/food references, and an attributed NWS tornado guide for offline
use. The owner uses N.O.M.A.D. as the main interface.
This is still an engineering prototype, not a complete emergency or navigation
appliance.

This repository contains the installer source, service configuration, hardware
selection logic, payload manifests, tests, and release instructions. ISOs,
package archives, container images, model weights, maps, and VM disks are local
build outputs and are excluded from Git.

## Current status

Latest tested source commit: `d8653336ea4597df8eb386a83d364c9dca19d290`.
`make check test` passes 71 tests. A clean-source no-NIC E2E at this exact
revision passed offline installation, firstboot, N.O.M.A.D., CPU inference,
embeddings, Kiwix retrieval, visible zoom-13 Middle Tennessee maps, optional
weather-pack transfer/indexing, and two reboots. Report:
`/mnt/shared/fieldos-e2e/20261104T125608Z-3534340/report.md`; test ISO SHA-256:
`0bd97610307320f5dd725b94eead0745ba61fbff69083d5d43d7f4ff473e2781`.

The separate interactive customer-mode candidate remains
`/mnt/shared/fieldos-releases/fieldos-customer-regional-3054c59.iso` (SHA-256
`522abcbc4ba04593ce7d1813af43c5c86110b22a41239c13c3e9800f017d1686`). Its
fresh disposable-VM install, desktop, and two reboot checks passed. The media
handoff powered off the VM at the virtual CD removal prompt; physical USB
handoff is untested. The optional `us-weather-safety` pack passed offline transfer testing; a new
`us-flood-safety` pack also passed no-network transfer, browser, indexing, and
two-reboot checks in a dirty-worktree pack integration run (using virtual optical transfer media, not physical USB); this is not a clean-source release pass. Both remain outside the customer ISO. Flood-pack evidence is
recorded in `docs/CONTENT-PACKS.md`; see the [field-use assessment](docs/FIELD-USE-ASSESSMENT.md). FieldOS remains an engineering candidate, not a disaster-ready or
customer-approved appliance: its reference set and map coverage are limited,
AI safety behavior is not comprehensive, physical GPU and LAN isolation remain
unverified, and redistribution review is incomplete. See
[docs/RELEASE.md](docs/RELEASE.md) for exact evidence and remaining gates, and [docs/FIELD-USE-ASSESSMENT.md](docs/FIELD-USE-ASSESSMENT.md) for the scenario-by-scenario preparedness review.

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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-regional-3054c59.iso
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
