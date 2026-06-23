# The Code Review Family

> **Make review deterministic about evidence — not just more verbose about opinions.**
> 讓複核對「證據」是確定性的——而不是對「意見」更囉嗦。

This README is the **canonical source** for the family's landing page
([`index.html`](index.html) is generated from it — edit this first).

`code-review` is the orchestrator; five sibling skills turn the vague instruction "review this
properly" into **deterministic, ranked, actionable findings**. They are the *verify (left-shift)*
layer of [The Spec Master Method](../../methodology.html) — pulled into SDD Phase 4/5 so smells,
weak tests, and security risk are caught **before** the readiness verdict is written.

## Why a family, not one reviewer

A single "review the code" prompt produces opinions that vary run to run, bury the dangerous finding
under style nits, and can't say *what to fix first*. In an agentic team that is expensive: reviews
stop being trustworthy evidence. This family fixes that with two principles:

1. **Deterministic-first, LLM-optional.** Each helper ships a deterministic detector that is the
   **source of truth**, needs no provider, and is safe in CI. An optional `--explain` / LLM pass only
   *calibrates severity* and writes developer-actionable reasoning — it never invents findings.
2. **Risk-based triage.** Findings are ranked (e.g. severity × confidence × blast-radius) so review
   effort goes to the highest-impact issue first. *What to review is judgement, not generation.*

## Family members

| Skill | Question it answers | What it owns |
|---|---|---|
| `code-review` | "What does this code *look like* — structure, dependencies, impact, bounded context?" | The orchestrator + program-graph / GraphRAG static analysis; folds in every sibling's findings. CLI binary (`review-cli-<os>-<arch>`) with an MCP runtime surface. |
| `code-refactoring-advisor` | "What should I *change*, and what test net must exist first?" | Deterministic Fowler smell detection → a **named refactoring move** + the **test safety-net** it requires before the move is safe. |
| `test-quality-reviewer` | "Are these tests *any good* — would a real defect survive them?" | Judges existing tests: assertion roulette, mystery guest, fragile/conditional tests, FIRST violations, test-pyramid inversion. "Green only means it ran." |
| `test-design-generator` | "*What should I test* — what are the real edge cases?" | Generates boundary-value, equivalence-partition, and pairwise cases from a parameter description; recommends an oracle strategy (property-based / metamorphic) when outputs can't be enumerated. |
| `security-risk-reviewer` | "Is this *secure* — where's the injection / secret / weak crypto?" | Deterministic OWASP Top-10 scan, **ranked by risk score** so the dangerous lines surface first. Each finding mapped to OWASP/CWE. |
| `sonarqube-bridge` | "Pull in our *SonarQube* findings and rank them with everything else." | An **adapter, not a scanner**: ingests Sonar findings and enriches each with code-graph blast-radius, business capability, and the project's remediation vocabulary. Never scans, never gates. |

## How they compose

- `code-review` builds the **inventory** ("what exists") — the program graph, capability/requirement
  traceability, bounded context. On its own it answers *structure*, not *quality*.
- The helpers extend that inventory from "what exists" to **"what should improve"**:
  - `code-refactoring-advisor` says *what to change*; `test-quality-reviewer` checks *the net you
    change it against*. They are natural partners.
  - `test-design-generator` is the "what should I test?" complement to `test-quality-reviewer`'s
    "are these tests good?" — where a thin test is flagged, this produces the missing cases.
  - `security-risk-reviewer` makes the orchestrator's prose security guidance **executable** — it
    finds the actual lines and prioritizes them.
  - `sonarqube-bridge` is the connective tissue when the team already runs Sonar: Sonar owns the
    broad SAST and the **blocking Quality Gate**; this family adds Sonar's blind spots (program-graph
    impact, capability traceability, refactoring/test vocabulary) and fuses both into one ranked report.

## Scope boundary (read this)

This family is **static analysis + review evidence**, *not* a runtime readiness authority.

- ✅ Use it to answer: "What's the structure / impact?", "What should improve?", "Are the tests
  effective?", "What's the security risk, ranked?"
- ❌ Do **not** use it alone to answer: "Is the feature live-demo ready?" Authoritative
  `PASS / CONDITIONAL / FAIL` for runtime or live-demo readiness still comes from runtime-backed
  review artifacts (`review.md`). Static green ≠ shipped.

This is the same anti-false-green discipline as the rest of the method: evidence is layered, and a
clean static report is not allowed to masquerade as readiness.

## Relationship to the Spec Master Method

In [the six-phase flow](../../docs/agentic-delivery-methodology.md), this family is **Phase 4/5 left-shift
detection**. `spec-driven-development` runs the lifecycle; when it reaches implementation and review,
it pulls these skills in as *capability-gated inputs* (they don't need to be vendored into every
workspace — once published to the skill home, they're available). `review.md` still owns the verdict;
this family makes that verdict rest on deterministic evidence instead of one-shot opinion.

## 繁中摘要

`code-review` 是協調者，五個 sibling skills 把「好好複核一下」變成**確定性、可排序、可執行**的發現，
是 [Spec Master Method](../../methodology.html) 的**驗證（左移）**層（SDD Phase 4/5）。

兩個核心原則：(1) **deterministic-first、LLM-optional** — 每個 helper 的確定性偵測器是事實來源，
CI 安全、不需 provider；可選的 `--explain` 只校準嚴重度，不會無中生有。(2) **risk-based triage** —
依風險排序，先看最危險的；「要複核什麼」是判斷，不是生成。

家族成員：`code-review`（程式圖／GraphRAG 靜態分析與協調）、`code-refactoring-advisor`（Fowler 異味 →
具名重構手法 + 必要測試安全網）、`test-quality-reviewer`（既有測試夠不夠好、真缺陷會不會存活）、
`test-design-generator`（該測哪些邊界／等價／pairwise 案例）、`security-risk-reviewer`（OWASP Top-10
依風險分數排序）、`sonarqube-bridge`（**adapter 而非 scanner**，融合 Sonar 發現與程式圖 blast-radius）。

**邊界**：這是靜態分析與複核證據，**不是** runtime readiness 權威；live-demo 的
`PASS / CONDITIONAL / FAIL` 仍由 runtime-backed 的 `review.md` 決定。靜態綠燈 ≠ 已交付。

---

*Attribution: this family is original work in this repository. Concept grounding (Fowler refactorings,
FIRST, the test pyramid, OWASP/CWE) is credited in [`../../CREDITS.md`](../../CREDITS.md).*
