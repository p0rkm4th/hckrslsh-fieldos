# FieldOS offline content sources and limits

This is the source and attribution guide for the current test payload. It is
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
from pinned Protomaps build `20261102.pmtiles`. A fresh no-NIC E2E and a
separate interactive customer installation visibly rendered eight Tennessee
locations; reports and screenshots are listed in `docs/RELEASE.md`. It is a
local geographic reference, not turn-by-turn navigation, GPS positioning,
trail guidance, or emergency advice. The map interface attributes
OpenStreetMap contributors and Protomaps. The full ODbL 1.0 text is at
`/usr/share/doc/fieldos/ODbL-1.0.txt`; the attribution notice and source-build
details are alongside it and in the map interface. The ODbL applies to the
database rights; individual content may have additional rights.

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

The test payload includes Qwen3 0.6B Q4_K_M for chat and Nomic Embed Text v1.5
for embeddings. Their pinned model-layer checksums and license sources are
listed in `/opt/fieldos/models/manifest.json`; license texts are available in
`/usr/share/doc/fieldos/models/`.

AI answers are generated output, not authoritative reference documents. They
can be incomplete or incorrect. Open the underlying reference article and
check its source and revision information. FieldOS includes CDC water/food
documents and NWS-based tornado, flood, hurricane, and winter-storm references.
An optional NIOSH heat-illness first-aid text pack can be installed from
removable media, but it is narrow, worker-focused, and has not had clinical
review. The core library is not comprehensive. Do not rely on AI as medical,
emergency, or safety guidance.

## Optional NIOSH heat-illness reference

An independently transferable, text-only pack transcribes NIOSH Publication
2024-100, *Heat Stress: First Aid for Heat Illness* (October 2023). The exact
[CDC Stacks record](https://stacks.cdc.gov/view/cdc/138337) marks the item
Public Domain. Its original photographs credited to iStock and Thinkstock and
CDC agency marks are omitted; source text is retained with layout normalized.
The original is available without charge from the linked record. This is a
narrow, worker-focused source, not a clinical review, a general first-aid
manual, or current emergency direction. The pack is optional and is not
included in the customer ISO. Its installed manifest provides the artifact
checksum and full attribution.

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
The statewide Tennessee map is included in the current customer candidate.
The Southeastern vegetable handbook and NIOSH heat-illness text are optional
packs and are not in that ISO. Packs require separate source, redistribution,
and field-use review. GPS integration and broader wildlife, outdoor, livestock,
food-preservation, and emergency references remain incomplete.
