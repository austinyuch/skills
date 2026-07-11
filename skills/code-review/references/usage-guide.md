# Code Review Usage Guide

This reference collects the workflow, evidence, and safety guidance that used to live in `SKILL.md`.

## Viewer And Evidence

- **Report Viewer**: fixture/static viewer evidence. Useful for proving bundled UI behavior, not runtime readiness.
- **Graph Explorer**: zero-backend viewer evidence. Useful for browser-side SQLite visualization, not runtime readiness.
- **Runtime readiness**: keep using runtime-backed review artifacts and spec-local review state as the authority.

Tracked evidence locations:

- `temp/report-viewer-e2e/report-viewer-evidence-summary.json`
- `docs/review/frontend-e2e-lane-matrix.json`

Use `review-cli-<os>-<arch> viewer` as the unified local HTTP surface for either report or graph mode.

## Runtime Preflight

Use these commands when a governed local runtime bundle is involved:

```bash
review-cli-<os>-<arch> runtime status <target-path> --stage evidence
review-cli-<os>-<arch> runtime request <target-path> --stage evidence
review-cli-<os>-<arch> runtime bootstrap-register <target-path> --stage evidence
```

- `runtime request` is the governance-safe path when the bundle is missing and must be brought to `ready`.
- `runtime bootstrap-register` is for already-ready current-state registration.
- These commands are raw producer-side inputs only.

## Command Triage

Use [cli-commands.md](cli-commands.md) for the canonical command-selection matrix. It covers:

- `index` vs `search-code`
- `index --no-embeddings` and `search-code --graph-only` vs hybrid graphRAG
- `graph fragment validate/apply` for subscription-agent semantic topology
- `search-code` Mode A vs Mode B
- when to switch to `bounded-context`
- when to switch to `developer-routing`
- when to use `viewer`
- when to use `runtime request`
- graph query surfaces like `impact`, `dependency-path`, `capability-inventory`, and `summary`
- diagnostics and traceability surfaces like `llm-config`, `doctor`, `rerank-config`, `rerank-doctor`, `scan-specs`, `spec-metadata-summary`, and `test-traceability`

## Environment And Mode Authority

Use [configuration.md](configuration.md) for runtime variables and provider/mode details.

The important working assumptions are:

- `local-sqlite` is the project-local graph/query path for this skill
- `server-postgresql` is a separate mode boundary and should fail closed for project-local query surfaces
- the published `scripts/` surface is native-binary-only
- `review.py` and similar Python runtime entrypoints are not part of the shipped contract

## Index Corpus Ignores

`index` and `watch` decide which files enter the corpus by merging five sources, all additive, in this order:

1. **Builtin excluded directories** — always active, parsed before anything else, and **cannot be re-included** by any `!` negation (REQ-ICB-001).
2. **`.gitignore`** at the target project root (the path passed to the command).
3. **`.reviewignore`** at the target project root — legacy import surface for older projects.
4. **`.code-review/config.yaml`** at the target project root — preferred review configuration SSOT.
5. **`--exclude <dir>`** flags on the command line (repeatable; REQ-ICB-003).

`.codereviewignore` is **not** recognized. Preview the resolved plan with `index --dry-run-corpus --format json`, which reports included/excluded samples annotated with `source` and matched `rule`, then exits before indexing — use it to confirm why a path was skipped.

### `.code-review/config.yaml`

Keep this file declarative. It may contain review settings and ignore rules; it must not contain copied project files, symlinked project files, generated inventories, matched file dumps, or expanded path lists. Runtime reports belong under `.code-review/reports/` or another evidence path, not inside the config file.

Minimal corpus config:

```yaml
version: 1
corpus:
  ignore:
    rules:
      - docs/showcase/generated-assets
      - tmp-review-fixtures
```

Use directory-level re-includes for SSOT child directories. A file-level `!` cannot rescue files below a pruned parent directory.

### Generated code and Ent

Treat generated code as a graph-topology decision, not a blanket ignore decision. Generated source that carries runtime contract or dependency shape should usually remain in the primary graph even when it is mechanically produced.

For Ent codegen:

- Keep `ent/schema/*.go` because it is the source of truth for entities, fields, edges, hooks, and annotations.
- Keep generated `ent/**/*.go` in the primary graph when reviewing impact, dependency paths, repository/service routing, query/mutation behavior, predicates, hooks, transactions, or client wiring. Excluding it can hide real runtime paths.
- Exclude generated Ent only for an explicitly named low-noise or human-authored-design profile, and record the limitation: runtime impact through Ent is incomplete in that graph.
- Do not use a broad `ent/*` example as a default corpus rule. If a target repo wants schema-only graphing, prefer a scoped local profile such as:

```yaml
version: 1
corpus:
  ignore:
    rules:
      - backend/ent
      - "!backend/ent/schema"
```

That profile is intentionally incomplete for runtime impact. The current config language can only include or exclude paths; it cannot mark generated nodes as lower-rank. When generated code adds ranking noise, prefer scoped `impact`, `dependency-path`, `bounded-context`, or separate graph profiles over silently dropping runtime topology from the default graph.

### Builtin excluded directories (non-negatable)

These 30 directory names are skipped wherever they appear in the tree and **cannot** be brought back with `!`. This is intentional for runtime/state dirs, but note that several **build-output names are also builtin** — if your real source lives in a directory named `bin`, `build`, `dist`, `out`, `target`, `obj`, or `coverage`, it will be skipped and a `.reviewignore` negation will not rescue it. Use `--exclude`-free layouts or rename, and verify with `--dry-run-corpus`.

| Group | Names |
|-------|-------|
| Universal | `.git` `node_modules` `vendor` `.venv` `venv` `__pycache__` `.cache` `.tmp` `tmp` `dist` `build` `bin` `.kiro` `.agents` |
| Python | `.mypy_cache` `.pytest_cache` `.ruff_cache` `.tox` `site-packages` |
| Node/JS | `.next` `.nuxt` `.output` `.turbo` `coverage` |
| C#/.NET | `obj` `.vs` `TestResults` |
| Rust | `target` |
| Java/Kotlin | `.gradle` `.idea` `out` |
| Tool/runtime state (REQ-ICB-001) | `.docker-data` `.code-review` |

### Pattern syntax for `.gitignore` / `.reviewignore`

The matcher is gitignore-**like** but deliberately limited (custom implementation over Go `filepath.Match`, not full gitignore). The same pattern policy applies to `.gitignore`, `.reviewignore`, and `.code-review/config.yaml` `corpus.ignore.rules`:

- **Supported:** plain directory names; a trailing `/` (stripped, so `generated/` ≡ `generated`); `*` and `?` file globs (e.g. `*.pb.go`); `#` comments; blank lines; `!pattern` negation.
- **Not supported:** `**` double-star, leading-`/` path anchors, and **nested ignore files** — only the root-level `.gitignore` / `.reviewignore` are parsed; ignore files in subdirectories are not.
- **Case sensitivity:** glob matching is case-sensitive on Linux/macOS and case-insensitive on Windows (Go `filepath.Match` semantics).

### Precedence and a directory-level gotcha

Rules merge into one ordered list (`.gitignore`, then `.reviewignore`, then `.code-review/config.yaml`) and evaluate **last-matching-rule-wins**. So a `.code-review/config.yaml` `!keep.pb.go` can re-include a *file* excluded by a `.reviewignore` glob. **But** a directory-level exclude prunes traversal entirely: if a directory is excluded, a file-level `!` negation inside it does **not** bring its files back. Negate at the directory level, or don't exclude the parent.

### `--exclude`

Repeatable. Each value matches either a directory **base name** (e.g. `--exclude node_modules`) or a **full relative path** (e.g. `--exclude legacy/shared`). It is exact-match and case-sensitive on all platforms — no globs. Use `--no-respect-gitignore` to ignore both `.gitignore` and legacy `.reviewignore`; builtin excludes, canonical `.code-review/config.yaml`, and `--exclude` remain active (REQ-ICB-002).

There is no binary-file detection, file-size cap, or special hidden-file handling in the corpus filter — selection is purely directory/filename-pattern based. Untracked/uncommitted files surfaced during incremental indexing are still run through these same exclusion rules.

For large repositories, use recursive checkpointed indexing with bounded batches:

```bash
PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true \
CODE_REVIEW_INDEX_MEMORY_MB=1536 \
.agents/skills/code-review/scripts/review-cli-<os>-<arch> index <project-root> \
  --recursive --resume --no-embeddings \
  --batch-max-files 50 \
  --batch-max-bytes 64MB \
  --batch-sort mtime
```

