#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_NAME = "security-review"
PROVENANCE_KEYS = (
    "skill_name",
    "skill_source_path",
    "benchmark_root_source",
    "workspace_root",
)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_path(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(Path(value).expanduser().resolve())


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _find_workspace_root(start: Path) -> Path | None:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / "docs").is_dir() or (candidate / "temp").is_dir():
            return candidate
    return None


def _resolve_benchmark_root(
    explicit_root: str | None, skill_dir: Path, cwd: Path
) -> tuple[Path, str, Path | None]:
    workspace_root = _find_workspace_root(cwd)
    timestamp = _utc_timestamp()

    if explicit_root:
        return Path(explicit_root).expanduser().resolve(), "explicit", workspace_root

    if workspace_root is not None and (workspace_root / "docs").is_dir():
        return (
            (workspace_root / "docs" / "review" / SKILL_NAME / timestamp).resolve(),
            "workspace_docs",
            workspace_root,
        )

    if workspace_root is not None and (workspace_root / "temp").is_dir():
        return (
            (workspace_root / "temp" / SKILL_NAME / timestamp).resolve(),
            "workspace_temp",
            workspace_root,
        )

    return (
        (Path.home() / "temp" / SKILL_NAME / timestamp).resolve(),
        "home_temp",
        workspace_root,
    )


def _build_context(
    skill_dir: Path,
    benchmark_root: Path,
    benchmark_root_source: str,
    workspace_root: Path | None,
) -> dict[str, Any]:
    context: dict[str, Any] = {
        "skill_name": SKILL_NAME,
        "run_mode": "scaffold",
        "scaffolded_at": _utc_iso(),
        "benchmark_root": str(benchmark_root),
        "benchmark_root_source": benchmark_root_source,
        "opencode_cwd": str(Path.cwd().resolve()),
        "skill_source_path": str(skill_dir.resolve()),
        "platform": platform.platform(),
        "python_version": sys.version,
    }
    if workspace_root is not None:
        context["workspace_root"] = str(workspace_root.resolve())
    return context


def _ensure_benchmark_root_allowed(benchmark_root: Path, skill_dir: Path) -> None:
    if _is_within(benchmark_root, skill_dir):
        raise SystemExit(
            "Refusing to use a benchmark root inside the installed skill directory: "
            f"{benchmark_root}. Choose an explicit root outside {skill_dir}, or let the runner use the current "
            "workspace docs/temp policy or ~/temp fallback."
        )


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit(
            f"Expected a JSON object in {path}, found {type(data).__name__}."
        )
    return data


def _check_existing_context(
    context_path: Path, candidate_context: dict[str, Any]
) -> bool:
    if not context_path.exists():
        return False

    existing = _load_json(context_path)
    mismatches: list[str] = []
    for key in PROVENANCE_KEYS:
        existing_value = existing.get(key)
        candidate_value = candidate_context.get(key)
        if key.endswith("_path") or key.endswith("_root"):
            existing_value = _normalize_path(existing_value)
            candidate_value = _normalize_path(candidate_value)
        if existing_value != candidate_value:
            mismatches.append(
                f"{key}: existing={existing_value!r}, requested={candidate_value!r}"
            )

    if mismatches:
        details = "\n  - ".join(mismatches)
        raise SystemExit(
            "Existing benchmark_root provenance is incompatible with this run. Reusing a root is only allowed when "
            "the stored provenance matches the requested provenance.\n"
            f"benchmark_root: {context_path.parent}\n"
            f"context_file: {context_path}\n"
            f"mismatches:\n  - {details}"
        )

    return True


def _write_context(context_path: Path, context: dict[str, Any]) -> None:
    context_path.parent.mkdir(parents=True, exist_ok=True)
    with context_path.open("w", encoding="utf-8") as handle:
        json.dump(context, handle, indent=2)
        handle.write("\n")


def _load_eval_catalog(skill_dir: Path) -> list[dict[str, Any]]:
    catalog_path = skill_dir / "evals" / "evals.json"
    if not catalog_path.exists():
        raise SystemExit(f"Missing benchmark catalog: {catalog_path}")

    with catalog_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise SystemExit(
            f"Expected a JSON list in {catalog_path}, found {type(data).__name__}."
        )

    return data


def _select_eval(evals: list[dict[str, Any]], eval_id: int) -> dict[str, Any]:
    for item in evals:
        if item.get("eval_id") == eval_id:
            return item
    raise SystemExit(
        f"Unknown eval_id={eval_id}. Available ids: {[item.get('eval_id') for item in evals]}"
    )


def _copy_eval_inputs(
    skill_dir: Path, benchmark_root: Path, eval_definition: dict[str, Any]
) -> tuple[Path, list[str]]:
    run_dir = benchmark_root / "runs" / f"eval-{eval_definition['eval_id']}"
    inputs_root = run_dir / "inputs"
    copied_inputs: list[str] = []

    for relative_path in eval_definition.get("files", []):
        source = skill_dir / relative_path
        destination = inputs_root / relative_path
        if not source.exists():
            raise SystemExit(f"Benchmark input is missing: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied_inputs.append(str(destination.relative_to(run_dir)))

    metadata = dict(eval_definition)
    metadata["copied_inputs"] = copied_inputs
    metadata_path = run_dir / "eval_metadata.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with metadata_path.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
        handle.write("\n")

    return run_dir, copied_inputs


def _create_run_output(run_dir: Path, config_name: str) -> Path:
    config_dir = run_dir / config_name
    config_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(
        path
        for path in config_dir.iterdir()
        if path.is_dir() and path.name.startswith("run-")
    )
    output_dir = config_dir / f"run-{len(existing) + 1}"
    output_dir.mkdir(parents=True, exist_ok=False)
    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a local security-review benchmark run."
    )
    parser.add_argument(
        "--eval-id",
        type=int,
        required=True,
        help="Benchmark eval id from evals/evals.json",
    )
    parser.add_argument(
        "--config",
        choices=("with_skill", "without_skill"),
        default="with_skill",
        help="Target config lane to scaffold",
    )
    parser.add_argument(
        "--benchmark-root",
        help="Explicit benchmark root. Must be outside the installed skill directory.",
    )
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    cwd = Path.cwd()
    benchmark_root, benchmark_root_source, workspace_root = _resolve_benchmark_root(
        args.benchmark_root, skill_dir, cwd
    )
    _ensure_benchmark_root_allowed(benchmark_root, skill_dir)

    context_path = benchmark_root / "benchmark_context.json"
    context = _build_context(
        skill_dir, benchmark_root, benchmark_root_source, workspace_root
    )
    context_exists = _check_existing_context(context_path, context)
    if not context_exists:
        _write_context(context_path, context)

    eval_definition = _select_eval(_load_eval_catalog(skill_dir), args.eval_id)
    run_dir, copied_inputs = _copy_eval_inputs(
        skill_dir, benchmark_root, eval_definition
    )
    output_dir = _create_run_output(run_dir, args.config)

    result = {
        "benchmark_root": str(benchmark_root),
        "benchmark_root_source": benchmark_root_source,
        "context_preserved": context_exists,
        "run_dir": str(run_dir),
        "output_dir": str(output_dir),
        "copied_inputs": copied_inputs,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
