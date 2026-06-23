# Spec Master Family Manual Guide

This guide defines how to maintain `skills/spec-master/manual.html` as the packageable operational manual for the Spec Master family.

## Purpose

The manual must serve three audiences:

- **Agent operators** who need a step-by-step routing guide.
- **Engineering leads** who want to understand which skill owns which surface.
- **Packagers / maintainers** who need a stable operational page to ship with the family.

The content should combine:

- user-manual style walk-throughs
- quick start guidance
- routing decision examples
- explicit claim boundaries
- a visible `EN / 繁中` language switch

## Canonical Locations

Maintain the operational manual in:

- `skills/spec-master/manual.html`

Maintain this update contract in:

- `skills/spec-master/MANUAL_GENERATION_GUIDE.md`

Do not make `docs/manual/**` the only authoritative copy. It may summarize or render this content, but the packageable source belongs with `skills/spec-master/`.

## Inputs To Read Before Updating

Read these first:

- `skills/spec-master/SKILL.md`
- `skills/spec-master/README.md`
- `skills/spec-master/GENERATION_GUIDE.md`
- `skills/spec-master/references/routing-matrix.md`

Read these when the manual mentions downstream authority surfaces:

- `skills/spec-driven-development/SKILL.md`
- `skills/spec-registry-manager/SKILL.md`
- `skills/test-registry-manager/SKILL.md`
- `skills/issue-log-manager/SKILL.md`
- `skills/local-infra-registry-governance/SKILL.md`
- `skills/shared-governance/SKILL.md`

## Required Manual Sections

Keep the manual concise enough to read before the skill file, but complete enough to use on its own.

Required sections:

1. Title and operational purpose
2. Quick start / when to use
3. Routing decision tree
4. Downstream skill map
5. Walkthroughs for common requests
6. Output interpretation
7. Responsible AI operator checks
8. FAQ
9. Evidence and claim boundary
10. Maintenance pointer back to this guide

## Content Rules

- Describe `spec-master` as a front-door router, not a second SDD workflow.
- Route by authority surface: branch spec, registry, tests, issue log, runtime, shared governance.
- Keep `review.md` as readiness authority.
- Do not describe `SPECS.md` as a task board.
- Do not describe `NEXT_STEPS.md` as immutable truth.
- Do not describe `RTM.md` as readiness authority.
- Do not describe local runtime allocation as spec registry state.
- Do not imply that this workspace has a product runtime or live UI evidence.
- Use conservative evidence language when discussing downstream artifacts.
- Include Responsible AI operator checks: before routing, confirm human owner resolution needs, sensitive runtime / secret / personal data risk, unresolved issue status, and evidence freshness; after routing, record downstream owner and do not claim readiness, compliance, fairness, or safety from routing alone.

## Manual Guidance

The manual should walk through common operator prompts such as:

- create a new spec
- resume an existing spec
- update `TESTS.md`
- reconcile `SPECS.md`
- record an unresolved improvement
- allocate or reuse local runtime

For each walkthrough, show:

- the trigger phrase or intent
- the surface owner
- the file or artifact to inspect first
- the expected next handoff

## Update Checklist

Before finishing an update:

- [ ] The walkthroughs match `skills/spec-master/SKILL.md`.
- [ ] The manual does not claim runtime evidence or readiness.
- [ ] The manual explains how to choose the downstream skill.
- [ ] The manual includes Responsible AI operator checks with explicit requirement-to-action wording.
- [ ] The manual exposes an `EN / 繁中` switch and keeps both languages aligned.
- [ ] The manual can be shipped with `skills/spec-master/` without depending on workspace docs.

## Verification

Use a text check after edits:

```bash
rg -n "production-ready|validated in live demo|fully integrated|guarantees no conflicts" skills/spec-master/manual.html
```

Any match should be reviewed and either removed or backed by explicit consuming-repo evidence.
