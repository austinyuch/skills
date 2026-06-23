## Conflict Evidence Review Checklist

這份 checklist 給 review / closeout 使用，用來判斷：當工作曾遇到 concurrent writable lane 風險時，是否真的有完成治理，而不是只是「最後看起來沒壞」。

## Minimum Review Evidence

### 1. Lane identity evidence

- 是否明確說出這條 lane 的 branch identity 與 lane role
- 是否有 ownership evidence，且可對應到本次 writeback scope
- ownership evidence 是否存在於 invoking repo/workspace 內，而不是 global skills 目錄或僅存在對話中

### 2. Worktree state evidence

- 是否至少有一次 `git worktree list --porcelain` 的檢查結果被納入證據或摘要
- 是否說明當時 branch 是否已被其他 writable worktree 佔用
- 若重用既有 worktree，是否說明它是乾淨的，或未提交內容確實屬於本 lane

### 3. Conflict resolution evidence

- 若另一條 lane 已存在，是否有明確 downgrade to `audit-only`
- 若 upstream authority 已變，是否停止 incremental patch 並重讀 upstream
- 若雙方都聲稱自己 authoritative，是否有 owner / scope / latest-fact resolution，而不是直接繼續寫

### 4. Writeback safety evidence

- 是否明確說明只有一條 authoritative writable lane 做正式 writeback
- 是否避免 derived-to-derived sync
- 是否遵守 cross-artifact regeneration order

### 5. Artifact hygiene evidence

- 是否避免把 machine-local path、detached compare 目錄、暫時草稿路徑、ports、containers、env locks 寫進治理 artifact

### 6. Cleanup / stale-state evidence

- 若使用暫時 writable worktree，是否說明 closeout / remove / prune 計畫
- 是否避免留下 dual-state wording（例如同時看起來像 completed handoff 又像仍在本地繼續執行）

### 7. Record traceability

- reviewer 是否能從 repo/workspace 內的 artifact 直接找到 ownership evidence / conflict note
- 若工作屬於 workspace 級治理 lane，是否使用 `.agents/specs/governance/...` 之類的 workspace surface，而不是把 record 留在 global skill 安裝路徑

## Review Verdict Guidance

- 若缺 ownership evidence，review 不應直接視為治理已完成
- 若缺 downgrade/reconcile evidence，只能保守降級為 `CONDITIONAL`
- 若已知存在 competing writable lane 卻仍直接 patch authoritative artifact，應視為 blocking governance flaw
