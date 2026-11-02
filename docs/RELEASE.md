# Release status and process

FieldOS is under active integration testing. A successful ISO build is not a
release; release status requires the installed-system checks below and retained
test evidence. Do not distribute an image until licensing and attribution review
is complete for every bundled package, container, model, and reference dataset.

## Current evidence (2026-11-02)

- Automated offline install acceptance passed in run
  `build/e2e/20261102T175415Z-1942621/report.md` from source revision
  `e0fb066`. It installed Ubuntu to a fresh 80 GiB qcow2 with no virtual NIC,
  completed local APT and container provisioning, validated N.O.M.A.D., Ollama
  chat and embedding, Kiwix search, real PMTiles tile retrieval and renderer
  configuration, blocked container egress, then repeated service checks after
  two reboots. Chat returned `FIELDOS_ACCEPTANCE_OK` and Kiwix search retrieved
  the New York Times article. The full guest logs and report are retained beside
  the disposable VM disk.
- Offline APT dependency resolution passed in an `ubuntu:26.04` container with
  networking disabled. The local package index installed the required Docker,
  Compose, curl, zstd, and QEMU guest agent packages.
- `make check` and `make test` passed (11 tests). Compose configuration
  validation passed.
- The customer-facing interactive test ISO was built at
  `build/out/fieldos-test.iso`, SHA-256
  `790fd21725e45ecb4625c313a87f8dcf58c811f29c31e919fb4ee4825205c834`.
  `make verify` and `sha256sum -c build/out/fieldos-test.iso.sha256` passed;
  BIOS and UEFI El Torito boot entries were present. A separate isolated VM
  booted its GRUB menu and reached Ubuntu's interactive disk setup screen. The
  observed screen evidence is under
  `build/e2e/customer-ui-20261102T180430Z/`. Installation was not confirmed from
  this interactive ISO.
- Hardware profile selection has fixture coverage; CPU inference was exercised
  in the installed guest. No physical GPU or accelerated backend was validated.
- The browser did not render a captured map view. The E2E test verified map
  style configuration, an actual tile response and bundled map assets, so map
  rendering remains a partial verification.
- Redistribution review for bundled third-party software, models, and content
  is still pending. No release ISO is published.
- The GitHub repository is public at
  [p0rkm4th/hckrslsh-fieldos](https://github.com/p0rkm4th/hckrslsh-fieldos).

## Release gate

1. Run `make check`, `make test`, and `make test-e2e`; retain the human-readable
   report and logs. The E2E test must install to a disposable VM disk with no
   network adapter and pass service, inference, retrieval, map, and two-reboot
   checks.
2. Build the customer-facing interactive ISO only after the test ISO passes.
   Verify BIOS/UEFI boot structure, embedded payload/checksums, interactive disk
   selection and credentials, and install that ISO separately to a disposable
   VM disk.
3. Review redistribution terms and attribution for Ubuntu packages, container
   images, models, and offline datasets. Record any restrictions in the release
   manifest.
4. Publish a manifest with source revision, build inputs/tool versions, ISO and
   payload SHA-256 checksums, test results, known limitations, and installation
   instructions. Keep ISO, model weights, generated credentials, VM disks, and
   downloaded container archives out of Git history.

The expanded/full ISO must wait until the test release satisfies these gates.

## Known limitations

- The automated acceptance script passed, but its map checks do not capture a
  browser-rendered view.
- The customer-facing interactive ISO reached disk setup in a separate VM but
  has not completed a separate installation.
- GPU acceleration is unvalidated. CPU is the tested inference backend.
- Redistribution review for all bundled third-party software and content is
  pending.
