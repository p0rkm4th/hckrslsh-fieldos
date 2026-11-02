import unittest
from unittest.mock import patch

from hardware.detect.detect import cpu_facts, memory_gib


class DetectionTests(unittest.TestCase):
    @patch("hardware.detect.detect.read_text", return_value="model name : Example CPU\nflags : avx avx2 sse4_2")
    def test_cpu_capabilities_are_filtered(self, _):
        result = cpu_facts()
        self.assertEqual(result["model"], "Example CPU")
        self.assertEqual(result["instruction_sets"], ["avx", "avx2", "sse4_2"])

    @patch("hardware.detect.detect.read_text", return_value="MemTotal:       8388608 kB")
    def test_memory_conversion(self, _):
        self.assertEqual(memory_gib(), 8.0)


if __name__ == "__main__":
    unittest.main()
