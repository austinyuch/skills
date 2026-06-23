# 第一階段：需求明確

## 觸發條件

- 您提出新的功能想法
- 或明確表示要梳理需求
- 或相關目錄不存在任何文件

## 我的工作

1. **(新增) 讀取全局規格地圖 (Lazy Loading Context)**：
   - 必須先呼叫 `task(subagent_type="explore", load_skills=["spec-registry-manager"])` 來掃描並讀取 `{workspace}/.agents/specs/SPECS.md`。
   - 若本次工作涉及 `ISSUE_LOG.md`、`NEXT_STEPS.md`、`RTM.md`、`TESTS.md` 或 governance artifact lifecycle，必須先讀 `../reference/SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md`，再判斷要開新 spec、續做、CR、fold-back，或留在 issue log。
   - **禁止盲目展開**：根據 `SPECS.md` 這張地圖，判斷新需求可能相依哪些特定的模組目錄，**只有確定相依時**，才去 Read 該特定模組的詳細文件（`requirements.md`, `design.md` 等），避免一次載入所有規格導致 Context 溢出。
   - **如果找不到 `SPECS.md`**：讓 `spec-registry-manager` 協助初始化此檔案，將舊有系統暫時歸類於 `[Legacy Core]`，不需強制一次性盤點所有舊功能。
    - **(新增) 需求分類**：讀完 `SPECS.md` 後，先判斷本次工作屬於 `continue active spec`、`new spec`、`retrofit`、`CR against completed spec`，或 `issue-log candidate`，避免把不同治理情境混成同一條流程。
    - 若請求屬於 review rejection、retro finding、known issue、tech debt、test gap、或 CR follow-up，先做 identity resolution：active spec → completed baseline CR → spec-local lesson / optimization follow-up → issue log → 最後才是 `new spec`。
    - 若既有 `ISSUE_LOG.md` row 被判定可承接，必須先決定 disposition：`Folded`、`Promoted`、`Closed`、`Dropped`、或仍保留 holding。只有 `Promoted` 或 `Folded` 且已進入正式 SDD/CR lane 的項目，才可成為 `requirements.md` 的 authoring input。
2. **(新增) 讀取或建立 `{workspace}/.agents/specs/NEXT_STEPS.md`**：
    - 若檔案已存在，提取其中的 active spec、open CR IDs、blockers、resume hint，與 `SPECS.md` 互相比對，不可只信任其中任一方。
    - 若檔案不存在，依 `../reference/NEXT_STEPS_TEMPLATE.md` 建立最小骨架。
    - 在 requirements 階段，只寫入高層摘要：本次工作分類、候選 impacted specs / contracts、下一個 approval / design 入口，以及對應 artifact 路徑。
    - 不要在此階段把 `NEXT_STEPS.md` 寫成 task checklist、execution ordering、或 per-task progress 紀錄；詳細內容應留在 `{spec-directory}/tasks.md` 或 reports。
3. 調整到 ultrawork 模式，完全了解專案程式碼，收集足夠完整的上下文再開始工作。
4. 若分類結果是 `new spec`，創建 `.agents/specs/{功能名}/requirements.md` 文件（功能名應使用 kebab-case 的英文）。若分類結果是 `continue active spec` 或 `CR against completed spec`，則更新既有 active spec；若結果是 `issue-log candidate`，則先將 issue 交由 `issue-log-manager` 維護，而不是直接開新 spec 目錄。若 workspace 採用 canonical issue-log surface，預設路徑為 `{workspace}/.agents/specs/ISSUE_LOG.md`。
   - `ISSUE_LOG.md` row 不可直接複製成 requirement；必須先完成 owner resolution，並在 row 中留下 folded / promoted pointer。
4.1 **(新增) Ponytail Rung 1 需求過濾**：在撰寫每個需求前，必須先執行 **Rung 1** 思考並展示：「Does this need to exist?」
   - 這個功能、模組、API endpoint、資料表、或設定項目，是否真的有已確認的需求支撐？
   - 是否只是「以後可能會用到」或「看起來應該要有」？
   - 若答案為 no，**直接標記為 `deferred` 或 `out-of-scope`**，不進入 design。
   - 展示方式：在 `requirements.md` 的「介紹」或每個需求段落，簡短說明為何這些需求是必要的（例如引用 stakeholder request、bug report、或業務指標）。
   - 參考：[`references/ponytail-yagni-ladder.md`](../references/ponytail-yagni-ladder.md)
5. **(新增) 唯一需求 ID (REQ-ID)**：為每個需求編列唯一的識別碼（如 `REQ-AUTH-001`）。
5.1 **(新增) Source of Truth 邊界**：`requirements.md` 是 requirement source of truth；即使 workspace 存在 `RTM.md`，也不得在此階段把 RTM 當成需求的 authoring 來源。
 5.2 **(新增) Branch-spec 執行邊界宣告**：若本次工作涉及另一台機器、CI runner、registry、雲端帳號、硬體特定環境、或任何 external execution，必須在 `requirements.md` 先明確寫出：哪些屬於 repo-local closure、哪些屬於 external execution、以及哪些只是 external blocker。這個區分必須先在 branch-spec artifact 建立，不能等 `tasks.md` 才補。
