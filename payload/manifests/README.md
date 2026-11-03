`maps.json` declares the deterministic sample-region extraction from the
bundled Protomaps world archive. It pins the source build key and checks its
upstream metadata instead of selecting a mutable latest build. Model manifests
pin and verify both the Ollama manifest and exact quantized model layer before
payload creation. The generated payload also records checksums and sizes for
the source archive and extracted region. `references.json` pins the miniature
Wikipedia ZIM to its exact upstream commit and verifies its size and SHA-256
during payload preparation. Its archive-level metadata does not replace
per-article or media license review. Binary payloads and caches are never
committed to Git.