`--recursive` writes `<project-root>/.gcr/index-recursive-checkpoint.json`. Use `--resume` after an interruption and `--restart` for a clean job. A recursive run produces the **same relation graph as a non-recursive full index** — per-batch `CALLS`/`DEPENDS_ON`/`DEFINES`/`CONTAINS` plus a bounded corpus-wide final language-graph pass for producer-backed semantic families (e.g. XPP `INHERITS_FROM`/`REFERENCES_CLASS`/`OVERRIDES`) and `BELONGS_TO_REPO` membership — at bounded memory. The project SQLite graph DB is single-writer, now enforced by a single writer connection plus a 30s `busy_timeout`: a recursive run serializes its own write phases (no `SQLITE_BUSY`), and a second concurrent graph-mutating process against the same DB serializes/waits rather than failing. On a full fresh index `--recursive` is typically *faster* than non-recursive (it skips the per-file owned-edge re-cleanup the non-recursive path performs) and uses less memory. `--batch-sort mtime` prioritizes recently updated files; git changed/untracked files are prioritized first when the target is a git checkout. `--prune-ignored` removes existing File/symbol/vector traces that are no longer present in the current discovered corpus, using targeted file cleanup instead of a full orphan scan.

Recursive `--batch-*` flags control file discovery/commit batching. Embedding provider throughput is controlled separately by `--embedding-batch-size`, `--embedding-workers`, `--embedding-rate-limit`, and `--embedding-timeout`, or by the matching `CODE_REVIEW_EMBEDDING_*` environment/config values.

Use `--no-embeddings` to skip embedding/vector provider initialization. Use `--no-model` when a run must avoid both embeddings and LLM API annotation writes. In `--no-model`, `--capabilities` and `--summaries` remain valid: the CLI reports an agent-instruction handoff for a subscription coding agent instead of calling provider APIs. That handoff is not self-executing unless you run `review-cli handoff run-agent <handoff-dir> --agent auto --apply` or a repo-owned equivalent: a separate agent workflow must process the queue and `apply-handoff` must validate/write before capability or summary annotations are present in the graph. `CODE_REVIEW_EMBEDDING_PROVIDER=mock` still writes deterministic mock embedding rows and is for tests, not graph-only indexing.

### Provider-bound evidence lanes

If a task names a concrete provider/model/endpoint, such as BGE-M3, ONNX GPU, CUDAExecutionProvider, a self-hosted `/v1/embeddings` endpoint, Bedrock Titan, Vertex, or OpenAI embeddings, record the provider contract before running write-producing or evidence-producing commands:

| Field | Required value |
|---|---|
| Allowed provider | Provider family or protocol for this lane. |
| Endpoint/base URL | Exact endpoint, or "not applicable" for local/bundled providers. |
| Model | Exact model ID. |
| Dimensions | Expected vector width, or "not used" for graph-only commands. |
| Execution provider | CPU/CUDA/other runtime where relevant. |
| Forbidden fallback | `CODE_REVIEW_EMBEDDING_PROVIDER=mock` unless the user explicitly authorized a diagnostic graph-only exception. |

Use `--no-embeddings` when the intended claim is graph-only. Do not switch to mock to avoid a provider setup problem in a provider-bound lane. `handoff run-agent` and `apply-handoff` consume agent-result files and write validated annotations; they do not generate embedding vectors, so their evidence supports annotation writeback only.

## Release And Publication

The canonical release workflow is:

```bash
cd ../../../go-review-service
make release-code-review-skill
```

Use `make install-skill` after the workspace bundle is verified.

The release bundle excludes local/runtime state such as:

- `scripts/.env`
- `scripts/__pycache__/`
- `scripts/viewer/reports/`
- `scripts/viewer/reports.index.json`

## Producer Routing Handoff

Use this when you need a generic downstream handoff artifact:

```bash
PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true \
.agents/skills/code-review/scripts/review-cli-<os>-<arch> developer-routing \
  <artifact-path> [symbol-identity] --layers 1 \
  --context-output ./.code-review/developer-routing-context.md \
  --handoff-output ./.code-review/developer-routing-handoff.json
```

This is producer-side only and deliberately stops before downstream workspace orchestration.

## Graph-Assisted Planning

Use graph-assisted planning by default for architecture discovery, project design, impact analysis, broad code retrieval, spec handoff, and non-trivial implementation planning. For those tasks, graph init/preflight is mandatory unless the task is clearly narrow, the relevant files are already known, or graph state is unavailable and rebuilding would cost more than the task warrants. When a spec, design, review, or handoff artifact is produced, record either the graph query and trigger/preflight result or the reason graph use was skipped.

