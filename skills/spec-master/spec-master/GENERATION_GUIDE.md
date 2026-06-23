# Spec Master Family Generation Guide

This guide defines how to maintain `skills/spec-master/README.md` and `skills/spec-master/index.html` as the packageable explanation, value proposition, and presentation surface for the Spec Master family.

## Purpose

The README must serve three audiences:

- **Agent operators** who need to know when to invoke the family.
- **Engineering leads** who need to understand why the governance model exists.
- **Packagers / maintainers** who need a stable explanation to ship with the family skills.

It should combine:

- user-manual style operating guidance
- project-review style value proposition
- Amazon backwards press / FAQ framing
- explicit evidence and claim boundaries
- concrete subskill rationale: each row should say what pain it solves and why it is not merged into a neighboring skill
- a three-part value proposition framed for CEO, CIO, and DevSecOps readers so the page reads like an adoption brief rather than a concept note
- first-principles framing for agentic AI behavior change, executive value/risk by role, and concrete solution mechanics
- explicit team-owned workflow rationale: coding agents change quickly, differ by vendor, and behave partly as black boxes, so teams need their own inspectable workflow for retrospection and improvement
- explicit Scrum Team mapping and Agile Manifesto mapping so the family is explained as a working system, not only as a product pitch
- explicit SDD / TDD / DDD / test governance / refactor mapping so the page explains business value and the concrete operating mechanism behind each practice
- explicit Responsible AI requirements-to-solution mapping, grounded in NIST AI RMF / OECD AI Principles / ISO/IEC 42001 language but translated into this family's routing, ownership, claim-boundary, evidence, privacy, safety, fairness, and auditability controls
- a controlled glossary / reference layer for dense terminology so first-use terms can link to authoritative explanations instead of relying on reader memory
- explicit usage and non-usage guidance so adopters know when to route to `spec-master` and when to go directly to a downstream skill
- a short section that states what gets worse if two neighboring skills are merged, so the split has an operational cost argument
- an outcome-signal section that names the observable effects of the family working well

## Canonical Location

Maintain the deliverable in:

- `skills/spec-master/README.md`

Maintain the shareable HTML presentation in:

- `skills/spec-master/index.html`

Maintain this update contract in:

- `skills/spec-master/GENERATION_GUIDE.md`

Do not make `docs/manual/**` or `docs/review/**` the only authoritative copy. Those workspace docs may summarize or render this content, but the packageable source belongs with `skills/spec-master/`.

## Inputs To Read Before Updating

Read these first:

- `skills/spec-master/SKILL.md`
- `skills/spec-master/references/routing-matrix.md`
- `skills/spec-driven-development/SKILL.md`
- `skills/spec-registry-manager/SKILL.md`
- `skills/test-registry-manager/SKILL.md`
- `skills/issue-log-manager/SKILL.md`
- `skills/local-infra-registry-governance/SKILL.md`
- `skills/shared-governance/SKILL.md`

Read these when the README mentions stakeholder-facing evidence or generated docs:

- `docs/MANUAL_GENERATION_GUIDE.md`
- `docs/REVIEW_GENERATION_GUIDE.md`
- `docs/EVIDENCE_METADATA_CONTRACT.md`
- `docs/DEMO_RISK_WARNING_TAXONOMY.md`

Read these when packaging, release, or setup wording changes:

- `README.md`
- `SKILLS.md`
- `AGENT_SKILLS_README.md`
- `AGENT_SKILLS_SETUP_GUIDE.md`

## Required README Sections

Keep the README short enough to be read before the skill files, but complete enough to ship alone.

Required sections:

1. Title and packageable purpose
2. One-line value proposition
3. Problem statement for large projects
4. Family members table
5. Operating model and routing examples
6. Amazon backwards press release
7. FAQ
8. Evidence and claim boundary
9. Maintenance pointer back to this guide

## Content Rules

