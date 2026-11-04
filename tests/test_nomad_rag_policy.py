import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "installer/provisioning/patch_nomad_rag_policy.py"
SPEC = importlib.util.spec_from_file_location("patch_nomad_rag_policy", MODULE_PATH)
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)


class NomadRagPolicyTests(unittest.TestCase):
    def fixture(self, block):
        return "const prompt = `\\nHOW TO ANSWER:\\n" + block + "\\n\\nFormat using markdown`;\n"

    def test_replaces_upstream_general_knowledge_fallback_with_fail_closed_policy(self):
        patched = POLICY.patch_prompt(self.fixture(POLICY.OLD_POLICY))
        self.assertIn(POLICY.NEW_POLICY, patched)
        self.assertNotIn("answer from your own general knowledge", patched)
        self.assertIn("do not give", patched)

    def test_is_idempotent(self):
        source = self.fixture(POLICY.NEW_POLICY)
        self.assertEqual(POLICY.patch_prompt(source), source)

    def test_refuses_unrecognized_upstream_prompt(self):
        with self.assertRaisesRegex(ValueError, "did not match exactly"):
            POLICY.patch_prompt("const prompt = 'upstream changed';")

    def test_refuses_ambiguous_duplicate_prompt(self):
        with self.assertRaisesRegex(ValueError, "old_policy=2"):
            POLICY.patch_prompt(self.fixture(POLICY.OLD_POLICY) * 2)

    def test_installs_deterministic_server_side_safety_guard(self):
        source = "class OllamaController { async chat() {\n" + POLICY.CONTROLLER_ANCHOR + "\n} }\n"
        patched = POLICY.patch_controller(source)
        self.assertIn("FieldOS has disabled AI-generated instructions", patched)
        self.assertIn("response.response.write", patched)
        self.assertIn(POLICY.CONTROLLER_ANCHOR, patched)

    def test_controller_patch_is_idempotent(self):
        source = "class OllamaController { async chat() {\n" + POLICY.CONTROLLER_ANCHOR + "\n} }\n"
        patched = POLICY.patch_controller(source)
        self.assertEqual(POLICY.patch_controller(patched), patched)

    def test_refuses_unrecognized_controller(self):
        with self.assertRaisesRegex(ValueError, "controller did not match exactly"):
            POLICY.patch_controller("class OllamaController {}")


if __name__ == "__main__":
    unittest.main()
