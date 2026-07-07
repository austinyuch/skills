## Compatibility Pointer: Git Branch / Worktree Guide

這份檔案保留為 **backward-compatible shim**。

canonical shared location 已移至：

- `shared-governance` skill 的 `references/git-worktree-guide.md`

若需要 branch namespace、layout、命令片段與 handoff checklist，請再讀：

- `shared-governance` skill 的 `references/git-worktree-templates.md`
- `shared-governance` skill 的 `references/concurrent-writable-lanes.md`
- `shared-governance` skill 的 `references/pre-write-conflict-checklist.md`
- `shared-governance` skill 的 `references/ownership-evidence-template.md`
- `shared-governance` skill 的 `references/conflict-evidence-review-checklist.md`
- `shared-governance` skill 的 `references/cross-artifact-regeneration-order.md`

最小不變式仍是：**一條 lane = 一個 branch = 一個 writable worktree；同一份 authoritative artifact 同時間只能有一條 authoritative writable lane。**

詳細內容請讀 canonical shared references，不要在這份 shim 上繼續擴寫。
