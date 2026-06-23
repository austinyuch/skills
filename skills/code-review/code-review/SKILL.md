---
name: code-review
description: Perform code review using Code Review System CLI tools. Use when agents need to analyze code, generate improvements, create reports, perform architecture analysis, inspect bounded context, query GraphRAG state, govern local GraphRAG artifacts, or produce generic producer-side routing handoff artifacts. Supports file-level and project-level reviews.
---

# Code Review

## Overview

Enables agents to perform comprehensive code reviews using the Code Review System's CLI tools. Supports analyzing individual files or entire projects, generating improvement suggestions, producing review reports, serving a local viewer, and exporting bounded context or producer-side routing handoff artifacts.

The published `scripts/` surface is native-binary-only. Agents should invoke the matching `review-cli-<os>-<arch>` binary directly and should not assume Python runtime entrypoints such as `review.py` remain part of the shipped contract.

It also exposes graph retrieval surfaces through `search-code`: hybrid graphRAG for embedding-backed semantic recall, and graph-only retrieval for exact structural questions when embeddings/provider APIs are disallowed.

MCP support is a runtime surface of the same binary, not a separate review engine. For local IDE/agent clients, use the matching binary as a stdio MCP subprocess. For shared or remote MCP clients, run the binary as an HTTP/SSE runtime instance with API-key auth. Container/Docker deployment is an optional packaging/runtime form for HTTP/SSE; the source of truth remains `review-cli mcp serve`. Spec #101 adds MCP `remote_review` for bounded remote Git `repo_url/ref` materialization with explicit `sandbox_level=filesystem|process|service`; repo-side routing is implemented, and `sandbox_level=process` has current-host bwrap proof when explicitly enabled with `CODE_REVIEW_REMOTE_REVIEW_PROCESS_SANDBOX=bwrap`. Filesystem-level remote materialization can also reuse `scan_specs`, `analyze_code`, `generate_report`, and `search_code` through `remote_review.tool`. Private GitHub/GitLab provider proof and live L3 sandbox-station runtime proof remain external.

## Scope Boundary

This skill is **static analysis + bounded context tooling**, not a runtime readiness authority.

- Use this skill to answer: “What does the code structure look like?”, “What are the likely dependency / impact relationships?”, “What bounded context should I hand off downstream?”
- Do **not** use this skill alone to answer: “Is the feature live-demo ready?”
- Authoritative `PASS / CONDITIONAL / FAIL` for runtime or live-demo readiness still comes from runtime-backed review artifacts.

## Start Here

Read these files for the actual workflow:

- [references/cli-commands.md](references/cli-commands.md)
- [references/usage-guide.md](references/usage-guide.md)
- [references/local-state-version-control.md](references/local-state-version-control.md)
- [references/configuration.md](references/configuration.md)
- [references/output-examples.md](references/output-examples.md)

## Packageable Family Explanation

If the request is about the `code-review` family, packagable explanation, value proposition, press-style summary, FAQ, or a shareable HTML page for the family, use:

- [README.md](./README.md)
- [GENERATION_GUIDE.md](./GENERATION_GUIDE.md)
- [index.html](./index.html)

These files are the packageable explanation surface for the family. They do not replace the actual review contract in this `SKILL.md`.

## Packageable Manual Explanation

If the request is about an operational manual, quick start, routing walkthrough, or a user-manual style explanation of how to run `code-review`, use:

- [MANUAL_GENERATION_GUIDE.md](./MANUAL_GENERATION_GUIDE.md)
- [manual.html](./manual.html)

These files should explain how to use the review surfaces step by step. They do not replace the review contract in this `SKILL.md` and they do not claim runtime readiness.
`manual.html` 需要提供 `EN / 繁中` 切換，讓操作說明可以同時服務中英文讀者。

## Agent-only Graph Lane

When policy or cost constraints prohibit embeddings or pay-as-you-go provider APIs, prefer the Spec #62 graph-only lane:

```bash
review-cli-<os>-<arch> index <project-path> --no-embeddings
review-cli-<os>-<arch> search-code <project-path> "<exact symbol or structural query>" --graph-only
```

For large repositories, use recursive checkpointed indexing with small batches:

```bash
PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true \
CODE_REVIEW_INDEX_MEMORY_MB=1536 \
review-cli-<os>-<arch> index <project-path> \
  --recursive --resume --no-embeddings \
  --batch-max-files 50 \
  --batch-max-bytes 64MB \
  --batch-sort mtime
```

