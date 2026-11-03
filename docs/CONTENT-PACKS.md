# Modular offline content packs

FieldOS keeps reference content independent from the core installer wherever
possible. The repository defines a versioned JSON manifest schema at
`payload/manifests/content-pack.schema.json` and a catalog at
`payload/manifests/content-packs.json`. The catalog is intentionally empty:
the architecture is ready, but customer-specific pack content awaits source,
requirements, licensing, and attribution review.

Staged pack directories use `payload/content-packs/<pack-id>/manifest.json`
with artifact paths relative to that pack. The catalog lists relative paths to
those manifests. Run `make validate-content-packs` to check catalog references,
required metadata, safe artifact paths, declared size and SHA-256, geographic
bounds, and emergency-reference review fields. The validator does not decide
whether a license permits redistribution; a human review is still required
before adding a pack to a distributable build.

Planned pack categories are:

- Agriculture, farming, soils, and equipment reference
- Wildlife, camping, and overlanding
- Water treatment and food preservation
- First aid and emergency reference
- Regional maps, GPS, and GIS data

Each populated pack has its own stable ID and version. Its manifest records
each source and URL, license and attribution, every artifact's size and
SHA-256, and installation target and requirements. Geographic packs also
declare bounds, coordinate reference system, and zoom range. Build tooling
validates sizes and checksums before packaging. `make content-packs` builds one
deterministic `.tar.zst` archive and SHA-256 sidecar per catalog entry under
`FIELDOS_PAYLOAD_ROOT/content-packs/`, independently of the core installer.
Archives contain the manifest and only the artifacts it declares, so stray
or unreviewed files in a staging directory are excluded.
`make payload` runs this builder after preparing the core payload. The current
catalog is empty, so these commands produce no pack archives today. The core
ISO includes the manifest schema and pack management command, but does not
embed optional pack archives.

On an installed system, verify and add a bundle with:

```sh
sudo /opt/fieldos/scripts/fieldos-content-packs.py install /path/to/pack-1.0.tar.zst
/opt/fieldos/scripts/fieldos-content-packs.py list
```

Installation checks the sidecar checksum, rejects unsafe archive entries,
validates the manifest and artifact hashes, checks available space, and stores
each immutable version under `/var/lib/fieldos/content-packs/<id>/<version>`.
Repeating the same install is safe; a different bundle cannot overwrite an
existing version. It stages on the destination filesystem and atomically moves
the verified version into place, so its free-space check accounts for one
unpacked copy plus a 256 MiB reserve. The command does not erase existing user data. This first
stage provides independent packaging, integrity checking, and local storage;
it does not yet import or activate content in N.O.M.A.D., Kiwix, the map UI, or
GIS applications. The manifest's `installation.target` and `requirements`
describe intended integration and are not automatically executed. Consumer
adapters and their end-to-end tests remain future work.

## Reference quality and retrieval

Manifest `authority` distinguishes authoritative references from community
material, AI-generated material, or a mixture. Retrieval should preserve the
originating document title and source attribution with each result and make
the original passage accessible. AI-generated responses are summaries, not
source documents. This distinction is essential for first-aid and emergency
material; those packs require a named, reviewable authority and revision date
before inclusion. No content is currently being represented as an approved
emergency library.

## Mapping and location

The present world and sample U.S. PMTiles fixtures cover zoom levels 0 through
5. They render in the acceptance VM but lack the detail required for
turn-by-turn, trail, parcel, or field work. Higher-resolution regional maps,
their storage budgets, source licenses, and update process need to be
specified before expanding release scope. GPS/GIS support needs a defined
hardware interface and offline behavior. The current detector only reports a
likely GPS device node; it does not read coordinates or provide a navigation
service. The pack schema already has geographic bounds and zoom metadata to
support later work. Protomaps supports extracting bounded regional PMTiles
archives and selecting a maximum zoom, so future regional packs can be built
without changing the core image ([PMTiles CLI documentation](https://docs.protomaps.com/pmtiles/cli)).
The current zoom-5 archives remain orientation fixtures; Protomaps documents
zoom 15 as sufficient for street-level mapping
([PMTiles creation guide](https://docs.protomaps.com/pmtiles/create)). This is
a planning reference, not a commitment to include zoom-15 data.

For GPS, `gpsd` is a possible future local interface for supported USB/serial
receivers. It can normalize several receiver protocols for local clients
([gpsd documentation](https://gpsd.io/README.html)). It is not selected or
bundled; hardware, permissions, offline behavior, and whether its local socket
can be kept inaccessible from the LAN need validation first.

Do not populate a pack from a public download until redistribution terms and
attribution have been reviewed for the exact artifact and derivative format.
Public availability alone is not permission to redistribute.
For OpenStreetMap-derived content, preserve the required attribution and
ODbL notices ([OpenStreetMap copyright and license](https://www.openstreetmap.org/copyright)).
