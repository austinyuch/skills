# Loop Engineering Intake

## When To Use

Use this reference when a user asks `spec-master` for a broad "next work / production-ready / UAT / loop engineering" request that mixes two or more of these surfaces:

- next issues / gaps / specs ranking
- mock-heavy / false-green / over-state reduction
- SDD / TDD / DDD / refactor / test coverage improvement
- manual or project-review artifact refresh
- `SPECS.md`, `NEXT_STEPS.md`, `ISSUE_LOG.md`, `RTM.md`, or `TESTS.md` reconciliation
- local runtime, E2E, VRT, smoke, chaos, or Podman rootless prerequisites
- commit / push closeout

Do not use this reference for a single-surface request already owned by a downstream skill, such as pure `SPECS.md` sync, pure `TESTS.md` maintenance, or pure local runtime allocation.

## Core Rule

Treat Loop Engineering Intake as a route macro, not an SDD Execution Profile.

- `prototype`, `harden`, and `default` remain SDD Execution Profiles.
- Loop Engineering Intake only decomposes a mixed request into lanes.
- Enter an SDD profile only after the first lane and authority surface are clear.
- A route table is not implementation approval; it only records the selected lane, evidence boundary, and stop condition.
- If an optional adapter disagrees with the portable route contract, the main agent must re-read the file-backed authorities and decide in the primary workflow.

## Required Preflight

Before implementation or artifact writes:

1. Read `SPECS.md` if present.
2. Read `NEXT_STEPS.md` if present.
3. Read relevant spec-local `review.md`, `tasks.md`, or reports only as needed.
4. If `SPECS.md`, `NEXT_STEPS.md`, and spec-local closure artifacts disagree, stop and route to stale-state reconciliation.
5. If the worktree is dirty and commit/push is requested, keep publish work behind route confirmation and bounded diff review.

## Route Table Output

Produce a concise route table before implementation.

| Field | Meaning |
|---|---|
| `Lane` | Bounded work lane selected from the table below |
| `Why now` | Evidence from user request or repo state |
| `Authority surface` | File or runtime source that controls the lane |
| `Downstream skill` | Skill that should own the next action |
| `Required evidence` | Files, reports, screenshots, tests, runtime state, or git evidence needed |
| `Stop condition` | What proves the lane is complete enough to move on |
| `Must not do yet` | Guardrail against over-eager automation |

If the user asks to continue immediately, select only the first safe lane and state why it comes first.

## First Safe Lane Rule

The first safe lane is the earliest lane whose authority surface is current enough to support action without overclaiming.

- If resume state is stale, choose `resume-preflight` before implementation.
- If ownership is unclear, choose `next-gap-ranking` or issue-log/CR owner resolution before opening a new spec.
- If runtime ownership is unclear, choose `runtime-e2e-vrt` through local infra governance before service commands.
- If commit/push is requested alongside other work, keep `closeout-publish` last until verification and bounded diff review are complete.

## Lanes

| Lane | Use when | Authority surface | Downstream skill | Must not do yet |
|---|---|---|---|---|
| `resume-preflight` | request says continue / next step / resume, or rolling memo may be stale | `SPECS.md`, `NEXT_STEPS.md`, spec-local closure artifacts | `spec-master` workflow, then SDD only if still active | continue obsolete tasks from stale `NEXT_STEPS.md` |
| `next-gap-ranking` | request asks most valuable next gaps/issues/specs | `SPECS.md`, `ISSUE_LOG.md`, active `review.md`, reports, git status | `spec-master`; may route to `issue-log-manager` or SDD | open a new spec before owner resolution |
| `readiness-hardening` | request mentions mock-heavy, false-green, over-state, hard-coded, stub-heavy, production-ready, UAT | active spec artifacts, test catalog, review evidence | `spec-driven-development` plus review/test support skills | claim PASS or full coverage before real evidence |
| `manual-review-refresh` | request asks for manual/review docs, screenshots, value proposition, stakeholder artifacts | `review.md`, `RTM.md`, `SPECS.md`, generation guides, screenshots; derived snapshots must not overwrite authority sources | `user-manual-skill` or `project-review-skill` after route context | generate polished claims beyond evidence |
| `runtime-e2e-vrt` | request needs backend/frontend, Podman rootless, E2E, VRT, smoke, chaos, or startup scripts | local infra registry and project runtime guide | `local-infra-registry-governance`, then SDD/test workflow | guess ports, stack names, compose ownership, or silently start services when user asked for scripts |
| `traceability-rollup` | request asks to create or reconcile `RTM.md` from spec/test evidence | spec-local requirements/tasks/tests/reviews; do not do derived-to-derived sync among `SPECS.md` / `RTM.md` / `TESTS.md` | `spec-master` workflow or SDD, depending on workspace rules | treat `RTM.md` as source of truth |
| `closeout-publish` | request says update artifacts, commit, push, or publish | upstream spec artifacts first, then derived rollups and git diff | SDD closeout, registry managers, bounded publish workflow | commit before tests, artifact order, and unrelated changes are clear |