`--recursive` stores a checkpoint at `<project-path>/.gcr/index-recursive-checkpoint.json`; use `--resume` after interruption and `--restart` for a fresh run. A recursive run produces the **same relation graph as a non-recursive full index** — per-batch `CALLS`/`DEPENDS_ON`/`DEFINES`/`CONTAINS` plus a bounded corpus-wide final pass for producer-backed semantic families (e.g. XPP `INHERITS_FROM`/`REFERENCES_CLASS`/`OVERRIDES`) and `BELONGS_TO_REPO` membership — at bounded memory. The project SQLite graph DB is single-writer, now enforced by a single writer connection plus a 30s `busy_timeout`, so a recursive run serializes its own write phases safely (no `SQLITE_BUSY`); a second concurrent graph-mutating process against the same project DB serializes and may wait rather than fail. For a full fresh index `--recursive` is also the recommended (and typically faster) path on large repos because it skips the per-file owned-edge re-cleanup that the non-recursive path runs. Use `--prune-ignored` only when you intentionally want to remove existing File/symbol/vector traces that no longer appear in the current discovered corpus.

The corpus is filtered by builtin excluded dirs → root `.gitignore` → legacy root `.reviewignore` → `.code-review/config.yaml` → `--exclude` (additive, in that order). Prefer `.code-review/config.yaml` as the target repo's single review configuration file; `.reviewignore` is accepted only as a legacy import surface. Never copy files, symlink files, or expanded inventories into `.reviewignore` or `.code-review/config.yaml`. Preview with `index --dry-run-corpus --format json` to see included/excluded samples plus the matched source/rule. Full rules: [references/usage-guide.md](references/usage-guide.md) "Index Corpus Ignores".

Use `--no-embeddings` to skip embedding/vector provider initialization. Use `--no-model` when the run must avoid both embeddings and LLM API annotation writes. `--no-model --capabilities` / `--no-model --summaries` still return agent-instruction handoff hints for the coding agent; they do not mean the capability/summary work is forbidden. `CODE_REVIEW_EMBEDDING_PROVIDER=mock` is a deterministic test provider and still creates mock embedding rows; it is not graph-only indexing.

Two opt-in LLM enrichment passes depend on **separate Agent Skills** that this skill orchestrates but does not contain: `index --capabilities` requires the **`capability-mapper`** skill (Layer 5 `BusinessCapability` nodes) and `index --summaries` requires the **`code-summarizer`** skill (File-node summaries). Both install to `~/.config/opencode/skills/` via their own `install.sh`, are Bedrock-first, and exit non-zero without fabricating when no provider is configured — the graph-only lane never invokes them unless you pass the flag. Details + the read-side vs write-side distinction: [references/cli-commands.md](references/cli-commands.md) `index`.

Incremental `index` reflects the working tree, not just committed history: an **uncommitted** edit in a git repo is picked up and reindexed (it no longer reports "No changes since last index"). A pure line shift / comment-only edit that leaves a file's structure unchanged is detected and its edges are preserved (no churn), and non-git working trees fall back to an OS-native `(mtime,size)` fast-path plus content hash so unchanged files are skipped without re-reading. These are deterministic graph-update behaviors and require no extra flags.

For large XPO/XPP corpora, run the coverage doctor before claiming class-level graph completeness:

```bash
PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true \
review-cli-<os>-<arch> index <project-root-or-xpo-subtree> --coverage --format json
```

Interpret the result conservatively. `declared_relation_families` means known vocabulary; `produced_relation_families` means actual graph edges in the current local-sqlite state. If filesystem `.xpo`, `index_layers`, graph `File` / artifact counts, or produced XPP semantic relation counts diverge, report that as partial coverage and use the output as a remediation handoff. Checked-in fixtures are regression proof only; they are not evidence that a full external `ax/xpp-corpus` rerun completed.

For richer semantic topology without repository-managed provider API calls, a subscribed coding-agent session may write an `agent-graph-fragment/v1` JSON file and import it:

```bash
review-cli-<os>-<arch> graph fragment validate fragment.json --target <project-path>
review-cli-<os>-<arch> graph fragment apply fragment.json --target <project-path> --source-owned
```

Do not claim this replaces vector search. Use hybrid graphRAG when broad natural-language recall, cross-repo semantic search, or ranking by similarity is needed.

## Review Depth — Helper Skills

