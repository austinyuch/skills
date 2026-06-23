# Local State Version-Control Policy

This skill commonly writes project-local SQLite state and small metadata files under a workspace-relative directory such as `.code-review/`. Agents must classify those files before changing `.gitignore`, `.gitattributes`, or committing generated state.

The core rule is intentionally conservative: generated local state is ignored unless the repository deliberately promotes a specific file into durable GraphRAG state or curated evidence.

## Working Tree Audit Workflow

Use this workflow when a user asks for code review, GraphRAG indexing, `search-code`, `developer-routing`, `bounded-context`, or Graph Explorer in a git repository.

1. Run `git status --short` before write-producing commands when git is available. Treat those entries as pre-existing user or repository changes.
2. Run the requested review/index/query command. Prefer read-only commands when the user only asked for inspection.
3. Run `git status --short` again after the command. Compare with the baseline.
4. Classify new or modified files:
   - review/report artifacts: summarize and leave for the user unless the repo has a known evidence path;
   - local runtime state: ignore or recommend ignore rules;
   - durable GraphRAG state: only promote when the repo explicitly needs shared prebuilt graph retrieval;
   - unrelated files: do not touch.
5. If new state should be ignored, prefer the narrowest `.gitignore` rule that covers generated runtime output without hiding durable evidence.
6. If a graph DB should be tracked, add a narrow `.gitattributes` LFS rule for the exact DB path and avoid broad `*.sqlite` / `*.db` patterns.
7. In the final response, state what changed in the working tree and which files should be committed, ignored, or left untracked.

Do not run destructive cleanup, reset user changes, or commit generated artifacts unless the user explicitly asks.

## Decision Rule

| File class | Default action | When to track | Reason |
|---|---|---|---|
| `.code-review/graph.sqlite` or configured graph `.db` / `.sqlite` | Ignore generated local copies | Track with Git LFS only when the repo intentionally shares a prebuilt GraphRAG DB for later agent queries | The DB can be useful durable project knowledge, but it is also generated and may go stale |
| Durable graph `manifest.json` | Ignore unless classified | Track as normal text when it documents the graph DB snapshot, source corpus, schema/version, generation inputs, freshness policy, or rebuild command | A reusable graph DB needs enough metadata for future agents to interpret or refresh it |
| Runtime/cache `manifest.json` | Ignore | Do not track | It only describes local generated runtime artifacts and can be recreated |
| Runtime `status.json` | Ignore | Rarely track; only by explicit curated-evidence convention, preferably outside `.code-review/` | Status is usually run-specific, machine-specific, or stale quickly |
| `vector.sqlite` / vector stores | Ignore | Track with Git LFS only after explicit review of size, provider/model coupling, freshness, and data sensitivity | Usually generated from code plus embedding settings; may be large, stale, or sensitive |
| `session.sqlite`, `state.sqlite`, local registry state | Ignore | Do not track | Runtime/session state is machine- and run-specific |
| `cache/`, `tmp/`, logs, report viewer runtime output | Ignore | Do not track | Derived runtime data, not source or durable evidence |
| env files, credentials, local config with secrets | Ignore | Do not track | Secrets must not be committed |

## How To Classify The Three Common Files

`graph.sqlite` is not automatically source. In this skill's GraphRAG flow, it becomes worth versioning only when the repository wants a shared, prebuilt graph for agent retrieval, handoff, or review evidence. If every agent can cheaply rebuild it from source with the same configuration, keeping it ignored is valid. If rebuild cost, corpus availability, or repeatability matters, promote it to a durable artifact and use Git LFS.

`manifest.json` should be paired with a durable graph when it answers questions future agents need: what source tree was indexed, which command/config produced the DB, which schema or skill version applies, when it was generated, and what freshness rule governs it. A manifest that only enumerates temp files, runtime cache entries, local ports, or machine paths is runtime state and should be ignored.

`status.json` should be ignored by default for this skill. Runtime status, readiness status, local registry status, and preflight output are point-in-time observations. They can mislead future agents if committed as if they were current truth. If a project needs durable status evidence, place it in a reviewed evidence path with clear timestamp/provenance instead of treating `.code-review/status.json` as source.

