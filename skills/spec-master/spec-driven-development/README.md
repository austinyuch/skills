# Spec-Driven Development (SDD) Skill

`spec-driven-development` 是 Spec Master 家族中負責交付主幹的核心子 skill。`spec-master` 負責判斷入口與路由；`spec-driven-development` 負責把一個模糊需求推進成可追溯、可驗證、可複核、可優化的軟體交付流程。

## 一句話價值主張

規格驅動開發(Spec-Driven Development, SDD) 不是把敏捷變慢的文件流程，而是讓人類團隊與程式代理人(coding agent) 在同一套可檢討的工作流中，把需求、設計、任務、測試、複核、重構與交付證據連成一條可治理的價值鏈。

## 為 SDD 正名

在程式代理人時代，各家工具的推理方式、上下文策略、檔案修改習慣、測試判斷與安全邊界都不同，而且多半是黑盒子。團隊若只依賴單次 prompt、單次 code diff 或單一 vendor 的內部行為，很容易得到看似快速、實際不可追溯的交付。

SDD 的定位是團隊自有的工程工作流：

- 將商業需求轉為明確需求與驗收標準，避免「做了很多，但不是要的價值」。
- 將架構、契約、資料、測試與風險提前對齊，避免 implementation 後期才發現方向錯。
- 將任務、證據、複核與優化留下可檢討紀錄，讓團隊可以改進工作方式，而不是只能追究個別 agent 的輸出。
- 將展示就緒(live demo readiness)、測試治理(test governance)、重構(refactoring) 與程式碼複核(code review) 納入同一條 delivery chain，避免 false-green 與 overclaim。

## 三個角色視角

| 角色 | 任務 | 痛點 | 獲益 |
|---|---|---|---|
| 執行長(CEO) | 確認投入的產品開發能回到商業成果、客戶承諾與上市節奏 | Agentic AI 讓產出速度變快，但若沒有治理，錯誤功能、展示翻車與返工成本也會同步放大 | 以需求、驗收、證據與 review 連回價值，降低「看起來完成、實際不能賣」的風險 |
| 資訊長(CIO) | 建立跨專案、跨團隊、跨工具的交付治理與技術債管理 | 不同 agent / vendor 交付方式不同，缺少組織可持續改善的標準流程 | 用 SDD 建立可重複、可稽核、可訓練團隊的 delivery operating model |
| 開發安全營運(DevSecOps) | 確保變更有測試、可回溯、可部署、可回復且不誤導 readiness | CI/CD 變快後，mock-heavy、fixture-heavy、security blind spot 可能更快進入主線 | 把測試證據、展示就緒、安全 gate、review verdict 與 artifact authority 分層，減少 false-green |

## Agentic AI 帶來的行為改變

Agentic AI 讓開發行為從「工程師逐行撰寫」變成「人類設定目標，代理人規劃、搜尋、修改、驗證」。這帶來三個變化：

- 速度變快：更多變更會在更短時間內進入 review 與 CI/CD。
- 黑盒增加：代理人如何選擇上下文、如何判斷完成、如何處理不確定性，不一定能被團隊完全觀察。
- 證據更重要：若沒有明確的需求、測試、review 與 artifact authority，團隊很難判斷結果是真完成，還是只是輸出看起來合理。

因此 SDD 強化的不是傳統敏捷的儀式，而是敏捷本來要求的工程紀律：working software、customer collaboration、responding to change，以及在變更中持續保有可交付品質。

## SDD + TDD + DDD + Test Management + Refactor