The graph/capability surfaces above answer *what exists* (structure, dependencies, business
capability, requirement traceability). They do **not** judge code maintainability or test
effectiveness. For a real review, orchestrate these four **separate sibling skills** — same
contract pattern as `capability-mapper`/`code-summarizer` (hybrid: a deterministic detector
that runs offline as the source of truth, plus an opt-in `--explain` LLM pass; Bedrock-first;
honest non-zero exit, never fabricates). Each installs to `~/.config/opencode/skills/` via its
own `install.sh`. Invoke per changed file; fold the JSON `findings[]` into the review report.

| Skill | Use it to | Invocation |
|-------|-----------|------------|
| `test-quality-reviewer` | judge EXISTING tests — smells, FIRST, missing boundaries, pyramid inversion | `run.py '{"file":"x_test.go"}'` |
| `code-refactoring-advisor` | name code smells → the Fowler move + test safety-net + Ponytail/YAGNI minimality check | `run.py '{"file":"x.go"}'` |
| `test-design-generator` | turn "test thoroughly" into boundary/equivalence/pairwise cases + an oracle strategy | `run.py '{"parameters":[...]}'` |
| `security-risk-reviewer` | OWASP Top-10 pattern scan, ranked by risk (the executable form of the security guidance above) | `run.py '{"file":"x.go"}'` |

Default mode is deterministic-only (offline, exit 0). Pass `--explain` for borderline /
low-confidence findings to let the configured provider calibrate severity (fails closed if
forced and unconfigured). High-confidence deterministic findings (e.g. `NO_ASSERTION`, an
`AKIA…` key) can be reported without the LLM pass. Pass the code graph's impact count as
`blast_radius` to `security-risk-reviewer` so widely-depended-on files rank higher. These are
review aids, not release gates — `security-risk-reviewer` is triage, not a SAST replacement.

### Ponytail / YAGNI minimality boundary

Within the code-review family, the Ponytail Ladder is a **pre-review design and implementation
rubric**, not a Phase 5 verdict authority:

| Stage | Ponytail Ladder | Code-review family |
|---|---|---|
| Phase 2 Design | Prevent over-engineering during option selection. | `code-review --graph-only` / impact evidence can support blast-radius decisions. |
| Phase 4 Implementation | Prevent over-building while code is being written or refactored. | `code-refactoring-advisor` reports smell → move → safety-net → `minimality_check`; `test-quality-reviewer` can flag over-specified tests that pin implementation details. |
| Phase 5 Review | Does not directly participate as a verdict source. | `code-review` reviews the diff; `security-risk-reviewer` checks that simplification did not weaken security. |

Use the ladder when a change proposes a new abstraction, helper, dependency, format, wrapper,
lifecycle manager, parser, rule engine, class/module split, or test harness:

1. Does this need to exist? If no, skip it.
2. Can the standard library do it? Use it.
3. Can a native platform feature do it portably? Use it, or isolate OS/arch-specific code behind a small adapter with fallback.
4. Can an already-installed dependency do it? Use it.
5. Is it one line? Keep it one line.
6. Only then build the minimum custom implementation.

Do not turn this into a deterministic `review-cli review` rule unless the future rule is narrow
and objective. Missing minimality justification is advisory context; it is not a blocking review
finding. Preserve custom abstractions when they carry policy, lifecycle, error, security,
external-contract, test-seam, or domain boundaries.

The ladder must stay architecture/platform agnostic across the published skill targets. Native
platform recommendations need either portable behavior across supported OS/arch builds or an
explicit platform adapter, guard, and fallback. Do not let a Linux/macOS/Windows or amd64/arm64
assumption masquerade as generic code-review guidance.

When forwarding `code-refactoring-advisor` output, do not translate its minimality finding into
`PASS`, `FAIL`, `BLOCK`, or approval language. If the same change creates a compile,
portability, runtime, or security regression, cite the advisor as context and let the relevant
build/test, `review-cli review`, `security-risk-reviewer`, SonarQube, or consuming repo
`review.md` authority make the verdict.

### Native AST review: `review-cli review` (Go, Python, TypeScript, C#)

