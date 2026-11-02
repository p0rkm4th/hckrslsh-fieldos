# Automated acceptance testing

## Prerequisites

The workstation needs KVM/libvirt, QEMU, `virt-install`, `virsh`, `qemu-img`,
xorriso, Python 3, Docker Engine, and the pinned Ubuntu 26.04.1 Desktop ISO.
Run the command as the workstation account that owns the existing libvirt
session. Set `UBUNTU_ISO` if the source ISO is outside the workstation's
default media path.

```sh
make check
make test
make test-e2e UBUNTU_ISO="/path/to/ubuntu-26.04.1-desktop-amd64.iso"
```

## What the VM test does

Each run gets a timestamped directory below `build/e2e/` and a distinct libvirt
domain. It creates a fresh 80 GiB qcow2 virtual disk, builds a test only ISO
with a generated temporary account, and boots it in UEFI mode without a
graphical console or virtual network device. The unattended configuration
exists only inside that test ISO; the normal customer ISO retains interactive
identity and target disk selection.

After installation, the harness ejects the ISO, boots the installed disk, and
uses a QEMU guest agent channel to read logs and run checks inside the guest.
Checks include local package provisioning, container state, N.O.M.A.D. health,
Ollama chat generation, embedding output, Kiwix library/search, a PMTiles world
tile and N.O.M.A.D. map style, blocked container egress, and two guest reboots.
The guest has no external network interface; Docker's local UI bridge also
disables masquerading.

## Outputs and cleanup

Each run keeps `report.md`, installer/firstboot logs when available, service
state, and the disposable VM disk beside each other. Temporary unattended
user-data and the test ISO are removed when the runner exits, including when a
check fails. A failed guest disk and its report remain available for diagnosis.

The test domain and disk are never reused or overwritten. To remove a completed
test guest after reviewing its report, first shut it down, then remove only
that exact libvirt domain and its matching `build/e2e/<run>/guest.qcow2`. Do not
remove active production infrastructure domains, physical disks, or unrelated files. Old test logs
are useful evidence and should be retained with the release record.

The test runner reports only checks actually executed. A successful ISO build
is not an installation or service acceptance result. Synthetic hardware
fixtures in `tests/test_select_profile.py` exercise policy branches but are
not GPU validation.
