# Pinned container images

The release payload uses the exact `linux/amd64` image references and digests
in [`payload/manifests/images.json`](../payload/manifests/images.json). The
manifest is the machine-readable source of image identity. A digest pins bytes;
it does not clear every component in those bytes for redistribution.

| Service | Pinned image | Direct project license reference |
|---|---|---|
| Project N.O.M.A.D. | `ghcr.io/crosstalk-solutions/project-nomad:v1.35.1` | [Upstream v1.35.1 source](https://github.com/Crosstalk-Solutions/project-nomad/tree/v1.35.1), Apache-2.0 |
| MySQL | `mysql:8.0` | [MySQL Server license](https://github.com/mysql/mysql-server/blob/8.0/LICENSE), GPL-2.0 with additional permissions |
| Redis | `redis:7-alpine`, digest in manifest | [Redis licensing change](https://redis.io/blog/redis-adopts-dual-source-available-licensing/): version 7.4.x is RSALv2 or SSPLv1 |
| Dozzle | `amir20/dozzle:v10.0` | [Upstream source](https://github.com/amir20/dozzle), MIT |
| Ollama | `ollama/ollama:0.33.3` | [Upstream source](https://github.com/ollama/ollama), MIT |
| Qdrant | `qdrant/qdrant:v1.16` | [Upstream source](https://github.com/qdrant/qdrant), Apache-2.0 |
| Kiwix | `ghcr.io/kiwix/kiwix-serve:3.8.1` | [Upstream source](https://github.com/kiwix/kiwix-tools), GPL-3.0-or-later |

## Redis version and license correction

The locally cached image has image ID
`sha256:8da19c7399dca900c6822a1cf30f9d2285585e2c4b457ff4095b0f4500054d3f`,
which matches the pinned digest, and its image configuration reports
`REDIS_VERSION=7.4.12`. The Redis project states that its 7.4 releases use
RSALv2 or SSPLv1 rather than BSD-3-Clause. The machine-readable image manifest
and redistribution review record this corrected license family. The local
read-only image inspection is retained at
`/mnt/shared/fieldos-e2e/redis-license-image-inspect-20261103.txt`.

RSALv2/SSPLv1 is a material release consideration for a FieldOS customer
appliance. Do not treat this image as cleared for commercial distribution.
Obtain a review for the planned product and distribution model, or choose a
compatible alternative and rebuild and retest the offline payload. The
candidate ISO and payload predate this manifest correction and remain private
test artifacts.

## Scope of the direct-license table

These references identify upstream projects and direct license information;
they are not a complete SBOM or redistribution clearance. Container layers
include transitive software with separate notices and, in some cases,
corresponding-source obligations. The exact-image SBOM, notice inventory, and
remaining review actions are tracked in
[`REDISTRIBUTION.md`](REDISTRIBUTION.md). Review every image digest again when
the pinned payload changes.
