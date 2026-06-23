---
name: uat-demo-agent
description: Use this skill when you need to generate a plan from structured inputs, validate a plan, run a demo/UAT plan, or inspect a generated report through the packaged `uatdemo` CLI delivered as the `uat-demo-agent` skill bundle. Also use it when the user explicitly wants the installed workspace/global agent skill surface rather than direct package-level Go calls.
---

# UAT Demo Agent

This skill is the **deliverable agent skill bundle** for `aclab-uat-demo-agent`. It stays thin: the runtime behavior lives in the packaged `uatdemo` CLI, while this skill provides the stable trigger surface, command mapping, and portability rules.

## When to use

- The user asks to generate a plan from structured source inputs.
- The user asks to validate a plan file.
- The user asks to run a demo plan.
- The user asks to run a web UAT plan.
- The user asks to run a bounded Windows VM computer-use proof through the packaged CLI.
- The user asks to inspect a generated report.
- The user explicitly wants the installed agent skill / packaged CLI surface rather than direct Go package calls.

## Commands

- `${UATDEMO_BIN:-uatdemo} plan generate --manifest <source-document-manifest.json> --request <plan-generation-request.json>`
- `${UATDEMO_BIN:-uatdemo} plan validate --file <plan.json>`
- `${UATDEMO_BIN:-uatdemo} run demo --file <plan.json>`
- `${UATDEMO_BIN:-uatdemo} run uat --file <plan.json>`
- `${UATDEMO_BIN:-uatdemo} run windows-vm-computer-use --file <scenario.json> [--vm-instance <domain-or-instance>]`
- `${UATDEMO_BIN:-uatdemo} report show --file <report.json>`
- `${UATDEMO_BIN:-uatdemo} report show --bundle <bundle.json>`
- `${UATDEMO_BIN:-uatdemo} report verify-computer-use-bundle --bundle <bundle.json>`

Read `references/commands.md` when you need the operator cookbook, input prep rules, and post-run verification flow.
Read `references/skill-integration.md` when the current workspace is the `aclab-uat-demo-agent` source repo and you need to cooperate with `spec-master`, `spec-driven-development`, `spec-registry-manager`, `user-manual-skill`, or `project-review-skill`.

When the user needs a reusable onboarding lane for a different target repository, prefer the generic project-profile path in `references/project-profile-onboarding.md` rather than the repo-local self-dogfood helper.

## Quick operating flow

Use this minimal sequence when a general agent needs to operate the packaged CLI without guessing:

1. Decide whether the user already has a plan file.
   - If yes: start at `plan validate`.
   - If no: prepare structured manifest/request inputs, then run `plan generate`.
2. Prefer `run uat` for normal web-oriented execution. Use `run windows-vm-computer-use` only when a spec or user request explicitly routes into Windows VM computer-use proof work; set `--vm-instance` or `UATDEMO_WINDOWS_VM_INSTANCE` when targeting a known VM domain/instance.
3. After `run uat` or `run demo`, inspect the returned `reportPath`, `bundlePath`, `runRecord`, and `artifacts` rather than assuming success from exit code alone.
4. If the user asks what still blocks UAT/demo, read workspace sources such as `.agents/specs/SPECS.md`, `.agents/specs/RTM.md`, and `.agents/specs/NEXT_STEPS.md` first, then distinguish strategic blockers from the local runnable path.

## Source-repo integration boundary

When the active workspace is this repository, `uat-demo-agent` is the repo-owned execution/proof surface, not the global spec router.

- Use `spec-master` as the global entrypoint that decides whether the work belongs to spec authoring, registry sync, runtime governance, or packaged CLI operation.
- Use `spec-driven-development` for new specs, follow-ons, resume, implementation, review, and closeout.
- Use `spec-registry-manager` only when the primary truth surface is `SPECS.md`.
- For improvement findings in this source repo, record the issue in `.agents/specs/ISSUE_LOG.md`, assign it to `.agents/specs/ISSUE_LOG.md#cluster-work-packages`, then rank and owner-resolve it before opening a new spec or change request.
- Use `user-manual-skill` / `project-review-skill` for consumer-doc generation, but keep them anchored to this repo's guides plus `bash scripts/refresh_tracked_consumer_docs.sh`.
- Keep repo-specific cooperation notes here in the source repo so that publish/deploy of `uat-demo-agent` carries the same guidance into installed skill roots.

