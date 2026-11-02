# Release process

1. Pin Ubuntu media, N.O.M.A.D. source/container digests, service images,
   packages, models, and content in manifests.
2. Run `make check`, `make test`, then build test/full media from a clean
   workspace with documented inputs.
3. Verify boot metadata and all embedded checksums.
4. Boot the test ISO under UEFI QEMU, install to a disposable disk, reboot,
   exercise UI/AI/reference/maps, disconnect all networking, and repeat after
   a second reboot.
5. Record exact host/tool versions, artifacts, SHA-256, test logs, and
   untested physical hardware.
6. Publish source and release metadata to the private GitHub repository.
   Upload large ISO/payload artifacts to an approved artifact destination;
   do not commit them to ordinary Git history.

No artifact is called a release until all applicable steps are evidenced.

## Current local build (2026-11-02)

- `build/out/fieldos-test.iso` is 11.1 GiB. SHA-256:
  `c2589409eba6589a3f38711ce0007250423a2ba175aea96b2549c63f07d74fb1`.
- `build/payload/offline-payload.tar.zst` is 5.11 GiB. SHA-256:
  `b2628e89368d9a6664360e8c22dd75a69b743a77675e45fcf9356ad562225763`.
- `make check`, `make test` (8 tests), Compose config validation, and
  `make verify` pass. The ISO has BIOS and UEFI boot records and boots to the
  Ubuntu installer in a UEFI QEMU VM with networking disabled.
- The installer detects an 80 GiB disposable VM disk. End-to-end installation
  has not yet completed; no installed-service, AI, reference, map, persistence,
  or post-install offline result is claimed.
- The repository has one local scaffold commit. GitHub SSH authentication is
  verified for `p0rkm4th`, but the requested private repository does not exist
  and the available GitHub connection cannot create repositories. Nothing has
  been pushed or published.
