# Installation

## Customer installation

**Current candidate status (2026-11-03):**
`/mnt/shared/fieldos-releases/fieldos-customer-handoff-c744e52.iso`, built from
`c744e5275ec2f5002244c92cef5101b603e53195`, SHA-256
`c8b09f678351b87a2d3784c4bd91949b6add9a7bb6ad5a9a8a5401a059f762f7`. A fresh
no-NIC interactive UEFI QEMU install accepted an identity and disposable target
disk and installed Ubuntu. After “Restart now,” the guest powered off at the
media-removal prompt after Enter; a host start was required to boot the disk.
The installed system then passed offline provisioning and service checks,
including two guest reboots. A prepper-oriented UI review found that the bundled
reference and map content are inadequate for emergencies and that the AI can
present unsourced generic advice as verified. This remains an engineering test
candidate, not a customer-ready appliance. Physical hardware is untested. See
[`RELEASE.md`](RELEASE.md) and the detailed report at
`/mnt/shared/fieldos-e2e/customer-interactive-c744e52-20261103/report.md`.

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
firmware can boot the installed disk. This workflow passed in the disposable VM
with the media-handoff caveat above. Review the release gates in
[`RELEASE.md`](RELEASE.md) before installing on physical customer hardware.
FieldOS leaves the customer identity and storage sections interactive. Ubuntu
documents that an autoinstall `shutdown` action is ignored when interactive
sections are configured, so FieldOS does not set one or treat it as a handoff
mechanism. The prior QEMU run powered off after the media-removal prompt; the
cause and behavior of the customer installer handoff remain under investigation.
See Canonical's [autoinstall reference](https://canonical-subiquity.readthedocs-hosted.com/en/latest/reference/autoinstall-reference.html#shutdown).
FieldOS is not yet recommended for physical customer hardware. The current ISO
remains a local test candidate; see
[`RELEASE.md`](RELEASE.md) for release gates and current blockers.
The unattended identity and storage settings in `make test-e2e` are not part
of the customer ISO.

## Verifying the candidate

The retained ISO is an unpublished test candidate, not a customer release.
Before testing it, compare its SHA-256 with the candidate hash recorded in
[`RELEASE.md`](RELEASE.md):

```sh
sha256sum /mnt/shared/fieldos-releases/fieldos-customer-handoff-c744e52.iso
```

Use a disposable VM with a disposable virtual disk and no network adapter to
investigate the customer-mode handoff failure. Do not write this candidate to a
physical disk or install it on customer hardware until the release gates pass.
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
