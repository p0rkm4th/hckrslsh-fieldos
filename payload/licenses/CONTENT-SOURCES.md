# FieldOS offline content sources and limits

This is the source and attribution guide for the FieldOS payload. It is
also installed in `/usr/share/doc/fieldos/CONTENT-SOURCES.md` and available
from the Applications menu as **FieldOS Content Sources and Limits**.

## Reference archive

The test fixture is the English Wikipedia 100-mini ZIM from Project N.O.M.A.D.
v1.35.1, source commit
`0dbbd21c2f470975e86131c497694c147ca8bc00`, at
`install/wikipedia_en_100_mini_2026-01.zim`. Its size is 4,537,782 bytes and
SHA-256 is
`2811724b72fd34a0728c28b7456d3d6866579019fbbe7ffe28528f3450c252db`.
The archive-level attribution notice is in
`/usr/share/doc/fieldos/wikipedia-zim-attribution.txt`; article-specific
credits and any embedded media notices remain applicable.

Wikimedia's Terms of Use generally license contributor text under CC BY-SA 4.0
and the GNU Free Documentation License, subject to project or feature
exceptions. Non-text media can have separate licenses. The bundled CC BY-SA
4.0 license text is at
`/usr/share/doc/fieldos/CC-BY-SA-4.0.txt`; the official source is
<https://creativecommons.org/licenses/by-sa/4.0/>. See the Wikimedia
[Terms of Use](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use).
FieldOS has not completed an entry-by-entry media license review, so this test
archive is not cleared for public redistribution.

## Maps

The test payload includes a global Protomaps basemap and a U.S. sample
extracted from it, both limited to zoom levels 0–5. The current statewide
Tennessee map covers the full state plus a neighboring-state buffer (bounds
`-90.9,34.5,-81.0,37.25`) at zoom levels 0–13. The 145,267,908-byte regional
file has SHA-256
`0d123132839b77e627c4f4f103bf7a78925099c57319e759757be3207cb89525`, extracted
from pinned Protomaps build `20261102.pmtiles`. The source manifest pins the
archive and metadata URLs, the N.O.M.A.D. image digest, and PMTiles CLI version
and commit; each generated `map-payload.json` records extraction arguments and
the derived file hash. The customer ISO built from source `8c81d64` passed a fresh interactive,
no-NIC UEFI VM install, disk boot, and two reboot checks; the map rendered in
Firefox at eight Tennessee locations. The exact ISO hash and screenshots are
listed in `docs/RELEASE.md` and the dated acceptance evidence. The visible map
attribution reads `MapLibre | Protomaps © OpenStreetMap` with a collapsed
attribution-info icon. The source manifest declares `© OpenStreetMap
contributors; Protomaps Basemap` and ODbL-1.0, but the attribution disclosure
has not yet been opened and inspected in the installed browser. This is a
local geographic reference, not turn-by-turn navigation, GPS positioning,
trail guidance, or emergency advice.
The full ODbL 1.0 text is at
`/usr/share/doc/fieldos/ODbL-1.0.txt`; the attribution notice and source-build
details are in the installed documentation. The payload also carries the
pinned N.O.M.A.D. Maps README, the Noto font OFL, and the MIT notice for
Tangrams-derived sprites. The exact source artwork revision for those modified
sprites is not identified by upstream. The ODbL applies to the database
rights; individual content may have additional rights.

## National Weather Service tornado-safety reference

