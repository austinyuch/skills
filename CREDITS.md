# Credits & Attribution / 致謝與出處

This collection stands on the work of others. Where a skill was derived from, inspired by, or
references an upstream project, that source is credited below. If you find an attribution that is
missing or wrong, please open an issue — corrections are welcome.

本合集建立在許多前人的成果之上。凡是衍生自、啟發自或引用了上游專案的 skill，其來源都列於下方。
若發現遺漏或錯誤的出處，歡迎開 issue 指正。

> This repository (the original skills, the methodology, and the glue) is licensed **MIT** — see
> [`LICENSE`](./LICENSE). Individual upstream components retain **their own licenses**, reproduced
> in each skill's `LICENSE.txt`. The MIT license of this repo does **not** relicense those components.

## ⭐ Recommended upstream sources

If you want skills we reference, removed, or built upon, get them from the original authors:

| Source | GitHub / Link | License | What to get there |
|---|---|---|---|
| **Anthropic Agent Skills** | <https://github.com/anthropics/skills> | Apache-2.0 + proprietary | `docx`, `pdf`, `pptx`, `xlsx`, `canvas-design`, `mcp-builder`, `skill-creator`, `brand-guidelines`, … (removed from this repo) |
| **Everything Claude Code** | <https://github.com/affaan-m/everything-claude-code> | MIT | instinct/continuous-learning system, agents, rules, memory hooks |
| **Ponytail** | <https://github.com/DietrichGebert/ponytail> | MIT | the YAGNI "ladder" minimal-implementation discipline |
| **gstack** (Garry Tan) | <https://github.com/garrytan/gstack> | MIT | CEO/eng review depth, cognitive patterns (`plan-ceo-review`, `plan-eng-review`, `office-hours`, ETHOS) |
| **mattpocock/skills** | <https://github.com/mattpocock/skills> | MIT | requirement "grilling", `codebase-design`, `domain-modeling` |
| **AWS Kiro** | <https://kiro.dev> · <https://github.com/kirodotdev> | product | the spec-driven workflow that inspired `spec-driven-development` |

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

## 3. Everything Claude Code (ECC) — MIT

The continuous-learning skills derive from **Everything Claude Code** by Affaan Mustafa
(<https://github.com/affaan-m/everything-claude-code>), used under the **MIT License**
("OSS stays free. This repo is MIT-licensed forever.").

| Skill (in this repo) | Source concept |
|---|---|
| `continuous-learning` | session-pattern extraction → learned skills |
| `continuous-learning-v2` | instinct-based learning with confidence scoring → evolve into skills |

Broader skill-authoring conventions (SKILL.md frontmatter, `references/`, `evals/`, install scripts)
across this collection were also informed by the wider Claude Code community.

## 4. Methodology & concept sources (The Spec Master Method)

The `spec-master` + `spec-driven-development` family operationalizes established engineering
practice. Credit to the originators:

| Concept | Source / Author | Used in |
|---|---|---|
| **Spec-driven development workflow** | **AWS Kiro** (<https://kiro.dev>) — `spec-driven-development` is inspired by Kiro's requirements → design → tasks spec flow | `spec-driven-development` |
| **YAGNI "Ponytail" Ladder** | **Ponytail** by Dietrich Gebert (<https://github.com/DietrichGebert/ponytail>), **MIT License** — adapted as the minimal-implementation ladder | `spec-driven-development/references/ponytail-yagni-ladder.md` |
| **CEO/eng review depth & cognitive patterns** | **gstack** by Garry Tan (<https://github.com/garrytan/gstack>), **MIT License** — `plan-ceo-review`, `plan-eng-review`, `office-hours`, `ETHOS` (selected subset) | `spec-master/references/requirement-interview-depth.md`, `spec-driven-development/references/architecture-design-depth.md`, `project-review-skill` |
| **Requirement "grilling" & design modeling** | **mattpocock/skills** (<https://github.com/mattpocock/skills>), **MIT License** — `grill-me`/`grilling`, `codebase-design`, `domain-modeling` | `spec-master` & `spec-driven-development` interview/design-depth references |
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
