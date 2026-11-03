import unittest
from unittest.mock import patch

from pathlib import Path
from hardware.detect.detect import available_memory_gib, cpu_facts, gpu_facts, memory_gib


class DetectionTests(unittest.TestCase):
    @patch("hardware.detect.detect.read_text", return_value="model name : Example CPU\nflags : avx avx2 sse4_2")
    def test_cpu_capabilities_are_filtered(self, _):
        result = cpu_facts()
        self.assertEqual(result["model"], "Example CPU")
        self.assertEqual(result["instruction_sets"], ["avx", "avx2", "sse4_2"])

    @patch("hardware.detect.detect.read_text", return_value="MemTotal:       8388608 kB")
    def test_memory_conversion(self, _):
        self.assertEqual(memory_gib(), 8.0)

    @patch("hardware.detect.detect.read_text", return_value="MemAvailable: 4194304 kB")
    def test_available_memory_conversion(self, _):
        self.assertEqual(available_memory_gib(), 4.0)

    @patch("hardware.detect.detect.read_text", return_value=(
        "processor : 0\nphysical id : 0\ncore id : 0\nmodel name : Example CPU\nflags : avx2\n\n"
        "processor : 1\nphysical id : 0\ncore id : 0\nmodel name : Example CPU\nflags : avx2\n\n"
        "processor : 2\nphysical id : 0\ncore id : 1\nmodel name : Example CPU\nflags : avx2"
    ))
    def test_cpu_reports_unique_physical_cores(self, _):
        result = cpu_facts()
        self.assertEqual(result["logical_cores"], 20)
        self.assertEqual(result["physical_cores"], 2)

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

    @patch("hardware.detect.detect.run", return_value="RTX fixture, 12288, 10240")
    @patch("hardware.detect.detect.Path.glob", return_value=[
        Path("/fixture/card0/device"), Path("/fixture/card1/device")])
    @patch("hardware.detect.detect.read_text")
    def test_integrated_gpu_is_reported_alongside_nvidia(self, read, _glob, _run):
        def facts(path):
            return {
                "/fixture/card0/device/vendor": "0x10de",
                "/fixture/card0/device/device": "0x2208",
                "/fixture/card0/device/mem_info_vram_total": str(12 * 1024**3),
                "/fixture/card0/device/mem_info_vram_used": str(2 * 1024**3),
                "/fixture/card1/device/vendor": "0x8086",
                "/fixture/card1/device/device": "0x1234",
            }.get(str(path), "")

        read.side_effect = facts
        result = gpu_facts()
        self.assertEqual([gpu["vendor"] for gpu in result], ["nvidia", "intel"])
        self.assertTrue(result[0]["driver_available"])
        self.assertFalse(result[0]["runtime_validated"])
        self.assertEqual(result[0]["vram_gib"], 10.0)
        self.assertEqual(result[1]["vram_gib"], 0.0)


if __name__ == "__main__":
    unittest.main()
