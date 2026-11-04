# Installation

## Customer installation

**Current candidate status (2026-11-04):**
`/mnt/shared/fieldos-releases/fieldos-customer-test-corepack-f9c10ec.iso`, source
`f9c10ec170c2b33000a287a0ee8ef38d6e2b0f50`, SHA-256
`95503d257465087b723ba1eb0725dbf63ac6cf2ac83383f4e35cd63af7738c8d`. Structure
and offline payload checks passed. A fresh no-NIC UEFI QEMU install completed
with interactive account and disk selection, and the installed EFI disk booted
to the branded desktop. Firstboot, all seven services, local inference,
embeddings, Kiwix, the bundled CDC source index, and overview maps were checked;
key services and local content persisted across two reboots. During this
candidate's Restart handoff, Ubuntu reached the media-removal prompt, but after
ISO ejection and Enter the VM powered off; a host-side `virsh start` was needed
to continue to the installed disk. Treat handoff as PARTIAL until that transition
is resolved and retested. Full evidence is at
`/mnt/shared/fieldos-e2e/customer-interactive-corepack-f9c10ec/20261104T040000Z/report.md`.

The prior `0085b7a` ISO was retired after this candidate passed the handoff
retest. Its checksum and retirement record remain beside the current candidate;
historical test evidence is retained under `/mnt/shared/fieldos-e2e`.

This is an engineering candidate, not a customer-ready field appliance. The
bundled Kiwix archive contains 100 articles, maps stop at zoom 5, and the local
AI returned generic, uncited, misleading text for a food-safety scenario.
Physical hardware, public redistribution, and LAN isolation remain unverified.
Do not rely on the assistant for emergency or medical advice. See
[`RELEASE.md`](RELEASE.md) for the current release gates.

The customer facing ISO is built with:

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
“Restart now.” For USB installation, remove the USB media when prompted so
firmware can boot the installed disk. In the current QEMU test, the installer
reached the explicit media-removal prompt; after ejection and Enter the VM
powered off, and a host start was required before the installed disk booted.
The installed disk itself boots, but the handoff is not yet verified as a
seamless customer flow. Physical USB behavior is still untested. Review the remaining release gates in
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
sha256sum /mnt/shared/fieldos-releases/fieldos-customer-test-corepack-f9c10ec.iso
```

The QEMU interactive install and installed-disk boot passed in a disposable
no-NIC VM. Installer media handoff is partial and needs a fresh retest after a
fix. For future changes, use a disposable VM
with a disposable virtual disk and no network adapter. Do not write this
candidate to physical media for customer use until all release gates pass.
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
