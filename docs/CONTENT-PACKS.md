# Modular offline content packs

FieldOS keeps reference content modular where practical. The versioned manifest
schema is `payload/manifests/content-pack.schema.json`; the source catalog is
`payload/manifests/content-packs.json`. The current source catalog declares nine core packs and three optional packs;
the ISO baseline bundles the nine core packs while optional archives are
transferable separately. This is a useful starter collection, not a
comprehensive customer library.

The current customer-mode engineering candidate is
`fieldos-customer-test-valkey-129da89.iso` (SHA-256 `ddd9015cbc56dad3635f5453f8d0f6b5ff6a834610394cf3d2fab38dd2d796e2`). It passed
interactive no-NIC installation, firstboot, local applications, and two reboots
in a disposable UEFI VM. The exact-source unattended E2E also passed. See
[current validation](VALIDATION-CURRENT.md). The CDC private-well core pack is
included and indexed. These are VM test results; physical USB is unverified and
redistribution remains uncleared.

The `8c81d64` ISO source contains all eight then-current core pack manifests.
Guest runtime records confirm the CDC emergency-kit checklist was indexed as
one chunk and Southeastern handbook version `2026.1.1` as 678 chunks. The
MedlinePlus core pack was version `2026.07.22`; its `index_with_ai: false`
setting keeps it out of the N.O.M.A.D. vector-index count, and direct Source
Library activation was not recorded in the acceptance report. Current source
metadata is newer for MedlinePlus (`2026.07.22.1`) and Southeastern
(`2026.1.2`); those updates are not in this ISO.

Current-source core archives were rebuilt from `f7b1962` under
`~/Workspaces/hckrslsh-fieldos-artifacts/source-f7b1962/content-packs/`. All eight
passed `zstd -t` and their SHA-256 sidecars passed `sha256sum -c`. These are
transfer/build artifacts, not a rebuilt or accepted ISO, and they do not close
the separate rights review.

**Historical pack-import check (manual, 2026-11-05):** An optional
household communications pack was built from the tracked manifest and imported
through the installed GNOME launcher, file picker, and administrator prompt
from read-only optical media. Firefox showed it in the Source Library with
source notes and a local document link. The document endpoint returned HTTP
200; package metadata, bundle checksum, and document checksum matched the
current source, and the pack, generated index, and seven containers survived an
additional reboot without a network adapter. This is an add-on test on the
customer acceptance guest, separate from the clean install run; physical USB
insertion/navigation remains untested. Evidence:
`/mnt/shared/fieldos-e2e/customer-8c81d64-20261105/content-pack-import-validation.txt`
and `viewer/content-pack-import-search.png` in that run directory.

The previous shared archive for `us-household-communications` had a valid
checksum for its own bytes but carried stale manifest metadata
(`weather-disaster` / `authoritative-reference`) inconsistent with the current
tracked pack (`communications` / `fieldos-authored`). That import was excluded
from acceptance and its test-only installed copies were removed. The old shared
archive was preserved. The current-candidate check used a newly built archive
from the tracked manifest (SHA-256
`114e846643edf5b4d196bc0e6ef4e33167e90e494efba84c2ed90ddea43ded63`). Keep
this discrepancy in mind before transferring the historical archive elsewhere.

Historical clean no-NIC pack-import and map checks are also recorded at
`/mnt/shared/fieldos-e2e/20261105T155548Z-3200639/report.md` (source
`8c9870b`). Earlier failed/intervened UI attempts remain historical only and
are not current-candidate acceptance evidence.

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
- General offline reference and encyclopedia collections
- Regional maps, GPS, and GIS data

## Wildlife and plant-reference licensing review

The initial Tennessee wildlife and hazardous-plant review did not identify a
complete guide with clearly documented redistribution rights. Do not add these
candidates to a FieldOS bundle unless the rights gaps below are resolved:

