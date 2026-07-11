---
name: spec-driven-development
description: 預設的系統化開發工作流 (SDD)。當用戶明確要求開發新功能、修復複雜問題、進行需求梳理、架構設計、任務規劃、程式碼實現、spec review / optimization，或在 project review / live demo 前盤點真實整合風險時使用。若工作同時需要處理 review rejection、retro finding、known issue、tech debt、change-request follow-up、或其他 continuous-improvement 請求，並且要判斷它應該 `continue active spec`、走 `CR against completed spec`、先進 issue log，還是真的需要 `new spec`，也應使用此 skill。若工作同時需要規劃需求到任務的主流程，並在 implementation / closeout 前安排 folder-level `TESTS.md` row-level 更新、workspace `.agents/specs/TESTS.md` reconciliation / rollup refresh、test evidence 回寫，或明確決定何時 handoff 給 `test-registry-manager`，也應使用此 skill。直接的 `TESTS.md` catalog cleanup / duplicate-ID / stale-row / mapping reconciliation 本身仍屬於 `test-registry-manager`。
---

# Spec-Driven Development (SDD)

SDD 是一個系統化的六階段開發工作流。你的目標是引導用戶完成從需求到部署的完整週期，並嚴格遵循「契約優先 (Contract-First)」與「單一真實來源 (SSOT)」原則。

## Execution Profile 機制（原型 / 強化模式）

SDD 支援三種 Execution Profile，讓同一套六階段流程能在不同嚴格度下執行：

| Profile | 用途 | 核心特徵 | 適用情境 |
|---|---|---|---|
| `default` | 標準交付 | 完整六階段、80%+ Coverage、完整 DoD | 正常功能開發、正式 Sprint |
| `prototype` | 極速驗證 | Sketch-DD、Behavior-Only TDD、Sandbox Integration、假設驗證 | PoC、Spike、MVP、快速假設驗證 |
| `harden` | 逆向補強 | Reverse-Engineering Spec、Backfill TDD、DevSecOps Guardrails | 原型驗證後升級為企業級品質 |

**Profile 切換規則**：
- Profile 由 `spec-master` 在路由時決定，透過 `--profile={prototype,harden,default}` 傳入。
- `prototype` → `harden` 是**同一個 Spec 的生命周期升級**，不是開新 Spec。
- 下游技能（`test-registry-manager`、`issue-log-manager`）不需要做 Profile 路由判斷，只需識別標準化的任務標籤 `[PROTOTYPE]` / `[HARDEN]`。

**強制 Session 拆分點**（所有 Profile 皆適用）：
1. Phase 1 (Requirements) → Phase 2 (Design): `handoff-requirements-design.md`
2. Phase 2 (Design) → Phase 3 (Tasks Planning): `handoff-design-tasks.md`
3. Phase 3 (Tasks) → Phase 3 (Implementation Execution): `handoff-tasks-implementation.md`
4. Phase 3+4 (Implementation+Integration) → Phase 5 (Review): `handoff-implementation-review.md`
5. Prototype → Harden: `handoff-prototype-harden.md`

每個拆分點必須產出 handoff 文件作為下一 Session 的**唯一輸入**。新 Session **禁止**讀取前一 Session 的完整歷史。

---

## Profile: `prototype`（極速驗證模式）

當 `--profile=prototype` 時，六階段執行規則如下：

### Phase 1+2: Sketch-DD（草圖驅動設計）
- **合併執行**：Requirements 與 Design 合併為單一階段。
- **輸出**：`sketch.md`（`requirements.md` + `design.md` 的 v0.1 Draft）。
- **內容邊界**：僅定義 Core Context、Bounded Context 邊界、關鍵 Data Flow。
- **允許**：暫時的 Monolith 結構、不完美的分層、Anemic Domain Model。

### Phase 3: Behavior-Only TDD（行為驗證）
- **僅 Happy Path**：只針對核心成功路徑撰寫高層級 Integration / E2E Test。
- **全面 Mock**：所有外部依賴改用 In-memory DB、Mock Server、Fake Repository。
- **任務標籤**：所有任務標記為 `[PROTOTYPE]`。
- **跳過**：Edge Cases、Exception Handling、80% Coverage 要求。

### Phase 4: Sandbox Integration（沙盒整合）
- **環境隔離**：在 Agent 沙盒或 Local 環境執行。
- **不接觸真實資料**：禁止連接 Production DB、真實第三方 API。
- **安全性**：僅防範致命漏洞（SQL Injection、RCE、XSS）與 Secret 硬編碼。

### Phase 5: Hypothesis Validation（假設驗證）
- **驗收重點**：「核心商業假設是否被驗證」，而非完整 DoD。
- **產出**：`review-prototype.md`（結構同 `review.md`，但驗收標準不同）。
- **通過條件**：Happy Path 可執行、核心假設獲得證據支持。

### Phase 6: Skip / Issue Log（暫時跳過）
- **不安裝 SAST/SCA/DAST 閘門**。
- **記錄技術債**：已知問題記入 `ISSUE_LOG.md`，為 Harden 階段預留線索。
- **產出**：`handoff-prototype-harden.md`（若確定進入 Harden）。

---

## Profile: `harden`（逆向補強模式）

當 `--profile=harden` 時，六階段執行規則如下：

### Phase 1+2: Reverse-Engineer Spec（逆向規格生成）
- **輸入**：`handoff-prototype-harden.md` + Prototype Code + `sketch.md`。
- **輸出**：精準的 `requirements.md`（回填 5W2H、NFRs）+ 完整的 `design.md`（含 OpenAPI Spec、Mermaid 架構圖、正式分層）。
- **任務**：從 Code 反向提煉 Domain Model、識別遺漏的 Bounded Context、補齊 Contract 定義。

### Phase 3: Backfill TDD（逆向測試補齊）
- **針對現有 Code**：對 Prototype 的 Happy Path Code 自動補齊：
  - Edge Cases（邊界條件）
  - Exception Handling（異常處理）
  - Unit Tests（單元測試）
- **任務標籤**：所有新任務標記為 `[HARDEN]`。
- **覆蓋率目標**：拉回 80%+ Coverage。
- **取代關係**：`[HARDEN]` 任務取代對應的 `[PROTOTYPE]` 任務（保留歷史但標記為 superseded）。

### Phase 4: Real Integration（真實整合）
- **移除 Mocks**：接入真實 DB、真實外部 API。
- **執行真實整合測試**：驗證真實環境下的行為。
- **資料遷移**：若有 Seed Data / Demo Data，建立 canonical scenario fixture。

### Phase 5: Full DoD Review（完整定義完成審查）
- **標準 DoD 審查**：所有驗收標準必須通過。
- **產出**：`review.md`（取代 `review-prototype.md`）。
- **檢查項目**：功能完整性、測試覆蓋率、文件完整性、安全性基線。

