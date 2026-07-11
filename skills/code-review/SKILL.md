---
name: code-review
description: Perform code review using Code Review System CLI tools. Use when agents need to analyze code, generate improvements, create reports, perform architecture analysis, inspect bounded context, query GraphRAG state, govern local GraphRAG artifacts, or produce generic producer-side routing handoff artifacts. Supports file-level and project-level reviews.
---

# Code Review

## Overview

Enables agents to perform comprehensive code reviews using the Code Review System's CLI tools. Supports analyzing individual files or entire projects, generating improvement suggestions, producing review reports, serving a local viewer, and exporting bounded context or producer-side routing handoff artifacts.

The published `scripts/` surface is native-binary-only. Agents should invoke the matching `review-cli-<os>-<arch>` binary directly and should not assume Python runtime entrypoints such as `review.py` remain part of the shipped contract.

**Download-on-install:** the `review-cli-<os>-<arch>` binaries are NOT shipped inside the bundle (they are not git-LFS-committed). On first use run `sh scripts/install.sh` once — it downloads and SHA-256-verifies **only this host's** single binary from the GitHub release (checksums in `scripts/review-cli-bundle-manifest.json`), so the bundle carries one platform binary instead of all six (~300 MB). The same `install.sh` also fetches the ONNX embedding model as ONE SHA-256-verified `.zip` from the same release and unzips it into `assets/models/` (checksums in `scripts/onnx-model-bundle-manifest.json`); the ~127 MB `model.onnx` + tokenizer/configs are likewise not committed. Set `REVIEW_CLI_SKIP_ONNX=1` to skip the model fetch if you only need `review-cli` without semantic search. Override the release source with `REVIEW_CLI_RELEASE` (`gh://OWNER/REPO@TAG`, an `https://` base URL, or a local dir). Both fetches are idempotent and are no-ops if the artifacts are already present (e.g. a local build). Maintainers (re)build the model zip + trust-anchor manifest with `scripts/pack-model-bundle.sh`.

It also exposes graph retrieval surfaces through `search-code`: hybrid graphRAG for embedding-backed semantic recall, and graph-only retrieval for exact structural questions when embeddings/provider APIs are disallowed.

MCP support is a runtime surface of the same binary, not a separate review engine. For local IDE/agent clients, use the matching binary as a stdio MCP subprocess. For shared or remote MCP clients, run the binary as an HTTP/SSE runtime instance with API-key auth. Container/Docker deployment is an optional packaging/runtime form for HTTP/SSE; the source of truth remains `review-cli mcp serve`. Spec #101 adds MCP `remote_review` for bounded remote Git `repo_url/ref` materialization with explicit `sandbox_level=filesystem|process|service`; repo-side routing is implemented, and `sandbox_level=process` has current-host bwrap proof when explicitly enabled with `CODE_REVIEW_REMOTE_REVIEW_PROCESS_SANDBOX=bwrap`. Filesystem-level remote materialization can also reuse `scan_specs`, `analyze_code`, `generate_report`, and `search_code` through `remote_review.tool`. Private GitHub/GitLab provider proof and live L3 sandbox-station runtime proof remain external.

## Scope Boundary

This skill is **static analysis + bounded context tooling**, not a runtime readiness authority.

- Use this skill to answer: “What does the code structure look like?”, “What are the likely dependency / impact relationships?”, “What bounded context should I hand off downstream?”
- Do **not** use this skill alone to answer: “Is the feature live-demo ready?”
- Authoritative `PASS / CONDITIONAL / FAIL` for runtime or live-demo readiness still comes from runtime-backed review artifacts.

## Agent Graph Dogfooding Default

For architecture discovery, project design, impact analysis, broad code retrieval, spec handoff, or non-trivial implementation planning, the agent must treat the local code graph as part of the default context bootstrap. This is an init/preflight requirement, not an optional nice-to-have. Start with the target repository's own instructions and any durable shared graph workflow it provides. If the repo has a tracked `.code-review/graph.sqlite` / `vector.sqlite` / `manifest.json` snapshot, inspect its manifest and run the repo's documented status or doctor command before rebuilding it.

