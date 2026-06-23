---
name: test-quality-reviewer
description: Judge the quality and effectiveness of EXISTING tests, not just whether they pass. Use when reviewing or refactoring test code, when asked "are these tests any good / thorough / brittle", when tests pass but you suspect weak assertions, or as the test-review pass of a code review. Flags test smells (assertion roulette, mystery guest, fragile/conditional tests), FIRST violations, missing boundary/negative cases, and test-pyramid inversion. Orchestrated by the code-review skill alongside capability-mapper and code-summarizer.
---

# test-quality-reviewer

## Overview

A hybrid reviewer skill: a **deterministic detector** flags test smells and FIRST /
test-pyramid violations in a test file offline, and an **optional LLM pass** calibrates
severity and writes developer-actionable reasoning. The deterministic findings are the
source of truth and need no provider, so this is safe in CI. "Green" only means a test
ran; this skill asks the harder question — *would a real defect survive it?*

It complements the `code-review` graph/capability inventory, which sees structure and
business mapping but does not judge whether the tests guarding that structure are any good.

## Contract

Invocation: `python3 scripts/run.py '<json>'` (also accepts JSON on stdin).

Input — a single test file (pass `content` to skip the disk read):
```json
{"file": "internal/order/fulfilment_test.go"}
```

Output (stdout, one JSON object): `skill_version`, `target`, `language`, `explained`,
`summary` (counts by severity + rule), and `findings[]` where each finding carries
`rule`, `file`, `line`, `severity`, `confidence`, `evidence`, `reasoning`, `remediation`.

An **empty `findings` list is a valid PASS.** The script exits non-zero only on bad input,
or when `--explain` was requested but the provider failed — it never fabricates findings.

### Rules detected

| Rule | Principle | What it means |
|------|-----------|---------------|
| `NO_ASSERTION` | FIRST: Self-validating | Test body has no assertion — a mutant survives it. |
| `ASSERTION_ROULETTE` | Clean tests | Many unlabeled asserts — failures are ambiguous. |
| `MYSTERY_GUEST` | FIRST: Repeatable | Hidden dependency on an external file/URL/DB. |
| `CONDITIONAL_TEST_LOGIC` | Clean tests | Branching/looping hides data-dependent assertions. |
| `FRAGILE_ASSERTION` | Clean tests | Equality on a long literal — breaks on cosmetic change. |
| `PYRAMID_INVERSION` | Test pyramid | A unit test drags in E2E/integration machinery. |
| `BOUNDARY_SIGNAL_WEAK` | Test design | A range/validation test with a single (happy-path) assertion. |

**Languages:** Go, Python, JavaScript/TypeScript, and C# (xUnit/NUnit/MSTest) are
structure-aware; other extensions get the file-level pyramid check only.

The full catalog and *why each smell matters* is in
[references/test-smells.md](references/test-smells.md) — read it when explaining a finding
to a human or deciding whether a low-confidence flag is real.

## When code-review invokes this

Run it on changed `*_test.*` files during a review, then fold the findings into the review
report next to the code findings. For low-confidence rules (`BOUNDARY_SIGNAL_WEAK`,
`FRAGILE_ASSERTION`) prefer `--explain` so the model can confirm or dismiss before you
surface it. High-severity rules (`NO_ASSERTION`, `MYSTERY_GUEST`) are reliable deterministic
calls and can be reported without the LLM pass.

## Optional LLM explanation (`--explain`)

Off by default (deterministic-only, exit 0, no network). Pass `--explain` (or set
`TEST_QUALITY_REVIEWER_EXPLAIN=1`) to ask the configured provider to recalibrate severity
and reasoning. Provider selection reuses `CODE_REVIEW_LLM_*` (Bedrock-first); see
[../capability-mapper/SKILL.md](../capability-mapper/SKILL.md) for the provider table. When
`--explain` is set but the provider is unconfigured, the run **fails closed** rather than
emitting un-calibrated findings as if a model had reviewed them.

## Mock mode (offline / CI)

`TEST_QUALITY_REVIEWER_MOCK=1` (or `--mock`) prefixes every `reasoning` with `MOCK:` and
suffixes `skill_version` with `-mock`, with no network call — so a mock explanation can
never be mistaken for a real model judgement.

## Install

Canonical source is this directory. Install the runtime copy with `scripts/install.sh`;
edit the source here and re-run it, never edit the installed copy.

## Testing

```bash
python3 scripts/test_run.py     # stdlib unittest, no network, no credentials
```
