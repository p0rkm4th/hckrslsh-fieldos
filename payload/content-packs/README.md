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
their reviewer and content revision date. The repository catalog currently
contains six core packs: CDC water/food references, NWS-based FieldOS summaries
for tornadoes, hurricanes/winter storms, and floods, a NIOSH heat-illness
reference, and a Southeastern vegetable production handbook. It also contains
two optional CDC preparedness items: a one-page emergency-health skills
orientation (not procedural first-aid instruction) and a two-page emergency
kit checklist. The optional household communications planner is FieldOS
authored and categorized separately from authoritative emergency guidance. Only packs
listed in `core_packs` are embedded in the installer. The build also produces
independent versioned archives for every listed pack, including core packs, so
they can be transferred and installed on an existing system. Other planned
specialist and regional packs are not yet populated.

`make content-packs` validates the catalog and writes separate
`<id>-<version>.tar.zst` and `.sha256` files under
`FIELDOS_PAYLOAD_ROOT/content-packs/`. `make payload` invokes the same builder.
On an installed system, the
bundled `fieldos-content-packs.py install` command verifies and stores a pack
version immutably below `/var/lib/fieldos/content-packs/`; `list` shows
installed versions. A pack with target `storage/maps/pmtiles` and exactly one
PMTiles artifact is additionally copied atomically into N.O.M.A.D.'s existing
map directory. N.O.M.A.D. discovers `.pmtiles` files there and exposes their
sources in its map style automatically. Conflicting filenames are preserved
and reported as errors. Other pack targets remain storage-only until an
application adapter is implemented.