Use direct file reads only when the task is clearly narrow, the relevant files are already known, or graph state is missing and rebuilding would cost more than the task warrants. In that case, say so briefly in the design/review notes instead of silently skipping the graph. Do not use graph evidence to overrule checked-out code, active specs, or runtime proof.

Mandatory sequence for non-trivial work:

1. Init/preflight the graph lifecycle: run the repo-local status/doctor command when one exists; otherwise run `review-cli-<os>-<arch> init <project-path> --graph` (or `graph init <project-path>`). If query commands support `--graph-init`, use `auto` by default and `always` when the graph is known stale; use `skip` only when a read-only lifecycle is intentional and existing graph state is already queryable.
2. Run one or more focused `search-code`, `architecture`, `developer-routing`, `bounded-context`, `impact`, `dependency-path`, `capability-inventory`, or `summary` queries that match the decision you are making before settling a design or implementation path.
3. Select a trigger strategy for ongoing work: repo-owned refresh command, `review-cli watch . --once --json` for a one-shot working-tree Layer 1-4 refresh, long-running `review-cli watch .` for active edit sessions, or `review-cli graph hook status` / explicit `graph hook install` for post-commit refresh where repo/user policy allows local hook installation. Plain Git/watch triggers are review-cli-only topology refresh mechanisms. For subscription-agent capability/summary enrichment, use `review-cli handoff run-agent <handoff-dir> --agent auto --apply` after no-model handoff emission, or opt in to `review-cli graph hook install --subscription-agent --agent auto` so the hook generates the handoff, bakes the resolved persistence env into the hook command, and launches the non-interactive agent handoff detached before applying through `apply-handoff`. A fast commit return proves the hook did not block on the agent; it does not prove annotation writeback has completed. Built-in handoff launchers are Codex CLI (`codex exec`), Claude Code CLI (`claude -p`), OpenCode (`opencode run`), Kiro CLI (`kiro-cli chat --no-interactive`), and Antigravity (`agy -p`); use `--agent-command` for custom wrappers. Before installing lifecycle hooks, run `review-cli handoff agent-doctor --agent <agent|all|auto> --strict` or install with `scripts/install-agent-handoff-hooks.py --preflight` so missing binaries and changed flags fail before the hook is written. If no trigger is used, record why.
4. Rebuild or refresh only when the status/manifest is stale, missing, not queryable, or too partial for the question.
5. Record the graph query and trigger/preflight result, or the reason for skipping them, in the spec/design/review artifact when the task produces one.

If a target repo repeatedly needs repo-specific graph bootstrap rules, durable snapshot ownership, or trigger policy, recommend a target-repo constitution update such as `AGENTS.md`, Kiro steering, or `CLAUDE.md`. Treat that as a candidate governance patch or handoff unless the user explicitly asks you to edit the target repo's constitution in the current task; do not silently rewrite another repo's agent rules from this skill alone.

## Provider-Bound Evidence Lane

When the user names a concrete provider, model, endpoint, execution provider, or dimension for graph/vector evidence, treat the run as provider-bound. Examples include BGE-M3, ONNX GPU, CUDAExecutionProvider, a self-hosted `/v1/embeddings` endpoint, Bedrock Titan, Vertex embeddings, or an OpenAI embedding model. In this lane, do not silently substitute `mock`, another provider family, another endpoint, or a different model.

Before any write-producing or evidence-producing code-review command, record the provider contract:

| Field | Required value |
|---|---|
| Allowed provider | Provider family or protocol selected for this lane, such as `self-hosted`, `onnx`, `openai`, `bedrock`, or `vertex`. |
| Endpoint/base URL | Exact endpoint or explicit "not applicable" for local/bundled providers. |
| Model | Exact model ID, such as `BAAI/bge-m3` or the configured provider model. |
| Dimensions | Expected vector dimensions, or explicit "not used" for graph-only commands. |
| Execution provider | CPU/CUDA/other runtime detail when the provider exposes it. |
| Forbidden fallback | Usually `CODE_REVIEW_EMBEDDING_PROVIDER=mock` and any unset-provider auto fallback. |

Rules for this lane:

