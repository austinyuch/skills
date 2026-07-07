# 第二階段：架構設計

## 觸發條件

- 需求文件已完成並獲得您的認可
- 或您明確表示要設計技術方案

## 我的工作

1. **(新增) 漸進式逆向工程 (Just-in-Time Retrofitting)**：
   - 若新需求牽涉到缺乏 Contract 定義的舊有模組，請先閱讀舊有程式碼。
   - 進行「反向推導」，將該舊模組的資料結構與 API 提取並定義到 `{workspace}/contract/` 中。
   - 寫入或更新 `SPECS.md`，將該舊模組標記為 `[Retrofit]`。
   - 若舊系統過於龐雜難以一次性抽取，請在 Contract 內定義防腐層 (Anti-Corruption Layer) 介面以隔離舊有黑箱邏輯。

2. **(新增) 契約優先 (Contract-First)**：
   - 如果這是一個涉及 API、資料儲存或模組通訊的新功能，必須優先在 `{workspace}/contract/` 下定義資料模型與介面契約（如 `openapi.json`, `JSON Schema`, `TypeSpec` 或 Prisma Schema）。
   - **(FMEA 防範：模組化 Contract)**：不要將所有定義塞進單一巨型 `openapi.json` 中（這會導致 Git 衝突與 Context 溢出），請建立模組化的契約檔案，例如 `contract/user-auth.yaml`。
   - 確保 `{workspace}/contract/` 成為後續開發的 Single Source of Truth (SSOT)。
   - 若此契約由外部系統主導，必須在 design 中額外宣告：`Contract Authority`、`Source of Truth`、`Pin/Version`，讓後續實作知道本地 contract 是同步對應，不是上游權威來源。
   - **(FMEA 防範：即時語法驗證)**：建立 Contract 檔案後，**必須**立即執行對應的檢查工具（如 `swagger-cli validate` 或 `npx @redocly/cli lint`）以確保語法和結構正確，避免將錯誤的契約推遲到程式碼生成階段。

3. 調整到 ultrawork 模式，完全了解專案程式碼與規範，收集足夠完整的上下文。
4. 仔細研讀已有的需求文件 (`requirements.md`)。
4.1 **(新增) 深度設計訪談 (Value Lens + Grilling)**：預設啟動、可隨時跳過。完整方法論見 [`references/requirement-interview-depth.md`](../references/requirement-interview-depth.md)。
   - 沿設計決策樹**逐題追問**：架構選型 → 契約邊界 / SSOT → 元件職責 → 失敗模式 → 可觀測性。一次只問一題、每題附建議答案、能從 codebase 查到的先查不問。
   - 以 **CEO 高階價值視角** 挑戰技術前提：這個架構/方案為何優於替代方案（與下方 alternatives 呼應）？哪些可逆 (雙向門) 可快速決定、哪些不可逆 (單向門：資料模型、對外契約、安全邊界) 需放慢逼出更多資訊？
   - 訪談結論落地為 `design.md` 的設計決策與理由；被排除的替代方案以一行「為何排除」記錄，方便追溯。
4.2 **(新增) Compliance Inventory Design Hook**：若 Phase 1 觸發 `iso-ai-security-auditor`，必須把其 control / legal / log / AI governance inventory 轉成設計期的 evidence boundary，而不是只放在附錄。
   - 在 `design.md` 納入 AI component boundary、PII/data flow、log/telemetry flow、trust boundary、external-control owner、evidence refs、以及 missing-evidence items。
   - 區分 code-implemented control、external-implemented control、organization-process evidence、與 assumed-baseline；不得把 vendor feature、planned task、或未提供文件寫成已實作控制。
   - 若需要修改整體 architecture docs，交由 `system-architect`；若需要新增正式 remediation tasks，進入 Phase 3 tasks planning。
5. 讀取最新的 `{workspace}/.agents/specs/NEXT_STEPS.md`（若存在），確認 current phase、候選 impacted specs、open CRs、以及上次 session 留下的 resume hint；若內容已過時，必須以 `SPECS.md` 與 active spec 文件校正。
5.1 若本次設計涉及治理 artifacts、需求追溯、issue-log promotion / fold-back、RTM refresh、或 registry/test rollup，必須讀取 `../reference/SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md`，並在 `design.md` 中明確說明本 spec 的 artifact authority model。
6. 創建 `.agents/specs/{spec-directory}/design.md` 文件。文件開頭必須說明相關章節的引用參照。
6.1 **(新增) Ponytail Rung 2-4 技術選型過濾**：在設計中決定引入新 dependency、新元件、新抽象或新模組時，必須展示 ladder 思考：
   - **Rung 2**：語言標準函式庫是否已經提供此功能？
   - **Rung 3**：當前執行平台（作業系統、runtime、硬體、或框架）是否提供原生能力？
   - **Rung 4**：專案現有依賴中是否已有可解決此問題的套件？
   - 若 rung 2-4 任一通過，**優先使用既有能力**，不引入新 dependency。
   - 若必須引入新 dependency，應在 `design.md` 的「架構」或「技術選型」段落明確說明「為何 rung 2-4 無法滿足」，並記錄選型理由。
   - 參考：[`references/ponytail-yagni-ladder.md`](../references/ponytail-yagni-ladder.md)
