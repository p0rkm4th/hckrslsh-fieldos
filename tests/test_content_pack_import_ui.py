import importlib.util
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/fieldos-content-pack-import.py"
SPEC = importlib.util.spec_from_file_location("fieldos_content_pack_import", SCRIPT)
IMPORTER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(IMPORTER)


class ContentPackImportUiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_authorized_reference_import_runs_the_existing_indexer(self):
        archive = self.root / "field-reference.tar.zst"
        archive.write_bytes(b"test archive")
        calls = [
            subprocess.CompletedProcess([], 0, "installed; activated reference documents", ""),
            subprocess.CompletedProcess([], 0, "Indexed reference.txt: 3 chunks", ""),
        ]
        with mock.patch.object(IMPORTER.os, "geteuid", return_value=0), \
             mock.patch.object(IMPORTER.sys, "argv", [str(SCRIPT), "--install-as-root", str(archive)]), \
             mock.patch.object(IMPORTER.subprocess, "run", side_effect=calls) as run:
            self.assertEqual(IMPORTER.install_as_root(), 0)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args_list[0].args[0][1:3], ["install", str(archive)])
        self.assertEqual(run.call_args_list[1].args[0][-1], IMPORTER.INDEXER)

    def test_authorized_map_import_does_not_reindex_references(self):
        archive = self.root / "map.tar.zst"
        archive.write_bytes(b"test archive")
        result = subprocess.CompletedProcess([], 0, "installed; activated map", "")
        with mock.patch.object(IMPORTER.os, "geteuid", return_value=0), \
             mock.patch.object(IMPORTER.sys, "argv", [str(SCRIPT), "--install-as-root", str(archive)]), \
             mock.patch.object(IMPORTER.subprocess, "run", return_value=result) as run:
            self.assertEqual(IMPORTER.install_as_root(), 0)
        run.assert_called_once()

    def test_root_import_rejects_symlink_before_invoking_installer(self):
        target = self.root / "target.tar.zst"
        target.write_bytes(b"not trusted")
        link = self.root / "link.tar.zst"
        link.symlink_to(target)
        with mock.patch.object(IMPORTER.os, "geteuid", return_value=0), \
             mock.patch.object(IMPORTER.sys, "argv", [str(SCRIPT), "--install-as-root", str(link)]), \
             mock.patch.object(IMPORTER.subprocess, "run") as run:
            self.assertEqual(IMPORTER.install_as_root(), 2)
        run.assert_not_called()

    def test_file_picker_requires_matching_checksum_sidecar(self):
        zenity = self.root / "zenity"
        pkexec = self.root / "pkexec"
        helper = self.root / "root-helper"
        zenity.touch()
        pkexec.touch()
        helper.touch()
        archive = self.root / "field-pack.tar.zst"
        archive.write_bytes(b"pack")
        choice = subprocess.CompletedProcess([], 0, str(archive) + "\n", "")
        with mock.patch.object(IMPORTER, "ZENITY", str(zenity)), \
             mock.patch.object(IMPORTER, "PKEXEC", str(pkexec)), \
             mock.patch.object(IMPORTER, "ROOT_HELPER", str(helper)), \
             mock.patch.object(IMPORTER.subprocess, "run", return_value=choice), \
             mock.patch.object(IMPORTER, "show_dialog") as dialog, \
             mock.patch.object(IMPORTER.subprocess, "Popen") as popen:
            self.assertEqual(IMPORTER.run_gui(), 2)
        dialog.assert_called_once()
        popen.assert_not_called()

    def test_desktop_launcher_uses_an_admin_authenticated_fixed_helper(self):
        desktop = (ROOT / "installer/provisioning/fieldos-content-pack-import.desktop").read_text()
        policy = ET.parse(ROOT / "installer/provisioning/fieldos-content-pack-import.policy").getroot()
        action = policy.find("action")
        self.assertIn("Exec=/usr/bin/python3 /opt/fieldos/scripts/fieldos-content-pack-import.py", desktop)
        self.assertIsNotNone(action)
        annotations = {
            item.attrib["key"]: item.text for item in action.findall("annotate")
        }
        self.assertEqual(
            annotations.get("org.freedesktop.policykit.exec.path"),
            "/usr/libexec/fieldos-content-pack-import-root",
        )
        self.assertEqual(action.findtext("defaults/allow_active"), "auth_admin")
        self.assertEqual(action.findtext("defaults/allow_any"), "no")

    def test_offline_importer_bundles_and_installs_graphical_polkit_agent(self):
        build = (ROOT / "build/prepare-payload.sh").read_text()
        firstboot = (ROOT / "installer/provisioning/firstboot.sh").read_text()
        self.assertIn("zenity", build)
        self.assertIn("policykit-1-gnome", build)
        self.assertIn("required_base_packages\":[\"zenity\",\"pkexec\",\"policykit-1-gnome\"]", build)
        self.assertIn("install \\\n  docker.io docker-compose-v2 curl zstd qemu-guest-agent zenity policykit-1-gnome", firstboot)
        self.assertIn("command -v pkexec", firstboot)
        self.assertIn("command -v zenity", firstboot)
        self.assertIn("/usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1", firstboot)


if __name__ == "__main__":
    unittest.main()