## Preflight checks

Before invoking the CLI, a general agent should verify:

1. the binary resolves successfully
2. the runtime state path is known
3. the chosen project-local state path is ignored by `.gitignore`
4. the input file (`plan.json`, manifest, request, or report) actually exists
5. any bundle/report/artifact paths referenced by later commands are local and readable

## Default local web UAT recipe

Use this when the user wants a bounded local smoke path:

1. create or locate a valid `plan.json`
2. run `plan validate --file <plan.json>`
3. set `UATDEMO_STATE_DIR` to a project-local temp path if you need an isolated run
4. run `run uat --file <plan.json>`
5. optionally run `report show --file <report.json>` on the generated report

The purpose of this recipe is to prove the packaged CLI surface works locally. It does not by itself upgrade the repo to full demo-ready or clear unrelated runtime blockers.

## Rules

1. Reuse the packaged CLI surface; do not bypass it with ad-hoc internal package calls when the user explicitly wants installed/global behavior.
2. Pass structured JSON files that already conform to repository contracts.
3. Treat `run uat` as web-oriented unless the caller explicitly routes into Windows executor work elsewhere. Treat `run windows-vm-computer-use` and VM instance hints as proof-entrypoint setup that still requires a real VM run before any live-readiness claim.
4. Resolve the binary in this order: `UATDEMO_BIN` override, then global config `UATDEMO_BIN`, then bundled platform binary inside `scripts/`, then `uatdemo` from `PATH`.
5. Resolve state/config in this order: env override `UATDEMO_STATE_DIR`, then project config, then global config.
6. Treat `UATDEMO_BIN` as a global-only trust boundary: project config may not override which binary is executed.
7. Default the runtime state to `{target-workspace}/.uatdemo` when running against a target workspace. If the current context is an installed skill directory rather than a target workspace, fall back to an agent-neutral user state directory instead of writing under the skill install folder.
8. When the resolved runtime state directory is project-local, require the target project's `.gitignore` to ignore it before running the CLI. The default `.uatdemo/` state must be ignored, and `temp/...` state directories must be covered by `temp/` or the exact subpath.
9. Never treat `~/.codex/skills/...`, `~/.config/opencode/skills/...`, `~/.claude/skills/...`, `~/.gemini/skills/...`, or `~/.kiro/skills/...` as runtime state homes.
10. Keep this skill thin. Domain logic remains in Go packages and contracts.

## BVT smoke test guidance

Use BVT (Build Verification Test) smoke to get fast feedback on core paths after a UAT run completes. BVT smoke is a necessary gate but does not by itself prove full readiness.

When to run:
- After `run uat` completes (post-run verification)
- As a CI gate before merge
- After a hotfix lands
- Before a release candidate is tagged

How to filter:
- From the project's Test Decision Table (TESTS.md), select tests tagged `smoke` with Risk ≥ 4.
- Execute using Go test pattern matching: `go test ./... -run "TestSmoke" -timeout 120s`
- Alternatively filter by build tags if the project uses them.

Success criteria:
- All filtered `smoke` + Risk ≥ 4 tests must report PASS (not PASS*, SKIP, or BLOCKED).
- A single failure blocks the gate.

BVT smoke does not prove demo readiness, full integration coverage, or absence of regression in non-smoke paths. It is a fast-feedback filter, not a readiness verdict.

Read `references/test-governance-guidance.md` for the complete BVT operating flow.

## Exploratory test guidance

