#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

APPROVAL_VALUES = {"1", "true", "yes", "y"}
VALID_RUNTIMES = {"docker", "podman"}
VALID_REASONS = {"older-than-keep-limit", "dangling-none"}
IMAGE_ID_PATTERN = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")
SAFE_RECOMMENDED_ACTIONS = {"safe-to-delete"}
CSV_FIELDNAMES = [
    "approved",
    "runtime",
    "repository",
    "image_id",
    "tags",
    "created_at",
    "created_epoch",
    "size_bytes",
    "reason",
    "group_key",
    "group_rank",
    "keep_limit",
    "repository_count",
    "tag_count",
    "group_size",
    "retained_newer_count",
    "container_count",
    "container_refs",
    "child_image_count",
    "child_image_ids",
    "dependency_risk",
    "recommended_action",
    "delete_command",
    "notes",
]


@dataclass(frozen=True)
class ImageRecord:
    runtime: str
    image_id: str
    tags: tuple[str, ...]
    repositories: tuple[str, ...]
    created_at: str
    created_epoch: int
    size_bytes: int
    parent_image_id: str

    @property
    def is_dangling(self) -> bool:
        return not self.tags


@dataclass(frozen=True)
class CleanupCandidate:
    approved: str
    runtime: str
    repository: str
    image_id: str
    tags: tuple[str, ...]
    created_at: str
    created_epoch: int
    size_bytes: int
    reason: str
    group_key: str
    group_rank: int
    keep_limit: int
    repository_count: int
    tag_count: int
    group_size: int
    retained_newer_count: int
    container_count: int
    container_refs: tuple[str, ...]
    child_image_count: int
    child_image_ids: tuple[str, ...]
    dependency_risk: str
    recommended_action: str
    notes: str

    def as_csv_row(self) -> dict[str, str]:
        return {
            "approved": self.approved,
            "runtime": self.runtime,
            "repository": self.repository,
            "image_id": self.image_id,
            "tags": ";".join(self.tags) if self.tags else "<none>:<none>",
            "created_at": self.created_at,
            "created_epoch": str(self.created_epoch),
            "size_bytes": str(self.size_bytes),
            "reason": self.reason,
            "group_key": self.group_key,
            "group_rank": str(self.group_rank),
            "keep_limit": str(self.keep_limit),
            "repository_count": str(self.repository_count),
            "tag_count": str(self.tag_count),
            "group_size": str(self.group_size),
            "retained_newer_count": str(self.retained_newer_count),
            "container_count": str(self.container_count),
            "container_refs": ";".join(self.container_refs),
            "child_image_count": str(self.child_image_count),
            "child_image_ids": ";".join(self.child_image_ids),
            "dependency_risk": self.dependency_risk,
            "recommended_action": self.recommended_action,
            "delete_command": format_delete_command(self.runtime, self.image_id),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class DeletionPlan:
    runtime: str
    image_id: str
    repository: str
    reason: str
    keep_limit: int
    exists: bool
    eligible: bool
    notes: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inventory Docker/Podman images, export an approval CSV, and apply deletions from that CSV."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory = subparsers.add_parser(
        "inventory", help="Scan Docker/Podman images and export a UTF-8-SIG CSV."
    )
    inventory.add_argument(
        "--runtime",
        choices=["docker", "podman", "all"],
        default="all",
        help="Which runtime to scan. Default: all available runtimes.",
    )
    inventory.add_argument(
        "--keep-latest",
        type=positive_int,
        default=3,
        help="How many newest images to keep per repository. Default: 3.",
    )
    inventory.add_argument(
        "--output",
        required=True,
        help="Path to the UTF-8-SIG CSV file to create.",
    )

    apply_parser = subparsers.add_parser(
        "apply",
        help="Read an edited CSV and preview or execute image deletions for approved rows.",
    )
    apply_parser.add_argument("--csv", required=True, help="Path to the edited CSV file.")
    apply_parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete approved images. Without this flag, only a dry-run plan is shown.",
    )
    apply_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt when combined with --execute.",
    )

    return parser


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")
    return parsed


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "inventory":
        return run_inventory(args.runtime, args.keep_latest, Path(args.output))
    if args.command == "apply":
        return run_apply(Path(args.csv), execute=args.execute, assume_yes=args.yes)
    raise RuntimeError(f"unsupported command: {args.command}")


