# 第五階段：程式碼複核

## 觸發條件

- `tasks.md` 中本輪實作任務已完成，且必要的 `reports/` 證據已建立（若 repo 仍沿用 `completed_tasks.md`，可視為 legacy 輔助 artifact，而不是唯一 trigger）
- 或您明確要求進行程式碼複核
- 或本次 slice 雖然主要變更的是 repo-owned global skill / shared workflow / governance wording，但已經改動了 review trigger、retrospective trigger、authority boundary、routing 行為、或其他會影響後續 agent 決策的正式 surface

### Agentic Review Trigger Scope

若本次變更符合以下任一情況，即使它是 docs / skill / governance slice，也必須進入 formal review，而不是只靠作者自述完成：

1. 變更了 repo-owned global skill（`skills/`）的正式行為、路由、trigger timing、authority boundary、或 shared governance asset consumption rule。
2. 變更了 agent 何時應該觸發 review / retrospective / QA gate。
3. 變更了 delivery truth、registry summary、evidence authority、或 runtime authority 的界線。
4. 變更了多個 downstream agents 可能共同依賴的 shared workflow wording。

這類 slice 的 review 不一定代表「產品功能已可交付」，而是代表：

- 變更已具備可讀回 evidence
- authority boundaries 未被破壞
- 後續 agent 不會因 wording drift 直接跳過 spec workflow

## 我的工作

### 全面程式碼分析

- 調整到 thinkharder 模式 with oracle agent (if available)
- 必須完全了解專案程式碼，了解專案規範和具體實現，收集足夠完整的上下文，再開始複核工作
- 仔細閱讀 requirements.md、design.md、tasks.md 和所有已實作的程式碼
- 若本次 review 涉及 governance artifact lifecycle、issue-log promotion / fold-back、RTM refresh、SPECS summary、TESTS rollup、或 NEXT_STEPS handoff，必須讀取 `../reference/SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md`。
- 若 `{workspace}/.agents/specs/NEXT_STEPS.md` 存在，先讀取其中的 last verified state、open CRs、blockers、與最新 resume hint，確認 review 是否需要先補跑 re-sync 或收斂前置條件。
- 檢查程式碼實作與需求文件的一致性
- 驗證程式碼是否符合設計文件中的架構決策

### 多維度評估

