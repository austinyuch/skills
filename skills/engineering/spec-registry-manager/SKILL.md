---
name: spec-registry-manager
description: 負責掃描專案內的所有 Specs 文件，進行規格盤點與狀態更新，並生成或維護全局規格註冊表 (`SPECS.md`)。當使用者要求「盤點 spec」、「更新 SPECS.md」、「建立規格目錄」，或需要管理 completed spec 的 change request、cross-spec 影響、external contract 依賴治理、continuous-improvement fragmentation 風險摘要、以及跨 spec 的 live-demo readiness / false-green review 風險摘要時使用。這個 skill 不負責 live local infra runtime registry，也不直接重做 runtime 驗證。
---

# Spec Registry Manager

這個 skill 專注於掃描與更新 `spec-driven-development` 工作流所產生的所有規格文件，確保專案具備完整且一致的 **Feature Registry (全局規格註冊表)**。

## 觸發情境

- 使用者要求「盤點目前的 specs」或「更新 `SPECS.md`」
- 專案剛導入 `spec-driven-development` 且需要初始化舊有系統清單
- 在 SDD 開發過程中需要分析系統間的 Spec 依賴關係
- 尋找某個模組是否已經存在過 Spec 紀錄
- 當 `[Completed]` Spec 被其他新需求影響，需確認是否已有對應的 Change Request (CR)
- 當 Spec 依賴外部系統 / 外部契約，需補齊 `Contract Authority`、`Source of Truth` 與 `Pin/Version`

> 若主要需求是更新 folder-level `TESTS.md`、刷新 workspace `.agents/specs/TESTS.md`、整理 duplicate test IDs、stale rows、或 row-level requirement / AC traceability，應改交給 `test-registry-manager`。本 skill 只消費 test summary，不維護 row-level test catalogs。

## 核心工作流程

你的任務是根據專案目錄中的現有狀況，掃描並產出/更新一份符合格式的 `SPECS.md` 文件。

`SPECS.md` 不只是 inventory，也是一份 **輕量治理登錄表**：
- 描述每個 Spec 的生命週期狀態
- 區分 `Depends On`（上游依賴）與 `Impacts`（下游受影響對象）
- 摘要顯示 `Open Change Requests`
- 為外部契約標記 `Contract Authority`、`Source of Truth`、`Pin/Version`
- 以**摘要**形式滾動呈現該 spec 最近一次已知的 demo / evidence posture（若上游 review 已提供）
- 在尚未產生 `review.md` 正式 readiness verdict 前，可摘要 requirements / design / tasks 已知的 **pre-review caution summary**（例如 early false-green、mock-dominant、artifact honesty 風險），但不得把這些 caution 寫成 `PASS` / `CONDITIONAL` / `FAIL`
- 視需要與 workspace-level `RTM.md` 協同，提供 traceability completeness / refs 的治理摘要
- 視需要摘要 `ISSUE_LOG.md` pointer 與 promotion 風險，但不得把 issue-log surface 本身當成 stable spec registry 替代品

上述 summary 都必須維持**高層、保守、可追溯**：
- registry 只摘要已存在 artifact 的結論或 caution，不自行推導 readiness
- registry 不記錄 per-task progress、task counters、execution ordering、或 resume ownership
- 若需要了解細節，應回到 `{spec}/tasks.md`、`review.md`、或 reports，而不是把那些內容複製進 `SPECS.md`

它**不應**承載即時 branch 狀態，也不應成為完整 CR 內容的容器；CR 細節固定放在 `.agents/specs/{linked-active-spec}/change-requests/{cr-id}.md`。需要固定格式時，請參考 [輕量 CR template](./references/change-request-template.md)。

`{workspace}/.agents/specs/NEXT_STEPS.md` 若存在，應視為 **跨 spec 共用的滾動式 operational memo**，不是 spec artifact、不是 registry entry，也不是 CR overlay。此 skill 不負責將它盤點為 spec 條目，也不負責把其中的 rolling state 寫入 `SPECS.md`。

`{workspace}/.agents/specs/RTM.md` 若存在，應視為 **workspace-level synthesized rollup**，用來統合各 spec 的 `requirements.md`、`design.md`、`tasks.md`、`review.md` 參照。此 skill 可協助掃描或摘要其狀態，但不可把 `RTM.md` 誤當成 spec-level source of truth。

