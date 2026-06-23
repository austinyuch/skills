---
name: code-summarizer
description: Generate a concise file-level summary through either agent-instruction mode or explicit LLM-API mode. Used by summary enrichment; defaults to subscription coding-agent instructions and never calls provider APIs unless llm-api mode is explicitly selected.
---

# code-summarizer

## Overview

Two-mode Agent Skill that produces a structured summary of a source file (plus its symbol
list) for the code knowledge graph. It is invoked by `internal/indexer/skill_runner.go`
(`RunSummaryEnrichment`) during the opt-in `review-cli index --summaries` step, and is the
sibling of `capability-mapper` (Spec #54).

Default mode is **agent-instruction**: a subscription coding agent follows this skill,
uses source/spec context, and emits an auditable summary. Provider-backed **llm-api**
mode is explicit opt-in for service/runtime execution and is owned by the Go service's
ADK provider path. Provider credentials alone must not switch the skill into llm-api mode.

Every completed summary carries a **confidence** score and a **reasoning** string so a
human can review and override it (REQ-0 transparency). The output is advisory, not
ground truth.

## Agent-Instruction State Machine

Use this state machine when a coding agent performs the summary directly:

1. `LOAD_INPUT`: read file path, symbols, and relevant source/spec context.
2. `IDENTIFY_ROLE`: name the file's main responsibility and important collaborators.
3. `BOUND_CLAIMS`: separate observed behavior from inferred intent.
4. `DECIDE`: choose confidence and a concise auditable reasoning summary.
5. `OUTPUT`: return the contract JSON, or record an explicit uncertainty note.

Do not expose hidden chain-of-thought. The `reasoning` field is a short reviewable decision summary.

### Writeback round-trip — apply your summaries to the graph (Spec #97 CR-2026-06-22-001)

In `agent-instruction` mode `review-cli index --summaries` only *emits a handoff* (`.code-review/agent-instruction-summaries.json`); it does not write File summaries. To enrich the graph: run this state machine over each handoff candidate, collect per-file outputs into a JSON array where each item adds `source_file`, then assemble and apply:

```
# wrap your per-file outputs (array of {source_file, summary, confidence, reasoning, skill_version})
python3 scripts/run.py --emit-result-envelope --target-root <handoff.target_root> --annotations annotations.json > sum-result.json
# write them onto the File nodes (same writer as llm-api mode; review-cli calls no provider API)
review-cli apply-handoff sum-result.json --target <handoff.target_root>
```

`apply-handoff` is fail-closed: `source_file` must be inside `target_root` and already indexed, `summary` non-empty, and `confidence` in `[0,1]` — any item that violates this is rejected with a reason, never partially written.

## Contract

Agent-instruction mode returns the same JSON shape below without calling a provider. The
`scripts/run.py` entrypoint remains the deterministic mock/legacy script contract; formal
product/runtime `llm-api` execution must go through the Go/ADK adapter.

Invocation for mock/legacy script contract: `python3 scripts/run.py '<json>'` (also
accepts the JSON on stdin).

Input:
```json
{"file": "internal/order/fulfilment.go", "symbols": ["ShipOrder", "CancelOrder"]}
```

Output (stdout, single JSON object):
```json
{
  "summary": "fulfilment.go: orchestrates order shipping and cancellation ...",
  "confidence": 0.81,
  "reasoning": "ShipOrder/CancelOrder operate on the order lifecycle ...",
  "skill_version": "code-summarizer/1.0"
}
```

On bad input, an unconfigured/missing provider, or unparseable model output, the script exits
**non-zero** and writes the reason to stderr. It never fabricates a summary — the runner counts
such files as failed and prints the stderr.

## Provider configuration (`llm-api` only)

Formal provider calls require explicit `CODE_REVIEW_SUMMARY_MODE=llm-api` or
`CODE_REVIEW_ANNOTATION_MODE=llm-api`, and the Go runner must route them through
the Go/ADK adapter. If no Go/ADK model can be created from config/env, `review-cli index
--summaries` fails closed instead of executing Python.

The legacy standalone Python adapter is retained only for compatibility tests and must
also set `CODE_REVIEW_ALLOW_LEGACY_PYTHON_LLM_API=1`; do not treat it as product
runtime evidence.

The provider is chosen by `CODE_REVIEW_LLM_PROVIDER` (default `bedrock`), reusing
the Go service's `CODE_REVIEW_LLM_*` env vars. AWS Bedrock is the
workspace-preferred foundation-model path (see `docs/provider-support-matrix.md`); the
gateway and OpenAI-compatible modes exist for environments without direct Bedrock access.

| Provider | Required env | Notes |
|----------|--------------|-------|
| `bedrock` (default in `llm-api`) | Go/ADK runtime credentials; legacy Python adapter additionally needs `CODE_REVIEW_LLM_BEDROCK_REGION` (or `AWS_REGION`) and `boto3` | explicit `CODE_REVIEW_LLM_BEDROCK_MODEL` wins; otherwise `CODE_REVIEW_LLM_BEDROCK_MODEL_SEQUENCE`; otherwise hardcoded low-cost sequence `moonshotai.kimi-k2.5` -> `minimax.minimax-m2.5`. Uses Bedrock Converse-capable runtime where available. Creds via `CODE_REVIEW_LLM_BEDROCK_*` or the default AWS chain. |
| `bedrock-gateway` | `CODE_REVIEW_LLM_GATEWAY_ENDPOINT`, `..._GATEWAY_API_KEY` | `x-api-key` + optional `user-id`. |
| `openai` | `CODE_REVIEW_LLM_OPENAI_BASE_URL` (+ `..._OPENAI_API_KEY`) | OpenAI-compatible `/chat/completions`; `..._OPENAI_AUTH_MODE=bearer|x-api-key`. |

If a non-Bedrock provider is used, it is because the deployment environment selected it via the
env vars above; the default and preferred path remains Bedrock.

## Mock mode (offline / CI)

Set `CODE_SUMMARIZER_MOCK=1` (or pass `--mock`) to produce deterministic offline output with
**no** LLM/network call. Mock output is clearly labelled — `skill_version` ends with `-mock` and
`reasoning` starts with `MOCK:` — and uses a conservative confidence (0.4), so it can never be
mistaken for real model evidence.

## Install

Canonical source is this directory (`.agents/skills/code-summarizer/`). The runtime loads the
installed copy from `~/.config/opencode/skills/code-summarizer/`:

```bash
scripts/install.sh
```

Edit the source here and re-run `install.sh`; do not edit the installed copy directly.

## Testing

```bash
python3 scripts/test_run.py     # stdlib unittest, no network, no credentials
```