- **需求符合度評估**：檢查每個需求是否完全實作，是否存在遺漏或偏差
- **設計一致性評估**：驗證實作是否遵循設計文件中的架構、介面、資料模型等規範
- **程式碼規範評估**：檢查程式碼是否符合專案的編碼規範、最佳實踐
- **程式碼品質評估**：評估程式碼的可讀性、可維護性、效能、安全性等
- **FMEA 緩解覆蓋評估**：若 design / tasks 含有 lightweight FMEA，必須檢查 high/major risk 是否已有 mitigation evidence、negative-case validation、或清楚標記的 residual risk / accepted fallback
- **AI / Security / Privacy / Log Compliance Inventory Review**：若 requirements/design 觸發 `iso-ai-security-auditor`，必須檢查其 inventory / gap table 是否已被納入 review inputs，且狀態值只使用 `implemented`、`external-implemented`、`partial`、`planned`、`missing-evidence`、`not-applicable`、`assumed-baseline`。確認 review 清楚區分 repo evidence、organization-document gaps、external-control dependencies、legal/regulatory assumptions、與 certification/legal-advice caveat；不得因文字完整就宣稱 CNS/ISO certification readiness 或 legal compliance PASS。
- **Acceptance Status 覆核**：若 spec 採用 `TESTS.md` / `SPECS.md` / `RTM.md` 治理模型，必須明確區分 authoritative verdict (`review.md`) 與 derived snapshots (`SPECS.md`, `RTM.md`)
- **ISSUE_LOG Lifecycle 覆核**：若本工作源自或產生 unresolved improvement，必須確認 issue row disposition：仍 holding、`Folded`、`Promoted`、`Closed`、或 `Dropped`。未經 SDD 正式化的 issue row 不得出現在 RTM requirement traceability 或 SPECS stable entry 中。
- **NEXT_STEPS Lifecycle 覆核**：確認 `NEXT_STEPS.md` 只保留目前 resume / blocker / handoff / closure state，不是歷史日誌、task ledger、second registry、或 issue log。
- **TESTS Closeout 覆核**：若 spec 影響 tests 或 evidence，必須確認 folder-level `TESTS.md` 已刷新，workspace `.agents/specs/TESTS.md`（若存在）已由 `test-registry-manager` 或等價 flow 刷新，且沒有任何 derived artifact 反向校正 `TESTS.md`
- **Git / Worktree Hygiene**：若本次工作使用了 dedicated branch/worktree lane，必須確認只有一條 authoritative writable lane 承擔正式 writeback、detached audit worktree 沒有累積未收斂 authoring 變更、且暫時 worktree 的 cleanup / prune 計畫已明確
- **Conflict Handling Evidence**：若本次工作曾遇到 concurrent writable lane 風險，必須依 `shared-governance` skill 的 `references/conflict-evidence-review-checklist.md` 檢查 downgrade / reconcile / ownership resolution evidence，而不是靠「最後沒有出錯」當成通過理由
- **Project Review-Tooling Inputs（Capability-Gated）**：若 `code-review` skill 家族可用（workspace-local 或 global skill home 皆算，見 SKILL.md Global Constraint #14 的 availability 判定），下列為本 phase 的 **required inputs（非 verdict）**：
  - `code-review`（`review --vet --race` / `analyze`）對變更程式碼的 static / 背景經典問題（race / deadlock / lock-no-defer / money-float 等）結果，併入「程式碼品質評估」。
  - `test-quality-reviewer` 對測試的 FIRST / test-smell / pyramid findings，併入「TESTS Closeout 覆核」的 quality 面。
  - `sonarqube-bridge` 為 optional enrichment，須做 **兩層判定 + 來源優先序**（見 SKILL.md Global Constraint #14）：bridge skill 可用、**且**有一個已設定的 SonarQube 來源時才 ingest + graph blast-radius / capability / remediation 排序。來源解析固定 **部門 / 共用 server > 本機 local > 無**：兩者皆有時必採部門共用 server；只有 local 時用 local 並在 `review.md` 標 source=`local`（非 canonical 部門 gate）。SonarQube 的 quality-gate verdict 仍是 authoritative，bridge 不改判。若 bridge 可用但 **部門與本機 SonarQube 皆未設定**（常見預設），視為 honest no-op、不阻塞，於 `review.md` 記「SonarQube not configured」（與「bridge unavailable」分開記）。
  - **Cross-Agent 獨立複核（`cross-agent-review` / `xreview`）**：把本輪工作**導引到 `cross-agent-review` skill**，讓它以**不同 model family** 的 agent 對變更做一次獨立複核，回應本 phase 開頭 Agentic Review Trigger Scope「review 不能只靠作者自述」的要求。兩層 gate（見 SKILL.md Global Constraint #14 與 [`../references/CROSS_AGENT_REVIEW.md`](../references/CROSS_AGENT_REVIEW.md)）：skill/binary 可用、**且**有真正跨 family 的 reviewer + 憑證時，執行為 **required input**。**不要 hard-code 作者/reviewer 配對**——作者身分與 reviewer 一律由該 skill 自行偵測（作者可為 claude / codex / opencode / kiro / antigravity 任一；Claude↔Codex 只是 default preference）。只有同 family 可用時**誠實降級**（`same-family-degraded`），不得宣稱已獲跨 model 獨立確認。findings 併入「程式碼品質評估」，outcome/reviewer/provider 記入 `review.md`；**`review.md` 仍是 verdict authority**，永遠 advisory、non-blocking。
  - **前端視覺複核（`frontend-designer`）**：**僅在本次變更觸及前端**（`.css`/`.scss`/`.html`/`.jsx`/`.tsx`/`.vue`/`.svelte`/樣式/版型，或有 web UI 產出）時，把本輪工作**導引到 `frontend-designer` skill** 的 Phase 3 視覺複核——補上 `code-review` 家族**完全不審前端**的缺口。兩層 gate（見 SKILL.md Global Constraint #14 與 [`../references/FRONTEND_DESIGN_REVIEW.md`](../references/FRONTEND_DESIGN_REVIEW.md)）：skill 可用即跑 **static**（CSS/JS/HTML 對 design-system 的遵循、anti-slop、a11y baseline）；有 Playwright backend（`uat-demo-agent`/`webapp-testing`，受 `local-infra-registry-governance` gate）時另跑 **visual**（render → 截圖 → Read PNG 評 layout/階層/對比/品牌/responsive）。findings 併入「設計一致性 / 程式碼品質」，**只給 findings 不下 verdict**（與 `security-risk-reviewer` 同 pattern）。三態誠實記錄：`ran` / `unavailable`（skill 皆無）/ `dependency-not-configured`（無 render backend → 只做 static，明記 visual 未跑）；非前端變更則不觸發。
  - 只有當某適用工具在 workspace-local 與 global home **皆不可用**時，才沿用既有內建評估，並必須在 `review.md` 記錄「該工具不可用」，不得 silent skip。