1. Print or record the active provider, endpoint/base URL, model, dimensions, and execution provider before each graph/vector write command or before claiming evidence from one.
2. Use `index --status --format json` when available to separate `graph` readiness from `vector` readiness. Structural graph readiness, vector readiness, and subscription-agent annotation writeback are separate claims. A vector `manifested` count means per-item outcomes were persisted for inspection; `rollback_deleted` means stale vectors from a prior non-ready local SQLite run were cleaned before the new run. A follow-up `index` also reprocesses files with generated/error/deferred items from the latest non-ready manifest even when file hashes are unchanged. These repo-side signals still do not prove live target-project dogfood completion.
3. Use `--no-embeddings` for intentional graph-only indexing. Do not use `CODE_REVIEW_EMBEDDING_PROVIDER=mock` as a graph-only shortcut; mock still creates deterministic mock vector rows.
4. `review-cli handoff run-agent` and `review-cli apply-handoff` do not generate embedding vectors. They process and validate subscription-agent annotation results. Do not wrap those commands in a mock embedding env inside a provider-bound lane; record their claim as annotation writeback, not vector provider proof.
5. If the wrong provider, endpoint, model, dimensions, or execution provider is observed, stop the run, audit the process tree/command history where practical, quarantine or clearly mark affected artifacts, and write a retrospective before continuing.

Closeout for code graph work in a provider-bound lane must include:

| Field | Value |
|---|---|
| Provider used | The actual provider family observed during the run. |
| Endpoint/base URL | The actual endpoint or "not applicable". |
| Model and dimensions | The observed model and vector width, or "not used" for graph-only. |
| Graph readiness claim | Structural graph status and supporting command. |
| Vector readiness claim | Vector status and supporting command, or "not claimed". |
| Annotation writeback claim | Handoff/apply status, or "not claimed". |
| Claim supported | Exact claim this evidence supports; do not roll graph/vector/annotation into one readiness statement. |

## Large Graph Retrieval Revalidation

When a downstream repo reports that a reusable `.code-review/graph.sqlite` has been refreshed, verify the graph itself before changing ranking code:

1. Treat the SQLite DB and live CLI output as stronger evidence than a companion `manifest.json`; manifests can lag behind a copied or rebuilt multi-GB graph.
2. Check graph size and counts directly, then run the exact user-facing query surface. For class-first XPO retrieval, use `search-code <repo> "<developer question>" --graph-only --graph-init skip --limit 10`.
3. Inspect `retrieval_stage`, `graph_capability`, `candidate_role`, and `ranking_reasons`; do not treat "topical" hits as sufficient if the requested source-of-truth method is missing from the practical top candidates.
4. Follow a ranked source-of-truth candidate with `impact <file> <method> --format json` or `bounded-context` when the next decision needs dependency or implementation context.
5. Record stale metadata separately from functional proof. A stale manifest, stale path property, or partial topology note is a residual artifact-hygiene finding; it is not automatically a ranking failure if the live query satisfies the acceptance contract.

For the detailed workflow and command examples, read [references/usage-guide.md](references/usage-guide.md) "Large Graph Retrieval Revalidation".

## AX Native Xref Recall Artifacts

For AX2009/X++ recall work, start from raw native xref exports with `xref-normalize`, then score with `xref-recall`:

```bash
review-cli-<os>-<arch> xref-normalize \
  --xref-dir <workspace-root>/projects/giant-ax/lab/download_xref_tables/xref_csv_output \
  --source-object AxSalesLine \
  --target <workspace-root>/projects/giant-ax \
  --out <workspace-root>/projects/giant-ax/.code-review/artifacts/xref/axsalesline.refs.csv \
  --run-log <workspace-root>/projects/giant-ax/.code-review/artifacts/xref/xref-normalize.jsonl
```

