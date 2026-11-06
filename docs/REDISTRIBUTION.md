# Redistribution review

## Decision

**The current ISO is for private testing only. Do not publish or distribute it.**
This document records an engineering review of the current test payload; it is
not a legal opinion or a substitute for counsel's review.

Canonical's current IPRights Policy was checked on 2026-11-06. It says
unmodified Ubuntu may be redistributed. A modified Ubuntu image that retains
Canonical trademarks requires Canonical approval, certification, or provision;
otherwise the trademarks must be removed/replaced and the source recompiled to
create new binaries. This FieldOS image is modified and retains Ubuntu marks;
no Canonical permission or complete debranding is recorded. See [Canonical's
IPRights Policy](https://canonical.com/legal/intellectual-property-policy).

The exact current customer candidate reviewed here is
`/mnt/shared/fieldos-releases/fieldos-customer-test-aedc570.iso`, SHA-256
`538ad22a3f024a173196bd9d18953b4a16c492cecc2338bf90d0bd028cccfab6`, source
`aedc5705915d4ff57bad18e535b602eace7310b8`. Its embedded manifest pins the
Ubuntu input and prepared payload checksums. Structural verification,
interactive no-NIC UEFI installation, firstboot, actual local application
checks, and two reboots passed in a disposable VM. Evidence is linked from
[`VALIDATION-CURRENT.md`](VALIDATION-CURRENT.md) and
`/mnt/shared/fieldos-e2e/customer-aedc570-interactive/customer-acceptance.md`.
These functional results do not clear the ISO or payload for redistribution.

The current payload includes the CDC-authored private-well text pack; the
pack's manifest records its source, date, checksum, text-only scope, CDC
attribution, non-endorsement, and no-charge notice. Its public-domain basis is
an engineering inference from CDC's general agency-materials policy, not an
item-specific rights label, and commercial redistribution clearance remains
open. Exact CDC Stacks records identify several other CDC documents as Public
Domain, but that alone does not resolve reuse of CDC/HHS logos or agency marks.
The exact illustrated PDFs in the CDC packs were visually reviewed and found to
contain CDC/HHS marks; some also contain photographs or graphics whose separate
reuse terms were not established. The current source revision removes those
five PDFs from the tracked pack artifacts and replaces them with text-only
extractions. The currently accepted `aedc570` ISO predates that update and still
contains the illustrated PDFs, so that ISO remains unsuitable for distribution
without rights clearance. Older public Git commits also retain historical PDF
blobs; repository history was not rewritten. The Wikipedia ZIM, Ubuntu marks,
all container transitive components (including the Valkey image layers), map
assets, model terms, notices, and source offers still have unresolved review
items. This is an engineering rights assessment, not legal advice or full
commercial distribution clearance. Do not publish or distribute the candidate
until those reviews are resolved.

### CDC PDF asset inspection — 2026-11-06

All pages of the five CDC PDFs staged in the original pack revision were
rendered and visually inspected: *Prepare Your Health: Practical Skills*;
*Keep Calm and Be Prepared*; *10 Dangerous Food Safety Mistakes*; *Make Water
Safe During an Emergency*; and *Eat Safe Food after a Power Outage*. Each
contains visible CDC or CDC/HHS agency marks. The *Practical Skills* page also
contains a CPR photograph; the food-safety mistakes PDF contains a family
photograph and multiple graphics; the remaining documents contain infographic
artwork. This inspection did not establish independent reuse terms for every
photograph or graphic. Exact Stacks Public Domain labels for some documents do
not by themselves settle reuse of agency marks under CDC's
[separate policy](https://www.cdc.gov/other/agencymaterials.html).
Therefore the exact illustrated PDFs are **not cleared for redistribution**
based on this review. The current tracked manifests now bundle only text files
for these four packs. Their updated, versioned archives passed integrity checks
and contain no PDF members. The text files were checked for the obvious
encoding/duplication errors observed in the CDC food-safety extracts; no
substantive safety instructions or numeric values were intentionally changed.
The `aedc570` installer has not been rebuilt or tested with these updates, so
no claim is made that an installed FieldOS uses the revised packs. Their
archives passed checksum, member, and temporary-root Source Library activation
checks. Full desktop import, reboot persistence, fresh ISO acceptance, and final
rights review remain open before distribution.

## Current artifact inventory

The historical `f250cc1` ISO contains Redis `7.4.12` (RSALv2 or SSPLv1) and is
not the current candidate. The current `aedc570` customer ISO pins Valkey
`8.0.12`; it passed interactive offline installation and two reboot checks,
and the separate unattended E2E from descendant source `31a244c` also exercised
Valkey. Those tests establish function, not distribution clearance. The
historical ISO's contents and status are unchanged.


| Artifact | Recorded terms and source | Evidence in payload | Open release review |
|---|---|---|---|
| Ubuntu 26.04.1 Desktop ISO | Original ISO URL and SHA-256 are in `payload/manifests/ubuntu-26.04.1-desktop-amd64.json`; Canonical IPR policy: <https://ubuntu.com/legal/intellectual-property-policy> | Original ISO retained as build input | Resolve Ubuntu trademark/modified-image permission; inventory notices for every redistributed Ubuntu package and confirm source/offer obligations. |
| Offline APT packages | The `562fee9` customer ISO installed its offline APT set, including Docker, Compose, curl, zstd, qemu-guest-agent, `vulkan-tools`, `zenity`, and `pkexec`. Package archive metadata is generated with the payload. | Firstboot completed in the customer candidate at `/mnt/shared/fieldos-e2e/customer-searchable-562fee9/validation.md`. | Review the detailed package-license inventory for the exact release artifact, including notices, trusted source metadata, and corresponding-source obligations. Offline tests prove installation, not redistribution clearance. Ubuntu's Resolute package records identify `zenity` as graphical dialog support and `pkexec` as PolicyKit-authorized command execution: <https://packages.ubuntu.com/resolute/zenity>, <https://packages.ubuntu.com/resolute/pkexec>. |
| N.O.M.A.D. image | Project N.O.M.A.D. is Apache-2.0; upstream release source: <https://github.com/Crosstalk-Solutions/project-nomad/tree/v1.35.1> | Pinned OCI digest; all-layer SBOM and candidate notice inventory are retained under `/mnt/shared/fieldos-e2e/repository-review-233b980/`. The pinned image includes Debian `ghostscript`, `libgs10`, and `libgs10-common` version `10.0.0~dfsg-11+deb12u8`; `/usr/share/doc/ghostscript/copyright` identifies AGPL-3+. The current candidate's payload hash matches the prepared archive, whose file list includes `manifests/source-offers.json` and the three checksum-pinned Ghostscript source-offer files. | Review the bundled source offer and its notice, verify the signer trust chain, review its dependencies and all other SBOM components, and finish license-specific offer analysis. |
| MySQL image | GPL-2.0 with MySQL's additional permissions; upstream licensing information: <https://github.com/mysql/mysql-server/blob/8.0/LICENSE> | Pinned OCI digest | Verify exact image version/layers, third-party component notices, and corresponding source/offer requirements. |
| Redis 7.4.12 in the historical `f250cc1` ISO | Redis Community Edition 7.4.x: [official licensing overview](https://redis.io/legal/licenses/) lists RSALv2 or SSPLv1, not BSD-3-Clause. | This exact ISO contains digest `sha256:8da19c7399dca900c6822a1cf30f9d2285585e2c4b457ff4095b0f4500054d3f`; version `7.4.12` was observed in image config. | This ISO is not cleared for customer/commercial distribution. Source `129da89` replaces Redis with a pinned Valkey image; the current candidate uses Valkey and remains subject to full license review. |
| Valkey 8.0.12 | [Valkey upstream](https://github.com/valkey-io/valkey), BSD-3-Clause; [migration guide](https://valkey.io/topics/migration/). | Pinned digest `sha256:19f0b3d350f5e6de618086d79ecdc9c474ab159bebb16ed95a92e4211562fee5`; isolated Compose client test plus `aedc570` interactive install/two-reboot acceptance and descendant `31a244c` unattended E2E. | Review all image layers/notices and validate upgrade behavior while preserving legacy Redis data. Redis 7.4 data files are not compatible with Valkey. |
| Dozzle, Ollama, Qdrant, Kiwix images | Direct licenses are recorded in `payload/manifests/images.json` and upstream links in `CONTAINER-IMAGES.md` | Pinned OCI digests | Generate/review SBOMs for the exact images; include transitive notices and any corresponding source required by the applicable licenses. |
| Qwen3 0.6B chat model | Apache-2.0 model page: <https://huggingface.co/Qwen/Qwen3-0.6B> | `models/manifest.json` pins the Ollama manifest SHA-256 and quantized model-layer SHA-256/size. The payload builder verifies both before archiving and emits `manifests/model-payload.json`. | Confirm all non-model Ollama layers and upstream source provenance match the reviewed model; exact upstream source revision remains to be documented. |
| Qwen3 1.7B Q4_K_M chat model | Ollama reports Apache-2.0; model card: <https://ollama.com/library/qwen3/tags> | Pulled from `qwen3:1.7b-q4_K_M`; manifest SHA-256 `8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7`, model layer SHA-256 `3d0b790534fe4b79525fc3692950408dca41171676ed7e21db57af5c65ef6ab6` (1,359,279,776 bytes). Ollama's license layer hash matches the 0.6B model. Current `562fee9` customer guest selected it on CPU and generated a response after two reboots. CPU evaluation is recorded at `/mnt/shared/fieldos-model-eval-20261105/benchmark.json`. | Review exact model provenance, complete Ollama-layer license terms, and notices for public distribution; the model/runtime licensing inventory is not closed. |
| Nomic Embed Text v1.5 | Apache-2.0 model page: <https://huggingface.co/nomic-ai/nomic-embed-text-v1.5> | `models/manifest.json` pins the Ollama manifest SHA-256 and model-layer SHA-256/size. The payload builder verifies both before archiving and emits `manifests/model-payload.json`. | Confirm all non-model Ollama layers and upstream source provenance match the reviewed model; exact upstream source revision remains to be documented. |
| Miniature Wikipedia ZIM | Wikimedia text terms: <https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use>; CC BY-SA 4.0 text is bundled | `payload/manifests/references.json` pins Project N.O.M.A.D. v1.35.1 commit `0dbbd21c2f470975e86131c497694c147ca8bc00`, exact archive size `4537782`, and SHA-256 `2811724b72fd34a0728c28b7456d3d6866579019fbbe7ffe28528f3450c252db`; direct upstream download matched the candidate bytes. Current guest's source/license documents match the repo checksums. | Archive-level provenance and attribution are present; article/media-level license review remains open. |
| MedlinePlus First Aid summary | NLM reuse policy: <https://medlineplus.gov/about/using/usingcontent/>; source page: <https://medlineplus.gov/firstaid.html> | 3,086-byte text snapshot of the health-topic page summary last updated 2026-07-22. Artifact SHA-256 `32cc39ebdff811dd08e6ca2550a432a8b1d436c304e899162d742a18a0829893`; pack archive and validation are recorded in `docs/CONTENT-PACKS.md`. NLM policy expressly identifies health-topic summaries as public domain; this artifact excludes linked pages and all images/media. | Attribution and exact source scope are recorded in the manifest. This is a U.S. rights assessment, not a clinical review or international rights determination. The 8c81d64 guest contains the pack at `/var/lib/fieldos/content-packs/us-medlineplus-first-aid/2026.07.22/`. |
| CDC Keep Calm and Be Prepared checklist | Exact CDC STACKS item record: <https://stacks.cdc.gov/view/cdc/23954> | Historical pack `1.0.0` included the 138,605-byte PDF (SHA-256 `d8d3ad68df32f5c069968e5f71d58e2e03bd3751e985877f28122a988388f319`) and was installed in an earlier VM. Current source pack `1.0.1` omits the PDF and provides a text-only extraction. | Current text-only source excludes visible CDC/HHS marks and artwork; its rebuilt archive and temporary-root activation are checked, but no guest or ISO acceptance has been run for `1.0.1`. This checklist names preparedness skills but is not medical or first-aid instruction. |
| CDC private-well emergency guidance | CDC *How to Disinfect Wells After an Emergency*, May 29, 2025: <https://www.cdc.gov/water-emergency/about/how-to-disinfect-wells-after-an-emergency.html>; CDC reuse policy: <https://www.cdc.gov/other/agencymaterials.html> | 15,338-byte text rendition, SHA-256 `d8a05f9568a60c1e568869018e0ec769cae3a0bf13260765cc8f6edbee8e09a6`; included in the `f250cc1` and `129da89` candidate payloads and their acceptance runs. | Text-only rendition excludes photograph and page navigation, preserving warnings and table values. Manifest records CDC attribution, non-endorsement, free-source notice, and no substantive edits. The CDC policy has exceptions for third-party material and urges periodic update checks. This is an engineering review; commercial redistribution clearance remains open. |
| Protomaps Tennessee, world, and U.S. PMTiles | Protomaps states its basemap is an ODbL Produced Work and requires OSM attribution: <https://docs.protomaps.com/basemaps/downloads>; ODbL text: <https://opendatacommons.org/licenses/odbl/1-0/> | The 8c81d64 guest contains the official ODbL text (SHA-256 `607680718977f6f6c9607972afd98f208573f19251315ed1362a8589b51beaf5`). Its map screen visibly shows `MapLibre | Protomaps © OpenStreetMap` and a collapsed attribution-info icon. Statewide bounds, zoom, size, and checksum are recorded in `CONTENT-SOURCES.md` and the acceptance evidence. | Review the derivative database and confirm the contributor and ODbL details in the collapsed map attribution disclosure are practically accessible before distribution. |
| Project N.O.M.A.D. Maps assets | Upstream source README, font OFL, and Tangrams-derived sprite notices are carried in the generated payload | Source commit pinned during build; exact Tangrams MIT notice copied to `licenses/project-nomad-maps/TANGRAMS-ICONS-MIT.txt` from upstream license commit `d7e160177365e00532d36e35e689727b97eb6be1` | The notice applies to Tangrams-derived sprite components; upstream does not identify the exact artwork revision or per-file provenance. Verify the notice in a rebuilt payload and resolve asset provenance before distribution. |

## Required actions before a public/customer release

1. Resolve Canonical's trademark/modified Ubuntu image requirement by obtaining
   written permission or completing a scoped debranding/rebuild and then
   reviewing the resulting image. No permission or debranding is claimed here.
2. Review the preserved Ubuntu package archive inventory and complete a
   reproducible license/SBOM inventory for the exact installed Ubuntu package
   closure and each pinned OCI image. An initial all-layer SPDX 2.3 scan of the
   seven pinned Compose images is preserved at
   `/mnt/shared/fieldos-e2e/repository-review-233b980/`; it catalogues 2,619
   package and 44,903 file entries. Syft emitted declared-license metadata for
   2,137 packages and concluded-license fields for 179, so manual review of
   missing metadata, transitive notices, source availability, and license-
   specific source offers remains necessary. An all-layer notice extraction
   from the seven exact pinned images found 1,174 unique candidate notice files
   (2,367 layer/path occurrences; 11.45 MB). It is filename-based, so zero
   matches for Valkey, Dozzle, or Kiwix does not mean those images have no notice
   obligations. The current candidate's payload was built with the source
   collector and source-offer changes; confirm all notices and source files
   again whenever its payload is rebuilt.

   The exact Project N.O.M.A.D. image's installed Debian packages and
   copyright metadata establish that Ghostscript
   `10.0.0~dfsg-11+deb12u8` is present and identifies AGPL-3+. Its Debian `.dsc`
   signature verified as cryptographically good and both source archive
   hashes/sizes match the signed descriptor. The signing key's trust chain was
   not established from a locally installed Debian keyring; that limit is
   recorded in `/mnt/shared/fieldos-e2e/repository-review-233b980/sources/ghostscript/verification.txt`.
   The source archives and exact image notice evidence are in the same
   `/mnt/shared/fieldos-e2e/repository-review-233b980/` directory. The source
   package is now checksum-pinned in `payload/manifests/source-offers.json` and
   future payload builds bundle it; it is not included in Git or the current
   ISO. The builder checks archive sizes and hashes against the committed
   manifest; separate trust-chain review of the Debian signing key is still
   outstanding.
3. Complete the entry-level media license review; archive-level metadata does
   not establish clearance for every embedded item. The current image includes
   the source/attribution guide and CC BY-SA text, and guest-side SHA-256
   matches passed.
4. Finish reviewing exact map, sprite, and font attribution coverage and
   corresponding license text in the installed system.
5. Have the final notices and distribution method reviewed before publishing
   any ISO or offline payload.

The public Git repository contains source and these review findings only; the
test ISO and binary payload remain unpublished.
