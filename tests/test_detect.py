import unittest
from unittest.mock import patch

from pathlib import Path
from hardware.detect.detect import cpu_facts, gpu_facts, memory_gib


class DetectionTests(unittest.TestCase):
    @patch("hardware.detect.detect.read_text", return_value="model name : Example CPU\nflags : avx avx2 sse4_2")
    def test_cpu_capabilities_are_filtered(self, _):
        result = cpu_facts()
        self.assertEqual(result["model"], "Example CPU")
        self.assertEqual(result["instruction_sets"], ["avx", "avx2", "sse4_2"])

    @patch("hardware.detect.detect.read_text", return_value="MemTotal:       8388608 kB")
    def test_memory_conversion(self, _):
        self.assertEqual(memory_gib(), 8.0)

    @patch("hardware.detect.detect.run", return_value="")
    @patch("hardware.detect.detect.Path.glob", return_value=[Path("/sys/class/drm/card0/device")])
    @patch("hardware.detect.detect.read_text")
    def test_dedicated_gpu_memory_reports_available_vram(self, read, _glob, _run):
        def facts(path):
            return {
                "/sys/class/drm/card0/device/vendor": "0x1002",
                "/sys/class/drm/card0/device/device": "0x744c",
                "/sys/class/drm/card0/device/mem_info_vram_total": str(8 * 1024**3),
                "/sys/class/drm/card0/device/mem_info_vram_used": str(3 * 1024**3),
            }.get(str(path), "")

        read.side_effect = facts
        result = gpu_facts()
        self.assertEqual(result[0]["vram_total_gib"], 8.0)
        self.assertEqual(result[0]["vram_gib"], 5.0)


if __name__ == "__main__":
    unittest.main()
