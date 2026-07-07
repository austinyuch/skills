# 安全更新守則 (Safe Document Update Protocol)

在修改任何長規格文件（如 `SPECS.md` 等）之前，為避免上下文過長導致文件被 LLM 改壞或截斷，必須遵循以下 4 個強制步驟：

1. **生成草稿 (Drafting)**：將修改或新增的完整內容寫入臨時檔案（例如 `temp/SPECS_draft.md`），而非直接編輯原檔。
2. **審查與比對 (Review)**：讀取草稿並確認內容完整，沒有出現「...[省略]...」等偷懶截斷現象。
3. **合併 (Merge)**：若確認無誤，將草稿覆寫回原檔（更新），或使用 Append 方式合併至原檔底部（新增任務）。
4. **清理與提交 (Clean & Commit)**：合併完成後刪除臨時草稿，並執行 `git commit`。

這能避開 Edit 工具在長文件上的風險，並在正式破壞原檔之前提供自行審查的保險機制。

額外治理原則：
- 對於 `[Completed]` spec（即 repo-local lifecycle 已關閉的穩定基線），不要以 destructive rewrite 的方式改寫歷史基線；治理上的變更（例如 open CR、外部相依、影響摘要）應優先以 append / overlay / 當前 active spec 的方式記錄。
- 更新 `SPECS.md` 時，優先做 targeted entry update 與 deterministic ordering，避免因整份重排而引入不必要的 merge noise。