def run_inventory(runtime: str, keep_latest: int, output_path: Path) -> int:
    requested_runtimes = resolve_requested_runtimes(runtime)
    if not requested_runtimes:
        print("No requested runtimes are available on this machine.", file=sys.stderr)
        write_candidates_csv(output_path, [])
        return 1

    images: list[ImageRecord] = []
    container_usage: dict[tuple[str, str], list[str]] = {}
    for selected_runtime in requested_runtimes:
        if selected_runtime == "docker":
            runtime_images = collect_docker_images()
            images.extend(runtime_images)
            container_usage.update(collect_docker_container_usage())
        elif selected_runtime == "podman":
            runtime_images = collect_podman_images()
            images.extend(runtime_images)
            container_usage.update(collect_podman_container_usage())

    candidates, warnings = build_cleanup_candidates(
        images,
        keep_latest=keep_latest,
        container_usage=container_usage,
    )
    write_candidates_csv(output_path, candidates)

    print(f"Scanned runtimes: {', '.join(requested_runtimes)}")
    print(f"Discovered image records: {len(images)}")
    print(f"Suggested cleanup rows exported: {len(candidates)}")
    print(f"CSV written to: {output_path}")
    if warnings:
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")

    return 0


def run_apply(csv_path: Path, *, execute: bool, assume_yes: bool) -> int:
    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}", file=sys.stderr)
        return 1

    try:
        approved_rows = load_approved_rows(csv_path)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    if not approved_rows:
        print("No approved rows found in the CSV. Nothing to do.")
        return 0

    runtimes = sorted({row["runtime"] for row in approved_rows})
    unavailable = [runtime for runtime in runtimes if not command_exists(runtime)]
    if unavailable:
        print(
            "The following runtimes are referenced by approved rows but are not installed: "
            + ", ".join(unavailable),
            file=sys.stderr,
        )
        return 1

    plans = build_deletion_plan(approved_rows)
    print_deletion_plan(plans, execute=execute)

    blocking_plans = [plan for plan in plans if plan.exists and not plan.eligible]
    eligible_existing_plans = [plan for plan in plans if plan.exists and plan.eligible]

    if not execute:
        print("Dry-run complete. Re-run with --execute to delete the approved images.")
        return 0

    if blocking_plans:
        print(
            "Blocked approved rows were found. Refresh the inventory CSV and re-review it before executing deletions.",
            file=sys.stderr,
        )
        return 1

    if not eligible_existing_plans:
        print("No currently eligible existing images remain to delete.")
        return 0

    if not assume_yes and not confirm_execution(len(eligible_existing_plans)):
        print("Aborted. No images were deleted.")
        return 0

    failures = execute_deletion_plan(plans)
    if failures:
        print(f"Completed with {failures} failure(s).", file=sys.stderr)
        return 1

    print("Deletion run completed successfully.")
    return 0


def resolve_requested_runtimes(runtime: str) -> list[str]:
    if runtime == "all":
        return [candidate for candidate in ("docker", "podman") if command_exists(candidate)]
    if not command_exists(runtime):
        return []
    return [runtime]


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def collect_runtime_images(runtime: str) -> list[ImageRecord]:
    if runtime == "docker":
        return collect_docker_images()
    if runtime == "podman":
        return collect_podman_images()
    raise RuntimeError(f"unsupported runtime: {runtime}")


def collect_runtime_container_usage(runtime: str) -> dict[tuple[str, str], list[str]]:
    if runtime == "docker":
        return collect_docker_container_usage()
    if runtime == "podman":
        return collect_podman_container_usage()
    raise RuntimeError(f"unsupported runtime: {runtime}")


def collect_docker_container_usage() -> dict[tuple[str, str], list[str]]:
    container_ids = load_container_ids(["docker", "ps", "-a", "-q", "--no-trunc"])
    if not container_ids:
        return {}

    usage: dict[tuple[str, str], list[str]] = {}
    for chunk in chunked(container_ids, 100):
        result = run_command(["docker", "inspect", *chunk])
        payload = json.loads(result.stdout or "[]")
        if not isinstance(payload, list):
            raise RuntimeError("unexpected docker container inspect output")
        for item in payload:
            image_id = str(item.get("Image", "")).strip()
            if not is_safe_image_id(image_id):
                continue
            usage.setdefault(("docker", image_id), []).append(build_container_ref(item))
    return {key: sorted(values) for key, values in usage.items()}


