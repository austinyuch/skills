# Spec Master + Spec-Driven Development

> **One front door for routing, one backbone for delivery — kept as two skills on purpose.**
> 一個路由前門、一個交付主幹——刻意維持成兩個技能。

This is the **single, merged brief** for the two core skills of the Spec Master family. It is the
**canonical source** for [`index.html`](index.html) (generated from this — edit markdown first), and it
replaces the two former per-skill landing pages.

- **`spec-master/`** — the **front-door router** and improvement classifier. Its only job is to decide
  *who should own this* before any file is edited.
- **`spec-driven-development/`** — the **6-phase delivery backbone**. It runs the lifecycle from vague
  intent to traceable, reviewable change.

For the wider 14-skill methodology these two anchor, see [The Spec Master Method](../../methodology.html).

## Why two skills, not one

It is tempting to merge the router into the workflow. Don't — the merge raises intake cost, because
then *every ambiguous request drags a full lifecycle with it*. Keeping them separate means:

- `spec-master` stays cheap to enter: classify the request, decide the owner, hand off. No artifacts
  are written just to find out where work belongs.
- `spec-driven-development` stays a real lifecycle: it can preserve traceability across phases without
  pretending to also be a router.

They are **one family, two responsibilities**: decide ownership first, then deliver.

## `spec-master` — route by authority surface

When a request touches specs, registries, tests, issue-holding, runtime, or shared governance and the
owner is unclear, enter here first. Route by *authority surface*, not by whichever file was mentioned
first.

| The request is about… | Route to |
|---|---|
| New feature / complex fix / design / tasks / review / optimization | `spec-driven-development` |
| `SPECS.md` lifecycle, CR summary, registry wording | `spec-registry-manager` |
| `TESTS.md` rows, stale evidence, traceability | `test-registry-manager` |
| Unresolved improvement with no safe owner yet | `issue-log-manager` |
| Local dev / UAT / E2E runtime allocation | `local-infra-registry-governance` |
| Cross-lane git/worktree ownership & writeback safety | `shared-governance` |

`spec-master` also classifies continuous-improvement requests (review rejections, retro findings, tech
debt, known issues, CR follow-ups): does this *continue an active spec*, become a *CR against a
completed spec*, go to the *issue log*, or justify a *new spec*? Deciding that wrong is what creates
fragmented, half-owned governance.

## `spec-driven-development` — the six phases

| Phase | What happens | Practice in play |
|---|---|---|
| 1 · Requirements | EARS-style acceptance criteria; YAGNI Rung 1 filters speculative needs | SDD intake |
| 2 · Design & contracts | Bounded contexts, contracts, data models, impact analysis; Rungs 2–4 justify dependencies | DDD |
| 3 · Tasks & traceability | Mirror the authority boundary; plan closeout for TESTS.md, RTM, SPECS, CR, issue disposition | planning |
| 4 · Implementation | Red → green → refactor with evidence reports; folder-level TESTS.md before rollups; Rungs 5–6 keep it minimal | TDD |
| 5 · Review verdict | `review.md` owns readiness; left-shift detection (code-review family) flags smells, weak tests, security risk; over-engineering check | review |
| 6 · Optimization | Convert repeated findings into bounded improvements or promoted process changes | retro |

## The one rule that prevents false-green

> **Evidence flows one way:** `ISSUE_LOG → spec artifacts & reports → folder-level TESTS.md →
> workspace rollup → RTM.md → SPECS.md`. Derived summaries (`SPECS.md`, `RTM.md`) never overwrite the
> upstream artifacts they summarize, and `review.md` — not a green dashboard — owns the readiness verdict.

This is the spine of the whole family: layered evidence, with a clean static or summary view never
allowed to masquerade as runtime readiness.

## Scrum, DevSecOps & Responsible AI (condensed)

- **Scrum** — strengthens boundary management, not ceremonies: PO routes ownership before the backlog
  hardens; SM holds routing discipline; Developers execute via the right downstream skill so
  implementation never contaminates governance.
- **DevSecOps** — test evidence, review verdict, and demo readiness live on separate authority
  surfaces, so mock-heavy green CI can't pose as production-ready; security review is left-shifted into
  Phase 5.
- **Responsible AI** — human oversight via phase gates, accountability via separate owners,
  transparency via authority-surface routing. Aligns with NIST AI RMF, OECD AI Principles, ISO/IEC 42001.

## The rest of the family

`spec-registry-manager` (SPECS.md lifecycle), `test-registry-manager` (TESTS.md catalog & freshness),
`issue-log-manager` (holding surface for unresolved work), `local-infra-registry-governance` (dev/UAT/E2E
runtime allocation), and `shared-governance` (git/worktree & ownership guardrails) each own one authority
surface so stale evidence, planning gaps, and runtime state never blur together. See
[the methodology](../../methodology.html) for the full 14-skill picture.

## 繁中摘要

這是 Spec Master 家族兩個核心技能的**單一合併說明**，也是 [`index.html`](index.html) 的**正本來源**
（先改 markdown），取代原本兩份各自的 landing page。

- **`spec-master`** 是**前門路由器**與改善項分類器：在動任何檔案前先決定*誰該擁有這件事*。依**權威面**
  路由，而不是依「哪個檔案先被提到」。
- **`spec-driven-development`** 是**六階段交付主幹**：需求 → 設計 → 任務 → 實作 → 複核 → 優化。

**為何分成兩個**：把 router 併進 workflow 會抬高 intake 成本，因為每個含糊請求都會拖著完整生命週期。
分開後，`spec-master` 進入成本低（分類、決定 owner、交棒），`spec-driven-development` 維持真正的生命週期
與跨階段追溯。一個家族、兩種責任：先決定歸屬，再交付。

**防止假綠燈的核心規則**：證據單向流動 `ISSUE_LOG → spec 工件 → folder-level TESTS.md → workspace
rollup → RTM.md → SPECS.md`；衍生摘要永不覆寫上游，`review.md`（而非綠色儀表板）擁有 readiness。

## Attribution

`spec-driven-development` is **inspired by [AWS Kiro](https://kiro.dev)** (requirements → design → tasks).
The YAGNI ladder adapts **[Ponytail](https://github.com/DietrichGebert/ponytail)** (MIT). Review-depth and
CEO/eng cognitive patterns adapt **[gstack](https://github.com/garrytan/gstack)** (MIT) and
**[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT). Full attribution:
[`../../CREDITS.md`](../../CREDITS.md).