### Phase 6: DevSecOps + Refactor（安全閘門 + 重構）
- **DevSecOps 標準任務模板**：
  - `[HARDEN] Enable Semgrep SAST`（Lightweight mode：僅高危規則如 SQLi, RCE, XSS）
  - `[HARDEN] Enable Secret Scanning`（Gitleaks / TruffleHog：硬編碼 Key 立即阻斷）
  - `[HARDEN] AI Security Review`（對抗式審查：專職安全 Agent 審查邏輯漏洞）
- **品質任務並列**：
  - `[HARDEN] Refactor Anemic Domain Model → Rich Domain Model`
  - `[HARDEN] Extract Value Objects and Aggregate Boundaries`
  - `[HARDEN] Performance tuning and load testing`
- **關鍵原則**：安全任務與品質任務並列，不取代現有的 Optimization 任務。

---

## Context Management & Session Optimization

為了縮減接續進行時的 context 負擔，所有 Profile 都必須執行三層減壓策略：

1. **Strategic Compact**（策略性壓縮）：每個 Phase 結束產出 `phase-{n}-compact.md`，只保留決策與開放問題。
2. **Phase Gate Handoff**（階段閘門交接）：五個強制拆分點（Requirements→Design, Design→Tasks, Tasks→Implementation, Implementation→Review, Prototype→Harden），每點產出 `handoff-{from}-{to}.md`。
3. **Sub-agent Delegation**（子代理分派）：依 Profile 將工作拆分給獨立 sub-agent（Prototype: Sketch/Coder/Validate/Log；Harden: Spec/Backfill/Integrate/Review/Guardrail）。

**Context Budget**：
| Profile | Max Phases / Session | Compact Trigger | Sub-agent Split | Handoff Required |
|---|---|---|---|---|
| `prototype` | 3 | Every Phase end | **強制**拆分 | **強制** |
| `harden` | 2 | Every Phase end | **強制**拆分 | **強制** |
| `default` | 4 | Every 2 Phases | 可選 | 可選 |

詳細格式與範例請參閱：[references/context-management.md](./references/context-management.md)

---

## 核心工作流與目錄結構

此 Skill 採用 Pipeline 模式。您必須依照以下 6 個階段順序執行。各階段的詳細指引（包含必須建立的文件結構）均位於 `phases/` 目錄下。觸發任一階段前，**必須讀取該階段的詳細指南檔案**。

- **第一階段**：[需求明確](./phases/01-requirements.md) (產出 `requirements.md`；AC 必須使用 H4 + 編號列表 canonical format，詳見 `reference/AC_FORMAT_GUIDE.md`)
- **第二階段**：[架構設計](./phases/02-design.md) (產出 `design.md` 與 `contract/*`)
- **第三階段**：[任務規劃](./phases/03-tasks.md) (產出 `tasks.md`)
- **第四階段**：[程式碼實現](./phases/04-implementation.md) (產出程式碼、`tasks.md` 勾選更新、以及 `reports/` 證據)
- **第五階段**：[程式碼複核](./phases/05-review.md) (產出 `review.md`)
- **第六階段**：[程式碼優化](./phases/06-optimization.md) (產出優化後的 `review.md` / `NEXT_STEPS.md` 更新；`optimization_log.md` 可作為 legacy/optional artifact)

**第一、二階段的深度需求/設計訪談**（CEO 高階價值視角 + 逐題 grilling 追問）方法論見：[references/requirement-interview-depth.md](./references/requirement-interview-depth.md)。預設啟動、可隨時跳過；它在既有「先生成草稿」流程上補強前提挑戰與決策樹逐題追問，但不取代 `requirements.md` / `design.md` 的 authority。

**第二、五階段的架構設計與複核深度**（實作方案比較 + deep module / seam + 輕量 domain modeling + 架構認知模式；複核期的架構深度維度 + per-finding confidence/verbatim-quote 防誤報 gate）方法論見：[references/architecture-design-depth.md](./references/architecture-design-depth.md)。與既有 contract-first SSOT、FMEA、Ponytail ladder、`code-review` 家族**互補而非取代**。

**跨 spec 的系統架構文件生命週期**（markdown + HTML 雙重文件、SAA good parts、project review claim-cap、與 spec lifecycle reconciliation）見：[references/system-architecture-lifecycle.md](./references/system-architecture-lifecycle.md)。當 project start、Phase 2 design、Phase 5 review、或 project-review artifact 需要能跟人溝通的整體架構觀點時讀取；它不取代 branch-spec `design.md`，只定義如何把 accepted design evidence 維持成 current architecture snapshot。若本 spec 涉及 AI/security/privacy/PII/log/regulatory-compliance scope，必須同時組合 `iso-ai-security-auditor`，把其 inventory / evidence refs 作為 architecture and review inputs，不得把盤點結果寫成法律或認證 verdict。

文件統一放置於：`.agents/specs/{spec-directory}/`。

跨 spec 共用的滾動式工作備忘錄固定放置於：`{workspace}/.agents/specs/NEXT_STEPS.md`。

workspace-level 追溯統合表固定放置於：`{workspace}/.agents/specs/RTM.md`（若存在）。

## Governance Artifact Lifecycle Reference

當工作涉及 `ISSUE_LOG.md`、`SPECS.md`、`NEXT_STEPS.md`、`TESTS.md`、`RTM.md`、`review.md` 的定位、更新順序、生命週期、authority boundary、requirement traceability、或跨 artifact closeout，必須讀取：

- [reference/SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md](./reference/SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md)

核心規則：`ISSUE_LOG.md` 是 unresolved improvement holding surface；`NEXT_STEPS.md` 是 rolling operational memo；`RTM.md` 是 requirement traceability rollup；`SPECS.md` 是 stable registry summary；`TESTS.md` 是 test catalog / evidence pointer authority；`review.md` 是 readiness verdict authority。不可讓 derived artifacts 反向改寫 upstream truth。

## Packageable Business Explanation

若使用者要「替 spec-driven-development / SDD 正名」、「建立可隨 Spec Master family 打包的商業價值說明」、「產生 value proposition / Amazon backwards press / FAQ / stakeholder brief」、「說明 SDD 與 TDD / DDD / test management / refactor / Scrum Team / Agile Manifesto 的關係」，優先使用：

- [README.md](./README.md)
- [GENERATION_GUIDE.md](./GENERATION_GUIDE.md)
- [index.html](./index.html)

`README.md` 是可隨 `skills/spec-driven-development/` 一起交付的文字說帖；`GENERATION_GUIDE.md` 是後續更新規則；`index.html` 是可直接展示的雙語 HTML 版本。這些文件必須把 SDD 定位為 Spec Master 家族中的主要交付 skill：`spec-master` 是入口與 routing front door，`spec-driven-development` 是 requirements → design → tasks → implementation → review → optimization 的 delivery backbone。

## Packageable Manual Explanation

若使用者要「操作等級的 SDD 使用手冊」、「quick start / phase walkthrough / closeout checklist」、「用 user-manual 方式說清楚 SDD 怎麼跑」，優先使用：