1. Read the target repo's local instructions first. Some repos deliberately promote a shared `.code-review/graph.sqlite`, `.code-review/vector.sqlite`, and `.code-review/manifest.json` snapshot and wrap CLI operations with repo-owned commands.
2. Run graph init/preflight before design or code changes. If a repo-owned shared snapshot exists, inspect the manifest and run the repo's status/doctor command before rebuilding it. Example shape: `python scripts/ops.py graphrag status-shared` or `python scripts/ops.py graphrag doctor-shared --embedding-provider mock`.
3. If no repo wrapper exists, run `review-cli-<os>-<arch> init <project-path> --graph --trigger watch-once`. The command emits `graph_queryable`, `relation_coverage_status`, `snapshot_artifacts`, `vector`, `recommended_query_mode`, `trigger_strategy`, and `skip_rationale_required`; by default it performs only a minimal graph-only refresh when graph state is missing or not queryable. The `vector` object is read-only readiness evidence from the same run-marker protocol as `index --status --format json`; a missing or failed vector run does not make the structural graph claim false, but it must block vector-readiness claims. Use `--status-only` when you only want classification and recommendations. `review-cli-<os>-<arch> graph init <project-path>` is the graph-namespace alias.
4. Query before changing code. Use `search-code`, `architecture`, `developer-routing`, `bounded-context`, `impact`, `dependency-path`, `capability-inventory`, or `summary` according to the decision you are making.
5. Prefer command-level init where available: use `--graph-init auto` by default, `--graph-init always` when state is stale, and `--graph-init skip` only when a read-only lifecycle is intentional and queryable graph state already exists.
6. Select a trigger strategy for ongoing work. Acceptable triggers are a repo-owned refresh command, `review-cli-<os>-<arch> watch . --once --json` for a one-shot working-tree Layer 1-4 refresh, long-running `review-cli-<os>-<arch> watch .` during active edit sessions, or `review-cli-<os>-<arch> graph hook status` / explicit `graph hook install` for post-commit refresh where repo/user policy allows local hook installation. The init command recommends hook status checks but does not install hooks. Plain watch/hook triggers run `review-cli` topology refresh only. The generated Git hook bakes the resolved persistence env into the managed block, defaulting to repo-local `local-sqlite` with SQLite enabled when no mode is resolved, and runs an explicit `context-index` refresh after indexing. For subscription-agent enrichment, either run `review-cli-<os>-<arch> handoff run-agent <handoff-dir> --agent auto --apply` after handoff emission, or explicitly install `graph hook install --subscription-agent --agent auto`; that hook keeps no-model index/handoff generation plus `context-index` refresh synchronous but launches `handoff run-agent --apply` detached from `git commit`. Built-in handoff launchers use Codex CLI (`codex exec`), Claude Code CLI (`claude -p`), OpenCode (`opencode run`), Kiro CLI (`kiro-cli chat --no-interactive`), and Antigravity (`agy -p`); custom wrappers use `--agent-command`. Before installing lifecycle hooks, run `review-cli-<os>-<arch> handoff agent-doctor --agent <agent|all|auto> --strict` to catch missing binaries or changed flags without sending an annotation prompt.
7. Do not silently leave the graph stale after meaningful structural changes. If no trigger is enabled, run an explicit refresh/status check before closeout or record why this lane intentionally stayed direct-source-only.
8. Use `search-code <project-path> "<query>" --graph-only` for exact structural questions. Use normal `search-code` for broad semantic recall and ranking.
9. If a subscribed coding-agent session produced semantic edges, validate and import them with `graph fragment validate/apply` before graph-only retrieval.
10. In Phase 2, use `architecture`, `search-code`, `impact`, and `developer-routing`.
11. In Phase 3, use `search-code`, `developer-routing`, `bounded-context`, and `test-traceability`.

Keep the authority boundary explicit: graph output is static-analysis evidence. It can guide where to inspect and what blast radius to expect, but it does not prove runtime readiness and does not outrank checked-out code, active specs, tests, or runtime evidence. Installing a Git hook changes local repository behavior, so use `graph hook status` freely but run `graph hook install` only when the repo/user policy allows it. Do not represent hook/watch refresh as complete Layer 5 subscription-agent annotation unless the handoff queue was processed and `apply-handoff` succeeded; `graph hook install --subscription-agent` is the explicit opt-in that wires those extra steps.

For provider-bound code graph closeout, include: `Provider used`, `Endpoint/base URL`, `Model and dimensions`, `Graph readiness claim`, `Vector readiness claim`, `Annotation writeback claim`, and `Claim supported`. If any observed provider setting differs from the contract, stop, quarantine or mark affected artifacts, and write a retrospective instead of claiming success.

For agent-lifecycle hooks instead of Git lifecycle hooks, run the published skill installer from the target repo: `python <code-review-skill>/scripts/install-agent-handoff-hooks.py --agent claude,codex,kiro,opencode,antigravity --run-agent auto --preflight`. It installs StopHook/session-idle wrappers for the host agents and embeds the current repo path as the target unless `--dynamic-target` is explicit. `--preflight` runs `handoff agent-doctor --strict` first, so unsupported launcher flags fail before hooks are written.

