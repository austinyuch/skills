# 第四階段：程式碼實作

## 觸發條件

- 任務清單已完成並獲得您的認可
- 或您指定要實作某個具體任務

## 我的工作

### 1. 實施前準備

- 調整到 thinkharder 模式，收集足夠完整的上下文。
- 必須先閱讀 `.agents/specs/{spec-directory}/` 下的 `requirements.md`、`design.md` 和 `tasks.md`，以及 `{workspace}/contract/` 下對應的契約檔案。
- 若本任務涉及 governance artifact 更新或 closeout，必須先讀取 `../reference/SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md`，確認 `ISSUE_LOG.md`、`NEXT_STEPS.md`、`TESTS.md`、`RTM.md`、`SPECS.md`、`review.md` 的更新順序。
- 若 `{workspace}/.agents/specs/NEXT_STEPS.md` 存在，必須先讀取它以恢復 current task、last verified state、blockers 與 resume hint；若與 `tasks.md` / `SPECS.md` 不一致，必須先校正再實作。
- 若使用者已明確告知 external execution 已在別處完成，或此事實與 `NEXT_STEPS.md` / `tasks.md` 的既有描述衝突，必須立即停止當前 local execution lane，切換到 drift-reconciliation / repo-state update；不得把 external execution 重新包裝成新的本地實作任務。
- 若 `tasks.md` 已規劃 branch/worktree isolation，實作前必須先依 `../../shared-governance/references/git-worktree-guide.md`、`../../shared-governance/references/git-worktree-templates.md`、`../../shared-governance/references/concurrent-writable-lanes.md`、`../../shared-governance/references/pre-write-conflict-checklist.md`、`../../shared-governance/references/ownership-evidence-template.md` 與 `../../shared-governance/references/cross-artifact-regeneration-order.md` 驗證 lane hygiene：
  - 目前 branch 是否已在其他 writable worktree 被占用
  - 這次工作是否應建立 / 重用 dedicated writable worktree
  - 若當前 worktree 是 detached audit lane，必須先切換到正式 authoring lane 才能改檔
  - 不可把 worktree path 或本機暫存位置寫進 spec artifacts
  - 若同一份 authoritative artifact 已由另一條 lane 擁有 writeback 權，必須停止正式寫入並降級為 audit-only / reconcile-first
  - 若準備正式 writeback，必須先補齊 ownership evidence，並把它寫入 invoking workspace 的 canonical artifact location；lane-id / evidence filename 應遵守 shared-governance 的 naming convention，而不是等 review 再回想
- **(新增) Code Generation First**：若當前任務涉及資料模型或 API 型別，**嚴禁手寫這些基礎型別**。必須優先執行指令或腳本，從 Contract (如 JSON Schema, OpenAPI) 自動生成 TypeScript Interfaces, Pydantic Models 等。
- **(新增) 防漂移修復**：若先前的架構設計修改了 Contract，必須在實作業務邏輯前，先執行全局型別檢查 (`tsc` 等)，找出並修復舊有模組因 Contract 改變而導致的編譯錯誤。

### 2. 思考過程展示（每個任務必須）

在修改任何程式碼之前，需要清晰展示：
1. **問題分析** - 這個任務要解決什麼問題？
2. **方案選擇依據** - 為什麼選擇這種實作方式？
3. **規範與契約依據** - 參考了哪些規範規則與 `{workspace}/contract/` 定義？
4. **需求追溯 (Traceability)** - 此任務對應哪一個 Requirement ID (`REQ-XXX`)？
5. **(新增) Ponytail Rung 5-6 最小實作檢視** - 這個實作是否已經走到 ladder 的最小可行解？
   - **Rung 5**：這個邏輯能否用一行（或極短片段）完成？若可以，是否過度包裝成了 class / module / service？
   - **Rung 6**：目前的實作是否為「當下需求所需的最小正確實作」，而非「預留擴展的通用版本」？
   - 若為了可讀性、可測試性、或架構一致性而需要多一層抽象，應在此說明理由。
   - 參考：[`references/ponytail-yagni-ladder.md`](../references/ponytail-yagni-ladder.md)

### 3. 程式碼分層規範複習（重要）

在每個程式碼開發任務開始前，必須：
1. 識別程式碼分層（Controller、Service、Repository 等）。
2. 讀取 `.agents/steering/` 或 `AGENTS.md` 下對應分層的規範文件。
3. 若規範指定了參考文件，必須重新讀取這些參考文件。
4. 向用戶展示該分層的核心規範要點。

### 4. 任務執行策略

