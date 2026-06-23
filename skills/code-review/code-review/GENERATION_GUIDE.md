# Code Review Family Generation Guide

This guide defines how to maintain `skills/code-review/README.md` and `skills/code-review/index.html` as the packageable explanation and presentation surface for the Code Review family.

## Purpose

The family docs must serve three audiences:

- **Agent operators** who need to know when to invoke the family.
- **Engineering leads** who need a concise explanation of the review model.
- **Packagers / maintainers** who need a stable explanation to ship with the skill bundle.

The content should combine:

- review-oriented operational guidance
- value-proposition framing
- Amazon backwards press / FAQ framing
- explicit evidence and claim boundaries
- concrete subskill rationale and a three-part value proposition framed for CEO, CIO, and DevSecOps readers
- first-principles framing for agentic AI behavior change, executive value/risk by role, and concrete solution mechanics
- explicit team-owned workflow rationale: coding agents change quickly, differ by vendor, and behave partly as black boxes, so teams need their own inspectable review workflow for retrospection and improvement
- explicit Scrum Team mapping and Agile Manifesto mapping so the family is explained as a working system, not only as a product pitch
- explicit SDD / TDD / DDD / test management / refactor mapping so the page explains business value and the concrete operating mechanism behind each practice
- explicit Responsible AI requirements-to-solution mapping, translating NIST AI RMF / OECD AI Principles / ISO/IEC 42001 language into review evidence, human oversight, explainable findings, accountability, security, privacy, fairness, and auditability controls
- a controlled glossary / reference layer for dense terminology so first-use terms can link to authoritative explanations instead of relying on reader memory
- explicit usage and non-usage guidance so adopters know when `code-review` is the front door and when to go directly to a sibling helper
- a short section that states what gets worse if sibling helpers are merged, so the split has a concrete operational cost argument
- an outcome-signal section that names the observable effects of the family working well

## Canonical Locations

Maintain the packageable explanation in:

- `skills/code-review/README.md`

Maintain the update contract in:

- `skills/code-review/GENERATION_GUIDE.md`

Maintain the shareable HTML presentation in:

- `skills/code-review/index.html`

Do not make workspace `docs/manual/**` or `docs/review/**` the only authoritative copy. They may summarize or render this content, but the packageable source belongs with `skills/code-review/`.

## Inputs To Read Before Updating

Read these first:

- `skills/code-review/SKILL.md`
- `skills/code-review/references/cli-commands.md`
- `skills/code-review/references/usage-guide.md`
- `skills/code-review/references/configuration.md`
- `skills/code-review/references/output-examples.md`
- `skills/code-review/references/local-state-version-control.md`

Read these when the README mentions sibling skills or global-skill packaging:

- `skills/spec-driven-development/SKILL.md`
- `skills/spec-master/SKILL.md`
- `skills/skill-creator/SKILL.md`

Read these when the HTML mentions evidence, claim caps, or generated docs:

- `docs/EVIDENCE_METADATA_CONTRACT.md`
- `docs/DEMO_RISK_WARNING_TAXONOMY.md`
- `docs/REVIEW_GENERATION_GUIDE.md`

> The cross-skill (`skills/...`) and workspace (`docs/...`) inputs above are **optional external context**, not part of the shipped `skills/code-review/` bundle. They are present when this skill is edited inside the full skill-home repo. When the package is shipped standalone and those paths are absent, do not block the update — rely on the in-skill inputs (`SKILL.md` + `references/`) and keep claims conservative. The README/HTML must remain accurate from the in-skill inputs alone.

## Required README Sections

Keep the README short enough to be read before the skill file, but complete enough to ship alone.

Required sections:

1. Title and packageable purpose
2. One-line value proposition
3. Problem statement for fragmented reviews
4. Family members table
5. Supporting tooling table
6. Operating model and routing examples
7. Amazon backwards press release
8. FAQ
9. Evidence and claim boundary
10. Maintenance pointer back to this guide

## Content Rules

