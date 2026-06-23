# 第三階段：任務規劃

## 觸發條件

- 設計文件已完成並獲得您的認可
- 或您表示要規劃實施任務

## 我的工作

1. 調整到 ultrawork 模式，完全了解專案程式碼與規範，收集上下文。
2. 仔細研讀 `requirements.md`, `design.md` 以及 `{workspace}/contract/` 內的相關定義。
3. 讀取 `{workspace}/.agents/specs/NEXT_STEPS.md`（若存在），確認目前的 active spec、open CRs、last verified state、以及上次 session 留下的 resume hint，並與 `SPECS.md` / design 內容對齊。
3.1 若任務會影響 `ISSUE_LOG.md`、`TESTS.md`、`RTM.md`、`SPECS.md`、`NEXT_STEPS.md` 或 `review.md` 的 lifecycle / authority boundary，必須讀取 `../reference/SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md`，並將 closeout / refresh 任務顯式寫入 `tasks.md`。
4. 創建 `.agents/specs/{spec-directory}/tasks.md` 文件。文件開頭必須說明相關章節的引用參照。
4.5 **(新增) Git / Worktree Lane 規劃**：若本次工作涉及 parallel spec lane、CR overlay、repo-owned global skill / shared governance wording 變更、或大型 `TESTS.md` / `SPECS.md` / `RTM.md` refresh，必須先讀 `../../shared-governance/references/git-worktree-guide.md`、`../../shared-governance/references/git-worktree-templates.md`、`../../shared-governance/references/concurrent-writable-lanes.md`、`../../shared-governance/references/pre-write-conflict-checklist.md`、`../../shared-governance/references/ownership-evidence-template.md` 與 `../../shared-governance/references/cross-artifact-regeneration-order.md`，並在任務規劃中明確決定：
    - 這次工作是否需要新的 writable branch / worktree
    - 是否只需要 detached / read-only audit worktree
    - authoritative writeback 由哪一條 lane 負責
    - closeout 時是否需要清理暫時 worktree
    - 任務文件只記錄 lane strategy，不記錄 machine-local worktree path
    - 若另一條 lane 已擁有同一份 authoritative artifact，這次工作是否必須降級成 audit-only / reconcile-first
    - 正式 writeback 前要留下哪份 ownership evidence，以及它會落在哪個 invoking workspace artifact（例如 `{spec-directory}/reports/...` 或 workspace `.agents/specs/governance/...`），並使用哪個 lane-id / filename slug
5. **(新增) Re-sync Gate 優先條件**：若本次 spec 存在 `Open Change Requests`，或相依的契約標記 `Contract Authority=external`，則必須規劃 re-sync gate：在 **baseline-touch**、shared/external contract 依賴被實際使用之前，或在 review / merge 前，重讀最新 `SPECS.md`、確認 CR 仍有效、確認 `Source of Truth` / `Pin/Version` 未漂移。
    - 若 first slice 一開始就直接依賴該 shared / external baseline，re-sync gate 應成為第一個任務；否則可作為 JIT gate，而不是 universal first-task bookkeeping。
    - 此任務完成時，必須把結果寫回對應 CR 的 `Re-sync Freshness Evidence`，而不是只在任務描述中口頭提及。