Keep reusable refs CSVs, graph-edge dumps, and JSONL run logs under the target repo's ignored `.code-review/artifacts/xref/` instead of `/tmp` when another agent should reuse them. For giant-ax, the sample reusable graph is `<workspace-root>/projects/giant-ax/.code-review/graph.sqlite`; that is the text-based local SQLite graph, distinct from any embedding/vector DB. If that 1GB+ graph is shared later, use an exact GitLab/Git LFS path or artifact-store rule for `.code-review/graph.sqlite` only. For inherited X++ `this.*` calls, include the optional `dispatch_object_qualified_name` column in graph-edge dumps so `xref-recall` can compare at AX native-xref dispatch granularity while the graph edge still targets the real base-class definition. Do not treat `xref-import` + `xref-recall` against the same xref as AST recall evidence; that path validates merge/import behavior, while AST recall requires an independently indexed graph dump.

When X++ producer code changes but the target XPO files did not, do not default to a full giant-ax
rebuild. First refresh only the affected XPO files against the existing text graph:

```bash
PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true \
review-cli-<os>-<arch> xpp-refresh \
  --target <workspace-root>/projects/giant-ax/gts \
  --file Classes/CLASSES_AxSalesLine.xpo \
  --json
```

Use `--file-list .code-review/artifacts/xpp-refresh/changed-xpo-files.txt` for a durable ignored
file set. Keep `xpp-refresh` JSONL run logs under `.code-review/artifacts/xpp-refresh/`. This command
loads the existing graph's Artifact catalog, refreshes only selected parser-derived nodes/edges, and
does not use embeddings or model providers. A full recursive rebuild is reserved for measuring true
full-corpus AST recall or creating a new reusable `graph.sqlite` snapshot.

For informal or not-yet-reproducible X++ parser reports, collect a narrow parser-diagnostics artifact
before patching parser behavior:

```bash
review-cli-<os>-<arch> xpp-diagnose /path/to/file.xpo --json \
  > /path/to/target/.code-review/artifacts/xpp-diagnose/<case>.json
```

The report is `schema_version=xpp-diagnose/v1` and intentionally omits source text. Attach it with
the concrete `.xpo` sample path or sanitized sample, expected AST/graph behavior, and current
`review` / `index` output. Use this for giant-ax partial-function parsing signals before promoting
the report into a Spec #103/#81/#82 CR.

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

Codegen policy is topology-first. Do not broadly exclude generated code just because it is generated when it carries runtime contract or dependency shape. For Ent specifically, keep both `ent/schema/*.go` and generated `ent/**/*.go` in the primary graph when impact analysis, dependency paths, repository/service routing, query/mutation behavior, predicates, hooks, edges, or client wiring may matter. If generated Ent nodes dominate search ranking for a human-authored design task, use a clearly named low-noise profile or temporary `.code-review/config.yaml` rule and record that runtime impact through Ent is incomplete. The current corpus config can include/exclude only; it cannot mark generated nodes as lower-rank. Prefer inclusion for correctness, and use scoped queries/impact surfaces to manage noise.

Use `--no-embeddings` to skip embedding/vector provider initialization. Use `--no-model` when the run must avoid both embeddings and LLM API annotation writes. `--no-model --capabilities` / `--no-model --summaries` still return agent-instruction handoff hints for the coding agent; they do not mean the capability/summary work is forbidden. Current binaries emit both the legacy `.code-review/agent-instruction-{capabilities,summaries}.json` file and a preferred sharded work queue under `.code-review/agent-instruction-handoffs/<run-id>/` with `manifest.json`, `candidates/*.jsonl`, `results/`, and `failures/`. For large repos, agents should process `candidates/*.jsonl` shards independently, write per-item result JSONL rows into `results/`, check `review-cli handoff status <handoff-dir> --format json`, then run `review-cli apply-handoff <handoff-dir> --target <manifest.target_root>`. `review-cli handoff run-agent <handoff-dir> --agent auto --apply` automates that middle step for supported non-interactive subscription-agent CLIs while preserving the same `apply-handoff` validator. This keeps annotation generation async and bounded while final persistence still goes through the same GraphStore writer. Plain Git hooks and `watch` do not run this subscription-agent loop automatically; `graph hook install --subscription-agent` is the explicit opt-in path. `CODE_REVIEW_EMBEDDING_PROVIDER=mock` is a deterministic test provider and still creates mock embedding rows; it is not graph-only indexing.