- University of Tennessee Extension PB 1586, *Poisonous Plants of the
  Southeastern United States*, is a searchable 51-page regional reference, but
  its official PDF does not state reuse terms and includes imagery whose rights
  were not established. Obtain written permission covering the document and
  images before redistribution: [official PDF](https://giles.tennessee.edu/wp-content/uploads/sites/194/2020/10/Ag-Poisonous-Plants-of-the-Southeastern-United-States.pdf).
- UTIA SP627, *Identification and Control of Non-Native Invasive Forest Plants
  in Tennessee*, is listed by UTIA, but its publication record does not provide
  a redistribution license. Request written permission: [UTIA publication
  record](https://solutions.tennessee.edu/publication/SP627/).
- USDA Forest Service GTR SRS-119, *A Field Guide for the Identification of
  Invasive Plants in Southern Forests*, covers 56 plants across 13 southern
  states including Tennessee. Although USDA-authored text may be public domain,
  the 126-page PDF contains credited third-party imagery, including an image
  explicitly marked used by permission. The whole PDF is therefore not cleared
  for redistribution; assess image rights or develop a separately reviewed
  text-only derivative before use: [USFS publication record](https://research.fs.usda.gov/treesearch/35292).

TWRA's [wildlife information pages](https://www.tn.gov/twra/wildlife) provide
topic information but did not establish a single licensed, distributable field
guide. This is a preliminary source review, not legal advice or clearance. Keep
these works out of public release payloads until the required permissions and
asset-level credits are recorded in a pack manifest.

## High-value references awaiting rights clearance

- The National Center for Home Food Preservation hosts the USDA *Complete
  Guide to Home Canning*, 2015 revision, as eight chapter PDFs. This would fill
  a major food-preservation gap, but the guide is a cooperative USDA/UGA
  publication with many contributors and no explicit whole-document
  redistribution grant was found. Request written permission from the relevant
  publishers and confirm image rights before packaging the PDFs or an edited
  derivative. Preserve its edition and safety limits if cleared:
  [NCHFP guide overview](https://nchfp.uga.edu/resources/entry/about-the-usda-guide-to-home-canning-2015-revision),
  [2015 introduction](https://nchfp.uga.edu/papers/guide/INTRO_HomeCanrev0715.pdf).
- USDA NRCS's 2021 *Cropland In-Field Soil Health Assessment Guide* is relevant
  to field use, but its acknowledgements credit multiple outside sources and
  say photos were used with permission. The complete illustrated PDF is not
  cleared for FieldOS redistribution; ask NRCS for reuse scope or develop a
  rights-reviewed text-only derivative. It is a field-assessment aid, not a
  soil laboratory test or complete fertility guide:
  [official PDF](https://www.nrcs.usda.gov/sites/default/files/2022-10/Cropland_InField_Soil_Health_Assessment_Guide.pdf).
- EPA's *Emergency Disinfection of Drinking Water* is a possible sanitation
  supplement, but an item-specific redistribution grant was not established in
  the review. The existing CDC emergency-water reference already addresses
  important treatment limits; do not add the EPA PDF until its rights and a
  specific coverage gap are confirmed:
  [EPA publication page](https://www.epa.gov/ground-water-and-drinking-water/emergency-disinfection-drinking-water-0).

## Southeastern vegetable production reference

`us-southeastern-vegetable-growers` source manifest version `2026.1.2` is a
Tennessee-relevant agriculture pack. It declares textual regional scope as the
Southeastern United States, including Tennessee; this does not make the handbook
a Tennessee-specific calendar. The `8c81d64` ISO contains the unmodified
handbook and manifest version `2026.1.1`; guest logs show it indexed as 678
chunks. Current source version `2026.1.2` adds the Southeastern U.S. scope
field. It contains the unmodified, searchable
397-page 2026 Southeastern U.S. Vegetable Crop Handbook (3,991,344 bytes;
SHA-256
`f7b07e9d630a39a998d0ed5da717a73cd3de5306773695b4d83b16f1ddd27e9c`). The
handbook's official publication page lists the last revision as January 2026,
describes the included crop, soil, pest, planting-date, fertilizer, and food
safety topics, and states that Virginia Cooperative Extension materials may
be publicly used, reprinted, or cited with specified institutional and author
credit. The pack attribution lists the seven authors named on the
publisher page: Mark S. Reiter, Tom P. Kuhar, Kemper Sutton, Laura Strawn,
Douglas S. Higgins, Steve L. Rideout, and Vijay Singh. It also credits senior
editor A. L. Wszelaki, Virginia Cooperative Extension, Virginia Tech, and
Virginia State University. The Source Library renders that manifest
attribution. The intact PDF preserves the handbook's full contributor and
photo credits. Source and reuse record: [Virginia Cooperative Extension
publication page](https://www.pubs.ext.vt.edu/AREC/AREC-66/AREC-66.html). This is a
regional commercial-vegetable reference, not a complete farm manual, livestock
guide, or Tennessee-specific calendar. The source record advises that local
markets, weather, and location can require changed practices or planting dates.
It remains independently packaged for transfer. A `2026.1.2` archive was
built and verified under
`~/Workspaces/hckrslsh-fieldos-artifacts/source-f7b1962/content-packs/`; the archive
below is historical version `2026.1.1`. Searchability was checked
by extracting 1.8 MB of text from the PDF. A fresh no-NIC E2E imported the
archive from read-only transfer media, activated its Source Library link, and
indexed the document in N.O.M.A.D. as 678 chunks. It survived two guest
reboots. This validates the existing transfer workflow, not a nontechnical
USB interface. The portable archive is
`/mnt/shared/fieldos-content-packs/content-packs/us-southeastern-vegetable-growers-2026.1.1.tar.zst`
(3,737,859 bytes; SHA-256
`67ba6be8136afcdfbe14642675520369fc04b8f5a44bbf39d36da31a69a175a9`).
The earlier `2026.1` archive remains historical. The `2026.1.2` archive is
current-source transfer material only; the new scope field remains source-only
in the accepted ISO until a successor payload/ISO is built and tested.
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
authentication prompt. Keep the exact matching sidecar
`<archive-name>.tar.zst.sha256` beside the archive in the same USB folder.
The virtual read-only media transfer passed; physical USB insertion and
navigation through GNOME Files have not yet been tested.
The launcher uses the same validator and installer described below; it asks
N.O.M.A.D. to index reference documents after activation. This adds no new
network service and exposes no remote administrative interface.

Kiwix remains limited to the bundled 100-article Wikipedia test ZIM in the
accepted `8c81d64` ISO. Source commit `a1257f2`, corrected by `0f83517`, includes
an optional ZIM-pack import adapter: it accepts only `.zim` artifacts, verifies manifest size and SHA-256,
hard-links verified immutable pack data into the persistent Kiwix directory
(with a space-checked copy fallback), updates a temporary Kiwix XML library
using the pinned local image with networking disabled, and atomically publishes
the updated library. The server's existing `--monitorLibrary` option should
pick up that change. Unit tests cover registration, idempotence, conflict and
failure handling, and hard-link reuse. A targeted test on the exact pinned
image passed real `kiwix-manage` registration and `kiwix-serve` retrieval on an
internal-only Docker network; a second import was observed in the live OPDS
catalog and its article route returned content. Evidence is at
`/mnt/shared/fieldos-e2e/kiwix-zim-runtime-20261106/report.md`. The guest
desktop/browser import workflow has not been tested, and this code is not in
the accepted ISO.

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

The Source Library's on-page search is deterministic and works offline. It
searches pack titles, descriptions, source/attribution metadata, and the full
text of plain-text documents up to 1 MiB. PDF and longer documents remain
linked as originals; open them and use the browser's Find command to search
within the document. Search results are document links and text excerpts, not
AI answers.

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

## CDC food-safety mistakes factsheet (optional transfer pack)

`us-cdc-food-safety` version `2023.04.14.1` is an optional, independently
installable pack. It contains CDC's original five-page *Food Safety: 10
Dangerous Food Safety Mistakes* factsheet and a searchable text companion. The
factsheet covers cooking, cross-contamination, thawing, time at room
temperature, produce washing, handwashing, risk groups, and food spoilage. Its
charts and illustrations remain in the PDF; the text extraction is only a
search aid. It is dated April 14, 2023, links to more detailed resources that
are not bundled, and is not a comprehensive food-preservation, canning, or
power-outage manual.

The [CDC Stacks record](https://stacks.cdc.gov/view/cdc/129474) marks this exact
item Public Domain, identifies the publisher and date, and provides a SHA-512
checksum matching the unchanged local PDF. CDC's [agency-materials policy](https://www.cdc.gov/Other/imagereuse.html)
requires attribution, a prominent non-endorsement disclaimer, and notice that
the source is available at no charge; those are recorded in the pack manifest
and generated Source Library. This is a source-specific U.S. rights review,
not clearance of the entire FieldOS distribution. The content is not indexed
for AI; users access the attributed PDF and searchable text directly.

The archive built from source `a88aece` plus this pack is
`/mnt/shared/fieldos-content-review-a88aece/content-packs/us-cdc-food-safety-2023.04.14.1.tar.zst`
(912 KiB; SHA-256
`6326e5eb910ef5ad1f7260507ce83722f54ba28b71afc4cc5f0d9a58450abd8c`). `zstd
-t`, the checksum sidecar, and a temporary-root install using the production
content-pack installer passed. The installer generated a local Source Library
entry linking both files; reinstall was idempotent. A desktop file-picker import
of this exact archive and inclusion in the standard ISO have not yet been
verified.

## Private-well emergency reference (unattended test ISO validated)

Source revision `d04f450` adds `us-cdc-private-wells` version `1.0.0`, a
15,338-byte searchable text rendition of CDC's *How to Disinfect Wells After
an Emergency* (May 29, 2025), SHA-256
`d8a05f9568a60c1e568869018e0ec769cae3a0bf13260765cc8f6edbee8e09a6`. It
preserves the page's hazard callouts, disinfection tables, testing advice, and
source links, while excluding the photograph and page navigation. CDC warns
that well work is hazardous and should be handled by a qualified contractor;
water contaminated by fuel or toxic chemicals is not made safe by boiling or
disinfection. The pack is not a substitute for local health-department advice.

The source is the CDC National Center for Environmental Health page at
<https://www.cdc.gov/water-emergency/about/how-to-disinfect-wells-after-an-emergency.html>.
CDC's agency-materials policy requires attribution, a clear non-endorsement
statement, no substantive edits, and notice that the material is available
from CDC at no charge; the pack records those terms and is text-only. Rights
review supports reuse of this CDC-authored text under that policy, but does not
constitute legal advice or clear unrelated FieldOS payloads. This pack is now
listed as a core pack in the source catalog and passed clean-source offline
installation and reboot checks as part of an unattended test ISO. The current
interactive customer ISO does not contain it. Its independently transferable
archive is at
`/mnt/shared/fieldos-content-packs/us-cdc-private-wells-2026.1.0/content-packs/us-cdc-private-wells-1.0.0.tar.zst`
(5,758 bytes; SHA-256
`e9f088235420ace9ffaa71b9c162e095ac817a78f1ece8cb4a14775b1541aac4`). The
archive passed `zstd -t`, member listing, and a temporary-root install through
the production pack installer; the installed file hash matched the manifest.
The E2E browser screenshot shows the entry, description, CDC attribution, and
offline document links in FieldOS Source Library. This does not establish
commercial redistribution clearance or a comprehensive private-well manual.

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
document. It is not one of the eight core packs in the `8c81d64` ISO. It contains the CDC's
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
close FieldOS's first-aid or medical-reference gap. It remains optional and
outside the `8c81d64` core catalog.

## CDC emergency kit checklist

`us-cdc-keep-calm-prepared` version `1.0.0` is an unchanged two-page
CDC emergency-kit checklist. It covers household, workplace, school, vehicle,
and additional family or pet supply considerations. It is a brief 2013
preparedness checklist, not a complete all-hazards plan, first-aid guide, or
medical reference. The exact [CDC STACKS record](https://stacks.cdc.gov/view/cdc/23954)
identifies the item as Public Domain, gives its publication date and two-page
extent, and provides the original PDF link. The current source catalog marks
this pack as core. It was absent from historical ISO `cc4aa38`, but the
`8c81d64` candidate contains it and its guest runtime record shows one indexed
chunk; see the current-candidate evidence above.
The bundled file is 138,605 bytes
with SHA-256
`d8d3ad68df32f5c069968e5f71d58e2e03bd3751e985877f28122a988388f319`; its PDF
text is extractable. In a separate offline copy-on-write guest test, the
archive was transferred from read-only media, appeared in Firefox's Source
Library, opened as a two-page PDF, and indexed in N.O.M.A.D. as one chunk. The
file, Source Library listing, and indexed row persisted through two reboots.
The manifest records CDC attribution and makes clear that source and license
review is not a clinical review. Its portable archive is
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

## MedlinePlus first-aid overview

`us-medlineplus-first-aid` source manifest version `2026.07.22.1` describes
a portable 3,086-byte text snapshot of the MedlinePlus **First Aid** health-topic summary.
It covers when to call 911, general cuts-and-scrapes care, Poison Control,
heat-related illness, and basic kit contents. The source page was last updated
2026-07-22. Its 436-word summary is not a complete first-aid manual, course,
or clinical review; the pack includes a separate FieldOS note identifying the
snapshot date and limits.

The source manifest now includes both the First Aid page and the [NLM reuse
policy](https://medlineplus.gov/about/using/usingcontent/) as separate source
records. The policy specifically identifies summaries on health-topic pages as
public domain and permits reproduction with attribution. The pack includes only that summary,
with whitespace/list formatting normalized; it excludes linked article text,
third-party material, images, logos, and page chrome. The artifact SHA-256 is
`32cc39ebdff811dd08e6ca2550a432a8b1d436c304e899162d742a18a0829893`. Its
manifest attributes the source to MedlinePlus and NLM and disclaims endorsement.
This is a U.S. public-domain review, not a statement about international rights.
The current source catalog marks the pack as core. The `8c81d64` candidate
source records version `2026.07.22`; source version `2026.07.22.1` adds the
policy page as a source record without changing the text artifact. The current
archive was rebuilt under
`~/Workspaces/hckrslsh-fieldos-artifacts/source-f7b1962/`,
but that updated metadata has not been tested in an ISO. The guest acceptance
log does not record direct Source Library activation for this pack; its
`index_with_ai: false` setting excludes it from the vector-index count.

Its portable archive is
`/mnt/shared/fieldos-content-packs/content-packs/us-medlineplus-first-aid-2026.07.22.tar.zst`
(2,649 bytes; SHA-256
`2670511092fb5796fef918a9468062bf24691b9ca3bee917f947046c17f94745`). A
Host-side isolated installation passed checksum/schema checks, generated a
Source Library entry, and passed an idempotent reinstall check. The pack then
passed installation from read-only transfer media in a clean no-NIC guest:
the installed and web-served document hashes matched, attribution and local
document links appeared in the Source Library, and the installation persisted
across two reboots. `index_with_ai: false` remains intentional: the summary is
available for deterministic Source Library search and direct reading, and is
not uploaded to N.O.M.A.D.'s vector Knowledge Base. The tested guest path called
the pack installer directly; the separate desktop file-picker flow has not yet
been exercised for this pack. Guest evidence:
`/mnt/shared/fieldos-e2e/20261105T120618Z-2754929/report.md`; host validation:
`/mnt/shared/fieldos-content-packs/content-packs/us-medlineplus-first-aid-2026.07.22-validation.md`.

## Household emergency communications planner

`us-household-communications` version `1.0.0` is a 6,411-byte,
FieldOS-authored text worksheet informed by FEMA/Ready.gov family planning
guidance and NWS information about NOAA Weather Radio. It helps a household
record primary and backup contacts, meeting locations, alternate channels,
school or caregiver contacts, access needs, and a review date. It warns that
communications can fail, recommends paper copies and privacy-conscious data
handling, and does not collect or store the user's personal plan. This is not
an official FEMA form, live alert service, or emergency communications system.
It contains no copied FEMA text, branding, artwork, or template. The text is
licensed under the project Apache-2.0 license; sources are listed for attribution
and factual context only. The manifest identifies it as `fieldos-authored`,
category `communications`, and records the artifact checksum.

A clean GUI import and persistence test on the current customer guest is
recorded in `content-pack-import-validation.txt` under the latest acceptance
run. The archive for that check was built from the current tracked manifest
(SHA-256 `114e846643edf5b4d196bc0e6ef4e33167e90e494efba84c2ed90ddea43ded63`).
The older portable archive at
`/mnt/shared/fieldos-content-packs/content-packs/us-household-communications-1.0.0.tar.zst`
(SHA-256 `3f5e60f956a8604cb8ee4d08e37993191af745e9484d4d36aab7d2bb6b28c812`)
has stale metadata and does not match the current tracked manifest. It remains
preserved as historical material; do not transfer it. A prior clean E2E
reported this pack as `authoritative-reference` and indexed its content, but
that evidence is superseded for the current manifest. The verified current
candidate import showed the worksheet directly in the Source Library and served
the local original; chat extraction of household fields remains unverified.
The pack is optional and is not embedded in the customer ISO.

## Flood safety reference pack

`us-flood-safety` source manifest version 1.0.1 records a short FieldOS-edited
summary of NWS flood preparedness and response pages. It describes pre-event
planning and basic actions while water is rising, identifies its gaps, and links
the original NWS sources. The 1.0.1 artifact metadata explicitly links the
summary to both NWS before-flood and during-flood source records, retaining
`source` as the primary source for older readers. No 1.0.1 archive has been
built. The text is an editorial summary, not an official NWS/NOAA publication;
it provides no current warning, forecast, local flood-zone data, or route
planning. The source list records NOAA reuse guidance, attribution, and
non-endorsement language. No third-party images are included. Full project
redistribution review remains open.

The recorded portable archive is the earlier version 1.0.0 at `/mnt/shared/fieldos-payload/content-packs/us-flood-safety-1.0.0.tar.zst`, SHA-256 `a8540ec40b5964f46c5fb0a2b3ff9f73afa601b96194a621bb91280605dbd470`. An earlier no-NIC E2E transferred it from a read-only ISO, validated and installed it, displayed it in the Firefox Source Library, indexed its two chunks in N.O.M.A.D., and confirmed persistence through two reboots. Report: `/mnt/shared/fieldos-e2e/20261104T132809Z-3606267/report.md`; that run used an uncommitted worktree and is integration evidence, not a clean-source release acceptance. The pack is now a core pack in the source catalog. The current clean-source six-pack unattended E2E and interactive customer candidate both activated and indexed flood references; current results are recorded in [`RELEASE.md`](RELEASE.md).

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