- [MANUAL_GENERATION_GUIDE.md](./MANUAL_GENERATION_GUIDE.md)
- [manual.html](./manual.html)

`MANUAL_GENERATION_GUIDE.md` 是操作手冊更新規則；`manual.html` 是雙語使用手冊。它應聚焦在何時啟動 SDD、何時回到 `spec-master` routing、每個 phase 要讀寫哪些 artifact、如何處理 `NEXT_STEPS.md` resume、如何刷新 test evidence、以及如何避免 mock-heavy / false-green / artifact overclaim。它不是 readiness verdict，也不可取代 `review.md`。

---

## 🛑 全局約束 (Global Constraints) - 必須嚴格遵守

### 1. 規格註冊表機制 (Feature Registry)

在專案根目錄必須維護 `{workspace}/.agents/specs/SPECS.md`，作為所有規格的「總目錄與依賴地圖」。(若有 `{workspace}/specs/SPECS.md`, 請移動到前述規定中的路徑.)

- **必須在 Phase 1 & Phase 2 第一步讀取此檔**，以確認新功能是否與舊功能重疊。
- `SPECS.md` 應作為穩定的治理登錄表，至少能摘要 `Depends On`、`Impacts`、`Open Change Requests`，以及 external contract 的 `Contract Authority`、`Source of Truth`、`Pin/Version`。
- `SPECS.md` 用來承載穩定治理資訊，不承載即時 branch 狀態，避免把 registry 變成高衝突的動態工作台。
- 新增或修改 spec 後，必須回寫更新此檔。
- 💡 **原因 (WHY)**：避免重複開發，並清楚掌控模組間的相依關係 (Dependencies)。

### 2. 滾動式下一步備忘錄 (Rolling NEXT_STEPS Memo)

`{workspace}/.agents/specs/NEXT_STEPS.md` 是一份 **workspace-scoped 的共用 operational memo**，用來承載跨 spec 的當前工作狀態、下一步、阻塞、恢復點與 CR / re-sync 摘要。

- 它是 **高階、滾動式、可覆寫** 的操作備忘，不是 immutable spec，也不是 registry。
- `NEXT_STEPS.md` 應與 `SPECS.md` 並存：
  - `SPECS.md` = 穩定治理登錄表（registry / dependency map）
  - `NEXT_STEPS.md` = 滾動中的 operational state / resume memo
  - `change-requests/{cr-id}.md` = 完整 CR overlay 內容
- 在 **new session / resumed session / 中斷後重啟** 時，若 `NEXT_STEPS.md` 存在，必須在讀取 `SPECS.md` 後立刻讀取它，再決定要展開哪些 spec 文件。
- 至少在以下時機更新它：
  1. 確認本次工作屬於 `continue active spec`、`new spec`、`retrofit`、`CR against completed spec`、或 `issue-log candidate`
  2. impact triage / `Open Change Requests` / re-sync 結果發生變化
  3. phase 結束後需要交棒、暫停、換 session、或等待人類確認
  4. 發生 circuit breaker、重大 blocker、或需要請求協助之前
- 內容必須保持**高層摘要**：例如 current phase、active spec(s)、impacted spec(s)、open CR IDs、next action、blockers、resume hint、以及相關 artifact 路徑。
- `NEXT_STEPS.md` 必須**簡短且可追溯**：預設只指向 `{spec-directory}/tasks.md`、`review.md`、或 reports 等正式 artifact，而不是複製其中的 task list、task progress、execution ordering、或長篇狀態敘述。
- **禁止重複貼上** `requirements.md` / `design.md` / `tasks.md` / `review.md` 全文、`SPECS.md` 全部條目，或完整 CR 內容。
- 格式與最小欄位請參考 `./reference/NEXT_STEPS_TEMPLATE.md`。
- 💡 **原因 (WHY)**：讓 original session 或 new session 都能快速恢復上下文，同時避免把 `SPECS.md` 變成高衝突的即時工作台。

### 2.5 Workspace RTM Rollup

`{workspace}/.agents/specs/RTM.md` 若存在，應視為 **workspace-level synthesized rollup**，用來統合各 spec 的 `requirements.md`、`design.md`、`tasks.md`、`review.md` 參照。

- **RTM.md 與 NEXT_STEPS.md 的 authoring owner 是 `spec-driven-development`。** RTM 的 synthesize / refresh 與 `NEXT_STEPS.md` rolling memo 的維護都由 SDD（透過 closeout 與 Phase 6）負責；`spec-registry-manager` 與 `test-registry-manager` 只能以 derived summary 方式讀取或彙整其狀態，`issue-log-manager` 只提供 pointer / warning，皆不得反向 author 這兩份 artifact。
- `RTM.md` 不是 spec-level authoring artifact。
- `requirements.md` 仍是 requirement source of truth；`design.md` / `tasks.md` / `review.md` 仍是對應的 spec-level truth。
- `RTM.md` 只負責提供 cross-spec traceability 與 verification rollup 視圖，不負責裁決 readiness。
- `RTM.md` **不得**成為 task-counter、execution-order tracker、resume controller、或 per-task progress authority。task 細節與狀態的真相來源仍是 `{spec-directory}/tasks.md`、reports、與 `review.md`。
- 💡 **原因 (WHY)**：真正需要被統合的是 workspace level，不是每個 spec 再多維護一份追溯文件。

### 2.6 兩層治理模型 (Two-Layer Governance)

為了兼顧治理強度與 first-slice 交付速度，治理活動必須區分為兩層：

1. **Early Declarative Governance**
   - 工作分類 (`continue active spec` / `new spec` / `retrofit` / `CR against completed spec` / `issue-log candidate`)
   - `Depends On` / `Impacts` / `Open Change Requests` 摘要
   - 最小 first-slice boundary
   - design-phase lightweight FMEA（若觸發條件存在）
   - review-authority / claim-cap posture

2. **Just-in-Time / Closeout Governance**
   - re-sync freshness writeback
   - CR closure / supersede 收斂
   - registry summary refresh
   - closeout / handoff reconciliation

核心規則：

> 若某個治理步驟**不會改變 first slice 的正確性**，它就不應阻塞 first slice 開始。

### 3. 文件安全更新守則 (Safe Document Update Protocol)

為避免上下文過長導致文件被改壞，在修改任何規格文件（如 `SPECS.md`, `requirements.md`, `design.md`, `tasks.md` 等）之前，必須：

1. **生成草稿 (Drafting)**：將修改或新增的內容寫入臨時檔案（例如 `temp/{spec-name}_update.md`），而非直接編輯原檔。
2. **審查與比對 (Review)**：讀取草稿並確認內容完整，沒有出現截斷或省略現象。
3. **合併 (Merge)**：若確認無誤，將草稿覆寫回原檔（更新），或使用 Append 方式合併至原檔底部（新增任務）。
4. **清理與提交 (Clean & Commit)**：合併完成後刪除臨時草稿，並執行 `git commit`。