6. **(新增) Code Generation 任務優先**：若有定義 contract (如 JSON Schema, TypeSpec 等)，確保 **第一個 coding 任務** 是將 Contract 轉換/編譯為應用程式的 TypeScript Types、Pydantic Models、Prisma Schema 等。**禁止手寫這些基礎模型**。
7. **(新增) 處理規格漂移 (Drift Repair)**：如果在 Phase 2 修改了共用 Contract，必須加入一項任務：「執行全局型別檢查 (`tsc`, `mypy` 等)，並修復因 Contract 變動而損壞的舊有實作程式碼。」
8. **(新增) Live Demo Readiness 任務前置判斷**：若功能涉及 UI、manual、project review、dashboard、auth、E2E、demo script、或任何需要向利害關係人展示的流程，任務規劃中必須明確聲明目前的 readiness posture 與 critical journeys。只有當 first slice 本身就是 stakeholder-facing / demo-facing slice 時，才需要在前段任務中加入完整 live-demo readiness workstream；否則應把 full inventory 與 final verdict 留給 review / closeout。
9. **(新增) FMEA Mitigation Trace**：若 design 含有 lightweight FMEA，則任務規劃必須先把 high/major risk 的 mitigation trace 進 `tasks.md`，不得只保留在設計文字中。
9.05 若 design 定義了 issue log 或 improvement classification，任務中必須顯式保留：哪些問題留在既有 active spec、哪些透過 CR 承接、哪些只是 issue-log 候選，避免實作階段再臨時改 lane。
9.06 若 `ISSUE_LOG.md` item 已 `Folded` / `Promoted`，任務中必須包含更新 issue disposition pointer 的 closeout 任務；若仍是 holding，任務中不得把它寫成正式 requirement 或 RTM row。
9.1 若 design 定義了 `TESTS.md` / `SPECS.md` / `NEXT_STEPS.md` / `RTM.md` 的 authority boundary，任務中必須保留對應的 prevention / detection tasks，避免循環更新。
9.2 若本次 spec 會新增、採用、重命名、淘汰、或重新驗證 tests，任務中必須包含 `TESTS.md` closeout / handoff 項；folder-level `TESTS.md` 的 row-level 更新可由 implementation 任務完成，但 workspace `.agents/specs/TESTS.md` 的 reconciliation / rollup refresh 應明確標註交由 `test-registry-manager` 執行，而不是在 task 中直接把 workspace rollup 當 row-level truth 修改。
9.3 若 impacted baseline 由 `Open Change Requests` 承接，任務中必須包含 freshness / closure 任務，並檢查 critical test evidence 是否因該 CR 變更而失效或需要重新標記為 stale。
10. 將功能設計轉換為一系列離散、可管理的編碼步驟，確保早期驗證核心功能。
11. 只專注於涉及編寫、修改或測試程式碼的任務。
12. **(新增) TDD 任務結構顯式化**：若本次任務採用 TDD/EDD，任務規劃不得只寫「寫測試」與「實作功能」；必須明確決定 REFRACTOR 如何被追蹤。
12.1 最少需滿足下列其中一種：
   - 為每個 critical slice 顯式拆成 `RED`、`GREEN`、`REFACTOR` 子步驟
   - 或至少在該任務的驗收 / Eval / Result 欄位中明確聲明「通過測試後要執行何種 refactor 與如何驗證 refactor 沒破壞行為」
12.2 若本次工作是 refactor-heavy、workflow/governance wording、shared skill 行為調整、或跨模組整合，優先採用顯式 `RED/GREEN/REFACTOR` 子步驟，而不是把 refactor 留成隱性假設。

## 任務格式要求

- 使用帶編號的核取方塊列表，最多 3 級層次結構（例如：`- [ ] 1.1 任務標題`）。
- 頂層項目僅在需要時使用，優先選擇簡單結構。

## 每個任務項必須包含

- 清晰的目標（編寫、修改或測試）。
- **(新增) 需求追溯 (Traceability)**：必須明確標註滿足了哪一條 Requirement ID（例如 `[Implements REQ-AUTH-001]`）。
- 對應的 EDD 驗證點 (Eval Check)（例如 `npm test` 指令）。
- 若該任務採用 TDD，必須說明 REFRACTOR 如何被處理：是獨立子任務、內嵌於同一任務的最後一步，或以何種 readback / eval 證明 refactor 後仍保持 green。

## 任務內容約束

