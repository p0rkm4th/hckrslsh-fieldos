PYTHON ?= python3
UBUNTU_ISO ?=
ISO ?=

.PHONY: check test test-e2e payload iso-test iso-full verify

check:
	$(PYTHON) -m compileall -q hardware installer/provisioning scripts tests
	bash -n scripts/*.sh build/*.sh

test:
	$(PYTHON) -m unittest discover -s tests -v

test-e2e:
	$(PYTHON) tests/test_e2e.py

payload:
	./build/prepare-payload.sh

iso-test:
	@test -n "$(UBUNTU_ISO)" || (echo 'Set UBUNTU_ISO to the verified Ubuntu 26.04.1 Desktop ISO' >&2; exit 2)
	./build/build-iso.sh test "$(UBUNTU_ISO)"

iso-full:
	@test -n "$(UBUNTU_ISO)" || (echo 'Set UBUNTU_ISO to the verified Ubuntu 26.04.1 Desktop ISO' >&2; exit 2)
	./build/build-iso.sh full "$(UBUNTU_ISO)"

verify:
	@test -n "$(ISO)" || (echo 'Set ISO to the FieldOS artifact to inspect' >&2; exit 2)
	./build/verify-iso.sh "$(ISO)"
