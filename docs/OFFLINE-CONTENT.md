# Offline content and redistribution

Every bundled artifact needs a stable version or digest, source URL, size,
checksum, and redistribution/license record. Do not bundle content with
unclear or non-redistributable terms. The build fails closed when a required
artifact is missing or its checksum differs.

The current test payload contains Project N.O.M.A.D.'s miniature English
Wikipedia ZIM, a low-zoom global Protomaps basemap (`world.pmtiles`) plus a
low-zoom continental United States sample region (`fieldos-sample-us.pmtiles`),
Ollama Qwen3 0.6B Q4_K_M for chat, and `nomic-embed-text:v1.5` for embeddings.
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

AI responses are generated text, not authoritative references. Open the source
articles before relying on an answer. The test edition has no reviewed
first-aid or emergency pack and must not be used as medical or emergency
guidance.

The current world map and sample regional map both top out at zoom level 5.
They support broad orientation and acceptance testing, but do not provide
detailed roads, trails, parcels, or field navigation. A higher resolution
regional pack requires separate source and redistribution review, coverage
and size metadata, and a real-device render test. GPS/GIS integration is not
part of the current test release; the detector only reports whether a likely
GPS device node is present.

The extensible pack format and planned categories are documented in
[`CONTENT-PACKS.md`](CONTENT-PACKS.md). No customer content packs have been
selected or approved for redistribution.

Model candidates are tracked in `models/manifest.json`. Content and package
inputs are tracked in `payload/manifests/`; license texts and attributions live
under `payload/licenses/`. An artifact is not approved merely because its
download endpoint is public.