- 不包含設計文件中已涵蓋的過度細節。
- 每個步驟在之前步驟的基礎上漸進構建。
- 預設不包含測試任務，除非用戶特別說明（但建議採用 TDD workflow）。
- 若任務聲稱採用 TDD，不能只停在 RED/GREEN；任務規劃必須明確保留 REFRACTOR 落點，避免「測試綠了就結束」的假完成。
- 若 design 有 FMEA，至少要把每個 high/major risk 對應到一個 prevention task 與一個 detection / validation task；若該風險在 first slice 內無法完全移除，則必須加入 containment / fallback task 或 closeout note。
- 設計時考量平衡平行開發，儘量減少整合複雜度，設計「移除 mock 採用真實實作並重新測試」的整合任務。
- 若存在 UI / E2E / demo 範圍，任務中應為**受影響的 critical journeys**安排必要的 real-backend / real-auth smoke 升級任務。完整 **E2E coverage tier inventory** 應以 `review.md` 與 workspace rollup 為主；除非 first slice 本身就是 stakeholder-facing / demo-facing slice，否則不要把 full inventory 變成前段 bookkeeping。
- 任務規劃時應視 `tasks.md` 為 implementation truth；workspace `RTM.md` 若存在，只能聚合 `[Implements REQ-*]`、verification layers、與 `review.md` 參照，不得反向成為任務 authoring 來源。
- `NEXT_STEPS.md` 只記錄下一個可恢復動作與 blocker；不得把完整 task list、execution ordering、safe-to-resume 細節、或 issue rows 複製進去。
- 若需要更新 `TESTS.md`，任務必須區分兩層：folder-level row updates 與 workspace `.agents/specs/TESTS.md` rollup refresh。前者是 authority update，後者是 derived maintenance。
- 若任務規劃要求 branch/worktree isolation，必須顯式保持 **一條 writable lane 對應一條 branch**；不要把多條 authoring lane 壓進同一個 worktree，也不要把 detached audit lane 寫成正式 writeback lane。
- 若工作分類不是 `new spec`，任務開頭必須清楚聲明目前 lane 是 `continue active spec`、`CR against completed spec`、或 `issue-log candidate`；禁止在 implementation 中途因為方便就切成新的未經批准 spec。
- `RTM.md` 不得承擔 task-counter、execution ordering、resume ownership、或 per-task progress authority；這些資訊的真相來源仍是 `{spec-directory}/tasks.md`、reports、與 `review.md`。
- `tasks.md` 只負責鏡射 `requirements.md` / `design.md` 已宣告的 repo-local vs external 邊界，不得在任務層自行發明 handoff lane、把 external execution 改寫成 local action、或反向取代 branch-spec 治理判定。
- 若 design 宣告了 `TESTS.md` / `SPECS.md` / `RTM.md` 的治理模型，任務若更新這些 artifact，必須遵守 one-way non-cyclic rollup：先更新 upstream authority，再由單次 snapshot 更新 derived outputs。
- 若任務會跨 `TESTS.md` / `SPECS.md` / `RTM.md` 進行摘要寫回，必須依 `../../shared-governance/references/cross-artifact-regeneration-order.md` 明確指定 regenerate 順序，不得在任務中留下含糊的「之後再同步」描述。
- 禁止 derived-to-derived sync（例如從 `SPECS.md` 回填 `RTM.md`，或從 `RTM.md` 回填 `TESTS.md`）。
- 若需要使用 graph 輔助規劃，必須明確標示其為 enhancement，不得將 graph 結果描述成 authority truth。
- 若 FMEA 指出「planned 被說成 executed」「summary 比 source 更樂觀」「warning code 可能遺失」「source ref 可能 stale / missing」等風險，任務中必須加入對應 negative-case validation，而不是只驗 happy path。
- 若存在 `page.route()`、mock helpers、HAR replay、fake providers、auth fixture、storageState、demo seed data、或 screenshot fixtures，任務中必須加入「盤點與去風險」項，明確說明哪些可保留、哪些必須在 demo 前替換成真實整合驗證。
- 若流程涉及登入、SSO、token refresh、RBAC、或 impersonation，任務中必須加入 **auth fixture coupling check**：確認測試沒有只依賴預先注入的 storage state / fake token，而忽略真實 auth path。
- 若存在 re-sync gate，後續 code generation、drift repair、integration 任務都必須顯式依賴該 gate 成功完成。
- 若存在 open CR，任務尾端必須安排一項治理收斂任務：`Closed` 或 `Superseded` 該 CR、更新 `Resolution Notes`，並同步清理 active spec 與 `SPECS.md` 的 `Open Change Requests` 摘要。
- 任務定稿後，回寫到 `NEXT_STEPS.md` 的內容必須保持高階、簡短、可追溯：只寫 current phase、active spec、next action、blocker / waiting item、resume hint、related artifacts。不要複製 task list、task progress、execution ordering、或 safe-to-resume 細節；這些內容應留在 `{spec-directory}/tasks.md`、CR、或 reports。
- 若 `tasks.md` 超過 3000 行，將完成的部分備份至 `tasks-{phase}.md` 並建立摘要。

## Local Infra 任務規劃補充

