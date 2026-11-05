# Installation

## Customer installation

**Current unpublished customer-mode test candidate (2026-11-05):**
`/mnt/shared/fieldos-releases/fieldos-customer-offline-1851e34.iso`, source
`1851e3491d6f7e28d53b73a6e02239d2ff681121`, SHA-256
`9d43df4be724a9937eb931347279660226976d1a6914c235fcba9244e418a4a6`.
Interactive identity and target-disk selection, disconnected installation,
firstboot, installed-disk boot after the normal media-removal prompt, and two
reboot checks passed in a disposable no-NIC UEFI VM. After the second reboot,
local chat, embeddings, Kiwix search, map-tile access, and all seven containers
were verified; Firefox visibly rendered Nashville map detail and the FieldOS
Command Center. The detailed report and screenshots are at
`/mnt/shared/fieldos-e2e/customer-offline-1851e34/report.md`.

The test controller ejected the virtual ISO at Ubuntu's standard “remove the
installation medium” prompt. This tested the installed-disk boot path without
repair; physical USB behavior remains unverified. The candidate is unpublished
engineering test material, not an approved public release. Physical hardware,
network-connected security, content breadth, and redistribution review remain
open; see [`RELEASE.md`](RELEASE.md).

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

Before testing, compare the ISO SHA-256 with the current candidate value above:

```sh
sha256sum /mnt/shared/fieldos-releases/fieldos-customer-offline-1851e34.iso
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
