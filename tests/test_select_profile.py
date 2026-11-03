import json
import unittest
from pathlib import Path

from hardware.select_profile import profile_for, select


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "models/manifest.json").read_text())
SMALL = "qwen3-0.6b-q4_k_m"


class ProfileSelectionTests(unittest.TestCase):
    def test_profile_bands(self):
        self.assertEqual(profile_for(4), "minimal")
        self.assertEqual(profile_for(8), "lightweight")
        self.assertEqual(profile_for(16), "standard")
        self.assertEqual(profile_for(32), "accelerated")
        self.assertEqual(profile_for(64), "high_performance")

    def test_low_memory_is_reference_only(self):
        result = select({"memory_gib": 4, "gpus": []}, MANIFEST, {SMALL})
        self.assertIsNone(result["chat_model"])
        self.assertIsNone(result["embedding_model"])

    def test_small_model_selected_when_it_fits(self):
        result = select({"memory_gib": 8, "gpus": []}, MANIFEST, {SMALL})
        self.assertEqual(result["chat_model"], SMALL)
        self.assertEqual(result["chat_backend"], "cpu")

    def test_fallback_uses_largest_bundled_model_that_fits(self):
        small = SMALL
        medium = "qwen3-1.7b-q4_k_m"
        large = "qwen3-4b-instruct-2507-q4_k_m"
        result = select({"memory_gib": 8.5, "gpus": []}, MANIFEST, {small, medium, large})
        self.assertEqual(result["chat_model"], medium)
        self.assertEqual(result["fallback_model_ids"], [small])

    def test_missing_payload_model_is_never_selected(self):
        result = select({"memory_gib": 64, "gpus": []}, MANIFEST, set(), available_embedding_ids=set())
        self.assertIsNone(result["chat_model"])

    def test_gpu_requires_explicit_backend_validation(self):
        hw = {"memory_gib": 16, "gpus": [{"vendor": "nvidia", "vram_gib": 16,
                                           "driver_available": True, "cuda": True}]}
        cpu_only = select(hw, MANIFEST, {SMALL})
        cuda_tested = select(hw, MANIFEST, {SMALL}, {"cpu", "cuda"})
        self.assertEqual(cpu_only["chat_backend"], "cpu")
        self.assertEqual(cuda_tested["chat_backend"], "cuda")

    def test_validated_vulkan_can_use_reported_shared_memory_budget(self):
        hw = {"memory_gib": 5.5, "gpus": [{
            "vendor": "intel", "driver_available": True, "vram_gib": 0,
            "vulkan_memory_budget_gib": 2.5,
        }]}
        not_validated = select(hw, MANIFEST, {SMALL}, {"cpu"})
        validated = select(hw, MANIFEST, {SMALL}, {"cpu", "vulkan"})
        self.assertIsNone(not_validated["chat_model"])
        self.assertEqual(validated["chat_model"], SMALL)
        self.assertEqual(validated["chat_backend"], "vulkan")

    def test_cpu_fallback_requires_cpu_support_in_manifest(self):
        gpu_only_manifest = dict(MANIFEST)
        gpu_only_manifest["chat_models"] = [
            dict(MANIFEST["chat_models"][0], backends=["cuda"])
        ]
        result = select({"memory_gib": 16, "gpus": []}, gpu_only_manifest, {SMALL}, {"cpu"})
        self.assertIsNone(result["chat_model"])

    def test_backend_uses_its_own_driver_and_vram(self):
        hw = {"memory_gib": 16, "gpus": [
            {"vendor": "amd", "vram_gib": 24, "driver_available": True},
            {"vendor": "nvidia", "vram_gib": 1, "driver_available": True},
        ]}
        selected = select(hw, MANIFEST, {SMALL}, {"cpu", "cuda"})
        self.assertEqual(selected["chat_backend"], "cpu")

    def test_manual_override_must_fit_and_be_bundled(self):
        bigger = "qwen3-4b-instruct-2507-q4_k_m"
        too_small = select({"memory_gib": 8, "gpus": []}, MANIFEST, {SMALL, bigger}, manual_model=bigger)
        missing = select({"memory_gib": 64, "gpus": []}, MANIFEST, {SMALL}, manual_model=bigger)
        self.assertIsNone(too_small["chat_model"])
        self.assertIsNone(missing["chat_model"])


if __name__ == "__main__":
    unittest.main()
