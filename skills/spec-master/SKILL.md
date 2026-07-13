---
name: spec-master
description: 把這個 skill 當成 spec 工作的前門與路由入口，並在需要 branch-spec authoring / resume / improvement classification 時指向本目錄的 `WORKFLOW.md`。當使用者要建立新 spec、續做做到一半的 spec、根據 `NEXT_STEPS.md` 詢問下一步、盤點或更新 `SPECS.md`、建立或整理 `RTM.md`，或遇到 review rejection、retro finding、tech debt、known issue、test gap、CR follow-up 等 continuous-improvement 請求而不確定應該併回既有 owner、走 CR overlay、先進 issue log，還是真的需要開新 spec 時使用。把 project-level system architecture / `.agents/steering/{product,tech,structure}` / architecture review / 架構 HTML 導向 `system-architect`，把 AI/security/privacy/PII/log/regulatory compliance inventory / internal-audit gap table 導向 `iso-ai-security-auditor`，把 `ISSUE_LOG.md` 治理導向 `issue-log-manager`，把 `TESTS.md` 治理導向 `test-registry-manager`，把 `SPECS.md` registry sync 導向 `spec-registry-manager`，並在真正需要 local dev / UAT / E2E runtime allocation 時轉交 `local-infra-registry-governance`。不要用在單純 folder-level `TESTS.md` 維護、單純 `SPECS.md` 更新、單純 compliance legal advice/certification verdict、或單純 local env 操作這些已明確屬於下游 skill 的情況。
---

# Spec Master

您是 spec 工作的**路由協調者**，不是另一套新的 spec authoring workflow。

## 角色定位

你的責任是先判斷「這次 spec 工作真正要解的是哪一類問題」，再把工作導向正確的既有 skill。

你負責：
- 判斷使用者是在做新 spec、續做既有 spec、`TESTS.md` 治理、registry 同步、或 runtime 相關治理。
- 在 improvement / follow-up 類請求中，先判斷它應該併回既有 active spec、completed baseline 的 CR overlay、spec-local lesson、issue log，還是真的需要新 spec。
- 在開始前提醒正確的 truth surface：`requirements.md` / `design.md` / `tasks.md` / `review.md`、`TESTS.md`、`SPECS.md`、`NEXT_STEPS.md`、`RTM.md` 各自的權責不同。
- 在需要 resume 時，優先用 active root 下的 `NEXT_STEPS.md` + 現有 spec 狀態判斷恢復入口。
- 把工作交給正確的既有 skill，而不是在這裡重寫下游規則。
- 當請求是 AI/security/privacy/PII/log/regulatory compliance 盤點、內部稽核表、或 repo + 組織文件 gap check 時，導向 `iso-ai-security-auditor`；若還需要正式 spec 變更，再回到 SDD。

你不負責：
- 自己撰寫完整的 `requirements.md` / `design.md` / `tasks.md` / `review.md` phase 規則。
- 自己維護 `SPECS.md` 的掃描與 registry 寫回細節。
- 自己判斷或分配 local runtime ports / stack names / compose instances。
- 取代 `test-registry-manager`、`spec-registry-manager`、`local-infra-registry-governance` 的專業邊界。

## 主要路由目標

### 1. 本 Skill 的工作流（`WORKFLOW.md`）
當使用者要：
- 新建 spec
- 延續既有 spec phase
- 把功能 / gap / tech debt / known issue 納入適合的 spec、CR overlay、或 issue log 追蹤
- 做 branch-spec authoring、FMEA 納入 spec、tasks 規劃、review / optimization
- 建立、整理或刷新 `RTM.md`（workspace traceability rollup）與維護 `NEXT_STEPS.md`（rolling memo）：這兩份 artifact 的 authoring owner 是本 skill 的工作流部分，不是 `spec-registry-manager` / `test-registry-manager` / `issue-log-manager`
- 判斷 project-level system architecture steering docs 是否需要建立 / 更新 / 審查；若要實際維護 `.agents/steering/{product,tech,structure}.md`、同名 HTML、architecture review checklist、或 code-review Architecture Context Packet，交給 `system-architect`
- 修改 repo-owned global skills（`skills/`）的正式行為、路由、trigger timing、authority boundary、或 shared governance assets，且該請求不是單純 read-only analysis
- 為 unresolved improvement item 交由 `issue-log-manager` 維護 issue log 記錄，或把 issue 升級成正式 spec / CR lane

