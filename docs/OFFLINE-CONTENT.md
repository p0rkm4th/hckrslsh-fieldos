# Offline content and redistribution

Every bundled artifact needs a stable version or digest, source URL, size,
checksum, and redistribution/license record. Do not bundle content with
unclear or non-redistributable terms. The build fails closed when a required
artifact is missing or its checksum differs.

## Current installation status (2026-11-06)

The current private customer-mode test ISO is source `129da89` at
`/mnt/shared/fieldos-releases/fieldos-customer-test-valkey-129da89.iso`
(SHA-256 `ddd9015cbc56dad3635f5453f8d0f6b5ff6a834610394cf3d2fab38dd2d796e2`).
Interactive no-NIC install, firstboot, map interaction, local apps, and two
reboots passed in a disposable UEFI VM. Separate same-source E2E visibly
rendered eight Tennessee locations. Full evidence is in
[`VALIDATION-CURRENT.md`](VALIDATION-CURRENT.md). Physical USB/hardware and
redistribution are unverified; this is not a cleared release.

The current candidate embeds payload SHA-256
`a257d4e4113254411b56e072fe301d35cb90dc4e6dceb2e002fdfb0f6d720614` (6.6 GiB),
recorded in its build manifest.
It provides the world overview, zoom 0–5, and statewide Tennessee vector map,
zoom 0–13, plus the small Kiwix `Wikipedia 100` fixture and ten indexed source
documents. The map opens a Tennessee overview by default; zoom-13 vector tiles are available
across the statewide extract. This is a geographic reference,
not turn-by-turn routing or GPS positioning.

Follow-up browser testing clarified the earlier apparent access failures.
Opening the bundled `Wikipedia 100` ZIM and searching within the book for
“United States” returned 59 results; the article “List of states and
territories of the United States” opened offline. The supported Start Here
link opened the Source Library in Firefox, where “flood” returned three
documents with source attribution. An earlier direct address-bar attempt still
showed `NS_ERROR_OFFLINE`, so use the documented Start Here workflow. This
validates access to the included small corpus; it does not make the mini ZIM or
19 displayed source entries a complete preparedness, medical, agricultural,
or survival library. Redistribution clearance and per-item review remain
incomplete; do not publish this ISO.

## New core reference in test ISO `d04f450`

The clean-source unattended E2E from commit `d04f450` includes CDC's
text-only private-well emergency reference as a ninth core pack. Firstboot
completed, and the Source Library HTML and Firefox screenshot show its title,
coverage notes, CDC attribution, warnings, and local document link. The exact
offline document URL returned bytes matching the manifest SHA-256
`d8a05f9568a60c1e568869018e0ec769cae3a0bf13260765cc8f6edbee8e09a6` after two
reboots. The pack was not indexed into AI embeddings (`index_with_ai: false`);
users can search and read the original text in Source Library. Evidence is in
`/mnt/shared/fieldos-e2e/20261106T072733Z-566287/`. This reference is not in the
interactive customer ISO `5abae15`, which still requires a current-source
customer-mode rebuild and separate interactive install test.

## Statewide Tennessee map candidate, verified 2026-11-05

The current payload replaces the former 19.6 MB Middle
Tennessee extract with `tennessee-20261102-z13.pmtiles`, a 145,267,908-byte
Protomaps vector-tile extract covering `-90.9,34.5,-81.0,37.25`, zoom 0–13.
It covers Tennessee with a buffer into neighboring states and preserves the
zoom 0–5 world and U.S. overview maps. The source is Protomaps build
`20261102.pmtiles`, version 4.15.2; the extracted file SHA-256 is
`0d123132839b77e627c4f4f103bf7a78925099c57319e759757be3207cb89525`.
Source metadata, bounds, expected size, and checksum are pinned in
`payload/manifests/maps.json`. The data is an ODbL 1.0 Produced Work derived
from OpenStreetMap. In the current customer candidate, Firefox visibly showed
`MapLibre | Protomaps © OpenStreetMap` and a collapsed attribution-info icon;
the expanded information has not yet been browser-checked. The source manifest
declares `© OpenStreetMap contributors; Protomaps Basemap` attribution and pins
the source and metadata URLs, N.O.M.A.D. image digest, PMTiles CLI
version/commit, extraction arguments, and derived file hash. The map is a local
geographic reference, not routing, GPS positioning, trail guidance, or
emergency advice.

