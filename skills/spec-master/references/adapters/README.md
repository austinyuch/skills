# Loop Engineering Native Adapters

These adapters are optional. The portable source of truth remains:

- `skills/spec-master/references/loop-engineering-intake.md`
- `skills/spec-master/evals/evals.json`
- route tables produced by the main agent

Do not make hooks, plugins, MCP, or subagents the only enforcement path.

Write-capable native adapter behavior is governed by:

- [write-capable-governance.md](./write-capable-governance.md)

That reference is design and dry-run guidance only. It does not enable any real write-capable hook, plugin, MCP tool, or sub-agent.

## Current Adapter Status

| Agent | Status | Source | Runtime path | Role |
|---|---|---|---|---|
| Claude Code | installed first | [claude-code-loop-engineering-reviewer.md](./claude-code-loop-engineering-reviewer.md) | `.claude/agents/loop-engineering-reviewer.md` | read-only route review |
| Claude Code specialized reviewers | installed | resume/gap/claim/closeout reviewer templates | `.claude/agents/loop-engineering-*.md` | read-only focused review |
| Codex | not installed | future `codex.md` | n/a | optional read-only reviewer, AGENTS.md guidance, or dry-run planner |
| OpenCode | warning source added | future formal package plus repo `plugins/loop-engineering-warning-adapter.js` | OpenCode plugin auto-discovery when copied/enabled | optional warning/telemetry adapter or dry-run planner |
| Kiro | reference added | [kiro-loop-engineering-adapter.md](./kiro-loop-engineering-adapter.md) | `.kiro/specs/` or project-specific Kiro surfaces when present | optional Kiro-specific route support |
| Git pre-commit | source added | `scripts/git-hooks/loop-engineering-artifact-hygiene.sh` | operator-installed hook path | static artifact hygiene guard |
| MCP | not installed | future provider-specific contract | n/a | read/query or dry-run mutation planning only until provider/schema/auth/rollback are pinned |

## Adapter Rules

- Keep the main route decision in the primary agent.
- Keep formal governance writes in the owning skill/workflow.
- Keep the portable contract usable without any adapter installed.
- Subagents may review, rank, or identify missing evidence.
- Subagents must not write `SPECS.md`, `NEXT_STEPS.md`, `RTM.md`, `TESTS.md`, `review.md`, or formal skill files.
- Runtime work must stay behind `local-infra-registry-governance`.
- Commit/push must stay behind bounded diff review and verification.
- Pre-commit hooks may block explicit static hygiene violations, but they do not author governance truth.
- Do not use OpenCode `opencode run` as an eval runner for action-shaped prompts.
- Keep write-capable behavior blocked unless an owning workflow explicitly approves the target artifact, scope token, pre-write conflict check, rollback path, and audit evidence.
- Reject derived-to-derived sync. Adapter output cannot directly become registry truth.

## Portable Fallbacks

| Agent | Fallback path when no native adapter is installed |
|---|---|
| Codex | read `loop-engineering-intake.md`, produce the route table in the main workflow, and optionally ask a read-only reviewer pattern to audit the table |
| Claude Code | use the Markdown route contract directly; `loop-engineering-reviewer` is a read-only convenience, not an authority replacement |
| OpenCode | use the global `spec-master` skill source and classify-only eval runner; plugins/hooks are warning or telemetry candidates only |
| Kiro | use the Markdown route contract and active spec root guidance; Kiro MCP/commands remain optional read/query or dry-run planning surfaces |
| MCP | keep external mutation blocked; use read/query or dry-run planning until a pinned provider/tool contract exists |

## Candidate Future Roles

| Role | Good use | Avoid |
|---|---|---|
| `resume-auditor` | read `SPECS.md`, `NEXT_STEPS.md`, active `review.md/tasks.md`; report stale-state drift | continuing obsolete tasks or rewriting memos |
| `gap-ranker` | rank `SPECS.md`, `ISSUE_LOG.md`, active reviews, and reports by authority/risk/value | opening new specs before owner resolution |
| `claim-reviewer` | compare manual/review claims with evidence level before artifact refresh | rewriting stakeholder artifacts directly |
| `closeout-reviewer` | review verification, bounded diff scope, registry/memo refresh order, and HITL leftovers before commit/push | committing, pushing, or rewriting artifacts |

Add these only after the portable route contract remains stable under evals.

## Write-Capable Candidates

Future write-capable candidates must start in dry-run mode:

| Candidate | Dry-run Output | Write Gate |
|---|---|---|
| permission planner | target artifact, owner, scope token, rollback path, audit evidence | owning workflow approval |
| registry summary proposer | upstream source summary and blocked derived-to-derived paths | registry lane delegation |
| CR freshness updater | proposed CR evidence text | active CR lane approval |
| MCP mutation planner | provider/tool schema/auth/rollback checklist | pinned external contract |

If any gate is missing, the adapter must produce `blocked` or `advisory` output, not a patch.