Beyond the heuristic Python skills above, `review-cli` has a built-in **AST-based** review —
`review-cli-<os>-<arch> review <path> [--language go|python|typescript|csharp|xpp] [--vet] [--race] [--format json|jsonl]` — covering concurrency
(real goroutine loop-var capture, lock-without-`defer`), resource leaks, error handling,
numeric (typed money-as-float/number across languages), and maintainability (long parameter
lists). It now spans **Go, Python, TypeScript/JavaScript, C#, and line-level XPO/XPP**:
- **Go** — `go/ast` pass + authoritative `go vet` / `go test -race` adapter.
- **Python** — `REVIEW_PY_MUTABLE_DEFAULT` (B006), `REVIEW_PY_BARE_EXCEPT` (E722), `REVIEW_PY_MONEY_FLOAT`.
- **TypeScript/JavaScript** (`.ts`/`.tsx`/`.js`/`.jsx`) — `REVIEW_TS_MONEY_NUMBER`, `REVIEW_TS_EMPTY_CATCH`, `REVIEW_TS_EXPLICIT_ANY` where syntax support is available; JS/TS also has line-level maintainability coverage in no-tree-sitter builds.
- **C#** — `REVIEW_CS_MONEY_FLOAT` (float/double vs decimal), `REVIEW_CS_EMPTY_CATCH`, `REVIEW_CS_ASYNC_VOID`.
- **XPO/XPP** — `.xpo` exports receive line-level maintainability checks such as `REVIEW_GOD_FILE` / duplicated-block with `source=xpp-line`; this is not a full X++ AST rule pack.
- **All four** — maintainability smells: `REVIEW_LONG_PARAM_LIST`, `REVIEW_LONG_METHOD`, `REVIEW_DEEP_NESTING` (Fowler; `else if` chains do not inflate nesting depth).

**Orchestration:** run `review-cli review` as the **primary deterministic pass** for any Go/Python/TS/C#
file — it is accurate by construction (real syntax trees, not regex), needs no LLM, and the shipped
linux/windows binaries are tree-sitter (the Python/TS/C# rules run there; darwin degrades with an
honest note). The Python helper skills above remain for **LLM-explained / heuristic / test-quality /
security-taint** findings the deterministic engine does not own. Details:
[references/cli-commands.md](references/cli-commands.md) `review`.

### SonarQube (authoritative gate) + `sonarqube-bridge`

When the team uses **SonarQube**, it is the authoritative static-scan / SAST and the blocking
quality gate; the four helper skills above are the advisory **shift-left** that pre-flights it.
Do not treat the helpers as a second gate. To bring Sonar findings into the review, use the
**`sonarqube-bridge`** skill: it ingests Sonar issues (Web API or an offline export) and fuses
them with the code graph (blast-radius), business capability, and the same remediation
vocabulary — emitting the shared finding schema so Sonar + heuristic + graph findings merge into
one ranked report. Division of labour:
`.agents/skills/sonarqube-bridge/references/sonar-integration.md`.

## Embedding Provider Configuration

For GraphRAG indexing and `search-code`, configure embedding providers through project-unique `CODE_REVIEW_EMBEDDING_*` environment variables or repo-local config. Use [references/configuration.md](references/configuration.md) for detailed setup.

- `bedrock`, `openai`, `vertex`, and `mock` remain available provider families.
- `self-hosted` is the generic local model-server provider. Select the protocol with `CODE_REVIEW_EMBEDDING_SELF_HOSTED_API_FORMAT` rather than naming the provider after one server.
- `onnx` uses workspace-relative paths by default: executable runners belong under `{the-skill}/scripts/`, while ONNX model/tokenizer assets belong under `{the-skill}/assets/`. These can be overridden with `CODE_REVIEW_EMBEDDING_ONNX_RUNNER_PATH`, `CODE_REVIEW_EMBEDDING_ONNX_MODEL_PATH`, and `CODE_REVIEW_EMBEDDING_ONNX_TOKENIZER_PATH`.

ONNX execution is intentionally behind a subprocess runner boundary so the main `review-cli` binary does not link ONNX runtime libraries directly. The runner must live under repo/skill-owned `scripts/` or be compiled into a shipped executable binary, and model/tokenizer files must live under repo/skill-owned `assets/` before claiming offline bundled ONNX execution.

The bundled CPU path uses `.agents/skills/code-review/scripts/embedding-runner` with `.agents/skills/code-review/assets/models/baai-bge-small-en-v1-5/`. GPU execution remains handoff-only until the CUDA validation workflow in `.agents/skills/opensource-embedding-onnx/references/gpu-validation-handoff.md` passes on a CUDA-capable machine.

When an open-source embedding model must be converted or packaged into ONNX format, use the repo-level `.agents/skills/opensource-embedding-onnx/` skill. This `code-review` skill should consume the resulting runner/model/tokenizer paths, not own the conversion workflow.
