# Hckrslsh FieldOS

FieldOS is an offline capable x86-64 field computer built on Ubuntu Desktop
and [Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad).
It bundles the container images, local AI models, a 100-article Wikipedia
fixture, low-zoom overview maps, and a zoom-13 statewide Tennessee map,
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

Latest statewide-map offline E2E: base commit `7e6fa24486f4fd500c7be9191119480acfe5762c`
with local map and verifier changes (the report records a dirty worktree).
`make check && make test` passed 73 tests. A fresh no-NIC VM installed Ubuntu,
completed firstboot, ran seven services, generated local inference, loaded
embeddings, searched the bundled reference, visibly rendered Firefox maps at
Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Jackson, Johnson City,
and rural Big South Fork, and passed two reboots. Report and screenshots:
`/mnt/shared/fieldos-e2e/20261104T210719Z-896057/report.md`; test ISO SHA-256:
`c0e2578509cde5522400cdd2969e8793f2278ac4e11f50900728a79acd6c2f09`.
The map is a 145,267,908-byte zoom 0–13 Protomaps extract; SHA-256
`0d123132839b77e627c4f4f103bf7a78925099c57319e759757be3207cb89525`.
It is verified in the unattended test image, not yet in a new customer ISO.

The current customer-mode candidate was built from clean source commit
`21ad4fcdb882998ca1c3bd47333b1139c162651c`:
`/mnt/shared/fieldos-releases/fieldos-customer-core4-21ad4fc.iso` (SHA-256
`38acf9bda9d62b328e5baf117895d25affa78688730cf9da1be7b4769791f9bd`). A fresh
interactive no-NIC UEFI installation selected the virtual disk and user,
completed offline firstboot, rendered the regional map in Firefox, and passed
chat, embeddings, Kiwix, and two reboot checks. The exact report and screenshots
are in `/mnt/shared/fieldos-e2e/customer-core4-21ad4fc/report.md`. At media
handoff the VM powered off after virtual CD ejection; the next power-on booted
the installed disk without repair. Physical USB handoff is untested. This is
still an engineering candidate, not a release approval.

The latest rebuilt payload is
`/mnt/shared/fieldos-payload/offline-payload.tar.zst` (SHA-256
`cdc90ea60a517bcc3217f8630a1fdfcceb3d208acaa54bead1f81260bb5351b6`).
Generated Ollama registry keys and cache are excluded. The last customer ISO
is still the earlier four-pack Middle Tennessee candidate listed below; it
does not contain the statewide map. FieldOS is not disaster-ready: reference
coverage is limited, AI safety behavior is not comprehensive, physical GPU and
LAN isolation remain unverified, and redistribution review is incomplete. See
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
make verify ISO=/mnt/shared/fieldos-releases/fieldos-customer-core4-21ad4fc.iso
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
