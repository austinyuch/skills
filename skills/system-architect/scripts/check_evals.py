#!/usr/bin/env python3
"""Static eval metadata check for the system-architect skill."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON: {exc}")


def main() -> None:
    evals = load_json(ROOT / "evals" / "evals.json")
    triggers = load_json(ROOT / "evals" / "trigger-eval.json")

    if evals.get("skill_name") != "system-architect":
        fail("evals.json must declare skill_name=system-architect")

    cases = evals.get("evals")
    if not isinstance(cases, list) or len(cases) < 4:
        fail("evals.json must contain at least four evals")

    for case in cases:
        for key in ("id", "prompt", "expected_output", "expectations"):
            if key not in case:
                fail(f"eval case missing {key}: {case}")
        if not isinstance(case["expectations"], list) or not case["expectations"]:
            fail(f"eval case has no expectations: {case['id']}")

    if not isinstance(triggers, list) or len(triggers) < 6:
        fail("trigger-eval.json must contain positive and negative cases")

    positives = [item for item in triggers if item.get("should_trigger") is True]
    negatives = [item for item in triggers if item.get("should_trigger") is False]
    if len(positives) < 4 or len(negatives) < 3:
        fail("trigger-eval.json must include at least four positive and three negative cases")

    trigger_text = "\n".join(item.get("query", "") for item in triggers)
    required_terms = [
        "architecture",
        "code-review",
        "GraphRAG",
        "Sprint review",
        "IBM SAA",
        ".agents/steering",
    ]
    missing = [term for term in required_terms if term not in trigger_text]
    if missing:
        fail(f"trigger-eval.json missing coverage terms: {', '.join(missing)}")

    print("system-architect eval metadata is valid")


if __name__ == "__main__":
    main()
