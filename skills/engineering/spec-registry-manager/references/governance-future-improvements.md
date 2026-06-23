# Governance Future Improvements Memo

本備忘錄記錄本輪 spec governance 調整後，仍值得未來持續改進的方向。

## 為什麼保留這份 memo

目前已補上：CR overlay、external contract provenance、impact triage、re-sync freshness evidence、closure rules。

以下項目暫時刻意不做重流程化，但若未來協作規模變大，這些會是高價值補強點。

## Deferred Improvements

1. **Depends On / CR decision table**
   - 目前已用文字規範區分 `Depends On only`、`Impacts completed/shared baseline`、`External contract assumption impact`。
   - 未來可補一個一頁式 decision table，讓新 agent 更快判斷何時應開 CR。

2. **End-to-end worked example**
   - 目前已有 CR template，但還沒有完整示範：
     `SPECS.md` 摘要 → active spec → `change-requests/{cr-id}.md` → 關閉 / supersede。
   - 若首次實戰使用時出現理解落差，優先補這個範例。

3. **Stale threshold for Re-sync Freshness Evidence**
   - 目前要求留下 freshness evidence，但尚未定義多久算 stale。
   - 若 external contract 變動頻繁，應補一條簡單規則，例如依 source 類型定義有效期限或重查時機。

4. **Overlap resolution policy**
   - 目前已能標示 overlapping CR，但尚未定義輕量處置策略。
   - 未來可補最小規範：`compatible with`、`blocked by`、`supersedes` 的使用時機。

5. **Automation backlog**
   - 若未來多人並行協作更頻繁，可考慮增加輕量自動檢查：
     - `[Impacts]` 但缺 `Open Change Requests`
     - open CR 沒有 canonical file
     - external contract 缺 `Source of Truth` / `Pin/Version`
     - stale `Re-sync Freshness Evidence`

## Revisit Triggers

- 同一個 completed spec 經常被多個 CR 同時影響
- external contract 經常發生 drift
- 使用者或 agent 常分不清 `Depends On` 與 `Impacts`
- open CR 長期不關閉，造成 `SPECS.md` 噪音累積

## Keep Out

- 不要把完整 CR 內容塞回 `SPECS.md`
- 不要把 branch-state / merge-state 放進 registry
- 不要引入 approval-heavy workflow，除非現有 lightweight controls 已明顯失效