7. 包含以下必需部分：
   - **概述** - 功能總覽
   - **架構** - 系統架構設計
   - **Test Coverage Declaration** - 宣告預期需要哪些 test tags、哪些 critical journeys 至少需要 real-wired evidence、哪些 mock 只能作為輔助
   - **Repo-side Closure vs External Execution Boundary** - 在 design 中明確聲明 branch-spec 層的本地完成範圍、外部執行範圍、authoritative handoff artifact / owner，以及哪些內容只是 external blocker；後續 `tasks.md` 只能鏡射這個區分，不得自行發明。
   - **契約定義 (Contracts)** - 指向 `{workspace}/contract/` 內具體定義檔的路徑。
   - **組件和介面** - 各組件詳細說明
   - **Graph-Assisted Architecture Insights** - 若執行 graph 查詢，記錄它作為輔助洞察，而不是 authority source
   - **Failure Mode and Effects Analysis (FMEA)** - 當功能涉及 external/shared contract、cross-spec rollup、stakeholder-facing artifact、high-risk auth/data/demo path、或任何 false-green / overclaim 風險時，必須加入 lightweight FMEA。
   - **Risk Response and Mitigation Plan** - 對 FMEA 中的高風險 failure modes 定義 Prevent / Detect / Contain 類型回應，並保留對應 task trace。
   - **錯誤處理** - 異常處理策略
   - **評估標準 (EDD)** - 依據需求定義此功能的成功標準。
   - **追溯參照 (Traceability References)** - 讓 workspace `RTM.md` 可以穩定聚合的 design identifiers / section refs。
   - **Governance Artifact Lifecycle** - 若本工作由 `ISSUE_LOG.md` promoted / folded 而來，或會影響 `NEXT_STEPS.md` / `TESTS.md` / `RTM.md` / `SPECS.md`，設計中必須寫清楚：哪個 artifact 是 upstream truth、哪些只是 derived rollup、何時刷新、何時不得寫入。

8. **相依與防漂移檢查 (Drift Prevention)**：
   - 在設計過程中，若發現需改動現有邏輯，必須在 `design.md` 中註明 `[Impacts: 舊spec名稱]`。
   - 若影響對象是 `[Completed]` spec、shared contract 或 external contract 假設，必須在 design 中引用對應 `Open Change Requests` 摘要，而不是把舊 spec 當成可直接覆寫的工作區。完整 CR 結構請沿用 [輕量 CR template](../../spec-registry-manager/references/change-request-template.md)。
   - 若改動了既有的 Contract，必須標註後續實作階段需執行全局型別檢查以修復漂移。
   - 在設計定稿前，必須重讀一次最新 `SPECS.md`，確認沒有新增的 overlapping CR、dependency 變化，或 external `Pin/Version` 漂移。
   - 若本 spec 涉及 external execution，design 必須明確標示 repo-side closure 的完成訊號、external execution 的權威執行位置、以及 authoritative handoff path；不得只寫模糊的「之後到外部驗證」。

