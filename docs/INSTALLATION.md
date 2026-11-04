# Installation

## Customer installation

**Current candidate status (2026-11-04):**
`/mnt/shared/fieldos-releases/fieldos-customer-test-0085b7a.iso`, source
`0085b7ac2989dc684776ae0910fe5c77dd829c0c`, SHA-256
`4d1b7ed6ed6c8089fbb0cdb416743fed2f917f9ae899d6bf6aa45de92915ba22`. Structure
and offline payload checks passed. A fresh no-NIC UEFI QEMU install completed
with interactive account and disk selection. Removing the installer media at
the restart prompt led directly to the installed OS without a host reset.
Firstboot started seven containers, the branded desktop and local N.O.M.A.D.
opened, and the guest returned to the desktop after two restarts. See the
customer report at
`/mnt/shared/fieldos-e2e/customer-interactive-0085b7a-20261104/report.md`.

This is an engineering candidate, not a customer-ready field appliance. The
bundled Kiwix archive contains only 100 articles and returned no result for
“water purification”; the U.S. map lacks useful Nashville street detail at a
10 km scale; and the local AI's water-storage response was generic and
unsourced. Physical hardware, public redistribution, and LAN isolation remain
unverified. Do not rely on the assistant for emergency or medical advice. The
ISO has not been validated on a physical machine. See [`RELEASE.md`](RELEASE.md)
for the current release gates.

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
“Restart now.” For USB installation, remove the USB media when prompted so firmware can boot
the installed disk. This media handoff was demonstrated in the latest disposable
UEFI QEMU run after ejecting the virtual media at the prompt. Physical USB
behavior remains untested. Review the remaining release gates in
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
sha256sum /mnt/shared/fieldos-releases/fieldos-customer-test-0085b7a.iso
```

The current QEMU handoff test passed. For future changes, use a disposable VM
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
