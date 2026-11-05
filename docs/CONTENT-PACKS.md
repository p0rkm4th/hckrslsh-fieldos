# Modular offline content packs

FieldOS keeps reference content independent from the core installer wherever
possible. The repository defines a versioned JSON manifest schema at
`payload/manifests/content-pack.schema.json` and a catalog at
`payload/manifests/content-packs.json`. The catalog contains the core reference
packs and planned categories; this is not a comprehensive customer library.
The Middle Tennessee map previously passed offline transfer and activation
testing as a pack. The statewide Tennessee map is built into the current source
payload and customer ISO candidate. It passed a fresh no-NIC unattended E2E
with visible Firefox rendering at eight locations and two reboots; the
interactive customer install rendered Nashville, though its installer
media-handoff test needed host intervention. The exact candidate, checksum,
and reports are recorded in [`RELEASE.md`](RELEASE.md).
Other regional and specialist reference collections remain modular packs
outside the core image.

Staged pack directories use `payload/content-packs/<pack-id>/manifest.json`
with artifact paths relative to that pack. The catalog lists relative paths to
those manifests. Run `make validate-content-packs` to check catalog references,
required metadata, safe artifact paths, declared size and SHA-256, geographic
bounds, and emergency-reference review fields. The validator does not decide
whether a license permits redistribution; a human review is still required
before adding a pack to a distributable build.

Planned pack categories are:

- Agriculture, farming, soils, and equipment reference
- Wildlife, camping, and overlanding
- Water treatment and food preservation
- Severe weather and emergency reference
- First aid
- Regional maps, GPS, and GIS data

## Southeastern vegetable production reference