Use exploratory testing to systematically probe boundaries that structured UAT test cases may not cover. Exploratory testing supplements UAT — it does not replace it.

When to trigger:
- A new feature integrates for the first time and structured tests are sparse.
- A coverage gap is identified (TESTS.md shows `none` or `mock` status for a critical path).
- A chaos test or degradation smoke reveals a failure mode not covered by existing tests.
- Post-release observation surfaces unexpected behavior.

Structured flow:
1. **Charter**: Define mission, scope, time-box, and risk focus.
2. **Session**: Execute within the time-box, recording observations.
3. **Findings**: Document each observation with severity and reproducibility.
4. **Follow-up**: Feed findings back into the Test Decision Table (new rows, updated Risk, or CRs).

Relationship to UAT:
- Exploratory findings that warrant permanent coverage → add test rows to TESTS.md.
- Exploratory findings that reveal design gaps → create a CR in the relevant spec.
- Exploratory testing never downgrades or replaces existing structured UAT results.

Read `references/test-governance-guidance.md` for the charter template and session recording format.

## Test-tag aware verification

When verifying results after a `run uat` or `run demo`, prioritize checks based on test tag relevance. The following tags are most relevant to `uat-demo-agent` operations:

| Tag | Verification focus |
|-----|-------------------|
| `smoke` | Core path pass/fail — check first |
| `error-force` | Error propagation and edge cases — check second |
| `api` | CLI contract and JSON schema compliance |
| `regression` | Previously-fixed bugs remain fixed |
| `cross-spec` | Publisher ↔ reporting ↔ bundle interactions |
| `ai-agent` | Reasoning loop and LLM fallback behavior |

Post-run verification priority order: `smoke` → `error-force` → `api` → `regression` → `cross-spec` → `ai-agent`.

Tag-to-depth mapping:
- `smoke` + `error-force`: Must pass for any forward progress. Block on failure.
- `api` + `regression`: Should pass. Investigate failures before claiming readiness.
- `cross-spec` + `ai-agent`: Informational for first slice. Gaps acceptable if documented.

Read `references/test-governance-guidance.md` for full tag definitions and filtering commands.

## Output expectations

- `plan validate` should return a validated status JSON.
- `run demo` should return a structured payload including report/artifacts/script.
- `run uat` should return a structured payload including `RunRecord`, `reportPath`/bundle info, and artifact locators.
- `report show` should print a compact human-readable report summary.

If a command returns output that lacks these expected fields, treat it as an investigation point rather than silently assuming the run succeeded.

## Portability note

This skill is intended to work when installed globally at either `~/.codex/skills/uat-demo-agent/` or `~/.config/opencode/skills/uat-demo-agent/`. Do not assume the active workspace contains this repository, `scripts/uatdemo.sh`, or `bin/uatdemo`.

Default config file locations:

- global config: `${UATDEMO_GLOBAL_CONFIG:-$HOME/.config/uatdemo/config.env}`
- project config: `${UATDEMO_PROJECT_CONFIG:-<discovered-project-root>/.uatdemo/config.env}` where the wrapper first walks upward from the current cwd to find the target workspace root (for example `go.mod`, `.uatdemo/`, or `admin-ui/src`).

In project config, only project-overridable values such as `UATDEMO_STATE_DIR` should be set. Do not use project config to select a different binary.

Target-project git hygiene:

- if the runtime state stays at the default location, add `.uatdemo/` to the target project's `.gitignore`
- if the runtime state is moved under `temp/...`, add `temp/` (or the exact configured subpath) to the target project's `.gitignore`

Default state policy:

- project-local default: `{target-workspace}/.uatdemo`
- user-level fallback outside project-local mode: `${XDG_STATE_HOME:-$HOME/.local/state}/uatdemo` on Linux, `~/Library/Application Support/uatdemo` on macOS, or `%LOCALAPPDATA%/uatdemo` on Windows
- project/global config may still set `UATDEMO_STATE_DIR`, and config path values may use `${HOME}` / `~` style expansions