def collect_podman_container_usage() -> dict[tuple[str, str], list[str]]:
    container_ids = load_container_ids(["podman", "ps", "-a", "-q", "--no-trunc"])
    if not container_ids:
        return {}

    usage: dict[tuple[str, str], list[str]] = {}
    for chunk in chunked(container_ids, 100):
        result = run_command(["podman", "container", "inspect", *chunk])
        payload = json.loads(result.stdout or "[]")
        if not isinstance(payload, list):
            raise RuntimeError("unexpected podman container inspect output")
        for item in payload:
            image_id = str(item.get("Image", "")).strip()
            if not is_safe_image_id(image_id):
                continue
            usage.setdefault(("podman", image_id), []).append(build_container_ref(item))
    return {key: sorted(values) for key, values in usage.items()}


def load_container_ids(command: list[str]) -> list[str]:
    result = run_command(command)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def build_container_ref(item: dict[str, Any]) -> str:
    state = str(item.get("State", {}).get("Status") or item.get("State", "unknown")).strip() or "unknown"
    name = str(item.get("Name", "")).strip().lstrip("/") or "unnamed"
    container_id = str(item.get("Id") or item.get("ID") or "").strip()
    short_id = container_id[:12] if container_id else "unknown"
    return f"{state}:{name}:{short_id}"


def run_command(command: list[str], *, allowed_codes: set[int] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    acceptable_codes = allowed_codes if allowed_codes is not None else {0}
    if result.returncode not in acceptable_codes:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        details = stderr or stdout or "no details available"
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{details}")
    return result


def collect_docker_images() -> list[ImageRecord]:
    list_result = run_command(
        ["docker", "image", "ls", "-a", "--no-trunc", "--format", "json"]
    )
    tag_map = parse_docker_tag_map(list_result.stdout)
    image_ids = sorted(tag_map) if tag_map else load_docker_image_ids()
    if not image_ids:
        return []

    inspected = inspect_docker_images(image_ids)
    records: list[ImageRecord] = []
    for item in inspected:
        image_id = str(item.get("Id", "")).strip()
        if not image_id:
            continue
        tags = sorted(tag_map.get(image_id, set()) | normalize_tags(item.get("RepoTags")))
        created_at = str(item.get("Created", "")).strip()
        created_epoch = parse_timestamp_to_epoch(created_at)
        records.append(
            ImageRecord(
                runtime="docker",
                image_id=image_id,
                tags=tuple(tags),
                repositories=tuple(sorted({extract_repository(tag) for tag in tags})),
                created_at=created_at,
                created_epoch=created_epoch,
                size_bytes=normalize_size_bytes(item.get("Size")),
                parent_image_id=normalize_parent_image_id(item.get("Parent", "")),
            )
        )
    return records


def load_docker_image_ids() -> list[str]:
    result = run_command(["docker", "image", "ls", "-a", "-q", "--no-trunc"])
    return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})


