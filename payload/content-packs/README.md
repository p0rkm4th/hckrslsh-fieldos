# Staged offline content packs

Each independently versioned pack belongs in its own directory:

```text
payload/content-packs/<pack-id>/
├── manifest.json
└── <artifacts named by the manifest>
```

Add its relative manifest path to `payload/manifests/content-packs.json` only
after the exact sources, licenses, and attribution have been reviewed. The
validator checks manifest fields, path containment, declared sizes, and SHA-256
values; it does not establish that a license grants redistribution rights.
First-aid/emergency packs must identify authoritative references and record
their reviewer and content revision date. No pack is currently approved or
included in a distributable payload.
