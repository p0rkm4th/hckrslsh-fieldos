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
test requires at least 50 GiB free on the evidence volume and 8 GiB free for
temporary build work.

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
The runner checks the map viewport contains actual low-zoom water tiles, then
checks blocked container egress and repeats service/model/reference/map-tile
checks after two guest reboots. The guest has no external network interface;
Docker's local UI bridge also disables masquerading.

## Outputs and cleanup

Each run keeps `report.md`, installer/firstboot logs when available, service
state, screenshots, and the disposable VM disk beside each other. Temporary
unattended user-data and the test ISO are removed when the runner exits,
including when a check fails. Failed reports and logs remain useful evidence;
after review, a stopped disposable guest disk may be removed to reclaim space,
with its report updated to record the disposition.

The test domain and disk are never reused or overwritten. To remove a completed
test guest after reviewing its report, first shut it down, then remove only
that exact libvirt domain and its matching run-directory `guest.qcow2`. Do not
remove active production infrastructure domains, physical disks, or unrelated files. Old test logs
are useful evidence and should be retained with the release record.

The test runner reports only checks actually executed. A successful ISO build
is not an installation or service acceptance result. Synthetic hardware
fixtures in `tests/test_select_profile.py` exercise policy branches but are
not GPU validation.