- **(Ponytail Over-Engineering Check)** 在複核變更程式碼時，必須檢查：
  - 新引入的 dependency / library / 元件，是否在 `design.md` 中有 **Ponytail Rung 2-4** 的紀錄（為何 stdlib / native / installed dependency 無法滿足）？
  - 新增的 class / module / service / wrapper，是否可以用更少程式碼完成（**Rung 5-6**）？
  - 測試程式碼是否過度複雜（例如為了一個原生 `<input>` 寫了過多 test helper）？
  - 若發現未經 ladder 思考就引入的新抽象或新 dependency，應在 `review.md` 標記為 `over-engineering risk`，並要求補上 ladder 紀錄或提供充分理由。
  - 此檢查與 `code-refactoring-advisor` 的 Fowler smell 偵測是**互補**關係：ladder 防止「不必要的存在」，refactoring advisor 防止「不良結構」。兩者皆應納入「程式碼品質評估」。

### Security-Review Gate（trust-boundary 變更時 mandatory）

- 若本次變更涉及下列任一 trust boundary，必須在給出 Phase 5 verdict 前執行 `security-review`：
  - identity boundary：login、session、role、tenant、secret、privilege escalation
  - data boundary：user input、files、queues、cache、database、analytics、logs
  - execution boundary：background jobs、third-party APIs、webhooks、shells、code execution
  - infrastructure boundary：CI/CD、cloud roles、deploy config、runtime identity、artifact provenance
  - agent boundary：prompts、tools、memory、retrieval、MCP servers、autonomous actions
- （Capability-Gated Pre-Flight）若 `security-risk-reviewer` 可用（workspace-local 或 global skill home 皆算），先跑其 deterministic、offline 的 OWASP / 風險掃描，把 findings 當成 `security-review` 的輸入；它 **餵給**而非取代 `security-review` gate。皆不可用時直接執行 `security-review`，不阻塞。
- 執行 `security-review` 時，至少應遵循其 `references/review-workflow.md` 的順序：先界定 trust boundary，再追 entry point → privilege context → sink → side effect，之後再選 deep lanes / language lane / platform overlay。
- `security-review` 的輸出必須至少包含：
  - 本次變更涉及的 trust boundaries
  - 主要 attack paths
  - `Confirmed issue` / `Risk to verify before merge` / `Acceptable with rationale` 三類分類
  - 對應到程式碼或設定層的 remediation / verification notes