def parse_docker_tag_map(text: str) -> dict[str, set[str]]:
    tag_map: dict[str, set[str]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        row = json.loads(line)
        image_id = str(row.get("ID", "")).strip()
        repository = str(row.get("Repository", "")).strip()
        tag = str(row.get("Tag", "")).strip()
        if not image_id:
            continue
        if repository in {"", "<none>"} or tag in {"", "<none>"}:
            tag_map.setdefault(image_id, set())
            continue
        tag_map.setdefault(image_id, set()).add(f"{repository}:{tag}")
    return tag_map


def inspect_docker_images(image_ids: list[str]) -> list[dict[str, Any]]:
    inspected: list[dict[str, Any]] = []
    for chunk in chunked(image_ids, 100):
        result = run_command(["docker", "image", "inspect", *chunk])
        payload = json.loads(result.stdout or "[]")
        if not isinstance(payload, list):
            raise RuntimeError("unexpected docker image inspect output")
        inspected.extend(payload)
    return inspected


def collect_podman_images() -> list[ImageRecord]:
    result = run_command(["podman", "images", "-a", "--format", "json"])
    payload = json.loads(result.stdout or "[]")
    if not isinstance(payload, list):
        raise RuntimeError("unexpected podman images output")

    image_ids = [
        str(item.get("Id") or item.get("id") or "").strip()
        for item in payload
        if isinstance(item, dict) and str(item.get("Id") or item.get("id") or "").strip()
    ]
    inspected_by_id = inspect_podman_images(image_ids)

    records: list[ImageRecord] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        image_id = str(item.get("Id") or item.get("id") or "").strip()
        if not image_id:
            continue
        inspected = inspected_by_id.get(image_id, {})
        tags = sorted(normalize_tags(item.get("Names") or item.get("names")))
        created_at = str(
            item.get("Created")
            or item.get("created")
            or item.get("CreatedAt")
            or item.get("createdAt")
            or ""
        ).strip()
        records.append(
            ImageRecord(
                runtime="podman",
                image_id=image_id,
                tags=tuple(tags),
                repositories=tuple(sorted({extract_repository(tag) for tag in tags})),
                created_at=created_at,
                created_epoch=parse_timestamp_to_epoch(created_at),
                size_bytes=normalize_size_bytes(
                    item.get("Size")
                    or item.get("size")
                    or item.get("VirtualSize")
                    or item.get("virtualSize")
                ),
                parent_image_id=normalize_parent_image_id(
                    inspected.get("Parent")
                    or inspected.get("ParentId")
                    or inspected.get("parent")
                    or inspected.get("parentId")
                    or ""
                ),
            )
        )
    return records


def inspect_podman_images(image_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not image_ids:
        return {}

    inspected: dict[str, dict[str, Any]] = {}
    for chunk in chunked(image_ids, 100):
        result = run_command(["podman", "image", "inspect", *chunk])
        payload = json.loads(result.stdout or "[]")
        if not isinstance(payload, list):
            raise RuntimeError("unexpected podman image inspect output")
        for item in payload:
            image_id = str(item.get("Id") or item.get("ID") or item.get("id") or "").strip()
            if image_id:
                inspected[image_id] = item
    return inspected


def normalize_tags(value: Any) -> set[str]:
    if not value:
        return set()
    if isinstance(value, str):
        raw_values = [value]
    else:
        raw_values = [str(item) for item in value if item]

    cleaned: set[str] = set()
    for item in raw_values:
        text = item.strip()
        if not text or text in {"<none>", "<none>:<none>"}:
            continue
        cleaned.add(text)
    return cleaned


def normalize_size_bytes(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, dict):
        for key in ("bytes", "Bytes", "size", "Size"):
            if key in value:
                return normalize_size_bytes(value[key])
        return 0
    text = str(value).strip()
    digits = re.sub(r"[^0-9]", "", text)
    return int(digits) if digits else 0


def normalize_parent_image_id(value: Any) -> str:
    text = str(value or "").strip()
    return text if is_safe_image_id(text) else ""


def is_safe_image_id(value: str) -> bool:
    return bool(IMAGE_ID_PATTERN.fullmatch(value.strip()))


def parse_timestamp_to_epoch(value: str) -> int:
    text = value.strip()
    if not text:
        return 0

    if re.fullmatch(r"\d+(?:\.\d+)?", text):
        return int(float(text))

    normalized = text
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    match = re.match(r"^(?P<head>.*?)(?P<fraction>\.\d+)?(?P<zone>[+-]\d{2}:\d{2})?$", normalized)
    if match:
        head = match.group("head") or ""
        fraction = match.group("fraction") or ""
        zone = match.group("zone") or ""
        if fraction:
            fraction = "." + fraction[1:7]
        normalized = f"{head}{fraction}{zone}"

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return 0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp())


def extract_repository(tag: str) -> str:
    if tag in {"", "<none>", "<none>:<none>"}:
        return "<none>"
    if ":" not in tag:
        return tag
    return tag.rsplit(":", 1)[0]


def build_cleanup_candidates(
    images: list[ImageRecord], *, keep_latest: int, container_usage: dict[tuple[str, str], list[str]] | None = None
) -> tuple[list[CleanupCandidate], list[str]]:
    warnings: list[str] = []
    candidates: list[CleanupCandidate] = []
    container_usage = container_usage or {}
    child_image_index = build_child_image_index(images)

    for image in sorted(images, key=image_sort_key, reverse=True):
        if not is_safe_image_id(image.image_id):
            warnings.append(
                f"Skipped cleanup suggestion for {image.runtime} image with unsafe or missing image ID: {image.image_id or '<blank>'}."
            )
            continue
        if image.is_dangling:
            image_key = (image.runtime, image.image_id)
            dependency_risk, recommended_action = classify_dependency_risk(
                container_refs=container_usage.get(image_key, []),
                child_image_ids=child_image_index.get(image_key, []),
            )
            candidates.append(
                CleanupCandidate(
                    approved="",
                    runtime=image.runtime,
                    repository="<none>",
                    image_id=image.image_id,
                    tags=(),
                    created_at=image.created_at,
                    created_epoch=image.created_epoch,
                    size_bytes=image.size_bytes,
                    reason="dangling-none",
                    group_key="<none>",
                    group_rank=1,
                    keep_limit=keep_latest,
                    repository_count=0,
                    tag_count=0,
                    group_size=1,
                    retained_newer_count=0,
                    container_count=len(container_usage.get(image_key, [])),
                    container_refs=tuple(container_usage.get(image_key, [])),
                    child_image_count=len(child_image_index.get(image_key, [])),
                    child_image_ids=tuple(child_image_index.get(image_key, [])),
                    dependency_risk=dependency_risk,
                    recommended_action=recommended_action,
                    notes="Untagged / dangling image.",
                )
            )

    grouped: dict[tuple[str, str], list[ImageRecord]] = {}
    for image in images:
        if image.is_dangling:
            continue
        if len(image.repositories) != 1:
            warnings.append(
                f"Skipped auto-cleanup suggestion for {image.runtime} image {image.image_id} because it spans {len(image.repositories)} repositories."
            )
            continue
        repository = image.repositories[0]
        grouped.setdefault((image.runtime, repository), []).append(image)

    for (runtime, repository), repository_images in sorted(grouped.items()):
        ordered = sorted(repository_images, key=image_sort_key, reverse=True)
        group_size = len(ordered)
        for index, image in enumerate(ordered, start=1):
            if index <= keep_latest:
                continue
            image_key = (image.runtime, image.image_id)
            dependency_risk, recommended_action = classify_dependency_risk(
                container_refs=container_usage.get(image_key, []),
                child_image_ids=child_image_index.get(image_key, []),
            )
            candidates.append(
                CleanupCandidate(
                    approved="",
                    runtime=runtime,
                    repository=repository,
                    image_id=image.image_id,
                    tags=image.tags,
                    created_at=image.created_at,
                    created_epoch=image.created_epoch,
                    size_bytes=image.size_bytes,
                    reason="older-than-keep-limit",
                    group_key=repository,
                    group_rank=index,
                    keep_limit=keep_latest,
                    repository_count=len(image.repositories),
                    tag_count=len(image.tags),
                    group_size=group_size,
                    retained_newer_count=min(index - 1, keep_latest),
                    container_count=len(container_usage.get(image_key, [])),
                    container_refs=tuple(container_usage.get(image_key, [])),
                    child_image_count=len(child_image_index.get(image_key, [])),
                    child_image_ids=tuple(child_image_index.get(image_key, [])),
                    dependency_risk=dependency_risk,
                    recommended_action=recommended_action,
                    notes=f"Repository {repository} keeps only the newest {keep_latest} image(s).",
                )
            )

    candidates.sort(key=candidate_sort_key)
    warnings = sorted(dict.fromkeys(warnings))
    return candidates, warnings


def image_sort_key(image: ImageRecord) -> tuple[int, str, str]:
    return (image.created_epoch, image.created_at, image.image_id)


def build_child_image_index(images: list[ImageRecord]) -> dict[tuple[str, str], list[str]]:
    child_index: dict[tuple[str, str], list[str]] = {}
    for image in images:
        if not image.parent_image_id or not is_safe_image_id(image.parent_image_id):
            continue
        if not is_safe_image_id(image.image_id):
            continue
        child_index.setdefault((image.runtime, image.parent_image_id), []).append(image.image_id)
    return {key: sorted(values) for key, values in child_index.items()}


def classify_dependency_risk(
    *, container_refs: list[str], child_image_ids: list[str]
) -> tuple[str, str]:
    if container_refs and child_image_ids:
        return "in-use-and-has-children", "blocked-by-container"
    if container_refs:
        return "in-use", "blocked-by-container"
    if child_image_ids:
        return "has-child-images", "blocked-by-child-image"
    return "clear", "safe-to-delete"


def candidate_sort_key(candidate: CleanupCandidate) -> tuple[str, str, int, str]:
    return (candidate.runtime, candidate.group_key, candidate.group_rank, candidate.image_id)


def write_candidates_csv(output_path: Path, candidates: list[CleanupCandidate]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for candidate in candidates:
            writer.writerow(candidate.as_csv_row())


def load_approved_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required_fields = {"approved", "runtime", "repository", "image_id", "reason", "keep_limit"}
        missing_fields = required_fields - set(reader.fieldnames or [])
        if missing_fields:
            raise RuntimeError(
                f"CSV is missing required field(s): {', '.join(sorted(missing_fields))}"
            )

        deduplicated_rows: dict[tuple[str, str], dict[str, str]] = {}
        for row in reader:
            approved = str(row.get("approved", "")).strip().lower()
            if approved not in APPROVAL_VALUES:
                continue

            normalized_row = {
                key: str(value or "").strip()
                for key, value in row.items()
                if key is not None
            }
            validate_approved_row(normalized_row)

            key = (normalized_row["runtime"], normalized_row["image_id"])
            existing = deduplicated_rows.get(key)
            if existing and any(
                existing[field] != normalized_row[field]
                for field in ("repository", "reason", "keep_limit")
            ):
                raise RuntimeError(
                    "Conflicting approved rows found for "
                    f"{normalized_row['runtime']} {normalized_row['image_id']}"
                )
            deduplicated_rows[key] = normalized_row
    return list(deduplicated_rows.values())


def validate_approved_row(row: dict[str, str]) -> None:
    runtime = row.get("runtime", "")
    if runtime not in VALID_RUNTIMES:
        raise RuntimeError(f"Unsupported runtime in approved CSV row: {runtime or '<blank>'}")

    image_id = row.get("image_id", "")
    if not image_id:
        raise RuntimeError("Approved CSV row is missing image_id")
    if image_id.startswith("-"):
        raise RuntimeError(f"Unsafe image_id in approved CSV row: {image_id}")
    if not IMAGE_ID_PATTERN.fullmatch(image_id):
        raise RuntimeError(
            "Approved CSV row must contain a full image ID in the form sha256:<64hex> or <64hex>: "
            f"{image_id}"
        )

    reason = row.get("reason", "")
    if reason not in VALID_REASONS:
        raise RuntimeError(f"Unsupported reason in approved CSV row: {reason or '<blank>'}")

    keep_limit = row.get("keep_limit", "")
    if not keep_limit.isdigit() or int(keep_limit) < 1:
        raise RuntimeError(f"Invalid keep_limit in approved CSV row: {keep_limit or '<blank>'}")

    repository = row.get("repository", "")
    if reason == "dangling-none" and repository != "<none>":
        raise RuntimeError(
            "Approved CSV row with reason dangling-none must keep repository set to <none>"
        )
    if reason == "older-than-keep-limit" and repository in {"", "<none>"}:
        raise RuntimeError(
            "Approved CSV row with reason older-than-keep-limit must include its repository"
        )


def build_deletion_plan(approved_rows: list[dict[str, str]]) -> list[DeletionPlan]:
    runtime_images: dict[str, list[ImageRecord]] = {}
    runtime_container_usage: dict[str, dict[tuple[str, str], list[str]]] = {}
    candidate_cache: dict[tuple[str, int], dict[str, CleanupCandidate]] = {}
    current_ids: dict[str, set[str]] = {}

    keep_limits_by_runtime: dict[str, set[int]] = {}
    for row in approved_rows:
        keep_limits_by_runtime.setdefault(row["runtime"], set()).add(int(row["keep_limit"]))

    for runtime, keep_limits in keep_limits_by_runtime.items():
        images = collect_runtime_images(runtime)
        runtime_images[runtime] = images
        runtime_container_usage[runtime] = collect_runtime_container_usage(runtime)
        current_ids[runtime] = {image.image_id for image in images}
        for keep_limit in keep_limits:
            candidates, _ = build_cleanup_candidates(
                images,
                keep_latest=keep_limit,
                container_usage=runtime_container_usage[runtime],
            )
            candidate_cache[(runtime, keep_limit)] = {
                candidate.image_id: candidate for candidate in candidates
            }

    plans: list[DeletionPlan] = []
    seen: set[tuple[str, str]] = set()
    for row in approved_rows:
        runtime = row["runtime"]
        image_id = row["image_id"]
        keep_limit = int(row["keep_limit"])
        key = (runtime, image_id)
        if key in seen:
            continue
        seen.add(key)

        exists = image_id in current_ids[runtime]
        current_candidate = candidate_cache[(runtime, keep_limit)].get(image_id)
        eligible = False
        notes = ""

        if not exists:
            notes = "Image no longer exists in the current runtime state."
        elif current_candidate is None:
            notes = "Current inventory no longer recommends deleting this image; refresh the CSV before executing."
        elif current_candidate.repository != row.get("repository", ""):
            notes = (
                "Current inventory still sees the image, but its repository group no longer matches the approved CSV row."
            )
        elif current_candidate.reason != row.get("reason", ""):
            notes = (
                "Current inventory still sees the image, but the cleanup reason no longer matches the approved CSV row."
            )
        elif current_candidate.recommended_action not in SAFE_RECOMMENDED_ACTIONS:
            notes = (
                "Current inventory reports dependency risk and does not recommend direct deletion: "
                f"{current_candidate.recommended_action} ({current_candidate.dependency_risk})."
            )
        else:
            eligible = True
            notes = "Current inventory still matches this approved deletion row."

        plans.append(
            DeletionPlan(
                runtime=runtime,
                image_id=image_id,
                repository=row.get("repository", ""),
                reason=row.get("reason", ""),
                keep_limit=keep_limit,
                exists=exists,
                eligible=eligible,
                notes=notes,
            )
        )
    return plans


def print_deletion_plan(plans: list[DeletionPlan], *, execute: bool) -> None:
    mode = "EXECUTE" if execute else "DRY-RUN"
    print(f"Mode: {mode}")
    print("Approved deletion rows:")
    for plan in plans:
        exists_label = "FOUND" if plan.exists else "MISSING"
        eligibility_label = "ELIGIBLE" if plan.eligible else "BLOCKED"
        print(
            f"- [{exists_label}/{eligibility_label}] {plan.runtime} {plan.image_id} ({plan.repository or '<none>'}) reason={plan.reason} keep_limit={plan.keep_limit}"
        )
        print(f"  -> {format_delete_command(plan.runtime, plan.image_id)}")
        print(f"  -> {plan.notes}")
    print()


def confirm_execution(existing_count: int) -> bool:
    if existing_count == 0:
        return True
    answer = input(
        f"Delete {existing_count} existing image(s) that are marked approved in the CSV? [y/N]: "
    )
    return answer.strip().lower() in APPROVAL_VALUES


def execute_deletion_plan(plans: list[DeletionPlan]) -> int:
    failures = 0
    for plan in plans:
        if not plan.exists:
            print(f"Skip: {plan.runtime} image no longer exists: {plan.image_id}")
            continue
        if not plan.eligible:
            print(
                f"Skip: {plan.runtime} image is no longer eligible for deletion: {plan.image_id}",
                file=sys.stderr,
            )
            failures += 1
            continue
        command = delete_command(plan.runtime, plan.image_id)
        result = run_command(command, allowed_codes={0, 1, 2, 125})
        if result.returncode != 0:
            failures += 1
            details = (result.stderr or result.stdout or "unknown failure").strip()
            print(
                f"Failed: {plan.runtime} {plan.image_id} (exit={result.returncode})\n{details}",
                file=sys.stderr,
            )
            continue
        print(f"Deleted: {plan.runtime} {plan.image_id}")
    return failures


def format_delete_command(runtime: str, image_id: str) -> str:
    return " ".join(delete_command(runtime, image_id))


def delete_command(runtime: str, image_id: str) -> list[str]:
    if runtime == "docker":
        return ["docker", "image", "rm", image_id]
    if runtime == "podman":
        return ["podman", "rmi", image_id]
    raise RuntimeError(f"unsupported runtime: {runtime}")


def chunked(values: list[str], chunk_size: int) -> Iterable[list[str]]:
    for index in range(0, len(values), chunk_size):
        yield values[index : index + chunk_size]


if __name__ == "__main__":
    sys.exit(main())
