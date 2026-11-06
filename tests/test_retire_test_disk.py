import json
import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts.retire_test_disk import RetirementError, main, retire, validate_candidate


class TestDiskRetirementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "fieldos-e2e"
        self.run_dir = self.root / "old-run"
        self.run_dir.mkdir(parents=True)
        self.disk = self.run_dir / "guest.qcow2"
        self.disk.write_bytes(b"fixture qcow data")
        self.report = self.run_dir / "report.md"
        self.report.write_text("# Completed disposable test\n", encoding="utf-8")
        self.release_doc = Path(self.temp.name) / "RELEASE.md"
        self.release_doc.write_text("# Release evidence\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def runner(self, attached_source="-"):
        def run(command, **kwargs):
            if command[:3] == ["virsh", "list", "--all"]:
                return subprocess.CompletedProcess(command, 0, "running-domain\n", "")
            if command[:2] == ["virsh", "domblklist"]:
                output = (
                    " Type   Device   Target   Source\n"
                    " file   disk     vda      " + attached_source + "\n"
                )
                return subprocess.CompletedProcess(command, 0, output, "")
            if command[:3] == ["qemu-img", "info", "--output=json"]:
                return subprocess.CompletedProcess(command, 0, json.dumps({"format": "qcow2"}), "")
            raise AssertionError(f"unexpected command: {command}")
        return run

    def validate(self, runner=None):
        return validate_candidate(
            self.disk, self.root, self.release_doc, runner or self.runner()
        )

    def test_refuses_disk_attached_to_running_or_defined_domain(self):
        with self.assertRaisesRegex(RetirementError, "attached to a libvirt domain"):
            self.validate(self.runner(str(self.disk)))
        self.assertTrue(self.disk.exists())

    def test_report_reference_does_not_require_preserving_guest_disk(self):
        self.release_doc.write_text(str(self.report), encoding="utf-8")
        disk, report = self.validate()
        self.assertEqual(disk, self.disk.resolve())
        self.assertEqual(report, self.report)
        self.assertTrue(disk.exists())

    def test_refuses_release_referenced_disk(self):
        self.release_doc.write_text(str(self.disk), encoding="utf-8")
        with self.assertRaisesRegex(RetirementError, "disk is referenced by docs/RELEASE.md"):
            self.validate()
        self.assertTrue(self.disk.exists())

    def test_requires_a_report_beside_the_disk(self):
        self.report.unlink()
        with self.assertRaisesRegex(RetirementError, "non-empty report.md"):
            self.validate()
        self.assertTrue(self.disk.exists())

    def test_accepts_retained_customer_validation_record_when_report_absent(self):
        self.report.unlink()
        validation = self.run_dir / "validation.md"
        validation.write_text("# Customer install acceptance\n", encoding="utf-8")
        disk, evidence = self.validate()
        self.assertEqual(disk, self.disk.resolve())
        self.assertEqual(evidence, validation)

    def test_rejects_empty_alternative_validation_record(self):
        self.report.unlink()
        (self.run_dir / "validation.md").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(RetirementError, "non-empty report.md"):
            self.validate()

    def test_disk_must_be_inside_evidence_root(self):
        outside = Path(self.temp.name) / "guest.qcow2"
        outside.write_bytes(b"fixture")
        with self.assertRaisesRegex(RetirementError, "inside E2E evidence root"):
            validate_candidate(outside, self.root, self.release_doc, self.runner())

    def test_retirement_removes_only_disk_and_keeps_evidence_and_audit(self):
        disk, report = self.validate()
        retire(disk, "superseded stopped disposable run", self.runner())
        self.assertFalse(disk.exists())
        self.assertTrue(report.exists())
        record = (self.run_dir / "disk-retirement.txt").read_text(encoding="utf-8")
        self.assertIn("Result: removed", record)
        self.assertIn("superseded stopped disposable run", record)

    def test_cli_defaults_to_dry_run(self):
        args = ["--disk", str(self.disk), "--e2e-root", str(self.root)]
        output = io.StringIO()
        with patch("scripts.retire_test_disk.validate_candidate", return_value=(self.disk, self.report)):
            with patch("scripts.retire_test_disk.retire") as delete:
                with redirect_stdout(output):
                    result = main(args)
        self.assertEqual(result, 0)
        self.assertIn("DRY RUN", output.getvalue())
        delete.assert_not_called()
        self.assertTrue(self.disk.exists())

    def test_cli_requires_reason_before_deleting(self):
        args = ["--disk", str(self.disk), "--e2e-root", str(self.root), "--delete"]
        errors = io.StringIO()
        with patch("scripts.retire_test_disk.validate_candidate", return_value=(self.disk, self.report)):
            with patch("scripts.retire_test_disk.retire") as delete:
                with redirect_stdout(io.StringIO()), redirect_stderr(errors):
                    result = main(args)
        self.assertEqual(result, 2)
        self.assertIn("--reason is required", errors.getvalue())
        delete.assert_not_called()
        self.assertTrue(self.disk.exists())


if __name__ == "__main__":
    unittest.main()