To install agent-lifecycle handoff hooks from a published global skill inside a target repo, run `python <code-review-skill>/scripts/install-agent-handoff-hooks.py --agent claude,codex,kiro,opencode,antigravity --run-agent auto` from that target repo. The installer embeds the current repo path with `--target` by default; use `--dynamic-target` only when runtime cwd should decide the target.

Two opt-in LLM enrichment passes depend on **separate Agent Skills** that this skill orchestrates but does not contain: `index --capabilities` requires the **`capability-mapper`** skill (Layer 5 `BusinessCapability` nodes) and `index --summaries` requires the **`code-summarizer`** skill (File-node summaries). Both install to `~/.config/opencode/skills/` via their own `install.sh`, are Bedrock-first, and exit non-zero without fabricating when no provider is configured — the graph-only lane never invokes them unless you pass the flag. Details + the read-side vs write-side distinction: [references/cli-commands.md](references/cli-commands.md) `index`.

Annotation lane knobs (CR-2026-07-11): summaries/capabilities **default to the subscription coding-agent CLI** (agent-instruction; `llm-api` opt-in) and have their **own concurrency** separate from embeddings — `--annotation-workers` / `--annotation-rate-limit` (env `CODE_REVIEW_ANNOTATION_WORKERS/_RATE_LIMIT`, default 4). Size the repo with `review-cli corpus-size <root> --format json` and pick a first-run `--index-strategy auto|lightweight|full` (agent-overridable; `lightweight` skips embeddings for small repos). Every `index` also **lands a folder-tree context index** by default — a provider-free, AFM/MEMORY.md-style `CONTEXT.md` per directory under `.code-review/context/<dir>/` (distinct filename, never `MEMORY.md`), discoverable by scanning only the top frontmatter, plus an SSOT `annotation-manifest.json`. Rebuild/refresh it with `review-cli context-index <root>`; opt out with `--no-context-index`. The index carries real summaries/capabilities when they exist (overlaid from the graph — `generated_from: annotated` in the manifest, else `structural`), auto-refreshes after `apply-handoff` / `handoff run-agent --apply`, and the managed Git/agent hook installers now also run an explicit `context-index` refresh step so hook logs show the lifecycle artifact was refreshed.

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

### DevSecOps audit + deep security scan (`review-cli security`)

Where `security-risk-reviewer` is offline OWASP *pattern* triage, the `review-cli security`
command family is the **active DevSecOps layer** — part of the binary itself, so it is
cross-platform and needs no shell scripts. Both commands take `--target <dir>` (default:
cwd); `security scan` also accepts `--target <file>` for narrow hook/review scopes. Both
commands accept `--json`:

