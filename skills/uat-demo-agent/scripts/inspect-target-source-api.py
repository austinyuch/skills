#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


SCHEMA_VERSION = "uatdemo-target-source-api-discovery/v1"
IGNORED_DIRS = {
    ".agents",
    ".claude",
    ".codex",
    ".git",
    ".code-review",
    ".kiro",
    ".uatdemo",
    ".venv",
    "build",
    "coverage",
    "node_modules",
    "target",
    "temp",
    "tmp",
    "vendor",
}
TEXT_SUFFIXES = {
    ".go",
    ".js",
    ".jsx",
    ".json",
    ".md",
    ".mjs",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}
SERVER_ENV_PATTERNS = (
    "VITE_OPENCODE_SERVER_HOST",
    "VITE_OPENCODE_SERVER_PORT",
    "PLAYWRIGHT_SERVER_HOST",
    "PLAYWRIGHT_SERVER_PORT",
    "OPENCODE_SERVER",
    "GOCODE",
)
API_ROUTE_PATTERNS = (
    "huma.DefaultConfig",
    "OpenAPI",
    "/doc",
    "/openapi",
    "HandleFunc(",
    ".Handle(",
    "router.",
)
GRAPH_QUERIES = [
    "OpenAPI contract manifest doc route",
    "Playwright server host port gocode backend binding",
    "browser e2e harness original OpenCode web interface gocode backend",
]


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def compact_text(text: str, limit: int = 2400) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "...[truncated]"


