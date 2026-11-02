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
