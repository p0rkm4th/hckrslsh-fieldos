# Installation

## Customer installation

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
“Restart now.” Keep the USB installation media connected until Ubuntu prompts
you to remove it; then remove it and press ENTER. An earlier R3 test booted the
installed target after media was ejected at that prompt. Later R4/R5 tests
reached the prompt with the virtual tray already empty and powered off after
ENTER. Eject timing is a hypothesis, not a confirmed cause; the handoff remains
unverified on the current candidate. If the computer powers off, press its
power button once to start the installed system. Ubuntu documents
`shutdown: reboot` as the default autoinstall action in its
[autoinstall reference](https://canonical-subiquity.readthedocs-hosted.com/en/latest/reference/autoinstall-reference.html#shutdown).
FieldOS is not yet recommended for customer hardware.
The unattended identity and storage settings in `make test-e2e` are not part
of the customer ISO.

After installation, firstboot may take several minutes while it checks and
unpacks the local payload, installs packages from the included APT repository,
loads the container images, and starts the local models. Progress and failures
are recorded in `/var/log/fieldos-firstboot.log` and
`/var/lib/fieldos/provisioning-status.json`. Do not interrupt power during
firstboot. The desktop launcher opens N.O.M.A.D. at `http://localhost:8080`.
The **FieldOS Content Sources and Limits** application entry opens the offline
source, license, and safety notes.

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
internet connected session; the bundled assistant, reference library, and
world basemap are intended to work without one.
