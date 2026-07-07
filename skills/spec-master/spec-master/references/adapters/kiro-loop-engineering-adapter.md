# Kiro Loop Engineering Adapter

This reference describes Kiro-specific Loop Engineering support. It is an optional adapter. The portable source of truth remains `../loop-engineering-intake.md`.

## Role

Use this adapter when a Kiro-style workflow, command, or MCP configuration needs to participate in Loop Engineering Intake without creating a divergent workflow.

Kiro support is allowed to:

- read the active spec root from `.agents/specs/`, `.kiro/specs/`, or `.claude/specs/`;
- map mixed production-ready / UAT / false-green / commit-push prompts into the Loop Engineering route table;
- preserve Kiro's requirements -> design -> tasks discipline after the route lane is selected;
- use Kiro MCP or command surfaces as read/query or dry-run planning support.

Kiro support must not:

- create a new Loop Engineering SDD profile;
- make `.kiro` the only valid spec root;
- treat MCP availability as required for correctness;
- write `SPECS.md`, `NEXT_STEPS.md`, `RTM.md`, `TESTS.md`, `review.md`, or formal skill files from a background adapter;
- start runtime, commit, push, or mutate external systems as a side effect of routing.

## Route Mapping

| Kiro prompt shape | Loop Engineering lane | Required boundary |
|---|---|---|
| "continue last task" with stale memo risk | `resume-preflight` | Compare `SPECS.md`, `NEXT_STEPS.md`, and spec-local closure artifacts first. |
| "production-ready", "UAT", "false-green", "mock-heavy" | `readiness-hardening` | Do not claim PASS before evidence from upstream spec/test/review surfaces. |
| "manual", "review", "stakeholder artifact" | `manual-review-refresh` | Claims must not exceed `review.md`, reports, and evidence source. |
| "start E2E/runtime" | `runtime-e2e-vrt` | Route to local infra governance; do not guess ports or stack ownership. |
| "commit/push" | `closeout-publish` | Keep behind verification and bounded diff review. |

## Active Root Resolution

In this workspace, `.agents/specs/` is the active authoritative root. Downstream Kiro projects may use `.kiro/specs/`; when multiple roots exist, use the project guidance and current `SPECS.md` / `NEXT_STEPS.md` authority before selecting a lane.

Do not copy runtime path decisions into `SPECS.md`, `NEXT_STEPS.md`, `RTM.md`, `TESTS.md`, or `review.md`.

## MCP Boundary

Kiro MCP configuration can expose read/query tools or dry-run planning. External mutation remains blocked until provider, tool schema, auth, approval, rollback path, and audit evidence are pinned in a separate approved implementation lane.

## Minimal Handoff

```text
Loop Engineering Intake selected lane: <lane>.
Kiro adapter role: optional route support only.
Authority surface: <files/runtime source>.
Required evidence before action: <evidence>.
Guardrail: portable route contract remains authoritative; write-capable adapter behavior is inactive.
```