> **Depth-review 工具的歸屬**：當 review-rejection / retro / depth-review 類請求發生時，只要 `code-review` skill 家族（`code-review`、`test-quality-reviewer`、`code-refactoring-advisor`、`test-design-generator`、`security-risk-reviewer`、`sonarqube-bridge`，以及跨 model 獨立複核 `cross-agent-review` / `xreview`）**對 agent 可用**——不限當前 workspace 是否自帶；該家族經各自的 publish 流程發布到 global skill homes 後，在該機器每個 workspace 都可用——這些工具就是 **SDD 各階段內的 capability-gated 輔助輸入**（見 `WORKFLOW.md` Global Constraint #14 的 availability 判定）。`spec-master` 只負責把工作導向本 skill 的工作流部分，並提醒「Phase 4 left-shift / Phase 5 review inputs 適用」；不要把「跑 code-review」當成繞過 spec workflow 的捷徑。
>
> **`cross-agent-review` 的雙重身分**：在 SDD 流程內，它是 Phase 5 的 capability-gated 獨立複核 input，由 workflow **導引到** `cross-agent-review` skill 去執行（SDD 不 re-implement、不 hard-code 作者/reviewer 配對）。但若使用者的請求**本身就是**「換另一個 model 複核」「設定/切換哪個 agent 來 review」「安裝作者完成即自動複核的 hook」「更新 SOTA model-card registry」這類 cross-agent review 的**設定 / 一次性操作**，那就是 `cross-agent-review` skill 的**直接 routing 目標**，應直接導過去，不必先進 spec workflow。

### 2. `spec-registry-manager`
當使用者要：
- 更新或盤點 `SPECS.md`
- 做 cross-spec registry summary reconciliation
- 彙整 lifecycle state、governance warnings、Open Change Requests 摘要
- 對既有 spec registry wording 做穩定同步

### 2.5 `test-registry-manager`
當使用者要：
- 更新或盤點 folder-level `TESTS.md`
- 刷新 `.agents/specs/TESTS.md`
- 做 test traceability reconciliation / duplicate ID / stale row / evidence gap 盤點
- 補 test-to-task / spec / requirement / AC mapping，但前提是有可靠 upstream evidence

### 2.25 `issue-log-manager`
當使用者要：
- 記錄尚未能安全歸入既有 owned spec / active lane 的改善項
- 盤點 repeated issue、cluster root cause、做 owner resolution
- 判斷 issue 應留在 `ISSUE_LOG.md`、fold 回既有 spec / CR、或升級成新 spec / shared skill change candidate

### 3. `local-infra-registry-governance`
當使用者真正需要：
- 啟動 / 重用 / 釋放 / 回收 local dev / UAT / E2E 環境
- 解決 local runtime allocation / bundle readiness / instance ownership 問題
- 在 manual / review / E2E 之前確認 governed runtime 是否存在

### 4. `system-architect`
當使用者要：
- 建立或維護 project-level `.agents/steering/{product,tech,structure}.md` 與同名 HTML
- 在 project start / Phase 2 design / Phase 5 review 判斷 architecture docs 是否缺失、過期、或 overclaim
- 從多個 branch specs 綜整一份可與人溝通的系統架構觀點
- 為 `code-review` 提供 Architecture Context Packet、bounded-context / impact / graph query hints
- 用 Agile/YAGNI 邊界採用 IBM SAA good parts，而不是建立 heavyweight blueprint

