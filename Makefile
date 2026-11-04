PYTHON ?= python3
UBUNTU_ISO ?=
ISO ?=
FIELDOS_STORAGE_ROOT ?= $(if $(wildcard /mnt/shared),/mnt/shared,$(CURDIR)/build)
FIELDOS_E2E_ROOT ?= $(FIELDOS_STORAGE_ROOT)/fieldos-e2e
FIELDOS_PAYLOAD_ROOT ?= $(if $(wildcard /mnt/shared),/mnt/shared/fieldos-payload,$(CURDIR)/build/payload)
FIELDOS_WORK_ROOT ?= $(FIELDOS_STORAGE_ROOT)/fieldos-build
FIELDOS_OUTPUT_ROOT ?= $(FIELDOS_STORAGE_ROOT)/fieldos-releases
export FIELDOS_E2E_ROOT FIELDOS_PAYLOAD_ROOT FIELDOS_WORK_ROOT FIELDOS_OUTPUT_ROOT
export UBUNTU_ISO FIELDOS_TEST_CONTENT_PACK

.PHONY: check test test-e2e cleanup-test-disk payload content-packs iso-test iso-full verify validate-content-packs

check: validate-content-packs
	$(PYTHON) -m compileall -q build hardware installer/provisioning payload scripts tests
	bash -n scripts/*.sh build/*.sh installer/provisioning/*.sh

validate-content-packs:
	$(PYTHON) payload/validate_content_packs.py

test:
	$(PYTHON) -m unittest discover -s tests -v

test-e2e:
	$(PYTHON) tests/test_e2e.py

cleanup-test-disk:
	@test -n "$(DISK)" || (echo 'Set DISK to one exact completed E2E guest.qcow2 path' >&2; exit 2)
	$(PYTHON) scripts/retire_test_disk.py --disk "$(DISK)" $(if $(filter 1,$(DELETE)),--delete --reason "$(REASON)",)

payload:
	./build/prepare-payload.sh

content-packs:
	$(PYTHON) build/build_content_packs.py --catalog payload/manifests/content-packs.json \
	  --output-root "$(FIELDOS_PAYLOAD_ROOT)"

iso-test:
	@test -n "$(UBUNTU_ISO)" || (echo 'Set UBUNTU_ISO to the verified Ubuntu 26.04.1 Desktop ISO' >&2; exit 2)
	./build/build-iso.sh test "$(UBUNTU_ISO)"

iso-full:
	@test -n "$(UBUNTU_ISO)" || (echo 'Set UBUNTU_ISO to the verified Ubuntu 26.04.1 Desktop ISO' >&2; exit 2)
	./build/build-iso.sh full "$(UBUNTU_ISO)"

verify:
	@test -n "$(ISO)" || (echo 'Set ISO to the FieldOS artifact to inspect' >&2; exit 2)
	./build/verify-iso.sh "$(ISO)"
