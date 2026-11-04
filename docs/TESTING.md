# Automated acceptance testing

## Prerequisites

The workstation needs KVM/libvirt, QEMU, `virt-install`, `virsh`, `qemu-img`,
xorriso, Python 3, Docker Engine, and the pinned Ubuntu
26.04.1 Desktop ISO.
Run the command as the workstation account that owns the existing libvirt
session. Set `UBUNTU_ISO` if the source ISO is outside the workstation's
default media path. With `/mnt/shared` mounted, the Makefile defaults test
evidence to `/mnt/shared/fieldos-e2e`, temporary build work to
`/mnt/shared/fieldos-build`, prepared payload to `/mnt/shared/fieldos-payload`,
and release outputs to `/mnt/shared/fieldos-releases`. Override
`FIELDOS_E2E_ROOT`, `FIELDOS_WORK_ROOT`, `FIELDOS_PAYLOAD_ROOT`, or
`FIELDOS_OUTPUT_ROOT` to use other storage. Before creating artifacts, the
test requires at least 48 GiB free on the evidence volume and 8 GiB free for
temporary build work. `build/build-iso.sh` also estimates complete output ISO
and payload staging space before creating a work directory; when output and
work share a filesystem, it checks their combined requirement.

`make payload` also requires at least 50 GiB free on both the payload output
and staging volumes. It refuses to overwrite an existing payload archive;
move an old archive aside explicitly before rebuilding. The acceptance VM RAM
can be configured with `FIELDOS_TEST_MEMORY_MIB` (default `12288`, minimum
`8192` MiB). For example, to run at the minimum supported acceptance size:

```sh
FIELDOS_TEST_MEMORY_MIB=8192 make test-e2e
```

```sh
make check
make test
FIELDOS_E2E_ROOT="/path/to/large-volume/fieldos-e2e" make test-e2e \
  UBUNTU_ISO="/path/to/ubuntu-26.04.1-desktop-amd64.iso"
```

## What the VM test does

Each run gets a timestamped directory below `FIELDOS_E2E_ROOT` and a distinct
libvirt domain. It creates a fresh 80 GiB qcow2 virtual disk, builds a test only ISO
with a generated temporary account, and boots it in UEFI mode with a
loopback-only VNC console and no virtual network device. No human display or
mouse/keyboard interaction is required; the harness sends login/browser keys
and captures a virtual-screen screenshot. Test-only first-login completion
markers suppress Ubuntu's GNOME welcome-upgrade flow. The test configuration specifies
the Ubuntu Desktop source and `shutdown: poweroff`; the runner waits for the
installer to power off or for the installed guest agent to come online before
continuing. This avoids interpreting installer screens or injecting restart
keys. The unattended configuration exists only inside that test ISO; the
normal customer ISO retains interactive identity and target disk selection.

After installation, the harness ejects the ISO, boots the installed disk if it
is powered off, and uses a QEMU guest agent channel to read logs and run checks
inside the guest.
Checks include local package provisioning, container state, N.O.M.A.D. health,
Ollama chat generation, embedding output, Kiwix library/search, a PMTiles world
tile and a registered sample region, and a rendered browser map screenshot.
They also check the installed content source guide, bundled license text, and
the reference archive checksum against its pinned manifest.
When `FIELDOS_TEST_CONTENT_PACK=/path/to/bundle.tar.zst` is set, the harness
creates a separate read-only transfer ISO and imports the pack entirely offline.
Map packs are checked against N.O.M.A.D.'s map inventory, rendering, and reboot
persistence. Reference-document packs are checked for checksum-matched installed
and web-served copies, a Firefox source-index view, and reboot persistence. A
direct document URL is also checked over the loopback web server; review the
retained screenshot when validating a specific PDF viewer experience. For
example:

```sh
FIELDOS_TEST_CONTENT_PACK="/mnt/shared/fieldos-content-packs/content-packs/us-water-food-emergency-1.0.0.tar.zst" \
  make test-e2e UBUNTU_ISO="/path/to/ubuntu-26.04.1-desktop-amd64.iso"
```
The runner checks the map viewport contains actual low-zoom water tiles, then
checks blocked container egress and repeats service/model/reference/map-tile
checks after two guest reboots. The guest has no external network interface;
Docker's local UI bridge also disables masquerading.

Each report records the source commit and whether the worktree had local
changes, alongside the test ISO SHA-256, so a test result can be tied to the
source used to build it.

An automated PASS requires an untouched fresh guest, unattended installation,
and all recorded checks to complete without manual repair. A recovered VM or
an installation that needed host-side intervention is diagnostic evidence,
not a clean automated PASS. Interactive customer-ISO installation is a
separate release gate and must be reported separately.

## Outputs and cleanup

Each run keeps `report.md`, installer/firstboot logs when available, service
state, screenshots, and the disposable VM disk beside each other. Temporary
unattended user-data and the test ISO are removed when the runner exits,
including when a check fails. Failed reports and logs remain useful evidence;
after review, a stopped disposable guest disk may be removed to reclaim space,
with its report updated to record the disposition.

The test domain and disk are never reused or overwritten. To remove a completed
test disk after reviewing its report, use the exact run-directory path. The
cleanup command defaults to dry run and refuses disks attached to any domain,
runs referenced by the release record, paths outside the E2E evidence root,
non-qcow2 files, or disks without a retained report. It deletes only the qcow2
and leaves screenshots, logs, `report.md`, and a retirement audit record:

```sh
make cleanup-test-disk DISK="/mnt/shared/fieldos-e2e/<run>/guest.qcow2"
make cleanup-test-disk DISK="/mnt/shared/fieldos-e2e/<run>/guest.qcow2" \
  DELETE=1 REASON="superseded stopped disposable run"
```

Review the dry-run result and report first. Never use this for physical disks,
active guests, or unrelated files. The command does not stop guests or remove
libvirt domains. Preserve current acceptance disks and any disk referenced by
`docs/RELEASE.md`. Old test logs and screenshots are useful evidence and remain
after disk retirement.

The test runner reports only checks actually executed. A successful ISO build
is not an installation or service acceptance result. Synthetic hardware
fixtures in `tests/test_select_profile.py` exercise policy branches but are
not GPU validation.
