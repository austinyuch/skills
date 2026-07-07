#!/usr/bin/env python3
"""Lightweight validation gate for governance writeback lanes."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys


REQUIRED_EVIDENCE_FIELDS = [
    "Lane Identity:",
    "Branch Identity:",
    "Lane Role:",
    "Artifact / Scope Owned:",
    "Upstream Authority Basis:",
    "Freshness Check Point:",
    "Conflict Status:",
    "Owner / Handoff Owner:",
    "Next Action:",
]

FIELD_VALUE_PATTERN = re.compile(r"^(?P<label>[^:\n]+:)[ \t]*(?P<value>.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    message: str


@dataclass(frozen=True)
class UpstreamClassification:
    classification: str
    relative_path: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate governance writeback evidence and upstream ordering"
    )
    parser.add_argument("--workspace", required=True, help="Invoking repo/workspace root")
    parser.add_argument(
        "--target-surface",
        required=True,
        choices=["folder-tests", "workspace-tests", "specs", "rtm", "shared-governance"],
        help="Authoritative surface about to be written",
    )
    parser.add_argument("--evidence-file", required=True, help="Repo/workspace-local ownership evidence markdown file")
    parser.add_argument("--upstream", action="append", default=[], help="Upstream file path used for this writeback (repeatable)")
    parser.add_argument("--expect-scope-token", action="append", default=[], help="Optional token that should appear in evidence content")
    return parser.parse_args()


def resolve_existing_path(raw_path: str) -> Path:
    return Path(raw_path).expanduser().resolve()


def ensure_under_workspace(path: Path, workspace: Path) -> bool:
    try:
        path.relative_to(workspace)
        return True
    except ValueError:
        return False


def classify_path(path: Path, workspace: Path) -> str:
    rel = path.relative_to(workspace).as_posix() if ensure_under_workspace(path, workspace) else path.as_posix()
    if path.name in {"requirements.md", "design.md", "tasks.md", "review.md"}:
        return "source-authority"
    if "/reports/" in f"/{rel}" or "/change-requests/" in f"/{rel}":
        return "source-authority"
    if path.name == "TESTS.md":
        return "workspace-tests" if rel == ".agents/specs/TESTS.md" else "folder-tests"
    if path.name == "SPECS.md":
        return "specs"
    if path.name == "RTM.md":
        return "rtm"
    if path.name == "NEXT_STEPS.md":
        return "rolling-memo"
    return "other"


def collect_upstream_classifications(workspace: Path, upstreams: list[Path]) -> list[UpstreamClassification]:
    rows: list[UpstreamClassification] = []
    for upstream in upstreams:
        try:
            relative_path = upstream.relative_to(workspace).as_posix()
        except ValueError:
            relative_path = upstream.as_posix()
        rows.append(
            UpstreamClassification(
                classification=classify_path(upstream, workspace) if upstream.exists() and ensure_under_workspace(upstream, workspace) else "outside-workspace-or-missing",
                relative_path=relative_path,
            )
        )
    return sorted(rows, key=lambda row: row.relative_path)


def validate_evidence_file(workspace: Path, evidence_file: Path, expect_scope_tokens: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not evidence_file.exists():
        return [ValidationIssue("ERROR", f"Evidence file not found: {evidence_file}")]
    if not ensure_under_workspace(evidence_file, workspace):
        issues.append(ValidationIssue("ERROR", "Evidence file must live inside the invoking workspace"))
    content = evidence_file.read_text(encoding="utf-8", errors="replace")
    parsed_values = {
        match.group("label"): match.group("value").strip()
        for match in FIELD_VALUE_PATTERN.finditer(content)
    }
    for field in REQUIRED_EVIDENCE_FIELDS:
        if field not in content:
            issues.append(ValidationIssue("ERROR", f"Missing required evidence field: {field}"))
        elif not parsed_values.get(field):
            issues.append(ValidationIssue("ERROR", f"Required evidence field has no value: {field}"))
    if not expect_scope_tokens:
        issues.append(ValidationIssue("ERROR", "At least one --expect-scope-token is required to bind evidence to the intended lane/scope"))
    for token in expect_scope_tokens:
        if token not in content:
            issues.append(ValidationIssue("ERROR", f"Evidence file is missing expected scope token: {token}"))
    lowered = content.lower()
    for marker in ["/.config/opencode/skills/", "worktree path:", "detached compare", "tmp/", "ports:", "containers:", "env locks"]:
        if marker.lower() in lowered:
            issues.append(ValidationIssue("ERROR", f"Evidence file contains forbidden machine-local marker: {marker}"))
    return issues


def validate_upstreams(workspace: Path, target_surface: str, upstreams: list[Path]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not upstreams:
        return [ValidationIssue("ERROR", "At least one --upstream path is required")]

    classes: list[str] = []
    for upstream in upstreams:
        if not upstream.exists():
            issues.append(ValidationIssue("ERROR", f"Upstream file not found: {upstream}"))
            continue
        if not ensure_under_workspace(upstream, workspace):
            issues.append(ValidationIssue("ERROR", f"Upstream file must live inside the invoking workspace: {upstream}"))
            continue
        classes.append(classify_path(upstream, workspace))

    if any(cls == "rolling-memo" for cls in classes):
        issues.append(ValidationIssue("ERROR", "NEXT_STEPS.md cannot be used as an upstream authority"))

    if target_surface == "folder-tests":
        if any(cls in {"workspace-tests", "specs", "rtm"} for cls in classes):
            issues.append(ValidationIssue("ERROR", "folder-level TESTS.md cannot be regenerated from derived artifacts"))
    elif target_surface == "workspace-tests":
        if "folder-tests" not in classes:
            issues.append(ValidationIssue("ERROR", "workspace TESTS rollup requires at least one folder-level TESTS.md upstream"))
        if any(cls in {"specs", "rtm"} for cls in classes):
            issues.append(ValidationIssue("ERROR", "workspace TESTS rollup cannot use SPECS.md or RTM.md as upstream authority"))
    elif target_surface == "specs":
        if "rtm" in classes:
            issues.append(ValidationIssue("ERROR", "SPECS.md cannot use RTM.md as an upstream source"))
        if not any(cls in {"source-authority", "folder-tests", "workspace-tests"} for cls in classes):
            issues.append(ValidationIssue("ERROR", "SPECS.md writeback must include source authority or TESTS upstream summaries"))
    elif target_surface == "rtm":
        if "specs" in classes:
            issues.append(ValidationIssue("ERROR", "RTM.md cannot use SPECS.md as an upstream source; regenerate from source authority or TESTS upstream summaries"))
        if not any(cls in {"source-authority", "folder-tests", "workspace-tests"} for cls in classes):
            issues.append(ValidationIssue("ERROR", "RTM.md writeback must be regenerated from source authority or TESTS upstream summaries"))
    elif target_surface == "shared-governance":
        if any(cls in {"workspace-tests", "specs", "rtm"} for cls in classes) and not any(cls == "source-authority" for cls in classes):
            issues.append(ValidationIssue("ERROR", "Shared-governance writeback must include source-authority context, not only derived artifacts"))

    return issues


def main() -> int:
    args = parse_args()
    workspace = resolve_existing_path(args.workspace)
    evidence_file = resolve_existing_path(args.evidence_file)
    upstreams = [resolve_existing_path(path) for path in args.upstream]

    if not workspace.exists():
        print(f"ERROR: Workspace not found: {workspace}")
        return 1

    issues: list[ValidationIssue] = []
    classifications = collect_upstream_classifications(workspace, upstreams)
    issues.extend(validate_evidence_file(workspace, evidence_file, args.expect_scope_token))
    issues.extend(validate_upstreams(workspace, args.target_surface, upstreams))

    print("Upstream classifications:")
    for row in classifications:
        print(f"- {row.classification}\t{row.relative_path}")

    if issues:
        print("FAIL: governance writeback validation failed")
        for issue in issues:
            print(f"- {issue.level}: {issue.message}")
        return 1

    print("PASS: governance writeback validation succeeded")
    print(f"- target surface: {args.target_surface}")
    print(f"- evidence file: {evidence_file}")
    print(f"- upstream count: {len(upstreams)}")
    print(f"- scope tokens: {len(args.expect_scope_token)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
