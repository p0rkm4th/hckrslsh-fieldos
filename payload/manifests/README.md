`maps.json` declares the deterministic sample-region extraction from the
bundled Protomaps world archive. It pins the source build key and checks its
upstream metadata instead of selecting a mutable latest build. Model manifests
pin and verify both the Ollama manifest and exact quantized model layer before
payload creation. The generated payload also records checksums
and sizes for the source archive and extracted region. Other package, container,
model, map, and reference payload records identify their version, source,
SHA-256, size, and license/attribution. Binary payloads and caches are never
committed to Git.
