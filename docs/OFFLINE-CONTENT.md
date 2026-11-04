# Offline content and redistribution

Every bundled artifact needs a stable version or digest, source URL, size,
checksum, and redistribution/license record. Do not bundle content with
unclear or non-redistributable terms. The build fails closed when a required
artifact is missing or its checksum differs.

The current customer candidate contains Project N.O.M.A.D.'s miniature English
Wikipedia ZIM, a low-zoom global Protomaps basemap (`world.pmtiles`) plus a
low-zoom continental United States sample region (`fieldos-sample-us.pmtiles`),
Ollama Qwen3 0.6B Q4_K_M for chat, `nomic-embed-text:v1.5` for embeddings, and
the `us-water-food-emergency` core pack. That small pack contains two unchanged
CDC PDFs about emergency water treatment and food safety after a power outage;
firstboot activates an attributed local source index. It is a starter set, not
a comprehensive disaster library.
The sample PMTiles region is extracted offline from the bundled world archive
by `build/prepare-payload.sh`; its bounding box and zoom levels are declared in
`payload/manifests/maps.json`, and the payload records its generated checksum
and size. The ZIM's Wikipedia content is CC BY-SA; map data is an ODbL Produced
Work derived from OpenStreetMap. Notices are included in the payload. Model
licensing is evaluated independently from the Ollama runtime. The full edition
may add openly licensed models, public-domain manuals, and user-selected
geographic packs; it must not include proprietary manuals or restricted
datasets.

The desktop's **FieldOS Start Here** guide states exactly what this test
payload contains and which features need a connected download. The Project
N.O.M.A.D. catalogs can offer archives, map regions, and software updates that
are not bundled here. Those downloads require a separate internet-connected
update session; the already installed AI models, ZIM archive, and map tiles do
not. A catalog being visible in N.O.M.A.D. does not mean its listed content is
included locally.

The exact Wikipedia fixture source revision, file size, checksum, and license
scope note are declared in `payload/manifests/references.json`. The installed
system exposes its source and limits guide from the Applications menu as
**FieldOS Content Sources and Limits** and stores the guide and license notices
under `/usr/share/doc/fieldos/`. The notice distinguishes archive-level
Wikimedia terms from item-specific media licenses; the latter still require
review before distribution.

Fresh installations use a FieldOS topo wallpaper and dark GNOME palette. The
GNOME dock includes **FieldOS Start Here** and **FieldOS Command Center** for
quick access. These are presentation defaults only and do not change system
networking, content catalogs, or application security boundaries.

AI responses are generated text, not authoritative references. The current
source revision uploads the CDC PDFs into N.O.M.A.D.'s native Knowledge Base
and requires a source-cited factual check in the next clean E2E run. Even with
retrieval enabled, open the source documents before relying on an answer. The
limited CDC water/food sources are not a first-aid or comprehensive emergency
library; FieldOS must not be used as a substitute for current medical or
emergency guidance.

The bundled world map and sample regional map both top out at zoom level 5.
They support broad orientation and acceptance testing, but do not provide
detailed roads, trails, parcels, or field navigation. A separate Middle
Tennessee map candidate exists outside the ISO: 19.6 MB, zoom 0–13, coverage
`-88.5,35.4,-85.7,36.7`, extracted from the 2026-11-02 Protomaps build. Its
manifest and ODbL license text are included in the portable archive. It passed guest import, N.O.M.A.D. registration, offline browser rendering at zoom 13, and two-reboot persistence in E2E source `43ec3f9faed73632c13a8113b546ade9b5bf488e` (report `/mnt/shared/fieldos-e2e/20261103T222621Z-2749281/report.md`). It remains an external test pack, not included in the ISO or approved for public redistribution. GPS/GIS integration is not
part of the current test release; the detector only reports whether a likely
GPS device node is present.

The extensible pack format and planned categories are documented in
[`CONTENT-PACKS.md`](CONTENT-PACKS.md). The `us-water-food-emergency` pack is
embedded in the current candidate. On source
`da61a843313c443c0e349a75b6395e48c0f73c20`, fresh no-NIC E2E and interactive
customer-mode tests confirmed its two CDC PDFs were indexed in N.O.M.A.D. and
retrievable with citations. The E2E and customer reports are at
`/mnt/shared/fieldos-e2e/20261104T060325Z-3127648/report.md` and
`/mnt/shared/fieldos-e2e/customer-da61a84/report.md`. This remains a narrow
starter pack, not a complete emergency library. The Middle Tennessee candidate
is separate and unreleased; agricultural, wildlife, first-aid, and comprehensive
reference packs still need requirements and licensing review.

Model candidates are tracked in `models/manifest.json`. Content and package
inputs are tracked in `payload/manifests/`; license texts and attributions live
under `payload/licenses/`. An artifact is not approved merely because its
download endpoint is public.