`RTM.md` 也**不得**被視為 task-counter、execution-order tracker、resume controller、或 per-task progress authority。若某個資訊已需要這種細節，它就應留在 `{spec}/tasks.md`、reports、或 `NEXT_STEPS.md` 的高階 artifact link 中。

若專案同時存在 local dev / UAT / E2E 的 **local infra registry**（例如管理 ports、networks、compose stacks、TTL、env ownership 的 runtime registry），那是另一個治理系統。`spec-registry-manager` 不負責掃描、合併或同步該 runtime registry，也不得把 live allocation state 寫進 `SPECS.md`。

若 workspace `AGENTS.md` 保存 stable canonical project naming、aliases、或 required service bundle policy，這仍屬於 workspace operational guidance，不屬於 `SPECS.md` registry 範圍。`spec-registry-manager` 不負責把這些 workspace runtime guidance 轉抄進 `SPECS.md`。

若需要在 registry 中呈現 live-demo readiness 或 artifact honesty 相關訊號，`spec-registry-manager` **只能聚合既有 spec artifacts**（例如 `review.md`、reports、CR 摘要、project review evidence 摘要）中的已宣告欄位；在 review 之前，只能把 requirements / design / tasks 已知的風險整理成 **pre-review caution summary**。它**不可**自行掃描測試程式碼、不可根據 `page.route()` / fixture 字串去推論真相，也不可取代 `spec-driven-development` 的正式 review gate。

warning code 命名請與共用 taxonomy 對齊：`../../docs/DEMO_RISK_WARNING_TAXONOMY.md`。

### 步驟 1: 掃描既有目錄結構 (Shallow Scan)

**禁止一次性讀取所有文件的全文！** 這會導致嚴重的 Context 溢出。
使用 `Glob` 與 `ls` 等工具，進行淺層掃描：
- 列出 `.agents/specs/` 下的所有資料夾。
- 查看每個資料夾內有哪些檔案（`requirements.md`, `design.md`, `tasks.md`, `review.md`, `reports/`；若存在 `completed_tasks.md`，視為 legacy 補充訊號而非唯一依據）。
- 在 spec artifact discovery 中，**只把子資料夾視為候選 spec entries**。位於 `.agents/specs/` 根層的共享檔案（例如 `SPECS.md`、`NEXT_STEPS.md`）必須明確排除，不得視為 spec 識別依據。

### 步驟 2: 按需讀取依賴摘要與契約狀態 (Header & Contract Extract)

當你需要確認模組名稱、業務描述、相依關係（如 `[Impacts: xxx]` / `Depends On`）或契約時：
- **僅讀取檔案的前幾十行**。使用 `Read` 工具時，務必設定 `offset=1` 與 `limit=50`，以擷取 Frontmatter 或前言即可。
- 檢查該 Spec 是否宣告了 `contract/` 目錄的對應路徑。
- 盡可能從 `requirements.md` / `design.md` 的前段提取以下摘要欄位：
  - `Depends On`
  - `Impacts`
  - `Open Change Requests`（僅摘要 ID / label）
  - `Contract Authority`（`owned` | `shared-consumer` | `external`）
  - `Source of Truth`（若為 `external`）
  - `Pin/Version`（若為 `external`）
- 若存在 `review.md`，可額外從其摘要段落提取已宣告的 demo evidence posture：
  - `Live-Demo Readiness`（`PASS` | `CONDITIONAL` | `FAIL`）
  - `Coverage Tier`（`mock-heavy` | `hybrid` | `full-integration`）
  - `Evidence Source`（例如 `real-backend smoke`, `fixture-backed screenshots`, `static analysis only`）
  - `Demo-Critical Depends On`（若 review 有列出）
  - `Source Ref`（例如 `review.md#live-demo-readiness`）
