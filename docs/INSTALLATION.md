# Installation

## Customer installation

**Current unpublished customer-mode test candidate (2026-11-04):**
`/mnt/shared/fieldos-releases/fieldos-customer-statewide-bc7e4c1.iso`, source
`bc7e4c1c3d0ec79519cc41b7c6ce1cd3a702b10c`, SHA-256
`bdfbe5c01f9960634f275e230c3a3957623f778c511c36a73ddf992a2f4e85bd`.
Interactive identity and target disk selection, offline installation,
firstboot, local services, and installed-disk boot passed in a disposable
no-NIC UEFI VM. Local chat, embeddings, Kiwix search, and Firefox map rendering
at eight Tennessee locations were verified. Two reboots preserved services,
map and knowledge availability, provisioning state, and user data. Detailed
report, logs, and screenshots:
`/mnt/shared/fieldos-e2e/customer-statewide-bc7e4c1/report.md`.

In this QEMU run, the ISO remained in the boot path after the initial restart.
After the virtual media was ejected and the VM powered on again, Ubuntu booted
from the installed disk without repair. Remove USB installation media when
prompted and power the computer back on if Ubuntu shuts down. Physical USB
installation and handoff have not been tested. This image is engineering test
material, not an approved public release; see [`RELEASE.md`](RELEASE.md).

Build a customer-mode test ISO with:

```sh
make iso-test UBUNTU_ISO="/path/to/ubuntu-26.04.1-desktop-amd64.iso"
```

The GRUB menu defaults to `Install Hckrslsh FieldOS (interactive)` after its
countdown. This entry uses the local FieldOS NoCloud configuration while
leaving identity and storage interactive. The ordinary `Try or Install Ubuntu`
entry is the upstream Ubuntu live installer and does not run FieldOS
provisioning. In the FieldOS installer, select the intended target disk and
review its erase confirmation carefully. Use the supported Ubuntu encryption
option if full-disk encryption is required. The unattended identity and storage
settings in `make test-e2e` are not part of the customer ISO.

Ubuntu documents that an autoinstall `shutdown` action is ignored when
interactive sections are configured, so FieldOS does not set one or treat it as
a handoff mechanism. See Canonical's
[autoinstall reference](https://canonical-subiquity.readthedocs-hosted.com/en/latest/reference/autoinstall-reference.html#shutdown).
Do not install on physical customer hardware until the remaining release gates
in [`RELEASE.md`](RELEASE.md) are complete.

## Verifying the candidate

Before testing, compare the ISO SHA-256 with the value above:

```sh
sha256sum /mnt/shared/fieldos-releases/fieldos-customer-statewide-bc7e4c1.iso
```

For future install tests, use a disposable VM disk with no virtual network
device. Never point the installer at a physical or protected HADES disk. The
interactive customer workflow and the unattended E2E workflow are separate
tests; a passing unattended run does not certify the customer installer.

## First boot and desktop

After installation, firstboot may take several minutes while it verifies and
unpacks the local payload, installs packages from the included APT repository,
loads container images, validates the local model, and indexes bundled source
documents. Progress and failures are recorded in
`/var/log/fieldos-firstboot.log` and
`/var/lib/fieldos/provisioning-status.json`. Do not interrupt power during
firstboot.

Sign in to the account selected during installation. **FieldOS Command Center**
opens N.O.M.A.D. at `http://localhost:8080`; **FieldOS Start Here** explains
which resources are included and which packs are optional. **FieldOS Content
Sources and Limits** opens source, license, and safety notes. To import an
offline pack without terminal commands, launch **FieldOS Install Content
Pack** from Applications → Utilities, select the `.tar.zst` archive beside its
`.sha256` sidecar, and approve the administrator prompt. The wallpaper, icon,
and dock shortcuts are local assets. Core application endpoints bind to
loopback and do not require an Internet connection.

For diagnostics, run:

```sh
sudo /opt/fieldos/scripts/fieldos-diagnostics.sh
```

## Development installation

For development, use the test-only image and a disposable QEMU/KVM disk:

```sh
make test-e2e UBUNTU_ISO="/path/to/ubuntu-26.04.1-desktop-amd64.iso"
```

This test is unattended and creates a VM without a virtual network device. Do
not point `virt-install` or any installer at a physical drive. See
[`TESTING.md`](TESTING.md) for prerequisites, artifacts, and failure recovery.