| 能力 | 商業主張 | SDD 中的實作 |
|---|---|---|
| 規格驅動開發(SDD) | 讓需求與交付證據可追溯，減少返工與需求漂移 | `requirements.md`、`design.md`、`tasks.md`、`review.md` 與 `SPECS.md` 串成一條可檢討鏈 |
| 測試驅動開發(TDD) | 在變更成本最低時驗證行為，降低 regression 風險 | Phase 4 依任務進行紅燈、綠燈、重構，並留下測試證據 |
| 領域驅動設計(DDD) | 讓系統邊界與業務語言一致，減少跨團隊誤解 | Phase 2 用 bounded context、contract、資料模型與上下游影響分析穩定設計邊界 |
| 測試管理(test management) | 讓測試不只是 CI 綠燈，而是可追溯的風險證據 | `TESTS.md` 保存 test IDs、canonical commands、evidence refs；`review.md` 保留 verdict authority |
| 重構(refactoring) | 在不改變外部行為下持續降低技術債 | Phase 4 left-shift 與 Phase 6 optimization 用 review findings、test safety net 與 bounded refactor 收斂品質 |
| 最小實作紀律(Ponytail YAGNI Ladder) | 在新增程式碼前依序檢查「是否需要存在→標準函式庫→原生平台→現有依賴→最小實作」，防止過度設計 | Phase 1 Rung 1 過濾 speculative 需求；Phase 2 Rung 2-4 指導技術選型；Phase 4 Rung 5-6 指導實作體積；Phase 5 檢查 over-engineering risk |

## Responsible AI 需求與解法

Responsible AI 對 SDD 的意義是：當程式代理人(coding agent) 參與需求、設計、實作、測試與複核時，團隊不能只問「有沒有產出」，還要問「這個產出是否可追溯、可解釋、可監督、可驗證、可改正」。SDD 以六階段生命週期和 governance artifacts，把 NIST AI RMF、OECD AI Principles 與 ISO/IEC 42001 中常見的 responsible / trustworthy AI 要求轉成可執行流程。

| Responsible AI 需求 | SDD 解法 | 對應 artifact / phase |
|---|---|---|
| Human agency / oversight 人類監督 | 每個 phase gate 都需要明確確認；agent 不應從模糊需求直接跳到程式碼或 readiness 宣稱。 | Phase 1-3 approval gates、`NEXT_STEPS.md` handoff |
| Transparency / explainability 透明與可解釋 | requirement、acceptance criteria、design decision、task、test evidence 與 review verdict 互相可追溯。 | `requirements.md`、`design.md`、`tasks.md`、`RTM.md` |
| Accountability 問責 | `review.md` 保留 final verdict；`TESTS.md` 只保留 test evidence；`SPECS.md` / `RTM.md` 只做 derived rollup。 | Authority boundary、`SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md` |
| Robustness / safety 穩健與安全 | 早期辨識 mock-heavy、false-green、auth / data / demo readiness 風險，並在 tasks 中安排真實整合與降級規則。 | Phase 2 FMEA、Phase 3 tasks、Phase 5 review |
| Privacy / data governance 隱私與資料治理 | 不把 secrets、PII、runtime allocation 或外部執行細節散落到 registry / manual / review summary；敏感資訊留在專案權威面。 | `design.md` boundary、`NEXT_STEPS.md` hygiene、runtime governance |
| Fairness / bias management 公平與偏誤管理 | 需求與 issue 必須先經 owner resolution；不讓單次模型輸出、偏好或 incomplete evidence 直接變成 requirement 或 RTM row。 | `ISSUE_LOG.md` → SDD lifecycle、Phase 1 routing |
| Auditability / continual improvement 可稽核與持續改善 | closeout 順序固定，review findings 可進 Phase 6、CR、issue log 或 shared guidance，形成可檢討改善鏈。 | Phase 5 review、Phase 6 optimization、`SPECS.md` / `RTM.md` |

這套解法的商業價值是降低 agentic delivery 的黑盒風險：不是禁止 agent 自動化，而是讓每個自動化結果都能被人類團隊追溯、質疑、修正與持續改善。