- 這些欄位若不存在，應標示為 `not_assessed` 或略過，不可自行腦補。
- 若 workspace 已存在 `RTM.md`，可額外讀取其對應 spec / REQ 的 rollup 參照與 completeness 狀態，但不得讓 `RTM.md` 覆寫 spec-level truth，也不得把 RTM 中的 count / progress semantics 帶回 registry。
- 若 workspace 或 package-level 存在 `TESTS.md`，可額外讀取其 test catalog / evidence pointer / acceptance snapshot 摘要，但必須視 `TESTS.md` 中的 summary 欄位為 **derived convenience view**；真正的 verdict authority 若存在，仍應回到 `review.md`。
- 若 `review.md` 尚不存在，但 requirements / design / tasks 已明確記錄 false-green、over-state、mock-dominant、或 early real integration 未完成等風險，可額外提取成 **pre-review caution summary**；此摘要只能使用既有 warning codes 與保守語意（例如 `not_assessed`、`pre-review caution`），不得自行產生 readiness verdict。
- **(FMEA 契約防呆)**：如果在 Spec 中宣告了 Contract 路徑（例如指向 `contract/user.yaml`），你**必須**使用 `Glob` 或 `ls` 驗證該檔案是否真實存在。若不存在，必須在產出的註冊表中標記 `[⚠️ Broken Contract]`。
- 若 `Open Change Requests` 有摘要 ID，應再讀取對應 `.agents/specs/{linked-active-spec}/change-requests/{cr-id}.md` 的前段，確認至少存在 `Status`、`Target Baseline`、`Target Identifier`、`CR Relation`。
- **(治理防呆)**：若某個新 Spec 宣告 `[Impacts: completed-spec]`，但沒有對應的 `CR-ID` / `Open Change Requests` 摘要，必須在註冊表中標記 `[⚠️ Missing CR]`。
- **(外部契約防呆)**：若 `Contract Authority=external`，但缺 `Source of Truth` 或 `Pin/Version`，必須標記 `[⚠️ External Drift Risk]`。
- **(測試治理防呆)**：若存在 `TESTS.md`，必須區分其中哪些欄位是 `Authoritative Source`，哪些欄位是 `Derived Snapshot`。`SPECS.md` / `RTM.md` / `NEXT_STEPS.md` 的摘要欄位不得反向成為 `TESTS.md` 的生成輸入。

### 步驟 3: 狀態判定 (State Evaluation)

根據找到的文件存在情況，為每個 Spec 判定當前生命週期狀態：
- **[Draft] 草稿**：僅有 `requirements.md`。
- **[Design] 設計中**：包含 `design.md`，但尚未有任務規劃。
- **[In Progress] 開發中**：包含 `tasks.md` 且尚未全數完成。
- **[Completed] 已完成**：以 `tasks.md` 的完成狀態、`review.md`、以及 fresh reports / closure evidence 判定 repo-local lifecycle closure；若存在 `completed_tasks.md`，僅視為 legacy 補充訊號，不自動聲稱外部執行已完成。
- **[Completed-Handoff] 外部交接完成**：本地 repo-side 工作已完成，並已準備好外部執行交接包（如 arm64 驗證、CI 驗證）；此狀態描述的是 handoff package closure，不是 external execution 本身的完成宣告。
- **[External-Blocked] 外部阻塞**：剩餘工作真實存在，但無法在當前環境執行（如缺硬體、缺 secrets）。
- **[Retired] 已退役**：因合規、安全或政策原因，決定不實作此路徑。
- **[Historical-Skeleton] 歷史骨架**：僅保留規劃意圖的歷史骨架，非活躍工作。
- **[Superseded] 被取代**：歷史 groundwork 或舊 spec，已被新的 current spec / handoff spec 取代，不再是當前 execution lane。
- **[Retrofit] 漸進式逆向**：該模組是從舊程式碼反向推導提取出的 Contract，並受新標準保護。
- **[Legacy Core] 遺留系統**：在專案中實際存在，但尚未有完整 Spec 文件的黑箱系統。

**外部執行與 Handoff 治理 (External Execution Governance)**：

- 對於 `[Completed-Handoff]` 的 spec，註冊表摘要必須明確說明「completed as a remote handoff package」、「actual execution remains external」。
- 必須避免舊的 precursor specs (前置作業) 看起來像當前活躍的 spec。若有新的 handoff spec 取代了舊的 groundwork，必須將舊 spec 標記為 `[Superseded]`，並明確指出「superseded by <new-spec>」、「not the current execution lane」。
- 確保外部阻塞工作有唯一權威的 handoff path，不可讓多個舊 lanes 同時存在於文件中。

### 步驟 3.5: 治理警示判定 (Governance Warnings)

