# Installation

## Customer installation

**Current customer-mode test candidate (2026-11-04):**
`/mnt/shared/fieldos-releases/fieldos-customer-core4-21ad4fc.iso`, source
`21ad4fcdb882998ca1c3bd47333b1139c162651c`, SHA-256
`38acf9bda9d62b328e5baf117895d25affa78688730cf9da1be7b4769791f9bd`. A fresh
interactive install in a disposable no-NIC UEFI VM selected the 80 GiB virtual
disk and user identity, completed four-pack offline provisioning, booted the
installed disk, and passed application checks across two consecutive reboots.
Firefox visibly rendered Nashville at zoom 13; local chat, embeddings, Kiwix,
and the FieldOS source library responded. Report and screenshots:
`/mnt/shared/fieldos-e2e/customer-core4-21ad4fc/report.md`. At media handoff
Ubuntu prompted to remove the virtual CD and press Enter, then powered off; the
next VM power-on booted the installed disk without repair. Physical USB handoff
is untested. This remains unpublished engineering test material, not an
approved release; see [`RELEASE.md`](RELEASE.md) for outstanding gates.

The customer-facing ISO is built with:

```sh
make iso-test UBUNTU_ISO="/path/to/ubuntu-26.04.1-desktop-amd64.iso"
```

The GRUB menu defaults to `Install Hckrslsh FieldOS (interactive)` after its
countdown. This entry invokes the local FieldOS NoCloud configuration while
leaving identity and storage interactive. The ordinary `Try or Install Ubuntu`
entry is the upstream Ubuntu live installer and does not run FieldOS
provisioning. In the FieldOS installer, select the intended target disk and
review its erase confirmation carefully. Use the supported Ubuntu encryption
option if full disk encryption is required. After installation, choose
“Restart now.” For USB installation, remove the USB media when prompted and
power the computer back on after Ubuntu shuts down. The current QEMU test
reached the explicit media-removal prompt; after ISO ejection and Enter, the VM
powered off, and its next power-on booted the installed disk normally. Physical
USB behavior is still untested. Review the remaining release gates in
[`RELEASE.md`](RELEASE.md) before installing on physical customer hardware.
FieldOS leaves the customer identity and storage sections interactive. Ubuntu
documents that an autoinstall `shutdown` action is ignored when interactive
sections are configured, so FieldOS does not set one or treat it as a handoff
mechanism. See Canonical's [autoinstall reference](https://canonical-subiquity.readthedocs-hosted.com/en/latest/reference/autoinstall-reference.html#shutdown).
FieldOS is not yet recommended for physical customer hardware. The current ISO
remains a local test candidate; see [`RELEASE.md`](RELEASE.md) for release gates
and current blockers.
The unattended identity and storage settings in `make test-e2e` are not part
of the customer ISO.

## Verifying the candidate

The retained ISO is an unpublished test candidate, not a customer release.
Before testing it, compare its SHA-256 with the candidate hash recorded in
[`RELEASE.md`](RELEASE.md):

```sh
sha256sum /mnt/shared/fieldos-releases/fieldos-customer-core4-21ad4fc.iso
```

The current candidate’s QEMU interactive install, installed-disk boot, desktop,
service checks, and two consecutive reboot checks passed in a disposable
no-NIC VM. At the end, Ubuntu prompted for media removal and Enter; the VM powered off, and a
subsequent power-on booted the installed disk without repair. Physical USB
handoff remains untested. For future changes, use
a disposable VM with a disposable virtual disk and no network adapter. Do not
write this candidate to physical media for customer use until all release
gates pass.
The E2E command below uses a separate unattended test image and does not
exercise the customer install workflow.

On an accepted installation, firstboot may take several minutes while it checks and
unpacks the local payload, installs packages from the included APT repository,
loads the container images, and starts the local models. Progress and failures
are recorded in `/var/log/fieldos-firstboot.log` and
`/var/lib/fieldos/provisioning-status.json`. Do not interrupt power during
firstboot. The **FieldOS Command Center** dock launcher opens N.O.M.A.D. at
`http://localhost:8080`; **FieldOS Start Here** explains which content is
bundled and which optional catalogs need a connected download. The **FieldOS
Content Sources and Limits** entry opens the offline source, license, and
safety notes. The wallpaper, icon, and dock shortcuts are local assets and do
not require a network connection.

## Development installation

For development, use the test only image and a disposable QEMU/KVM disk:

```sh
make test-e2e UBUNTU_ISO="/path/to/ubuntu-26.04.1-desktop-amd64.iso"
```

This test is headless, unattended, and has no virtual network device. Do not
point `virt-install` or any installer at a physical drive. Read
[`TESTING.md`](TESTING.md) for prerequisites, artifacts, and failure recovery.

## After installation

Services and their data start locally. Firstboot checks the selected bundled
model, performs a small chat generation and loads the embedding model. The
owner can review hardware and service diagnostics with:

```sh
sudo /opt/fieldos/scripts/fieldos-diagnostics.sh
```

The local web endpoints bind to loopback. Software updates and additional
content downloads are explicit owner actions and may require a separate
internet-connected session. The bundled assistant and embedding model run
locally; the included reference and map data are deliberately small test
fixtures, not a complete field library or navigation-grade regional map.