- 💡 **原因 (WHY)**：避免 LLM 因 Context Window 限制或 Edit 工具替換失敗，導致大文件內容遺失且難以救回。

### 3.5 Git Branch / Worktree 隔離

- 若工作涉及平行 spec lane、completed baseline 的 CR overlay、repo-owned global skill / shared governance wording 變更、或大型 `TESTS.md` / `SPECS.md` / `RTM.md` refresh，預設採用 **一條 lane = 一個 branch = 一個 writable worktree**。
- 同一個 branch 同時間只應存在一個 writable worktree。需要只讀盤點、比對或 review 時，可使用 detached / read-only worktree。
- branch name 應使用穩定 namespace（例如 `spec/`, `cr/`, `tests/`, `registry/`, `review/`），並保持可追溯；不要依賴模糊縮寫或臨時亂數名稱。
- worktree path、機器本地暫存位置、與其他 machine-local execution state，不可寫入 `SPECS.md`、`NEXT_STEPS.md`、`RTM.md`、`TESTS.md` 或 `review.md`；共享規則與範本應優先由 global skill 內建 shared-governance references 承載，而不是依賴 `AGENTS.md` 才存在。
- 具體的建立 / 重用 / 清理規則，必須讀取 `../shared-governance/references/git-worktree-guide.md`；branch namespace、layout、命令範本與 handoff checklist 則讀取 `../shared-governance/references/git-worktree-templates.md`；多 lane 衝突處理則讀取 `../shared-governance/references/concurrent-writable-lanes.md` 與 `../shared-governance/references/pre-write-conflict-checklist.md`。

### 4. 契約驅動與 SSOT (Contract-Driven)

`contract/` 目錄是所有資料模型、API、與事件定義的**唯一真實來源 (Single Source of Truth)**。

- 必須在 Phase 2 優先產出或更新 contract 定義檔（如 `openapi.json`, `TypeSpec`, `JSON Schema`）。
- 若某個契約實際由外部系統主導，仍須在本專案 `contract/` 中維護本地對應定義，但必須同步標記 `Contract Authority`、`Source of Truth`、`Pin/Version`，說明上游權威來源與目前鎖定版本。
- 程式碼實作（Phase 4）**不可手寫基礎型別**。必須透過指令/腳本從 contract 自動生成 (Code Generation) 對應的 TypeScript Types, Pydantic Models 或 ORM Entities。
- 💡 **原因 (WHY)**：從根源消滅程式碼與規格不符的問題。

### 5. 跨生命週期的規格更動與外部執行治理 (Drift & External Handoff Management)

舊有已完成的 Specs 視為 **Immutable (不可變)** 的歷史快照，絕不偷偷塗改。

- 當新需求需要更動舊邏輯時，必須在「新 Spec」的 `requirements.md` 與 `design.md` 中明確宣告 `[Impacts: {舊spec名稱}]`。
- 若目標是 `[Completed]` spec、shared contract 或 external contract 假設，必須以 **Change Request (CR) overlay** 的方式登錄於當前 active spec 與 `SPECS.md`，而不是直接靜默改寫舊 spec 基線。
- 若修改了 `contract/` 中的舊定義，必須觸發全局型別檢查 (`tsc` 或 lint)，找出舊實作的漂移並在當前任務中修復。
- 若存在 `Open Change Requests` 或 `Contract Authority=external` 的相依，必須在 **設計核准前** 與 **review / merge 前** 各重讀一次最新 `SPECS.md`，確認沒有新增的 overlapping CR、遺漏的 dependency，或上游版本漂移。
- CR overlay 必須先做 impact triage、使用 canonical CR 路徑、在 re-sync gate 留下 freshness evidence，並在收斂後明確 `Closed` 或 `Superseded`，避免長期漂浮的 open CR。

**外部執行與 Handoff 治理 (External Execution Governance)**：
當任務依賴外部執行（如另一台機器、CI runner、硬體特定環境）時，必須嚴格區分「Repo-side closure」與「External execution」。

- **狀態分類**：
  - `completed-local`：所有 repo-side 工作已完成，無進一步本地可執行動作。
  - `completed-handoff`：已準備好完整的外部交接包（包含精確指令與成功標準），下一步在當前工作站之外。
  - `external-blocked`：剩餘工作真實存在，但無法在當前環境執行（如缺硬體、缺 secrets）。
  - `retired`：因合規、安全或政策原因，決定不實作此路徑。
  - `historical-skeleton`：僅保留規劃意圖的歷史骨架，非活躍工作。
- **Truth-Source Priority (真相來源優先級)**：
  1. Explicit current user fact (使用者明確告知的最新事實)
  2. Latest pulled repo state
  3. Spec-local closure artifacts (`closure.md`, `review.md`, updated `tasks.md`, fresh reports, plus legacy `completed_tasks.md` if that repo still uses it)
  4. `SPECS.md` registry state
  5. `NEXT_STEPS.md` operational memo
  6. Older reports / historical summaries
- **User Fact Override / Drift Audit (使用者事實覆寫 / 漂移稽核)**：若使用者告知的外部執行事實（如「arm64 驗證已在另一台機器完成」）與 `NEXT_STEPS.md`、舊 spec、或歷史報告衝突，必須**立即停止執行模式，進入漂移協調模式 (drift-reconciliation mode)**。舊文件在完成協調前一律視為 stale state；不得要求使用者先證明 repo memo 錯誤，也不得讓較舊的 repo 文字覆蓋較新的明確使用者事實。
- **協調完成要求**：一旦確認使用者事實較新，必須把 repo-local closure 與 external execution state 分別回寫到 active spec、`review.md` / `closure.md`、`SPECS.md` 與 `NEXT_STEPS.md`，避免同一工作同時以「已交接完成」與「仍需本地執行」兩種狀態並存。
- **文件分離要求**：
  - `requirements.md` / `design.md`：必須先在 branch-spec 層建立 repo-side closure 與 external execution 的邊界，再進入任務拆解。
  - `tasks.md`：只鏡射（mirror）前述 branch-spec 邊界，不得自行發明或改寫治理邊界。最後一個本地任務應為「finalize remote verification handoff package」，而非「execute locally」。
  - `review.md`：必須明確聲明「local repo-side work complete」且「external execution pending/completed elsewhere」。
- **Stale-State Hygiene Gate (過期狀態衛生檢查)**：在關閉 spec 前，必須確認：
  1. 是否還有本地程式碼/文件工作？若無，停止本地迴圈。
  2. 是否只有唯一一個權威的 handoff spec？
  3. `NEXT_STEPS.md` 是否已清除舊的、重複的 handoff 描述？不可同時存在「completed handoff」與「still active local work」。
  4. 歷史/被取代的 spec 是否已明確標記為 historical/superseded？

- 💡 **原因 (WHY)**：保持規格的歷史完整性，並確保合約更動能確實反應在現有程式碼上。同時防止 Agent 在外部依賴已完成時，仍因過期文件陷入本地執行的無限迴圈。