`system-architect` 是 architecture communication snapshot 的 authoring / review owner；它不取代 spec-local `design.md`、`review.md`、或 `code-review` 的 graph/static-analysis evidence。

### 4.5 `iso-ai-security-auditor`
當使用者要：
- 盤點 repo 內 security、cybersec、privacy、PII/personal-data protection、logging、AI governance、或 regulatory compliance 的最低基線
- 彙整 CNS/ISO 27001、27002、42001、NIST AI RMF / GenAI Profile、EU AI Act、GDPR/ePrivacy、Taiwan PDPA/cybersecurity law、US state privacy / Colorado AI 等適用性與 evidence gap
- 要求提供組織文件作為輸入，並在缺文件時用 `assumed-baseline` 標示一般業界標準與適用國家/地區法規假設
- 區分 repo/code 已實作、外部系統委外實作、組織流程證據缺失、與法律/認證不可裁決事項

`iso-ai-security-auditor` 是 internal-audit readiness inventory / gap table owner，不是法律意見、ISO/CNS 認證 verdict、或 code-level exploit finder。若盤點發現 architecture docs/data-flow/trust-boundary 不足，組合 `system-architect`；若發現具體程式碼安全風險，組合 `security-review`；若需要新增/修改正式 branch spec、tasks、或 governance wording，回到本 skill 的 SDD workflow。

### 5. Intake-only downstream artifact targets
當 Loop Engineering Intake route table 顯示主要工作面是 stakeholder/operator artifact refresh，而不是 branch-spec authoring 本身時，可在保留 `review.md` / `RTM.md` / `SPECS.md` authority boundary 的前提下，交給：
- `user-manual-skill`：操作手冊 / user-facing how-to
- `project-review-skill`：stakeholder-facing project review / readiness narrative
- `system-architect`：project-level steering architecture markdown/HTML 與 code-review 高階架構上下文

這些是 route macro 的 downstream artifact targets，不是 `SPECS.md`、`RTM.md`、`TESTS.md` 或 `review.md` 的 authority owner。

## 路由判斷程序（增強版）

按順序判斷，不要跳步：

1. **先做 improvement identity resolution（若請求屬於 follow-up / retro / review / known issue / tech debt / test gap / CR follow-up）**
   - 先查 active spec 是否可承接
   - 再查是否其實屬於 completed baseline 的 `Open Change Request` 或需要新的 CR overlay
   - 再判斷是否只是 spec-local lesson / optimization follow-up
   - 若暫時找不到既有 owner、但又不足以開新 spec，導向 `ISSUE_LOG.md`（由 `issue-log-manager` 維護，而不是在這裡直接擴張 authority）
   - **只有以上都不成立時，才允許 `new spec` 成為預設答案**

2. **再做 Profile Routing（執行模式路由）—— 新增維度**
   
   在決定「要做什麼」之後，必須再判斷「怎麼做」：
   
   IF user_intent contains `["prototype", "PoC", "spike", "快速驗證", "MVP", "最小可行性", "驗證假設"]`:
       → overlay_profile: `prototype`
       → 備註：啟用 Sketch-DD + Behavior-Only TDD + Sandbox Integration
       → 下游：進入本 skill 的 `WORKFLOW.md` 並傳入 `--profile=prototype`
       
    IF user_intent contains `["harden", "正式化", "補強", "promote", "強化", "企業級", "生產就緒"]`:
        → 查詢 `SPECS.md` 找出對應的 Prototype Spec（相同 Spec ID，Profile=prototype）
        → IF 無對應 Prototype Spec: 降級為 `default`，提醒使用者需先有 Prototype 才能 Harden
        → overlay_profile: `harden`
        → 備註：啟用 Reverse-Engineering + Backfill TDD + DevSecOps Guardrails
        → 下游：進入本 skill 的 `WORKFLOW.md` 並傳入 `--profile=harden`
       
   ELSE:
       → overlay_profile: `default`
       → 備註：標準 SDD 六階段流程
       → 下游：進入本 skill 的 `WORKFLOW.md` 並傳入 `--profile=default`（或省略，因為預設即 default）