9. 程式碼和設定檔範例保存在 `{spec-directory}/code` 並參照到該文件，以減少 context；若 `./scripts/{檔名}` 與規劃重複，請評估是否另行建立新的文件和檔名，並確保與 design.md 內的路徑一致，不要逕行覆寫
10. 視覺化設計（各種表格、流程圖、元件圖、循序圖等），請盡可能採用「Mermaid」語法繪製避免排版混亂
11. 確保設計解決需求明確過程中識別的所有功能需求
12. 突出設計決策及其理由
13. 在設計過程中可能就特定技術決策徵求您的意見
14. 將研究發現直接整合到設計過程中
14.1 **Graph Dogfooding Default（見樹又見林）**：對 non-trivial 設計（架構探索 / 影響分析 / 廣域 retrieval / spec handoff），`code-review` 的 code graph 是 **default context bootstrap**，不是可選加值。序列：先 preflight（tracked `.code-review/` snapshot 的 doctor 或 `index --status`）→ 若 stale 可背景更新（不得阻塞設計）→ 跑聚焦查詢。完整規範見 [`../reference/GRAPH_ASSISTED_PLANNING.md`](../reference/GRAPH_ASSISTED_PLANNING.md)。
14.2 graph 查詢 (`architecture`, `impact`, `bounded-context`, `dependency-path`, `search-code --graph-only`, `developer-routing`) 的結果只能作為 **design aid**，不得自動成為 truth，也不得覆蓋 checked-out code / active spec / runtime proof。
14.3 **Record-in-artifact**：若跑了 graph，`design.md` 至少要留下跑了哪些 query + 關鍵洞察 + `relation_coverage_status`（partial 要保守解讀）；若刻意**不**跑而改直接讀檔（見樹即可），也要一句話說明理由，不得無聲跳過。此紀錄是 derived note，不得反向覆寫 `SPECS.md` / `RTM.md` / `TESTS.md`。
15. **(新增) 風險前移規劃 (FMEA-lite)**：若本 spec 容易出現「planned 被寫成 executed」「summary 比 source 更樂觀」「warning code 在聚合過程中遺失」「artifact 誤導 stakeholder」等 failure mode，必須在 `design.md` 中加入輕量 FMEA 表，而不是等到 review 階段才補救。
15.1 若設計包含 `ISSUE_LOG.md`、`TESTS.md`、`SPECS.md`、`NEXT_STEPS.md`、`RTM.md` 等治理 artifact，必須明確定義 **Non-Cyclic Authority Model**，避免 derived artifact 互相回寫。
15.2 `RTM.md` 的設計角色是 requirement traceability rollup。design 應提供穩定 section refs / contract refs，讓 RTM 能追 requirement → AC → design → tasks → tests → review，但不得要求 RTM 反向生成 design。
16. FMEA 應保持 spec-local、輕量、可追溯；建議最少欄位為：`Risk ID`、`Failure Mode`、`Effect`、`Cause`、`Current Control`、`Severity`、`Occurrence`、`Detection Difficulty`、`Planned Response`、`Task Trace`。FMEA 應在此階段正式 authoring，不得延後到 review / closeout 才補寫。
17. 對每個 high/major risk，至少定義一種 `Prevent`、`Detect`、或 `Contain` 類型的 mitigation response；若 first slice 內無法完全消除，必須明確規劃 conservative fallback（例如 `gap` / `blocked` / `not_assessed` / warning code propagation），而不是把風險留成隱性假設。
18. 若存在 `Open Change Requests` 或 `Contract Authority=external` 的相依，設計中必須明確寫出後續的 **re-sync gate**：何時重讀 `SPECS.md`、檢查哪個 upstream source、若版本漂移如何回退到需求 / 設計修訂。這個 gate 應在 baseline-touch 或 review / merge 前以 JIT 方式執行；只有當 first slice 一開始就直接依賴該 shared / external baseline 時，才應成為前置阻塞 gate。
19. re-sync gate 不是口頭說明；每次執行後都必須把結果寫回對應 CR 的 `Re-sync Freshness Evidence`。
20. 若 target 是 external contract assumption，design 應引用 CR 中的 `Assumption Snapshot` 與 `Observed Constraint / Behavior`，而不是只引用 live upstream 或只寫版本號。
21. 若 design-time re-sync 改變了 impact triage 結果，必須先修正 / 拆分 CR，再定稿 design。
22. 在請求 design approval 前，更新 `NEXT_STEPS.md`：至少記錄 active spec、關鍵設計決策摘要、impacted specs / contracts、open CR IDs、以及下一個 tasks planning 入口。
    - `NEXT_STEPS.md` 應只保留高階摘要與 artifact 指引；re-sync 的完整細節與 per-task execution 規劃仍應留在 CR / `tasks.md` / reports。
    - 若本輪設計確認某 issue-log item 仍不該進 SDD，應交由 `issue-log-manager` 更新 issue disposition；不要把未正式化的 issue 塞進 RTM 或 SPECS。
23. 自然地詢問：「設計方案與 Contract 契約看起來可行嗎？如果認可的話，我們可以開始拆解具體任務了」
24. 與前端設計相關任務請參考 skills: `brand-guideline-giant`, `ui-skill`, `frontend-design-skill`, `frontend-patterns`, `theme-factory`
25. 與程式語言相關的, 請搜尋相關的 skills (e.g. `golang-patterns`, `golang-testing`)
26. 需要登入請優先參考整合GAC: skill `gac-integration-skill`
27. 設計時請將安全性考量在內, 參考 skill `security-review`

## Local Infra Governance（若功能需要 local dev / UAT / E2E 環境）

- design 中只能描述 **需要哪些服務、預期 stage、reconcile / reuse / release 原則、以及 TTL / ownership 假設**，不可直接手配 host ports 或臨時 compose stack names。
- 若需要真實啟動 local backend / frontend / worker / database，設計必須引用 skill `local-infra-registry-governance`，將 local infra registry 視為 allocation authority。
- design 應明確區分：
  - feature / contract governance → `SPECS.md`, `requirements.md`, `design.md`
  - live runtime allocation state → local infra registry
- 若設計依賴 `devops-container-orchestration`，應將其定位為 allocation 之後的實作模式，而不是 host resource 決策來源。

## 重要約束

- 必須等待用戶明確認可才能進入下一階段。
- 技術方案應側重於架構設計、Contract 契約與資料流動，而非過早進入具體的業務邏輯實作細節。
- 每次編輯後必須明確請求批准。

## 完成標誌

用戶明確認可設計方案與定義的 Contract。
