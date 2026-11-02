# Hckrslsh FieldOS

Hckrslsh FieldOS is an offline-first field computer prototype built around
[Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad).
The target is an x86-64 laptop installed from a self-contained Ubuntu 26.04
LTS image, with N.O.M.A.D., local AI, reference material, and map samples
available without an internet connection.

The first milestone is a reproducible **test ISO** for disposable QEMU/KVM
installation and offline acceptance. Full content packs are separate because
worldwide maps and large language models do not fit a sensible universal ISO.
No production production infrastructure node or physical disk is a build target.

## Status

Prototype in active development. Ubuntu 26.04.1 Desktop and Project N.O.M.A.D.
v1.35.1 are pinned. The 11.1 GiB test ISO at
`build/out/fieldos-test.iso` boots to the Ubuntu installer under UEFI; BIOS and
UEFI records and payload presence pass `make verify`. The offline payload is
5.11 GiB. A disposable QEMU guest detects its 80 GiB disk, but the install has
not completed, so no installed-service or offline-operation result is claimed.
See [current verification status](docs/RELEASE.md).

## Development

Requirements: Python 3.11+, Bash, Git, xorriso, squashfs-tools, QEMU/KVM, and
Docker Engine with Compose v2. Model weights, container images, and ISO files
are build artifacts and are excluded from Git.

```sh
make check
make test
make iso-test UBUNTU_ISO=/path/to/ubuntu-26.04.1-desktop-amd64.iso
make verify ISO=build/out/fieldos-test.iso
```

See [architecture](docs/ARCHITECTURE.md), [installation](docs/INSTALLATION.md),
[hardware profiles](docs/HARDWARE.md), [offline content](docs/OFFLINE-CONTENT.md),
and [release process](docs/RELEASE.md).

## Safety

Installer testing uses disposable virtual disks. No build or test command may
select or erase a physical disk automatically. The ISO must ask the installer
user to choose a target disk and confirm erasure. No credentials are embedded.
Runtime services bind to localhost by default; opening them to a LAN is an
explicit owner action.

## License

Project-specific source is Apache-2.0. Third-party software, models, maps, and
reference data retain their own licenses; see `payload/licenses/` and the
attribution manifest before redistributing an artifact.