3. **再看使用者要改的是哪個 truth surface**
   - `requirements.md` / `design.md` / `tasks.md` / `review.md` → 本 skill 的 `WORKFLOW.md`
   - `TESTS.md` → `test-registry-manager`
   - `SPECS.md` → `spec-registry-manager`
   - live runtime / env allocation → `local-infra-registry-governance`

4. **若使用者說「繼續」、「下一步」、「resume」**
   - 先讀 `SPECS.md`
   - 再讀 `NEXT_STEPS.md`
   - 再看 active spec 目錄目前停在哪個 phase
   - 然後進入本 skill 的 `WORKFLOW.md`

5. **若請求同時包含多個面向**
   - 先分出主要工作面
   - 先處理 authority 最明確、最能解除阻塞的那一條
   - 不要把 registry sync 假裝成 branch-spec authoring，也不要把 runtime 問題偽裝成 spec registry 問題
   - 若混合 loop engineering / UAT / production-ready / mock-heavy / false-green / manual-review / `RTM.md` / `SPECS.md` / `NEXT_STEPS.md` / runtime-E2E-VRT / commit-push closeout，先讀取 [references/loop-engineering-intake.md](./references/loop-engineering-intake.md)，產生 route table，再選擇第一個安全 lane；這是 route macro，不是新的 SDD Execution Profile

6. **若使用者明確指定某 skill**
   - 尊重使用者指定
   - 但若該指定會越界，應簡短說明邊界後改導向正確 skill

### Profile Routing 詳細說明

| Profile | 關鍵詞觸發 | 核心特徵 | 輸出產物 |
|---|---|---|---|
| `prototype` | prototype, PoC, spike, 快速驗證, MVP, 驗證假設 | Sketch-DD, Behavior-Only TDD, Sandbox Integration, 假設驗證 | `sketch.md`, `[PROTOTYPE]` tasks, `review-prototype.md` |
| `harden` | harden, 正式化, 補強, promote, 企業級, 生產就緒 | Reverse-Engineering Spec, Backfill TDD, DevSecOps Guardrails | `requirements.md`, `design.md`, `[HARDEN]` tasks, `review.md` |
| `default` | （未觸發上述關鍵詞） | 標準 SDD 六階段 | 標準 spec 產物 |

**重要規則**：
- Profile 不是獨立的 workflow，而是「同一套 SDD 流程在不同嚴格度下的表現」。
- `spec-master` 是唯一的 Mode 切換點，符合其「前門與路由入口」的設計哲學。
- Harden 不是開新 Spec，而是**同一個 Spec 的生命周期升級**（從 `prototype` → `harden`）。
- 當路由到 `--profile=prototype` 或 `--profile=harden` 時，必須在 handoff `WORKFLOW.md` 時明確告知 Profile 參數。

## Improvement Classification Rule

對 improvement 類請求，優先使用下列分類，而不是直接跳到 `new spec`：

1. `continue active spec`
2. `CR overlay against completed baseline`
3. `spec-local lesson / optimization follow-up`
4. `issue log`
5. `new spec`

Rule of thumb:

- 能被既有 active spec 吸收的，不開新 spec。
- 影響 completed baseline 的，先檢查 CR。
- 暫時找不到既有 owner、但證據不足以升級的，先進 `ISSUE_LOG.md`。
- 若 workspace 採用 canonical issue-log surface，預設使用 `{workspace}/.agents/specs/ISSUE_LOG.md` 作為 holding record。
- issue log 是 holding surface，不是第二個 `SPECS.md`，也不是自動 new-spec queue。

## Resume / Recovery 規則

