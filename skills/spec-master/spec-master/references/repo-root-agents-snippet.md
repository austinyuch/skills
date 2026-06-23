# Repo Root `AGENTS.md` Snippet for Spec / Governance Routing

Use the following snippet when a project repository needs a short, opinionated `AGENTS.md` rule that pushes complex spec/governance work into the right front door.

```md
## Spec / Governance Front Door

### Default rule

If work touches any of the following, treat `spec-master` as the default entrypoint:

- `requirements.md`
- `design.md`
- `tasks.md`
- `review.md`
- `.agents/specs/NEXT_STEPS.md`
- `.agents/specs/SPECS.md`
- `.agents/specs/RTM.md`
- repo-owned global skill behavior under `skills/`
- review / retrospective / optimization planning
- governance wording, readiness wording, or workflow trigger logic

When unsure, start with `spec-master`.

### What `spec-master` is for

`spec-master` is the routing front door for spec and governance work.

It should:
- route branch-spec authoring / resume / review / optimization to `spec-driven-development`
- route `TESTS.md` governance to `test-registry-manager`
- route `SPECS.md` registry sync to `spec-registry-manager`
- route local runtime allocation / reuse / release to `local-infra-registry-governance`

It should not be treated as the final authority for readiness or test evidence.

### Review and retro rule

If the work is already inside an active spec lane:

- formal review = `spec-driven-development` Phase 5
- retro / optimization / repeated-gap follow-up = `spec-driven-development` Phase 6

Scrum-style coordination may trigger review or retro,
but final truth still belongs to spec-local artifacts, especially `review.md`.

### Exceptions (direct routing allowed)

Do not force `spec-master` if the work is clearly only one of these:

- folder-level or workspace `TESTS.md` governance only  
  → use `test-registry-manager`

- `SPECS.md` registry wording / lifecycle summary only  
  → use `spec-registry-manager`

- local dev / UAT / E2E runtime allocation only  
  → use `local-infra-registry-governance`

### Authority boundary reminder

- `review.md` = final readiness / acceptance authority
- `TESTS.md` = test catalog / evidence authority
- `SPECS.md` = stable registry summary
- `NEXT_STEPS.md` = rolling operational memo
- `RTM.md` = derived traceability rollup
- local infra registry = runtime allocation authority

Never let derived artifacts replace `review.md`.
Never let runtime state leak into `SPECS.md` / `RTM.md` / `NEXT_STEPS.md`.
```
