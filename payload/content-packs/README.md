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
their reviewer and content revision date. The repository catalog remains empty;
optional packs are built separately and are not embedded in the customer ISO.

`make content-packs` validates the catalog and writes separate
`<id>-<version>.tar.zst` and `.sha256` files under
`FIELDOS_PAYLOAD_ROOT/content-packs/`. `make payload` invokes the same builder.
These optional bundles are outside the core ISO. On an installed system, the
bundled `fieldos-content-packs.py install` command verifies and stores a pack
version immutably below `/var/lib/fieldos/content-packs/`; `list` shows
installed versions. A pack with target `storage/maps/pmtiles` and exactly one
PMTiles artifact is additionally copied atomically into N.O.M.A.D.'s existing
map directory. N.O.M.A.D. discovers `.pmtiles` files there and exposes their
sources in its map style automatically. Conflicting filenames are preserved
and reported as errors. Other pack targets remain storage-only until an
application adapter is implemented.
