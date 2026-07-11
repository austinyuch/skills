# CLI Commands Reference

<!-- min-review-cli-version: 0.19.1 -->

## Compatibility

This reference documents the CLI surface as of **`review-cli` v0.19.1** (the
`min-review-cli-version` marker above is the machine-readable floor). Flags and
commands such as `--no-embeddings`, `--no-model`, `--capabilities`, `--summaries`,
`apply-handoff`, `capability-inventory`, and `summary --granularity` require a
binary at or above this version. If a documented flag errors with `unknown flag`
or a command returns an empty/legacy result, verify the vendored binary:

```bash
review-cli-<os>-<arch> version   # must be >= the marker above
```

A stale vendored binary — not documentation drift — is the most common cause of a
mismatch; re-sync per `VENDORED_SYNC.md`. The repo-side `check_docs_freshness.py`
gate keeps this marker in major.minor lock-step with the shipped binary.

## Command Syntax

Targets are passed positionally; behavior is tuned with flags (documented per command below).
Use the matching published binary for your host:

```bash
review-cli-<os>-<arch> <command> <target> [flags]
```

**Global flag:** `--config <path>` is available on every command (default `config.yaml`) to point at an alternate configuration file.

## Available Commands

### analyze
Analyze code files for structure and metrics.

**Usage:**
```bash
review-cli-<os>-<arch> analyze <filepath>
```

**Output:**
- Language detected
- Function count
- Class/struct count
- Complexity metrics
- Import analysis

**Example:**
```bash
review-cli-<os>-<arch> analyze ./internal/agent/scan.go
```

---

### improve
Generate improvement suggestions for code.

**Usage:**
```bash
review-cli-<os>-<arch> improve [project]
```

The positional argument is a **project path** (default `.`), not a single file. The binary's usage is `improve [project]`.

**Output:**
- Specific improvement suggestions
- Rationale for each suggestion
- Priority level

**Example:**
```bash
review-cli-<os>-<arch> improve ./internal
```

---

### report
Generate comprehensive review report.

**Usage:**
```bash
review-cli-<os>-<arch> report <directory> [--open]
```

**Flags:**
- `--open` — open the generated report in the default browser.

**Output:**
- Executive summary
- Code metrics
- Issues found
- Recommendations
- Architecture insights

**Example:**
```bash
review-cli-<os>-<arch> report ./internal
review-cli-<os>-<arch> report ./
```

---

### architecture
Analyze system architecture and dependencies.

**Usage:**
```bash
review-cli-<os>-<arch> architecture <directory> [--open]
```

**Flags:**
- `--open` — open the generated analysis in the default browser.

**Output:**
- Module structure
- Dependency graph
- Design patterns detected
- Architecture recommendations

**Example:**
```bash
review-cli-<os>-<arch> architecture ./
review-cli-<os>-<arch> architecture ./internal
```

---

### scan
Scan specification files.

**Usage:**
```bash
review-cli-<os>-<arch> scan <spec-directory>
```

**Expected Files:**
- requirements.md
- design.md
- tasks.md

**Output:**
- Spec completeness check
- Missing sections
- Validation results

**Example:**
```bash
review-cli-<os>-<arch> scan ./.agents/specs/go-backend-rewrite
```

---

### version
Display version information.

**Usage:**
```bash
review-cli-<os>-<arch> version
```

---

