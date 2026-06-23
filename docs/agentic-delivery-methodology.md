# Porting DevSecOps + Scrum + TDD into Agentic Workflows

### How a 14-skill open-source family — *The Spec Master Method* — keeps coding agents honest

> **TL;DR** — Coding agents made *producing* code cheap. They did not make *coordinating* it cheap. The bottleneck moved from typing to deciding ownership, keeping evidence fresh, and stopping a green-looking file from lying about readiness. The Spec Master Method ports five proven engineering practices — **SDD, TDD, DDD, test management, and refactoring** — into a governed, inspectable agentic workflow built from 14 composable, open-source skills.

*A 繁體中文版本在本文末尾 → [中文版](#中文版).*

---

## 1. The problem agents created

In a classic team, work moves through people in a roughly linear handoff: a PM writes a story, a dev builds it, a reviewer checks it, CI gates it. Each handoff is slow enough that a human re-reads the context and notices when something is off.

Agentic teams break that assumption. An agent can produce text, mutate files, call tools, and hand work to *another* agent faster than any human can re-establish context. So the scarce resource is no longer output — it's **decision quality and boundary control**:

- **Ownership drift** — two agents route the same request to two different workflows, and the team pays the clarification cost twice.
- **Authority collisions** — `SPECS.md`, `NEXT_STEPS.md`, `RTM.md`, `TESTS.md`, and `review.md` start competing to be "the truth," so handoffs get fragile.
- **False green** — a mock-heavy test stays green while the underlying evidence is stale, and confidence rises faster than signal.
- **Runtime leakage** — ports, local stacks, and demo state leak into spec files and start masquerading as authority.

The instinct to "just let the agent figure it out" is exactly what produces these failures at scale. The fix is not *less* process — it's process that gets **stricter about ownership, evidence, and boundaries**, while staying cheap enough that agents can actually follow it.

## 2. The thesis: port, don't abandon

SDD, TDD, DDD, test management, and refactoring already solve these problems — for humans. The method's claim is that each one keeps its job in an agentic team, but needs an explicit **owner skill** so an agent always knows *who* is responsible for *what*.

| Classic practice | The job it still does | Owner skill in the family |
|---|---|---|
| **Spec-Driven Development (SDD)** | Turn vague intent into traceable delivery | `spec-driven-development` |
| **Test-Driven Development (TDD)** | Pin behavior before code changes; make refactoring safe | `tdd-workflow` + `test-design-generator` |
| **Domain-Driven Design (DDD)** | Align boundaries with business language | SDD Phase 2 (bounded contexts & contracts) |
| **Test Management** | Turn green CI into auditable risk evidence | `test-registry-manager` + `test-quality-reviewer` |
| **Refactoring** | Lower cost of change — *after* behavior is protected | `code-refactoring-advisor` |
| **Security left-shift** | Catch injection/secrets/weak crypto in review | `security-risk-reviewer` + `code-review` |

These are not separate slogans. **SDD decides what to build, TDD proves it safely, DDD keeps the boundary language honest, test management keeps the evidence fresh, and refactoring stops cost-of-change from compounding.**

> **Lineage.** `spec-driven-development` is inspired by [AWS Kiro](https://kiro.dev)'s requirements → design → tasks spec flow; the YAGNI ladder adapts [Ponytail](https://github.com/DietrichGebert/ponytail) (MIT). Full attribution is in [`CREDITS.md`](../CREDITS.md).

## 3. The shape: route first, then deliver, then verify

The 14 skills sit in three layers.

**Layer 1 — Govern & route.** `spec-master` is the front door. Its only job is to decide *who owns this* before any file is edited — route by authority surface, not by whichever file got mentioned first. Around it sit the governance owners: `spec-registry-manager` (the `SPECS.md` lifecycle), `issue-log-manager` (a holding pen for unresolved work that has no safe owner yet), `local-infra-registry-governance` (runtime allocation), and `shared-governance` (git/worktree and ownership guardrails shared across families).

**Layer 2 — Deliver.** `spec-driven-development` runs the six-phase lifecycle. `tdd-workflow` and `test-design-generator` supply Phase 4's red/green/refactor discipline; `test-registry-manager` owns the `TESTS.md` evidence catalog.

**Layer 3 — Verify (left-shift).** The `code-review` family — `code-refactoring-advisor`, `test-quality-reviewer`, `security-risk-reviewer`, `sonarqube-bridge` — is pulled into Phase 4/5 as *detection*, catching smells, weak tests, and security risk before the review verdict is written.

See [`methodology-diagram.md`](./methodology-diagram.md) for the full handoff, evidence-flow, and practice-mapping diagrams.

## 4. The six phases, and where each practice lands

1. **Requirements** — EARS-style acceptance criteria. The *Ponytail YAGNI Ladder* Rung 1 filters speculative needs (`deferred` / `out-of-scope`) before they pollute the requirement matrix.
2. **Design & contracts** — DDD shows up here: bounded contexts, contracts, data models, impact analysis. Rungs 2–4 force *stdlib → native platform → existing dependency* before any new dependency is justified.
3. **Tasks & traceability** — mirror the authority boundary and plan explicit closeout for `TESTS.md`, `RTM.md`, `SPECS.md`, CR closure, and issue disposition. Governance becomes executable, not aspirational.
4. **Implementation** — TDD's red → green → refactor with evidence reports. Folder-level `TESTS.md` is updated *before* any workspace rollup. Rungs 5–6 keep the implementation to "the minimum that works."
5. **Review verdict** — `review.md` owns readiness. The code-review family runs left-shift detection; new dependencies without a ladder record and unreasoned abstractions get flagged as `over-engineering risk`.
6. **Optimization** — repeated findings become a local lesson, an issue-log item, a CR fold-back, or a promoted skill/process change. Review pain becomes process improvement.

## 5. The one rule that prevents false-green

> **Evidence flows one way.** `ISSUE_LOG → spec artifacts & reports → folder-level TESTS.md → workspace rollup → RTM.md → SPECS.md`. Derived summaries **never** sync back into upstream truth.

This single constraint is what separates "looks done" from "is done." `review.md` owns the readiness verdict; `TESTS.md` owns the test catalog and evidence pointers; `SPECS.md` and `RTM.md` are *derived* and may never overwrite the upstream artifacts they summarize. A beautiful green dashboard generated from a stale rollup is, structurally, not allowed to be the source of confidence.

## 6. How it maps to Scrum, DevSecOps, and Responsible AI

- **Scrum** — the method strengthens boundary management rather than replacing ceremonies. The Product Owner routes ownership before the backlog hardens; the Scrum Master holds routing discipline and clarification cadence; Developers execute through the right downstream skill so implementation never contaminates governance.
- **DevSecOps** — test evidence, review verdict, and demo readiness live on *separate* authority surfaces, so mock-heavy green CI cannot masquerade as production-ready. Security review is left-shifted into Phase 5 instead of bolted on before release.
- **Responsible AI** — human oversight via phase gates, accountability via separate owners, transparency via authority-surface routing and recorded handoff reasons. This aligns with the [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework), [OECD AI Principles](https://oecd.ai/en/ai-principles), and [ISO/IEC 42001](https://www.iso.org/standard/42001).

## 7. Try it

1. Read the [Spec Master family page](../skills/spec-master/spec-master/index.html) for routing and authority surfaces.
2. Read the [Spec-Driven Development brief](../skills/spec-master/spec-driven-development/index.html) for the lifecycle and artifacts.
3. Install the skills (see the [README](../README.md)) and point your coding agent at `spec-master` as the front door.

All 14 skills are open-source under MIT. The family root is `skills/spec-master/`; downstream members install as sibling skill folders.

> **Claim boundary.** This article explains a methodology and a skill family. It does not claim that any consuming repository is demo-ready or production-ready — those claims must come from that repo's own `review.md`, test evidence, and runtime registry state.

---

<a name="中文版"></a>

# 中文版：把 DevSecOps + Scrum + TDD 移植到 Agentic 工作流

### 一套 14 個 skills 的開源家族——*Spec Master 開發方法*——如何讓程式代理人保持誠實

> **一句話總結**：程式代理人讓「產生程式碼」變便宜了，卻沒讓「協調程式碼」變便宜。瓶頸從打字轉移到決定責任歸屬、維持證據新鮮，以及阻止一個看似綠燈的檔案謊報 readiness。Spec Master 開發方法把五種已驗證的工程實踐——**SDD、TDD、DDD、測試管理與重構**——移植成一個由 14 個可組合開源 skills 構成、受治理且可檢視的 agentic 工作流。

## 1. 代理人製造的新問題

在傳統團隊裡，工作大致是線性地在人之間交棒：PM 寫故事、工程師實作、審查者複核、CI 把關。每次交棒都夠慢，慢到人能重讀上下文、察覺哪裡不對。

代理人團隊打破了這個前提。代理人產生文字、變更檔案、呼叫工具、把工作交給*另一個*代理人的速度，快過任何人重建上下文的速度。因此稀缺資源不再是產出，而是**決策品質與邊界控制**：

- **責任漂移**——兩個代理人把同一請求路由到兩條工作流，團隊付兩次澄清成本。
- **權威衝突**——`SPECS.md`、`NEXT_STEPS.md`、`RTM.md`、`TESTS.md`、`review.md` 開始競爭「誰才是真相」，交棒變脆弱。
- **假綠燈**——mock-heavy 測試保持綠燈，底層證據卻過期，信心上升得比訊號還快。
- **執行環境滲漏**——port、本地 stack、demo 狀態滲進 spec 檔案，開始假扮權威。

「讓代理人自己搞定」的直覺，正是這些失敗在規模化時的成因。解法不是*更少*流程，而是對**責任、證據與邊界更嚴格**、同時又便宜到代理人真的能遵循的流程。

## 2. 論點：移植，而非丟棄

SDD、TDD、DDD、測試管理與重構，早就為人類解決了這些問題。此方法主張：每一項在代理人團隊裡都保有它的職責，但需要一個明確的 **owner skill**，讓代理人永遠知道*誰*負責*什麼*。

| 經典實踐 | 它依然負責的任務 | 家族中的 owner skill |
|---|---|---|
| **規格驅動開發 (SDD)** | 把模糊意圖轉成可追溯交付 | `spec-driven-development` |
| **測試驅動開發 (TDD)** | 改程式前先釘住行為；讓重構安全 | `tdd-workflow` + `test-design-generator` |
| **領域驅動設計 (DDD)** | 讓邊界對齊業務語言 | SDD Phase 2（bounded context 與契約） |
| **測試管理** | 把 CI 綠燈變成可稽核的風險證據 | `test-registry-manager` + `test-quality-reviewer` |
| **重構** | 降低變更成本——在行為被保護*之後* | `code-refactoring-advisor` |
| **安全左移** | 在審查階段抓出注入／機密／弱加密 | `security-risk-reviewer` + `code-review` |

這些不是分離的口號。**SDD 決定要做什麼，TDD 安全地證明它，DDD 維持邊界語言誠實，測試管理讓證據保持新鮮，重構則避免變更成本持續累積。**

> **淵源**：`spec-driven-development` 啟發自 [AWS Kiro](https://kiro.dev) 的 requirements → design → tasks 規格流程；YAGNI 階梯改編自 [Ponytail](https://github.com/DietrichGebert/ponytail)（MIT）。完整出處見 [`CREDITS.md`](../CREDITS.md)。

## 3. 形狀：先路由、再交付、後驗證

14 個 skills 分三層。

**第一層——治理與路由。** `spec-master` 是前門，唯一職責是在任何檔案被編輯前，先決定*誰擁有這件事*——依權威面路由，而不是依「哪個檔案先被提到」。圍繞它的是治理 owner：`spec-registry-manager`（`SPECS.md` 生命週期）、`issue-log-manager`（尚無安全 owner 的未解決工作的暫存區）、`local-infra-registry-governance`（執行環境配置）、`shared-governance`（跨家族共用的 git/worktree 與責任護欄）。

**第二層——交付。** `spec-driven-development` 跑六階段生命週期；`tdd-workflow` 與 `test-design-generator` 供應 Phase 4 的紅/綠/重構紀律；`test-registry-manager` 擁有 `TESTS.md` 證據目錄。

**第三層——驗證（左移）。** `code-review` 家族——`code-refactoring-advisor`、`test-quality-reviewer`、`security-risk-reviewer`、`sonarqube-bridge`——在 Phase 4/5 作為*偵測*被引入，在 review verdict 寫下前抓出異味、弱測試與安全風險。

完整的交棒圖、證據流圖與實踐對照圖見 [`methodology-diagram.md`](./methodology-diagram.md)。

## 4. 六階段，以及每項實踐落在哪裡

1. **需求**——EARS 式驗收標準。*Ponytail YAGNI Ladder* Rung 1 在投機需求污染需求矩陣前先過濾（`deferred` / `out-of-scope`）。
2. **設計與契約**——DDD 在此登場：bounded context、契約、資料模型、影響分析。Rung 2–4 強制*標準函式庫 → 原生平台 → 現有依賴*，再決定是否引入新依賴。
3. **任務與追溯**——鏡射權威邊界，並為 `TESTS.md`、`RTM.md`、`SPECS.md`、CR 收尾與 issue disposition 規劃明確收尾任務。治理變得可執行，而非口號。
4. **實作**——TDD 的紅 → 綠 → 重構，附證據報告。folder-level `TESTS.md` 在任何 workspace rollup *之前*更新。Rung 5–6 讓實作維持在「最小可用」。
5. **複核裁決**——`review.md` 擁有 readiness。code-review 家族跑左移偵測；沒有 ladder 紀錄的新依賴與未經思考的抽象被標記為 `over-engineering risk`。
6. **優化**——重複發現轉成 local lesson、issue-log 項目、CR fold-back，或升級的 skill／流程變更。把 review 痛點轉成流程改善。

## 5. 防止假綠燈的那一條規則

> **證據單向流動。** `ISSUE_LOG → spec 工件與報告 → folder-level TESTS.md → workspace rollup → RTM.md → SPECS.md`。衍生摘要**永不**反向同步回上游真相。

這條單一約束，把「看起來完成」和「真的完成」分開。`review.md` 擁有 readiness verdict；`TESTS.md` 擁有測試 catalog 與 evidence pointer；`SPECS.md` 與 `RTM.md` 是*衍生*的，永遠不能覆寫它們所摘要的上游工件。一個由過期 rollup 生成的漂亮綠色儀表板，在結構上就不被允許成為信心來源。

## 6. 如何對應 Scrum、DevSecOps 與 Responsible AI

- **Scrum**——此方法強化邊界管理，而非取代儀式。Product Owner 在 backlog 寫死前先路由責任；Scrum Master 維持路由紀律與澄清節奏；Developers 透過正確的下游 skill 執行，讓實作永不污染治理。
- **DevSecOps**——測試證據、review verdict 與 demo readiness 分屬*不同*權威面，讓 mock-heavy 綠燈 CI 無法假扮成可上線。安全審查左移進 Phase 5，而不是上線前才硬接。
- **Responsible AI**——以 phase gate 做人類監督、以分離 owner 做問責、以權威面路由與記錄交棒理由做透明。對齊 [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)、[OECD AI Principles](https://oecd.ai/en/ai-principles) 與 [ISO/IEC 42001](https://www.iso.org/standard/42001)。

## 7. 試試看

1. 閱讀 [Spec Master 家族頁](../skills/spec-master/spec-master/index.html)，了解路由與權威面。
2. 閱讀 [規格驅動開發說帖](../skills/spec-master/spec-driven-development/index.html)，了解生命週期與工件。
3. 安裝 skills（見 [README](../README.md)），並讓你的程式代理人以 `spec-master` 作為前門。

14 個 skills 全部以 MIT 開源。家族根目錄是 `skills/spec-master/`；下游成員作為並列 skill 資料夾安裝。

> **宣稱邊界**：本文說明一套方法論與 skill 家族，不宣稱任何使用中的 repository 已可示範或可上線——這些宣稱必須來自該 repo 自己的 `review.md`、測試證據與執行環境註冊狀態。
