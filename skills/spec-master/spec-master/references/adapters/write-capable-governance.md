# Write-Capable Native Adapter Governance

This reference defines the safety contract for future write-capable native adapters. It is design and dry-run guidance only. It does not enable hooks, plugins, MCP tools, or sub-agents to write files.

## Authority Principle

The portable Loop Engineering route contract remains authoritative:

- `skills/spec-master/references/loop-engineering-intake.md`
- `skills/spec-master/evals/evals.json`
- active SDD / CR artifacts in the invoking workspace

Native adapters are optional gated executors. They are not governance owners.

## Plain-Language Red Line

A native adapter crosses the write-capable red line when it can cause a side effect beyond advice or dry-run planning. Examples include:

- editing or deleting files;
- writing `SPECS.md`, `NEXT_STEPS.md`, `RTM.md`, `TESTS.md`, `review.md`, or formal skill files;
- starting or stopping runtime services;
- mutating external systems through MCP or APIs;
- committing, tagging, merging, or pushing git state.

Read-only sub-agents, warning-only plugins, and static pre-commit checks stay below the red line when they only report findings or block explicit static hygiene violations. They still do not become authority owners: upstream SDD/CR/review/test/registry artifacts remain the source of truth.

## Adapter States

| State | Meaning | Allowed Behavior |
|---|---|---|
| `advisory` | adapter can read context and identify risks | read-only review, route-table critique |
| `dry-run` | adapter can describe a proposed write | planned target, owner, evidence, rollback, blocked reason |
| `write-requested` | user explicitly asks for a bounded write | pre-write checks only |
| `write-mode` | all gates pass and owning workflow authorized the write | bounded patch plus audit report |
| `blocked` | any required proof is missing | no write; produce conflict or handoff note |

Default state is `advisory` or `dry-run`. Any unclear state is `blocked`.

## Permission Contract

A write-capable adapter must name all of these before writing:

1. **Target artifact**: exact file or bounded section.
2. **Owning workflow**: SDD phase, CR lane, registry manager, test registry manager, local infra lane, or closeout lane.
3. **Allowed write**: the specific summary, patch, or report it may create.
4. **Forbidden writes**: adjacent surfaces it must not mutate.
5. **Scope token**: a lane token such as `spec/<name>` or `cr/<id>`.
6. **Pre-write conflict check**: ownership, freshness, dirty worktree, and competing lane checks.
7. **Rollback path**: how the bounded write can be reverted or superseded.
8. **Audit evidence**: report, diff/readback, command output, and CR freshness evidence.

If any item is absent, the adapter must remain dry-run or blocked.

## Target Surface Rules

| Surface | Default | Write Gate | Blocked Pattern |
|---|---|---|---|
| `requirements.md`, `design.md`, `tasks.md`, `review.md` | dry-run | active SDD phase owns the file | writing outside phase approval |
| `SPECS.md` | dry-run | registry lane or explicit bounded summary delegation | using another derived artifact as source |
| `NEXT_STEPS.md` | dry-run | current active lane updates rolling memo from upstream truth | task ledger or history log |
| `RTM.md` | dry-run | traceability rollup from upstream source authority | generating from `SPECS.md` |
| `TESTS.md` | dry-run | owning test registry lane and row-level authority are clear | workspace rollup as row-level truth |
| formal skill files | dry-run | active SDD / CR lane owns the behavior change | background hook/plugin mutation |
| runtime / services | blocked | route to local infra lane | silent service start |
| commit / push | blocked | route to closeout-publish lane | commit without bounded diff review |

## Pre-Write Conflict Check

Before any formal writeback, an adapter must confirm:

- lane identity and branch identity are clear,
- current lane is authoritative for the target surface,
- upstream source authority was re-read,
- no competing writable lane owns the same artifact,
- derived-to-derived sync is not being used,
- ownership evidence exists in the invoking workspace,
- target content does not include machine-local paths, ports, containers, or temp directories.

If a conflict is found, stop the write and produce an audit-only conflict note.

## Cross-Agent Boundaries

| Agent / Mechanism | Allowed Initial Role | Write-Mode Status |
|---|---|---|
| Codex repo/user guidance | main workflow routing and dry-run planning | design-only until a bounded task approves implementation |
| Claude Code read-only reviewer | advisory review with read-only tools | must not write files or run mutating commands |
| Claude Code future write-capable sub-agent | dry-run planning only | blocked until separate approval, owner, scope token, rollback, and audit path exist |
| Claude hooks/plugins | warning or telemetry only | not required for correctness |
| OpenCode global skill | portable route contract and classify-only eval source | formal skill source remains under the owning repo |
| OpenCode agents/subagents/plugins | warning, telemetry, or dry-run planning only | no action-shaped execution until classify-only proof exists |
| MCP tools | read/query or dry-run mutation planning | external writes blocked until provider, schema, auth, approval, and rollback are pinned |

No single native mechanism is required for correctness. If an adapter is missing, use the portable Markdown contract.

## Eval Safety

Action-shaped prompts must be judged in classify-only / no-tools mode when they mention:

- starting runtime,
- commit or push,
- editing `SPECS.md`, `NEXT_STEPS.md`, `RTM.md`, `TESTS.md`, or `review.md`,
- writing formal skill files,
- calling external MCP mutation tools,
- installing hooks/plugins/sub-agents.

The evaluator must not claim that a write, runtime startup, commit, push, or external action happened.

## Audit and Closeout

Every approved write must leave:

- ownership evidence,
- pre-write conflict result,
- bounded diff or readback,
- rollback or supersede path,
- report under the active spec,
- CR freshness or resolution update when a CR is active.

If write mode is not implemented, final review must say `DESIGN_ONLY` or `NOT_IMPLEMENTED` and must not imply that write-capable adapters are enabled.
