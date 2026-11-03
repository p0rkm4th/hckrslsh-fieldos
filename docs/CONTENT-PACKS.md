# Modular offline content packs

FieldOS keeps reference content independent from the core installer wherever
possible. The repository defines a versioned JSON manifest schema at
`payload/manifests/content-pack.schema.json` and a catalog at
`payload/manifests/content-packs.json`. The catalog is intentionally empty: the architecture is ready, but customer-specific pack content awaits requirements and license/attribution review. One external Middle Tennessee map bundle has passed transfer, validation, activation, actual browser rendering, and two-reboot persistence checks; it remains a test artifact outside the catalog and core ISO.

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
`make payload` runs this builder after preparing the core payload. The public
catalog remains empty so the customer ISO stays bounded; optional archives
are built separately and are not embedded in the core image. An independently
staged Middle Tennessee candidate is described below and stored outside Git
pending final customer content and redistribution review.

On an installed system, verify and add a bundle with:

```sh
sudo /opt/fieldos/scripts/fieldos-content-packs.py install /path/to/pack-1.0.tar.zst
sudo /opt/fieldos/scripts/fieldos-content-packs.py list
```

Installation checks the sidecar checksum, rejects unsafe archive entries,
validates the manifest and artifact hashes, checks available space, and stores
each immutable version under `/var/lib/fieldos/content-packs/<id>/<version>`.
Repeating the same install is safe; a different bundle cannot overwrite an
existing version. For a map pack whose target is `storage/maps/pmtiles`, the
installer additionally requires exactly one PMTiles archive and atomically
publishes it in `/var/lib/fieldos/storage/maps/pmtiles/`. N.O.M.A.D. discovers
that file in its region inventory and generates its map source automatically.
Existing filenames are never replaced. Other targets currently remain
storage-only. A failed validation or conflicting destination leaves existing
application data untouched.

The test harness accepts `FIELDOS_TEST_CONTENT_PACK=/path/to/bundle.tar.zst`.
It places that archive and checksum on a second, read-only ISO attached to the
disposable no-NIC VM, imports it from inside the installed guest, then checks
N.O.M.A.D.'s region and style APIs, PMTiles reads, browser map rendering, and
persistence after reboots. This transfer medium is test-only and does not
change the customer installer.

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

The bundled world and sample U.S. PMTiles fixtures cover zoom levels 0 through
5 and remain suitable only for broad orientation. A separate test candidate
covers Middle Tennessee around Nashville (bounding box `-88.5,35.4,-85.7,36.7`)
at zoom levels 0–13. Its 19.6 MB PMTiles file was extracted from the 2026-11-02
Protomaps build using bounded HTTP range requests and includes road and land-use
detail. Its manifest records the source URL, date, size, SHA-256, ODbL Produced
Work license, attribution, bounds, and zoom range. It is not currently bundled
in the customer ISO or approved as a release artifact. The E2E import and browser checks passed on source `43ec3f9faed73632c13a8113b546ade9b5bf488e`; the retained report is `/mnt/shared/fieldos-e2e/20261103T222621Z-2749281/report.md`, and `map-render.png` shows Nashville roads at zoom 13. The 19.6 MB archive (SHA-256 `9dce859a72d3b13afa1235838cbfddabfcf8c8cdd741b90fa4b0dec4dcb024a9`) is a test artifact only, not an approved public release pack.

This map is a geographic reference, not turn-by-turn navigation, trail,
parcel, or emergency guidance. GPS/GIS support needs a defined hardware
interface and offline behavior. The current detector only reports a likely GPS
device node; it does not read coordinates or provide a navigation service.
Protomaps supports bounded regional extraction from its hosted archives
([PMTiles CLI documentation](https://docs.protomaps.com/pmtiles/cli)).
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