6. **(新增) 規格漂移宣告**：若此需求修改了舊有 Specs 的邏輯，必須在文件中明確宣告 `[Impacts: {舊spec名稱}]`。
7. **(新增) CR Intake Gate**：若需求影響 `[Completed]` spec、shared contract 或 external contract 假設，必須先在當前 active spec 中建立 / 更新 `Open Change Requests` 摘要，再進入 requirements approval。完整欄位請參考 [輕量 CR template](spec-registry-manager skill 的 references/change-request-template.md)。
   - **Impact Triage**：先將每個變更分類為：`Depends On only`、`Impacts completed/shared baseline`、`External contract assumption impact`。
   - 只有後兩者需要開 CR；單純 `Depends On` 不應濫開 CR。
   - 若需要開 CR，完整內容固定放在 `.agents/specs/{linked-active-spec}/change-requests/{cr-id}.md`，且 `Target Identifier` 必須使用標準格式。
   - 若同時影響多個 immutable baseline，應拆成多個 CR，而不是把多個 target 混在同一份自由文字裡。
7.5 **(新增) 深度需求訪談 (Value Lens + Grilling)**：預設啟動、可隨時跳過。完整方法論見 [`references/requirement-interview-depth.md`](../references/requirement-interview-depth.md)。
   - **生成草稿前**：先用 **CEO 高階價值視角** 快速掃描，挑出 1–2 個最有張力的前提問題逐一詢問（如：這是對的問題嗎？真正的使用者/業務結果是什麼？不做會怎樣？）。這是高層價值確認，不是一次丟一串問題。
   - **生成草稿後**：針對草稿的具體缺口，沿決策樹**逐題追問 (grilling)**——一次只問一題、每題附上建議答案、能從 codebase 查到的先查不問，直到分支收斂或使用者喊停。
   - 訪談結論必須落地：確認的需求寫入 `requirements.md`、被砍/延後的標記 `deferred`/`out-of-scope` 並附理由（呼應 Rung 1 與 Focus as Subtraction）。
8. 基於您的描述生成初始需求。**不會一口氣丟一串問題 (barrage)**；高層前提確認與草稿後的 grilling 都採「逐題詢問、每題附建議答案」的方式進行（詳見步驟 7.5）。
9. 採用 EARS 格式（Easy Approach to Requirements Syntax）與用戶故事格式編寫：

```markdown
# 需求文件

## 介紹

[功能介紹文本]

## 相依、影響與變更請求 (Dependencies, Impacts & CRs)

- [Depends On: shared-session-contract, gac-oauth]
- [Impacts: old-spec-name] (如果有影響舊有邏輯)
- [Open Change Requests: CR-2026-004] (若影響 completed spec / shared contract / external contract)

> 完整 CR 內容應依 [輕量 CR template](spec-registry-manager skill 的 references/change-request-template.md) 撰寫；本處只保留摘要引用。

## Repo-side Closure vs External Execution

- **Repo-side Closure**: [在此列出 branch-spec 內可於目前 repo / 工作站完成的內容]
- **External Execution**: [在此列出必須於外部環境執行的內容]
- **External Blockers / Constraints**: [在此列出外部限制；若無可省略]

## 需求

### 需求 1 [REQ-FEAT-001]

**用戶故事：** 作為一個[角色]，我希望[功能]，以便[收益]

#### 驗收標準

本節應包含 EARS 格式的需求

1. 當[事件]時，那麼[系統]應該[響應]
2. 如果[前置條件]，那麼[系統]應該[響應]
```

9.1 **(新增) 驗收標準 Canonical Format（Machine-Parseable AC）**：
   - **Header**：必須使用四級標題 `#### 驗收標準` 或 `#### Acceptance Criteria`。
   - **AC 項目**：必須使用編號列表（`1.` `2.` `3.`），不得使用 dash 列表（`-`）。
   - **建議格式**：每個 AC 項目建議採用 EARS 格式（When/If/While），但不強制。
   - **禁止格式**：不得使用 bold inline header（如 `**驗收標準**:`）或無序列表作為 AC 容器。
   - 💡 **原因 (WHY)**：統一格式使 AC parser 能 100% 可靠提取新 spec 的驗收標準。Legacy specs 仍以 best-effort heuristic 處理，不需立即 migrate。
   - 詳細格式定義與 legacy 對照表請參閱 `../reference/AC_FORMAT_GUIDE.md`。

10. 考慮邊緣情況、用戶體驗、技術約束和成功標準。
11. 與您反覆討論直到需求清晰。
12. 在請求 requirements approval 前，更新 `NEXT_STEPS.md`：至少包含 active spec、工作分類、候選 impacted specs / contracts、open CR IDs（若有）、以及進入 design 的下一步。
    - `NEXT_STEPS.md` 應保持高階、簡短、可追溯到 `{spec-directory}/tasks.md` 或 reports；不要複製 requirements 細節或預先展開 tasks 層級內容。
    - 若本次從 `ISSUE_LOG.md` promoted / folded 而來，`NEXT_STEPS.md` 只記錄 owner / pointer / 下一步；不要複製 issue row 內容，也不要把它當歷史日誌。
13. 自然地詢問：「需求看起來完整了嗎？如果沒問題，我們可以開始架構設計了。」

## 重要約束

- 必須等待您的明確認可才能進入下一階段。
- 如果您提供反饋，我必須修改並再次請求確認。
- 必須持續「反饋－修訂」循環直到獲得明確批准。
- 不會假設用戶偏好或需求——總是明確詢問。
- 若本次工作屬於 `CR against completed spec`，不得以 requirements 階段的輸出覆寫舊 spec；必須以當前 active spec 的 CR 摘要承接變更。

## 完成標誌

您明確表示滿意當前需求（如「是的」、「批准」、「看起來不錯」等）
並且已委託 `spec-registry-manager` 確認/更新 `SPECS.md` 中關於此新 spec 的條目。