參考來源：

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OECD AI Principles](https://oecd.ai/en/ai-principles)
- [ISO/IEC 42001:2023 AI management systems](https://www.iso.org/standard/42001)

## Scrum Team 對應

| Scrum 角色 | SDD 提供什麼 |
|---|---|
| 產品負責人(Product Owner) | 將目標、使用者故事、驗收標準與商業價值連接起來，避免只交付技術活動 |
| Scrum Master | 提供清楚的流程邊界、阻塞揭露、下一步備忘與 retrospective promotion path |
| Developers | 提供需求、設計、任務、測試與 review 的共同工作面，讓並行工作仍能回到同一條證據鏈 |

## 敏捷宣言對應

| 敏捷價值 | SDD 的落地方式 |
|---|---|
| Individuals and interactions over processes and tools | SDD 的 phase approval 與 review 是協作節點，不是把人排除在流程外 |
| Working software over comprehensive documentation | 文件只保留會影響交付正確性、驗證與恢復的內容；readiness 以 evidence 與 working path 為準 |
| Customer collaboration over contract negotiation | requirements 與 acceptance criteria 讓客戶語言成為驗證標準，而不是只靠實作細節爭辯 |
| Responding to change over following a plan | Change Request、impact triage、NEXT_STEPS 與 optimization 讓變更有治理路徑，而不是被舊計畫綁死 |

## Ponytail YAGNI Ladder：最小實作紀律

SDD 整合 [Ponytail](https://github.com/DietrichGebert/ponytail) 的 6-Rung Ladder，作為貫穿需求、設計、實作與複核的最小實作紀律。

> **Lazy, not negligent**：精簡的是不必要的功能與過度設計，不是安全、驗證或錯誤處理。

### 六級階梯

```
1. Does this need to exist?   → no: skip it (YAGNI)
2. Stdlib does it?            → use it
3. Native platform feature?   → use it
4. Installed dependency?      → use it
5. One line?                  → one line
6. Only then: the minimum that works
```

### 階段對應

| Phase | Ladder Rungs | 決策焦點 |
|---|---|---|
| Phase 1 需求明確 | Rung 1 | 這個需求是否真的有已確認的支撐？ speculative 功能應標記為 `deferred` / `out-of-scope`。 |
| Phase 2 架構設計 | Rung 2-4 | 標準函式庫 / 原生平台 / 現有依賴是否已涵蓋？引入新 dependency 必須說明為何 rung 2-4 無法滿足。 |
| Phase 4 程式碼實作 | Rung 5-6 | 能否用更少程式碼完成？實作是否為「最小可用」而非「預留擴展」？ |
| Phase 5 程式碼複核 | — | 檢查新 dependency 是否有 ladder 紀錄；未經 ladder 思考的新抽象標記為 `over-engineering risk`。 |

### 與 Code-Review Skill 的協作

- **ladder** 是設計與實作階段的「前置自我檢視」，防止「不必要的存在」。
- **`code-review` 家族**（`code-refactoring-advisor`、`test-quality-reviewer`、`security-risk-reviewer`）是複核階段的「left-shift 偵測」，防止「不良結構」。
- 兩者衝突時（ladder 說「一行就夠」，refactoring advisor 說「抽出 function」），以「可讀性與可測試性」為最終判準。

詳細規範與展示格式範例請參閱 [`references/ponytail-yagni-ladder.md`](./references/ponytail-yagni-ladder.md)。

---

## 六階段交付模型

| Phase | 主要產出 | 交付價值 |
|---|---|---|
| 1. 需求明確 | `requirements.md` | 將模糊需求轉成可驗收的商業與使用者需求 |
| 2. 架構設計 | `design.md`、`contract/*` | 提前處理架構、契約、資料、風險與整合邊界 |
| 3. 任務規劃 | `tasks.md` | 將設計拆成可執行、可追溯、可測試的小步工作 |
| 4. 程式碼實作 | 程式碼、reports、測試證據 | 以 TDD / EDD 思維逐步交付並留下證據 |
| 5. 程式碼複核 | `review.md` | 用需求、設計、測試、安全與 demo readiness 做 final readiness verdict |
| 6. 程式碼優化 | 更新後的 review / NEXT_STEPS | 將 review findings 收斂成重構、補測、流程改善或下一輪 change request |

## Spec Governance Artifacts 的商業意義

SDD 的治理 artifact 不是「文件庫」，而是降低交付風險的營運控制面。它們讓團隊能回答四個管理問題：

- 現在承諾了什麼？哪些需求、契約與驗收條件是有效的？
- 每個需求是否真的被設計、任務、測試與 review 覆蓋？若沒有，缺口在哪裡？
- 現在做到了哪裡？哪些工作可恢復、哪些被阻塞、哪些需要外部執行？
- 現在有什麼證據？測試、review、demo readiness 是否真的支持目前宣稱？
- 現在可以對外說什麼？哪些摘要只是 derived snapshot，哪些 artifact 才能裁決 readiness？

執行面生命週期規則由 [reference/SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md](./reference/SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md) 維護。README、HTML 說帖與手冊只能摘要這套規則；真正要跑 SDD phase、更新治理 artifact、或做 closeout 時，應回到該 reference 與各 phase 文件。

| Artifact | Why：商業意義 | What：承載內容 | When：何時讀寫 | How：流程規則 |
|---|---|---|---|---|
| `ISSUE_LOG.md` | unresolved improvement 的暫存與收斂面，避免 owner 不明的 gap 被誤開成 spec，或在對話中遺失 | issue、source trigger、cluster key、root-cause hypothesis、evidence refs、candidate owner、promotion threshold、disposition | review / retro / known issue / repeated gap 暫時找不到安全 owner 時寫入；定期 triage / cluster / owner resolution | 只做 holding surface；不是第二個 `SPECS.md`、不是第二個 `NEXT_STEPS.md`、不是自動 new-spec queue；可 `Folded` 回 active spec / CR，或在證據足夠時 `Promoted` 成正式 spec |
| `SPECS.md` | 建立跨 spec 的穩定投資地圖，避免重複開發、相依遺漏與 completed baseline 被偷偷改寫 | spec 狀態、Depends On、Impacts、Open Change Requests、external contract metadata、穩定 readiness 摘要 | Phase 1 / Phase 2 開始前必讀；impact triage、CR overlay、closeout 後更新摘要 | 只保存 stable registry summary；不可當 sprint board、task counter、runtime state 或 final verdict authority |
| `NEXT_STEPS.md` | 滾動式操作備忘錄，降低 session 中斷、agent 換手與跨天恢復成本，避免團隊靠記憶找下一步 | current phase、active spec、work classification、next action、blockers、resume hint、handoff state | 新 session / resumed session 必讀；phase 結束、暫停、等待人類確認、blocker、handoff 前更新；完成或失效時覆寫成 closure / superseded state | 只保留「下一步怎麼恢復」；不是歷史日誌、不是 task ledger、不是第二個 registry；只指向 canonical artifacts，不複製完整 requirements / tasks / review |
| `TESTS.md` | 把「CI 綠燈」升級為可審計的測試資產，降低 false-green、stale evidence 與 coverage overclaim | Test ID、type、scenario、requirement / AC trace、owner、canonical command、status、last run、result、evidence ref | 新增、修改、淘汰或重新驗證測試時更新；review / closeout 前必須確認 freshness | 先更新 folder-level row authority，再由 `test-registry-manager` 刷新 workspace rollup；不可由 `SPECS.md` / `RTM.md` 反向回填 |
| `RTM.md` | 需求管理的追溯控制面，讓產品、工程、QA 與管理者看見每個 requirement 是否被設計、任務、測試與 review 覆蓋，降低 scope gap、coverage gap 與 release surprise | requirement ID、acceptance criteria、design section、task IDs、test IDs、review verdict、gap / residual risk 的 workspace-level traceability rollup | 多 spec 匯總、release review、governance reporting、需求變更 impact review、closeout snapshot 時更新 | 只根據 upstream artifacts 產生 synthesized rollup；不可成為 authoring source、task progress tracker 或 readiness verdict authority |

### 執行面維護行為

| SDD 階段 | Governance artifact 維護行為 |
|---|---|
| Phase 1 需求明確 | 先讀 `SPECS.md`，再讀 `NEXT_STEPS.md`。若來源是 unresolved improvement，先做 owner resolution，再決定 fold、promote、close、drop 或繼續 holding。不可從 `RTM.md` 反向撰寫需求。 |
| Phase 2 架構設計 | 若工作會影響 `TESTS.md`、`RTM.md`、`SPECS.md`、`ISSUE_LOG.md` 或 stakeholder summary，必須在 `design.md` 寫清 artifact authority model 與 RTM traceability anchors。 |
| Phase 3 任務規劃 | `tasks.md` 只鏡射 Phase 1 / 2 的治理邊界，並顯式安排 `TESTS.md`、RTM、SPECS、CR closure、ISSUE_LOG fold / promote / close 的 closeout 任務。 |
| Phase 4 程式碼實作 | 先更新 upstream evidence：程式碼、測試、reports、task status。folder-level `TESTS.md` 必須早於 workspace rollup；`NEXT_STEPS.md` 只保留短期恢復狀態。 |
| Phase 5 程式碼複核 | `review.md` 裁決 final verdict 與 residual risk，並檢查 issue row 是否 folded、promoted、closed、dropped 或仍明確 holding。RTM / SPECS 只能從 upstream truth 產生。 |
| Phase 6 程式碼優化 | 將 repeated failure 判斷為 spec-local lesson、`ISSUE_LOG.md` holding、CR fold-back、或 promoted skill / process change candidate；不可把 optimization finding 直接塞入 RTM 或 SPECS。 |

維護原則是單向流動：`ISSUE_LOG.md` holding → owner resolution → SDD upstream artifacts → `TESTS.md` → workspace test rollup → `RTM.md` → `SPECS.md`。`NEXT_STEPS.md` 平行存在，只記錄目前恢復、阻塞、交棒或 closure 狀態。

### Requirement Traceability 與 RTM

需求追溯性(requirement traceability) 是 SDD 連接商業需求與工程交付的核心控制。沒有 RTM，團隊通常只能回答「這個功能有人做了嗎？」；有 RTM，團隊才能回答：

- 哪些 requirement 已經有設計支撐？
- 哪些 requirement 已經拆成可執行任務？
- 哪些 acceptance criteria 已經有對應 test evidence？
- 哪些 requirement 的 review verdict 仍是 `CONDITIONAL`、`FAIL` 或 `NOT_ASSESSED`？
- 哪些變更會影響既有需求、契約或 completed baseline？

RTM 的商業價值在於讓需求管理從口頭追蹤變成可稽核矩陣。它支撐產品範圍控管、release go/no-go、變更影響分析、QA coverage review、合規稽核與跨團隊交接。RTM 仍是 derived artifact：它不創造需求、不裁決 readiness，而是把 `requirements.md`、`design.md`、`tasks.md`、`TESTS.md`、reports 與 `review.md` 的最新事實整理成需求管理視圖。

### ISSUE_LOG → SPEC / SDD / RTM 的生命週期

`ISSUE_LOG.md` 的用途是讓尚未能安全歸屬的改善項不被遺失，但它不是最終交付面。典型生命週期如下：

1. **Captured / Triaged**：review rejection、retro finding、known issue、tech debt 或 repeated gap 先進 `ISSUE_LOG.md`，補 source、evidence、cluster key、root-cause hypothesis。
2. **Owner Resolution**：先判斷是否能 fold 回 active spec、completed baseline 的 Change Request、或 spec-local lesson。能歸屬就不要開新 spec。
3. **Folded / Promoted**：若屬於既有 active spec / CR，issue row 標成 `Folded` 並指向 owner；若 repeated root cause、clear cluster、enough evidence 且沒有 owner，才升級成新 spec 或 shared skill change candidate。
4. **SDD Authoring**：一旦 promoted 成正式 spec，才由 SDD 建立或更新 `requirements.md`、`design.md`、`tasks.md`、reports、`review.md`。此時 issue log 只保留 pointer，不再承載任務細節。
5. **RTM Reflection**：只有當 promoted / folded item 變成正式 requirement、acceptance criteria、task、test evidence 或 review verdict 後，才反映到 `RTM.md`。RTM 不直接把 issue-log row 當需求。
6. **Registry Summary**：`SPECS.md` 只摘要正式 spec / CR 狀態；不把 unresolved issue log 當成 stable spec entry。

這條生命週期的商業意義是：先用 issue log 保留不確定性，再用 owner resolution 避免 premature spec，最後只有經 SDD 正式化的需求才進入 RTM 與 registry。這能降低規格膨脹、責任不清、需求矩陣污染與管理報告過度宣稱。

### 推薦更新順序

當一個 spec 準備 closeout 或跨 artifact 刷新時，順序應是：

1. 若有 unresolved improvement，先在 `ISSUE_LOG.md` 完成 owner resolution；能 fold 回既有 spec / CR 就不要開新 spec。
2. 更新 SDD upstream source：`requirements.md`、`design.md`、`tasks.md`、reports、test output、`review.md`。
3. 更新最近的 folder-level `TESTS.md`，補齊 test IDs、trace refs、canonical commands 與 evidence refs。
4. 若 workspace 採用 `.agents/specs/TESTS.md`，交由 `test-registry-manager` 依 folder-level catalogs 產生 rollup。
5. 若 workspace 採用 `RTM.md`，只根據正式 requirement / acceptance criteria / task / test / review upstream facts 產生 synthesized rollup。
6. 最後由 `spec-registry-manager` 或等價流程刷新 `SPECS.md` 的 stable summary。
7. `NEXT_STEPS.md` 只記錄目前可恢復的下一步、blocker、handoff 或 closure，不保留已過期工作流歷史。

禁止 derived-to-derived sync：不要用 `SPECS.md` 去補 `RTM.md`，不要用 `RTM.md` 去補 `TESTS.md`，也不要用 registry 摘要反向改寫 spec-local source。

## 與 Spec Master 家族的分工

- `spec-master`：入口與路由。判斷是 new spec、continue active spec、CR overlay、issue log、registry sync、test registry 還是 runtime governance。
- `spec-driven-development`：交付主幹。負責 branch-spec lifecycle 與六階段工作流。
- `spec-registry-manager`：維護 `SPECS.md` 的穩定 registry summary。
- `test-registry-manager`：維護 `TESTS.md` 的測試 catalog 與 evidence pointer。
- `code-review` 家族：作為 SDD Phase 4 / Phase 5 的 capability-gated review、test quality、security、refactor 輔助輸入。
- `local-infra-registry-governance`：處理 local dev / UAT / E2E runtime allocation；SDD 不自行猜測 port 或 stack。
- **Ponytail YAGNI Ladder**：貫穿 Phase 1-5 的最小實作紀律，防止 over-engineering 與過度設計。

## 權威邊界

SDD 產生治理文件，但不會單獨宣稱 runtime readiness。

- `requirements.md` 是需求真相來源。
- `design.md` 是設計與契約邊界真相來源。
- `tasks.md` 是任務與 traceability 真相來源。
- `TESTS.md` 是測試 catalog / evidence pointer authority。
- `review.md` 是 acceptance / readiness verdict authority。
- `SPECS.md` 與 `RTM.md` 是 derived summary，不可反向覆寫 upstream artifact。

## 可交付文件

- [index.html](./index.html)：雙語商業價值說明與高階說帖。
- [GENERATION_GUIDE.md](./GENERATION_GUIDE.md)：商業價值說明更新規則。
- [manual.html](./manual.html)：雙語操作手冊。
- [MANUAL_GENERATION_GUIDE.md](./MANUAL_GENERATION_GUIDE.md)：操作手冊更新規則。

## 參考名詞

- [Spec-Driven Development](https://en.wikipedia.org/wiki/Software_requirements_specification)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
- [Domain-Driven Design](https://en.wikipedia.org/wiki/Domain-driven_design)
- [Code Refactoring](https://en.wikipedia.org/wiki/Code_refactoring)
- [Scrum](https://scrumguides.org/)
- [Manifesto for Agile Software Development](https://agilemanifesto.org/)
- [Continuous Integration](https://en.wikipedia.org/wiki/Continuous_integration)
- [Continuous Delivery](https://en.wikipedia.org/wiki/Continuous_delivery)
- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [EARS Requirements Syntax](https://alistairmavin.com/ears/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OECD AI Principles](https://oecd.ai/en/ai-principles)
- [ISO/IEC 42001:2023 AI management systems](https://www.iso.org/standard/42001)
