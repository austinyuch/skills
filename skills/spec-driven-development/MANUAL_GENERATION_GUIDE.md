# SDD Manual Generation Guide

本指南用於更新 `spec-driven-development` 的操作等級手冊：

- `manual.html`

## 目標

`manual.html` 是使用者手冊，不是價值說帖。它必須讓工程團隊、產品負責人(Product Owner)、Scrum Master、開發者(Developers) 與 DevSecOps 知道如何實際啟動、推進、暫停、恢復、複核與關閉 SDD workflow。

## 必須回答的操作問題

1. 什麼情境要用 SDD？
2. 什麼情境應先交給 `spec-master` routing？
3. 什麼情境不應用 SDD，而應交給 `test-registry-manager`、`spec-registry-manager`、`local-infra-registry-governance`？
4. 新 spec 如何開始？
5. 既有 spec 如何恢復？
6. 每個 phase 要讀哪些檔案、產出哪些 artifact、何時需要人類確認？
7. Phase 4 如何執行 TDD / EDD、測試證據、reports、`TESTS.md` 更新？
8. Phase 5 如何判斷 `PASS` / `CONDITIONAL` / `FAIL`，以及 mock-heavy / hybrid / full-integration？
9. Phase 6 如何把 review findings 轉成 refactor、補測、issue log、CR 或 shared guidance？
10. closeout 前有哪些 artifact authority 必須保持一致？
11. `TESTS.md`、`SPECS.md`、`NEXT_STEPS.md`、`RTM.md` 各自的 why / what / when / how 是什麼？
12. 跨 artifact 更新時，哪個 artifact 先更新、哪個 artifact 只能 derived、哪些同步方向被禁止？
13. 如何使用 `RTM.md` 做需求追溯性(requirement traceability)：從 requirement / acceptance criteria 追到 design、task、test evidence、review verdict 與 residual risk？
14. `ISSUE_LOG.md` 中的 unresolved issue 何時留存、何時 fold 回 active spec / CR、何時 promoted 成正式 spec、何時才可反映到 RTM？
15. `NEXT_STEPS.md` 的生命週期是什麼？何時讀、何時寫、何時覆寫 stale state、何時變成 closure / handoff memo？
16. Responsible AI closeout 要檢查什麼？包含人類監督、traceability、secrets / PII / runtime details、unresolved issue rows、unsupported readiness claims 是否有外洩到 derived summaries。
17. **Ponytail YAGNI Ladder 的操作要求**：每個 phase 何時執行 ladder、如何展示思考過程、如何與 `code-review` skill 家族協作、衝突時的判準為何（可讀性與可測試性 > 單純行數最少）。

## 操作手冊結構

`manual.html` 至少包含：

- Quick Start
- When to Use / When Not to Use
- Six Phase Walkthrough
- Artifact Authority Map
- Spec Governance Artifacts Flow
- Requirement Traceability / RTM Workflow
- ISSUE_LOG to SDD Lifecycle
- NEXT_STEPS Lifecycle
- Phase Gate Checklist
- Test / Review / Demo Readiness Flow
- Resume / NEXT_STEPS Flow
- Ponytail YAGNI Ladder Operational Guide
- Common Failure Modes
- Closeout Checklist
- Responsible AI Closeout Checks
- FAQ

## 雙語要求

- 必須提供 `EN / 繁中` 切換。
- 中文使用繁體中文。
- 專有名詞首次出現使用 `中文名詞(Original Term)`。
- 英文版要能獨立閱讀，不只是中文逐字翻譯。

## 不可做的事

- 不可把操作手冊寫成商業價值簡報。
- 不可承諾 SDD 會自動完成所有實作、部署、安全核准或 runtime readiness。
- 不可把 `SPECS.md` / `RTM.md` 寫成 upstream authority。
- 不可把 `TESTS.md` 寫成 readiness verdict authority。
- 不可把 `NEXT_STEPS.md` 寫成歷史日誌、task ledger 或 second registry。
- 不可把 RTM 寫成只有高階摘要；它必須能支撐需求管理的 traceability review。
- 不可讓 unresolved `ISSUE_LOG.md` row 直接進入 RTM 或 SPECS；必須先經 owner resolution 與 SDD 正式化。
- 不可讓 `NEXT_STEPS.md` 長期累積歷史狀態；stale state 必須被覆寫。
- 不可省略 `SPECS.md` / `NEXT_STEPS.md` / `TESTS.md` / `RTM.md` 的 why / what / when / how。
- 不可省略 mock-heavy / false-green / artifact honesty 的操作檢查。
- 不可省略 Responsible AI 的操作檢查；必須把原則轉成 closeout 前可檢查的行為，而不是只列高階詞彙。

## 更新檢查清單

- [ ] 手冊能讓新使用者知道第一步要讀什麼、問什麼、寫什麼。
- [ ] 每個 phase 都有清楚入口、輸入、輸出、approval gate。
- [ ] 有 `NEXT_STEPS.md` resume 流程。
- [ ] 有 `SPECS.md` / `NEXT_STEPS.md` / `TESTS.md` / `RTM.md` 的操作流程。
- [ ] 有 RTM / requirement traceability 的需求管理操作說明。
- [ ] 有 ISSUE_LOG → spec / SDD / RTM lifecycle。
- [ ] 有 NEXT_STEPS.md lifecycle 與 stale-state 覆寫規則。
- [ ] 有 test governance 與 review verdict 邊界。
- [ ] 有 live demo readiness 操作規則。
- [ ] 有 closeout checklist。
- [ ] 有 Responsible AI closeout checks，且連到 phase gates、traceability、privacy / data governance、risk hygiene。
- [ ] 有 Ponytail YAGNI Ladder 操作指南：每個 phase 的 ladder rung、展示格式、與 code-review 的協作、衝突判準。
- [ ] 有 bilingual toggle。