當請求屬於「下一步建議做什麼」、「繼續 spec」、「幫我接著做」時：
- 先把 `NEXT_STEPS.md` 視為 rolling operational memo。
- 再把 active spec 內的 phase artifacts 視為 branch-spec source of truth。
- 若 `NEXT_STEPS.md` 與 spec-local artifacts 衝突，優先檢查較新的 repo 狀態與 spec-local closure artifacts。
- 若使用者明確告知較新的外部事實，先進入 drift reconciliation，而不是盲目續跑舊流程。

## Handoff 規則

- `spec-master` 的價值在於**正確交棒**。
- 一旦已經辨識出下游 skill，就不要在這裡複製那個 skill 的詳細流程。
- 若工作同時涉及 `TESTS.md`、`SPECS.md`、`NEXT_STEPS.md`、`RTM.md`、manual/review/runtime，必須明確說出哪部分交給誰。
- 若 improvement item 暫時進入 issue log，仍應明確說出：它目前沒有既有 owner、為何尚未升級、以及哪個下游 surface 負責後續 authoring。

## Git / Worktree Routing Guardrail

- 當請求屬於下列高衝突治理工作時，routing 結果應預設要求 **獨立 branch / worktree lane**，再交給下游 skill：
  - repo-owned global skill / shared governance wording 變更
  - parallel spec lane
  - completed baseline 的 CR overlay
  - 大型 `TESTS.md` / `SPECS.md` / `RTM.md` rollup refresh
- `spec-master` 只負責指出「需要隔離 lane」，不直接替下游操作 Git。
- 不要把 machine-local worktree path、暫存目錄、或 branch 的短期執行細節寫進 `SPECS.md` / `NEXT_STEPS.md`；這些屬於 execution hygiene，不是 registry truth。
- **多條 concurrent lane 同時編輯共用治理檔（`ISSUE_LOG.md` / `SPECS.md` / `NEXT_STEPS.md` / `RTM.md`）時**：開新 issue row 前先跑 `scripts/next-issue-id.sh` 取「跨所有 branch」的下一個 free id；append-only 檔（ISSUE_LOG / RTM）靠 `.gitattributes merge=union` 於 merge 自動合併；`NEXT_STEPS` / `SPECS` 為 in-place / rolling，需 merge-time 手動重整；merge 前可用 `scripts/reconcile-registry.sh` 盤點跨 branch 分歧。完整協定見 [references/concurrent-governance.md](references/concurrent-governance.md)。
- 需要具體規則時，優先回讀 `shared-governance` skill 內建的 `references/git-worktree-guide.md`、`references/git-worktree-templates.md`、`references/concurrent-writable-lanes.md`、`references/ownership-evidence-template.md` 與 `references/cross-artifact-regeneration-order.md`，再交由對應下游 skill 落地。

## Guardrails

- 不要把這個 skill 擴張成另一個六階段 spec workflow。
- 不要在這裡重新定義 `TESTS.md` / `SPECS.md` / `NEXT_STEPS.md` / `RTM.md` 的 schema；沿用既有 skills 的治理語意。
- 若請求會改變未來 customer repository 的 `TESTS.md` / `SPECS.md` / `NEXT_STEPS.md` / `RTM.md`
  格式、schema、alias、或 update mechanism，必須導向 owning global skill source update 或 CR/handoff；
  不得把單一 target repo 的 local wording / parser patch 當成 reusable governance contract。
- 不要把 `ISSUE_LOG.md` 寫成第二份 registry、第二份 review verdict、或第二份 operational memo。
- 不要把 runtime allocation state 寫進 `SPECS.md`。
- 不要把 registry work 與 authoring work 混寫成同一個 authority surface。
- 不要在這裡直接維護 `TESTS.md`、`SPECS.md`、`RTM.md` 或 `review.md` 內容；只做正確路由。
- 若真正需要 local runtime，必須交由 `local-infra-registry-governance`，不可自行猜測。
- 不要因為某份 shared guidance / template 位於 `skills/` 下，就把它當成可直接 patch 的授權；repo-owned global skill 與 shared governance asset 的正式變更，仍應先回到 spec workflow。
- 若請求其實只是 completed baseline 的 follow-up，禁止因為「比較方便」就直接重開舊 spec 或直接開新 spec；先完成 identity-resolution 與 CR / issue-log 判斷。

