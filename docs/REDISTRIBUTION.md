# Redistribution review

## Decision

**The current ISO is for private testing only. Do not publish or distribute it.**
This document records an engineering review of the current test payload; it is
not a legal opinion or a substitute for counsel's review.

The reviewed candidate is R3, SHA-256
`e07f39a20e64fc1127086739afce39fbbffc12220f8cff126509072c32f7e899`.
Its build modifies the Ubuntu desktop ISO by adding FieldOS payload,
provisioning files, and a GRUB entry. It retains Ubuntu branding. Canonical's
IP rights policy says redistribution of modified Ubuntu versions associated
with Ubuntu trademarks must be approved/certified/provided by Canonical;
otherwise the marks must be removed/replaced and source rebuilt. No such
approval or debranding has been completed. This is a release blocker independent
of the open-source licenses of individual Ubuntu packages.

## Current artifact inventory

| Artifact | Recorded terms and source | Evidence in payload | Open release review |
|---|---|---|---|
| Ubuntu 26.04.1 Desktop ISO | Original ISO URL and SHA-256 are in `payload/manifests/ubuntu-26.04.1-desktop-amd64.json`; Canonical IPR policy: <https://ubuntu.com/legal/intellectual-property-policy> | Original ISO retained as build input | Resolve Ubuntu trademark/modified-image permission; inventory notices for every redistributed Ubuntu package and confirm source/offer obligations. |
| Offline APT packages | Requested package set is in `package-request.json`; the reviewed payload contains 61 resolved `.deb` packages | Local audit inventory `/mnt/shared/fieldos-e2e/package-license-audit-20261102/packages.json` records package identity and archive hashes. The matching `notice-files.json` records size and SHA-256 for 59 extracted copyright notices, retained under `notices/`. `libatomic1` and `libpython3.14-stdlib` have no bundled copyright path. Debian control metadata supplies no license field for these packages. | This is provenance and notice evidence, not an SPDX/license determination. Review every notice and source/offer obligation; investigate packages without bundled notices before release. |
| N.O.M.A.D. image | Apache-2.0; upstream release source: <https://github.com/Crosstalk-Solutions/project-nomad/tree/v1.35.1> | Pinned OCI digest and upstream license text | Inspect the exact image's SBOM and all bundled third-party notices. |
| MySQL image | GPL-2.0 with MySQL's additional permissions; upstream licensing information: <https://github.com/mysql/mysql-server/blob/8.0/LICENSE> | Pinned OCI digest | Verify exact image version/layers, third-party component notices, and corresponding source/offer requirements. |
| Redis image | Manifest currently labels `redis:7-alpine` BSD-3-Clause | Pinned OCI digest | Verify the exact Redis version and Alpine/transitive components for this digest; do not infer terms from the mutable tag alone. |
| Dozzle, Ollama, Qdrant, Kiwix images | Direct licenses are recorded in `payload/manifests/images.json` and upstream links in `CONTAINER-IMAGES.md` | Pinned OCI digests | Generate/review SBOMs for the exact images; include transitive notices and any corresponding source required by the applicable licenses. |
| Qwen3 0.6B chat model | Apache-2.0 model page: <https://huggingface.co/Qwen/Qwen3-0.6B> | `models/manifest.json` pins the Ollama manifest SHA-256 and quantized model-layer SHA-256/size. The payload builder verifies both before archiving and emits `manifests/model-payload.json`. | Confirm all non-model Ollama layers and upstream source provenance match the reviewed model; exact upstream source revision remains to be documented. |
| Nomic Embed Text v1.5 | Apache-2.0 model page: <https://huggingface.co/nomic-ai/nomic-embed-text-v1.5> | `models/manifest.json` pins the Ollama manifest SHA-256 and model-layer SHA-256/size. The payload builder verifies both before archiving and emits `manifests/model-payload.json`. | Confirm all non-model Ollama layers and upstream source provenance match the reviewed model; exact upstream source revision remains to be documented. |
| Miniature Wikipedia ZIM | Wikimedia text licensing/attribution terms: <https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use> | ZIM is copied from Project N.O.M.A.D. v1.35.1; a general CC BY-SA attribution notice is included | Inspect the ZIM metadata and article notices; add exact archive version, source, size, SHA-256, license URI/text, and a practical attribution path in the installed UI. Wikimedia content can include media with separate licenses. |
| Protomaps world and U.S. PMTiles | Protomaps states its basemap is an ODbL Produced Work and requires OSM attribution: <https://docs.protomaps.com/basemaps/downloads>; ODbL text: <https://opendatacommons.org/licenses/odbl/1-0/> | Build key, bounds, zoom, size/checksum for generated maps; OSM/Protomaps attribution is present in the map UI and payload notices | Archive the applicable ODbL text and verify the exact build's attribution and derivative database obligations before distribution. |
| Project N.O.M.A.D. Maps assets | Upstream source README and license/OFL notices are carried in the generated payload | Source commit pinned during build | Confirm notices cover every bundled sprite/font/asset and their exact source revisions. |

## Required actions before a public/customer release

1. Resolve Canonical's trademark/modified Ubuntu image requirement, or build a
   compliant debranded derivative and retest it.
2. Review the preserved Ubuntu package archive inventory and generate a
   reproducible license/SBOM inventory for the exact package closure and each
   pinned OCI image, including transitive licenses, copyright notices, source
   availability, and license-specific source offers.
3. Add per-file SHA-256, version/source revision, and license identifiers for
   the bundled model blobs and ZIM, then verify that the attribution is visible
   and usable offline.
4. Preserve exact map, sprite, and font attributions and license text in the
   installed system.
5. Have the final notices and distribution method reviewed before publishing
   any ISO or offline payload.

The public Git repository contains source and these review findings only; the
test ISO and binary payload remain unpublished.
