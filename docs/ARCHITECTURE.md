# Architecture

## Base and upstream components

- x86-64 Ubuntu 26.04.1 LTS Desktop from the checksum pinned official ISO.
- Project N.O.M.A.D. v1.35.1 from the upstream Apache-2.0 project.
- Docker Compose services for MySQL, Redis, Ollama, Qdrant, Kiwix, and Dozzle.
- A bundled Ollama chat model and separate embedding model.
- A small Kiwix ZIM and N.O.M.A.D. compatible `world.pmtiles` basemap.

N.O.M.A.D. remains the main application. FieldOS seeds its runtime data paths
and loads pinned container images from the local payload before starting the
Compose project. It does not add a separate assistant interface.

## Installer and first boot

The customer ISO keeps Ubuntu's interactive account and storage setup, target
disk choice, and supported full disk encryption option. The unattended
identity and disk layout exist only in the generated acceptance ISO.

The installed system runs `fieldos-firstboot.service`. It checks the payload
checksum, extracts the local APT package index and dependencies, installs
packages without accessing remote repositories, loads OCI images, seeds
persistent content and runtime directories, initializes the Kiwix library,
creates per installation service secrets, and starts the services without
pulling images. The provisioning marker and diagnostics are stored under
`/var/lib/fieldos/`; logs are in `/var/log/fieldos-firstboot.log`.

Repeated provisioning does not replace existing database, Redis, Qdrant,
model, or valid Kiwix library data. Invalid Kiwix XML is retained with an
`.invalid.<timestamp>` suffix before a new library is made.

## Local network boundaries

The containers share an internal Docker bridge. Services exposing local web
or API ports also attach to a host accessible bridge with masquerading disabled.
This addresses the current Docker 29 behavior for port publishing from an
internal only bridge while allowing the owner to use loopback endpoints.
Firstboot and acceptance tests use a VM with no virtual network adapter.

The management UI and service ports bind to `127.0.0.1`. Opening them to a LAN
is an explicit operator configuration change. The initial offline payload
does not require remote registries, package repositories, or online content
services at run time.

## Hardware selection

`hardware/detect/detect.py` reports CPU instruction features, RAM, GPU facts,
storage, battery, and GPS visibility as JSON. `hardware/select_profile.py`
compares that data with `models/manifest.json` and the model IDs present in the
offline payload. It reserves RAM, prefers a validated compatible backend, and
falls back to CPU. The current firstboot path validates CPU inference only;
GPU backends and their usable VRAM must not be described as tested until a
physical hardware run validates model loading and generation on them.

## Payload and release boundary

The test edition contains one small content/model tier. The expanded edition
is a later release step and may use a separate content partition when its
payload is too large for practical USB media. ISO images, VM disks, downloaded
packages, model weights, container archives, and build caches stay outside Git.

`make test-e2e` is the operational acceptance gate. A successful build or
container start alone does not establish that the application, inference,
reference content, maps, or reboot persistence work. See
[`TESTING.md`](TESTING.md) and [`RELEASE.md`](RELEASE.md) for measured results.
