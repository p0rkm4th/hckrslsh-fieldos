# Offline content and redistribution

Every bundled artifact needs a stable version or digest, source URL, size,
checksum, and redistribution/license record. Do not bundle content with
unclear or non-redistributable terms. The build fails closed when a required
artifact is missing or its checksum differs.

The current test payload contains Project N.O.M.A.D.'s miniature English
Wikipedia ZIM, a low-zoom global Protomaps extract named `nomad.pmtiles`,
Ollama Qwen3 0.6B Q4_K_M for chat, and `nomic-embed-text:v1.5` for embeddings.
The ZIM's Wikipedia content is CC BY-SA; map data is an ODbL Produced Work
derived from OpenStreetMap. Notices are included in the payload. Model licensing
is evaluated independently from the Ollama runtime. The full edition may add
openly licensed models, public-domain manuals, and user-selected geographic
packs; it must not include proprietary manuals or restricted datasets.

Model candidates are tracked in `models/manifest.json`. Content and package
inputs are tracked in `payload/manifests/`; license texts and attributions live
under `payload/licenses/`. An artifact is not approved merely because its
download endpoint is public.
