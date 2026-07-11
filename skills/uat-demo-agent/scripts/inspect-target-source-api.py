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
MAX_SCAN_FILE_BYTES = 1_000_000
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
ASSISTANT_GENERATION_PATTERNS = (
    "llm.Stream",
    "provider.Request",
    "providerID",
    "modelID",
    "role: \"assistant\"",
    'Role == "assistant"',
    "NewMessage(\"assistant\"",
    "NewMessageWithParts(\"assistant\"",
    "assistantMessage",
    "SessionExecution",
    "noReply",
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


def run_review_cli_command(
    command: list[str],
    target_root: Path,
    env: dict[str, str],
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=target_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


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
        result = run_review_cli_command(command, target_root, env, 30)
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
            result = run_review_cli_command(command, target_root, env, 20)
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
                if path.stat().st_size > MAX_SCAN_FILE_BYTES:
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
    if "/internal/session/" in f"/{path}/":
        score -= 15
    if path.endswith("_test.go") or ".spec." in path:
        score += 25
    if path.endswith(("processor.go", "loop.go", "title.go", "compactor.go")):
        score -= 10
    if "session-timeline" in path or "uatdemo-ui-screenshot" in path:
        score -= 12
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


def scan_api_evidence(path: Path, path_rel: str, lower: str, text: str) -> dict[str, list[dict]]:
    api_contracts: list[dict] = []
    backend_surfaces: list[dict] = []

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

    return {
        "apiContracts": api_contracts,
        "backendSurfaces": backend_surfaces,
    }


def scan_frontend_evidence(path_rel: str, lower: str, text: str) -> dict[str, list[dict]]:
    frontend_surfaces: list[dict] = []
    frontend_backend_bindings: list[dict] = []

    if Path(lower).name.startswith("playwright.config"):
        frontend_surfaces.append(
            {
                "kind": "playwright-config",
                "path": path_rel,
                "evidence": matching_lines(
                    text,
                    SERVER_ENV_PATTERNS + ("webServer", "baseURL"),
                ),
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
        frontend_backend_bindings.append(
            {
                "kind": "frontend-backend-env-binding",
                "path": path_rel,
                "evidence": binding_hits,
            }
        )

    return {
        "frontendSurfaces": frontend_surfaces,
        "frontendBackendBindings": frontend_backend_bindings,
    }


def scan_assistant_generation_evidence(path_rel: str, lower: str, text: str) -> list[dict]:
    hits = matching_lines(text, ASSISTANT_GENERATION_PATTERNS)
    if not hits:
        return []

    kind = "assistant-generation-source"
    claim = "target source has assistant-generation or assistant-message evidence"
    if any("noReply" in hit["text"] for hit in hits):
        kind = "no-reply-boundary-source"
        claim = "target source has a no-reply persisted-message boundary that must not be confused with assistant generation"
    elif "/e2e/" in f"/{lower}/" or lower.endswith(".spec.ts"):
        kind = "assistant-browser-e2e-source"
        claim = "target browser tests include assistant-message or provider-model evidence candidates"
    elif "/internal/session/" in f"/{lower}/" or "llm.Stream" in text or "provider.Request" in text:
        kind = "assistant-generation-runtime-source"
        claim = "target backend/session source contains provider-backed assistant-generation flow evidence"

    return [
        {
            "kind": kind,
            "path": path_rel,
            "claim": claim,
            "evidence": hits,
        }
    ]


def scan_file(root: Path, path: Path) -> dict[str, list[dict]]:
    path_rel = rel(path, root)
    lower = path_rel.lower()
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return {
            "apiContracts": [],
            "frontendSurfaces": [],
            "backendSurfaces": [],
            "frontendBackendBindings": [],
            "assistantGenerationSurfaces": [],
        }

    api_scan = scan_api_evidence(path, path_rel, lower, text)
    frontend_scan = scan_frontend_evidence(path_rel, lower, text)
    assistant_scan = scan_assistant_generation_evidence(path_rel, lower, text)
    return {
        "apiContracts": api_scan["apiContracts"],
        "frontendSurfaces": frontend_scan["frontendSurfaces"],
        "backendSurfaces": api_scan["backendSurfaces"],
        "frontendBackendBindings": frontend_scan["frontendBackendBindings"],
        "assistantGenerationSurfaces": assistant_scan,
    }


def scan_source(root: Path, files: list[Path]) -> dict:
    api_contracts: list[dict] = []
    frontend_surfaces: list[dict] = []
    backend_surfaces: list[dict] = []
    bindings: list[dict] = []
    assistant_surfaces: list[dict] = []

    for path in files:
        file_scan = scan_file(root, path)
        api_contracts.extend(file_scan["apiContracts"])
        frontend_surfaces.extend(file_scan["frontendSurfaces"])
        backend_surfaces.extend(file_scan["backendSurfaces"])
        bindings.extend(file_scan["frontendBackendBindings"])
        assistant_surfaces.extend(file_scan["assistantGenerationSurfaces"])

    return {
        "apiContracts": sort_evidence(api_contracts),
        "frontendSurfaces": sort_evidence(frontend_surfaces),
        "backendSurfaces": sort_evidence(backend_surfaces),
        "frontendBackendBindings": sort_evidence(bindings),
        "assistantGenerationSurfaces": sort_evidence(assistant_surfaces),
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

    assistant_runtime = [
        item
        for item in scan["assistantGenerationSurfaces"]
        if item.get("kind") == "assistant-generation-runtime-source"
    ]
    assistant_browser = [
        item
        for item in scan["assistantGenerationSurfaces"]
        if item.get("kind") == "assistant-browser-e2e-source"
    ]
    if assistant_runtime and (assistant_browser or scan["frontendSurfaces"]):
        candidates.append(
            {
                "assertionKind": "assistant-generation-ui-journey",
                "evidencePaths": unique_paths(
                    assistant_runtime
                    + assistant_browser
                    + scan["frontendSurfaces"]
                    + scan["frontendBackendBindings"],
                    10,
                ),
                "nextStep": "target repo must define provider/deterministic generation posture, assistant-response marker, UI selectors, live uatdemo plan validate/run uat evidence, screenshot artifact, and fail-closed report guard before any assistant-generation readiness claim",
                "claimBoundary": "static-source-candidate-only",
            }
        )
    else:
        blocked.append(
            {
                "assertionKind": "assistant-generation-ui-journey",
                "blockedReason": "assistant-generation runtime source plus browser/UI evidence are required before requesting a target-owned generated assistant-response proof",
            }
        )

    return candidates, blocked


def build_preflight_decision(
    graph_preflight: dict,
    candidate_file_count: int,
    candidates: list[dict],
    blocked: list[dict],
) -> dict:
    graph_queryable = bool(graph_preflight.get("graphQueryable"))
    if graph_queryable:
        graph_step = "graph-preflight-queryable-then-focused-graph-queries"
    else:
        graph_step = "graph-preflight-recorded-then-direct-source-fallback"

    if candidates:
        next_action = "author-bounded-assertion-candidates"
    elif blocked:
        next_action = "record-blocked-assertions-with-source-scan-evidence"
    else:
        next_action = "record-empty-source-scan-boundary"

    return {
        "sourceAvailable": True,
        "graphPreflight": graph_step,
        "directSourceScan": "required-and-completed",
        "insufficientDataVerdictAllowed": False,
        "notEnoughDataPolicy": "do-not-stop-before-graph-preflight-and-direct-source-scan",
        "candidateFileCount": candidate_file_count,
        "candidateAssertionCount": len(candidates),
        "blockedAssertionCount": len(blocked),
        "nextAction": next_action,
    }


def build_report(target_root: Path, review_cli: str | None) -> dict:
    graph_preflight = run_graph_preflight(target_root, review_cli)
    graph_queries = run_graph_queries(target_root, review_cli, graph_preflight)
    candidate_files = iter_candidate_files(target_root)
    scan = scan_source(target_root, candidate_files)
    candidates, blocked = build_candidate_assertions(scan)
    preflight_decision = build_preflight_decision(
        graph_preflight,
        len(candidate_files),
        candidates,
        blocked,
    )

    return {
        "schemaVersion": SCHEMA_VERSION,
        "targetProject": {
            "rootPath": str(target_root),
            "projectId": target_root.name,
        },
        "codeReviewGraph": graph_preflight,
        "codeReviewGraphQueries": graph_queries,
        "preflightDecision": preflight_decision,
        "discoveryEvidence": {
            "sourceScan": {
                "status": "ok",
                "filesConsidered": len(candidate_files),
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


def render_evidence_paths(paths: list[str]) -> list[str]:
    if not paths:
        return ["  - Evidence paths: none recorded"]
    lines = ["  - Evidence paths:"]
    for path in paths:
        lines.append(f"    - `{path}`")
    return lines


def render_handoff_markdown(report: dict, *, redact_local_root: bool = False) -> str:
    target = report["targetProject"]
    target_root = "<target-root>" if redact_local_root else target["rootPath"]
    preflight = report["preflightDecision"]
    graph = report["codeReviewGraph"]
    candidates = report["candidateAssertions"]
    blocked = report["blockedAssertions"]
    assistant_surfaces = report["assistantGenerationSurfaces"]

    lines = [
        "# Target Source/API Discovery Handoff",
        "",
        f"- Target project: `{target['projectId']}`",
        f"- Target root: `{target_root}`",
        f"- Schema: `{report['schemaVersion']}`",
        f"- Graph status: `{graph.get('status', 'unknown')}`",
        f"- Graph queryable: `{bool(graph.get('graphQueryable'))}`",
        f"- Preflight: `{preflight['graphPreflight']}`",
        f"- Direct source scan: `{preflight['directSourceScan']}`",
        f"- Candidate assertions: `{preflight['candidateAssertionCount']}`",
        f"- Blocked assertions: `{preflight['blockedAssertionCount']}`",
        f"- Runtime readiness: `{report['claimBoundary']['runtimeReadiness']}`",
        "",
        "## Claim Boundary",
        "",
        "This handoff is static-analysis-only. It can justify target-owned follow-up work,",
        "but it does not prove runtime readiness, generated assistant behavior, screenshot",
        "evidence, deployment status, or provider coverage.",
        "",
        "## Candidate Assertions",
        "",
    ]

    if candidates:
        for candidate in candidates:
            lines.extend(
                [
                    f"### `{candidate['assertionKind']}`",
                    "",
                    f"- Claim boundary: `{candidate.get('claimBoundary', 'static-source-candidate-only')}`",
                    f"- Next step: {candidate['nextStep']}",
                ]
            )
            lines.extend(render_evidence_paths(candidate.get("evidencePaths", [])))
            lines.append("")
    else:
        lines.extend(["No assertion candidates were discovered.", ""])

    lines.extend(["## Blocked Assertions", ""])
    if blocked:
        for item in blocked:
            lines.extend(
                [
                    f"- `{item['assertionKind']}`: {item['blockedReason']}",
                ]
            )
        lines.append("")
    else:
        lines.extend(["No blocked assertions were emitted.", ""])

    lines.extend(["## Assistant-Generation Surfaces", ""])
    if assistant_surfaces:
        for item in assistant_surfaces[:12]:
            lines.extend(
                [
                    f"- `{item['kind']}` in `{item['path']}`",
                    f"  - {item['claim']}",
                ]
            )
        if len(assistant_surfaces) > 12:
            omitted = len(assistant_surfaces) - 12
            lines.append(f"- Additional assistant-generation surfaces omitted: {omitted}")
        lines.append("")
    else:
        lines.extend(
            [
                "No assistant-generation source evidence was discovered.",
                "",
            ]
        )

    has_assistant_candidate = any(
        item.get("assertionKind") == "assistant-generation-ui-journey"
        for item in candidates
    )
    if has_assistant_candidate:
        lines.extend(
            [
                "## Target-Owned Assistant-Generation Gates",
                "",
                "Before closing a richer assistant-generation UI journey CR, "
                "the target repo must provide:",
                "",
                "1. generation mode and provider/deterministic-fixture posture, "
                "with fixture-backed evidence labeled as such;",
                "2. target-owned composer, submit, settled-state, assistant-response, "
                "and screenshot selectors;",
                "3. state/API evidence that distinguishes a generated assistant response "
                "from a seeded user-message fixture;",
                "4. a `uatdemo` visual assertion catalog entry or handoff plan that uses "
                "only target-owned selectors;",
                "5. live `uatdemo plan validate` and `uatdemo run uat` evidence;",
                "6. screenshot bytes and committed JSON/Markdown evidence; and",
                "7. a fail-closed target report writer guard that refuses partial, failed, "
                "or marker-missing runs.",
                "",
            ]
        )

    lines.extend(
        [
            "## Non-Goals",
            "",
            "- Do not claim a PASS from this handoff.",
            "- Do not treat no-reply or seeded persisted-message visibility as assistant generation.",
            "- Do not invent target selectors, prompt behavior, provider semantics, "
            "or accepted evidence boundaries outside the target repo.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-root", required=True, help="Target repository root")
    parser.add_argument("--out", help="Optional JSON output path")
    parser.add_argument("--handoff-md", help="Optional Markdown handoff output path")
    parser.add_argument(
        "--handoff-redact-local-root",
        action="store_true",
        help="write <target-root> instead of the absolute local target path in Markdown handoff output",
    )
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
    if args.handoff_md:
        handoff_path = Path(args.handoff_md).expanduser().resolve()
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        handoff_path.write_text(
            render_handoff_markdown(
                report,
                redact_local_root=args.handoff_redact_local_root,
            )
            + "\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