The core content catalog includes `us-tornado-safety`, a text-only conversion
of the National Weather Service page [“What to Do During a
Tornado”](https://www.weather.gov/safety/tornado-during). The source page was
accessed 2026-11-04. The converted text is
`payload/content-packs/us-tornado-safety/nws-tornado-safety.txt`; its header
identifies the source, access date, omitted page elements, non-endorsement,
and no-live-alert limits. NOAA's [content reuse
guidance](https://www.noaa.gov/office-education/outreach-communication/faq)
says nearly all NOAA content is public domain unless otherwise noted, requires
attribution, and forbids implied endorsement or misrepresentation. The source
page displayed NOAA/NWS attribution and no third-party credits when checked.
This is an engineering content review, not legal clearance for commercial
release. The reference is narrow tornado guidance, not first aid, a warning
service, or a complete severe-weather guide.

## Local AI models and generated answers

The current customer candidate includes Qwen3 1.7B Q4_K_M as the selected
CPU chat model, Qwen3 0.6B Q4_K_M as fallback, and Nomic Embed Text v1.5 for
embeddings. The installed hardware selector selected the CPU 1.7B model in the
acceptance VM and validated generation. Their pinned model-layer checksums and
license sources are listed in `/opt/fieldos/models/manifest.json`; license
texts are available in `/usr/share/doc/fieldos/models/`.

AI answers are generated output, not authoritative reference documents. They
can be incomplete or incorrect. Open the underlying reference article and
check its source and revision information. FieldOS includes CDC water/food documents and NWS-based tornado, flood,
hurricane, and winter-storm references, plus a narrow NIOSH heat-illness first
aid reference and a regional vegetable production handbook. The core library
is not comprehensive. Do not rely on AI as medical,
emergency, or safety guidance.

## NIOSH heat-illness first-aid reference

An independently transferable, text-only pack transcribes NIOSH Publication
2024-100, *Heat Stress: First Aid for Heat Illness* (October 2023). The exact
[CDC Stacks record](https://stacks.cdc.gov/view/cdc/138337) marks the item
Public Domain. Its original photographs credited to iStock and Thinkstock and
CDC agency marks are omitted; source text is retained with layout normalized.
CDC reuse guidance requires source attribution, a no-endorsement disclaimer,
unchanged substantive text, and notice that the source is available without
charge. The transcription preserves those conditions in its header. The text
is 6,593 bytes; SHA-256
`51c4b1f22ce0d7402ce02c05d436bd4e92e132d5c3b04e930cfc794d6a3c3165`. This
is a narrow, worker-focused source, not a clinical review, general first-aid
manual, or substitute for current emergency direction. The exact CDC use terms
are at <https://www.cdc.gov/other/agencymaterials.html>.

## Regional vegetable production reference

The core source set includes the unmodified 2026 Southeastern U.S. Vegetable
Crop Handbook (3,991,344 bytes; SHA-256
`f7b07e9d630a39a998d0ed5da717a73cd3de5306773695b4d83b16f1ddd27e9c`). The
publisher says the handbook was last revised January 2026 and covers crop
varieties, planting dates, soils and fertilizer, pest management, irrigation,
postharvest handling, and food safety. Virginia Cooperative Extension permits
public use, reprinting, and citation when credit is given to the authors,
Virginia Cooperative Extension, Virginia Tech, and Virginia State University.
The original PDF and all contributor/photo credits are preserved. Its regional
recommendations may not fit every Tennessee farm; it is not a complete
agriculture or livestock manual. Source and reuse terms:
<https://www.pubs.ext.vt.edu/AREC/AREC-66/AREC-66.html>.

## Optional CDC emergency-health checklist

The optional `us-basic-emergency-health` pack contains CDC's 2019 one-page
*Prepare Your Health: Practical Skills* checklist. The original is unmodified,
294,644 bytes, SHA-256
`f29fe3dd877b45c11c4a752a783af2aad965339a695137573c4445a5d8b97966`. The
exact CDC STACKS item is marked Public Domain. It identifies practical skills
to learn but does not teach first-aid procedures. Its source metadata and CDC
attribution are in the installed manifest and Source Library.

## CDC private-well emergency guidance (unattended test ISO)

The FieldOS source tree contains a text-only rendition of CDC's *How to Disinfect
Wells After an Emergency*, dated May 29, 2025. The file is 15,338 bytes with
SHA-256 `d8a05f9568a60c1e568869018e0ec769cae3a0bf13260765cc8f6edbee8e09a6`.
It preserves CDC warnings, tables, and follow-up testing information, and
excludes the page photograph and navigation. CDC's agency-materials policy
requires attribution, a non-endorsement notice, no substantive changes, and a
notice that the source is available from CDC at no charge. The pack manifest
records these terms and links to the exact source:
<https://www.cdc.gov/water-emergency/about/how-to-disinfect-wells-after-an-emergency.html>.
The document stresses that well work is hazardous, recommends a qualified well
or pump contractor, and says fuel or toxic chemical contamination is not made
safe by boiling or disinfection. The pack is included in the `d04f450`
unattended test ISO and its clean no-NIC E2E passed; it is not in the separately
tested interactive customer ISO `5abae15`. Legal review for commercial FieldOS
distribution and all other payload items remains open.

## Software notices

Payloads built from a source revision with the container notice-collection
step include `CONTAINER-IMAGES.md` and candidate copyright/license files under
`/usr/share/doc/fieldos/container-images/`. Per-image indexes record the image
digest, original layer path, and file checksum. This aids review but is not
complete license clearance: some images may carry no filename-matched notices,
and corresponding source or license-specific offers may still be required.
The release record identifies the source revision and known unresolved
obligations. Older installed payloads may not contain the candidate indexes.
Identified corresponding-source packages are listed in
`/usr/share/doc/fieldos/source-offers.json` and included under
`/usr/share/doc/fieldos/source-offers/` in payloads built from a revision that
implements those offers. Check the release record for the exact verified
contents.

## Additional packs

The content-pack format supports independently sourced and licensed additions.
The statewide Tennessee map is included in the customer candidate. The next
core payload adds the 2026 vegetable handbook and NIOSH heat-illness text; the
exact ISO that contains them must pass its own acceptance run. Packs require separate source, redistribution,
and field-use review. GPS integration and broader wildlife, outdoor, livestock,
food-preservation, and emergency references remain incomplete.
