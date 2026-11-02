# Offline content and redistribution

Every bundled artifact needs a stable version or digest, source URL, size,
checksum, and redistribution/license record. Do not bundle content with
unclear or non-redistributable terms. The build fails closed when a required
artifact is missing or its checksum differs.

The initial test payload is intended to include one small Project Gutenberg
or public-domain reference, one compact N.O.M.A.D.-compatible ZIM, a tiny
OpenStreetMap-derived map fixture with ODbL attribution, one Ollama chat model,
and a separate embedding model. Model licensing is evaluated independently
from the Ollama runtime. The full edition may include additional openly
licensed models, public-domain manuals, and user-selected geographic packs;
it must not include proprietary manuals or restricted datasets.

Model candidates are tracked in `models/manifest.json`. Content and package
inputs are tracked in `payload/manifests/`; license texts and attributions live
under `payload/licenses/`. An artifact is not approved merely because its
download endpoint is public.