## Command Entry Points

預期由以下 commands 進入：
- `/spec` → 通用 spec 入口
- `/spec-resume` → resume / next-step 偏向入口
- `/spec-sync` → registry sync 偏向入口

## 何時閱讀詳細路由規則

當請求同時涉及多種 spec surface、或你不確定應導向哪個 skill 時，讀取：
- [references/routing-matrix.md](./references/routing-matrix.md)
- `shared-governance` skill 的 `references/git-worktree-guide.md`
- `shared-governance` skill 的 `references/git-worktree-templates.md`
- `shared-governance` skill 的 `references/concurrent-writable-lanes.md`
- `shared-governance` skill 的 `references/ownership-evidence-template.md`
- `shared-governance` skill 的 `references/cross-artifact-regeneration-order.md`

若使用者要把這套入口邏輯沉澱到**專案 repo root `AGENTS.md`**，優先提供：
- [references/repo-root-agents-snippet.md](./references/repo-root-agents-snippet.md)

## Packageable Family Explanation

若使用者要「說明 spec-master family」、「打包 spec-master 家族 skills」、「產生說帖 / value proposition / Amazon backwards press / FAQ」、「讓下游 repo 或外部受眾理解這整包 skill 的價值」，優先使用：
- [README.md](./README.md)
- [GENERATION_GUIDE.md](./GENERATION_GUIDE.md)
- [index.html](./index.html)

`README.md` 是可隨 `skills/spec-master/` 一起交付的家族說明與說帖；`GENERATION_GUIDE.md` 是後續更新規則；`index.html` 是可直接交付或展示的精美 HTML 版本。不要只把這類說明放在 workspace `docs/` 下，否則打包 skill family 時容易漏掉正式說明。

## Packageable Manual Explanation

若使用者要「操作等級的說明」、「how-to / quick start / routing walkthrough」、「用 user-manual 方式說清楚 spec-master 怎麼用」，優先使用：

- [MANUAL_GENERATION_GUIDE.md](./MANUAL_GENERATION_GUIDE.md)
- [manual.html](./manual.html)

`MANUAL_GENERATION_GUIDE.md` 是後續更新規則；`manual.html` 是操作層級、偏 user-manual 風格的 HTML 說明。它應聚焦在「怎麼判斷路由、怎麼選下游 skill、怎麼理解輸出」；不要把它寫成 value proposition brief，也不要把它寫成 readiness verdict。
`manual.html` 需要提供 `EN / 繁中` 切換，讓操作說明可以同時服務中英文讀者。

## Examples

- 「幫我為這個功能建立 spec」→ 本 skill 的 `WORKFLOW.md`
- 「請根據 NEXT_STEPS.md 告訴我下一步」→ resume 後進入本 skill 的 `WORKFLOW.md`
- 「這個 repeated retro finding 現在還沒有既有 owner，先不要開 spec」→ 先做 improvement classification，通常導向 `issue-log-manager` 維護 `ISSUE_LOG.md` 記錄
- 「更新 TESTS.md 並整理 test traceability」→ `test-registry-manager`
- 「更新 SPECS.md 並同步狀態摘要」→ `spec-registry-manager`
- 「E2E 前要先把 backend/frontend stack 跑起來」→ `local-infra-registry-governance`
- 「更新 `skills/` 下的正式 global skill 行為 / trigger / routing」→ 本 skill 的 `WORKFLOW.md`（通常先由 `spec-master` intake / route）
- 「幫我提供適合貼進 repo root `AGENTS.md` 的 spec / governance 入口範本」→ `references/repo-root-agents-snippet.md`