- Describe `code-review` as static analysis plus bounded-context tooling, not a runtime gate.
- Keep `review.md` and consuming-repo artifacts as the authority for readiness.
- Treat `test-quality-reviewer`, `code-refactoring-advisor`, `test-design-generator`, `security-risk-reviewer`, and `sonarqube-bridge` as sibling review helpers.
- Treat `capability-mapper` and `code-summarizer` as supporting tooling, not core review members.
- Include the Ponytail / YAGNI minimality boundary from `SKILL.md` / `README.md`: it is advisory design and implementation pressure, not a Phase 5 verdict source; it must remain architecture/platform agnostic, and native platform features require portable behavior or an explicit adapter, guard, and fallback.
- Ground the value proposition in first principles: state how agentic AI changes review behavior, then explain the risk and value for CEO, CIO, and DevSecOps, and finally name the concrete mechanism that the family uses to solve it.
- Explain why the team should own its review workflow instead of outsourcing process truth to a coding-agent vendor: agents vary, model behavior changes, and black-box decisions need a local review contract, evidence trail, and retrospective surface to improve safely.
- Include a Scrum Team mapping and an Agile Manifesto mapping that explain how the family strengthens review feedback loops, decision quality, and evidence discipline in an agentic team.
- Include an SDD / TDD / DDD / test management / refactor mapping that states the business payoff, the operating mechanism, and the cost avoided when the practice is done badly.
- Do not describe graph output as proof of production readiness.
- Do not imply that the package replaces human review judgment.
- Use conservative claim language when discussing generated HTML or downstream artifacts.
- For each sibling helper, state the task boundary in plain language and include why the helper is separate from the main review orchestrator.
- For dense terminology in the README or HTML, add a compact glossary or first-use references section. Prefer official docs, standards, and canonical project pages first; use Wikipedia for broadly established concepts or when a concise neutral overview helps the reader.
- For each high-signal term, define it once in plain language, then keep later mentions short. Do not force the reader to infer meaning from context alone.
- 中文段落避免中英夾雜。優先完整翻譯成繁體中文；若專有名詞需要保留原文，請用 `中文(Original)` 的形式呈現。程式碼名稱、檔名與路徑可維持原樣。
- Avoid generic marketing fluff. Each value statement should connect a behavior change to a role-level risk/value and a concrete solution mechanism.
- When discussing SDD, TDD, DDD, test management, or refactoring, explain them as business risk controls and cost-of-change reducers, not as methodology name-drops.
- Include a Responsible AI section that maps each requirement to concrete review behavior. At minimum cover human oversight, transparency / explainability, accountability, robustness / safety, privacy / data governance, fairness / bias management, and auditability / continual improvement.
- Responsible AI wording must keep Code Review as evidence / diagnosis / handoff input, not as release authority. Do not claim certification, legal compliance, or guaranteed safe AI output.

## Amazon Backwards Press Guidance

Write the press section from a future successful launch perspective, but do not overclaim.

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

- "helps agents analyze code"
- "separates test and security concerns"
- "produces bounded-context handoffs"
- "ships as a packageable skill family"

Avoid claims unless backed by consuming-repo evidence:

- "production-ready"
- "validated in live demo"
- "fully integrated"
- "guarantees correctness"

## FAQ Guidance

Include questions for:

- operators: when to use the family
- maintainers: where to update the docs
- engineering leads: why review, test, and security helpers are separate
- reviewers: how claims are capped by evidence

## Usage Guidance

Include a clear "When To Use" section that states:

- when `code-review` is the correct entry point
- when to skip it and go directly to `test-quality-reviewer`, `code-refactoring-advisor`, `test-design-generator`, or `security-risk-reviewer`
- the practical test for deciding between review intake and a narrow helper task

## HTML Guidance

The HTML page should:

- mirror the README structure
- be self-contained
- include the same claim boundary language
- show the core family and supporting tooling clearly
- use simple, readable styling with no runtime claims
- include a "Three Demand Dimensions" section that states the coordination, evidence, and adoption value in executive language
- include a short "When To Use" section with both use and non-use conditions
- include short "What You Lose If You Merge These" and "Outcome Signals" sections so adopters can judge whether the split is paying off
- include a compact "Key Terms / References" section or inline term links for jargon-heavy passages so readers can verify definitions quickly
- include a "Responsible AI: Requirements to Solutions" section with requirement, Code Review mechanism, and business value columns

## Update Checklist

Before finishing an update:

- [ ] The sibling skill list matches the current `SKILL.md`.
- [ ] The supporting tooling list matches the current `SKILL.md`.
- [ ] The README does not claim readiness or production status.
- [ ] The README includes usage and non-usage guidance for `code-review`.
- [ ] The README states what gets worse if sibling helpers are merged.
- [ ] The README and HTML page explain Ponytail / YAGNI `minimality_check` as advisory context, including the arch/platform-agnostic native-feature boundary.
- [ ] The README names observable outcome signals.
- [ ] The HTML page mirrors the README content.
- [ ] The package can be shipped from `skills/code-review/` without depending on workspace docs.
- [ ] Dense terminology in the README or HTML has a clear glossary or authoritative reference path.
- [ ] Responsible AI requirements map to concrete review-family controls and do not overclaim readiness, compliance, or safety guarantees.

## Suggested Packaging Manifest

When shipping the Code Review family, include:

- `skills/code-review/`
- `skills/test-quality-reviewer/`
- `skills/code-refactoring-advisor/`
- `skills/test-design-generator/`
- `skills/security-risk-reviewer/`
- `skills/sonarqube-bridge/`

Optional supporting tooling:

- `skills/capability-mapper/`
- `skills/code-summarizer/`

## Verification

Use a text check after edits:

```bash
rg -n "production-ready|validated in live demo|fully integrated|guarantees correctness" skills/code-review/README.md skills/code-review/index.html
```

Any match should be reviewed and either removed or backed by explicit consuming-repo evidence.