For AX native-xref recall work, keep raw/derived evidence durable but local by default. Use `xref-normalize --out <target>/.code-review/artifacts/xref/<scope>.refs.csv --run-log <target>/.code-review/artifacts/xref/xref-normalize.jsonl` instead of `/tmp` when a result should be reused by later agents. Store graph-edge dumps under the same ignored artifact root. A large reusable target graph, such as giant-ax's `<workspace-root>/projects/giant-ax/.code-review/graph.sqlite`, should be shared only by a target-repo decision using an exact GitLab/Git LFS path or equivalent artifact store; do not casually commit generated SQLite/vector/session/log siblings.

When the same target repo repeatedly needs repo-specific graph bootstrap commands, durable `.code-review` snapshot rules, or trigger policy, recommend a repo-constitution update such as `AGENTS.md`, Kiro steering, or `CLAUDE.md`. The recommendation should name the concrete command and authority boundary to add. Do not silently edit those files unless the user explicitly authorized target-repo governance changes in the current task.

## Large Graph Retrieval Revalidation

Use this workflow when a target repo says an existing multi-GB graph has been copied, refreshed, or rebuilt and the task is to validate retrieval quality rather than rebuild the graph.

1. Confirm the graph artifact directly:

   ```bash
   ls -lh --time-style=long-iso <repo>/.code-review/graph.sqlite <repo>/.code-review/manifest.json
   sqlite3 <repo>/.code-review/graph.sqlite 'select count(*) from nodes; select count(*) from edges;'
   ```

   A durable `manifest.json` is useful context, but it can be stale after manual copy/rebuild. If manifest counts and SQLite counts differ, cite SQLite and CLI output as the evidence authority and record manifest freshness as a separate hygiene issue.

2. Verify the expected anchor exists before scoring the query:

   ```bash
   sqlite3 <repo>/.code-review/graph.sqlite \
     'select id,label,json_extract(props_json,"$.name"),json_extract(props_json,"$.object_qualified_name"),json_extract(props_json,"$.file_path") from nodes where json_extract(props_json,"$.object_qualified_name") like "%CouponCreateBase%" limit 20;'
   ```

3. Run the exact user-facing retrieval surface. For no-model XPO class-first questions, use the graph-only path:

   ```bash
   PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true \
   review-cli-<os>-<arch> search-code <repo> \
     "coupon id numbering rule" \
     --graph-only --graph-init skip --limit 10
   ```

   Check the ranked candidates, not only `retrieval_stage`. For a source-of-truth retrieval claim, the practical top candidates should include the expected method or an equally authoritative method, and the output should expose matching `candidate_role` / `ranking_reasons` when available.

4. Follow the top candidate with an implementation-context query when the decision needs more than rank:

   ```bash
   PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true \
   review-cli-<os>-<arch> impact <repo>/gts/Classes/CLASSES_CouponCreateBase.xpo \
     CouponCreateBase.nextCouponId --format json
   ```

   For X++ graphs, treat method-level impact as bounded static-analysis evidence. Non-empty `direct_callers` / `direct_callees` is useful proof that the anchor is connected, but the CLI may still warn that unsupported flow-sensitive receiver forms are skipped.

5. Capture lessons separately:
   - `ranking failure`: expected source-of-truth candidate is absent or buried despite graph capability being available.
   - `metadata hygiene`: manifest counts, stored file paths, or snapshot descriptions lag behind the SQLite graph.
   - `coverage residual`: query passes, but relation families or bounded resolver notes show incomplete topology.

Do not patch ranking heuristics until the live graph query proves the current behavior still fails.

## Hallucination And Safety

When using graph results, verify:

- API existence with `search-code`
- deprecated / replacement pointers conservatively when topology is partial
- license compatibility for external dependencies
- duplicate implementation opportunities before recommending new code

Flag security and data risks in design/task artifacts when you see:

- injection
- broken access control
- cryptographic failures
- security misconfiguration
- SSRF
- prompt injection
- sensitive information disclosure
- insecure output handling

Use graph traversal to reason about PII exposure, secrets, and dependency risk.

## Test Traceability

Use `test-traceability <spec-path>` after `scan-specs` and `index` when you need requirement-to-test coverage status.

`trace <req-id>` follows a single requirement to tasks and code.
`trace-llm` is the Layer 5 LLM-assisted mapping and requires the graph/spec pipeline to be in place.