- `security-review` 是 **QA/QC gate**，不是可選備註：
  - 若存在 `Confirmed issue` 且未補救，review verdict 不得為 `PASS`
  - 若存在 `Risk to verify before merge` 且無清楚補證計畫，review verdict 至少降為 `CONDITIONAL`
  - `review.md` 仍是最終 authoritative readiness artifact；security-review 是必須納入的輸入，而不是平行 authority

### Live-Demo Readiness Gate（獨立於分數）

- 若本次工作涉及 UI、manual、project review、dashboard、auth、E2E、demo script、screenshot、或任何 stakeholder-facing showcase，必須額外讀取 `./reference/DEMO_READINESS_GUIDE.md` 並執行 live-demo readiness gate。
- 此 gate 不可被綜合分數稀釋。即使綜合得分很高，只要 live-demo readiness 為 `FAIL` 或 `CONDITIONAL`，都不得直接宣告「可以 live demo」。
- 至少要檢查：
  - 目前驗證層級是 `mock-heavy`、`hybrid` 還是 `full-integration`
  - 是否存在 `page.route()`、HAR replay、mock helpers、fake providers、storageState、auth fixture、固定 API response、或 screenshot fixture 讓畫面綠燈但 backend/auth 沒真的打通
  - login / SSO / token refresh / RBAC / dashboard data / 關鍵查詢頁 是否至少有一條 real-backend / real-auth smoke path
  - project review / manual / screenshot artifacts 是否明確標示資料來源，不會把 fixture/mock 當成真實整合證據
  - demo environment 是否與 test environment 有足夠接近的 service bundle、seed data、與 auth configuration
- Gate 結果只允許：`PASS`、`CONDITIONAL`、`FAIL`。
  - `PASS`：關鍵旅程存在 real-backend / real-auth evidence，mock 只扮演加速或 UI regression 輔助角色
  - `CONDITIONAL`：核心功能大致可運行，但仍有 mock / fixture blind spot，需要在 demo 前補 smoke 或補標示
  - `FAIL`：目前成果仍主要依賴 mock / fixture / fake auth，或 review artifact 會誤導利害關係人

若本次工作涉及 local dev / UAT / E2E stack，必須額外檢查 skill `local-infra-registry-governance` 的遵循情況：是否遵守 registry-governed flow、是否只在 exact match / resolver / HITL selection 後才 reuse instance、是否以 required service bundle 判定 readiness，且沒有把 live runtime allocation state 誤寫進 `SPECS.md` / `NEXT_STEPS.md`。這個檢查點應被納入「設計一致性」與「程式碼品質」分析，而不是額外改寫本 phase 的評分權重。

### 評分機制

每個維度使用 0-10 分評分，最終計算綜合得分：

- **需求符合度**（25% 權重）
- **設計一致性**（25% 權重）
- **程式碼規範性**（25% 權重）
- **程式碼品質**（25% 權重）
- **綜合得分** = 各維度得分 × 權重之和

### 複核報告生成

創建 `.agents/specs/{spec-directory}/review.md` 文件，包含：