### 6. 需求追溯性 (Traceability)

從需求到程式碼，必須有一條清晰的追溯鏈。

- `requirements.md` 中的每個需求必須有唯一 ID（例：`REQ-AUTH-001`）。
- `tasks.md` 的每個任務，以及 Contract 中的對應端點，必須標註 `[Implements REQ-AUTH-001]`。
- `RTM.md` 若存在，應只作為 workspace-level traceability rollup，將 `requirements.md` / `design.md` / `tasks.md` / `review.md` 的穩定參照整合起來。
- 💡 **原因 (WHY)**：確保每個開發動作都有商業價值支撐。

### 7. 專案規範與上下文感知

- 必須通讀並嚴格遵守當前專案 `.agents/steering/` 或 `AGENTS.md` 下指定的所有規則。
- 如果採用 Dependency Injection 模式，讀取程式碼時必須一併讀取其實作與介面。
- 若工作會修改任何 Go 檔案，且 repo 含有 `go.mod`，必須先讀取 `go.mod` 的 `module` 行，再決定專案內 self-import path。**永遠不要根據 Git remote host、舊倉庫記憶、或 import 長相去猜測 module path。**
- 若專案提供 Go module path guard script / CI guardrail，必須將它納入 verification，而不是只依賴人工檢查。
- 💡 **原因 (WHY)**：確保新程式碼能完美融入既有架構，而非突兀的補丁。

### 8. 可重複樣本資料管理 (Reusable Sample Data)

- 可重複使用的樣本資料（測試資料、Mock Payload、Seed Data、Demo Data）不得只留在 `temp/` 或行內測試常數中。
- 若同一份業務資料會被 manual / review / demo / test 重複使用，必須建立一個 **canonical scenario** 作為單一真實來源（SSOT）。
- 測試應透過 fixture / helper / adapter 層讀取 canonical scenario，而不是在每個 spec 內複製 JSON 或硬編路徑。
- 💡 **原因 (WHY)**：避免資料漂移、降低維護成本，並讓多個流程能共享同一套可驗證的業務情境。

### 9. 專案指南應承載具體路徑 (Project Guides Hold Concrete Paths)

- Global skill 只定義通用規則；具體目錄、指令、輸出位置應落在專案級 guide（例如 review / manual / demo guide）中。
- 若某個流程依賴固定樣本目錄、截圖路徑或啟動命令，應將這些具體資訊寫入專案 guide，而不是散落在測試或臨時腳本裡。
- 💡 **原因 (WHY)**：保持 global skill 通用，同時讓專案內的實際執行路徑清楚、可維護、可重現。

### 10. Local Infra Registry Governance

- 若工作需要啟動或管理 local dev / UAT / E2E 服務，必須先使用 `local-infra-registry-governance` 思維與工具契約進行 registry query / reconcile / allocation，再決定是否 request、reuse、release 或 gc。
- workflow skill 不可直接猜測 localhost ports、networks、compose stack names，也不可把 live allocation state 寫進 `SPECS.md` 或 `NEXT_STEPS.md`。
- `devops-container-orchestration` 僅提供容器實作模式；真正的 allocation authority 必須來自 local infra registry。
- project-instance selection 必須遵守 **exact match → deterministic resolve → developer HITL selection**；不可由 agent 自行做 synonym / fuzzy match 推論。
- 若需要持久化 canonical project naming / alias / required service bundle 規則，只能寫回 **workspace-scoped `AGENTS.md`** 或該 workspace 指定的穩定檔案，不可寫入 global `AGENTS.md`。
- multi-service local runtime 的成功條件以 required service bundle readiness 為準，而不是單一 service / 單一 port 的存活。
- 💡 **原因 (WHY)**：跨專案與跨 stage 的 local infra 衝突，本質上是 runtime resource governance 問題，不是 feature registry 或 agent 記憶問題。

### 11. Live Demo Readiness 與 False-Green 防護

- 若功能涉及 UI、E2E、manual、project review、dashboard、auth flow、或任何需要對外展示的 live demo，必須把 **live-demo readiness** 視為獨立品質閘門，而不是附屬於「測試有跑過」的口頭結論。
- 必須區分目前的驗證層級：`mock-heavy`、`hybrid`、`full-integration`。不可把只驗 UI、只驗 stub/mock、或只重播 HAR/fixture 的結果描述成 backend-ready / demo-ready。
- 若存在 `page.route()`、mock helpers、fake providers、HAR replay、storageState / auth fixture、demo seed data、或任何會繞過真實 backend / 真實 auth 的機制，必須先盤點其用途、覆蓋範圍、殘留風險，再決定 demo readiness 結論。
- 對於 login、SSO、session refresh、RBAC、dashboard data、或任何高風險關鍵旅程，必須至少保留一組 **real-backend / real-auth smoke path**。沒有這條路徑時，review 不得給出「可直接 live demo」的結論。
- `project-review-skill`、`user-manual-skill`、E2E screenshot、與 review artifacts 若使用 mock/fixture 產生，必須在輸出中明確標示，不可讓截圖或報告看起來像真實整合證據。
- 詳細檢查清單與代表性風險請參閱 `./reference/DEMO_READINESS_GUIDE.md`。
- 風險代碼命名請與共用 taxonomy 對齊：`../../docs/DEMO_RISK_WARNING_TAXONOMY.md`。此 warning-code taxonomy 與 per-spec domain glossary / ADR 同屬統一**術語治理**，單一查詢入口見 [references/terminology-governance.md](./references/terminology-governance.md)（區分跨 skill 穩定 enum vs per-spec 領域術語，避免混用）。
- 💡 **原因 (WHY)**：E2E 常出現「畫面看起來過了，但其實 backend、auth、或 live data 沒有真的通」的 false-green 現象。把 demo readiness 升格為獨立 gate，才能避免 project review 文件綠燈、live demo 現場翻車。

### 12. Lightweight FMEA 與風險回應規劃

- 若功能涉及以下任一情況，design 階段**必須**加入 **lightweight FMEA**，而不是等到 implementation / review 才被動補救：
  - stakeholder-facing artifact（manual / project review / screenshot / report / demo script）
  - external contract / shared contract / CR overlay
  - cross-spec synthesized rollup（例如 workspace `RTM.md` / registry summary）
  - 高風險 auth / data / readiness 路徑
  - failure 會直接造成 false-green、overclaim、或 stale summary
