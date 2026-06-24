#!/usr/bin/env python3

from __future__ import annotations

import argparse
import filecmp
import fnmatch
import shutil
from dataclasses import dataclass
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent.parent

HOME = Path.home()

FULL_SYNC_TARGETS = (
    HOME / ".config/opencode/skills/security-review",
    HOME / ".opencode/skills/security-review",
)

REFERENCE_SYNC_TARGETS = (
    HOME / ".opencode/skills/scrum-developer-skill/references/security-review",
    HOME / ".config/opencode/skills/scrum-developer-skill/references/security-review",
)

TRANSIENT_NAMES = {
    "__pycache__",
    ".DS_Store",
    "Thumbs.db",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

TRANSIENT_PATTERNS = (
    "*.pyc",
    "*.pyo",
    "*.tmp",
    "*.temp",
)

REFERENCE_EXCLUDED_NAMES = {
    "scripts",
    "evals",
    *TRANSIENT_NAMES,
}


@dataclass(frozen=True)
class SyncPolicy:
    name: str
    excluded_names: frozenset[str]
    excluded_patterns: tuple[str, ...]


FULL_POLICY = SyncPolicy(
    name="full",
    excluded_names=frozenset(TRANSIENT_NAMES),
    excluded_patterns=TRANSIENT_PATTERNS,
)

REFERENCE_POLICY = SyncPolicy(
    name="reference",
    excluded_names=frozenset(REFERENCE_EXCLUDED_NAMES),
    excluded_patterns=TRANSIENT_PATTERNS,
)


def _is_excluded_name(name: str, policy: SyncPolicy) -> bool:
    return name in policy.excluded_names


def _is_excluded_pattern(name: str, policy: SyncPolicy) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in policy.excluded_patterns)


def _should_exclude(path: Path, policy: SyncPolicy) -> bool:
    return _is_excluded_name(path.name, policy) or _is_excluded_pattern(
        path.name, policy
    )


def _iter_source_paths(source_root: Path, policy: SyncPolicy) -> dict[Path, Path]:
    included: dict[Path, Path] = {}
    stack = [source_root]

    while stack:
        current = stack.pop()
        for child in current.iterdir():
            if _should_exclude(child, policy):
                continue

            relative = child.relative_to(source_root)
            included[relative] = child

            if child.is_dir():
                stack.append(child)

    return included


def _copy_file(source: Path, destination: Path) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and filecmp.cmp(source, destination, shallow=False):
        return False
    shutil.copy2(source, destination)
    return True


def _remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
        return
    path.unlink()


def _ensure_target_safe(target_root: Path) -> None:
    resolved_source = SOURCE_ROOT.resolve()
    resolved_target = target_root.resolve()

    if resolved_target == resolved_source:
        raise SystemExit(
            f"Refusing to sync source directory onto itself: {resolved_target}"
        )

    if resolved_source in resolved_target.parents:
        raise SystemExit(
            "Refusing to sync into a nested path inside the source directory: "
            f"{resolved_target}"
        )


def _sync_directory(
    source_root: Path, target_root: Path, policy: SyncPolicy
) -> dict[str, int]:
    _ensure_target_safe(target_root)
    target_root.mkdir(parents=True, exist_ok=True)

    included_sources = _iter_source_paths(source_root, policy)
    expected_relatives = set(included_sources)

    copied_files = 0
    created_directories = 0
    removed_paths = 0

    for relative_path in sorted(expected_relatives):
        source_path = included_sources[relative_path]
        target_path = target_root / relative_path

        if source_path.is_dir():
            if not target_path.exists():
                target_path.mkdir(parents=True, exist_ok=True)
                created_directories += 1
            continue

        if _copy_file(source_path, target_path):
            copied_files += 1

    existing_paths = sorted(
        (path.relative_to(target_root), path) for path in target_root.rglob("*")
    )

    for relative_path, existing_path in reversed(existing_paths):
        if relative_path in expected_relatives:
            continue
        _remove_path(existing_path)
        removed_paths += 1

    return {
        "copied_files": copied_files,
        "created_directories": created_directories,
        "removed_paths": removed_paths,
    }


def _run_sync() -> int:
    results: list[tuple[Path, SyncPolicy, dict[str, int]]] = []

    for target in FULL_SYNC_TARGETS:
        results.append(
            (target, FULL_POLICY, _sync_directory(SOURCE_ROOT, target, FULL_POLICY))
        )

    for target in REFERENCE_SYNC_TARGETS:
        results.append(
            (
                target,
                REFERENCE_POLICY,
                _sync_directory(SOURCE_ROOT, target, REFERENCE_POLICY),
            )
        )

    for target, policy, stats in results:
        print(
            f"[{policy.name}] {target} -> "
            f"copied_files={stats['copied_files']} "
            f"created_directories={stats['created_directories']} "
            f"removed_paths={stats['removed_paths']}"
        )

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synchronize duplicated security-review skill copies."
    )
    parser.parse_args()
    raise SystemExit(_run_sync())


if __name__ == "__main__":
    main()
