---
name: capability-mapper
description: Map a code file and its symbols to a single business capability, optionally grounded in the project's declared requirements / business value, through either agent-instruction mode or explicit LLM-API mode. Used by Layer 5 capability enrichment; defaults to subscription coding-agent instructions and never calls provider APIs unless llm-api mode is explicitly selected.
---

# capability-mapper

## Overview

Two-mode Agent Skill that maps a source file (plus its symbol list) to one business
capability for the code knowledge graph. It is invoked by
`internal/indexer/skill_runner.go` (`RunCapabilityEnrichment`) during Layer 5
(`review-cli index --capabilities`).

Default mode is **agent-instruction**: a subscription coding agent follows this skill,
uses source/spec context, and emits an auditable decision summary or glossary patch.
Provider-backed **llm-api** mode is explicit opt-in for service/runtime execution and is
owned by the Go service's ADK provider path. Provider credentials alone must not switch
the skill into llm-api mode.

Every completed mapping carries a **confidence** score and a **reasoning** string so a
human can review and override it (REQ-0 transparency). The output is advisory, not
ground truth.

## Agent-Instruction State Machine

Use this state machine when a coding agent performs the mapping directly:

1. `LOAD_INPUT`: read file path, symbols, optional glossary, optional requirement corpus, and relevant source/spec context.
2. `MATCH_GLOSSARY`: reuse a glossary term verbatim when it fits; otherwise prepare `NEW: <name>`.
3. `ASSESS_VARIANT`: collapse country/region/document suffixes into the base capability.
4. `MATCH_REQUIREMENTS` (Spec #96): if a requirement corpus is available, identify which declared requirements this capability serves (may be none) and a one-line business-value statement. Gather the corpus by reading `SPECS.md` / `RTM.md` / `{.agents,.kiro,.claude}/specs/*/requirements.md` directly, or by running `run.py --collect-requirements <root>`. Never invent requirement ids that are not declared.
5. `DECIDE`: choose one capability, confidence, and a concise auditable reasoning summary.
6. `OUTPUT`: return the contract JSON, or propose a `.code-review/capabilities.yaml` patch when curation is needed.

Do not expose hidden chain-of-thought. The `reasoning` field is a short reviewable decision summary.

### Writeback round-trip — apply your annotations to the graph (Spec #97 CR-2026-06-22-001)

In `agent-instruction` mode `review-cli index --capabilities` only *emits a handoff* (`.code-review/agent-instruction-capabilities.json`); it does not write graph nodes. To actually enrich the graph: run this skill's state machine over each handoff candidate, collect the per-file outputs into a JSON array where each item adds `source_file` (the candidate path), then assemble and apply the result:

```
# wrap your per-file outputs (array of {source_file, capability, description, confidence, reasoning, requirements?, business_value?, skill_version})
python3 scripts/run.py --emit-result-envelope --target-root <handoff.target_root> --annotations annotations.json > caps-result.json
# write them into the graph (same writer as llm-api mode; review-cli calls no provider API)
review-cli apply-handoff caps-result.json --target <handoff.target_root>
```

`apply-handoff` is fail-closed: never invent a `req_id` that is not in the declared corpus, keep `source_file` inside `target_root` and already indexed, and keep `confidence` in `[0,1]` — any item that violates this is rejected with a reason, never partially written.

## Contract

Agent-instruction mode returns the same JSON shape below without calling a provider. The
`scripts/run.py` entrypoint remains the deterministic mock/legacy script contract; formal
product/runtime `llm-api` execution must go through the Go/ADK adapter.

Invocation for mock/legacy script contract: `python3 scripts/run.py '<json>'` (also
accepts the JSON on stdin).

Input:
```json
{"file": "internal/order/fulfilment.go", "symbols": ["ShipOrder", "CancelOrder"],
 "glossary": [{"canonical_id": "order-fulfilment", "name": "Order Fulfilment", "aliases": ["Shipping"]}],
 "requirements": [{"req_id": "REQ-OF-001", "title": "Ship and cancel customer orders", "source": "spec:order/requirements.md"}]}
```

`glossary` is **optional** (Spec #91): the project's existing canonical capabilities. When present,
map into the best-matching term verbatim and only propose `NEW: <name>` when nothing fits (see the
Ubiquitous Language section below). The Go runner passes it automatically from
`.code-review/capabilities.yaml` when that file exists.

`requirements` is **optional** (Spec #96): the project's declared requirement corpus, so the
mapping can carry a business-value linkage. Each entry is `{req_id, title, source}`. Absent or
empty → byte-for-byte v1.0 behavior. Gather it with the `--collect-requirements` collector below.

Output (stdout, single JSON object):
```json
{
  "capability": "Order Fulfilment",
  "description": "Handles shipping and cancellation of customer orders.",
  "confidence": 0.82,
  "reasoning": "Functions ShipOrder/CancelOrder operate on order lifecycle ...",
  "requirements": [{"req_id": "REQ-OF-001", "confidence": 0.78}],
  "business_value": "Lets customers receive and cancel orders reliably (REQ-OF-001).",
  "skill_version": "capability-mapper/1.1"
}
```

`requirements` and `business_value` are **optional, additive** (Spec #96): present only when an
input requirement corpus was supplied and a real linkage was produced. They remain **advisory** —
evidence/diagnosis for the next step, not a readiness verdict. In `index --capabilities` (writing
mode) the Go runner persists this linkage as a `Capability -[SERVES]-> Requirement` edge (matching
`Requirement` nodes by `req_id`, created by `scan-specs`) plus a `business_value` property on the
`BusinessCapability` node. The original keys are unchanged, so the Go `SkillOutput` consumer keeps
working. On bad input, an unconfigured/missing provider, or
unparseable model output, the script exits **non-zero** and writes the reason to stderr. It never
fabricates a capability or a requirement linkage — the Go runner counts such files as failed and
prints the stderr.

### Requirement collector (Spec #96 — replaces the retired `spec-tracer`)

`python3 scripts/run.py --collect-requirements <project-root> [--format json]` parses the project
requirement corpus (`.agents/specs/*/requirements.md` concrete ids + titles, then `RTM.md` /
`SPECS.md` family rows, plus `.kiro`/`.claude` spec trees) into a deduped `requirements` list you
can feed back into a mapping call. Concrete `REQ-<FAM>-<NNN>` ids win over `REQ-<FAM>-*` family
rows. It fails closed (non-zero + stderr) when no spec corpus is found; it never fabricates.

```json
{"requirements": [{"req_id": "REQ-OF-001", "title": "...", "source": "spec:order/requirements.md"}],
 "stats": {"count": 103, "dropped": 0, "specs_scanned": 297}}
```

## Ubiquitous Language — map into the glossary, don't drift (Spec #91)

Capability naming is a **DDD ubiquitous language**: every file must map into the project's
*shared* vocabulary so the same business capability is not minted under many near-duplicate names
(e.g. `Address Data Management` vs `Postal Address Data Management` vs `Address & Postal Code Data
Management` for one mechanism). To avoid drift:

- When the caller provides the project glossary (the canonical capabilities already chosen, e.g.
  from `.code-review/capabilities.yaml`), **reuse the best-matching existing term verbatim**.
  Propose a new term only when nothing fits, and mark it `NEW: <name>` so a human can curate it —
  never silently emit a free-text variant of an existing capability.
- Prefer the **base capability**, not a per-variant label: X++ AOT names one capability across many
  objects with systematic suffixes (per-country `_BE/_NL/_SE/_US`, per-region `…Europe/…Base`,
  per-document `_SalesTable/_PurchTable`). Map the whole family to the same capability; the family
  variant is not itself a distinct capability.

The Go writer **enforces** this deterministically (snap-to-canonical by exact → normalized slug →
alias → X++ variant-base; `canonical_id`-keyed nodes; raw names retained in `aliases[]`), so drift
is corrected even if the model varies — but mapping into the glossary at the source keeps the
signal clean and the `NEW:` proposals meaningful.

## Provider configuration (`llm-api` only)

Formal provider calls require explicit `CODE_REVIEW_CAPABILITY_MODE=llm-api` or
`CODE_REVIEW_ANNOTATION_MODE=llm-api`, and the Go runner must route them through
the Go/ADK adapter. If no Go/ADK model can be created from config/env, `review-cli index
--capabilities` fails closed instead of executing Python.

The legacy standalone Python adapter is retained only for compatibility tests and must
also set `CODE_REVIEW_ALLOW_LEGACY_PYTHON_LLM_API=1`; do not treat it as product
runtime evidence.

The provider is chosen by `CODE_REVIEW_LLM_PROVIDER` (default `bedrock`), reusing
the Go service's `CODE_REVIEW_LLM_*` env vars. AWS Bedrock is the
workspace-preferred foundation-model path (see `docs/provider-support-matrix.md`); the
gateway and OpenAI-compatible modes exist for environments where direct Bedrock access is
unavailable.

| Provider | Required env | Notes |
|----------|--------------|-------|
| `bedrock` (default in `llm-api`) | Go/ADK runtime credentials; legacy Python adapter additionally needs `CODE_REVIEW_LLM_BEDROCK_REGION` (or `AWS_REGION`) and `boto3` | explicit `CODE_REVIEW_LLM_BEDROCK_MODEL` wins; otherwise `CODE_REVIEW_LLM_BEDROCK_MODEL_SEQUENCE`; otherwise hardcoded low-cost sequence `moonshotai.kimi-k2.5` -> `minimax.minimax-m2.5`. Uses Bedrock Converse-capable runtime where available. Creds come from `CODE_REVIEW_LLM_BEDROCK_ACCESS_KEY_ID`/`..._SECRET_ACCESS_KEY`/`..._SESSION_TOKEN` or the default AWS chain. |
| `bedrock-gateway` | `CODE_REVIEW_LLM_GATEWAY_ENDPOINT`, `..._GATEWAY_API_KEY` | `x-api-key` + optional `user-id`. |
| `openai` | `CODE_REVIEW_LLM_OPENAI_BASE_URL` (+ `..._OPENAI_API_KEY`) | OpenAI-compatible `/chat/completions`; `..._OPENAI_AUTH_MODE=bearer|x-api-key`. |

If a non-Bedrock provider is used, it is because the deployment environment selected it via
the env vars above; the default and preferred path remains Bedrock.

## Mock mode (offline / CI)

Set `CAPABILITY_MAPPER_MOCK=1` (or pass `--mock`) to produce deterministic offline output
with **no** LLM/network call. Mock output is clearly labelled — `skill_version` ends with
`-mock` and `reasoning` starts with `MOCK:` — and uses a conservative confidence (0.4), so it
can never be mistaken for real model evidence.

## Install

The canonical source is this directory (`.agents/skills/capability-mapper/`). The runtime
loads the installed copy from `~/.config/opencode/skills/capability-mapper/`:

```bash
scripts/install.sh
```

Edit the source here and re-run `install.sh`; do not edit the installed copy directly.

## Testing

```bash
python3 scripts/test_run.py     # stdlib unittest, no network, no credentials
```
