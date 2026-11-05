import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ModelHandoffPackagingTests(unittest.TestCase):
    def test_iso_builder_bundles_the_firstboot_model_handoff_helper(self):
        builder = (ROOT / "build/build-iso.sh").read_text()
        self.assertIn(
            'install -m 0644 "$ROOT/hardware/nomad_initial_model.py" '
            '"$WORK/fieldos/hardware/nomad_initial_model.py"',
            builder,
        )

    def test_iso_verifier_requires_the_model_handoff_helper(self):
        verifier = (ROOT / "build/verify-iso.sh").read_text()
        self.assertIn("/fieldos/hardware/nomad_initial_model.py", verifier)
        self.assertIn("/fieldos/models/manifest.json", verifier)

    def test_builder_bundles_the_helper_manifest_input(self):
        builder = (ROOT / "build/build-iso.sh").read_text()
        self.assertIn(
            'install -m 0644 "$ROOT/models/manifest.json" '
            '"$WORK/fieldos/models/manifest.json"',
            builder,
        )


if __name__ == "__main__":
    unittest.main()