- **嚴格一次只專注一個任務**，從子任務開始。
- 使用 Test-Driven Development 流程 (skill `tdd-workflow`)。
- **(Capability-Gated Left-Shift)** 進入 TDD 的 **REFACTOR** 步驟時，若 `code-review` skill 家族可用（workspace-local 或 global skill home 皆算，見 SKILL.md Global Constraint #14），把以下偵測前移，作為 review 之前的便宜 pre-flight；皆不可用則沿用既有人工 refactor，不阻塞：
  - 對 changed files 跑 `code-review`（含 `review --vet --race` 等背景經典問題：race / deadlock / lock-no-defer / money-float 等），依語言受支援程度 gate。
  - `code-refactoring-advisor` 提出 Fowler smell → move + safety-net 建議（advisory，由你決定採納）。
  - 對本次新增 / 變更的測試跑 `test-quality-reviewer`（FIRST / test-smell / pyramid）。
  - 這些工具是 left-shift 偵測與建議，**不是** verdict authority；正式裁決仍在 Phase 5 `review.md`。
- **(Trust-Boundary Pre-Flight)** 若本任務觸及 identity / data / execution / infrastructure / agent 任一 trust boundary，且 `security-risk-reviewer` 可用（workspace-local 或 global skill home 皆算），先跑其 deterministic、offline 掃描，其 findings 將餵給 Phase 5 既有的 mandatory `security-review` gate（compose, not replace）。
- **(Ponytail × Code-Review 協作)** 進入 TDD REFACTOR 步驟時，除了 `code-refactoring-advisor` 的 Fowler smell 偵測，還必須以 **Ponytail Rung 5-6** 自我檢視：這段程式碼是否可以用更少行數完成？是否過度包裝了一個本來可以一行解決的邏輯？兩者結果若衝突（ladder 說「一行就夠」，refactoring advisor 說「抽出 function」），以「可讀性與可測試性」為最終判準，並在報告中說明理由。`test-quality-reviewer` 應同步檢查測試是否過度複雜（例如為了一個標準函式庫的內建函數寫了過多 test helper）。
- 完成任務後，在 `tasks.md` 中將任務標記完成 (`[x]`)，並極簡要更新內容。
- 撰寫任務完整報告於 `.agents/specs/{spec-directory}/reports/`。
- 每完成一個任務或準備暫停時，更新 `NEXT_STEPS.md`：至少記錄 current task / last completed task、最新驗證結果、下一個建議動作、blockers、以及 resume hint。
- 若本 branch-spec 的治理邊界顯示目前屬於 `completed-handoff` / `external-blocked`，implementation 階段只能完成 repo-side closure、handoff artifact 更新、或 stale-state reconciliation；不得把 external execution 本身當成可在本階段補做的本地工作。
- **(新增) Git 聯動**：在完成一個具體功能節點並準備 Commit 時，Commit Message 必須包含 `Ref: {spec-name}` 或對應的 `Ref: {REQ-ID}`。
- 若本次 lane 使用 dedicated writable worktree，暫停 / handoff 時必須清楚留下 branch identity、目前是否可安全重用該 lane、以及是否仍有未提交變更；但這些資訊應放在 session / report / repo-local execution 說明中，不可把 machine-local path 寫進 registry artifacts。
- 若 implementation 期間發現 lane ownership 衝突、dirty reusable worktree、或更新的 upstream facts 讓既有 snapshot 失效，必須停止 incremental patch，回到 upstream authority 重讀與 ownership resolution；不要在衝突狀態下繼續 patch authoritative file。
- 若任務涉及 `TESTS.md`、`SPECS.md`、`RTM.md`，先更新 upstream authority（`review.md`、test reports、test catalog），再由單次 snapshot 更新 derived fields；禁止 derived-to-derived sync。
- 若任務承接 `ISSUE_LOG.md` 的 folded / promoted item，只能更新正式 SDD artifacts 與 issue disposition pointer；不可在 implementation 中把 issue row 直接寫進 `RTM.md` 或 `SPECS.md`。
- 若任務涉及 `TESTS.md`、workspace `.agents/specs/TESTS.md`、`SPECS.md`、或 `RTM.md` 的跨 artifact 更新，必須依 `../../shared-governance/references/cross-artifact-regeneration-order.md` 的順序重新生成，而不是在剛寫出的 derived artifact 上做修補式同步。
- 若任務需要刷新 `TESTS.md`，必須先更新最近的 folder-level `TESTS.md`，再視需要交由 `test-registry-manager` 刷新 workspace `.agents/specs/TESTS.md`。不得直接把 workspace rollup 當成 row-level authority 編修。

### 5. 任務推薦

- 如果您指定了具體任務，就實作該任務；否則我會推薦下一個應該執行的任務。

### 6. 品質控制與驗證 (EDD)