## Recommended `.gitattributes`

Use Git LFS only for graph DB files intentionally promoted to durable GraphRAG artifacts. Avoid broad `*.sqlite` or `*.db` rules because they can accidentally capture session, vector, cache, or application databases. JSON metadata should stay regular text unless it is unusually large.

```gitattributes
# Durable code-review GraphRAG graph database, only if intentionally shared.
.code-review/graph.sqlite filter=lfs diff=lfs merge=lfs -text

# If the project config uses a graph-specific .db name instead:
# .code-review/graph.db filter=lfs diff=lfs merge=lfs -text
```

For customized `CODE_REVIEW_SQLITE_GRAPH_FILE` values, replace the path above with the configured graph DB path. If several graph DB shards are intentionally durable, prefer a narrow graph-only pattern such as `.code-review/graphs/*.db` instead of `.code-review/*.db`.

## Recommended `.gitignore`

Default generated-state posture:

```gitignore
# code-review local state: ignore generated runtime data by default.
.code-review/*
!.code-review/
!.code-review/config.yaml
```

This is the safest option for most target repositories: keep the declarative review config versioned, while runtime DBs, reports, sessions, caches, status files, and generated inventories stay ignored.

If the repo intentionally promotes `graph.sqlite` and a durable graph manifest into versioned GraphRAG artifacts, use an allowlist pattern instead:

```gitignore
# code-review local state: ignore generated runtime data by default.
.code-review/*
!.code-review/
!.code-review/config.yaml
!.code-review/graph.sqlite
!.code-review/manifest.json

# If the project config uses a graph-specific .db name instead:
# !.code-review/graph.db
```

Do not unignore `.code-review/**` or copy/symlink target project files under `.code-review/`. Configuration belongs in `.code-review/config.yaml`; generated dry-run evidence belongs in a report path such as `.code-review/reports/corpus-plan.json` and remains ignored unless the repository has an explicit evidence-review convention.

Do not unignore `.code-review/status.json` by default. Track a `status.json` only when the repository has an explicit curated-evidence convention and the file is not transient runtime status.

Git applies ignore rules in order, so the `!` lines only work when the parent path is already visible to Git. In practice:

- Ignore the tree or broad pattern first.
- Unignore the parent directory next.
- Unignore only the exact durable file paths after that.

Prefer file-specific negation over directory-wide negation. `!.code-review/graph.sqlite` is safe; `!.code-review/**` is not, because it can accidentally bring back caches, session DBs, logs, or viewer output.

If the repo wants to keep one durable DB plus a manifest and nothing else, the practical pattern is:

```gitignore
.code-review/*
!.code-review/
!.code-review/config.yaml
!.code-review/graph.sqlite
!.code-review/manifest.json
```

If the project stores durable graph DB files in a subdirectory, every parent directory must be unignored before unignoring the file and its durable manifest:

```gitignore
.code-review/*
!.code-review/
!.code-review/config.yaml
!.code-review/graphs/
!.code-review/graphs/*.db
!.code-review/graphs/manifest.json
```

## Agent Checklist

Before modifying repository tracking rules:

1. Compare post-command `git status --short` with the pre-command baseline.
2. Identify the configured graph state path from env/config or CLI output.
3. Decide whether the graph DB is an intended shared GraphRAG artifact or just a local rebuildable index.
4. If it is durable, add a narrow Git LFS rule for that exact graph DB path in `.gitattributes`.
5. Classify `manifest.json`: track only if it documents the durable graph snapshot; otherwise ignore it.
6. Classify `status.json`: ignore runtime/local status by default; track only curated evidence by explicit repo convention.
7. Add `.gitignore` rules that either ignore all generated state or allowlist only the durable graph DB and its durable manifest.
8. Avoid committing local env files, credentials, absolute machine paths, logs, temporary reports, and stale caches.
9. Report the recommended disposition: commit, ignore, leave untracked, or ask the repo owner to classify.

When unsure whether a file is durable graph state or derived runtime state, leave it ignored and ask the repository owner to classify the intended GraphRAG workflow.