Fresh clean-source no-NIC E2E report:
`/mnt/shared/fieldos-e2e/20261105T031700Z-1734990/report.md`. Firefox screenshots
visibly show detailed streets, labels, waterways, and public/green space at
Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Jackson, Johnson City,
and Big South Fork. Nonempty zoom-13 vector tiles at all eight locations were
also checked. The world and U.S. overviews remain low resolution. This map does
not supply routing, GPS positioning, trail data, or navigation. The statewide
The map is also verified in the current interactive customer candidate. Its
no-NIC UEFI install completed, booted the installed disk, visibly rendered all
eight locations, and passed two reboots. Screenshots are in
`/mnt/shared/fieldos-e2e/customer-8c81d64-20261105/viewer/`; physical USB
behavior remains unverified. Full evidence is in [`RELEASE.md`](RELEASE.md).

The historical `cc4aa38` customer candidate was
`/mnt/shared/fieldos-releases/fieldos-customer-cc4aa38.iso` (SHA-256
`0319a069a4874d0522f660c6d69027e6ab9c4aaf86f2f8c995efb9d359a1e139`). It
contains Project N.O.M.A.D.'s miniature English
Wikipedia ZIM, a low-zoom global Protomaps basemap (`world.pmtiles`) plus a
low-zoom continental United States sample region (`fieldos-sample-us.pmtiles`),
Ollama Qwen3 1.7B Q4_K_M selected for CPU chat with the 0.6B model as fallback,
`nomic-embed-text:v1.5` for embeddings, and six core water, food, agriculture,
heat-illness, weather, and emergency reference packs. The water/food pack
contains two unchanged CDC PDFs about emergency water treatment and food
safety after a power outage. Firstboot indexes the CDC documents and NWS-based
summaries in N.O.M.A.D.'s local source library. This is a starter set, not a
comprehensive disaster library. The tested candidate does not contain the
MedlinePlus first-aid overview or CDC emergency-kit checklist. The current
source catalog marks both as core, but a successor ISO must be built and
accepted before claiming these packs are installed. The customer candidate
contains the pinned statewide Tennessee map described above. Fresh no-NIC E2E
and interactive customer installation checks confirmed it is available
offline and visibly renders in Firefox. The sample
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
Earlier scenario testing found that N.O.M.A.D. could attach unrelated sources
and generate unsafe, unsupported advice, including false claims about chemical
water treatment and irrelevant wildfire evacuation guidance. The current
candidate installs a source-bounded policy; tested high-risk prompts returned a
fixed refusal with no citations. The policy uses a lightweight keyword guard
and alternate phrasing can bypass it, so it is not a general safety system.
Open original documents directly and do not use AI answers for emergency or
medical decisions.

The earlier `fieldos-customer-core4-21ad4fc.iso` contained a 19.6 MB Middle
Tennessee map, zoom 0–13, coverage `-88.5,35.4,-85.7,36.7`; it was superseded
by the statewide customer candidate above. GPS/GIS integration is not
validated; the detector only reports whether a likely GPS device node is
present.

The extensible pack format and planned categories are documented in
[`CONTENT-PACKS.md`](CONTENT-PACKS.md). An earlier candidate on source
`1fb6806` installed and indexed both CDC PDFs and the NWS tornado text in
N.O.M.A.D.; its historical reports are in
`/mnt/shared/fieldos-e2e/20261104T080251Z-3272638/report.md` and
`/mnt/shared/fieldos-e2e/customer-nws-1fb6806/`.

The current `8c81d64` customer guest installed the eight packs marked core in
the source catalog, including the CDC emergency-kit checklist and short
MedlinePlus first-aid overview. After firstboot, N.O.M.A.D. indexed 10 files
and 690 chunks. The 2026 Southeastern Vegetable Crop Handbook search companion
supplied 678 chunks; the NIOSH heat-illness source remains narrow, worker-focused
material. Wildlife, broader agriculture, procedural first aid, and
comprehensive reference packs still need source selection, licensing review,
and activation evidence. These references remain limited and do not close the
broader agriculture or medical coverage gaps. A further manual test imported
the optional FieldOS-authored communications planner from read-only media; the
Source Library displayed it and it survived a reboot. Physical USB import
remains unverified.

For direct source discovery, the 2026 crop handbook and selected CDC PDFs now
have small `pdftotext -layout` search companions in their content packs. The
handbook is split into five page ranges so each stays within the Source
Library's existing 1 MiB text-search limit. The original PDFs remain the
authoritative documents and open from the Source Library; companions are
machine-generated navigation aids, with layout loss possible. They are
checksum-verified and included in their pack manifests, searchable from the
local Source Library, and excluded from duplicate N.O.M.A.D. AI indexing.
Searchability does not fix semantic RAG ranking: the tested model retrieved
unrelated crop tables for a tomato-date question. Use the companion to locate
the original page and verify it directly. The `dc6d823` clean-source payload
and no-NIC E2E confirmed the companions install and appear in the Source
Library; a post-run guest check found the East/West tomato dates and frost-free
qualification in the library text and confirmed they were not uploaded to the
AI index. This validates source discovery, not the model's semantic answers.

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