- 根據 tasks.md 定義的 Eval Check (例如單元測試指令)，實際執行腳本以客觀驗證任務是否真正完成。
- 若本次工作有 capability / regression 評估價值，應明確使用 `eval-harness` skill 或等價 EDD 流程來定義與執行 eval，而不是只停留在 ad-hoc test command。
- 對於 workflow / skill / governance 類變更，若沒有可執行的 app/runtime target，也應至少以 readback / grep / deterministic grader 的形式保留 EDD 思維，並在 report / review 中說明為何該 eval 層級足夠。
- 若測試失敗，在當前 task 內修正並紀錄。未達允收準則不會自動進入下一個任務。
- 若任務產出 test execution evidence，應先寫入 `TESTS.md` 或 reports；`RTM.md` / `SPECS.md` 只接收 derived snapshot，不作為 implementation authority。
- 若任務新增或採用測試，應同步補齊 `Test ID`、`Task / Spec Trace`、`Requirement / AC Trace`、`Canonical Command`、`Evidence Ref`。若映射仍不可靠，保守標成 `unmapped` / `partial`，不要硬補假的 traceability。
- 若 design / tasks 含有 FMEA，高風險 mitigation 與其 negative-case validation 必須優先於低風險 polishing work。不要先完成好看的 happy path，再把 false-green / overclaim 風險留到最後。
- 若任務涉及 UI、E2E、manual、dashboard、auth flow、或 demo path，必須在完成前先標註目前驗證層級：`mock-heavy`、`hybrid`、或 `full-integration`。這個標註必須寫進任務報告或 `NEXT_STEPS.md`，不能只留在對話中。
- 若存在 `page.route()`、routeFromHAR、mock helpers、fake providers、storageState、auth fixture、固定 API response、或 demo seed data，必須盤點哪些驗證被它們短路，並安排至少一條 **real-backend / real-auth smoke path** 去覆蓋高風險旅程。
- 若 FMEA 已指出「summary overclaim」「warning propagation loss」「planned vs executed confusion」「stale / missing refs」等風險，實作時必須把對應 validation 一起落地，而不是只完成資料流或 UI 輸出。
- 對 login、SSO、token refresh、RBAC、dashboard data loading、impersonation、或關鍵查詢頁，若只有 fixture / mock 驗證而沒有真實整合 smoke，任務不得標記為 demo-ready。
- 若使用 screenshot 或 project review artifacts 當作「功能已完成」證據，必須同步記錄該畫面是來自真實整合還是 fixture/mock。模擬資料可作為 UI regression 證據，但不可冒充 live-demo readiness evidence。

### 7. 並行操作優化

- 盡可能優先並行調用工具（例如同時搜尋多個檔案、或讀取多個模組）。

### 7.5 Local Infra 實作邊界

- 若當前任務需要啟動 local dev / UAT / E2E stack，必須先遵守 `local-infra-registry-governance`：query registry → exact match / resolver / developer selection → reconcile → allocation / reuse → governed action。
- 不可直接根據「看起來沒人用」的 localhost port、container name、或 network name 自行啟動 compose / podman。
- `devops-container-orchestration` 可以用來決定 compose / Podman 的實作細節，但不能取代 registry query / lock / reconcile。
- 若缺少 registry-governed tool 或 allocation authority 不明，應回報 blocker，而不是自行建立 shadow workflow。
- 若 local runtime 需要多個 services，必須先確認 required service bundle 全部 ready，才可進入後續 QA / manual / E2E flow。

### 8. Circuit Breaker, 求助與回報

- **任務失敗紀錄**：於 `reports/` 記錄失敗嘗試與改善方向。
- **卡關處理機制**：嘗試 3 次仍卡關，請立刻停止盲目除錯。切換為「Senior Software Architect」，對過去的錯誤進行根因分析 (RCA)，提出新策略並等待人類認可。
- 在切換到 RCA、等待外部輸入、或中止當前 session 前，必須先更新 `NEXT_STEPS.md`，留下最後驗證點、目前 blocker、以及下次恢復時的第一步。
- 重試達 6 次仍失敗，直接終止任務並明確請求協助。
- 若發現 auth fixture、storageState、fake token、mock provider fallback、或固定 API response 讓測試看似通過，但真實 backend / auth 路徑尚未被驗證，必須立即觸發 circuit breaker：停止把當前成果描述為 ready，改為建立專門的 live-demo risk 報告與補測任務。

## 關鍵原則

- **一次一個任務**。
- **Contract 優先，嚴禁手寫基礎型別**。
- **確保 Traceability**：所有改動與 Commit 必須能追溯至 Requirement ID。
- **持續驗證**：依賴客觀指令 (Eval Checks) 而非主觀感覺。

## 完成標誌

- 所有任務在 `.agents/specs/{spec-directory}/reports/` 文件中記錄完成狀態。
- 完成實作後更新 `{workspace}/docs/*FEATURE_INVENTORY.md` 以及 **workspace-scoped** `AGENTS.md`（如有必要）；不得把這條要求解讀為更新 global `~/.config/opencode/AGENTS.md`。  