生命週期狀態與治理警示必須分開處理。對於 `[Completed]` spec，**不要**因為有 CR 或外部風險就改寫其歷史狀態；請額外標記治理警示：
- **[⚠️ Broken Contract]**：宣告了 local contract 路徑，但檔案不存在
- **[⚠️ Missing CR]**：有 `[Impacts: completed-spec]`，但沒有對應 CR 摘要
- **[⚠️ Open CR]**：該 spec 目前有尚未結案的 CR
- **[⚠️ Overlapping CRs]**：多個 open CR 指向同一個 `[Completed]` spec 或 shared contract
- **[⚠️ External Drift Risk]**：external contract 缺少 `Source of Truth` 或 `Pin/Version`
- **[⚠️ DEMO_NOT_ASSESSED]**：spec 被描述為 stakeholder-facing / demo-facing，但沒有任何已宣告的 `Live-Demo Readiness` 摘要
- **[⚠️ CROSS_SPEC_DEMO_DEPENDENCY]**：該 spec 依賴的 demo-critical upstream spec 目前 `Live-Demo Readiness != PASS`、存在 stale CR、或 evidence posture 不明
- **[⚠️ EVIDENCE_STALE_AFTER_CHANGE]**：spec 的 review / project-review evidence 明顯早於近期 relevant change / open CR，或 freshness evidence 已逾期
- **[⚠️ ARTIFACT_HONESTY_GAP]**：上游 review / project-review artifact 的對外 claim 與 evidence source 不一致，或已伴隨 `MOCK_DOMINANT_EVIDENCE` 仍被包裝成 ready
- **[⚠️ AMBIGUOUS_HANDOFF_LANE]**：historical / superseded / handoff lanes 仍以 current wording 並存，或 registry 摘要無法判斷唯一權威的外部執行路徑
- **[⚠️ POTENTIAL_FRAGMENTATION]**：多個 specs / CR / improvement lanes 指向相同 objective 或相同 repeated root cause，但沒有清楚 owner / relation
- **[⚠️ MISSING_ACTIVE_LANE]**：已知 improvement / repeated issue / open CR 存在，但 registry 無法指出唯一 active spec 或 `ISSUE_LOG.md` pointer
- **[⚠️ OPEN_CR_WITH_CLOSED_TEST_POSTURE]**：open CR 仍在，但上游 test summary 看起來像已 closure / fully fresh，缺少重新驗證證據
- **[⚠️ TEST_EVIDENCE_STALE_AFTER_CR]**：test evidence 明顯早於相關 open CR 或 baseline-touch 變更

若 `review.md` 尚未產生，registry 仍可揭露 requirements / design / tasks 已知的 warning codes，但必須加上 **Pre-Review Caution** 類型欄位或等價保守措辭，明確表明：這是治理摘要，不是 readiness verdict。

上述四個 warning code 與其他技能共享 taxonomy，但在 registry 中只作為**摘要與導引**，不取代原始 artifact 的細節說明。

### 步驟 4: 更新全局註冊表 (Update Registry)

將整理好的盤點結果，寫入到 `{workspace}/.agents/specs/SPECS.md`。

更新時必須遵守 **single snapshot pass**：

1. 一次讀取 upstream authority (`requirements.md`, `design.md`, `tasks.md`, `review.md`, test reports, `TESTS.md`)
2. 在記憶體內生成 derived summaries / warnings
3. 一次性寫回 `SPECS.md` 與（若需要）`RTM.md`
4. **禁止**讀回剛寫出的 `SPECS.md` / `RTM.md` 再次推導，直到「收斂」

這個 skill 必須把 `SPECS.md`、`RTM.md` 視為 **derived outputs**，而非新的 authority inputs。

### 步驟 4.5: Git / Worktree Hygiene