### review
Static review of **Go, Python, TypeScript/JavaScript, C#, and XPO/XPP** source: concurrency,
resource leaks, error handling, numeric/time correctness, and maintainability. Built into
`review-cli` (a `go/ast` pass for what the Go toolchain misses, plus an authoritative `go vet` /
`go test -race` adapter; tree-sitter passes for Python/TypeScript/C# where linked; and line-level
checks for JavaScript/XPO fallback cases) — distinct from the heuristic Python helper skills. Rules
per language:
- **Python:** `REVIEW_PY_MUTABLE_DEFAULT` (B006), `REVIEW_PY_BARE_EXCEPT` (E722), `REVIEW_PY_MONEY_FLOAT`.
- **TypeScript/JavaScript** (`.ts`/`.tsx`/`.js`/`.jsx`): `REVIEW_TS_MONEY_NUMBER` (TS/JS `number` is a float), `REVIEW_TS_EMPTY_CATCH`, `REVIEW_TS_EXPLICIT_ANY` where syntax support is available; JS/TS also has line-level maintainability coverage in no-tree-sitter builds.
- **C#:** `REVIEW_CS_MONEY_FLOAT` (`float`/`double` vs `decimal`), `REVIEW_CS_EMPTY_CATCH`, `REVIEW_CS_ASYNC_VOID`.
- **XPO/XPP:** `.xpo` exports receive line-level maintainability checks such as `REVIEW_GOD_FILE` and duplicated-block with `source=xpp-line`; this is not a full X++ AST rule pack.
- **Shared maintainability:** `REVIEW_LONG_PARAM_LIST` (> 5 params), `REVIEW_LONG_METHOD` (> 60-line body), `REVIEW_DEEP_NESTING` (> 4 nesting levels; `else if` chains don't inflate depth), plus file/block smells where supported.

The tree-sitter (Python/TS/C#) rules run only in the tree-sitter build — the shipped linux/windows
binaries are tree-sitter; the darwin binaries degrade with an honest "requires the tree-sitter build"
note. Any still-unsupported target reports an honest note rather than failing.

**Usage:**
```bash
review-cli-<os>-<arch> review <file|directory> [--language go|python|typescript|csharp|xpp] [--vet] [--race] [--format text|json|jsonl] [--exclude DIR] [--no-respect-gitignore] [--xpp-metrics]
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--vet` | Also run `go vet ./...` and fold its findings in (authoritative; lostcancel/copylocks/loopclosure). |
| `--race` | Also run `go test -race ./...` and fold real data races in (authoritative). |
| `--format <text\|json\|jsonl>` | Output format (default `text`). Use `jsonl` for large persisted evidence: one metadata line, one finding per line, and one note per line. |
| `--language <family>` | Review only one language family. Repeatable. Supported values: `go`, `python`, `typescript`/`javascript`, `csharp`, and `xpp`. Use this to avoid unrelated parser/degrade work in mixed repos. |
| `--graph` | Fold graph **blast-radius** (distinct callers of the file's functions) + **owning capability** into the finding ranking (Phase 4a). Requires an indexed project graph (`index`); best-effort — an un-indexed target falls back to the deterministic ranking. Findings carry `blast_radius` + `capability`, and within a severity tier higher-blast-radius findings rank first. |
| `--exclude <dir-or-pattern>` | Exclude a directory or ignore-style pattern from directory review. Repeatable. Review uses the same built-in corpus exclusions as `index` (`.next`, `.nuxt`, `.output`, `.turbo`, `node_modules`, `.code-review`, etc.). |
| `--no-respect-gitignore` | Do not parse `.gitignore` or legacy `.reviewignore`; built-in, `.code-review/config.yaml`, and `--exclude` rules still apply. |
| `--xpp-metrics` | Emit an aggregate **X++ AST metrics** summary as JSON (files, methods, avg/max nesting depth, tts-balance rate, select-in-loop rate, money-as-`real` rate) over the `.xpo` corpus, **instead of** per-finding output. Honors `--language`/`--exclude`. |

Findings carry `rule`, `category` (concurrency / resource-leak / error-handling / numeric / time),
`severity`, `file:line`, `message`, `remediation`, and `source` (`go-ast` / `go-vet` / `go-race`),
ranked by severity. The `go/ast` checks are accurate by construction — e.g. goroutine
loop-variable capture and lock-without-`defer`-unlock — which is why this lives in the Go binary.

---

### index
Build or refresh graph state for a project.

**Usage:**
```bash
review-cli-<os>-<arch> index <project-path> [--no-embeddings|--no-model]
```

**Use `--no-embeddings` when:**
- policy or cost constraints require no embedding model and no vector provider initialization
- the change set is code-only and deterministic graph reconciliation is sufficient
- you want a `no-model` graph-only indexing run before structural graph queries

`--no-embeddings` does not remove vector support from the product; it only forces this run to avoid embedding/vector providers.

Use `--no-model` when the run must avoid both embedding/vector providers and LLM API annotation writes. `--no-model` does **not** forbid capabilities or summaries: with `--capabilities` or `--summaries`, the CLI resolves the source corpus and returns an `agent-instruction` handoff/guideline for a subscription coding agent instead of invoking provider APIs.

If the user names a concrete embedding provider/model/endpoint for evidence, this command is provider-bound. Record the allowed provider, endpoint/base URL, model, dimensions, execution provider if relevant, and forbidden fallback before the run. Use `--no-embeddings` for a graph-only claim; do not set `CODE_REVIEW_EMBEDDING_PROVIDER=mock` as a workaround in a provider-bound lane. Mock is a deterministic test provider and creates mock vector rows.

**Optional LLM enrichment flags (depend on separate Agent Skills):**

After Layers 1–4, `index` can run two opt-in enrichment passes. Each is powered by its **own separate skill** — `code-review` orchestrates them but does not contain them:

| Flag | Adds to graph | Requires skill | Notes |
|------|---------------|----------------|-------|
| `--capabilities` | Layer 5 `BusinessCapability` nodes (maps files/symbols to a business capability) | **`capability-mapper`** (Spec #54, CR-2026-06-02-001) | LLM judgment; emits `confidence` + `reasoning` |
| `--summaries` | File-node structured summaries | **`code-summarizer`** (Spec #56) | LLM judgment; emits `confidence` + `reasoning` |

Both required skills install to `~/.config/opencode/skills/<skill>/` via their own `scripts/install.sh`. The default annotation mode is `agent-instruction`, intended for subscription coding agents such as Codex/Claude Code/Kiro. Explicit `llm-api` mode is Go/ADK based and provider-backed. These flags are independent of `--no-embeddings`: the graph-only lane never invokes them unless you add the flag. (Separately, `index --lsp-edges` is Go-only and needs an external language server such as `gopls`; honest no-op without one.)

Do **not** confuse these with the read-side `capability-inventory` and `summary` commands below — those *query* an already-annotated graph; `--capabilities` / `--summaries` are what *write* those annotations.

The `--capabilities` run summary is **eligibility-aware** (Spec #87 cluster): only behavioral artifacts (e.g. X++ Classes/Forms) are enrichable, so the text summary reports `N processed, M failed (E of C recognized source files eligible; S skipped — no behavioral symbols)` — "processed" is not the same as "failed". With `--format json` it emits a structured `{"skill_available","annotation_mode","handoff_required","guideline","files_considered","files_eligible","files_skipped_no_symbol","files_processed","files_failed"}` object instead of human lines.

**Agent-instruction writeback round-trip (`handoff status` + `apply-handoff`, Spec #97 CR-2026-06-22-001 / CR-2026-07-09-001):** in `agent-instruction` mode `--capabilities`/`--summaries` only *emit a handoff*; they do not write graph annotations (that is by design — `review-cli` calls no provider API in this mode). To actually enrich the graph "with a subscription coding agent", complete the round-trip:

1. `review-cli index <path> --no-model --capabilities --handoff-shard-size 500` (and/or `--summaries`) writes the legacy `.code-review/agent-instruction-{capabilities,summaries}.json` plus a sharded work queue at `.code-review/agent-instruction-handoffs/<run-id>/`.
2. Prefer the sharded path for large repos: agents process `candidates/*.jsonl` independently, write one result JSON object per line into `results/*.jsonl`, and check progress with `review-cli handoff status <handoff-dir> [--format text|json]`.
3. Either run the agent manually, or use `review-cli handoff run-agent <handoff-dir> --agent auto --apply`. The command detects supported non-interactive CLIs (`codex exec`, Claude Code `claude -p`, `opencode run`, `kiro-cli chat --no-interactive`, `agy -p`) or uses `--agent-command <wrapper>` for custom agents, waits for result shards, then calls the same apply path.
4. Before installing lifecycle hooks, run `review-cli handoff agent-doctor --agent <agent|all|auto> --strict` to verify the real host CLI command shape without sending an annotation prompt. Built-in checks validate `codex exec --help`, `claude -p --help`, `opencode run --help`, `kiro-cli chat --no-interactive --help`, and `agy -p --help`; custom `--agent-command` wrappers get executable-only validation.
4. `review-cli apply-handoff <handoff-dir> [--target <root>] [--format text|json]` writes sorted result shards into the graph through the **same** writer `llm-api` mode uses (canonical `BusinessCapability` nodes, `SERVES` edges for declared `req_id`s, `business_value`, File summaries), tagged `annotation_mode=agent-instruction`.
5. Legacy single-file result envelopes remain supported: the skills' `run.py --emit-result-envelope --target-root <root>` (reads a JSON array of `{source_file, capability|summary, …}` from `--annotations <file>` or stdin) assembles `agent-instruction-{capabilities,summaries}-result/v1`; apply it with `review-cli apply-handoff <result.json>`.

`apply-handoff` is **fail-closed**: a wrong `schema_version`/`cost_class`/`provenance` rejects the whole file or shard; per item, an out-of-range confidence, a `source_file` outside `target_root` or absent from the current graph, or an undeclared `req_id` fails that item (counted in `files_failed` with a printed reason) without writing it — never a partial write, never a fabricated requirement. JSON output reports `files_processed`/`files_failed`/`nodes_created`/`serves_created`/`summaries_written`/`failures`, reconcilable with the handoff's `candidate_count`. `review-cli` still calls no provider API — the annotations come from the agent.

`handoff run-agent` and `apply-handoff` do not consume embedding provider configuration to create vectors. In a provider-bound evidence lane, do not prefix these commands with `CODE_REVIEW_EMBEDDING_PROVIDER=mock`; record their result as subscription-agent annotation writeback evidence only. Vector readiness still needs `index --status --format json` or an equivalent vector-specific check from the embedding-backed indexing command.

**Complete `index` flag reference** (authoritative — mirrors the binary):

| Flag | Meaning |
|------|---------|
| `--no-embeddings` | Force graph-only indexing; do not initialize embedding/vector providers (cost class: no-model; Spec #62). |
| `--no-model` | Force no-model indexing: no embeddings and no LLM API annotation writes. `--capabilities`/`--summaries` return agent-instruction handoff hints instead of provider execution. |
| `--handoff-shard-size <int>` | Agent-instruction candidates per JSONL shard; `<=0` disables the sharded handoff directory and leaves only the legacy single-file handoff. |
| `--status` | Show index status instead of indexing. |
| `--watch` | With `--status`: poll readiness every 2s until Ctrl-C (REQ-ICB-103). Distinct from the top-level `watch` command. |
| `--force` | Force a full re-index (clears the triage cache). |
| `--recursive` | Directory-batch recursive execution with structured progress/result/error reporting. |
| `--resume` | With `--recursive`: skip checkpointed completed batches and continue pending work. |
| `--restart` | With `--recursive`: discard the recursive checkpoint and start a fresh job. |
| `--batch-max-files <int>` | With `--recursive`: max files per commit batch (default 100). |
| `--batch-max-bytes <size>` | With `--recursive`: max logical input bytes per batch, e.g. `64MB`, `128MiB` (default `64MB`). |
| `--batch-sort <dir\|name\|mtime>` | With `--recursive`: batch ordering (default `dir`; git changed/untracked files prioritized when available). |
| `--prune-ignored` | With `--recursive`: remove existing File/symbol/vector traces no longer in the discovered corpus. |
| `--embedding-batch-size <int>` | Embedding provider batch size override for this run. Distinct from recursive file batching. |
| `--embedding-workers <int>` | Embedding provider worker count override for this run. Use low values for bounded local/self-hosted endpoints. |
| `--embedding-rate-limit <float>` | Embedding provider request rate limit override in requests per second; `0` disables rate limiting. |
| `--embedding-timeout <duration>` | Embedding provider request timeout override, e.g. `60s`, `1m`, `2m30s`. |
| `--exclude <dir>` | Exclude a directory (repeatable; REQ-ICB-003). See "Index Corpus Ignores" in usage-guide.md. |
| `--no-respect-gitignore` | Do not parse `.gitignore`/legacy `.reviewignore`; use builtin + `.code-review/config.yaml` + `--exclude` only (REQ-ICB-002). |
| `--dry-run-corpus` | Report the corpus plan and exit before indexing. Use `--format json` for included/excluded samples with matched source/rule. |
| `--coverage` | Show the local-sqlite XPO coverage diagnostic for a directory instead of indexing. |
| `--diff-base <sha>` | Git SHA for incremental test-traceability indexing (only re-index changed files). |
| `--lsp-edges` | Resolve cross-file references via a language server (e.g. `gopls`) → Layer-4 `RESOLVES_TO` edges (Go only; honest no-op without a server; Spec #57). |
| `--capabilities` | Layer 5 capability enrichment — requires `capability-mapper` (see table above). |
| `--summaries` | File-summary enrichment — requires `code-summarizer` (see table above). |
| `--format <text\|json>` | Output format for `--recursive`, `--coverage`, or `--dry-run-corpus` mode (default `text`). |

---

### search-code
Inspect retrieval results over graph state.

**Hybrid graphRAG usage:**
```bash
review-cli-<os>-<arch> search-code <artifact-path> "<natural language query>"
```

**Graph-only usage:**
```bash
review-cli-<os>-<arch> search-code <artifact-path> "<file, symbol, or structural query>" --graph-only
```

Use hybrid graphRAG for broad semantic recall and ranking. Use `--graph-only` for exact structural questions when embeddings/provider APIs are unavailable or disallowed.

**Graph-only ranking (Spec #89):** without embeddings, results are ordered by a deterministic **structural rank** — name-match quality (exact > case-insensitive/qualified > whole-word > substring) combined with token coverage — so exact-name matches sort above substring matches instead of all tying. Each result discloses its `ranking_reasons` (e.g. `exact name match`, `token coverage 1.00`); a `notes` line states the rank is structural, not semantic.

---

### graph (program-graph management)

`graph` is a command **group** for managing the program graph. Subcommands: `boundary`, `export`, `fragment`, `gc`, `hook`, `zoom-precompute`. (For index/graph readiness use `index --status` — there is no `graph status` subcommand.)

#### graph fragment
Validate and import subscription-agent graph fragments. Subcommands: `validate`, `apply`, `example`.

**Usage:**
```bash
review-cli-<os>-<arch> graph fragment validate fragment.json --target <project-path>
review-cli-<os>-<arch> graph fragment apply fragment.json --target <project-path> --source-owned
review-cli-<os>-<arch> graph fragment example         # print a minimal valid agent-graph-fragment/v1 JSON
```

**`apply` / `validate` flags:**
- `--target <path>` — project root whose graph store receives/validates the fragment (default `.`).
- `--source-owned` (apply only) — replace prior agent-fragment edges owned by each `source_file` before writing (default `true`).

Fragments must use `schema_version=agent-graph-fragment/v1`, `cost_class=subscription-agent`, and `provenance=agent-fragment`. The CLI validates confidence, source-file containment, node types, relation allowlist, and payload limits before graph writes. Use `graph fragment example` to get a known-valid starting template.

#### graph boundary
Manage `IntegrationBoundary` nodes (HITL cross-system contracts) in the graph. Subcommands: `add`, `list`.

**Usage:**
```bash
review-cli-<os>-<arch> graph boundary add --name <name> --type <type> --source-path <path> [--description <text>] [--repo <name>]
review-cli-<os>-<arch> graph boundary list [--format text|json]
```

**`add` flags:** `--name` (required), `--type` (required), `--source-path` (required), `--description`, `--repo`.
`--type` is one of: `rest_api`, `grpc_service`, `event_contract`, `db_schema`, `openapi_contract`, `graphql_schema`.

#### graph gc
Detect (and optionally remove) orphaned nodes — nodes with no incoming/outgoing edges and no `Repository` association.

**Usage:**
```bash
review-cli-<os>-<arch> graph gc [--dry-run] [--include-hitl]
```

- `--dry-run` — list orphans without deleting.
- `--include-hitl` — also consider HITL-created `IntegrationBoundary` nodes (excluded by default).

#### graph export
Carve a **bounded subgraph** out of the program graph via depth-bounded BFS from a focus node, and write it as a small SQLite (or JSON) file. Use this when the full `graph.sqlite` is too large to open whole in the browser-side Graph Explorer — the exported subgraph stays under `--max-nodes` (default 5000, aligned with the viewer node limit) so it loads directly.

**Usage:**
```bash
review-cli-<os>-<arch> graph export --center <node> --depth 2 --output subgraph.sqlite
review-cli-<os>-<arch> graph export --center path/to/File --depth 1 --format json --output subgraph.json
review-cli-<os>-<arch> graph export --center some:node:id --depth 3 --graph-db .code-review/graph.sqlite --output subgraph.sqlite
```

**Flags:**
- `--center <string>` (required) — focus node, matched by exact id, id substring, or a substring of its name/file_path/path.
- `--depth <int>` — BFS expansion hops from the focus node (default `1`).
- `--format sqlite|json` — output format (default `sqlite`). SQLite output opens directly in the Graph Explorer.
- `--output <path>` (required) — output file path.
- `--max-nodes <int>` — cap before truncation (default `5000`); reaching it stops expansion and marks the result truncated.
- `--graph-db <path>` — explicit graph DB path (overrides `--target` resolution).
- `--target <dir>` — project root used for local-sqlite graph DB resolution (default `.`).

#### graph zoom-precompute
Materialize semantic-zoom aggregation metadata (per-node rel path, name, edge degree) into a derived table so the viewer's server-side `/__graph_view` overview/drill-down reads indexed rows instead of scanning the whole graph per request. Optional speedup for very large graphs; the viewer falls back to on-the-fly aggregation when the precompute is missing or stale (tracked by a node/edge-count marker). Safe to re-run.

**Usage:**
```bash
review-cli-<os>-<arch> graph zoom-precompute                        # resolve local-sqlite graph from --target (default .)
review-cli-<os>-<arch> graph zoom-precompute --graph-db .code-review/graph.sqlite
```

**Flags:**
- `--graph-db <path>` — explicit graph DB path (overrides `--target` resolution).
- `--target <dir>` — project root used for local-sqlite graph DB resolution (default `.`).

#### graph hook
Manage a Git post-commit hook that triggers precise incremental graph/vector re-indexing. Subcommands: `install`, `status`, `uninstall`.

Plain hook mode is a Git/review-cli mechanism only; it does not run a subscription agent. The generated hook bakes the resolved persistence env into the managed block (`CODE_REVIEW_PERSISTENCE_MODE`/`PERSISTENCE_MODE`, `CODE_REVIEW_SQLITE_ENABLED`/`SQLITE_ENABLED`, and SQLite file/state aliases when present); if no mode is resolved, Git-hook installs default to repo-local `local-sqlite` with SQLite enabled. Opt-in `--subscription-agent` mode first runs no-model capability/summary handoff generation synchronously, then launches `handoff run-agent --latest --artifact all --apply` detached from the commit via `setsid nohup`/`nohup`; that detached command invokes a supported non-interactive agent CLI or an explicit `--agent-command` wrapper and applies results through `apply-handoff`. Do not use hook installation or commit return as proof that annotations completed; verify the handoff/apply result before claiming subscription-agent annotation writeback.

**Usage:**
```bash
review-cli-<os>-<arch> graph hook install     # install the managed post-commit hook
review-cli-<os>-<arch> graph hook install --subscription-agent --agent auto
review-cli-<os>-<arch> graph hook status      # show whether the managed hook is installed
review-cli-<os>-<arch> graph hook uninstall   # remove the managed hook block
```

**Flags:**
- `--path <dir>` — path inside the Git repository to manage/inspect (default `.`; all three subcommands).
- `--binary <path>` (install only) — `review-cli` binary the hook invokes (default: current executable).
- `--fail-on-error` (install only) — let hook failures propagate instead of logging and continuing.
- `--subscription-agent` (install only) — after synchronous `index --no-model --capabilities --summaries`, launch latest handoffs through detached `handoff run-agent --apply`.
- `--agent <auto|codex|claude|opencode|kiro|antigravity>` (install only) — subscription agent selector for `--subscription-agent`; Kiro uses `kiro-cli chat --no-interactive`, Antigravity uses `agy -p`.
- `--agent-command <command>` (install only) — explicit non-shell wrapper command passed to `handoff run-agent`.

For agent StopHook/session-idle lifecycle installation from a published global skill, use `scripts/install-agent-handoff-hooks.py` from the `code-review` skill directory while your shell is in the target repo. It installs Claude/Codex/Kiro Stop hooks, an OpenCode idle plugin, and an Antigravity agy plugin that call `scripts/agent-handoff-hook.py`; the wrapper then runs `index --no-model --capabilities --summaries`, an explicit `context-index` refresh, and `handoff run-agent --apply` against the target repo. Use `--preflight` when installing so the script runs `handoff agent-doctor --strict` before writing hooks.

The project SQLite graph DB is single-writer — enforced by a single writer connection plus a `busy_timeout` — so concurrent graph mutations against the same DB serialize (a second writer waits) rather than failing with `SQLITE_BUSY` while a hook-triggered index is active.

---

### xref-normalize
Normalize raw AX2009 native xref table exports into the CSV contract consumed by `xref-recall` and `xref-import`.

**Usage:**
```bash
review-cli-<os>-<arch> xref-normalize \
  --xref-dir <workspace-root>/projects/giant-ax/lab/download_xref_tables/xref_csv_output \
  --source-object AxSalesLine \
  --target <workspace-root>/projects/giant-ax \
  --out <workspace-root>/projects/giant-ax/.code-review/artifacts/xref/axsalesline.refs.csv \
  --run-log <workspace-root>/projects/giant-ax/.code-review/artifacts/xref/xref-normalize.jsonl
```

**Flags:**
- `--xref-dir <dir>` — directory containing raw `XREFPATHS.csv`, `XREFNAMES.csv`, and `XREFREFERENCES.csv`.
- `--out <path>` — write normalized references CSV to this path. When omitted, CSV is written to stdout.
- `--source-object <name>` — scope to one AX source object and emit that object name as `source` (for example `AxSalesLine`).
- `--source-path-prefix <path>` — raw AOT path prefix for `--source-object`; default is `\Classes\<source-object>`.
- `--target <dir>` — target project root used only for graph/artifact path hints.
- `--run-log <path>` — append a JSONL run record to a durable ignored path.

**Output contract:**
`source,target,target_kind,reference,line`, where field and method targets are owner-qualified (`Table.Field`, `Class.method`) and enum literals roll up to their owning enum. `xref-recall` filters the denominator to graph-modeled first-layer families.

**Artifact convention:**
For reusable AX recall evidence, prefer target-local ignored paths such as `.code-review/artifacts/xref/*.csv` and `.code-review/artifacts/xref/*.jsonl` over `/tmp`. For the giant-ax sample project, the reusable full graph is `<workspace-root>/projects/giant-ax/.code-review/graph.sqlite` (about 1.2 GB on this host). If a target repo deliberately shares that graph later, track only the exact `.code-review/graph.sqlite` path via GitLab/Git LFS or an equivalent artifact store; keep derived refs, graph-edge dumps, and JSONL run logs ignored unless the target repo explicitly promotes a curated evidence file.

### xpp-diagnose
Emit method-level AX2009/XPO parser diagnostics for one `.xpo` file without writing graph state or
including source text in the report.

Use this before promoting an informal partial-function parser report into a Spec #103/#81/#82 CR.
The JSON contract is `schema_version=xpp-diagnose/v1` and includes SOURCE block counts, method line
spans, brace balance, parsed statement counts, raw-statement ratio, calls, table / field / enum
references, intrinsics, labels, and structured diagnostics.

**Usage:**
```bash
review-cli-<os>-<arch> xpp-diagnose <workspace-root>/projects/giant-ax/gts/Classes/CLASSES_AxSalesLine.xpo --json
review-cli-<os>-<arch> xpp-diagnose /path/to/file.xpo --method suspectMethod --json
```

**Flags:**
- `--json` — emit `schema_version=xpp-diagnose/v1` JSON.
- `--method <name>` — only report the SOURCE block whose parsed or source name matches this method.

**Bug-report evidence bundle:**
Attach the `xpp-diagnose` JSON, the concrete `.xpo` sample path or sanitized sample, the expected
AST/graph behavior, and current `review` / `index` output. Keep reusable reports under
`.code-review/artifacts/xpp-diagnose/*.json` so they are durable for agents but ignored by default.

### xpp-refresh
Refresh selected X++ parser-derived graph nodes/edges against an existing project graph without rebuilding the full corpus.

Use this when `review-cli` producer logic changed but the XPO source content did not, so a normal
incremental `index` would skip by content hash. The command loads the target graph's existing XPP
Artifact catalog and re-runs graph-only indexing only for the explicit file set.

**Usage:**
```bash
review-cli-<os>-<arch> xpp-refresh \
  --target <workspace-root>/projects/giant-ax/gts \
  --file Classes/CLASSES_AxSalesLine.xpo \
  --json

review-cli-<os>-<arch> xpp-refresh \
  --target <workspace-root>/projects/giant-ax/gts \
  --file-list <workspace-root>/projects/giant-ax/gts/.code-review/artifacts/xpp-refresh/changed-xpo-files.txt \
  --json
```

**Flags:**
- `--target <dir>` — project root whose existing `.code-review/graph.sqlite` is refreshed.
- `--file <path>` — XPO file to refresh; repeatable. Relative paths resolve under `--target`.
- `--file-list <path>` — newline-delimited XPO file list; blank lines and `#` comments are ignored.
- `--dry-run` — resolve inputs and print the planned file set without graph writes.
- `--json` — emit `schema_version=xpp-refresh-run/v1` summary JSON.

Keep file lists and JSONL run logs under `.code-review/artifacts/xpp-refresh/` so they are durable
for agents but ignored by default. `xpp-refresh` updates the text-based graph only; it does not touch
embedding/vector DBs, does not import xref ground truth, and does not by itself prove AST recall.
For recall evidence, dump graph edges after refresh and run `xref-recall`. For a full-corpus recall
lift or a new reusable giant-ax graph snapshot, run the explicit full Path A rebuild separately.

### xref-recall
Score normalized AX native xref references against a normalized code-review graph edge dump.

**Usage:**
```bash
review-cli-<os>-<arch> xref-recall --xref axsalesline.refs.csv --graph axsalesline.graph.csv --floor 0.8
review-cli-<os>-<arch> xref-recall --xref axsalesline.refs.csv --graph axsalesline.graph.csv --json
```

**Flags:**
- `--xref <path>` — normalized AX xref references CSV from `xref-normalize` or an equivalent producer.
- `--graph <path>` — normalized graph edge dump CSV with `source,rel,target[,fields]`. `fields` may be semicolon/comma-separated or a JSON array from SQLite `json_extract`.
- `--floor <0..1>` — minimum overall recall required to pass.
- `--json` — emit the report as JSON.

### xref-import
Materialize first-layer graph edges directly from normalized AX native xref references.

**Usage:**
```bash
review-cli-<os>-<arch> xref-import --xref axsalesline.refs.csv --target /path/to/project
review-cli-<os>-<arch> xref-import --xref axsalesline.refs.csv --target /path/to/project --json
```

**Flags:**
- `--xref <path>` — normalized AX xref references CSV.
- `--target <dir>` — project whose graph store receives the edges (default `.`).
- `--json` — emit the import summary as JSON.
- `--fabricate-missing` — upsert a bare-name node for an endpoint absent from the graph. Default is strict merge: skip unresolved endpoints and report them, never create orphan nodes.

Keep the evidence boundary clear: `xref-normalize` + `xref-recall` measures parser graph recall when the graph dump came from AST indexing. `xref-import` validates xref-to-graph merge/import behavior; scoring imported xref edges against the same xref is circular and must not be claimed as AST recall.

---

### watch
Run a long-running watcher that observes working-tree file changes and drives the incremental reconciliation pipeline, so the code graph stays fresh while you edit — without waiting for a commit (Spec #66). It is a **trigger surface**, not a separate indexer: it reuses the same per-file reindex and source-owned cleanup as `index`.

**Usage:**
```bash
review-cli-<os>-<arch> watch [path] [flags]
```

**Flags:**
- `--once` — run a single initial index pass then exit (no long-running watch).
- `--debounce <duration>` — coalesce window for file-change events (default `500ms`).
- `--bridge <addr>` — also enable the IDE event bridge on this local address (e.g. `127.0.0.1:7842`).
- `--json` — suppress the human banner; emit only machine-readable JSON.

**Examples:**
```bash
review-cli-<os>-<arch> watch . --once --json          # one working-tree pass, JSON output
review-cli-<os>-<arch> watch . --debounce 1s          # long-running, 1s coalesce window
```

---

### diagnostics and configuration

These commands are useful when triaging provider wiring or environment readiness. They do not build graph state.

#### llm-config
Inspect the active non-embedding LLM configuration.

**Usage:**
```bash
review-cli-<os>-<arch> llm-config
```

**Use when:**
- You need to confirm which provider and model will be used for non-embedding calls.
- You want a read-only bootstrap inspection that does not call the model.

#### doctor
Actively validate the configured non-embedding provider with a minimal model call.

**Usage:**
```bash
review-cli-<os>-<arch> doctor [--timeout N] [--prompt <text>] [--allow-mock]
```

**Flags:**
- `--timeout N` — diagnostic timeout in seconds (default `20`).
- `--prompt <text>` — minimal prompt used for the active validation call (default `"Reply briefly with OK."`).
- `--allow-mock` — allow the deterministic mock provider for diagnostics. Output remains labeled as mock-heavy / not UAT proof; omit this flag for real provider readiness checks.

**Use when:**
- You need a real PASS / FAIL provider smoke.
- You want to validate runtime reachability, not just inspect config.

#### models
Inspect the live foundation-model catalog. Subcommand: `list`.

**Usage:**
```bash
review-cli-<os>-<arch> models list [--json] [--refresh]
```

Lists available foundation models live from the provider's catalog (Bedrock `ListFoundationModels`) instead of a hardcoded list. If the live catalog cannot be reached (no AWS credentials, offline, or network-blocked), it **degrades honestly** to the config-driven model IDs with a clear warning — it never fabricates a catalog. The CLI fetches live on each invocation (does not cache).

**Flags:**
- `--json` — emit machine-readable JSON.
- `--refresh` — force a fresh live fetch (default for the CLI, which does not cache across invocations).

#### rerank-config
Inspect the active rerank configuration.

**Usage:**
```bash
review-cli-<os>-<arch> rerank-config
```

**Use when:**
- You need to inspect model-backed rerank wiring without making a model call.
- You want a read-only summary of rerank provider settings.

#### rerank-doctor
Active diagnostic for rerank readiness.

**Usage:**
```bash
review-cli-<os>-<arch> rerank-doctor
```

**Use when:**
- You want to verify that rerank is disabled, unsupported, or live-reachable.
- You need a no-mock rerank provider probe before claiming model-backed rerank readiness.

**Current support:**
- `CODE_REVIEW_RERANK_PROVIDER=bedrock` executes a small Bedrock Agent Runtime `Rerank` probe when a Bedrock rerank model ARN is configured.
- `CODE_REVIEW_RERANK_PROVIDER=openai|vllm|ollama|lm-studio` executes a small OpenAI-compatible `/rerank` probe against the configured or default local host.
- `CODE_REVIEW_RERANK_PROVIDER=local-cpu` executes a bounded local CPU probe and enforces the small-candidate guard.
- Vertex and custom gateway rerank providers remain unsupported and fail closed.

**Output:**
- Machine-readable `rerank-readiness-result`
- `execution_supported: false` until a future provider implementation and verification path exist
- `recommended_fallback: rule-based graph rerank`

#### check-lsp
Check whether key language servers are available on the machine.

**Usage:**
```bash
review-cli-<os>-<arch> check-lsp
```

**Use when:**
- You plan to run language-aware analysis and want a quick environment sanity check.
- You need to know whether a local LSP-backed flow will likely work.

---

### developer-routing
Generate a generic producer-side routing handoff artifact from an explicit target.

**Usage:**
```bash
review-cli-<os>-<arch> developer-routing <artifact-path> [symbol-identity] [--layers N] [--graph-init auto|always|skip] [--context-output <path>] [--handoff-output <path>]
```

**Output:**
- Machine-readable producer-side handoff artifact
- Fresh bounded evidence generated from the explicit target
- Optional project-boundary graph init / refresh behavior
- Context markdown path and bounded evidence provenance for downstream consumers
- Symbol identity is optional; when omitted, the command produces artifact-level bounded evidence without symbol-specific impact data

**Example:**
```bash
review-cli-<os>-<arch> developer-routing ./internal/parser/testdata/xpp/sample_form.xpo \
  SampleForm.init \
  --layers 1 \
  --graph-init auto \
  --context-output ./.code-review/developer-routing-context.md \
  --handoff-output ./.code-review/developer-routing-handoff.json
```

**Notes:**
- This is the generic producer-side command.
- It stays intentionally out of downstream workspace-local packaging/orchestration.
- It can reuse the current XPO-specialized bounded-context realization as one specialization, but its own handoff artifact remains generic.
- For project-local graph/query work, use `PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true`.

---

### bounded-context
Generate bounded real-corpus development context for a selected XPO target.

**Usage:**
```bash
review-cli-<os>-<arch> bounded-context <xpo-file> <object-qualified-method> [--layers N] [--context-output <path>]
```

**Output:**
- Project-boundary-rooted bounded context payload
- Direct file summary for the selected XPO
- Impact output bounded to `N` layers (default `1`)
- Viewer-compatible report JSON
- Optional markdown context artifact when `--context-output` is provided

**Example:**
```bash
review-cli-<os>-<arch> bounded-context /path/to/repo/gts/lab/packages/classes/cust/CustVoucherJournal.xpo \
  CustVoucherJournal.initCustVendTrans \
  --layers 1 \
  --context-output .agents/specs/xpp-corpus-bounded-context-evidence/reports/xpp-corpus-bounded-context.md
```

**Boundedness Rule:**
- Project boundary + `N` layers
- Default `N=1`
- Not an unlimited graph export

**Specialization Note:**
- `bounded-context` is the current XPO-specialized realization of the generic producer-side routing/query contract.
- For project-local graph/query work, use `PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true`.

---

### graph query surfaces

Use these commands when graph state already exists and you need targeted traversal, inventory, or summary output.

#### impact
Analyze the impact of changing a function or file.

**Usage:**
```bash
review-cli-<os>-<arch> impact <file> <function> [--depth N] [--format text|json]
```

**Argument resolution (tolerant):**
- `<file>` may be a **relative path** — it is normalized to the indexer's absolute key, so `impact gts/Classes/X.xpo …` resolves the same as the absolute form (run it from the indexed project root).
- `<function>` may be the **bare method name** (e.g. `couponId`) when unambiguous in that file, the fully-qualified name (`Class.couponId`), or the function name. On a miss the error lists the file's **candidate function names**; an ambiguous bare name fails closed and names the matches.

**Granularity (`impact_granularity`):**
- **Go etc.** → `call-level`: `direct_callers` / `indirect_callers` / `direct_callees` from the `CALLS` family (unchanged).
- **X++ (`.xpo`)** → `object-level` plus bounded method-level CALLS when the indexed graph has enough X++ relation data. The result may populate `direct_callers` / `direct_callees` for deterministic `this.method()`, `Class::method()`, local/parameter/field receiver, and simple alias calls. Treat the output as conservative: unsupported flow-sensitive receiver forms are skipped, and the CLI's `risk_reason` explains the boundary. Older or partial graphs can still return only object-level references.

**Use when:**
- You need a bounded dependency-impact view around a specific function (Go: call-level; X++: object-level references plus bounded method-level callers/callees when available).

#### dependency-path
Find a dependency path between two **indexed files** in the graph.

**Usage:**
```bash
review-cli-<os>-<arch> dependency-path <source-file> <target-file> [--depth N]
```

Both arguments are **file paths** within the indexed project (the graph store is resolved from the source file's location). They are normalized and resolved to their File nodes, then searched. Output is a JSON object with `found`, the `path`, and — when no path exists — an explained `reason` (or `unresolved` endpoints), instead of a bare `null`.

**Use when:**
- You need an explicit graph path between two files.
- You are debugging why two files are connected or not connected (the `reason` discloses why a file→file path may not exist — edges are often stored at finer artifact/symbol granularity).

#### capability-inventory
List all business capabilities.

**Usage:**
```bash
review-cli-<os>-<arch> capability-inventory [--format json|markdown]
```

**Use when:**
- You need a capability-level inventory from the graph.
- You want a high-level business capability list for review or planning.

#### summary
Generate a structured summary of a codebase.

**Usage:**
```bash
review-cli-<os>-<arch> summary <path> [--granularity project|package|file] [--format json|markdown] [--top-modules N] [--output <path>]
```

**Use when:**
- You need a structured overview of a path at project, package, or file granularity.
- You want a faster overview than a full `report`, but richer than a single-file `analyze`.
- Use `--top-modules` to keep project summaries bounded and `--output` to write the rendered summary
  to a file for handoff or review evidence.

---

### search-code
Search graphRAG code entities for relevance evaluation.

**Usage:**
```bash
review-cli-<os>-<arch> search-code <artifact-path> <query> [--graph-init auto|always|skip] [--limit N] [--threshold FLOAT] [--entity-type <type>]
```

**Output:**
- Machine-readable ranked search results
- Relevance-oriented scores from the current hybrid/vector search implementation
- Local vector SQLite path when local project state is used
- Graph init action used for the query surface
- Conservative ranking notes when topology readiness or class semantics are partial
- Per-result audit fields: `base_similarity`, `final_score`, and `ranking_reasons`

**Example:**
```bash
PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true \
review-cli-<os>-<arch> search-code \
  ./tests/testdata/xpp_corpus_coupon/gts/Classes/CLASSES_CouponCreateBase.xpo \
  "CouponCreateBase nextCouponId" \
  --graph-init auto \
  --limit 5 \
  --threshold 0.1
```

**Notes:**
- This is the base graphRAG relevance inspection surface.
- **Mode A (current)** keeps hybrid/vector first-pass retrieval and adds bounded graph-aware refinement when graph capability is available.
- **Mode B (current, minimal)** adds bounded per-result `recovered_context` previews on top of the same ranked search surface.
- Current output distinguishes `hybrid_only`, `graph_reranked`, `boundary_summarized`, and `capability_unavailable` for the delivered Mode A path. If an executable rerank provider is configured and succeeds, output also includes `model_rerank_stage`, `model_rerank_provider`, `model_rerank_model`, and per-result `model_rerank_score`.
- Current output may also disclose `relation_coverage_status` indirectly through conservative ranking notes when graph topology is only partially materialized.
- When additive role semantics are available, per-result output may also expose `candidate_role` so developer-facing consumers can distinguish authoritative generators from helper/consumer hits.
- Per-result audit fields distinguish first-pass `base_similarity` from final deterministic `final_score`; `similarity` remains the final score for backward compatibility.
- When Mode B is selected, output may additionally expose `execution_mode: mode_b` and bounded `recovered_context` previews per result.
- For large existing graphs, do not infer success from `manifest.json` alone. Validate the live SQLite DB and run the exact query path (`--graph-only --graph-init skip` for read-only no-model revalidation). If `candidate_role` / `ranking_reasons` say the source-of-truth generator is top-ranked, follow with `impact` or `bounded-context` before writing a closure artifact.

---

### search-code-eval
Evaluate `search-code` retrieval quality against fixed JSON cases.

**Usage:**
```bash
review-cli-<os>-<arch> search-code-eval <artifact-path> <cases-json> [--graph-init auto|always|skip] [--limit N] [--threshold FLOAT] [--entity-type <type>] [--mode mode_a|mode_b]
```

**Cases JSON:**
```json
[
  {
    "id": "coupon-numbering-rule",
    "query": "coupon id numbering rule",
    "expected_any": ["CouponCreateBase.nextCouponId"],
    "top_k": 3
  }
]
```

For XPP semantic relation review, use the checked-in `xpp_semantic_cases.json` fixture to inspect `REFERENCES_CLASS` edges and warning codes. Use `xpp_multifamily_cases.json` to inspect a compact XPP class hierarchy fixture covering `INHERITS_FROM` and `OVERRIDES` edge production.

**Output:**
- Machine-readable PASS/FAIL summary with `total_cases`, `passed_cases`, and `failed_cases`
- Per-case `matched_name`, `matched_rank`, `retrieval_stage`, `graph_capability`, and `ranking_notes`
- Per-result audit fields inherited from `search-code`: `base_similarity`, `final_score`, `candidate_role`, and `ranking_reasons`

**Use when:**
- You need a fixed retrieval-quality baseline for comparing changes across releases.
- You want to detect top-k discoverability regressions before enabling richer rerank behavior.

---

### graph-relation-eval
Evaluate graph relation edges against fixed JSON cases.

**Usage:**
```bash
review-cli-<os>-<arch> graph-relation-eval <target-path> <cases-json> [--graph-init auto|always|skip]
```

**Cases JSON:**
```json
[
  {
    "id": "go-direct-call-handle-validates-coupon",
    "relation_type": "CALLS",
    "source_name": "HandleCoupon",
    "target_name": "validateCoupon",
    "source_label": "Function",
    "target_label": "Function"
  }
]
```

**Output:**
- Machine-readable PASS/FAIL summary with `total_cases`, `passed_cases`, and `failed_cases`
- `relation_family_counts` from the materialized graph state
- Per-case matched edge details: source, target, relation type, owner artifact path, language, provenance, and warning code when present
- Checked-in fixture families currently cover Go `CALLS`, Go same-file and same-package cross-file interface-signature `IMPLEMENTS`, TypeScript same-file syntax/signature `IMPLEMENTS`, TypeScript same-directory relative-import interface-signature `IMPLEMENTS`, XPP `REFERENCES_CLASS`, XPP `INHERITS_FROM`, and XPP `OVERRIDES`.

**Use when:**
- You need to compare graph topology across parser/indexer changes.
- You want edge-level evidence for relation families such as `CALLS` or `REFERENCES_CLASS` before trusting downstream graph traversal.
- You need deterministic Go interface implementation evidence before trusting `IMPLEMENTS` topology.
- You need a fail-closed check that distinguishes missing relation evidence from general graph queryability.

---

### eval-compare
Compare two fixed evaluation JSON artifacts.

**Usage:**
```bash
review-cli-<os>-<arch> eval-compare <baseline-json> <current-json>
```

**Supported inputs:**
- `search-code-eval-result`
- `graph-relation-eval-result`

**Output:**
- Machine-readable `eval-comparison-result`
- Aggregate deltas: baseline/current totals, pass/fail deltas, regression/improvement/unchanged/added/removed counts
- Per-case `status`: `regressed`, `improved`, `unchanged`, `added`, or `removed`
- Search eval comparisons include `matched_rank_delta` when both runs matched the case
- Graph relation eval comparisons include `relation_family_deltas`
- Checked-in comparison fixtures include search artifacts and graph relation artifacts so packaged smoke checks can exercise both delta types.

**Example:**
```bash
review-cli-<os>-<arch> eval-compare \
  .code-review/baseline/search-code-eval.json \
  .code-review/current/search-code-eval.json
```

**Use when:**
- You need a release-to-release or branch-to-branch regression gate over graph/search eval output.
- You want reviewable comparison evidence without manually diffing JSON.
- You need non-interactive proof; this command never opens browser or terminal windows.

---

### eval-gate
Gate one fixed evaluation comparison artifact against release thresholds.

**Usage:**
```bash
review-cli-<os>-<arch> eval-gate <eval-comparison-json> [--max-regressions N] [--min-passed-delta N] [--max-failed-delta N] [--max-matched-rank-regression N] [--allow-removed] [--allow-relation-family-drop]
```

**Output:**
- Machine-readable `eval-gate-result`
- `passed`, `policy`, `summary`, `violation_count`, and structured `violations`
- Non-zero CLI exit when the gate fails

**Default policy:**
- `max_regressions: 0`
- `min_passed_delta: 0`
- `max_failed_delta: 0`
- `max_matched_rank_regression: 0`
- removed cases fail unless `--allow-removed` is set
- graph relation-family drops fail unless `--allow-relation-family-drop` is set

**Use when:**
- You need CI/release enforcement over `eval-compare` output.
- You want graph/search quality checks to fail closed instead of relying on manual JSON inspection.
- You need a reviewable artifact that explains exactly which policy was violated.

---

### spec and test traceability

These commands are for spec metadata and requirement-to-test mapping. Use them after graph state exists.

#### scan-specs
Index spec files and higher-level spec metadata into the knowledge graph.

**Usage:**
```bash
review-cli-<os>-<arch> scan-specs [--specs-dir <dir> ...]
```

`--specs-dir` is **repeatable** — pass it multiple times to index several agent spec directories in one run.

**Use when:**
- You want to materialize `Spec`, `Requirement`, `Task`, and related metadata nodes.
- You need graph-backed spec governance rather than a shallow file scan.

#### spec-metadata-summary
Summarize indexed spec, contract, and review metadata.

**Usage:**
```bash
review-cli-<os>-<arch> spec-metadata-summary
```

**Use when:**
- You want a quick overview of indexed spec metadata from the current graph state.

#### test-traceability
Show test coverage traceability for a spec.

**Usage:**
```bash
review-cli-<os>-<arch> test-traceability <spec-path> [--format text|json]
```

**Use when:**
- You want requirement-to-test coverage status for a spec.
- You need to see covered / partial / uncovered requirements before changing tests or spec scope.

#### trace
Trace a requirement to tasks and code implementation.

**Usage:**
```bash
review-cli-<os>-<arch> trace <req-id>
```

**Use when:**
- You want to follow a single requirement through task and code layers.

> The legacy `trace-llm` command (LLM-inferred Function → Requirement edges, backed by the
> retired `spec-tracer` skill) was removed in Spec #96. Requirement / business-value grounding now
> lives in the `capability-mapper` skill (File → Capability → Requirement), which reads the spec
> corpus via `capability-mapper/scripts/run.py --collect-requirements <root>`.

## Decision Table: index vs search-code

| When to use | Command |
|---|---|
| First time indexing a project or refreshing graph state after code changes | `review-cli-<os>-<arch> index <path>` |
| Building graph state in directory batches with progress/result/error reporting | `review-cli-<os>-<arch> index <path> --recursive [--format text\|json]` |
| Inspecting ranked graphRAG retrieval results over already-built local project state | `review-cli-<os>-<arch> search-code <artifact-path> <query>` |

**Notes:**
- In git repositories, run `git status --short` before and after `index` because it may create or update local state. Classify new files before changing tracking rules.
- `index` is the primary graph-building workflow; `search-code` is the retrieval/query workflow.
- `search-code --graph-init auto` is a convenience path for query-time bootstrap, not the recommended way to build graph state for a project.
- `index --diff-base <sha>` and `index --force` are the incremental and fail-open/force-refresh knobs. Use them when you need a changed-file rebuild or want to discard triage cache state.
- `search-code` requires `PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true` for graph-aware refinement. Unsupported modes fail closed with explicit capability disclosure rather than silently falling back.
- `review index <path> --status` is the primary readiness surface. It now distinguishes plain `graph_queryable` from `relation_coverage_status`, so a graph can be traversable while topology coverage remains only partial.
- `review init <path> --graph --format json` and `review graph init <path>` emit the same read-only vector readiness object under `vector`. Treat graph readiness, vector readiness, and subscription-agent annotation writeback as separate claims.
- When vector readiness includes `manifested`, that count comes from per-run `embedding_run_items` rows. It proves the run has inspectable item outcomes; it does not by itself prove automated resume/rollback or a refreshed live target-project dogfood run.
- When vector readiness includes `rollback_deleted`, that count means the latest local SQLite run cleaned stale generated vectors from a prior non-ready run before starting. It is cleanup evidence, not proof of selective failed/deferred-only retry scheduling or live target-project dogfood completion.
- A normal follow-up `index <path>` uses the latest non-ready local SQLite embedding manifest to reprocess files with generated/error/deferred vector items even when file content hashes are unchanged. This is repo-side retry scheduling evidence; live target-project dogfood still needs an actual target run.
- When `index` creates `.code-review/graph.sqlite`, do not automatically commit it. If the repository intentionally promotes that DB into reusable GraphRAG state for later agent queries, track the exact graph DB with Git LFS. Track a graph `manifest.json` as text only when it documents that durable snapshot; runtime `status.json`, session, cache, vector, and local registry outputs remain ignored by default. See `local-state-version-control.md`.

### Triage Summary

- Use `search-code` when you need ranked retrieval or candidate ranking for a query.
- Use `search-code` Mode B only when the ranked result set also needs bounded `recovered_context` previews.
- Use `bounded-context` when the next step is a symbol-specific or object-method-specific context bundle for downstream handoff.
- Use `developer-routing` when the handoff is producer-side and should remain generic.
- Use `viewer` when you need to inspect a report or graph visually; it is not a replacement for query-time triage.
- Use `runtime request` when the missing target is governed runtime readiness, not code retrieval.

---

### runtime status
Show governed local runtime status for a target path.

**Usage:**
```bash
review-cli-<os>-<arch> runtime status <target-path> --stage evidence
```

**Notes:**
- Raw producer-side input only
- Not a readiness authority by itself

---

### runtime request
Request or reuse a governed local runtime bundle for a target path.

**Usage:**
```bash
review-cli-<os>-<arch> runtime request <target-path> --stage evidence
```

**Notes:**
- Use this as the governance-safe authority path when the required bundle is missing and must be brought to `ready`
- `runtime status` remains read-only
- `runtime bootstrap-register` remains for already-ready current-state registration

---

### runtime bootstrap-register
Bootstrap-register current local runtime state into the machine-local registry.

**Usage:**
```bash
review-cli-<os>-<arch> runtime bootstrap-register <target-path> --stage evidence
```

---

### runtime release
Release a previously requested/registered governed runtime bundle for a target path, freeing its registry allocation.

**Usage:**
```bash
review-cli-<os>-<arch> runtime release <target-path> --stage evidence
```

`--stage` defaults to `evidence`. Use after evidence capture to return the bundle so the next allocation can reuse the slot.

---

### mcp serve
Expose the code-review tool surface through Model Context Protocol transports.

**Usage:**
```bash
# Local IDE/agent subprocess transport. stdout is MCP JSON-RPC only.
review-cli-<os>-<arch> mcp serve --transport stdio --graph auto --target <project-path>

# Streamable HTTP at /mcp plus legacy HTTP+SSE at /sse + /message.
review-cli-<os>-<arch> mcp serve \
  --transport http \
  --addr 127.0.0.1:3000 \
  --path /mcp \
  --sse-path /sse \
  --message-path /message \
  --auth-mode api-key \
  --api-key "$CODE_REVIEW_MCP_API_KEY" \
  --target <project-path>
```

**Notes:**
- MCP is a runtime surface of the same `review-cli` binary, not a new review engine.
- Use stdio when the MCP client and target checkout are on the same host/user session.
- Use HTTP/SSE with a mounted/local checkout for normal target review, or use MCP `remote_review` for bounded remote Git `repo_url/ref` materialization.
- `--auth-mode none` is for trusted loopback/local use. Non-loopback HTTP/SSE without auth fails closed unless `--allow-unauthenticated-remote` is explicit.
- Container/Docker deployment is optional for HTTP/SSE runtime instances; it does not change the product contract.
- MCP `remote_review` supports bounded remote Git `repo_url/ref` materialization with `sandbox_level=filesystem|process|service`: `filesystem` is the repo-side default, `process` requires explicit `CODE_REVIEW_REMOTE_REVIEW_PROCESS_SANDBOX=bwrap` configuration and has current-host bwrap smoke proof, and `service` delegates to a sandbox service endpoint. Filesystem-level materialization can also reuse `scan_specs`, `analyze_code`, `generate_report`, and `search_code` through `remote_review.tool` plus optional `tool_args`. Private GitHub/GitLab provider proof and live L3 sandbox-station runtime proof remain external claim boundaries.

---

### serve
Serve the bundled report viewer locally.

**Usage:**
```bash
review-cli-<os>-<arch> serve [--port N] [--open]
```

**Output:**
- JSON status containing a localhost URL
- Optional browser open behavior when `--open` is set

**Example:**
```bash
review-cli-<os>-<arch> serve --port 8080
review-cli-<os>-<arch> serve --open
```

**Notes:**
- Raw producer-side input only
- Consume declared conclusions from `review.md`, not this command output alone
- Test, CI, and non-interactive smoke flows should omit `--open` or set `CODE_REVIEW_DISABLE_BROWSER_OPEN=true`; browser/terminal launch is no longer required as proof.

---

### viewer
Serve the bundled Report Viewer or Graph Explorer locally.

**Usage:**
```bash
review-cli-<os>-<arch> viewer [--port N] [--open] [--mode report|graph] [--workspace <path>] [--graph-db <path>]
```

**Output:**
- JSON status containing a localhost URL
- `mode` indicating `report` or `graph`
- Optional `workspace_root` and `graph_db` fields when graph mode resolves a concrete workspace-local DB path

**Examples:**
```bash
review-cli-<os>-<arch> viewer --open
review-cli-<os>-<arch> viewer --mode graph --open
review-cli-<os>-<arch> viewer --mode graph --workspace ./src --graph-db ./.code-review/graph.sqlite
```

**Notes:**
- `viewer` is the authoritative Agent-facing control surface for bundled visualization.
- `--graph-db` takes precedence over env/config path and localstate inference.
- `--graph-db` must stay within the workspace boundary and point to a `.sqlite` / `.db` file or the command fails closed.
- Test, CI, and non-interactive smoke flows should omit `--open` or set `CODE_REVIEW_DISABLE_BROWSER_OPEN=true`; use the JSON `url` output as evidence instead of proving that a browser/terminal can launch.
- Browser-side `?db=` / file-picker loading remains a manual Graph Explorer convenience path, not the authoritative Agent-facing contract.
- A `--graph-db` path proves which DB Graph Explorer is loading; it does not by itself mean the DB should be committed. Commit it only when the repo intentionally shares that DB as reusable GraphRAG state. In that case, use Git LFS for `graph.sqlite` / graph `.db`, keep a durable `manifest.json` as normal text when needed, and keep sibling runtime `status.json` / cache files ignored.

---

## security

DevSecOps capability (spec `local-devsecops-hardening`): audit a target project's DevSecOps posture, run deep multi-language scans, and gate agent output. All subcommands accept `--target <dir>` (default: cwd), `--json`, and `--timeout <seconds>` (bound the whole run so a hung external tool can't block a Stop-hook; 0 = no timeout). `security scan` also accepts `--target <file>` for narrow hook/review scopes; local scanners run from the file's parent directory and scan the basename.

### security audit

Inventory a target project's DevSecOps controls (SAST, secret-scan, dependency-vuln, SBOM, signing, OWASP-LLM agent-safety) and report gaps with a maturity %.

- `--strict` — exit non-zero if any high-severity control is absent (else report-only).

### security scan

Invoke multi-language SAST + secret + dependency-vuln + SBOM against the target (JS/C#/Py/Go). Detects `govulncheck`/`gitleaks`/`trivy`/`semgrep`; honest `tool-unavailable` degradation.

- `--severity <levels>` — trivy severity gate (default `HIGH,CRITICAL`).
- `--delegate` — delegate the scan round-trip to the aclab-middlewares security-stack (per its DELEGATION_CONTRACT.md): resolve the Dependency-Track / DefectDojo hubs from the local-infra registry, run `sectool` scans → import findings to DefectDojo, and generate an SBOM → ingest to Dependency-Track. Honest `local-fallback` when `sectool` is absent or the hubs are not `active`; hub steps skip with a note when no credentials.
- `--sectool <cmd>` — the sectool binary/command used for `--delegate` (default `sectool`).
- `--dt-base-url <url>` — Dependency-Track base for `--delegate` (default: resolved from the local-infra registry).
- `--dd-base-url <url>` — DefectDojo base for `--delegate` (default: resolved from the local-infra registry).
- `--delegate-project <name>` — shared identity for the DT project + DefectDojo product (default: target dir name).
- `--delegate-engagement <name>` — DefectDojo engagement name (default: `delegated-scan`).
- `--trust-target-policy` — apply a target-local `.gitleaks.toml`/`.trivyignore` even when the target is not the invoking workspace (default: trust only the current workspace, so a foreign/hostile target can't suppress its own findings).

Credentials for `--delegate` are read from the environment (operator-provided, never committed): `CODE_REVIEW_DT_API_KEY` (Dependency-Track), `CODE_REVIEW_DD_API_TOKEN` (DefectDojo). Endpoint overrides also via `CODE_REVIEW_DT_BASE_URL` / `CODE_REVIEW_DD_BASE_URL`; registry path via `CODE_REVIEW_LOCAL_INFRA_REGISTRY`.

### security grounding

OWASP-LLM content-safety + hallucination gate for agent/subAgent output: fabricated file refs (LLM09), secret leakage (LLM06), prompt-injection phrasing (LLM01). Reads a Claude/Codex/Kiro Stop payload (`transcript_path`) from stdin; exits non-zero on a HIGH finding so a Stop-hook can gate unless `--warn-only` is set.

- `--transcript <file>` — transcript/output file to scan (default: stdin).
- `--warn-only` — always exit 0 (report only, do not gate).
- `--hook-mode` — Stop-hook mode: write reports/diagnostics to stderr and keep stdout reserved for hook protocol output. Emitted Claude/Codex/Kiro hooks include this by default.
- `--stderr` — write the report to stderr and keep stdout empty. Required when run as a Stop-hook unless `--hook-mode` is used.
- `--gate-injection` — treat prompt-injection (LLM01) as a HIGH gating finding instead of a warning (for autonomous loops where injected instructions are higher-risk).
- `--emit-hook <agent>` — print a ready-to-install Stop-hook config for `claude|codex|kiro|opencode` and exit (Claude/Codex JSON Stop, Kiro `hooks.stop`, opencode `session.idle` JS plugin). Stop-hook configs default to `--hook-mode --warn-only --stderr --timeout 60`; OpenCode's advisory `session.idle` scan trigger also uses `--timeout 60`.
- `--hook-binary <path>` — binary path to embed in emitted Claude/Codex/Kiro Stop-hook commands. Defaults to `REVIEW_CLI_BIN`, then `review-cli`.
- `--hook-skill-dir <path>` — code-review skill directory containing `scripts/` for emitted hook command resolution. Defaults to `REVIEW_CLI_SKILL_DIR` when set; opencode plugin templates otherwise resolve the flat OpenCode home `~/.config/opencode/skills/code-review`.

When a blocking grounding hook exits nonzero, hook mode writes a bounded diagnostic to stderr with a classification such as `hook-gated-high-finding` or `hook-missing-transcript`, the advisory/gating mode, high finding count when known, source path, and remediation. `--warn-only` still reports findings but never exits nonzero for findings.

### security hook-audit

Inspect installed agent Stop hooks without executing them. Use this when the host only reports an opaque failure such as `hook exited with code 1`.

**Usage:**
```bash
review-cli-<os>-<arch> security hook-audit
review-cli-<os>-<arch> security hook-audit --agent codex --config ~/.codex/hooks.json
review-cli-<os>-<arch> security hook-audit --json
```

The audit classifies recognized commands:

- `xreview run --host-agent ...` — expected advisory/non-blocking.
- `review-cli security grounding --hook-mode --warn-only --stderr --timeout 60` — expected advisory Stop hook.
- `review-cli security grounding --hook-mode --warn-only` without `--timeout` — `hook-timeout-missing`; reinstall/emit the hook so a hung grounding pass cannot block the host agent.
- `review-cli security grounding` without `--warn-only` — `hook-installed-command-drift` / "expected warn-only, found gating"; valid only when the operator intentionally wants HIGH findings to block Stop.
- unknown Stop hook command — includes command/config/owner hints so the operator can route the failure.

OpenCode is reported separately as a `session.idle` plugin surface; it is advisory by default and is not the same wire contract as Claude/Codex/Kiro Stop-hook JSON.

### security hook-diagnose

Classify captured Stop-hook stdout/stderr/exit-code evidence without executing the hook. Use this when a host reports `invalid stop hook JSON output`, `hook exited with code 1`, or another opaque Stop-hook protocol failure.

**Usage:**
```bash
review-cli-<os>-<arch> security hook-diagnose \
  --agent codex \
  --config ~/.codex/hooks.json \
  --command 'review-cli security grounding --hook-mode --warn-only --stderr --timeout 60' \
  --stdout-file /tmp/hook.stdout \
  --stderr-file /tmp/hook.stderr \
  --exit-code 0 \
  --require-json

review-cli-<os>-<arch> security --json hook-diagnose --agent claude --stdout '{"message":"hello"}' --require-json
```

Classifications:

- `stdout-not-json` — stdout is neither empty nor JSON.
- `stdout-json-schema-mismatch` — stdout is valid JSON but lacks recognized Stop-hook protocol fields.
- `stdout-mixed-protocol-and-logs` — stdout contains log text before/after protocol JSON, or more than one JSON value.
- `stdout-empty-when-json-required` — stdout is empty but this hook invocation requires protocol JSON.
- `hook-exit-nonzero` — the hook process exited nonzero; stderr/stdout previews are bounded and redacted.

Good Stop-hook stdout/stderr contract:

```text
stdout: {"decision":"block","reason":"Security grounding found HIGH findings"}
stderr: RESULT: FLAG
```

Good advisory/no-op contract when the host permits no output:

```text
stdout:
stderr: RESULT: PASS
```

Bad contract:

```text
stdout: [ContinuousLearning] saved note
stdout: {"decision":"block","reason":"..."}
stderr:
```

Fix: move all logs, progress, warnings, and diagnostics to stderr or durable records; reserve stdout for either nothing or exactly one Stop-hook protocol JSON object.

---

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - File not found
- `4` - Database connection error

---

## Environment Variables

Required for database operations:

```bash
CODE_REVIEW_PERSISTENCE_MODE
CODE_REVIEW_SQLITE_ENABLED
CODE_REVIEW_SQLITE_PROJECT_STATE_DIR
CODE_REVIEW_EMBEDDING_PROVIDER
```

---

## Supported Languages

18 languages via LSP integration:
- Go (gopls)
- Python (pyright)
- TypeScript/JavaScript (typescript-language-server)
- Rust (rust-analyzer)
- Java (jdtls)
- C/C++ (clangd)
- SQL (sql-language-server)
- Vue (vue-language-server)
- GraphQL (graphql-lsp)
- Prisma (prisma-language-server)
- ABAP (abaplint-language-server)
- And 7 more...

See `LSP_QUICK_REFERENCE.md` for complete list.

---

## Canonical Workspace Authority

This `code-review` skill is the canonical workspace bundle authority in this repository.

- Use `.agents/skills/code-review/` as the live workspace skill path.
- Use the global `~/.config/opencode/skills/code-review/` only as a downstream installed copy of this canonical workspace bundle.
