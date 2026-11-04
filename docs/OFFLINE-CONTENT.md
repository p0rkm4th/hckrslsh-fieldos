# Offline content and redistribution

Every bundled artifact needs a stable version or digest, source URL, size,
checksum, and redistribution/license record. Do not bundle content with
unclear or non-redistributable terms. The build fails closed when a required
artifact is missing or its checksum differs.

The previous customer candidate contains Project N.O.M.A.D.'s miniature English
Wikipedia ZIM, a low-zoom global Protomaps basemap (`world.pmtiles`) plus a
low-zoom continental United States sample region (`fieldos-sample-us.pmtiles`),
Ollama Qwen3 0.6B Q4_K_M for chat, `nomic-embed-text:v1.5` for embeddings, and
the `us-water-food-emergency` and `us-tornado-safety` core packs. The current
source catalog also makes `us-weather-safety` and `us-flood-safety` core packs;
the new offline payload and unattended test verified that they install and
index. A customer-mode ISO with those packs has not yet completed its separate
interactive test. The water/food pack contains two unchanged CDC PDFs about
emergency water treatment and food safety after a power outage. Firstboot
indexes the CDC documents and NWS-based summaries in N.O.M.A.D.'s local source
library. This is a starter set, not a comprehensive disaster library.
The retained customer candidate also contains the pinned Middle Tennessee map
described below. Fresh no-NIC E2E and interactive customer installation checks
confirmed it is available offline and visibly renders in Firefox. The sample
PMTiles region is extracted offline from the bundled world archive
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
core payload includes two CDC water/food PDFs and FieldOS-edited NWS summaries
on tornado, flood, hurricane, and winter-storm preparedness, indexed in
N.O.M.A.D.'s native Knowledge Base. NOAA's [reuse
guidance](https://www.noaa.gov/office-education/outreach-communication/faq)
says nearly all NOAA content is public domain unless otherwise noted, and
requires attribution and no implied endorsement. Pack manifests record the
source review and each summary's limits. These selected topics are not a
first-aid or comprehensive emergency library; the packs provide no live
warnings. Open the original documents and follow current local instructions.
FieldOS must not be used as a substitute for medical or emergency guidance.
Current scenario testing found that N.O.M.A.D. can attach unrelated sources
and generate unsafe, unsupported advice: it claimed boiling removes chemical
contaminants even though the CDC PDF explicitly says it does not, and it gave
wildfire evacuation instructions attributed to the unrelated tornado guide.
Until retrieval is made reliably source-bounded and retested, open the source
documents directly and do not use AI answers for disaster decisions.

The bundled world and U.S. overview maps top out at zoom 5. The payload also
contains a 19.6 MB Middle Tennessee road and land-use map, zoom 0–13, coverage
`-88.5,35.4,-85.7,36.7`, extracted from the 2026-11-02 Protomaps build. Its
source build, checksum, bounds, attribution, and ODbL Produced Work status are
recorded in `payload/manifests/maps.json` and generated `map-payload.json`. The
earlier separate-pack import test rendered it in Firefox at zoom 13 and
survived two reboots. The current customer candidate integrates it directly
into the core map payload; a fresh customer install rendered it at zoom 13 and
the map persisted through two reboots. It is a geographic
reference, not turn-by-turn navigation, GPS positioning, trails, or emergency
advice. GPS/GIS integration is not
part of the current test release; the detector only reports whether a likely
GPS device node is present.

The extensible pack format and planned categories are documented in
[`CONTENT-PACKS.md`](CONTENT-PACKS.md). An earlier candidate on source
`1fb6806` installed and indexed both CDC PDFs and the NWS tornado text in
N.O.M.A.D.; the historical E2E and customer-mode
evidence is in `/mnt/shared/fieldos-e2e/20261104T080251Z-3272638/report.md`
and `/mnt/shared/fieldos-e2e/customer-nws-1fb6806/`. The previous customer candidate at source `85a33f8` also installed the CDC and tornado references;
its fresh interactive results are recorded in [`RELEASE.md`](RELEASE.md). This remains a narrow
starter set, not a complete emergency library. The Middle Tennessee map is
included in the current customer candidate; agricultural, wildlife,
first-aid, and comprehensive reference packs still need requirements and
licensing review.

Model candidates are tracked in `models/manifest.json`. Content and package
inputs are tracked in `payload/manifests/`; license texts and attributions live
under `payload/licenses/`. An artifact is not approved merely because its
download endpoint is public.

The weather and flood summaries are small enough for the core offline baseline
and remain independently versioned, checksummed packs. `make content-packs`
also creates removable-media archives for them. The documents have no live
forecasts or alerts and are not comprehensive emergency guides. Each identifies
itself as an edited FieldOS summary and links its NWS sources. NOAA's reuse
policy requires attribution and forbids implying endorsement; full project
redistribution review remains open.

### FEMA CERT manual review (not bundled)

The 2011 FEMA CERT Basic Training Participant Manual was reviewed as a
possible optional preparedness reference (332 pages; source:
[FEMA PDF](https://www.fema.gov/sites/default/files/2020-07/fema-cert_basic-training-participant-manual_01-01-2011.pdf)).
No explicit reuse or redistribution statement was found in the manual. FEMA's
[NDEMU FAQ](https://training.fema.gov/programs/independent-study/isfaq.aspx?lang=en)
describes public-domain status for NDEMU materials unless otherwise indicated;
that guidance does not resolve rights for this contractor-credited CERT manual
or any third-party material it may contain. FEMA's [development resources]
(https://training.fema.gov/devres/) require permission or approval for
third-party material in instructional products. Therefore the manual is not
included in FieldOS or its packs unless rights are confirmed. It is also dated
training material, not current medical procedure; any future use must label it
as historical training reference and direct users to current authoritative
guidance.
