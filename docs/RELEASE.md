# Release status and process

FieldOS is under active integration testing. A successful ISO build is not a
release; release status requires the installed-system checks below and retained
test evidence. Do not distribute an image until licensing and attribution review
is complete for every bundled package, container, model, and reference dataset.

## Current evidence (2026-11-02)

- Offline APT dependency resolution passed in an `ubuntu:26.04` container with
  networking disabled. The local package index installed the required Docker,
  Compose, curl, zstd, and QEMU guest agent packages.
- `make check` and `make test` passed (11 tests). Compose configuration
  validation passed.
- An installed test guest with no network adapter completed first-boot
  provisioning. Direct checks passed for N.O.M.A.D. health, local Ollama chat
  generation, embedding generation, Kiwix catalog/search, PMTiles range
  retrieval and map assets, and blocked container external egress. The services
  passed two consecutive guest reboots. Logs are retained under
  `build/e2e/20261102T174250Z-1936778/`.
- That run's automated report failed because its harness checked provisioning
  completion before first boot had finished. The manual checks above are
  recorded as evidence; they are not an automated acceptance PASS.
- A corrected fresh `make test-e2e` run is in progress. Until its report is
  PASS, the offline acceptance test remains incomplete.
- Hardware profile selection has fixture coverage; CPU inference was exercised
  in the installed guest. No physical GPU or accelerated backend was validated.
- No customer-facing interactive ISO has completed a separate installation
  test. No release ISO is currently published.
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

- The automated E2E run is still in progress; do not represent acceptance as
  passed until its report is available.
- Map verification so far exercised the map style, tile endpoint, tile bytes,
  and sprite assets; a rendered browser view has not been captured.
- GPU acceleration is unvalidated. CPU is the tested inference backend.
- Redistribution review for all bundled third-party software and content is
  pending.