- Describe `spec-master` as a front-door router, not a second SDD workflow.
- Route by authority surface: branch spec, registry, tests, issue log, runtime, shared governance.
- Explain the business reason for each downstream skill in the family table. The goal is to make adoption easier by showing why the split reduces drift, stale evidence, or ownership confusion.
- Ground the value proposition in first principles: state how agentic AI changes work behavior, then explain the risk and value for CEO, CIO, and DevSecOps, and finally name the concrete mechanism that the family uses to solve it.
- Explain why the team should own its workflow instead of outsourcing process truth to a coding-agent vendor: agents vary, model behavior changes, and black-box decisions need a local workflow, evidence trail, and retrospective surface to improve safely.
- Include a Scrum Team mapping and an Agile Manifesto mapping that explain how the family strengthens boundary management, feedback loops, and evidence discipline in an agentic team.
- Include an SDD / TDD / DDD / test governance / refactor mapping that states the business payoff, the operating mechanism, and the cost avoided when the practice is done badly.
- For each downstream skill, state the specific task boundary in plain language. Include at least one "why separate" explanation so the reader can see the operational cost saved by the split.
- Keep `review.md` as readiness authority.
- Do not describe `SPECS.md` as a task board.
- Do not describe `NEXT_STEPS.md` as immutable truth.
- Do not describe `RTM.md` as readiness authority.
- Do not describe local runtime allocation as spec registry state.
- Do not imply that this workspace has a product runtime or live UI evidence.
- Use conservative evidence language when discussing generated manuals or review artifacts.
- For dense terminology in the README or HTML, add a compact glossary or first-use references section. Prefer official docs, standards, and canonical project pages first; use Wikipedia for broadly established concepts or when a concise neutral overview helps the reader.
- For each high-signal term, define it once in plain language, then keep later mentions short. Do not force the reader to infer meaning from context alone.
- 中文段落避免中英夾雜。優先完整翻譯成繁體中文；若專有名詞需要保留原文，請用 `中文(Original)` 的形式呈現。程式碼名稱、檔名與路徑可維持原樣。
- Avoid generic marketing fluff. Each value statement should connect a behavior change to a role-level risk/value and a concrete solution mechanism.
- When discussing SDD, TDD, DDD, test governance, or refactoring, explain them as business risk controls and cost-of-change reducers, not as methodology name-drops.
- Include a Responsible AI section that states the requirement and the concrete family solution in the same row. At minimum cover human oversight, accountability, transparency / explainability, robustness / safety, privacy / data governance, fairness / bias management, and auditability / continual improvement.
- Responsible AI wording must not imply certification or legal compliance. It may say "aligns with", "supports", or "operationalizes"; do not say "complies with ISO/IEC 42001" unless there is separate audit evidence.

## Amazon Backwards Press Guidance

The press section should be written from the future successful launch perspective, but must not overclaim runtime readiness.

Use this structure:

```text
Headline: [Product] introduces [capability] for [audience]

[City], [Date] - [Product/team] today introduced [product],
which helps [audience] achieve [outcome].

[Quote explaining why the problem matters]

[Problem paragraph]

[Solution paragraph]

[Feature paragraph]

[Availability / packaging paragraph]
```

Acceptable claims:

- "helps agents route work"
- "separates authority surfaces"
- "reduces stale summaries and false confidence"
- "ships as a packageable skill family"

Avoid claims unless backed by consuming-repo evidence:

- "production-ready"
- "validated in live demo"
- "fully integrated"
- "guarantees no conflicts"

## FAQ Guidance

Include questions for:

- operators: when to use the family
- maintainers: where to update the docs
- engineering leads: why the family is not a single monolithic workflow
- governance reviewers: how evidence and readiness claims are capped
- adopters: why the split skills save coordination cost on real repositories

## Usage Guidance

Include a clear "When To Use" section that states:

- when `spec-master` is the correct entry point
- when the user should skip `spec-master` and go directly to a downstream skill
- the practical test for deciding between routing work and doing the work

## HTML Guidance

The HTML page should include a "Three Demand Dimensions" section that states the coordination, authority, and adoption value in executive language.
The HTML page should include a "Responsible AI: Requirements to Solutions" section mapping each responsible AI requirement to the family mechanism and business value.
The HTML page should also include a short "When To Use" section with both use and non-use conditions.
The HTML page should also include a short "What You Lose If You Merge These" section and an "Outcome Signals" section so adopters can judge whether the split is paying off.
The HTML page should include a compact "Key Terms / References" section or inline term links for jargon-heavy passages. Use authoritative links on first mention so readers can verify definitions quickly.

## Update Checklist

Before finishing an update:

- [ ] The downstream family list matches actual skill directories.
- [ ] Routing examples match `skills/spec-master/SKILL.md`.
- [ ] Authority boundaries match downstream `SKILL.md` files.
- [ ] The family table explains why each subskill is separate.
- [ ] The README includes usage and non-usage guidance for `spec-master`.
- [ ] The README states what gets worse if adjacent skills are merged.
- [ ] The README names observable outcome signals.
- [ ] The README does not claim product runtime evidence.
- [ ] The README can be packaged with `skills/spec-master/` without depending on `docs/`.
- [ ] If a generated docs page summarizes this README, it links back to this source.
- [ ] Dense terminology in the README or HTML has a clear glossary or authoritative reference path.
- [ ] Responsible AI requirements are mapped to concrete Spec Master controls, not listed as generic principles.
- [ ] Responsible AI references are present and do not overclaim compliance or certification.

## Suggested Packaging Manifest

When shipping the Spec Master family, include:

- `skills/spec-master/`
- `skills/spec-driven-development/`
- `skills/spec-registry-manager/`
- `skills/test-registry-manager/`
- `skills/issue-log-manager/`
- `skills/local-infra-registry-governance/`
- `skills/shared-governance/`

Optional companion skills may be included when the target environment uses them:

- `skills/project-review-skill/`
- `skills/user-manual-skill/`
- `skills/agentic-scrum-governance/`
- `skills/scrum-master-skill/`
- `skills/scrum-developer-skill/`

## Verification

Use a text check after edits:

```bash
rg -n "production-ready|validated in live demo|fully integrated|guarantees no conflicts" skills/spec-master/README.md
```

Any match should be reviewed and either removed or backed by explicit consuming-repo evidence.
