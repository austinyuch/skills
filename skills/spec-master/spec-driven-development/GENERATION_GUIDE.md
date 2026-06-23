# SDD Business Explanation Generation Guide

本指南用於更新 `spec-driven-development` 的商業價值說明與 HTML 說帖：

- `README.md`
- `index.html`

## 目標

這組文件必須替規格驅動開發(Spec-Driven Development, SDD) 正名：SDD 是 Spec Master 家族中的主要交付 skill，不是附屬文件步驟。文件要讓 CEO、CIO、DevSecOps、Scrum Team 與工程團隊理解：為什麼在程式代理人(coding agent) 時代，團隊更需要自己的可檢討工作流。

## 必須保留的核心訊息

1. `spec-master` 是入口與路由；`spec-driven-development` 是 delivery backbone。
2. SDD 的價值不是多寫文件，而是讓需求、設計、任務、測試、review、重構與交付證據可追溯。
3. Agentic AI 讓交付速度提升，也讓黑盒行為、false-green、overclaim、security blind spot、test evidence drift 更容易被放大。
4. SDD 強化傳統敏捷軟體工程，而不是取代敏捷：working software、customer collaboration、responding to change 都必須靠證據鏈支撐。
5. 商業價值必須涵蓋三個需求面向：任務、痛點、獲益。
6. 角色視角必須至少包含 CEO、CIO、DevSecOps。
7. 必須明確陳述 SDD + TDD + DDD + test management + refactor 的商業主張與實作方式。
8. 必須映射 Scrum Team 與敏捷宣言(Agile Manifesto)。
9. 必須保留 authority boundary：`review.md` 是 readiness verdict authority；`TESTS.md` 是 test evidence pointer authority；`SPECS.md` / `RTM.md` 是 derived summary。
10. 不可宣稱 SDD 自己等於 runtime readiness、deployment success 或 security approval。
11. 必須說明 spec governance artifacts 的商業意義與流程：`TESTS.md`、`SPECS.md`、`NEXT_STEPS.md`、`RTM.md` 的 why / what / when / how。
12. 必須說明 artifact 更新順序與禁止 derived-to-derived sync，避免 summary drift、false-green 與 authority confusion。
13. 必須把需求追溯性(requirement traceability) 與 `RTM.md` 寫成需求管理的核心控制面，而不是只寫成高階摘要；需說明它如何支撐 scope control、coverage gap、release decision、impact analysis、QA coverage review 與 audit。
14. 必須說明 `ISSUE_LOG.md` → spec / SDD / RTM 的生命週期：captured / triaged / clustered / owner-resolved / folded / promoted，以及何時不能進 RTM 或 SPECS。
15. 必須清楚定位 `NEXT_STEPS.md`：它是 rolling operational memo / resume surface，不是歷史日誌、task ledger、second registry、或 issue log。
16. 必須加入 Responsible AI 需求到解法的對應，至少涵蓋 human oversight、transparency / explainability、accountability、robustness / safety、privacy / data governance、fairness / bias management、auditability / continual improvement。
17. Responsible AI 必須連到 SDD 的具體 artifact 與 phase：phase gate、`requirements.md`、`design.md`、`tasks.md`、`TESTS.md`、`review.md`、`RTM.md`、`SPECS.md`、`ISSUE_LOG.md`、`NEXT_STEPS.md`。不可只列原則。
18. 可以參考 NIST AI RMF、OECD AI Principles、ISO/IEC 42001 的語言，但只能說「對齊 / 支撐 / operationalize」，不得宣稱已符合認證或法律合規，除非另有正式稽核證據。
19. **必須說明 Ponytail YAGNI Ladder**：六級階梯（Does this need to exist → Stdlib → Native → Installed → One line → Minimum that works）如何貫穿 Phase 1-5，防止 over-engineering。必須說明 "Lazy, not negligent" 安全守則（security、validation、accessibility 永不妥協）。必須說明與 `code-review` skill 家族的協作關係（ladder 防止「不必要的存在」，code-review 防止「不良結構」）。

## 子 skill 與相依能力說明要求

文件中提到子 skill 或相依 skill 時，必須說明「為什麼要這樣分工」：