- registry 掃描、cross-spec diff、與 read-only compare 可使用 detached / read-only worktree；但 `SPECS.md` / `RTM.md` 的正式 writeback 只能由 **一條 authoritative writable lane** 執行。
- 若這次工作涉及大型 registry refresh、repo-owned governance wording 變更、或與其他 implementation / CR lanes 並行，預設建立 dedicated branch / worktree，而不是把 registry writeback 混進共用工作目錄。
- 若要重用既有 worktree，必須先確認該 branch/worktree 對應同一條 registry lane、狀態乾淨、且沒有其他 session 佔用。
- 不要把 machine-local worktree path、暫存草稿絕對路徑、或本機 runtime 狀態寫進 `SPECS.md` / `RTM.md` / `NEXT_STEPS.md`。需要操作規則時，優先回讀 `shared-governance` skill 的 `references/git-worktree-guide.md`、`references/git-worktree-templates.md`、`references/concurrent-writable-lanes.md`、`references/pre-write-conflict-checklist.md`、`references/ownership-evidence-template.md` 與 `references/cross-artifact-regeneration-order.md`。
- 若另一條 lane 已擁有 `SPECS.md` / `RTM.md` 的正式 writeback 權，當前 lane 必須停止 registry writeback，改成 detached compare / audit lane，輸出 reconcile note，而不是繼續 patch registry。
- 正式 writeback `SPECS.md` / `RTM.md` 前，必須先留下 ownership evidence；這份 record 應落在 invoking workspace（預設 `.agents/specs/governance/ownership-evidence/` 或對應 spec reports），並依 cross-artifact regeneration order 從 upstream authority 重新生成 summary，不得用舊 derived snapshot 修補另一個 derived artifact。
- 若需要 deterministic gate，應在正式 writeback 前執行 `shared-governance` skill 的 `scripts/validate_governance_writeback.py`，至少檢查 evidence file 是否位於 invoking workspace、欄位是否完整且非空、是否提供 `--expect-scope-token` 綁定當前 lane/scope、以及 upstream 方向是否違反 regeneration-order 規則。若 script 失敗，禁止正式 writeback，必須先修正 repo/workspace 內的 evidence 或 upstream 問題。

更新時必須同時執行輕量治理檢查：
1. 檢查每個 `[Impacts: ...]` 是否有對應 `Open Change Requests` 摘要
2. 檢查是否有多個 open CR 指向同一個 completed spec / shared contract
3. 檢查 external contract 是否具備 `Contract Authority`、`Source of Truth`、`Pin/Version`
4. 檢查 `Open Change Requests` 摘要是否對應到 canonical CR 檔案位置
5. 檢查 `Target Identifier` 是否符合 baseline 對應的標準格式
6. 檢查 `Closed` / `Superseded` 的 CR 是否已從 `Open Change Requests` 摘要移除，且 `Superseded` 是否指向替代 CR
7. 對 registry 採用 **deterministic ordering**（固定排序）與 **targeted entry update**（只改有變化的條目），避免每次重排整份文件造成 merge noise
8. 若某個 stakeholder-facing spec 的 `Demo-Critical Depends On` 指向的 upstream spec readiness 不是 `PASS`，則在當前 spec 標記 `[⚠️ CROSS_SPEC_DEMO_DEPENDENCY]`
9. 若 review/project-review 已標記 `MOCK_DOMINANT_EVIDENCE`、`ARTIFACT_HONESTY_GAP`、或 evidence source 為 `illustrative` / `fixture-backed`，但 spec 對外仍以 completed/ready 敘述呈現，則標記 `[⚠️ ARTIFACT_HONESTY_GAP]`
10. 若 `review.md` 缺少 live-demo posture，而 spec 又被 README / docs / guide 描述為 demo-facing，則標記 `[⚠️ DEMO_NOT_ASSESSED]`
11. 若 `[Completed-Handoff]` / `[External-Blocked]` / `[Superseded]` 條目之間仍同時保留多條像是 current 的 handoff / historical lane，或摘要無法指出唯一 authoritative handoff path，則標記 `[⚠️ AMBIGUOUS_HANDOFF_LANE]`
12. 若 requirements / design / tasks 已明確指出 demo-critical / high-risk journey 存在 early false-green、mock-dominant、或 over-state 風險，但尚未有 `review.md` verdict，則可在 registry 摘要中加入 `Pre-Review Caution` 與對應 warning codes；不得填入 `PASS` / `CONDITIONAL` / `FAIL`，除非該值明確來自 `review.md`
13. 若同一 objective / repeated root cause 同時出現在多個 specs、CR、或 improvement lanes，但 registry 內沒有清楚 relation / owner，則標記 `[⚠️ POTENTIAL_FRAGMENTATION]`
14. 若已知存在 repeated issue、open CR、或 promoted issue-log candidate，但 `SPECS.md` 無法指出 active lane 或 pointer，則標記 `[⚠️ MISSING_ACTIVE_LANE]`
15. 若 open CR 仍存在，但 test summary 或 evidence posture看起來像已 closure、且未見新鮮證據，則標記 `[⚠️ OPEN_CR_WITH_CLOSED_TEST_POSTURE]` 或 `[⚠️ TEST_EVIDENCE_STALE_AFTER_CR]`