- 若任務需要 local dev / UAT / E2E 服務，必須顯式引用 skill `local-infra-registry-governance`，並加入對應的 registry-governed 任務，例如：query registry、exact-match / resolver / HITL selection、reconcile、request/reuse env、release / gc 收斂。
- 任務描述應使用 high-level governance 語言（例如 `request env`, `reuse instance`, `release expired env`），不要直接要求 agent 執行 ad-hoc compose / podman 指令。
- 若實作後會暫時佔用 live resources，任務尾端必須安排 cleanup / release 或確認 reuse ownership 的步驟，避免把殘留 instance 留給下個 session 猜測。
- `SPECS.md` / `NEXT_STEPS.md` 只需記錄高層 blocker 或治理結論，不可把整份 local infra inventory 貼進任務文件。
- 若 runtime success 需要 1..n services，任務必須顯式記錄 required service bundle，而不是假設單一 port 開啟就算成功。
- 若 local runtime 也承擔 demo / review / screenshot 來源，任務必須額外指定這些 artifacts 是否允許使用 fixtures；預設應至少保留一條 real-backend path 作為 live-demo readiness evidence。
- 若這次 lane 使用暫時 writable worktree，任務尾端應安排 closeout：確認已 merge / handoff 後移除 worktree，必要時補做 `prune`；若只使用 detached audit worktree，則應在報告中確認它沒有承擔正式 writeback。

## 示範格式

```markdown
# 實施計畫

- [ ] 1. Re-sync Gate
  - [ ] 1.1 重讀 `.agents/specs/SPECS.md`，確認 `CR-2026-004` 仍為有效 open CR，且 external `Pin/Version` 未漂移
    - _需求: [Implements REQ-SYS-001]_
    - _產出: 更新 `CR-2026-004` 的 `Re-sync Freshness Evidence`_

- [ ] 2. Contract & 模型生成
  - [ ] 2.1 執行腳本從 `contract/openapi.json` 生成 TypeScript 型別
    - _需求: [Implements REQ-SYS-001]_
  - [ ] 2.2 執行全域 `tsc` 檢查並修復舊模組的編譯錯誤 (Drift Repair)
    - _需求: [Impacts: old-auth-spec]_

- [ ] 3. 實作資料模型和驗證
  - [ ] 3.1 實作帶驗證的 User 儲存庫
    - _需求: [Implements REQ-AUTH-001]_
    - _Eval: `npm run test:unit -- userRepository`_

- [ ] 3A. TDD cycle for critical slice
  - [ ] 3A.1 RED：先補一個目前失敗的測試 / grader
    - _需求: [Implements REQ-AUTH-001]_
    - _Eval: 測試在實作前失敗_
  - [ ] 3A.2 GREEN：加入最小實作讓測試通過
    - _需求: [Implements REQ-AUTH-001]_
    - _Eval: 測試轉為通過_
  - [ ] 3A.3 REFACTOR：整理命名、抽取共用函數、降低重複，並確認行為仍為 green
    - _需求: [Implements REQ-AUTH-001]_
    - _Eval: 原測試與回歸驗證仍通過_

- [ ] 4. 治理收斂
  - [ ] 4.1 更新 `CR-2026-004` 的 `Resolution Notes`，並將狀態標記為 `Closed` 或 `Superseded`
    - _需求: [Implements REQ-SYS-001]_
  - [ ] 4.2 從 active spec 與 `.agents/specs/SPECS.md` 的 `Open Change Requests` 摘要移除或替換 `CR-2026-004`
    - _需求: [Implements REQ-SYS-001]_

- [ ] 5. External execution handoff
  - [ ] 5.1 finalize arm64 verification handoff package（彙整 command、artifact path、success criteria、owner）
    - _需求: [Implements REQ-SYS-001]_
    - _Eval: `review.md` / `NEXT_STEPS.md` 明確聲明 repo-side closure completed，且 external execution 另有權威 handoff path_
```

## 測試義務種子（Capability-Gated）

- 若 `test-design-generator` 可用（workspace-local 或 global skill home 皆算，見 SKILL.md Global Constraint #14），規劃 test obligations 時可先用它對關鍵 REQ / AC 產生 boundary / equivalence / pairwise 候選案例，作為 `tasks.md` 測試任務與 `TESTS.md` 草稿列的 **advisory 種子**。
- 它只提出候選案例，不裁決覆蓋率，也不自動寫入 `TESTS.md`；最終要納入哪些案例、如何對應 `Test ID` / `Requirement / AC Trace`，仍由本階段規劃決定。
- 在 workspace 與 global home 皆不可用時，照常以人工方式定義 test obligations，不需阻塞。

## 重要約束

- 必須等待您的明確認可才能完成工作流程並進入 Phase 4。
- 如果在規劃期間發現差距，會建議返回之前步驟（需求或設計）。

## 完成標誌

用戶明確同意任務規劃。