`us-southeastern-vegetable-growers` version `2026.1` is a Tennessee-relevant
agriculture pack included in the current core payload. It contains the unmodified, searchable
397-page 2026 Southeastern U.S. Vegetable Crop Handbook (3,991,344 bytes;
SHA-256
`f7b07e9d630a39a998d0ed5da717a73cd3de5306773695b4d83b16f1ddd27e9c`). The
handbook's official publication page lists the last revision as January 2026,
describes the included crop, soil, pest, planting-date, fertilizer, and food
safety topics, and states that Virginia Cooperative Extension materials may
be publicly used, reprinted, or cited with specified institutional and author
credit. The intact PDF preserves the handbook's full contributor and photo
credits. Source and reuse record: [Virginia Cooperative Extension publication
page](https://www.pubs.ext.vt.edu/AREC/AREC-66/AREC-66.html). This is a
regional commercial-vegetable reference, not a complete farm manual, livestock
guide, or Tennessee-specific calendar. The source record advises that local
markets, weather, and location can require changed practices or planting dates.
It remains independently packaged for transfer, although the current ISO
includes it in the core payload. Searchability was checked
by extracting 1.8 MB of text from the PDF. A fresh no-NIC E2E imported the
archive from read-only transfer media, activated its Source Library link, and
indexed the document in N.O.M.A.D. as 678 chunks. It survived two guest
reboots. This validates the existing transfer workflow, not a nontechnical
USB interface. The portable archive is
`/mnt/shared/fieldos-content-packs/content-packs/us-southeastern-vegetable-growers-2026.1.tar.zst`
(3,273,118 bytes; SHA-256
`e7dd06a657973a15bd75a1d9986ec774aef7f0b86c1f88ce4e4b25416cac7e30`).
E2E evidence: `/mnt/shared/fieldos-e2e/20261104T215624Z-1056575/report.md`.

Each populated pack has its own stable ID and version. Its manifest records
each source and URL, license and attribution, every artifact's size and
SHA-256, and installation target and requirements. Geographic packs also
declare bounds, coordinate reference system, and zoom range. Build tooling
validates sizes and checksums before packaging. `make content-packs` builds
deterministic `.tar.zst` archives and SHA-256 sidecars for removable-media
transfer under `FIELDOS_PAYLOAD_ROOT/content-packs/`. Packs listed in the
catalog's `core_packs` are also embedded in the offline payload by `make payload`
and activated during firstboot. Other catalog packs remain separate from the
core image. Archives contain the manifest and only the artifacts it declares,
so stray or unreviewed files in a staging directory are excluded. The core
packs' manifests and source documents are staged in Git; their portable
archives are generated during payload construction. The current source map
payload and separately tested interactive customer ISO contain the same
checksum-pinned statewide Tennessee map. Redistribution review remains incomplete; see the payload manifest and
[`REDISTRIBUTION.md`](REDISTRIBUTION.md).

For a desktop import, open **FieldOS Install Content Pack** from Applications
→ Utilities, choose the `.tar.zst` archive, and approve the administrator
authentication prompt. Keep the matching `.sha256` sidecar beside the archive.
The launcher uses the same validator and installer described below; it asks
N.O.M.A.D. to index reference documents after activation. This adds no new
network service and exposes no remote administrative interface.

For operator use, verify and add a bundle with:

```sh
sudo /opt/fieldos/scripts/fieldos-content-packs.py install /path/to/pack-1.0.tar.zst
sudo /opt/fieldos/scripts/fieldos-content-packs.py list
```

Installation checks the sidecar checksum, rejects unsafe archive entries,
validates the manifest and artifact hashes, checks available space, and stores
each immutable version under `/var/lib/fieldos/content-packs/<id>/<version>`.
Repeating the same install is safe; a different bundle cannot overwrite an
existing version. For a map pack whose target is `storage/maps/pmtiles`, the
installer additionally requires exactly one PMTiles archive and atomically
publishes it in `/var/lib/fieldos/storage/maps/pmtiles/`. N.O.M.A.D. discovers
that file in its region inventory and generates its map source automatically.
For a reference-document pack whose target is `storage/references/documents`,
the installer accepts only PDF and plain-text artifacts and atomically creates
`/var/lib/fieldos/storage/references/index.html`. The local index lists source,
license, attribution, and links to original documents; it identifies them as
source material rather than AI output. It warns that inclusion is not publisher
endorsement and users should consult current local guidance. On first boot,
FieldOS uploads checksum-verified PDF and TXT artifacts through N.O.M.A.D.'s
native `/api/rag/upload` endpoint and waits until each appears as indexed with
embedded chunks. This uses N.O.M.A.D.'s existing Knowledge Base and Qdrant
integration; it adds no separate retrieval service. Run
`sudo python3 /opt/fieldos/scripts/fieldos-nomad-index-references.py` after
installing another reference pack from removable media. The command is
idempotent for files that are already indexed. Verified documents are copied without replacement to
`/var/lib/fieldos/storage/references/documents/<id>/<version>/`; N.O.M.A.D.'s
existing static-file server exposes only this reference directory read-only at
`http://localhost:8080/fieldos-references/`. No new service or external route is
added. Existing filenames are never replaced. A failed validation or
conflicting destination leaves existing application data untouched. If
indexing fails, firstboot records failure rather than claiming provisioning is
complete; source documents remain available in the Source Library.

The core starter reference pack is `us-water-food-emergency` version 1.0.0.
It contains two unchanged CDC PDFs: “Make Water Safe During an Emergency” and
“Eat Safe Food After a Power Outage.” Their source records are CDC STACKS
items [128149](https://stacks.cdc.gov/view/cdc/128149) and
[88473](https://stacks.cdc.gov/view/cdc/88473); each record identifies the item
as Public Domain. The original PDFs are reproduced unmodified with CDC
attribution and a non-endorsement statement. The included files are 730,926
bytes (SHA-256
`c39b55b4d8f3dd40ecd2b13175f7661b52dfc6e73e4a24ef189de64fb9d513b1`) and
1,675,372 bytes (SHA-256
`0982174617e2b3405e966b0b1dc2838e3ce92dfad3185da3d450b525a62a7ebf`). The
manifest records source URLs, access and review dates, and license basis. The
archive built from this revision is
`/mnt/shared/fieldos-content-packs/content-packs/us-water-food-emergency-1.0.0.tar.zst`,
SHA-256 `c862c023e8999268be6d78692e4d3a01c95a3f5f840fa954b424b5604eb9518c`.
It is a small starter set, not a complete water, food, first-aid, medical, or
disaster-preparedness library. Consult current local guidance. Source-tree
configuration includes this pack in the offline payload, and its installation
in the current candidate is verified by fresh E2E and interactive-install
reports. The customer candidate is not approved for release.

## Severe-weather content

`us-weather-safety` version 1.0.1 is a portable reference pack included in the
current core installer. It contains three clearly labeled editorial summaries based
on National Weather Service guidance for hurricane threats, winter-storm
preparation, and actions during a winter storm. Each document links its exact
NWS source, states that it is an edited FieldOS summary rather than official
NWS material, and warns that it cannot provide current forecasts or alerts.
The manifest records source URLs, access/review dates, NOAA reuse guidance,
artifact hashes, and attribution. NOAA says nearly all NOAA content is public
domain unless otherwise noted, while requiring source credit and prohibiting
implied endorsement; the pages were checked for their agency attribution and
third-party credits. This is a limited reference set, not an all-hazards plan.

Build its removable-media archive with `make content-packs`. The current
archive is `/mnt/shared/fieldos-payload/content-packs/us-weather-safety-1.0.1.tar.zst`
(SHA-256 `9be415ad975ef8ef5ef2bd483254dac6ca2b400bfc594ec4309db6205e3b1e1c`).
The pack also has a removable-media archive. When installed separately,
FieldOS verifies the archive and checksums, publishes the source documents,
and asks N.O.M.A.D. to index them. The source library remains
available directly even when AI chat is unavailable or refuses emergency
questions. The clean-source transfer test at commit `d865333` passed using virtual optical transfer media (not physical USB) as part of the
full acceptance run: all three documents were installed, checksummed, indexed,
opened through the local source library, and persisted across two reboots. The
report and archive hash are recorded in [`RELEASE.md`](RELEASE.md). An earlier
run failed because its cached baseline payload was stale; that source-to-payload
mismatch is now checked before ISO creation.

On source `1fb6806`, a fresh no-NIC E2E and a separate interactive customer-mode
install confirmed that the two CDC PDFs and NWS tornado text were activated in
N.O.M.A.D.'s indexed Knowledge Base. CDC food-safety and NWS tornado queries
returned answers with source references. E2E evidence is
`/mnt/shared/fieldos-e2e/20261104T080251Z-3272638/report.md`; customer-mode
evidence and screenshots are in `/mnt/shared/fieldos-e2e/customer-nws-1fb6806/`.
This verifies activation of these narrow references; it does not make the pack
a comprehensive preparedness library or approve redistribution.
The core catalog also includes `us-tornado-safety`, a text-only conversion of
the National Weather Service's “What to Do During a Tornado” page. Its source,
NOAA reuse basis, attribution, access date, and conversion limits are recorded
in its manifest and document. It adds narrow tornado guidance, not a first-aid
or comprehensive all-hazards library. The current customer candidate includes
the statewide Tennessee map. The Southeastern vegetable handbook and NIOSH
heat-illness transcription are now core payload packs and were activated and
indexed in the current customer guest. Broader livestock, wildlife, procedural
first-aid, and comprehensive reference coverage still need development and
licensing review.

The test harness accepts `FIELDOS_TEST_CONTENT_PACK=/path/to/bundle.tar.zst`.
It places that archive and checksum on a second, read-only ISO attached to the
disposable no-NIC VM and imports it inside the installed guest. Map packs are
checked through N.O.M.A.D.'s region and style APIs, PMTiles reads, browser map
rendering, and persistence after reboots. Reference packs are checked for
installed source documents, local HTTP delivery, a Firefox view, and
persistence after reboots. The transfer medium is test-only and does not
change the customer installer. The latest map-pack acceptance report is
`/mnt/shared/fieldos-e2e/20261104T073217Z-3246434/report.md`; its test ISO hash
is `f82809d05c009d021b2427b3ce3f68664c942e33eb12ae2fe0870df5b9f26b38`, and
the imported archive hash is
`9dce859a72d3b13afa1235838cbfddabfcf8c8cdd741b90fa4b0dec4dcb024a9`. A
separate diagnostic run that tried to re-import the already bundled core pack
failed safely without overwriting it; its report is
`/mnt/shared/fieldos-e2e/20261104T071953Z-3238411/report.md`.

## Basic emergency-health checklist

`us-basic-emergency-health` version `1.0.0` is a portable, optional CDC source
document and is not included in the current core ISO. It contains the CDC's
one-page 2019 *Prepare Your Health: Practical Skills* checklist. The sheet
encourages users to learn skills such as Hands-Only CPR, AED use, seizure first
aid, choking response, and wound care; it does not explain how to perform those
procedures. Treat it as a training checklist, not a first-aid manual, medical
advice, or substitute for professional instruction.

The unchanged PDF is 294,644 bytes with SHA-256
`f29fe3dd877b45c11c4a752a783af2aad965339a695137573c4445a5d8b97966`. Its
[CDC STACKS record](https://stacks.cdc.gov/view/cdc/79987) marks the exact item
Public Domain; the [CDC STACKS rights guidance](https://stacks.cdc.gov/Content%20and%20Copyright)
requests acknowledgement and warns that some materials have separate rights.
The pack retains CDC attribution and says no endorsement is implied. The
manifest records source, license basis, checksum, review date, and its
nonclinical-review limitation. This is a small orientation sheet and does not
close FieldOS's first-aid or medical-reference gap. The pack remains optional
until broader content and redistribution review are complete.

## CDC emergency kit checklist

`us-cdc-keep-calm-prepared` version `1.0.0` is an optional, unchanged two-page
CDC emergency-kit checklist. It covers household, workplace, school, vehicle,
and additional family or pet supply considerations. It is a brief 2013
preparedness checklist, not a complete all-hazards plan, first-aid guide, or
medical reference. The exact [CDC STACKS record](https://stacks.cdc.gov/view/cdc/23954)
identifies the item as Public Domain, gives its publication date and two-page
extent, and provides the original PDF link. The bundled file is 138,605 bytes
with SHA-256
`d8d3ad68df32f5c069968e5f71d58e2e03bd3751e985877f28122a988388f319`; its PDF
text is extractable. In a separate offline copy-on-write guest test, the
archive was transferred from read-only media, appeared in Firefox's Source
Library, opened as a two-page PDF, and indexed in N.O.M.A.D. as one chunk. The
file, Source Library listing, and indexed row persisted through two reboots.
The manifest records CDC attribution and makes clear that source and license
review is not a clinical review. The pack is optional and is not part of the
customer ISO baseline. Its portable archive is
`/mnt/shared/fieldos-content-packs/content-packs/us-cdc-keep-calm-prepared-1.0.0.tar.zst`
(109,922 bytes; SHA-256
`ebfb8bb14588f9af2521a3139420b17eb7db5e96014ad093526dba27d38f8617`). The
existing offline installer was exercised against this archive on the build
host: checksum validation, immutable installation, checksum recheck, generated
Source Library entry, and local original-document link all passed. This
archive then passed the isolated guest integration above. No AI semantic
question-answering test was run for this checklist. Host-side validation
details are at
`/mnt/shared/fieldos-content-packs/content-packs/us-cdc-keep-calm-prepared-1.0.0-validation.md`.

## Household emergency communications planner

`us-household-communications` version `1.0.0` is a 6,411-byte,
FieldOS-authored text worksheet informed by FEMA/Ready.gov family planning
guidance and NWS information about NOAA Weather Radio. It helps a household
record primary and backup contacts, meeting locations, alternate channels,
school or caregiver contacts, access needs, and a review date. It warns that
communications can fail, recommends paper copies and privacy-conscious data
handling, and does not collect or store the user's personal plan. This is not
an official FEMA form, live alert service, or emergency communications
system. It contains no copied FEMA text, branding, artwork, or template.

The authored text is licensed under the project Apache-2.0 license. FEMA and
NWS pages are listed as factual references only; no source files are bundled.
Source links, review date, and the exact artifact checksum are in
`payload/content-packs/us-household-communications/manifest.json`. Its portable
archive is built alongside the other optional packs with `make content-packs`.
The archived pack is 4,037 bytes with SHA-256
`3f5e60f956a8604cb8ee4d08e37993191af745e9484d4d36aab7d2bb6b28c812` at
`/mnt/shared/fieldos-content-packs/content-packs/us-household-communications-1.0.0.tar.zst`.
The latest current-source no-NIC E2E transferred the archive on read-only
optical media, verified and installed it, generated a Source Library entry,
and indexed its document as three chunks in N.O.M.A.D. Firefox visibly opened
the local Source Library. The pack's installed files and generated index
survived two reboots. A later isolated query check failed to retrieve simple
contact fields from the indexed worksheet, although Firefox could open the
original text directly. Treat the pack as locally readable; do not rely on
chat retrieval to extract its fields. The pack remains optional and is not
embedded in the customer ISO. Evidence:
`/mnt/shared/fieldos-e2e/20261105T051319Z-2105879/report.md` and
`reference-library-render.png` in the same directory.

## Flood safety reference pack

`us-flood-safety` version 1.0.0 contains a short FieldOS-edited summary of NWS flood preparedness and response pages. It describes pre-event planning and basic actions while water is rising, identifies its gaps, and links the original NWS sources. The text is an editorial summary, not an official NWS/NOAA publication; it provides no current warning, forecast, local flood-zone data, or route planning. The source list records NOAA reuse guidance, attribution, and non-endorsement language. No third-party images are included. Full project redistribution review remains open.

The portable archive is `/mnt/shared/fieldos-payload/content-packs/us-flood-safety-1.0.0.tar.zst`, SHA-256 `a8540ec40b5964f46c5fb0a2b3ff9f73afa601b96194a621bb91280605dbd470`. An earlier no-NIC E2E transferred it from a read-only ISO, validated and installed it, displayed it in the Firefox Source Library, indexed its two chunks in N.O.M.A.D., and confirmed persistence through two reboots. Report: `/mnt/shared/fieldos-e2e/20261104T132809Z-3606267/report.md`; that run used an uncommitted worktree and is integration evidence, not a clean-source release acceptance. The pack is now a core pack in the source catalog. The current clean-source six-pack unattended E2E and interactive customer candidate both activated and indexed flood references; current results are recorded in [`RELEASE.md`](RELEASE.md).

## NIOSH heat-illness first-aid text

`us-niosh-heat-first-aid` version `2024.1` is a text-only searchable
transcription of NIOSH Publication 2024-100, *Heat Stress: First Aid for Heat
Illness*. The exact [CDC Stacks record](https://stacks.cdc.gov/view/cdc/138337)
marks the 2023 source item Public Domain. The original two-page PDF contains
third-party stock photographs credited to iStock and Thinkstock and CDC
agency marks; those are excluded from this transcription. Source wording is
retained with only layout normalized. The pack includes source attribution,
no-endorsement language, and the free original source URL in its manifest and
document. See [CDC material-use guidance](https://www.cdc.gov/other/agencymaterials.html)
for attribution and logo restrictions. This is a narrow, worker-focused
reference, not a clinical review or general first-aid manual; consult current
emergency guidance and professional care.

The plain-text artifact is 6,593 bytes, SHA-256
`51c4b1f22ce0d7402ce02c05d436bd4e92e132d5c3b04e930cfc794d6a3c3165`. Its
portable archive is
`/mnt/shared/fieldos-content-staging/niosh-heat-first-aid-2024/bundle/content-packs/us-niosh-heat-first-aid-2024.1.tar.zst`,
4,136 bytes, SHA-256
`761fc09ba843a69591021e820050eabdaa7cf98f004f3e0d6bfc698cee7f35df`. It is
included in the current core payload and customer ISO candidate; the
interactive customer guest indexed it as three chunks. This does not establish
clinical correctness or complete first-aid coverage.

## Reference quality and retrieval

Manifest `authority` distinguishes authoritative references from community
material, AI-generated material, or a mixture. Retrieval should preserve the
originating document title and source attribution with each result and make
the original passage accessible. AI-generated responses are summaries, not
source documents. This distinction is essential for first-aid and emergency
material; those packs require a named, reviewable authority and revision date
before inclusion. The CDC starter pack is an attributed source-document
collection; it does not make AI source-grounded and is not a comprehensive
emergency library.

## Mapping and location

The bundled world and sample U.S. PMTiles maps cover zoom levels 0 through 5
for broad orientation. The tested customer candidate also includes a
checksum-pinned statewide Tennessee map with a neighboring-state buffer (bounds
`-90.9,34.5,-81.0,37.25`) at zoom levels 0–13. The 145,267,908-byte PMTiles
file is extracted from the pinned 2026-11-02 Protomaps build using bounded HTTP
range requests. The source manifest records expected size and SHA-256,
ODbL/OSM attribution, bounds, and zoom range. The fresh no-NIC E2E report
(`/mnt/shared/fieldos-e2e/20261105T031700Z-1734990/report.md`) records visible
Firefox map views for eight locations and persistence across two reboots. The
current interactive customer installation visibly rendered Nashville at
zoom 13; its validation report records the installer handoff caveat. See
[`RELEASE.md`](RELEASE.md) for checksums and exact evidence paths.

This map is a geographic reference, not turn-by-turn navigation, trail,
parcel, or emergency guidance. GPS/GIS support needs a defined hardware
interface and offline behavior. The current detector only reports a likely GPS
device node; it does not read coordinates or provide a navigation service.
Protomaps supports bounded regional extraction from its hosted archives
([PMTiles CLI documentation](https://docs.protomaps.com/pmtiles/cli)).
The current zoom-5 archives remain orientation fixtures; Protomaps documents
zoom 15 as sufficient for street-level mapping
([PMTiles creation guide](https://docs.protomaps.com/pmtiles/create)). This is
a planning reference, not a commitment to include zoom-15 data.

For GPS, `gpsd` is a possible future local interface for supported USB/serial
receivers. It can normalize several receiver protocols for local clients
([gpsd documentation](https://gpsd.io/README.html)). It is not selected or
bundled; hardware, permissions, offline behavior, and whether its local socket
can be kept inaccessible from the LAN need validation first.

Do not populate a pack from a public download until redistribution terms and
attribution have been reviewed for the exact artifact and derivative format.
Public availability alone is not permission to redistribute.
For OpenStreetMap-derived content, preserve the required attribution and
ODbL notices ([OpenStreetMap copyright and license](https://www.openstreetmap.org/copyright)).
