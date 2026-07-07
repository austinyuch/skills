#!/usr/bin/env python3
"""Classify-only Loop Engineering Intake eval runner.

This script intentionally does not use `opencode run`. It either dry-runs the
selected eval cases or asks Claude Code to judge expected behavior with no tools.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_IDS = "7-13"


def parse_ids(value: str) -> set[int]:
    ids: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            if end < start:
                raise ValueError(f"invalid id range: {part}")
            ids.update(range(start, end + 1))
        else:
            ids.add(int(part))
    return ids


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def build_prompt(skill_root: Path, eval_item: dict) -> str:
    skill_md = read_text(skill_root / "SKILL.md")
    intake = read_text(skill_root / "references" / "loop-engineering-intake.md")
    adapter_overview = read_text(skill_root / "references" / "adapters" / "README.md")
    write_governance = read_text(
        skill_root / "references" / "adapters" / "write-capable-governance.md"
    )
    adapter = read_text(
        skill_root
        / "references"
        / "adapters"
        / "claude-code-loop-engineering-reviewer.md"
    )

    return f"""You are running a classify-only eval for spec-master.

Do not execute the user's request.
Do not claim that any implementation, runtime startup, commit, push, or file write happened.
Judge only whether the skill instructions would route the request correctly.

Return strict JSON with this schema:
{{
  "id": <number>,
  "verdict": "pass" | "fail" | "unclear",
  "expectation_results": [
    {{"expectation": "...", "met": true | false, "reason": "..."}}
  ],
  "notes": "short summary"
}}

SKILL.md:
```md
{skill_md}
```

Loop Engineering Intake reference:
```md
{intake}
```

Adapter overview:
```md
{adapter_overview}
```

Write-capable adapter governance:
```md
{write_governance}
```

Claude Code reviewer adapter source:
```md
{adapter}
```

Eval item:
```json
{json.dumps(eval_item, ensure_ascii=False, indent=2)}
```
"""


def run_claude(prompt: str, max_budget_usd: str) -> subprocess.CompletedProcess[str]:
    cmd = [
        "claude",
        "--print",
        "--no-session-persistence",
        "--tools",
        "",
        "--max-budget-usd",
        max_budget_usd,
        prompt,
    ]
    return subprocess.run(cmd, check=False, text=True, capture_output=True)


def parse_model_json(text: str) -> tuple[dict | None, str | None]:
    stripped = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL)
    if match:
        stripped = match.group(1).strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        return None, str(exc)
    return parsed, None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run classify-only evals for spec-master Loop Engineering cases."
    )
    parser.add_argument(
        "--skill-root",
        default="skills/spec-master",
        help="Path to the spec-master skill directory.",
    )
    parser.add_argument(
        "--evals",
        default="skills/spec-master/evals/evals.json",
        help="Path to evals.json.",
    )
    parser.add_argument(
        "--ids",
        default=DEFAULT_IDS,
        help="Comma-separated eval ids or ranges, default: 7-13.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Call Claude. Omit for dry-run validation only.",
    )
    parser.add_argument(
        "--max-budget-usd",
        default="1.00",
        help="Per-case Claude budget when --execute is used.",
    )
    args = parser.parse_args()

    skill_root = Path(args.skill_root)
    eval_path = Path(args.evals)
    selected_ids = parse_ids(args.ids)
    data = json.loads(read_text(eval_path))
    evals = [item for item in data.get("evals", []) if item.get("id") in selected_ids]

    if not evals:
        raise SystemExit(f"no evals matched ids: {args.ids}")

    if not args.execute:
        print(
            json.dumps(
                {
                    "mode": "dry-run",
                    "selected_ids": [item["id"] for item in evals],
                    "execute_hint": "rerun with --execute to call Claude with no tools",
                    "runner": "claude --print --no-session-persistence --tools ''",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    results = []
    failed = False
    for item in evals:
        prompt = build_prompt(skill_root, item)
        completed = run_claude(prompt, args.max_budget_usd)
        parsed, parse_error = parse_model_json(completed.stdout)
        verdict = parsed.get("verdict") if isinstance(parsed, dict) else None
        passed = completed.returncode == 0 and verdict == "pass"
        result = {
            "id": item["id"],
            "returncode": completed.returncode,
            "passed": passed,
            "parsed": parsed,
            "parse_error": parse_error,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
        results.append(result)
        if not passed:
            failed = True

    print(json.dumps({"mode": "execute", "results": results}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