## Owner Resolution Order

For mixed issue / gap / tech debt requests, check in this order:

1. Continue active spec.
2. Create CR overlay against completed baseline.
3. Record spec-local lesson or optimization follow-up.
4. Put unresolved item in `ISSUE_LOG.md`.
5. Open a new spec only when the previous options do not apply.

## Compressed Invocation

A user should be able to replace the repeated manual mega-prompt with:

```text
With spec-master, run Loop Engineering Intake for UAT / production-ready readiness.
Decompose the request into route lanes, rank by current evidence, and start with the first safe lane.
Focus on reducing mock-heavy / false-green / over-state, and keep runtime, docs, RTM/SPECS/NEXT_STEPS, and commit/push behind their proper authority surfaces.
```

## Cross-Agent Portability

This route macro must work in Codex, Claude Code, OpenCode, and Kiro-style spec workflows without requiring native hooks, plugins, subagents, or MCP.

- Portable core: Markdown reference, route table, authority surfaces, evals, and file-backed handoff.
- Codex fallback: use repo/user instructions plus the same `spec-master` reference and route table; any native reviewer remains optional and read-only.
- Preferred optional native adapter: Claude Code project sub-agent `.claude/agents/loop-engineering-reviewer.md` for read-only route review.
- Packageable source template: [adapters/claude-code-loop-engineering-reviewer.md](./adapters/claude-code-loop-engineering-reviewer.md).
- Optional specialized Claude reviewers: [adapters/claude-code-loop-engineering-resume-auditor.md](./adapters/claude-code-loop-engineering-resume-auditor.md), [adapters/claude-code-loop-engineering-gap-ranker.md](./adapters/claude-code-loop-engineering-gap-ranker.md), and [adapters/claude-code-loop-engineering-claim-reviewer.md](./adapters/claude-code-loop-engineering-claim-reviewer.md).
- Optional closeout reviewer: [adapters/claude-code-loop-engineering-closeout-reviewer.md](./adapters/claude-code-loop-engineering-closeout-reviewer.md) for read-only commit/push readiness review.
- Adapter overview: [adapters/README.md](./adapters/README.md).
- Write-capable adapter governance: [adapters/write-capable-governance.md](./adapters/write-capable-governance.md). This is design and dry-run guidance only unless a later approved task enables a bounded write executor.
- Kiro specialization: [adapters/kiro-loop-engineering-adapter.md](./adapters/kiro-loop-engineering-adapter.md). This maps Kiro-style spec roots, commands, and optional MCP surfaces to the same route contract; it does not create a new SDD profile.
- Pre-commit static hygiene hook: `scripts/git-hooks/loop-engineering-artifact-hygiene.sh`. This may block explicit staged artifact hygiene violations when installed by an operator, but it does not author governance truth.
- Route table template: [loop-engineering-route-table-template.md](./loop-engineering-route-table-template.md).
- Safe eval runner: `scripts/run_loop_engineering_eval.py` dry-runs by default and only calls Claude with no tools when `--execute` is explicitly passed.
- OpenCode fallback: use the global `spec-master` skill source and classify-only eval runner; plugins/hooks may warn later but must not own correctness.
- Other optional adapters: if available, subagents may do read-only resume audit, gap ranking, and claim review.
- Hooks/plugins/MCP may warn, observe, or enrich context, but must not be the only enforcement path.
- Write-capable hooks/plugins/sub-agents/MCP must remain blocked unless the owning workflow explicitly approves the target artifact, scope token, pre-write conflict check, rollback path, and audit evidence.
- Do not use OpenCode `opencode run` trigger evals for action-shaped prompts; use a classify-only harness or Claude read-only sub-agent review instead.

