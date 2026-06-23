---
name: code-refactoring-advisor
description: Detect code smells in a source file and name the specific refactoring move plus the test safety-net it requires first. Use when reviewing code for maintainability, when asked "how should I refactor this / what's wrong with this file / is this too complex", or as the refactoring pass of a code review. Flags long methods, long parameter lists, deep nesting, god files, duplicated blocks, magic numbers, and complex conditionals, each mapped to a named Fowler refactoring. Orchestrated by the code-review skill alongside test-quality-reviewer.
---

# code-refactoring-advisor

## Overview

A hybrid reviewer skill: a **deterministic detector** finds Fowler-style code smells in a
source file offline and maps each to a **named refactoring move** and the **test safety-net**
that must exist before the move is safe (Fowler's own precondition — refactor only under
trustworthy tests). An OPTIONAL `--explain` pass calibrates severity and reasoning.

It is the natural partner of `test-quality-reviewer`: this skill says *what to change*,
that skill checks the net you change it against. Together they extend the `code-review`
graph/capability inventory from "what exists" to "what should improve".

## Contract

Invocation: `python3 scripts/run.py '<json>'` (also accepts JSON on stdin).

Input — a single source file:
```json
{"file": "internal/indexer/indexer.go"}
```
Optional: `content` (skip disk read), `thresholds` (override any of `long_method`,
`long_params`, `deep_nesting`, `god_file_lines`, `god_file_funcs`, `magic_numbers`,
`bool_ops`).

Output (stdout, one JSON object): `skill_version`, `target`, `language`, `explained`,
`summary`, and `findings[]`. Each finding adds three fields beyond the usual ones:
`refactoring` (the named move), `safety_net` (the test that must exist first), and
`minimality_check` (the Ponytail/YAGNI ladder applied before recommending new abstractions).
An empty `findings` list is a valid PASS; exit is non-zero only on bad input or a forced
`--explain` provider failure.

### Minimality / YAGNI boundary

Use the Ponytail Ladder as a **pre-review design and implementation rubric**, not as a
Phase 5 verdict authority. Before recommending a new helper, wrapper, dependency,
parameter object, lifecycle manager, parser, rule engine, or class/module split, apply:

1. Does this need to exist? If no, skip it.
2. Can the standard library do it? Use it.
3. Can a native platform feature do it portably? Use it, or isolate OS/arch-specific code behind a small adapter with fallback.
4. Can an already-installed dependency do it? Use it.
5. Is it one line? Keep it one line.
6. Only then build the minimum custom implementation.

The ladder reduces over-building, but it must not become blanket anti-abstraction. A custom
abstraction is still justified when it carries a real policy boundary, lifecycle boundary,
error boundary, security boundary, external contract adapter, or cross-call-site domain
concept. Findings should frame missing minimality justification as advisory context, not a
blocking review verdict.

Do not use verdict labels such as `PASS`, `FAIL`, `BLOCK`, or `approved` in this advisor's
own output. If a minimality issue also exposes a real compile, portability, security, or
runtime regression, state the advisory finding and hand it off to the appropriate authority
(`code-review`, build/test gates, `security-risk-reviewer`, SonarQube, or the consuming
repo's `review.md`) for the actual verdict.

The ladder is architecture/platform agnostic by default. Native platform features are acceptable
only when the recommendation remains portable across the skill's supported OS/arch targets, or
when platform-specific behavior is isolated behind an explicit adapter, build/runtime guard, and
fallback. Do not turn a Linux, macOS, Windows, amd64, or arm64 assumption into generic review
guidance.

### Smell → refactoring map

| Rule | Refactoring move | Safety-net first |
|------|------------------|------------------|
| `LONG_METHOD` | Extract Function | characterization test on current output |
| `LONG_PARAMETER_LIST` | Introduce Parameter Object | test pinning each call site |
| `DEEP_NESTING` | Replace Nested Conditional with Guard Clauses | branch-covering tests |
| `GOD_FILE` | Extract Class / Move Function | tests around the split responsibilities |
| `DUPLICATED_BLOCK` | Extract Function, call from both sites | a test covering both sites |
| `MAGIC_NUMBER` | Replace Magic Literal with Named Constant | mechanically safe |
| `COMPLEX_CONDITION` | Decompose Conditional (named predicate) | truth-combination tests |

Why each smell matters and how to apply the move: [references/refactoring-catalog.md](references/refactoring-catalog.md).

## When code-review invokes this

Run it on changed source files, then present each finding as *smell → move → safety-net →
minimality check* so the reviewee gets an actionable change, not a complaint. Cross-check
`DUPLICATED_BLOCK` and `GOD_FILE` against the code graph's blast-radius (`developer-routing`
/ impact) before recommending an extraction. Use `--explain` for borderline `MAGIC_NUMBER`
/ `COMPLEX_CONDITION`, or whenever the minimality call depends on domain intent.

## Heuristic honesty

**Languages:** Go, Python, JavaScript/TypeScript, and C# get function-level smells (long
method / params / nesting / complex condition); duplicated-block and god-file checks are
language-agnostic and apply to any text file.

These are line/structure heuristics, not a full AST. Treat thresholds as conversation
starters: a 70-line function may be fine, a 30-line one may not. The deterministic pass
finds candidates; severity is best confirmed with `--explain` or human judgement. Comment
density and language idioms (idiomatic Go `if err != nil`) are intentionally not counted as
nesting/branching to keep false positives low.

## Optional LLM explanation, mock mode, install, testing

`--explain` (or `CODE_REFACTORING_ADVISOR_EXPLAIN=1`) recalibrates via `CODE_REVIEW_LLM_*`
(Bedrock-first; fails closed if forced and unconfigured). `CODE_REFACTORING_ADVISOR_MOCK=1`
(or `--mock`) gives labelled offline output. Install with `scripts/install.sh` (self-naming).
Test with `python3 scripts/test_run.py` (stdlib, no network).
