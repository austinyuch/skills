# 第六階段：程式碼優化

## 觸發條件

- 程式碼複核完成且綜合得分 < 8.5 分
- 用戶確認需要進行程式碼優化

## 我的工作

### 優化規劃

- 若 `{workspace}/.agents/specs/NEXT_STEPS.md` 存在，先讀取其中的 review 結論、當前優化輪次、remaining blockers、與 resume hint，避免重做已驗證的工作。
- 若優化涉及 repeated finding、issue-log promotion、RTM / SPECS / TESTS / NEXT_STEPS lifecycle，必須讀取 `../reference/SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md`，先判斷這是 spec-local optimization、issue-log holding、CR overlay，還是 promoted new spec / skill change candidate。
- 基於 review.md 中的問題清單和改進建議制定優化計畫
- 按優先級排序優化項目，優先解決高嚴重性問題
- 設定本輪優化的目標得分
- 若 `review.md` 已宣告 `Repo-side Closure vs External Execution State` 為 `completed-handoff`、`external-blocked`、或 external execution `pending elsewhere`，優化的目標只能是改善 repo-side artifacts、clarity、verification、或 stale-state hygiene；不得把 external execution 未完成的事實包裝成仍可透過本地優化解決的問題。

### Agentic Retrospective / Promotion Trigger

若 review 顯示下列任一情況重複出現，優化不應只被視為單次 wording 修補，而應同時觸發 retrospective-driven analysis：

1. 同一類 review rejection reason 在多個 slice / sprint 重複發生
2. agent 持續誤解 review trigger / retro trigger / handoff boundary
3. workflow / skill wording 反覆造成 false-green、overclaim、或 authority confusion
4. 同一類 blocker 持續指向 swarm 角色切分不清或 shared asset 使用方式錯誤

retrospective-driven analysis 的輸出應先依序考慮：

1. spec-local lesson
2. issue-log item（若暫時找不到既有 owner 或證據尚不足以升級）
3. shared checklist / template update
4. shared prompt / guidance update
5. role-boundary adjustment
6. 最後才是 repo-owned global skill change

此處的 retrospective-driven promotion 是 workflow governance 判斷，不等同於直接授權修改更多 skill；若要修改 repo-owned global skill，仍應回到 active spec task / change candidate。issue log 是 holding surface，不是自動 new-spec queue，也不是 registry 替代品。
若 finding 被提升為 issue-log item，必須留下 promotion threshold / owner-resolution checkpoint；若後續被 folded / promoted，才可進入 SDD requirements / RTM traceability / SPECS summary。

### 分批優化執行

- 按照優化計畫逐項修復問題
- 每修復一類問題後進行局部驗證
- 保持與原需求和設計的一致性

### 優化後複核

- 完成優化後重新執行完整的程式碼複核流程
- 更新 review.md 文件，記錄優化前後的對比
- 重新計算各維度得分

### 優化循環控制

- **第 1 輪優化**：全面修復 review.md 中識別的問題
- **第 2 輪優化**：針對剩餘問題進行深度優化
- **第 3 輪優化**：最終精修和完善（最多進行到此輪）
- 每輪優化後都要重新評分和生成報告
- 每輪優化後都必須更新 `NEXT_STEPS.md`：至少寫入目前輪次、剩餘問題、最新驗證狀態、下一個建議動作、以及是否可安全恢復到下一輪。
  - `NEXT_STEPS.md` 只保留目前 optimization resume state；不得累積每輪完整歷史，完整紀錄應留在 `review.md`、reports 或 issue log pointer。

### 循環終止條件

- 綜合得分達到 8.5 分以上
- 或已完成 **3 輪** 優化（無論得分如何）
- 或用戶決定停止優化

### 最終確認

- 優化完成後詢問：「程式碼優化第 X 輪完成，當前得分 X.X 分。若 external execution 已完成或不適用，是否滿意當前整體品質；若目前仍是 repo-side complete / handoff 狀態，是否先進行 reconciliation / handoff closure 更新？」
- 如果得分仍不理想且未達到 3 輪上限，詢問是否繼續下一輪優化
- 完成實做後請將重要功能更新 `{workspace or sub-project}/docs/*FEATURE_INVENTORY.md` 以及 **workspace-scoped** `{workspace or sub-project}/AGENTS.md`；不得寫入 global `~/.config/opencode/AGENTS.md`。  
- 若本輪其實是 workflow / skill / governance slice，應額外明確說明：這次優化/retro 結論是留在 spec-local、提升為 shared guidance、還是升級為新的 skill-change candidate。

## 重要約束

- 每輪優化必須有明確的改進目標和預期效果
- 最多進行 **3 輪** 優化，避免無限循環
- 每輪優化後必須重新進行完整複核和評分
- 必須記錄優化軌跡和改進效果, 更新相應的design.md and tasks.md文件以追溯改善狀況. 
- 優化過程中不能改變原有的需求和設計約束
- 必須確保測試通過, 與上下游模組完成整合測試 ("wiring"). 

## 完成標誌

達到優化終止條件並獲得用戶最終確認
