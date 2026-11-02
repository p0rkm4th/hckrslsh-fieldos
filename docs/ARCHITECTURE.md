# Architecture

## Base and upstream

- x86-64 Ubuntu 26.04.1 LTS Desktop, official live installer.
- Project N.O.M.A.D. v1.35.1, upstream commit
  `0dbbd21c2f470975e86131c497694c147ca8bc00` (Apache-2.0).
- Ollama for local inference, with independently selected chat and embedding
  models. N.O.M.A.D. remains the central interface; no competing UI is added.
- Kiwix ZIM content and ProtoMaps-compatible map data remain separate,
  checksummed payloads with their own attribution and redistribution review.
- Optional QGIS and GPS support are not required for the first test image.

## Installer and first boot

The installer must use explicit user account credentials, provide optional
full-disk encryption through Ubuntu's supported installer path, and require
explicit target-disk selection/erasure confirmation. Provisioning is
idempotent and consumes only local package, container, model, and content
payloads. It never performs a hidden network fetch. A local systemd unit
completes provisioning after installation and before presenting the N.O.M.A.D.
launcher. Failure of optional hardware or payloads leaves a usable desktop and
reports a local diagnostic rather than blocking login.

## Hardware adaptation

`hardware/detect/` reports CPU, memory, graphics, storage, battery, and GPS
capabilities as JSON. `hardware/select_profile.py` applies a declarative model
manifest, reserving memory for the OS and selecting the highest-priority model
that fits known RAM/VRAM and backend constraints. Missing or uncertain GPU
information falls back to CPU. A short load/inference check can fall back to
the next compatible bundled model. Embeddings are selected independently.

## Offline payload boundary

The ISO build assembles a manifest-verified payload: package dependencies,
pinned N.O.M.A.D. and service images, Ollama runtime, at least one legally
redistributable chat model and embedding model, a small ZIM, and a small map
fixture. The test image contains one small tier; the full edition uses an
installer plus an automatically recognized offline payload partition when
the resulting image exceeds practical USB-media limits. Large outputs and
download caches stay out of Git.

## Trust boundaries

N.O.M.A.D. requires Docker control of local services. Its management interface
therefore binds to localhost by default. No remote exposure, telemetry,
credentials, or online update is required for initial use. Upstream updates
are opt-in and reviewed as versioned changes to the manifests.

## Current integration constraint

Upstream v1.35.1's documented setup wizard downloads container images, models,
ZIMs, maps, and other content. FieldOS must stage these in advance and seed
N.O.M.A.D.'s documented storage/runtime paths or provide a local image/content
source. Until the boot/install/offline acceptance tests pass, the upstream UI
and individual service integrations are not considered a completed appliance.
