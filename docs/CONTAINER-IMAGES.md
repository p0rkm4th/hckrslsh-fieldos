# Pinned container images

The release payload uses the exact `linux/amd64` image references and digests
in [`payload/manifests/images.json`](../payload/manifests/images.json). The
manifest is the machine-readable source of image identity. A digest pins bytes;
it does not clear every component in those bytes for redistribution.

| Service | Pinned image | Direct project license reference |
|---|---|---|
| Project N.O.M.A.D. | `ghcr.io/crosstalk-solutions/project-nomad:v1.35.1` | [Upstream v1.35.1 source](https://github.com/Crosstalk-Solutions/project-nomad/tree/v1.35.1), Apache-2.0 |
| MySQL | `mysql:8.0` | [MySQL Server license](https://github.com/mysql/mysql-server/blob/8.0/LICENSE), GPL-2.0 with additional permissions |
| Cache/queue service | `valkey/valkey:8.0-alpine`, digest in manifest | [Valkey upstream](https://github.com/valkey-io/valkey), BSD-3-Clause |
| Dozzle | `amir20/dozzle:v10.0` | [Upstream source](https://github.com/amir20/dozzle), MIT |
| Ollama | `ollama/ollama:0.33.3` | [Upstream source](https://github.com/ollama/ollama), MIT |
| Qdrant | `qdrant/qdrant:v1.16` | [Upstream source](https://github.com/qdrant/qdrant), Apache-2.0 |
| Kiwix | `ghcr.io/kiwix/kiwix-serve:3.8.1` | [Upstream source](https://github.com/kiwix/kiwix-tools), GPL-3.0-or-later |

## Valkey compatibility candidate

The current source pins `valkey/valkey:8.0-alpine` at digest
`sha256:19f0b3d350f5e6de618086d79ecdc9c474ab159bebb16ed95a92e4211562fee5`;
the image configuration reports Valkey `8.0.12` and `linux/amd64`. The
upstream Valkey project is BSD-3-Clause. Its [migration guide](https://valkey.io/topics/migration/)
states that Redis clients can use the RESP protocol with Valkey, while also
warning that Redis Community Edition 7.4+ data files are not compatible with
Valkey.

An isolated Docker Compose compatibility smoke test used the exact pinned
N.O.M.A.D., MySQL, Qdrant, and Valkey images on an internal-only network. The
N.O.M.A.D. image completed database migrations, started background workers,
and returned HTTP 200 from `/api/health`. Its bundled `ioredis` client
successfully performed PING/SET/GET against Valkey. Valkey retained a test key
through a restart on its persistent bind mount. The test had no published
ports and no Docker socket mount; temporary database and app data were isolated
under `/tmp`. It did not exercise a rebuilt FieldOS payload, actual interactive
AI workflows, full no-NIC installation, or old-Redis data migration.

The accepted `f250cc1` ISO still contains Redis 7.4.12 under RSALv2 or SSPLv1;
this source change is a Valkey candidate only until a new payload/ISO and full
offline acceptance pass. The previous `/var/lib/fieldos/redis` data directory
is retained, and the candidate uses a new `/var/lib/fieldos/valkey` directory
because 7.4 data files cannot be assumed compatible. Existing queue/session
state migration and upgrade behavior need review before recommending an
in-place upgrade. Container-layer notices and licenses also require their own
review; BSD-3-Clause for Valkey itself is not clearance of every image layer.

## Scope of the direct-license table

These references identify upstream projects and direct license information;
they are not a complete SBOM or redistribution clearance. Container layers
include transitive software with separate notices and, in some cases,
corresponding-source obligations. The exact-image SBOM, notice inventory, and
remaining review actions are tracked in
[`REDISTRIBUTION.md`](REDISTRIBUTION.md). Review every image digest again when
the pinned payload changes.