def find_review_cli(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    env_cli = os.environ.get("CODE_REVIEW_CLI")
    if env_cli:
        return env_cli

    home = Path.home()
    candidates = [
        home / ".agents/skills/code-review/scripts/review-cli-linux-amd64",
        home / ".codex/skills/code-review/scripts/review-cli-linux-amd64",
        home / ".config/opencode/skills/code-review/scripts/review-cli-linux-amd64",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return shutil.which("review-cli-linux-amd64") or shutil.which("review-cli")


def extract_json_object(text: str) -> dict | None:
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", text):
        try:
            value, _ = decoder.raw_decode(text[match.start() :])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def run_graph_preflight(target_root: Path, review_cli: str | None) -> dict:
    if not review_cli:
        return {
            "status": "unavailable",
            "reason": "code-review CLI was not found",
            "authority": "static-analysis-only",
        }

    env = os.environ.copy()
    env.setdefault("CODE_REVIEW_PERSISTENCE_MODE", "local-sqlite")
    env.setdefault("CODE_REVIEW_SQLITE_ENABLED", "true")
    env.setdefault("CODE_REVIEW_SQLITE_PROJECT_STATE_DIR", ".code-review")
    command = [review_cli, "init", str(target_root), "--graph", "--status-only"]

    try:
        result = subprocess.run(
            command,
            cwd=target_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        return {
            "status": "unavailable",
            "reviewCli": review_cli,
            "reason": "code-review CLI path does not exist",
            "authority": "static-analysis-only",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "timeout",
            "reviewCli": review_cli,
            "stdout": compact_text(exc.stdout or ""),
            "stderr": compact_text(exc.stderr or ""),
            "authority": "static-analysis-only",
        }

    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    payload = extract_json_object(combined)
    status = "ok" if result.returncode == 0 else "failed"
    preflight = {
        "status": status,
        "reviewCli": review_cli,
        "returnCode": result.returncode,
        "stdout": compact_text(result.stdout or ""),
        "stderr": compact_text(result.stderr or ""),
        "authority": "static-analysis-only",
    }
    if payload:
        preflight["payload"] = payload
        preflight["graphQueryable"] = bool(payload.get("graph_queryable"))
        preflight["recommendedQueryMode"] = payload.get("recommended_query_mode")
        preflight["relationCoverageStatus"] = payload.get("relation_coverage_status")
    return preflight


def run_graph_queries(target_root: Path, review_cli: str | None, preflight: dict) -> list[dict]:
    if not review_cli:
        return [{"status": "skipped", "reason": "code-review CLI was not found"}]
    if not preflight.get("graphQueryable"):
        return [
            {
                "status": "skipped",
                "reason": "graph is not queryable",
                "recommendedQueryMode": preflight.get("recommendedQueryMode"),
            }
        ]

    results: list[dict] = []
    env = os.environ.copy()
    env.setdefault("CODE_REVIEW_PERSISTENCE_MODE", "local-sqlite")
    env.setdefault("CODE_REVIEW_SQLITE_ENABLED", "true")
    env.setdefault("CODE_REVIEW_SQLITE_PROJECT_STATE_DIR", ".code-review")
    for query in GRAPH_QUERIES:
        command = [
            review_cli,
            "search-code",
            str(target_root),
            query,
            "--graph-only",
            "--graph-init",
            "skip",
        ]
        try:
            result = subprocess.run(
                command,
                cwd=target_root,
                env=env,
                capture_output=True,
                text=True,
                timeout=20,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            results.append(
                {
                    "query": query,
                    "status": "failed",
                    "reason": exc.__class__.__name__,
                    "authority": "static-analysis-only",
                }
            )
            continue
        results.append(
            {
                "query": query,
                "status": "ok" if result.returncode == 0 else "failed",
                "returnCode": result.returncode,
                "stdout": compact_text(result.stdout or "", 1200),
                "stderr": compact_text(result.stderr or "", 1200),
                "authority": "static-analysis-only",
            }
        )
    return results


def iter_candidate_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root):
        current_path = Path(current)
        kept_dirs = []
        for dirname in dirs:
            if dirname in IGNORED_DIRS:
                continue
            if dirname == "dist" and current_path.name != "contracts":
                continue
            kept_dirs.append(dirname)
        dirs[:] = kept_dirs

        for name in names:
            path = current_path / name
            suffix = path.suffix.lower()
            if suffix not in TEXT_SUFFIXES:
                continue
            try:
                if path.stat().st_size > 1_000_000:
                    continue
            except OSError:
                continue
            files.append(path)
    return sorted(files)


def matching_lines(text: str, patterns: tuple[str, ...], limit: int = 6) -> list[dict]:
    matches: list[dict] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if any(pattern in line for pattern in patterns):
            matches.append({"line": number, "text": line.strip()[:240]})
        if len(matches) >= limit:
            break
    return matches


def evidence_priority(item: dict) -> tuple[int, str]:
    path = str(item.get("path", ""))
    score = 100
    if path.startswith("packages/gocode/"):
        score -= 50
    if path == "packages/app/playwright.config.gocode.ts":
        score -= 50
    if "/contracts/dist/" in f"/{path}":
        score -= 20
    if "doc_handler" in path or "openapi" in path:
        score -= 10
    if "/e2e/" in f"/{path}/" or "playwright.config" in path:
        score -= 10
    return (score, path)


def sort_evidence(items: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for item in items:
        key = (str(item.get("kind", "")), str(item.get("path", "")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return sorted(deduped, key=evidence_priority)


def unique_paths(items: list[dict], limit: int) -> list[str]:
    paths: list[str] = []
    for item in items:
        path = str(item.get("path", ""))
        if path and path not in paths:
            paths.append(path)
        if len(paths) >= limit:
            break
    return paths


def scan_source(root: Path) -> dict:
    api_contracts: list[dict] = []
    frontend_surfaces: list[dict] = []
    backend_surfaces: list[dict] = []
    bindings: list[dict] = []

    for path in iter_candidate_files(root):
        path_rel = rel(path, root)
        lower = path_rel.lower()
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue

        if path.name == "manifest.json" and "/contracts/dist/" in f"/{lower}":
            api_contracts.append(
                {
                    "kind": "contract-manifest",
                    "path": path_rel,
                    "claim": "target exposes a generated contract manifest",
                }
            )
        if "openapi" in lower or "swagger" in lower:
            api_contracts.append(
                {
                    "kind": "openapi-artifact",
                    "path": path_rel,
                    "claim": "target has an API contract artifact candidate",
                }
            )

        route_hits = matching_lines(text, API_ROUTE_PATTERNS)
        if route_hits:
            entry = {
                "kind": "api-route-source",
                "path": path_rel,
                "evidence": route_hits,
            }
            if "doc_handler" in lower or "openapi" in lower or "huma." in text:
                api_contracts.append(entry)
            else:
                backend_surfaces.append(entry)

        if Path(lower).name.startswith("playwright.config"):
            frontend_surfaces.append(
                {
                    "kind": "playwright-config",
                    "path": path_rel,
                    "evidence": matching_lines(text, SERVER_ENV_PATTERNS + ("webServer", "baseURL")),
                }
            )
        elif "/e2e/" in f"/{lower}/" or lower.endswith(".spec.ts"):
            e2e_hits = matching_lines(text, SERVER_ENV_PATTERNS + ("page.goto", "expect("))
            if e2e_hits:
                frontend_surfaces.append(
                    {
                        "kind": "browser-e2e-source",
                        "path": path_rel,
                        "evidence": e2e_hits,
                    }
                )

        binding_hits = matching_lines(text, SERVER_ENV_PATTERNS)
        if binding_hits:
            bindings.append(
                {
                    "kind": "frontend-backend-env-binding",
                    "path": path_rel,
                    "evidence": binding_hits,
                }
            )

    return {
        "apiContracts": sort_evidence(api_contracts),
        "frontendSurfaces": sort_evidence(frontend_surfaces),
        "backendSurfaces": sort_evidence(backend_surfaces),
        "frontendBackendBindings": sort_evidence(bindings),
    }


def build_candidate_assertions(scan: dict) -> tuple[list[dict], list[dict]]:
    candidates: list[dict] = []
    blocked: list[dict] = []

    if scan["apiContracts"]:
        candidates.append(
            {
                "assertionKind": "api-contract-readback",
                "evidencePaths": unique_paths(scan["apiContracts"], 6),
                "nextStep": "derive route/status/response-shape predicates from the contract artifact before marking a browser/API step executable",
            }
        )
    else:
        blocked.append(
            {
                "assertionKind": "api-contract-readback",
                "blockedReason": "no API contract or doc-route source candidate was discovered",
            }
        )

    if scan["frontendSurfaces"] and scan["frontendBackendBindings"]:
        candidates.append(
            {
                "assertionKind": "browser-surface-binding",
                "evidencePaths": unique_paths(
                    scan["frontendSurfaces"] + scan["frontendBackendBindings"],
                    8,
                ),
                "nextStep": "bind Playwright baseURL/server env to concrete UI or API assertions in the generated project profile or hand-authored UAT plan",
            }
        )
    else:
        blocked.append(
            {
                "assertionKind": "browser-surface-binding",
                "blockedReason": "both a browser surface and a frontend-backend binding are required before generating executable browser steps",
            }
        )

    return candidates, blocked


def build_report(target_root: Path, review_cli: str | None) -> dict:
    graph_preflight = run_graph_preflight(target_root, review_cli)
    graph_queries = run_graph_queries(target_root, review_cli, graph_preflight)
    scan = scan_source(target_root)
    candidates, blocked = build_candidate_assertions(scan)

    return {
        "schemaVersion": SCHEMA_VERSION,
        "targetProject": {
            "rootPath": str(target_root),
            "projectId": target_root.name,
        },
        "codeReviewGraph": graph_preflight,
        "codeReviewGraphQueries": graph_queries,
        "discoveryEvidence": {
            "sourceScan": {
                "status": "ok",
                "filesConsidered": len(iter_candidate_files(target_root)),
            }
        },
        **scan,
        "candidateAssertions": candidates,
        "blockedAssertions": blocked,
        "claimBoundary": {
            "authority": "static-analysis-only",
            "runtimeReadiness": "not-proven",
            "notes": [
                "code-review graph and direct source scans can justify assertion candidates",
                "only plan validate/run uat/report verification can justify executable UAT pass claims",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-root", required=True, help="Target repository root")
    parser.add_argument("--out", help="Optional JSON output path")
    parser.add_argument("--review-cli", help="Optional code-review CLI path")
    args = parser.parse_args()

    target_root = Path(args.target_root).expanduser().resolve()
    if not target_root.exists() or not target_root.is_dir():
        print(f"target root not found: {target_root}", file=sys.stderr)
        return 1

    review_cli = find_review_cli(args.review_cli)
    report = build_report(target_root, review_cli)
    output = json.dumps(report, indent=2, sort_keys=True)

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
