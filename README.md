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

Repository revision before this documentation update: `4532c0677eaaabbedfdff51906c5a9d879cd9955`. The current customer-mode candidate was built cleanly from `562fee9b93c53679f57fd25af49fd79fc61a2d95`: `/mnt/shared/fieldos-releases/fieldos-customer-searchable-562fee9.iso`, SHA-256 `4d9ccf3f3e7d9b30bc0b0bf645303bb97e683a7eb79a9ffcd570edcbb2111ccfe`. On 2026-11-05 it passed a fresh interactive install to a disposable 80 GiB UEFI VM disk with no NIC, detached installation media, completed offline firstboot, and booted to the branded desktop. Two consecutive guest reboots retained user data, maps, references, and seven services. The earlier report of a disabled disk-selection button was an interaction error: the button looked disabled, but a properly delivered click advanced the installer. Full results and screenshots: `/mnt/shared/fieldos-e2e/customer-searchable-562fee9/validation.md`.

In that installed customer candidate, the selected Qwen3 1.7B CPU model generated `FIELDOS_CUSTOMER_BOOT_OK`; the 768-dimensional embedding API returned a nonempty vector; N.O.M.A.D. chat returned a real response; all nine installed reference documents reached indexed state; and Kiwix opened a locally stored article in Firefox. The Tennessee map visibly rendered at Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Jackson, Johnson City, and Big South Fork. Urban detail is useful; rural detail is sparse, and the map does not provide routing or GPS positioning. The Kiwix encyclopedia remains a 100-article test fixture, and semantic answer/citation quality is not reliable enough for safety-critical use.

The latest clean-source unattended E2E passed separately on `dc6d823bd8427c9193588e5460c28a7e4b20aad8`. Its no-NIC UEFI install provisioned seven services, exercised CPU inference and embeddings, indexed references, served Kiwix, rendered statewide Tennessee maps in Firefox, blocked container egress, and passed two reboots. Screenshots, logs, and report are in `/mnt/shared/fieldos-e2e/searchable-sidecars-20261105/20261105T095217Z-2608514/`; its temporary ISO was removed after the run. The payload was `/mnt/shared/fieldos-payload-searchable-20261105/offline-payload.tar.zst`, SHA-256 `b8f798477aae21468d86afd4d44df9cbf1d8cbc16463e358d5fc98aac0787403`. This is a separate unattended-test path, not the interactive install described above.

The candidate is validated in a VM only. Physical USB/firmware behavior, varied physical hardware and GPUs, LAN exposure review, broader field references, AI grounding/citations, and redistribution clearance remain open. This is not an emergency or medical appliance; do not rely on the local model for safety-critical decisions. See [`docs/RELEASE.md`](docs/RELEASE.md) for the acceptance matrix and limitations.

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