## Claude Code Sub-Agent Adapter

When Claude Code is available and the user asks for an agent/sub-agent path, prefer the `loop-engineering-reviewer` project sub-agent.

Author and review the canonical adapter text in:

```text
skills/spec-master/references/adapters/claude-code-loop-engineering-reviewer.md
```

Install or sync its sub-agent definition to the Claude runtime path:

```text
.claude/agents/loop-engineering-reviewer.md
```

In this workspace, `.claude` may be a symlink to `.agents`; treat the skill reference template as the packageable source and the Claude path as the runtime copy.

Use it for:

- stale resume checks before continuing from `NEXT_STEPS.md`
- route-table review before implementation
- claim honesty review before manual/review artifact refresh
- closeout review before commit/push

Use the narrower Claude sub-agents when the task is clearly one concern:

- `loop-engineering-resume-auditor`: stale resume / closure drift checks.
- `loop-engineering-gap-ranker`: next-gap ranking from registry, issue log, reviews, CRs, and evidence.
- `loop-engineering-claim-reviewer`: claim honesty review for manual/review/project-review/closeout text.
- `loop-engineering-closeout-reviewer`: verification, dirty-file grouping, derived-summary order, HITL residuals, and bounded commit/push readiness.

Do not use it for:

- writing governance artifacts
- starting or inspecting runtime by executing service commands
- replacing the main agent's route decision
- enforcing correctness as the only mechanism

## Kiro Adapter

When Kiro or `.kiro/specs/` is the user's chosen surface, read [adapters/kiro-loop-engineering-adapter.md](./adapters/kiro-loop-engineering-adapter.md) after this portable contract.

Kiro support is optional and must preserve these boundaries:

- no new Loop Engineering SDD profile;
- no Kiro-only correctness path;
- no MCP write behavior without a future approved write-capable lane;
- no background mutation of governance artifacts.

## OpenCode Warning-Only Adapter

OpenCode plugins may provide warning-only hints for risky tool actions such as governance artifact writes, runtime starts, commit/push, or action-shaped eval prompts. They must not mutate tool arguments, block execution, write formal artifacts, or claim enforcement. If the plugin is unavailable, use this Markdown contract and classify-only evals.

## Pre-Commit Artifact Hygiene Hook

The versioned hook script `scripts/git-hooks/loop-engineering-artifact-hygiene.sh` is a static staged-diff guard. It can be installed by an operator as a pre-commit hook or run manually before closeout.

It checks for:

- hard-coded home-directory paths in added lines;
- strong readiness / live-proof claims without staged evidence pointers;
- derived-to-derived governance sync wording.

It must not:

- rewrite files;
- generate registry truth;
- replace `review.md` as verdict authority;
- replace the closeout reviewer or main agent bounded diff review.

## Minimal Handoff Text

When handing off to a downstream skill, include:

```text
Loop Engineering Intake selected lane: <lane>.
Authority surface: <files/runtime source>.
Required evidence before write/action: <evidence>.
Stop condition: <condition>.
Guardrail: <must-not-do-yet>.
```

## Expected Failures To Avoid

- Treating a mixed mega-prompt as one monolithic SDD implementation request.
- Opening a new spec before owner resolution.
- Continuing stale `NEXT_STEPS.md` despite completed `SPECS.md` / `review.md` closure.
- Routing runtime allocation through registry sync or SDD authoring.
- Generating manual/review docs that overstate fixture-backed evidence.
- Committing broad dirty worktree state because the prompt says "then git commit and push".
