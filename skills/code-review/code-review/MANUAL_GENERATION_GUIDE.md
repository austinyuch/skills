# Code Review Family Manual Guide

This guide defines how to maintain `skills/code-review/manual.html` as the packageable operational manual for the Code Review family.

## Purpose

The manual must serve three audiences:

- **Agent operators** who need a step-by-step guide for running review-oriented work.
- **Engineering leads** who want to understand which helper skill to use for each review surface.
- **Packagers / maintainers** who need a stable operational page to ship with the family.

The content should combine:

- user-manual style walk-throughs
- quick start guidance for review workflows
- command / artifact interpretation
- explicit claim boundaries
- a visible `EN / 繁中` language switch

## Canonical Locations

Maintain the operational manual in:

- `skills/code-review/manual.html`

Maintain this update contract in:

- `skills/code-review/MANUAL_GENERATION_GUIDE.md`

Do not make workspace `docs/manual/**` the only authoritative copy. It may summarize or render this content, but the packageable source belongs with `skills/code-review/`.

## Inputs To Read Before Updating

Read these first:

- `skills/code-review/SKILL.md`
- `skills/code-review/README.md`
- `skills/code-review/GENERATION_GUIDE.md`
- `skills/code-review/references/cli-commands.md`
- `skills/code-review/references/usage-guide.md`

Read these when the manual mentions sibling helpers or claim boundaries:

- `skills/test-quality-reviewer/SKILL.md`
- `skills/code-refactoring-advisor/SKILL.md`
- `skills/test-design-generator/SKILL.md`
- `skills/security-risk-reviewer/SKILL.md`
- `skills/sonarqube-bridge/SKILL.md`

Read these when the manual mentions evidence, claim caps, or generated docs:

- `docs/EVIDENCE_METADATA_CONTRACT.md`
- `docs/DEMO_RISK_WARNING_TAXONOMY.md`
- `docs/REVIEW_GENERATION_GUIDE.md`

## Required Manual Sections

Keep the manual concise enough to read before the skill file, but complete enough to use on its own.

Required sections:

1. Title and operational purpose
2. Quick start / when to use
3. Review workflow walkthroughs
4. Helper skill map
5. CLI / artifact interpretation
6. Responsible AI operator checks
7. FAQ
8. Evidence and claim boundary
9. Maintenance pointer back to this guide

## Content Rules

- Describe `code-review` as static analysis plus bounded-context tooling, not a runtime gate.
- Keep `review.md` and consuming-repo artifacts as the authority for readiness.
- Treat sibling review helpers as step-specific tools rather than a monolithic workflow.
- Treat `capability-mapper` and `code-summarizer` as supporting tooling.
- Include the Ponytail / YAGNI operator boundary from `SKILL.md`: `code-refactoring-advisor` may emit advisory `minimality_check`, but it is not a Phase 5 verdict source; native platform recommendations must remain architecture/platform agnostic or be isolated behind an explicit adapter, guard, and fallback.
- Do not describe graph output as proof of production readiness.
- Do not imply that the package replaces human review judgment.
- Use conservative claim language when discussing downstream artifacts.
- Include Responsible AI operator checks: each finding should have explainable risk, evidence source, affected file / behavior, and next owner; handoff should check secrets, privacy-sensitive data, auth / tenant-boundary risk, stale scanner output, and unsupported readiness claims.

## Manual Guidance

The manual should walk through common operator prompts such as:

- analyze a file
- review an entire project
- judge existing tests
- suggest refactor moves
- run offline security preflight
- ingest Sonar findings

For each walkthrough, show:

- the trigger phrase or intent
- the surface owner
- the file or artifact to inspect first
- the expected next handoff

## Update Checklist

Before finishing an update:

- [ ] The walkthroughs match `skills/code-review/SKILL.md`.
- [ ] The manual does not claim readiness or production status.
- [ ] The manual explains how to choose the helper skill.
- [ ] The manual explains Ponytail / YAGNI `minimality_check`, the Phase 5 authority boundary, and the arch/platform-agnostic guardrail.
- [ ] The manual includes Responsible AI checks for findings acceptance and handoff hygiene.
- [ ] The manual exposes an `EN / 繁中` switch and keeps both languages aligned.
- [ ] The manual can be shipped with `skills/code-review/` without depending on workspace docs.

## Verification

Use a text check after edits:

```bash
rg -n "production-ready|validated in live demo|fully integrated|guarantees correctness" skills/code-review/manual.html
```

Any match should be reviewed and either removed or backed by explicit consuming-repo evidence.