更新 registry 時，**不得**將 `NEXT_STEPS.md` 內的 rolling operational fields 併入 `SPECS.md`，例如 `Current Phase`、`Next Action`、`Blockers`、`Resume Hint`、`Safe-to-Resume Checks`、或其他 session / handoff 狀態。這些資訊應維持在 `NEXT_STEPS.md`，不可污染 registry 的穩定治理語意。

同樣地，更新 registry 時不得從 `RTM.md` 抽取 task counters、execution ordering、或任何把 workspace rollup 變成 task dashboard 的欄位；若這類資訊存在，應視為超出 registry 的治理邊界。

同樣地，更新 registry 時不得讓 `SPECS.md` 與 `RTM.md` 互相糾正彼此的 snapshot 欄位。若 `SPECS.md`、`RTM.md` 與 `TESTS.md` / `review.md` 的欄位衝突，必須返回 upstream authority 重新生成，而不是 derived-to-derived sync。

必須採用 **[安全文件更新守則](./references/safe-update-protocol.md)** 來編輯檔案：
1. **生成草稿**：寫入臨時檔案（如 `temp/SPECS_draft.md`）。
2. **審查與比對**：確認草稿內容無截斷。
3. **覆寫原檔**：將草稿移至目標路徑。
4. **清理**：刪除草稿檔案。

## SPECS.md 格式要求

產出的 `SPECS.md` 是**全局索引 (Index)**。你必須在文件開頭加上 **Lazy Loading (漸進式載入)** 警告標語，指導未來閱讀此檔案的 Agent 不應盲目載入所有內容。

```markdown
# 專案全局規格註冊表 (Feature Registry)

本文件自動追蹤並維護專案中所有的功能規格 (Specs) 與其相依關係。

> 🛑 **Context 管理警告 (Lazy Loading)**：
> 開發新功能時，請先查閱這份清單（地圖）。找到相關的 Themes / Features 後，**才去具體讀取該目錄下的設計文件**。絕對不要盲目使用 grep 讀取所有 `requirements.md` 的全文，避免 Context 溢出。

## 狀態圖例
- 🟢 `[Completed]` - repo-local spec lifecycle 已完成；不單獨聲稱外部執行也已完成
- 🟢 `[Completed-Handoff]` - 本地 repo-side 工作已完成，且 repo 已完成外部交接包；actual execution 仍屬 external lane
- 🟡 `[In Progress]` - 正在實作階段
- 🔵 `[Design]` - 正在架構設計階段
- ⚪ `[Draft]` - 需求盤點階段
- 🟣 `[Retrofit]` - 從舊系統提取的 Contract
- 🟤 `[Legacy Core]` - 尚未導入 Contract-First 的遺留系統
- 🔴 `[External-Blocked]` - 外部阻塞，無法在當前環境執行
- ⚪ `[Retired]` - 已退役，不實作此路徑
- ⚪ `[Historical-Skeleton]` - 歷史骨架，非活躍工作
- ⚪ `[Superseded]` - 被新的 handoff spec 取代

## 治理警示圖例
- 🔴 `[⚠️ Broken Contract]` - Spec 宣告了 Contract 但檔案不存在 (需優先修復)
- 🟠 `[⚠️ Missing CR]` - 影響 completed spec，但尚未建立對應的 CR 摘要
- 🟧 `[⚠️ Open CR]` - 該 spec 目前存在未結案的 CR
- 🟥 `[⚠️ Overlapping CRs]` - 多個 open CR 指向相同 completed spec / shared contract
- 🟨 `[⚠️ External Drift Risk]` - external contract 缺少 `Source of Truth` 或 `Pin/Version`
- 🟪 `[⚠️ DEMO_NOT_ASSESSED]` - stakeholder-facing spec 尚未留下 live-demo readiness 摘要
- 🟫 `[⚠️ CROSS_SPEC_DEMO_DEPENDENCY]` - demo-critical upstream spec 尚未 `PASS`
- 🟦 `[⚠️ EVIDENCE_STALE_AFTER_CHANGE]` - demo / review evidence 已落後於近期 relevant change
- ⬛ `[⚠️ ARTIFACT_HONESTY_GAP]` - evidence source 與對外 claim 不一致，或已存在 `MOCK_DOMINANT_EVIDENCE` 仍被過度包裝
- 🟥 `[⚠️ AMBIGUOUS_HANDOFF_LANE]` - current / historical / handoff lane 邊界不清，無法判斷唯一權威路徑

## 模組清單 (Feature Sets / Themes)

### 1. [模組名稱] (例如: user-authentication)
- **狀態**: 🟢 `[Completed]`
- **規格路徑**: `.agents/specs/user-authentication/` (需了解細節時請查閱此目錄下的文件)
- **契約 (Contract)**: `contract/openapi.json#/components/schemas/User`
- **Depends On**: `shared-session-contract`, `gac-oauth`
- **Demo-Critical Depends On**: `gac-oauth`, `shared-session-contract`
- **相依與影響 (Impacts)**: 影響了 `email-notification` 模組
- **Contract Authority**: `external`
- **Source of Truth**: `https://apidog.example.com/gac/session` (僅 `external` 時必填)
- **Pin/Version**: `2026-04-01` (僅 `external` 時必填)
- **Open Change Requests**: `CR-2026-004`, `CR-2026-009` (摘要即可，不寫完整敘述)
- **Pre-Review Caution**: `Known early integration risk in login + dashboard journeys; summary only, not a readiness verdict`
- **Pre-Review Warning Codes**: `MOCK_DOMINANT_EVIDENCE`, `DEMO_NOT_ASSESSED`
- **Live-Demo Readiness**: `CONDITIONAL`
- **Coverage Tier**: `hybrid`
- **Evidence Source**: `review.md + project-review evidence`
- **Source Ref**: `.agents/specs/user-authentication/review.md#live-demo-readiness`
- **治理警示**: `[⚠️ Open CR]`, `[⚠️ CROSS_SPEC_DEMO_DEPENDENCY]`
- **簡述**: 處理使用者的登入、註冊與 JWT Token 發放。