- FMEA 應保持 **輕量、spec-local、可追溯**：不要導入新的 global governance framework，也不要追求虛假的精密分數。
- FMEA 的正式 authoring 位置是 `design.md`；`review.md` 只負責驗證 mitigation evidence 與 residual risk，不負責補寫本來應在設計期識別的 failure modes。
- 最小欄位建議包含：`Risk ID`、`Failure Mode`、`Effect`、`Cause`、`Current Control`、`Severity`、`Occurrence`、`Detection Difficulty`、`Planned Response`、`Task Trace`。
- 每個高風險 failure mode 至少要定義一種 **Prevent / Detect / Contain** 類型的回應，並在 `tasks.md` 中對應到具體任務或驗證步驟。
- 若某個風險在 first slice 內無法完全消除，輸出必須採取保守降級（例如 `gap` / `blocked` / `not_assessed` / warning codes），而不是隱藏 residual risk。
- 💡 **原因 (WHY)**：很多實際失敗不是來自單一 bug，而是來自「摘要比證據更樂觀」、「planned 被說成 executed」、「warning 在聚合時遺失」這類規劃期就可識別的 failure mode。把輕量 FMEA 放進 design / tasks / implementation，可以把風險回應前移，而不是等 review 才發現。 

---

### 13. Test Governance (測試治理)

#### 13.1 TESTS.md 雙層模型

- workspace level: `{workspace}/.agents/specs/TESTS.md` 作為 repo-wide test registry / summary
- package or folder level: `{module}/TESTS.md` 作為 test decision table 與整合測試細節
- 若需要 discovery / reconciliation / stale-row cleanup / workspace TESTS rollup refresh，預設交給 `test-registry-manager`
- 詳細模板與欄位請參考 `./reference/TEST_GOVERNANCE_GUIDE.md`

#### 13.2 Authority Boundary

- `TESTS.md` 擁有 test catalog、test ownership、canonical commands、evidence refs
- `review.md` 擁有最終 acceptance / readiness verdict
- `SPECS.md` 與 `RTM.md` 只保留 **non-authoritative derived snapshots**
- 若 `SPECS.md`、`TESTS.md`、`RTM.md` 的 snapshot 欄位衝突，必須回到 upstream source（`review.md`、test reports、spec-local docs）重新生成
- 若 impacted CR 為 `Open` 或 `Review Pending`，critical test evidence 不得因舊 snapshot 仍顯示綠燈就被視為 fresh；必須以最新 upstream evidence 重新判定

#### 13.3 Non-Cyclic Rollup Rule

- 允許：`requirements.md` / `design.md` / `tasks.md` / `review.md` / test reports → `TESTS.md` / `RTM.md` / `SPECS.md`
- 禁止：`SPECS.md -> RTM.md`、`RTM.md -> TESTS.md`、`SPECS.md / RTM.md -> TESTS.md` 等 derived-to-derived 回填

#### 13.4 Packaged Skill Governance

- packaged/global skill surface 的正式更新必須遵守其 **repo-owned source-of-truth → release/install** 流程
- 不可把 runtime / deployed copy 當成 authoring target

#### 13.5 Why

💡 **原因 (WHY)**：測試治理需要同時滿足可追溯、可聚合、不可循環回寫。把 `TESTS.md` / `SPECS.md` / `RTM.md` 建成 one-way derived authority graph，才能降低 false-green、summary drift、與 endless refresh 風險。

#### 13.6 Concrete Maintenance Boundary

- `spec-driven-development` 負責：
  - 在 requirements / design / tasks 階段定義 test obligations、traceability expectations、與 closeout timing
  - 在 improvement / CR 類 spec 中明確定義 test lifecycle 與 CR freshness crosswalk
  - 在 implementation / review closeout 前要求刷新 folder-level `TESTS.md` 與相關 evidence refs
  - 在需要時把 `TESTS.md` 治理工作交給 `test-registry-manager`
- `test-registry-manager` 負責：
  - 掃描 folder-level `TESTS.md`
  - row reconciliation / duplicate ID / stale row / missing evidence 檢查
  - workspace `.agents/specs/TESTS.md` rollup refresh
  - 產出 drift / gap summary
- `review.md` 仍是最終 verdict authority；`test-registry-manager` 不可自行裁決 PASS / FAIL / CONDITIONAL readiness。

---

### 14. 專案 Review 工具整合（Capability-Gated Project Review Tooling）

若 `code-review` skill 家族（`code-review` 本體與其 depth-review 同伴 `test-quality-reviewer`、`code-refactoring-advisor`、`test-design-generator`、`security-risk-reviewer`、`sonarqube-bridge`，跨 model 獨立複核 `cross-agent-review`（`xreview`），以及前端 design/engineer/visual-review domain expert `frontend-designer`）**對當前 agent 可用**，SDD 應在對應階段把它們當成 **review / test / 前端設計與視覺複核的輔助輸入與 left-shift 偵測層**，但必須遵守 capability gate 與 authority 邊界：

- **Availability 的判定範圍**：「可用」**不限於當前 workspace 是否 vendor 了這些 skill**。這個家族由其專案的 `code-review-publish` 流程發布到 global skill homes（`~/.claude/skills`、`~/.config/opencode/skills`、`~/.kiro/skills`、`~/.codex/skills`、`~/.gemini/config/skills`），因此一旦發布，它在該機器上的 **每個 workspace 都可用**。判定順序：workspace-local skill → global skill home → 對 `code-review` 而言還包含已發布 bundle 內的 `review-cli-<os>-<arch>` binary（PATH 或 bundle `scripts/`）。任一來源命中即視為可用。
- **兩層可用性判定（Skill present ≠ Dependency ready）**：capability gate 必須分清兩件事——(1) **skill 本身可用**（workspace / global / binary，如上），與 (2) **該 skill 的外部依賴是否就緒**。許多 skill 依賴本機尚未必存在的外部資源：`sonarqube-bridge` 需要一個 **SonarQube 來源**（可達 server + token，或匯出的 issues 檔）；`security-risk-reviewer --explain` / 任何 LLM pass 需要已設定的 provider/creds；`code-review` 的 hybrid 檢索需要 embedding provider。判定規則：
  - **skill 不可用**（workspace 與 global 皆無）→ 沿用既有內建 gate，於 `review.md` 記「tool unavailable」。
  - **skill 可用但依賴未就緒** → 該工具 **honest no-op，絕不阻塞**；於 `review.md` 記「dependency not configured」（例：`SonarQube not configured`），**與 "tool unavailable" 區分**，因為兩者的後續補救動作不同（前者要裝/發布 skill，後者要設定服務/creds）。
  - **skill 可用且依賴就緒** → 才進入下方 conditionally-required 判定。
  - 任何具 deterministic / offline 模式的 skill（`code-review --graph-only`、`security-risk-reviewer` 不帶 `--explain`、`*_MOCK=1`）即使外部依賴缺席仍應跑其 offline 偵測；only 真正需要外部服務的增益部分才降級。