- `spec-master`：避免所有 spec / governance 請求直接混進同一個 workflow，先做 identity resolution 與 routing。
- `spec-driven-development`：負責正式 branch-spec lifecycle，保留可檢討的 delivery evidence。
- `test-registry-manager`：避免 test catalog 被 `SPECS.md` / `RTM.md` 這類 derived summary 反向污染。
- `spec-registry-manager`：讓 cross-spec 狀態穩定摘要化，不把 registry 當 sprint board。
- `code-review` 家族：把 review、test quality、security、refactor risk 左移，但不取代 final verdict。
- `local-infra-registry-governance`：避免 agent 自行猜測 ports、stack names、runtime ownership。
- **Ponytail YAGNI Ladder**：防止 over-engineering 與過度設計，貫穿 Phase 1-5 的最小實作紀律。

## 中文撰寫規則

- 使用繁體中文。
- 避免中英夾雜；第一次出現專有名詞時使用 `中文名詞(Original Term, Abbreviation)`，後續可用中文或縮寫。
- 例：規格驅動開發(Spec-Driven Development, SDD)、測試驅動開發(Test-Driven Development, TDD)、領域驅動設計(Domain-Driven Design, DDD)、重構(Refactoring)、程式代理人(coding agent)。
- 不要把口號式句子寫成價值主張；每個價值主張都要連到痛點、任務或可驗證解法。

## HTML 要求

`index.html` 必須：

- 可單檔開啟，不依賴外部 build tool。
- 提供 `EN / 繁中` 雙語切換。
- 以商業價值與解決方案為主，不寫成操作手冊。
- 包含名詞參考連結，例如 Scrum Guide、Agile Manifesto、TDD、DDD、refactoring、CI/CD、Test Pyramid、EARS。
- 明確標示 claim boundary，避免讓讀者誤解成「有 SDD 就等於已完成、已部署、已安全」。
- 包含治理 artifact 專章，說明 `SPECS.md`、`NEXT_STEPS.md`、`TESTS.md`、`RTM.md` 的商業用途、流程時機與 authority boundary。
- 包含 Responsible AI 專章，使用「需求 → SDD 解法 → 對應 artifact / phase」格式，明確說明人類監督、透明可解釋、問責、安全穩健、隱私資料治理、公平偏誤管理、可稽核持續改善。
- 對 `RTM.md` 必須額外說明 requirement traceability 的需求管理價值：requirement → acceptance criteria → design → tasks → tests → review verdict / residual risk。
- 對 `ISSUE_LOG.md` 必須說明它與 spec / SDD / RTM / SPECS 的 lifecycle boundary，避免 unresolved issue 直接污染 requirement traceability。
- 對 `NEXT_STEPS.md` 必須說明它的短期恢復定位與失效覆寫規則。

## 更新檢查清單

- [ ] README 與 HTML 都有 SDD 正名定位。
- [ ] 有 CEO / CIO / DevSecOps 三角色視角。
- [ ] 有任務、痛點、獲益三面向。
- [ ] 有 SDD + TDD + DDD + test management + refactor。
- [ ] 有 Scrum Team 與 Agile Manifesto mapping。
- [ ] 有 Agentic AI 黑盒與 team-owned workflow 論述。
- [ ] 有 authority boundary 與 false-green / overclaim 防護。
- [ ] 有 spec governance artifacts 的 why / what / when / how。
- [ ] 有 requirement traceability / RTM 的需求管理價值。
- [ ] 有 ISSUE_LOG → SPEC / SDD / RTM 的生命週期。
- [ ] 有 NEXT_STEPS.md 的 rolling operational memo 定位。
- [ ] 有 artifact 更新順序與 derived-to-derived sync 禁止規則。
- [ ] 有 references / glossary。
- [ ] 有 Responsible AI 需求到解法 mapping，且每個解法都連到 SDD artifact 或 phase。
- [ ] 有 Ponytail YAGNI Ladder 的商業價值說明：為何最小實作紀律能降低技術債與返工成本。
- [ ] 有 ladder 與 code-review skill 家族的協作關係說明。
- [ ] 沒有宣稱 ISO/IEC 42001 certification、法規合規、或自動安全保證。
