---
name: test-design-generator
description: Turn "test it thoroughly" into concrete test cases using formal test-design techniques. Use when planning tests for a function/endpoint/form, when asked "what cases should I test / what are the edge cases / give me boundary tests", or before writing tests so coverage is deliberate not happy-path. Generates boundary-value, equivalence-partition, and pairwise combination cases from a parameter description, and recommends an oracle strategy (property-based/metamorphic) when outputs cannot be enumerated. Orchestrated by the code-review skill alongside test-quality-reviewer.
---

# test-design-generator

## Overview

A hybrid generator skill: a **deterministic generator** applies boundary-value analysis,
equivalence partitioning, and pairwise combination to a structured parameter description,
and recommends an oracle strategy when the answer cannot be enumerated by hand. An OPTIONAL
`--explain` pass adds the semantic/negative cases a structural generator cannot infer
(injection strings, type confusion, unicode, locale, domain rules).

This is the "what should I test?" complement to `test-quality-reviewer`'s "are these tests
good?". Where `BOUNDARY_SIGNAL_WEAK` flags a thin test, this skill produces the missing cases.

## Contract

Invocation: `python3 scripts/run.py '<json>'` (also accepts JSON on stdin).

Input — describe the parameters (or give a short free-text spec):
```json
{"subject": "registration form",
 "parameters": [
   {"name": "age", "type": "int", "min": 18, "max": 65},
   {"name": "country", "type": "enum", "values": ["US", "CA", "UK"]},
   {"name": "email", "type": "string", "minLength": 3, "maxLength": 254, "pattern": "email"},
   {"name": "subscribed", "type": "bool"}
 ]}
```
Or `{"spec": "age accepts 18 to 65"}` — a light free-text integer range is parsed.

Output (stdout): `cases[]` (each `technique`, `parameter`, `inputs`, `expected`
accept/reject, `rationale`), `combinations[]` (pairwise rows), `oracle_hint`, and
`techniques`/`explained`. Exit is non-zero only on bad input or a forced `--explain`
provider failure.

### Techniques applied deterministically

| Type | Cases generated |
|------|-----------------|
| `int`/`number` (min,max) | boundary-value: min-1 (reject), min, min+1, max-1, max, max+1 (reject) + interior rep |
| `enum` (values) | each member (accept) + one out-of-set value (reject) |
| `string` (minLength,maxLength,pattern) | length boundaries, empty, valid/invalid pattern |
| `bool` | true, false |
| multiple params | pairwise (all-pairs) combination cover |

Definitions and *why each technique catches a distinct defect class*:
[references/test-design-techniques.md](references/test-design-techniques.md).

## The oracle reminder

For functions whose correct output you cannot enumerate (sorting, pricing, parsing), the
`oracle_hint` steers you to **property-based**, **metamorphic**, or **golden-master/
differential** testing instead of hand-picked expected values. The generated boundary cases
tell you *which inputs*; the oracle hint tells you *how to know the right answer*.

## When code-review invokes this

Use it during test planning or when a review finds thin coverage on a validated input. Feed
the parameters from the function signature (the code graph already has them) and present the
case table to the developer. For domain-specific negatives, add `--explain`.

## Optional LLM enrichment, mock mode, install, testing

`--explain` (or `TEST_DESIGN_GENERATOR_EXPLAIN=1`) adds semantic/negative cases via
`CODE_REVIEW_LLM_*` (Bedrock-first; fails closed if forced and unconfigured).
`TEST_DESIGN_GENERATOR_MOCK=1` (or `--mock`) appends a labelled offline placeholder. Install
with `scripts/install.sh` (self-naming). Test with `python3 scripts/test_run.py` (stdlib, no
network).