- **SonarQube 來源解析優先序（Shared > Local）**：SonarQube 是 **組織級 quality gate**，部門共用 server 才是 canonical authority。因此 `sonarqube-bridge` 解析其來源時，優先序固定為 **部門 / 共用 SonarQube server（含其 quality gate / token）> 本機 local SonarQube > 無**：
  - 同時存在共用與本機設定時，**必須採用部門共用 server**，不可因為本機方便就用 local 蓋過共用結果。
  - 只設定了 local 時才用 local，並在 `review.md` 標明 source 為 `local`（非 canonical 部門 gate），避免把 local 掃描誤當部門 verdict。
  - 部門 server 與本機皆未成功設定時（很可能的預設情況）→ 落入上方「dependency not configured」：honest no-op、不阻塞、記 `SonarQube not configured`。
  - 不論來源為何，SonarQube 的 quality-gate verdict 本身仍是 authoritative；`sonarqube-bridge` 只做 ingest + graph blast-radius / capability / remediation 排序，不改判 verdict。
- **Detect → Conditionally Required**：在 Phase 4 / Phase 5，若某個 skill 依上述範圍可用、其依賴就緒、且情境適用（語言受支援、觸及 trust boundary、或本次有變更測試），執行它即為 **required**，其輸出是 review 的 **required input**；依「兩層可用性判定」對 unavailable / not-configured 分別誠實記錄，避免 silent skip 造成 false-green。
- **Authority 不轉移**：這些工具只提供 **static / deterministic evidence**，永遠不是 verdict authority。最終 readiness 仍由 `review.md` 裁決；trust-boundary 結論仍由 global `security-review` gate 裁決；若採用 SonarQube，authoritative gate 仍是 SonarQube 本身，`sonarqube-bridge` 只負責 ingest + graph blast-radius / capability / remediation 排序。
- **Generators 永遠 advisory**：`test-design-generator`、`code-refactoring-advisor` 只提出建議（測試案例、refactor move + safety-net），由人決定採納；不得因工具輸出就自動改寫程式碼或 `TESTS.md`。
- **Compose, not replace**：`security-risk-reviewer` 是 deterministic、offline 的 OWASP / 風險 pre-flight，**餵給**既有的 mandatory `security-review` gate，而不是取代它。
- **Cross-Agent 獨立複核（`cross-agent-review` / `xreview`）**：讓**不同 model family** 的 agent 獨立跑一次 `code-review`，消除「作者審自己」的 blind spot。**這條 lane 的 owner 是 `cross-agent-review` skill**——SDD 只負責「何時觸發、傳 scope、把結果寫回 `review.md`」，並把它導引過去；**不得** re-implement 機制、hard-code `--host-agent`、或假設固定的作者/reviewer 配對。作者可為 claude / codex / opencode / kiro / antigravity 任一，reviewer 由該 skill 的 model-card registry 自動偵測與挑選（**Claude↔Codex 只是 default preference，非寫死**）。它的兩層 gate 特別在第二層——除了 skill/binary 可用，還必須有**真正跨 family 的 reviewer + 憑證**（direct provider key 或 opencode Zen；`codex` 可走 exec；訂閱制 Claude Code CLI 因 ToS 不得當自動 reviewer，Anthropic-family 需 `ANTHROPIC_API_KEY`）。只有同 family 可用時**誠實降級**（`same-family-degraded`），絕不無聲自審。findings 併入 `review.md`，但 **`review.md` 仍是 verdict authority**；永遠 advisory、non-blocking。完整規範見 [references/CROSS_AGENT_REVIEW.md](./references/CROSS_AGENT_REVIEW.md)。
- **Graph Dogfooding Default**：對 non-trivial 工作（架構探索 / 影響分析 / 廣域 retrieval / spec handoff / 非瑣碎實作規劃），`code-review` 的 **code graph（見林）** 是 default context bootstrap，而非可選加值——preflight graph → 跑聚焦查詢 → 選 freshness trigger → 只在 stale 時 rebuild → **把 query 結果（或跳過理由）寫回 `design.md` / `review.md`**。graph 仍 non-blocking、非 authority，不得覆蓋 checked-out code / active spec / runtime proof。完整規範見 [reference/GRAPH_ASSISTED_PLANNING.md](./reference/GRAPH_ASSISTED_PLANNING.md)。
- **前端 design/engineer/visual-review（`frontend-designer`）**：**只在本 spec 有前端產出時**（web UI / 頁面 / 元件 / landing / dashboard / artifact，或變更 `.css`/`.scss`/`.html`/`.jsx`/`.tsx`/`.vue`/`.svelte`/樣式/版型）才觸發，補上 `code-review` 家族**完全不審前端**的缺口。它是整合的前端 domain expert：Phase 2 設計（design system → CSS-var tokens → layout、anti-slop）、Phase 4 實作 left-shift（shadcn / open-design / gstack-Pretext / A2UI）、Phase 5 **視覺複核**（render → 截圖 → 評 layout/階層/對比/品牌/a11y）。**這條 lane 的 owner 是 `frontend-designer` skill**，SDD 只導引過去、傳 scope、把結果寫回；它 composes 既有前端 skills（`shadcn`/`brand-guideline-company`/`web-artifacts-builder`/`frontend-patterns`/`webapp-testing`/`uat-demo-agent`），SDD 不 re-implement。Phase 5 的視覺複核**只提供 findings，不下 verdict**（與 `security-risk-reviewer` 同 pattern，`review.md` 仍是 authority）；視覺 lane 需 Playwright backend，受 `local-infra-registry-governance` gate。完整規範見 [references/FRONTEND_DESIGN_REVIEW.md](./references/FRONTEND_DESIGN_REVIEW.md)。

階段對應（皆 capability-gated）：

- **Phase 2 Design**：`code-review` 的 `impact` / `bounded-context` / `search-code --graph-only` 可佐證 `[Impacts: …]` 宣告與 lightweight FMEA 的 blast-radius。對 non-trivial 設計，graph 是 **dogfooding default**（preflight → 聚焦查詢 → 寫回 `design.md`，非 authority、non-blocking），細節見 GRAPH_ASSISTED_PLANNING.md。**若本 spec 有前端產出**，`frontend-designer` 的 Phase 1（設計）為前端設計輸入：確立 design system → CSS-var tokens → layout、載入 anti-slop / a11y 準則，寫進 `design.md`（capability-gated、advisory）。
- **Phase 3 Tasks**：`test-design-generator` 產生 boundary / equivalence / pairwise 候選案例，轉成 test obligations 與 `TESTS.md` 草稿列（advisory）。
- **Phase 4 Implementation（REFACTOR）**：`code-refactoring-advisor`、`test-quality-reviewer`、以及對 changed files 跑 `code-review`（含 `review --vet --race` 等背景經典問題偵測）為 left-shift（conditionally required，依語言 gate）。**前端變更**則以 `frontend-designer` 的 Phase 2（實作）為 left-shift：選 render target（shadcn / open-design / gstack-Pretext / A2UI）、tokens 用 CSS var、responsive / dark / a11y，並對照 anti-slop blacklist（conditionally required，有前端產出時）。
- **Phase 5 Review**：`code-review` 與 `test-quality-reviewer` 為 required inputs（非 verdict）；`security-risk-reviewer` pre-flight 餵 security-review gate；**`cross-agent-review`（`xreview`）在有跨 family reviewer 憑證時為 required input**——跑一次獨立跨 model 複核、把 outcome 與 findings 記入 `review.md`，無跨 family 可用時誠實降級；**前端變更時 `frontend-designer` 的 Phase 3（視覺複核）為 required input**——static（CSS/JS/HTML 對 design-system 的遵循）+ visual（render→截圖→評 layout/階層/對比/品牌/a11y），findings 併入「設計一致性 / 程式碼品質」，只給 findings 不下 verdict；若組織採用 SonarQube，`sonarqube-bridge` 為 optional enrichment。

