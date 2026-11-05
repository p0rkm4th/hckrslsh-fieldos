# Installation

## Customer installation

**Current customer-mode candidate (2026-11-05; VM installation PASS):**
`/mnt/shared/fieldos-releases/fieldos-customer-cc4aa38.iso`, source
`cc4aa38f3debd078b877589355221e94821bd160`, SHA-256
`0319a069a4874d0522f660c6d69027e6ab9c4aaf86f2f8c995efb9d359a1e139`.
Interactive disk/account selection and installation completed in a fresh
no-NIC 80 GiB UEFI VM. At Ubuntu's “Please remove the installation medium,
then press ENTER” prompt, the guest's virtual CD tray was already open. Enter
caused a clean guest shutdown; an ordinary VM power-on then booted the installed
disk with no ISO attached. No reset or repair was used. Offline firstboot,
application checks, map rendering, and two post-install reboots passed. Fully
automatic restart without the ordinary power-on after the prompt, physical USB
handoff, and physical hardware remain unverified. Full current evidence:
[`VALIDATION-CURRENT.md`](VALIDATION-CURRENT.md) and
`/mnt/shared/fieldos-e2e/customer-cc4aa38-handoff-20261105/`.

**Previous customer-mode installation PASS (2026-11-05; historical):**
`/mnt/shared/fieldos-releases/fieldos-customer-searchable-562fee9.iso`, source
`562fee9`, SHA-256
`4d9ccf3f3e7d9b30bc0b0bf645303bb97e683a7eb79a9ffcd570edcbb2111ccfe`.
Interactive account and target-disk selection, destructive-action confirmation,
normal virtual-media handoff, installed-disk boot, and offline firstboot passed
in a fresh no-NIC 80 GiB UEFI VM. The branded desktop, local AI, embeddings,
Kiwix, and statewide map worked; two consecutive reboots preserved services
and user data. This is evidence for a previous ISO, not the current candidate.
Evidence and screenshots:
`/mnt/shared/fieldos-e2e/customer-searchable-562fee9/validation.md`.

**Earlier customer-mode VM pass (2026-11-05; superseded):**
`/mnt/shared/fieldos-releases/fieldos-customer-offline-9c59a5f.iso`, source
`9c59a5f63cf6a2b35b7489a45cf53c0fc93d2f19`, SHA-256
`4e9800fc6facf698d2408579b42375e9d6fc31fbd38896ff2e68ada6d2654c74`.
Interactive account and target-disk selection completed in a disposable no-NIC
UEFI VM; firstboot finished and the installed disk booted to the branded
desktop. All six core packs indexed, local chat and embeddings worked, Kiwix
returned a local result, Firefox rendered Nashville at zoom 13, and services
persisted across two reboots. An initial handoff attempt ejected the ISO before
Ubuntu reached its removal prompt and was not a valid handoff test. A repeat
test reached Ubuntu's standard “Please remove the
installation medium, then press ENTER” prompt. After the virtual ISO was
removed and Enter was pressed, the VM powered off; powering it on once booted
the installed disk to GDM without repair. Do not eject the installer before
this prompt. Physical USB behavior remains unverified. Detailed reports and
screenshots are in `/mnt/shared/fieldos-e2e/customer-offline-9c59a5f-20261105/`
and `/mnt/shared/fieldos-e2e/customer-handoff-9c59a5f-20261105/`.

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
sha256sum /mnt/shared/fieldos-releases/fieldos-customer-cc4aa38.iso
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
