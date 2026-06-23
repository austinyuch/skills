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
      - backend/ent/*
      - "!backend/ent/schema/"
```

Use directory-level re-includes for SSOT child directories. A file-level `!` cannot rescue files below a pruned parent directory.

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

Use `--no-embeddings` to skip embedding/vector provider initialization. Use `--no-model` when a run must avoid both embeddings and LLM API annotation writes. In `--no-model`, `--capabilities` and `--summaries` remain valid: the CLI reports an agent-instruction handoff for a subscription coding agent instead of calling provider APIs. `CODE_REVIEW_EMBEDDING_PROVIDER=mock` still writes deterministic mock embedding rows and is for tests, not graph-only indexing.

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

Use graph-assisted planning only when it helps the task.

1. Check graph freshness with `index <project-path> --status`.
2. Rebuild with `index <project-path>` when state is stale or missing.
3. Use `index <project-path> --no-embeddings` when the task requires deterministic graph-only state and no embedding/vector provider.
4. Use `search-code <project-path> "<query>" --graph-only` for exact structural questions. Use normal `search-code` for broad semantic recall and ranking.
5. If a subscribed coding-agent session produced semantic edges, validate and import them with `graph fragment validate/apply` before graph-only retrieval.
6. In Phase 2, use `architecture`, `search-code`, and `developer-routing`.
7. In Phase 3, use `search-code`, `developer-routing`, and `test-traceability`.

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
