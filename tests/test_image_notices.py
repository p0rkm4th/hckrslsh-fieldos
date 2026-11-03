import hashlib
import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "build" / "collect_image_notices.py"
SPEC = importlib.util.spec_from_file_location("collect_image_notices", MODULE_PATH)
collector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collector)


def make_tar(entries):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        for name, data in entries:
            member = tarfile.TarInfo(name)
            if isinstance(data, tuple) and data[0] == "symlink":
                member.type = tarfile.SYMTYPE
                member.linkname = data[1]
                archive.addfile(member)
            else:
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
    return buffer.getvalue()


def docker_save_fixture(path, layers, tag="example/image:1"):
    layer_names = [f"blobs/sha256/layer-{index}" for index in range(len(layers))]
    with tarfile.open(path, mode="w") as archive:
        for name, contents in zip(layer_names, layers):
            data = make_tar(contents)
            member = tarfile.TarInfo(name)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
        manifest = json.dumps([{"RepoTags": [tag], "Layers": layer_names}]).encode()
        member = tarfile.TarInfo("manifest.json")
        member.size = len(manifest)
        archive.addfile(member, io.BytesIO(manifest))


class ImageNoticeCollectionTests(unittest.TestCase):
    def test_scans_all_layers_even_when_manifest_is_last_and_deduplicates(self):
        notice = b"Copyright and license notice\n"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "image.tar"
            docker_save_fixture(
                archive,
                [
                    [("usr/share/doc/pkg/copyright", notice)],
                    [("app/node_modules/pkg/LICENSE.md", notice), ("app/README.md", b"not a license")],
                ],
            )
            report = collector.collect_image_archive(
                archive,
                {"name": "example", "ref": "example/image:1", "digest": "sha256:test", "license": "MIT"},
                root / "out",
            )
            digest = hashlib.sha256(notice).hexdigest()
            self.assertEqual(report["layer_count"], 2)
            self.assertEqual(report["unique_notice_files"], 1)
            self.assertEqual(report["occurrences"], 2)
            self.assertEqual(
                (root / "out" / "files" / f"{digest}.txt").read_bytes(), notice
            )
            self.assertEqual(
                [item["layer"] for item in report["files"][0]["occurrences"]], [0, 1]
            )

    def test_records_symlink_candidates_without_following_them(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "image.tar"
            docker_save_fixture(
                archive,
                [[("usr/share/doc/pkg/copyright", ("symlink", "../copyright.txt"))]],
            )
            report = collector.collect_image_archive(
                archive,
                {"name": "example", "ref": "example/image:1", "digest": "sha256:test"},
                root / "out",
            )
            self.assertEqual(report["unique_notice_files"], 0)
            self.assertEqual(report["non_regular_candidates"][0]["link"], "../copyright.txt")

    def test_rejects_unexpected_image_tag(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "image.tar"
            docker_save_fixture(archive, [[("usr/share/doc/pkg/copyright", b"x")]], tag="wrong/image:1")
            with self.assertRaisesRegex(ValueError, "tag mismatch"):
                collector.collect_image_archive(
                    archive,
                    {"name": "expected", "ref": "example/image:1", "digest": "sha256:test"},
                    root / "out",
                )

    def test_rejects_missing_layer_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "image.tar"
            manifest = json.dumps([{"RepoTags": ["example/image:1"], "Layers": ["missing/layer.tar"]}]).encode()
            with tarfile.open(archive, mode="w") as output:
                member = tarfile.TarInfo("manifest.json")
                member.size = len(manifest)
                output.addfile(member, io.BytesIO(manifest))
            with self.assertRaisesRegex(ValueError, "layer is missing"):
                collector.collect_image_archive(
                    archive,
                    {"name": "expected", "ref": "example/image:1", "digest": "sha256:test"},
                    root / "out",
                )


if __name__ == "__main__":
    unittest.main()
