# Redistribution review

## Decision

**The current ISO is for private testing only. Do not publish or distribute it.**
This document records an engineering review of the current test payload; it is
not a legal opinion or a substitute for counsel's review.

The latest current-source test candidate is
`/mnt/shared/fieldos-releases/fieldos-test-customer-main-a4eebb8.iso`, size
11,956,584,448 bytes, SHA-256
`47fdf3f07773bb61f2bca321513f875ade39f6a01bf51afba98fb282529c3b28`. It was
built from source commit `a4eebb84be8667d061f20b34b8701aa169b66d3e`; later
commits changed documentation only. `make verify` passed ISO structure,
BIOS/UEFI boot record, installer configuration, and payload checks. A fresh
no-NIC QEMU installation passed interactive installation, clean media handoff,
firstboot, service checks, and two reboots. The guest's installed content
source and CC BY-SA license files matched the repository copies by SHA-256.
These are technical and integrity checks; they do not clear redistribution
rights. This candidate retains Ubuntu branding and is not approved for
distribution. Detailed installation evidence is in `docs/RELEASE.md` and
`/mnt/shared/fieldos-e2e/customer-iso-current-main-a4eebb8/report.md`.

R5, the preceding candidate, was built from
`fa0a2034044ac994fb2ea9663dc597da20aa2fa3`; its interrupted handoff is
historical evidence only. It was superseded by the current-source candidate.

Canonical's [IP rights policy](https://ubuntu.com/legal/intellectual-property-policy)
says modified Ubuntu versions associated with Ubuntu trademarks require
Canonical approval/certification/provision, or the trademarks must be removed
and the source rebuilt. No approval or debranding has been completed. This is a
release blocker independent of the open-source licenses of individual Ubuntu
packages. R3 (`e07f39a20e64fc1127086739afce39fbbffc12220f8cff126509072c32f7e899`)
is a historical candidate; its binary has been removed.

## Current artifact inventory

| Artifact | Recorded terms and source | Evidence in payload | Open release review |
|---|---|---|---|
| Ubuntu 26.04.1 Desktop ISO | Original ISO URL and SHA-256 are in `payload/manifests/ubuntu-26.04.1-desktop-amd64.json`; Canonical IPR policy: <https://ubuntu.com/legal/intellectual-property-policy> | Original ISO retained as build input | Resolve Ubuntu trademark/modified-image permission; inventory notices for every redistributed Ubuntu package and confirm source/offer obligations. |
| Offline APT packages | Requested package set is in `package-request.json`; the reviewed payload contains 61 resolved `.deb` packages | Local audit inventory `/mnt/shared/fieldos-e2e/package-license-audit-20261102/packages.json` records package identity and archive hashes. `notice-files.json` records size/SHA-256 for 59 bundled copyright notices. Follow-up in `source-notice-review.json` traces `libpython3.14-stdlib` to its same-version companion notice and `libatomic1` to GCC source copyright; the GCC source tar checksum matches its `.dsc`, but that descriptor's signature could not be verified with the available keyring. | This is provenance and notice evidence, not an SPDX/license determination. Verify trusted source metadata, review every notice and source/offer obligation, and complete exact package licensing/SBOM analysis before release. |
| N.O.M.A.D. image | Apache-2.0; upstream release source: <https://github.com/Crosstalk-Solutions/project-nomad/tree/v1.35.1> | Pinned OCI digest and upstream license text | Inspect the exact image's SBOM and all bundled third-party notices. |
| MySQL image | GPL-2.0 with MySQL's additional permissions; upstream licensing information: <https://github.com/mysql/mysql-server/blob/8.0/LICENSE> | Pinned OCI digest | Verify exact image version/layers, third-party component notices, and corresponding source/offer requirements. |
| Redis image | Manifest currently labels `redis:7-alpine` BSD-3-Clause | Pinned OCI digest | Verify the exact Redis version and Alpine/transitive components for this digest; do not infer terms from the mutable tag alone. |
| Dozzle, Ollama, Qdrant, Kiwix images | Direct licenses are recorded in `payload/manifests/images.json` and upstream links in `CONTAINER-IMAGES.md` | Pinned OCI digests | Generate/review SBOMs for the exact images; include transitive notices and any corresponding source required by the applicable licenses. |
| Qwen3 0.6B chat model | Apache-2.0 model page: <https://huggingface.co/Qwen/Qwen3-0.6B> | `models/manifest.json` pins the Ollama manifest SHA-256 and quantized model-layer SHA-256/size. The payload builder verifies both before archiving and emits `manifests/model-payload.json`. | Confirm all non-model Ollama layers and upstream source provenance match the reviewed model; exact upstream source revision remains to be documented. |
| Nomic Embed Text v1.5 | Apache-2.0 model page: <https://huggingface.co/nomic-ai/nomic-embed-text-v1.5> | `models/manifest.json` pins the Ollama manifest SHA-256 and model-layer SHA-256/size. The payload builder verifies both before archiving and emits `manifests/model-payload.json`. | Confirm all non-model Ollama layers and upstream source provenance match the reviewed model; exact upstream source revision remains to be documented. |
| Miniature Wikipedia ZIM | Wikimedia text terms: <https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use>; CC BY-SA 4.0 text is bundled | `payload/manifests/references.json` pins Project N.O.M.A.D. v1.35.1 commit `0dbbd21c2f470975e86131c497694c147ca8bc00`, exact archive size `4537782`, and SHA-256 `2811724b72fd34a0728c28b7456d3d6866579019fbbe7ffe28528f3450c252db`; direct upstream download matched the candidate bytes. Current guest's source/license documents match the repo checksums. | Archive-level provenance and attribution are present; article/media-level license review remains open. |
| Protomaps world and U.S. PMTiles | Protomaps states its basemap is an ODbL Produced Work and requires OSM attribution: <https://docs.protomaps.com/basemaps/downloads>; ODbL text: <https://opendatacommons.org/licenses/odbl/1-0/> | Build key, bounds, zoom, size/checksum for generated maps; OSM/Protomaps attribution is present in the map UI and payload notices | Archive the applicable ODbL text and verify the exact build's attribution and derivative database obligations before distribution. |
| Project N.O.M.A.D. Maps assets | Upstream source README and license/OFL notices are carried in the generated payload | Source commit pinned during build | Confirm notices cover every bundled sprite/font/asset and their exact source revisions. |

## Required actions before a public/customer release

1. Resolve Canonical's trademark/modified Ubuntu image requirement, or build a
   compliant debranded derivative and retest it.
2. Review the preserved Ubuntu package archive inventory and complete a
   reproducible license/SBOM inventory for the exact installed Ubuntu package
   closure and each pinned OCI image. An initial all-layer SPDX 2.3 scan of the
   seven pinned Compose images is preserved at
   `/mnt/shared/fieldos-e2e/repository-review-233b980/`; it catalogues 2,619
   package and 44,903 file entries. Syft emitted declared-license metadata for
   2,137 packages and concluded-license fields for 179, so manual review of
   missing metadata, transitive notices, source availability, and license-
   specific source offers remains necessary.
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
