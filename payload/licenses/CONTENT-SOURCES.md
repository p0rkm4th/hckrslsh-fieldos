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

The test payload includes a global Protomaps basemap and a small United States
sample extracted from it. The data is limited to zoom levels 0–5 and is for
broad orientation and software testing; it does not provide detailed roads,
trails, parcels, or field navigation. The map interface attributes
OpenStreetMap contributors and Protomaps. The attribution and ODbL 1.0 notice
are in `/usr/share/doc/fieldos/` and in the map interface.

## Local AI models and generated answers

The test payload includes Qwen3 0.6B Q4_K_M for chat and Nomic Embed Text v1.5
for embeddings. Their pinned model-layer checksums and license sources are
listed in `/opt/fieldos/models/manifest.json`; license texts are available in
`/usr/share/doc/fieldos/models/`.

AI answers are generated output, not authoritative reference documents. They
can be incomplete or incorrect. Open the underlying reference article and
check its source and revision information. FieldOS currently ships no reviewed
first-aid or emergency reference pack; do not rely on the AI as medical,
emergency, or safety guidance.

## Additional packs

The content-pack format supports independently sourced and licensed additions.
No customer-specific packs are currently approved or included. Higher-zoom
regional maps, GPS integration, and additional agriculture, outdoor, water,
food-preservation, and emergency references require separate source,
redistribution, and field-use review.