| Command | Use it to | Notes |
|---|---|---|
| `review-cli security audit` | **inventory a target project's DevSecOps posture and report gaps** — SAST, secret-scan, dependency-vuln, SBOM, dependabot, signing, pre-commit, license, OWASP-LLM agent-safety | pure-Go filesystem inspection; deterministic; scores maturity % + lists high-severity gaps + a fix per gap. Use it to answer "what DevSecOps controls is this project missing?" |
| `review-cli security scan` | **invoke deep multi-language scans** (JS/C#/Py/Go SAST + secret + dependency-vuln + SBOM/misconfig) against the target | detects tools via `LookPath`, runs `govulncheck`/`gitleaks`/`trivy`/`semgrep`, honest `tool-unavailable` (never silent-skip). **Local-tool fallback today; preferred path is delegation to `~/aclab-middlewares/security-stack` (`sectool`/`secsdlc-mcp` → DefectDojo/Dependency-Track)** once its integration contract lands (see that spec's CR). |
| `review-cli security grounding --hook-mode --warn-only --stderr --timeout 60` | **advisory Stop-hook content-safety grounding** for agent output | installed Claude/Codex/Kiro Stop hooks use the configured `review-cli` command from agent settings; raw `review-cli security grounding` still honors `--warn-only` on timeout. OpenCode's session-idle plugin uses `.nothrow()` advisory scan behavior. Omit `--warn-only` only for an intentional blocking security gate. |
| `review-cli security hook-audit` | **inspect installed Stop hooks for xreview/security-grounding drift** | read-only audit that classifies xreview as advisory/non-blocking, detects `security grounding` hooks that drifted from expected `--warn-only`, and labels unknown Stop-hook commands for operator routing. |
| `review-cli security hook-diagnose` | **classify captured Stop-hook stdout/stderr protocol failures** | feed captured stdout/stderr/exit-code evidence to distinguish `stdout-not-json`, `stdout-json-schema-mismatch`, `stdout-mixed-protocol-and-logs`, `stdout-empty-when-json-required`, and `hook-exit-nonzero`; previews are bounded and redacted. |

These emit **deterministic evidence** that feeds the companion `security-review` skill's lanes
(`infrastructure-supply-chain.md`, `ai-agent-mcp.md` for OWASP-LLM, and the
`languages/{go,javascript-typescript,python,dotnet-csharp}.md` lanes) — they do not adjudicate;
`review.md` + the `security-review` gate keep verdict authority. Spec: `local-devsecops-hardening`.

### NIS2 / GenAI / SecSDLC Evidence Packet

When the user asks for NIS2, GenAI usage, AI-assisted development, SecSDLC, OWASP LLM Top 10, RAG,
MCP/tool execution, coding-agent governance, or developer compliance evidence, produce a bounded
evidence packet instead of a compliance verdict:

- graph preflight/status, focused `impact` / `dependency-path` / `bounded-context` / `search-code`
  queries for the changed AI, data, CI/CD, and security-sensitive components;
- `review-cli security audit --target <dir>` posture evidence when available;
- `review-cli security scan --target <dir>` SAST/SCA/secrets/SBOM evidence or honest
  `tool-unavailable` / `dependency not configured` notes;
- SBOM, provenance/signing, dependency lockfile, CI/CD, model/provider, MCP/tool, and supply-chain
  evidence refs;
- OWASP LLM Top 10 evidence refs for prompt injection, sensitive-data leakage, supply chain,
  poisoning, output handling, excessive agency, prompt leakage, vector/embedding weaknesses,
  misinformation, and unbounded consumption.

Feed this packet to `security-review` for per-change trust-boundary judgment and to
`iso-ai-security-auditor` for NIS2 / EU AI Act / GDPR / ISO / NIST evidence inventory. Do not turn
the packet into legal compliance, certification, or release-readiness approval.

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
lists). It now spans **Go, Python, TypeScript/JavaScript, C#, and XPO/XPP** (the last driven by a
native AX 2009 X++ method-body AST):
- **Go** — `go/ast` pass + authoritative `go vet` / `go test -race` adapter.
- **Python** — `REVIEW_PY_MUTABLE_DEFAULT` (B006), `REVIEW_PY_BARE_EXCEPT` (E722), `REVIEW_PY_MONEY_FLOAT`.
- **TypeScript/JavaScript** (`.ts`/`.tsx`/`.js`/`.jsx`) — `REVIEW_TS_MONEY_NUMBER`, `REVIEW_TS_EMPTY_CATCH`, `REVIEW_TS_EXPLICIT_ANY` where syntax support is available; JS/TS also has line-level maintainability coverage in no-tree-sitter builds.
- **C#** — `REVIEW_CS_MONEY_FLOAT` (float/double vs decimal), `REVIEW_CS_EMPTY_CATCH`, `REVIEW_CS_ASYNC_VOID`.
- **XPO/XPP** — a native AX 2009 `.xpo` method-body AST (`source=xpp-ast`, build-tag-free → runs on all six binaries incl. darwin) drives money-as-`real`, `REVIEW_XPP_TTS_UNBALANCED`, `REVIEW_QUERY_IN_LOOP` (select in a loop), `REVIEW_XPP_DML_OUTSIDE_TTS`, `REVIEW_XPP_EMPTY_CATCH`, `REVIEW_XPP_ASSIGNMENT_IN_CONDITION`, `REVIEW_XPP_INFINITE_LOOP_CANDIDATE`, and `REVIEW_XPP_UNUSED_RETURN`; the language-agnostic file-level smells (`REVIEW_GOD_FILE` / duplicated-block, `source=xpp-line`) still apply. `review --xpp-metrics` emits an aggregate AST metrics summary (nesting, tts-balance, select-in-loop, money-as-real rates). Fulfils Spec #103.
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