- 💡 **原因 (WHY)**：spec-driven-development 是跨 workspace 的 global skill，不能 hard-couple 任一專案的工具。但 capability gate 的 availability 必須以「agent 是否真的可呼叫到該工具」為準，而非「當前 workspace 是否自帶」——因為這個家族一旦透過 `code-review-publish` 發布到 global homes，就在該機器的每個 workspace 都可用，若仍以 workspace-local 判定會讓 gate 不當休眠（少跑了實際可用的偵測，等於另一種 false-green）。以「workspace 或 global 任一可用即 required、皆不可用才記錄不可用」兼顧嚴格度與通用性，同時保住 readiness / security / SonarQube 的 authority 不被 static 工具稀釋。

---

### 15. 最小實作紀律 (Minimal Implementation Discipline — Ponytail YAGNI Ladder)

在新增任何程式碼、元件、依賴或抽象之前，必須依序走完 **Ponytail 6-Rung Ladder**，並在設計或實作文件中**展示思考過程**。

> 來源：改編自 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)，MIT License。原始說明：「Makes your AI agent think like the laziest senior dev in the room. The best code is the code you never wrote.」

**六級階梯**：

```
1. Does this need to exist?   → no: skip it (YAGNI)
2. Stdlib does it?            → use it
3. Native platform feature?   → use it
4. Installed dependency?      → use it
5. One line?                  → one line
6. Only then: the minimum that works
```

**核心規則**：

- **Lazy, not negligent**：trust-boundary validation、data-loss handling、security、accessibility 永遠不在精簡範圍內。
- **展示，不強制**：ladder 是「必須展示思考過程」的決策框架，不是「無論如何都必須最少行數」的硬性約束。若可讀性、可測試性、或架構一致性要求多一層抽象，應在展示中說明理由。
- **與 Code-Review Skill 協作**：ladder 是設計與實作階段的「前置自我檢視」；`code-review` 家族（`code-refactoring-advisor`、`test-quality-reviewer`、`security-risk-reviewer`）是複核階段的「left-shift 偵測」。兩者協作方式詳見 `references/ponytail-yagni-ladder.md`。

**階段對應**：

- **Phase 1 Requirements**：以 **Rung 1** 過濾 speculative 需求。在 `requirements.md` 中展示「為何這個需求需要存在」。
- **Phase 2 Design**：以 **Rung 2-4** 指導技術選型。對每個新 dependency 或元件，展示「為何標準函式庫 / 原生平台 / 現有依賴無法滿足」。
- **Phase 4 Implementation**：以 **Rung 5-6** 指導實作體積。在「思考過程展示」中回答「能否用更少程式碼完成」與「是否為最小可用實作」。
- **Phase 5 Review**：`code-review` diff review 應檢查新引入的 dependency 是否有 ladder 紀錄；若無，標記為 `over-engineering risk`。

**詳細規範、展示格式範例、與 code-review skill 協作模式**請參閱：
- [references/ponytail-yagni-ladder.md](./references/ponytail-yagni-ladder.md)

- 💡 **原因 (WHY)**：YAGNI 與 KISS 是 AGENTS.md 的核心設計原則，但缺乏操作化的檢查步驟。Ponytail ladder 提供具體的 rung-by-rung 決策流程，把「避免過度設計」從口號轉成可追溯的設計與實作紀律。

---

## 互動與執行指導

### 階段切換與判斷

- 通過檢查 `.agents/specs/{spec-directory}/` 下的文件是否存在，來判斷當前處於哪個階段。
- 若 `NEXT_STEPS.md` 存在，必須先用它確認當前 active spec、阻塞點與 resume target，再決定要讀哪些 spec 文件；但不可只憑它跳過 `SPECS.md` 的治理檢查。
- **無需詢問用戶「是否繼續」**。請使用自然語言對話，例如：「需求看起來完整了，我們可以開始架構設計了嗎？」
- 只有在用戶明確授權後，才能正式推進到下一個階段並寫入文件。

### 任務執行紀律 (Phase 4)

- **每次只專注並執行一個任務**。任務開始前，將大任務分解為子任務 To-dos（精確到每一步）。
- 在修改任何程式碼之前，**必須展示思考過程**：問題分析、方案選擇依據、規範依據、參考程式碼。
- 針對超過 5 行的命令列腳本，將其寫入臨時文件（如 `temp/run.sh`）再執行，避免在 terminal 直接輸入長指令。
- 長時間測試 (Regression / PBT) 設定 timeout，若發現少量錯誤 (<10) 應立即追蹤修復，再重新測試。
- **Git 綁定**：提交程式碼時，Git Commit Message 必須附帶 `Ref: {spec-name}` 或 `Ref: {REQ-ID}`。

### TESTS.md Refresh / Closeout Flow

若本次 spec 影響 test catalog、test evidence、或 requirement / AC traceability，closeout 前至少執行以下順序：

0. （capability-gated）若 `test-quality-reviewer` 可用（workspace-local 或 global skill home 皆算，見 Global Constraint #14），先對本次新增 / 變更的測試跑一次品質檢查（FIRST / test-smell / pyramid），把 findings 當成 closeout 的 **quality input**。此步驟只負責測試品質，不取代 step 1–2 的 registry 治理（仍屬 `test-registry-manager`），也不改寫 `review.md` 的 verdict authority。
1. 更新 folder-level `TESTS.md` row-level authority（test IDs、trace refs、canonical commands、evidence refs）
2. 若 workspace 採用 `.agents/specs/TESTS.md`，使用 `test-registry-manager` 刷新高階 rollup
3. 若 workspace 採用 `RTM.md` / `SPECS.md` snapshot，僅在 upstream authority 完整後進行 single snapshot write
4. 在 `review.md` 中裁決 acceptance / readiness verdict

禁止跳過 folder-level authority，直接更新 workspace rollup。

### 遇到阻礙時

- 若任務中斷或出錯超過預期，不要盲目猜測。請在 `.agents/specs/{spec-directory}/reports/` 留下卡關報告。
- 在任何中斷、換 session、或等待外部回覆前，必須同步更新 `{workspace}/.agents/specs/NEXT_STEPS.md`，留下最後驗證狀態、阻塞原因與建議恢復入口。
- 針對重複發生的錯誤，主動記錄至 `.agents/steering/lesson-learned.md`，以利未來 Agent 參考。