> 若 `review.md` 尚未產生，應只保留 `Pre-Review Caution` / `Pre-Review Warning Codes` 等 summary-only 欄位，並將 readiness 相關欄位維持缺省或 `not_assessed`；不得由 registry 自行補出 `PASS` / `CONDITIONAL` / `FAIL`。

### 2. [模組名稱]
...
```

## 注意事項

- 當遇到極度龐大的專案，請分批次進行分析，避免超過 Context Window。
- 對於尚未建立文件但明顯存在於 `src/` 或 `app/` 中的核心服務，主動將其列入 `[Legacy Core]`，方便未來 `spec-driven-development` 在開發時進行 Retrofit (漸進式逆向工程)。
- `Open Change Requests` 只放摘要，不要把完整 CR 內容塞進 `SPECS.md`。
- 不要為 `NEXT_STEPS.md` 建立 registry entry，也不要把此 skill 擴張成 resume / handoff orchestration；它只負責 registry 掃描與治理更新。
- 不要讓 `RTM.md` 或 `SPECS.md` 承擔 task-counter、execution ordering、或 per-task progress summary；這類細節若需要存在，只能回到 `{spec}/tasks.md`、reports、或由 `NEXT_STEPS.md` 以高階 artifact 指引方式引用。
- 不要把 local runtime allocation state（例如 ports、networks、containers、env locks）寫進 `SPECS.md`；那屬於 local infra registry，不屬於 feature governance registry。
- 不要把 worktree path、machine-local compare 目錄、或 detached audit lane 的暫時資訊寫進 registry artifact；這些資訊只屬於執行表面。
- `Live-Demo Readiness` 與 `Coverage Tier` 是 review / artifact 的**摘要欄位**，不是 registry 自行推論出來的 runtime truth。
- `Pre-Review Caution` / `Pre-Review Warning Codes` 若存在，只能表示在 requirements / design / tasks 已知風險，不能被閱讀成 readiness verdict，也不能覆寫後續 `review.md` 的正式結論。
- registry 可以摘要 handoff / external execution posture，但 canonical lifecycle distinction 仍來自 spec-level `requirements.md` / `design.md` / `review.md` 與其對應 closure artifacts。
- 若需要撰寫完整 CR，請使用 [輕量 CR template](./references/change-request-template.md) 作為最小欄位基準，並存放於 `.agents/specs/{linked-active-spec}/change-requests/{cr-id}.md`。
- `Depends On` 與 `Impacts` 不可混用：前者是上游依賴，後者是此 spec 對其他 spec / contract 的變更影響。
- `Contract Authority=external` 描述的是上游權威來源；它不會推翻本專案 `contract/` 作為本地實作 SSOT 的原則。