- **評分總覽**：各維度得分和綜合得分
- **Live-Demo Readiness**：`PASS` / `CONDITIONAL` / `FAIL`、目前 coverage tier、已確認的真實整合證據、仍存在的 mock / fixture 風險
- **Security-Review Lane Summary**：若本次工作觸發 trust-boundary 條件，需摘要 security-review 的 findings、分類、主要 remediation 與 verification notes
- **Verification Coverage**：required test layers 的 planned vs executed 狀態，供 workspace `RTM.md` / `SPECS.md` 摘要聚合
- **Git / Worktree Hygiene**：本輪 review 使用的 branch/worktree strategy、是否維持單一 authoritative writable lane、是否仍有待清理的暫時 worktree / stale registration
- **Conflict Handling Evidence**：是否有另一條 lane 被正確降級為 audit-only、是否有 pre-write conflict checklist 的執行證據、是否有 ownership evidence、以及是否避免在衝突狀態下直接 patch authoritative artifact
- **Ownership / Conflict Record Location**：相關 evidence 是否實際存在於 invoking repo/workspace 內的 reports 或 governance artifact surface，而不是 global skills 安裝目錄
- **Validation Gate Result**：若本次 workstream 使用 `validate_governance_writeback.py`，其結果若為 FAIL，review 不得接受這次 governance writeback
- **Cross-Artifact Regeneration Order**：若本次工作跨 `TESTS.md` / `SPECS.md` / `RTM.md`，是否有證據顯示更新順序是從 upstream authority 重新生成，而不是 derived-to-derived 收斂
- **Governance Artifact Lifecycle**：若涉及 `ISSUE_LOG.md` / `NEXT_STEPS.md` / `RTM.md`，摘要其 lifecycle state、allowed next action、以及禁止寫入的 downstream surfaces
- **EDD / Eval Coverage**：若本次工作宣告了 capability eval / regression eval，需摘要 `eval-harness` 或等價 EDD 的執行情況、缺口與結果；若無法執行 app/runtime eval，必須明確說明退化為何種 deterministic readback grader，以及為何足以支撐本輪 review 結論
- **Project Review-Tooling Inputs**：若 `code-review` 家族可用（workspace-local 或 global skill home 皆算），摘要各工具（`code-review` / `test-quality-reviewer` / `security-risk-reviewer` / `sonarqube-bridge`）的 resolved-from（workspace / global / binary）+ 三態狀態 + findings。三態必須區分：`ran`、`unavailable`（skill 在 workspace 與 global 皆無）、`dependency-not-configured`（skill 可用但外部依賴未就緒，例如 `SonarQube not configured`、無 LLM provider）。`unavailable` 與 `dependency-not-configured` 不可混記，因兩者補救動作不同；避免讓 review 看起來覆蓋了實際未跑的偵測
- **Cross-Agent Review Summary**：若導引到 `cross-agent-review`（`xreview`），記錄：**outcome**（`consensus-reached` / `same-family-degraded` / `no cross-family reviewer configured` / `unavailable` / `skipped-*` 等其一）、**reviewer** family 與 `provider`（如 `codex / exec:codex`、`gemini-api`）、**independence 判定**（是否真的來自不同 family——是才可當獨立確認，否只能當額外 self-consistency）、以及**併入本輪的跨 model findings 與 disposition**。三態 `ran (cross-family)` / `dependency-not-configured` / `unavailable` 不可混記，避免把降級偽裝成已通過跨 model 獨立複核（false-green）。
- **Test Registry Hygiene**：duplicate IDs、stale rows、missing owner、missing canonical command、missing evidence refs、critical unmapped rows 的治理狀態
- **Acceptance Status**：per-spec 與 per-REQ 的 verdict，必須明確指出其 authority source 與 derived snapshot writeback 範圍
- **Repo-side Closure vs External Execution State**：明確聲明 repo-side closure 是否完成、external execution 是 pending / completed elsewhere / blocked、authoritative handoff path 在哪裡、以及 repo 內是否仍有任何可執行本地工作
- **FMEA Coverage**：高風險 failure modes 的 mitigation 狀態、未解決 residual risk、以及是否仍需 conservative downgrade
- **AI / Security / Privacy / Log Compliance Inventory**：若適用，摘要 `iso-ai-security-auditor` 的 scope、organization documents reviewed/missing、repo evidence refs、external-control table、assumed-baseline items、legal/regulatory caveats、以及 priority remediation backlog。
- **符合度分析**：詳細對比需求、設計與實作的一致性
- **問題清單**：發現的所有問題，按嚴重程度分類
- **改進建議**：具體的優化建議和修改方案
- **優化優先級**：建議的修復順序
- 生成 review.md 後，必須同步更新 `NEXT_STEPS.md`：至少寫入 review score、關鍵 blocker / 重大缺陷、是否進入 optimization、以及下一個 resume target。
- 若本次工作涉及 handoff / external execution，review 還必須做 stale-state hygiene：確認 `NEXT_STEPS.md`、`SPECS.md`、completed/reports/historical notes 不再把已完成的 repo-side handoff 寫成仍需本地執行，也不可同時留下 dual-state wording。
- 若本次工作預期應有 `eval-harness` / EDD evidence 而缺失，review verdict 至少降為 `CONDITIONAL`，不得只因文字看起來完整就直接 `PASS`。

