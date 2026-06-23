# Credits & Attribution / 致謝與出處

This collection stands on the work of others. Where a skill was derived from, inspired by, or
references an upstream project, that source is credited below. If you find an attribution that is
missing or wrong, please open an issue — corrections are welcome.

本合集建立在許多前人的成果之上。凡是衍生自、啟發自或引用了上游專案的 skill，其來源都列於下方。
若發現遺漏或錯誤的出處，歡迎開 issue 指正。

> This repository (the original skills, the methodology, and the glue) is licensed **MIT** — see
> [`LICENSE`](./LICENSE). Individual upstream components retain **their own licenses**, reproduced
> in each skill's `LICENSE.txt`. The MIT license of this repo does **not** relicense those components.

---

## 1. Anthropic skills — removed from this collection

Skills derived from **Anthropic's `anthropics/skills`** (Apache-2.0) and Anthropic's proprietary
Claude-bundled document skills have been **removed** from this repository to keep it cleanly
self-owned and free of third-party redistribution constraints.

Removed (Apache-2.0, `anthropics/skills`): `algorithmic-art`, `canvas-design`,
`frontend-design-skill`, `theme-factory`, `web-artifacts-builder`, `slack-gif-creator`,
`internal-comms`, `brand-guidelines`, `mcp-builder`, `claude-api`, `skill-creator`, `webapp-testing`.

Removed (proprietary, `© 2025 Anthropic, PBC`): `docx`, `pdf`, `pptx`, `xlsx`.

> If you want any of these, install them directly from
> [`anthropics/skills`](https://github.com/anthropics/skills) under their original licenses.
> `brand-guidelines-naelt` (kept) is an original organization-specific work; its structure was
> historically informed by Anthropic's `brand-guidelines` but ships no Anthropic-licensed content.

## 3. Claude Code ecosystem — community resources

Patterns, conventions, and skill-authoring ideas across this collection were informed by the wider
**Claude Code** community, including the **"Everything Claude Code"** community knowledge resource
and the broader collection of Claude Code skills, hooks, and agent recipes shared publicly. These
shaped *how* skills are structured (SKILL.md frontmatter, references/, evals/, install scripts)
rather than providing copied content.

## 4. Methodology & concept sources (The Spec Master Method)

The `spec-master` + `spec-driven-development` family operationalizes established engineering
practice. Credit to the originators:

| Concept | Source / Author | Used in |
|---|---|---|
| **Spec-driven development workflow** | **AWS Kiro** (<https://kiro.dev>) — `spec-driven-development` is inspired by Kiro's requirements → design → tasks spec flow | `spec-driven-development` |
| **YAGNI "Ponytail" Ladder** | **Ponytail** by Dietrich Gebert (<https://github.com/DietrichGebert/ponytail>), **MIT License** — adapted as the minimal-implementation ladder | `spec-driven-development/references/ponytail-yagni-ladder.md` |
| **Scrum** | The **Scrum Guide**, Ken Schwaber & Jeff Sutherland (<https://scrumguides.org>) | family Scrum-role mapping |
| **Agile values** | **Manifesto for Agile Software Development** (<https://agilemanifesto.org>) | family Agile mapping |
| **Test-Driven Development** | Kent Beck — *Test-Driven Development: By Example* | `tdd-workflow`, SDD Phase 4 |
| **Domain-Driven Design** | Eric Evans — *Domain-Driven Design* | SDD Phase 2 (bounded contexts) |
| **Refactoring & Test Pyramid** | Martin Fowler (<https://martinfowler.com>) | `code-refactoring-advisor`, test strategy |
| **EARS requirement syntax** | Alistair Mavin (<https://alistairmavin.com/ears/>) | SDD Phase 1 acceptance criteria |
| **OWASP Top 10 / CWE** | OWASP Foundation (<https://owasp.org>) | `security-risk-reviewer` |
| **Responsible AI** | NIST AI RMF (<https://www.nist.gov/itl/ai-risk-management-framework>), OECD AI Principles (<https://oecd.ai/en/ai-principles>), ISO/IEC 42001 (<https://www.iso.org/standard/42001>) | family Responsible-AI alignment |

---

## How attribution is kept in-tree

- **Concept sources** are cited inline where used (e.g. the Ponytail header in
  `ponytail-yagni-ladder.md`, the References sections of the family `index.html` pages).
- This file is the **single index** that ties those attributions together.
