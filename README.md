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

Latest source is `562fee9`. Its customer-mode ISO is `/mnt/shared/fieldos-releases/fieldos-customer-searchable-562fee9.iso`, SHA-256 `4d9ccf3f3e7d9b30bc0b0bf645303bb97e683a7eb79a9ffcd570edcbb2111ccfe`. A fresh no-NIC UEFI VM booted the installer, but Ubuntu listed no selectable installation target and kept Next disabled even though the 80 GiB `/dev/vda` was visible to `lsblk` and `fdisk`; no writes occurred. This build has **not** passed interactive installation. Evidence and screenshots: `/mnt/shared/fieldos-e2e/customer-searchable-562fee9/validation.md`.

The previous candidate, `ac319b3aa1c458295bd2672f7608f146870a2df8`, did pass interactive no-NIC UEFI installation, firstboot, desktop app checks, and two reboots; it remains the latest passing customer-mode VM install. Physical USB behavior remains unverified, and source-assisted AI produced unrelated crop advice without visible citations. See [`docs/RELEASE.md`](docs/RELEASE.md) for exact evidence and remaining blockers.

The latest clean-source E2E passed on `dc6d823bd8427c9193588e5460c28a7e4b20aad8`. Its no-NIC UEFI install provisioned seven services, exercised CPU model initialization and generation, loaded embeddings, indexed references, served Kiwix, rendered all eight statewide Tennessee locations in Firefox, blocked external egress, and passed two reboots. Screenshots, logs, and report are in `/mnt/shared/fieldos-e2e/searchable-sidecars-20261105/20261105T095217Z-2608514/`; the test ISO was removed after the run (SHA-256 `77a7408739d302f312ea2a16e1beb875469bb1a55936c149715d55733681ea25`). The payload was `/mnt/shared/fieldos-payload-searchable-20261105/offline-payload.tar.zst`, SHA-256 `b8f798477aae21468d86afd4d44df9cbf1d8cbc16463e358d5fc98aac0787403`. An optional content-transfer branch was skipped. This unattended E2E does not validate interactive installation; the newer customer-mode install failure is recorded above.

The unattended E2E and customer-mode installer are separate acceptance paths. The latest unattended E2E passed; the newest customer ISO's interactive VM install failed at disk selection, while the earlier `ac319b3` candidate passed. Physical USB behavior is untested. See [`docs/RELEASE.md`](docs/RELEASE.md) for the full gate matrix and unresolved content, semantic retrieval, security, licensing, and hardware work.

These results establish engineering test acceptance in VMs, not physical hardware support or release readiness. Physical USB behavior, hardware/GPU variety, LAN exposure review, grounded AI answer quality, broader field reference coverage, and redistribution clearance remain open. This is not an emergency or medical appliance; do not rely on the local model for safety-critical decisions. Detailed source revisions, checksums, reports, and limitations are in [`docs/RELEASE.md`](docs/RELEASE.md); the latest customer install attempt and screenshots are at `/mnt/shared/fieldos-e2e/customer-searchable-562fee9/`, with the prior passing VM install retained at `/mnt/shared/fieldos-e2e/customer-ac319b3-20261105/`.

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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-offline-ac319b3.iso
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
