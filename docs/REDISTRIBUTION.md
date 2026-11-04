# Redistribution review

## Decision

**The current ISO is for private testing only. Do not publish or distribute it.**
This document records an engineering review of the current test payload; it is
not a legal opinion or a substitute for counsel's review.

Canonical's official IPRights Policy was rechecked on 2026-11-04. It permits
modified Ubuntu for personal/internal use. For redistribution, it requires
Canonical approval/certification/provision when Ubuntu marks remain; otherwise
the policy says to remove/replace those marks and recompile. This candidate
still contains Ubuntu branding. No Canonical permission or complete debranding
is recorded. See [Canonical's IPRights Policy](https://ubuntu.com/legal/intellectual-property-policy).

The current unpublished customer test candidate is
`/mnt/shared/fieldos-releases/fieldos-customer-regional-3054c59.iso`,
12,007,178,240 bytes, SHA-256
`522abcbc4ba04593ce7d1813af43c5c86110b22a41239c13c3e9800f017d1686`. Its source
revision is `3054c59fe38295d54a316b4da22088582a23d3bc`. A fresh interactive
customer-mode install, local service checks, offline operation, actual browser
map and Kiwix checks, and two consecutive reboots passed in a disposable UEFI
VM. Evidence is in
`/mnt/shared/fieldos-e2e/customer-regional-3054c59-20261104/report.md`. It
remains a private engineering artifact, not a release: Ubuntu branding remains,
and complete notice, trademark, source-offer, model, map, and content reviews
are outstanding. The no-NIC tests establish operation and file integrity, not
redistribution rights. Do not distribute the ISO or payload until the reviews
below are done.

## Current artifact inventory

| Artifact | Recorded terms and source | Evidence in payload | Open release review |
|---|---|---|---|
| Ubuntu 26.04.1 Desktop ISO | Original ISO URL and SHA-256 are in `payload/manifests/ubuntu-26.04.1-desktop-amd64.json`; Canonical IPR policy: <https://ubuntu.com/legal/intellectual-property-policy> | Original ISO retained as build input | Resolve Ubuntu trademark/modified-image permission; inventory notices for every redistributed Ubuntu package and confirm source/offer obligations. |
| Offline APT packages | The current source requests Docker, Compose, curl, zstd, qemu-guest-agent, and `vulkan-tools` from Ubuntu 26.04; package archive metadata is generated with the payload. | The current offline acceptance at source `3054c59` completed firstboot from its bundled APT payload; reports: `/mnt/shared/fieldos-e2e/20261104T112428Z-3477254/report.md` and `/mnt/shared/fieldos-e2e/customer-regional-3054c59-20261104/report.md`. | The detailed package-license inventory predates the current payload and must be regenerated/reviewed for the exact release artifact, including notices, trusted source metadata, and corresponding-source obligations. The E2E pass proves offline installation, not redistribution clearance. `vulkan-tools` Ubuntu package details: <https://packages.ubuntu.com/resolute/amd64/vulkan-tools>. |
| N.O.M.A.D. image | Project N.O.M.A.D. is Apache-2.0; upstream release source: <https://github.com/Crosstalk-Solutions/project-nomad/tree/v1.35.1> | Pinned OCI digest; all-layer SBOM and candidate notice inventory are retained under `/mnt/shared/fieldos-e2e/repository-review-233b980/`. The pinned image includes Debian `ghostscript`, `libgs10`, and `libgs10-common` version `10.0.0~dfsg-11+deb12u8`; `/usr/share/doc/ghostscript/copyright` identifies AGPL-3+. The current candidate's payload hash matches the prepared archive, whose file list includes `manifests/source-offers.json` and the three checksum-pinned Ghostscript source-offer files. | Review the bundled source offer and its notice, verify the signer trust chain, review its dependencies and all other SBOM components, and finish license-specific offer analysis. |
| MySQL image | GPL-2.0 with MySQL's additional permissions; upstream licensing information: <https://github.com/mysql/mysql-server/blob/8.0/LICENSE> | Pinned OCI digest | Verify exact image version/layers, third-party component notices, and corresponding source/offer requirements. |
| Redis image | The pinned image config reports `REDIS_VERSION=7.4.12`; Redis's [official licensing overview](https://redis.io/legal/licenses/) lists 7.4.x as RSALv2 or SSPLv1, not BSD-3-Clause. The earlier [licensing-change announcement](https://redis.io/blog/redis-adopts-dual-source-available-licensing/) records the change. | Local image ID matches the pinned digest in `payload/manifests/images.json`; `REDIS_VERSION` was read from the image config. Read-only image inspection is retained at `/mnt/shared/fieldos-e2e/redis-license-image-inspect-20261103.txt`. | Redis's licensing overview describes RSALv2 as allowing distribution while prohibiting commercializing the software or providing it as a managed service that exposes Redis functionality; SSPLv1 has source obligations when providing a service. Applicability to a FieldOS appliance sold or distributed to customers is not determined here. Obtain license-specific review or evaluate Valkey, then rebuild and acceptance-test the offline payload. Valkey compatibility with pinned N.O.M.A.D. and the replacement image's own transitive licenses are unverified. |
| Dozzle, Ollama, Qdrant, Kiwix images | Direct licenses are recorded in `payload/manifests/images.json` and upstream links in `CONTAINER-IMAGES.md` | Pinned OCI digests | Generate/review SBOMs for the exact images; include transitive notices and any corresponding source required by the applicable licenses. |
| Qwen3 0.6B chat model | Apache-2.0 model page: <https://huggingface.co/Qwen/Qwen3-0.6B> | `models/manifest.json` pins the Ollama manifest SHA-256 and quantized model-layer SHA-256/size. The payload builder verifies both before archiving and emits `manifests/model-payload.json`. | Confirm all non-model Ollama layers and upstream source provenance match the reviewed model; exact upstream source revision remains to be documented. |
| Nomic Embed Text v1.5 | Apache-2.0 model page: <https://huggingface.co/nomic-ai/nomic-embed-text-v1.5> | `models/manifest.json` pins the Ollama manifest SHA-256 and model-layer SHA-256/size. The payload builder verifies both before archiving and emits `manifests/model-payload.json`. | Confirm all non-model Ollama layers and upstream source provenance match the reviewed model; exact upstream source revision remains to be documented. |
| Miniature Wikipedia ZIM | Wikimedia text terms: <https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use>; CC BY-SA 4.0 text is bundled | `payload/manifests/references.json` pins Project N.O.M.A.D. v1.35.1 commit `0dbbd21c2f470975e86131c497694c147ca8bc00`, exact archive size `4537782`, and SHA-256 `2811724b72fd34a0728c28b7456d3d6866579019fbbe7ffe28528f3450c252db`; direct upstream download matched the candidate bytes. Current guest's source/license documents match the repo checksums. | Archive-level provenance and attribution are present; article/media-level license review remains open. |
| Protomaps world and U.S. PMTiles | Protomaps states its basemap is an ODbL Produced Work and requires OSM attribution: <https://docs.protomaps.com/basemaps/downloads>; ODbL text: <https://opendatacommons.org/licenses/odbl/1-0/> | Source and current candidate include the official ODbL text at `payload/licenses/ODbL-1.0.txt` (SHA-256 `607680718977f6f6c9607972afd98f208573f19251315ed1362a8589b51beaf5`) and install it under `/usr/share/doc/fieldos/`; the payload and installed copies were verified in the current guest. Map build key, bounds, zoom, size/checksum and UI attribution are also recorded. | The current unattended guest compared bundled and installed ODbL text hashes; the interactive candidate uses the same pinned payload. Repeat exact-image verification and review the derivative database and displayed attribution before any distribution. |
| Project N.O.M.A.D. Maps assets | Upstream source README and license/OFL notices are carried in the generated payload | Source commit pinned during build | Confirm notices cover every bundled sprite/font/asset and their exact source revisions. |

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
   matches for Redis, Dozzle, or Kiwix does not mean those images have no notice
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
