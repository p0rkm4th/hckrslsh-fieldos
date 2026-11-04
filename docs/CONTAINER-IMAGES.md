# Pinned container images

The release payload uses the exact `linux/amd64` image references and digests
in [`payload/manifests/images.json`](../payload/manifests/images.json). The
manifest is the machine-readable source of image identity. A digest pins bytes;
it does not clear every component in those bytes for redistribution.

| Service | Pinned image | Direct project license reference |
|---|---|---|
| Project N.O.M.A.D. | `ghcr.io/crosstalk-solutions/project-nomad:v1.35.1` | [Upstream v1.35.1 source](https://github.com/Crosstalk-Solutions/project-nomad/tree/v1.35.1), Apache-2.0 |
| MySQL | `mysql:8.0` | [MySQL Server license](https://github.com/mysql/mysql-server/blob/8.0/LICENSE), GPL-2.0 with additional permissions |
| Redis | `redis:7-alpine`, digest in manifest | [Redis licensing overview](https://redis.io/legal/licenses/): Redis 7.4.x is RSALv2 or SSPLv1; see also the [licensing change announcement](https://redis.io/blog/redis-adopts-dual-source-available-licensing/) |
| Dozzle | `amir20/dozzle:v10.0` | [Upstream source](https://github.com/amir20/dozzle), MIT |
| Ollama | `ollama/ollama:0.33.3` | [Upstream source](https://github.com/ollama/ollama), MIT |
| Qdrant | `qdrant/qdrant:v1.16` | [Upstream source](https://github.com/qdrant/qdrant), Apache-2.0 |
| Kiwix | `ghcr.io/kiwix/kiwix-serve:3.8.1` | [Upstream source](https://github.com/kiwix/kiwix-tools), GPL-3.0-or-later |

## Redis version and license correction

The locally cached image has image ID
`sha256:8da19c7399dca900c6822a1cf30f9d2285585e2c4b457ff4095b0f4500054d3f`,
which matches the pinned digest, and its image configuration reports
`REDIS_VERSION=7.4.12`. The Redis project's current [licensing overview](https://redis.io/legal/licenses/)
states that version 7.4.x uses RSALv2 or SSPLv1 rather than BSD-3-Clause. It
summarizes RSALv2 restrictions on commercializing Redis software and offering
Redis functionality as a managed service; SSPLv1 includes source obligations
for service providers. The machine-readable image manifest and redistribution
review record the corrected license family and leave customer distribution
clearance open. The local read-only image inspection is retained at
`/mnt/shared/fieldos-e2e/redis-license-image-inspect-20261103.txt`.

RSALv2/SSPLv1 is a material release consideration for a FieldOS customer
appliance. Do not treat this image as cleared for commercial distribution.
Obtain a review for the planned product and distribution model, or choose a
compatible alternative and rebuild and retest the offline payload. The customer-mode ISO is an older private test artifact. The payload was
rebuilt from current manifests and exercised by the clean-source E2E at
`d865333`; this confirms installation behavior, not license clearance.

Valkey is a possible replacement to evaluate. The [Valkey upstream project](https://github.com/valkey-io/valkey)
is BSD-3-Clause, and its [migration guide](https://valkey.io/topics/migration/)
describes Valkey 7.2+ as protocol, configuration, and persistence compatible
with Redis OSS 7.2. This is a useful
licensing and compatibility candidate, not a FieldOS validation result: the
pinned Project N.O.M.A.D. image has not been acceptance-tested against Valkey,
and the complete Valkey container image still needs its own layer and notice
review. No service image has been changed. A fresh payload rebuild and install
acceptance passed at `d865333`; the licensing and compatibility review remains
open.

## Scope of the direct-license table

These references identify upstream projects and direct license information;
they are not a complete SBOM or redistribution clearance. Container layers
include transitive software with separate notices and, in some cases,
corresponding-source obligations. The exact-image SBOM, notice inventory, and
remaining review actions are tracked in
[`REDISTRIBUTION.md`](REDISTRIBUTION.md). Review every image digest again when
the pinned payload changes.
