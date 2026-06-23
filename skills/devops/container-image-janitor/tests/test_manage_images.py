from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "manage_images.py"
SPEC = importlib.util.spec_from_file_location("container_image_janitor_manage_images", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load manage_images.py for tests")
manage_images = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = manage_images
SPEC.loader.exec_module(manage_images)


class ManageImagesTests(unittest.TestCase):
    def test_extract_repository_handles_registry_port(self) -> None:
        self.assertEqual(
            manage_images.extract_repository("localhost:5000/demo/service:2026-05-26"),
            "localhost:5000/demo/service",
        )

    def test_build_cleanup_candidates_keeps_newest_three_and_dangling(self) -> None:
        image_id_1 = "sha256:" + "1" * 64
        image_id_2 = "sha256:" + "2" * 64
        image_id_3 = "sha256:" + "3" * 64
        image_id_4 = "sha256:" + "4" * 64
        image_id_5 = "sha256:" + "5" * 64
        image_id_6 = "sha256:" + "6" * 64
        images = [
            manage_images.ImageRecord(
                runtime="docker",
                image_id=image_id_1,
                tags=("demo/app:v1",),
                repositories=("demo/app",),
                created_at="2026-05-20T00:00:00Z",
                created_epoch=1,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=image_id_2,
                tags=("demo/app:v2",),
                repositories=("demo/app",),
                created_at="2026-05-21T00:00:00Z",
                created_epoch=2,
                size_bytes=101,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=image_id_3,
                tags=("demo/app:v3",),
                repositories=("demo/app",),
                created_at="2026-05-22T00:00:00Z",
                created_epoch=3,
                size_bytes=102,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=image_id_4,
                tags=("demo/app:v4",),
                repositories=("demo/app",),
                created_at="2026-05-23T00:00:00Z",
                created_epoch=4,
                size_bytes=103,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=image_id_5,
                tags=(),
                repositories=(),
                created_at="2026-05-24T00:00:00Z",
                created_epoch=5,
                size_bytes=104,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=image_id_6,
                tags=("repo-a:latest", "repo-b:latest"),
                repositories=("repo-a", "repo-b"),
                created_at="2026-05-25T00:00:00Z",
                created_epoch=6,
                size_bytes=105,
                parent_image_id="",
            ),
        ]

        candidates, warnings = manage_images.build_cleanup_candidates(images, keep_latest=3)
        candidate_ids = {candidate.image_id for candidate in candidates}

        self.assertEqual(candidate_ids, {image_id_1, image_id_5})
        self.assertEqual(
            {candidate.reason for candidate in candidates},
            {"older-than-keep-limit", "dangling-none"},
        )
        ranked_candidate = next(candidate for candidate in candidates if candidate.image_id == image_id_1)
        dangling_candidate = next(candidate for candidate in candidates if candidate.image_id == image_id_5)
        self.assertEqual(ranked_candidate.group_size, 4)
        self.assertEqual(ranked_candidate.retained_newer_count, 3)
        self.assertEqual(ranked_candidate.repository_count, 1)
        self.assertEqual(ranked_candidate.tag_count, 1)
        self.assertEqual(ranked_candidate.dependency_risk, "clear")
        self.assertEqual(ranked_candidate.recommended_action, "safe-to-delete")
        self.assertEqual(dangling_candidate.group_size, 1)
        self.assertEqual(dangling_candidate.tag_count, 0)
        self.assertEqual(dangling_candidate.repository_count, 0)
        self.assertEqual(dangling_candidate.recommended_action, "safe-to-delete")
        self.assertEqual(len(warnings), 1)
        self.assertIn(image_id_6, warnings[0])

    def test_write_candidates_csv_uses_utf8_sig_and_loads_approved_rows(self) -> None:
        candidate = manage_images.CleanupCandidate(
            approved="",
            runtime="podman",
            repository="demo/api",
            image_id="sha256:" + "7" * 64,
            tags=("demo/api:old",),
            created_at="2026-05-26T00:00:00Z",
            created_epoch=7,
            size_bytes=2048,
            reason="older-than-keep-limit",
            group_key="demo/api",
            group_rank=4,
            keep_limit=3,
            repository_count=1,
            tag_count=1,
            group_size=4,
            retained_newer_count=3,
            container_count=0,
            container_refs=(),
            child_image_count=0,
            child_image_ids=(),
            dependency_risk="clear",
            recommended_action="safe-to-delete",
            notes="test row",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "cleanup.csv"
            manage_images.write_candidates_csv(csv_path, [candidate])
            self.assertTrue(csv_path.read_bytes().startswith(b"\xef\xbb\xbf"))

            with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
                rows = list(csv.DictReader(handle))

            rows[0]["approved"] = "yes"
            with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

            approved_rows = manage_images.load_approved_rows(csv_path)
            self.assertEqual(len(approved_rows), 1)
            self.assertEqual(approved_rows[0]["image_id"], "sha256:" + "7" * 64)

    def test_write_candidates_csv_includes_dependency_columns(self) -> None:
        candidate = manage_images.CleanupCandidate(
            approved="",
            runtime="docker",
            repository="demo/api",
            image_id="sha256:" + "8" * 64,
            tags=("demo/api:old",),
            created_at="2026-05-26T00:00:00Z",
            created_epoch=8,
            size_bytes=1024,
            reason="older-than-keep-limit",
            group_key="demo/api",
            group_rank=4,
            keep_limit=3,
            repository_count=1,
            tag_count=1,
            group_size=4,
            retained_newer_count=3,
            container_count=1,
            container_refs=("running:demo-api:abc123",),
            child_image_count=2,
            child_image_ids=("sha256:child1", "sha256:child2"),
            dependency_risk="in-use-and-has-children",
            recommended_action="blocked-by-container",
            notes="test",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "cleanup.csv"
            manage_images.write_candidates_csv(csv_path, [candidate])

            with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(rows[0]["container_count"], "1")
            self.assertEqual(rows[0]["container_refs"], "running:demo-api:abc123")
            self.assertEqual(rows[0]["child_image_count"], "2")
            self.assertEqual(rows[0]["dependency_risk"], "in-use-and-has-children")
            self.assertEqual(rows[0]["recommended_action"], "blocked-by-container")

    def test_build_cleanup_candidates_marks_container_and_child_dependencies(self) -> None:
        parent_id = "sha256:" + "a" * 64
        new_1_id = "sha256:" + "b" * 64
        new_2_id = "sha256:" + "c" * 64
        new_3_id = "sha256:" + "d" * 64
        child_id = "sha256:" + "e" * 64
        images = [
            manage_images.ImageRecord(
                runtime="docker",
                image_id=parent_id,
                tags=("demo/api:v1",),
                repositories=("demo/api",),
                created_at="2026-05-20T00:00:00Z",
                created_epoch=1,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=new_1_id,
                tags=("demo/api:v4",),
                repositories=("demo/api",),
                created_at="2026-05-23T00:00:00Z",
                created_epoch=4,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=new_2_id,
                tags=("demo/api:v3",),
                repositories=("demo/api",),
                created_at="2026-05-22T00:00:00Z",
                created_epoch=3,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=new_3_id,
                tags=("demo/api:v2",),
                repositories=("demo/api",),
                created_at="2026-05-21T00:00:00Z",
                created_epoch=2,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=child_id,
                tags=("demo/child:v1",),
                repositories=("demo/child",),
                created_at="2026-05-24T00:00:00Z",
                created_epoch=5,
                size_bytes=100,
                parent_image_id=parent_id,
            ),
        ]
        container_usage = {("docker", parent_id): ["running:demo-api:container-1"]}

        candidates, _ = manage_images.build_cleanup_candidates(
            images,
            keep_latest=3,
            container_usage=container_usage,
        )

        parent_candidate = next(candidate for candidate in candidates if candidate.image_id == parent_id)
        self.assertEqual(parent_candidate.container_count, 1)
        self.assertEqual(parent_candidate.child_image_count, 1)
        self.assertEqual(parent_candidate.dependency_risk, "in-use-and-has-children")
        self.assertEqual(parent_candidate.recommended_action, "blocked-by-container")
        self.assertEqual(parent_candidate.container_refs, ("running:demo-api:container-1",))

    def test_load_approved_rows_accepts_csv_with_new_dependency_columns(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "cleanup.csv"
            with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.DictWriter(handle, fieldnames=manage_images.CSV_FIELDNAMES)
                writer.writeheader()
                writer.writerow(
                    {
                        "approved": "yes",
                        "runtime": "docker",
                        "repository": "demo/api",
                        "image_id": "sha256:" + "9" * 64,
                        "reason": "older-than-keep-limit",
                        "keep_limit": "3",
                        "container_count": "1",
                        "container_refs": "running:demo-api:abc123",
                        "dependency_risk": "in-use",
                        "recommended_action": "blocked-by-container",
                    }
                )

            approved_rows = manage_images.load_approved_rows(csv_path)
            self.assertEqual(len(approved_rows), 1)
            self.assertEqual(approved_rows[0]["image_id"], "sha256:" + "9" * 64)

    def test_load_approved_rows_accepts_old_minimal_csv_shape(self) -> None:
        minimal_fields = ["approved", "runtime", "repository", "image_id", "reason", "keep_limit"]
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "cleanup.csv"
            with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.DictWriter(handle, fieldnames=minimal_fields)
                writer.writeheader()
                writer.writerow(
                    {
                        "approved": "yes",
                        "runtime": "docker",
                        "repository": "demo/api",
                        "image_id": "sha256:" + "a" * 64,
                        "reason": "older-than-keep-limit",
                        "keep_limit": "3",
                    }
                )

            approved_rows = manage_images.load_approved_rows(csv_path)
            self.assertEqual(len(approved_rows), 1)
            self.assertEqual(approved_rows[0]["image_id"], "sha256:" + "a" * 64)

    def test_parse_timestamp_to_epoch_accepts_numeric_string(self) -> None:
        self.assertEqual(manage_images.parse_timestamp_to_epoch("1748217600.0"), 1748217600)

    def test_load_approved_rows_rejects_invalid_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "cleanup.csv"
            with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.DictWriter(handle, fieldnames=manage_images.CSV_FIELDNAMES)
                writer.writeheader()
                writer.writerow(
                    {
                        "approved": "yes",
                        "runtime": "nerdctl",
                        "repository": "demo/api",
                        "image_id": "sha256:" + "1" * 64,
                        "reason": "older-than-keep-limit",
                        "keep_limit": "3",
                    }
                )

            with self.assertRaises(RuntimeError):
                manage_images.load_approved_rows(csv_path)

    def test_load_approved_rows_rejects_option_like_image_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "cleanup.csv"
            with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.DictWriter(handle, fieldnames=manage_images.CSV_FIELDNAMES)
                writer.writeheader()
                writer.writerow(
                    {
                        "approved": "yes",
                        "runtime": "docker",
                        "repository": "demo/api",
                        "image_id": "--force",
                        "reason": "older-than-keep-limit",
                        "keep_limit": "3",
                    }
                )

            with self.assertRaises(RuntimeError):
                manage_images.load_approved_rows(csv_path)

    def test_build_deletion_plan_blocks_stale_rows(self) -> None:
        approved_image_id = "sha256:" + "2" * 64
        current_image_1 = "sha256:" + "3" * 64
        current_image_2 = "sha256:" + "4" * 64
        current_image_3 = "sha256:" + "5" * 64
        approved_rows = [
            {
                "approved": "yes",
                "runtime": "docker",
                "repository": "demo/app",
                "image_id": approved_image_id,
                "reason": "older-than-keep-limit",
                "keep_limit": "3",
            }
        ]
        current_images = [
            manage_images.ImageRecord(
                runtime="docker",
                image_id=approved_image_id,
                tags=("demo/app:v4",),
                repositories=("demo/app",),
                created_at="2026-05-23T00:00:00Z",
                created_epoch=4,
                size_bytes=103,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=current_image_1,
                tags=("demo/app:v3",),
                repositories=("demo/app",),
                created_at="2026-05-22T00:00:00Z",
                created_epoch=3,
                size_bytes=102,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=current_image_2,
                tags=("demo/app:v2",),
                repositories=("demo/app",),
                created_at="2026-05-21T00:00:00Z",
                created_epoch=2,
                size_bytes=101,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id=current_image_3,
                tags=("demo/app:v1",),
                repositories=("demo/app",),
                created_at="2026-05-20T00:00:00Z",
                created_epoch=1,
                size_bytes=100,
                parent_image_id="",
            ),
        ]

        with patch.object(manage_images, "collect_runtime_images", return_value=current_images):
            plans = manage_images.build_deletion_plan(approved_rows)

        self.assertEqual(len(plans), 1)
        self.assertTrue(plans[0].exists)
        self.assertFalse(plans[0].eligible)
        self.assertIn("no longer recommends deleting", plans[0].notes)

    def test_build_deletion_plan_blocks_container_risk(self) -> None:
        image_id = "sha256:" + "b" * 64
        approved_rows = [
            {
                "approved": "yes",
                "runtime": "docker",
                "repository": "demo/api",
                "image_id": image_id,
                "reason": "older-than-keep-limit",
                "keep_limit": "3",
            }
        ]
        images = [
            manage_images.ImageRecord(
                runtime="docker",
                image_id=image_id,
                tags=("demo/api:v1",),
                repositories=("demo/api",),
                created_at="2026-05-20T00:00:00Z",
                created_epoch=1,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id="sha256:" + "c" * 64,
                tags=("demo/api:v4",),
                repositories=("demo/api",),
                created_at="2026-05-23T00:00:00Z",
                created_epoch=4,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id="sha256:" + "d" * 64,
                tags=("demo/api:v3",),
                repositories=("demo/api",),
                created_at="2026-05-22T00:00:00Z",
                created_epoch=3,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id="sha256:" + "e" * 64,
                tags=("demo/api:v2",),
                repositories=("demo/api",),
                created_at="2026-05-21T00:00:00Z",
                created_epoch=2,
                size_bytes=100,
                parent_image_id="",
            ),
        ]
        container_usage = {("docker", image_id): ["running:demo-api:abc123"]}

        with patch.object(manage_images, "collect_runtime_images", return_value=images), patch.object(
            manage_images,
            "collect_runtime_container_usage",
            return_value=container_usage,
        ):
            plans = manage_images.build_deletion_plan(approved_rows)

        self.assertEqual(len(plans), 1)
        self.assertTrue(plans[0].exists)
        self.assertFalse(plans[0].eligible)
        self.assertIn("blocked-by-container", plans[0].notes)

    def test_build_deletion_plan_blocks_child_dependency_risk(self) -> None:
        parent_id = "sha256:" + "f" * 64
        approved_rows = [
            {
                "approved": "yes",
                "runtime": "docker",
                "repository": "demo/api",
                "image_id": parent_id,
                "reason": "older-than-keep-limit",
                "keep_limit": "3",
            }
        ]
        images = [
            manage_images.ImageRecord(
                runtime="docker",
                image_id=parent_id,
                tags=("demo/api:v1",),
                repositories=("demo/api",),
                created_at="2026-05-20T00:00:00Z",
                created_epoch=1,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id="sha256:" + "1" * 64,
                tags=("demo/api:v4",),
                repositories=("demo/api",),
                created_at="2026-05-23T00:00:00Z",
                created_epoch=4,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id="sha256:" + "2" * 64,
                tags=("demo/api:v3",),
                repositories=("demo/api",),
                created_at="2026-05-22T00:00:00Z",
                created_epoch=3,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id="sha256:" + "3" * 64,
                tags=("demo/api:v2",),
                repositories=("demo/api",),
                created_at="2026-05-21T00:00:00Z",
                created_epoch=2,
                size_bytes=100,
                parent_image_id="",
            ),
            manage_images.ImageRecord(
                runtime="docker",
                image_id="sha256:" + "4" * 64,
                tags=("demo/child:v1",),
                repositories=("demo/child",),
                created_at="2026-05-24T00:00:00Z",
                created_epoch=5,
                size_bytes=100,
                parent_image_id=parent_id,
            ),
        ]

        with patch.object(manage_images, "collect_runtime_images", return_value=images), patch.object(
            manage_images,
            "collect_runtime_container_usage",
            return_value={},
        ):
            plans = manage_images.build_deletion_plan(approved_rows)

        self.assertEqual(len(plans), 1)
        self.assertTrue(plans[0].exists)
        self.assertFalse(plans[0].eligible)
        self.assertIn("blocked-by-child-image", plans[0].notes)


if __name__ == "__main__":
    unittest.main()