### 完成標準判斷

- 綜合得分 ≥ 8.5 分 **且** Live-Demo Readiness = `PASS`：程式碼品質優秀；若 `Repo-side Closure vs External Execution State` 顯示 external execution 已完成或不適用，可完成此專案；若仍為 repo-side complete / completed-handoff / pending elsewhere，則只能宣告 repo-side review 完成，並進入 reconciliation / handoff closure
- 綜合得分 ≥ 8.5 分 **但** Live-Demo Readiness = `CONDITIONAL`：不得直接宣告 ready，需先補 demo gap 或在交付中明確降級聲明
- 綜合得分 6.0–8.4 分：存在改進空間，建議優化
- 綜合得分 < 6.0 分：必須進行優化
- 無論綜合分數多高，只要 Live-Demo Readiness = `FAIL`，都必須進入優化或補測流程
- `review.md` 是 authoritative readiness artifact；任何 workspace `RTM.md` / `SPECS.md` 摘要都只能引用這裡的結論，不可反向取代它。
- 若需要更新 `SPECS.md` / `RTM.md`，只能進行 **single snapshot write**；不得讓 `SPECS.md` 與 `RTM.md` 互相收斂或互相糾正。
- 若需要更新 `.agents/specs/TESTS.md`，該更新只能根據 folder-level `TESTS.md` 與 upstream evidence 產生；不得把 workspace TESTS rollup 反向當成 row-level authority。

### 交互確認

- 如果綜合得分 ≥ 8.5 分，詢問：「程式碼複核完成，品質評估為優秀。若 external execution 已完成或不適用，我們可以完成此專案；若目前是 repo-side complete / handoff package，是否先做 reconciliation / handoff closure 更新？」
- 如果需要優化，詢問：「發現了一些需要改進的地方，是否開始程式碼優化？」
- 若 Live-Demo Readiness 不是 `PASS`，應改為明確說明 blind spot，例如：「目前 review 分數不錯，但 live demo 仍受 mock / auth fixture 風險影響。是否先補真實整合 smoke / auth 驗證，再進入 project review 或 manual 產出？」
- 若本次 slice 主要是 workflow / skill / governance 變更，應額外明確說明：「本次 review 結論只代表 workflow wording / trigger model 已完成本輪驗證；若後續要證明它在更多 skill 或更多 sprint 中有效，仍需後續 slice 或 retrospective evidence。」

## Local Infra 複核檢查點

- 是否有直接繞過 registry 的 compose / podman 啟動或釋放行為
- 是否以 guessed ports / guessed stack names 取代 allocation authority
- 是否錯把 `podman ps` 當成唯一真相，而沒有 reconcile / ownership 說明
- 是否把 live runtime allocation state 寫進 feature governance 文件
- 若該 runtime 也承擔 demo / review / screenshot / manual 來源，是否清楚區分了 test env 與 demo env，並以 required service bundle readiness 證明真實整合可用
- 若使用者已明確表示 external execution completed elsewhere，是否已停止本地執行迴圈，改為宣告 repo-side closure 與 stale-state reconciliation

## 重要約束

- 必須基於完整的需求、設計、任務文件進行複核
- 評分必須客觀、詳細，有具體的問題和建議支撐
- 複核報告必須清晰、可操作，便於後續優化
- 必須等待用戶明確決定是否進入優化階段

## 完成標誌

創建 review.md 文件並獲得用戶對後續行動的明確指示
