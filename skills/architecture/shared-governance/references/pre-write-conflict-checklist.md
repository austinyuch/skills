## Pre-Write Conflict Checklist

在任何 lane 準備寫入 authoritative artifact 前，先跑完這份 checklist。

### A. Lane identity

- 我現在是哪一條 lane？
- 這條 lane 的 branch identity 是否清楚？
- 這條 lane 是 writable 還是 audit-only？

### B. Worktree hygiene

- `git worktree list --porcelain` 是否顯示這個 branch 已被其他 writable worktree 使用？
- 當前 worktree 是否乾淨？
- 若不乾淨，未提交內容是否確實屬於本 lane？
- 這是不是 detached audit lane？如果是，它是否被錯誤地拿來做正式 writeback？

### C. Artifact ownership

- 這份 artifact 的 upstream authority 是什麼？
- 是否已存在另一條 lane 明確擁有這份 artifact 的正式 writeback 權？
- 若存在，我是否應立刻降級為 audit-only？

### D. Freshness and drift

- 我是否已重讀最新 upstream authority？
- 是否有 open CR、recent baseline-touch、或新的使用者事實讓舊 snapshot 失效？
- 若發現 drift，是否已停止 incremental patch，準備重新生成？

### E. Writeback safety

- 這次更新是否會造成 derived-to-derived sync？
- 是否只會有一條 authoritative writable lane 執行正式 writeback？
- 若發生衝突，我是否已知道應該留下 reconcile note 而不是硬寫？

### F. Artifact hygiene

- 我要寫入的內容是否包含 machine-local path、detached compare 目錄、暫時草稿絕對路徑、ports、containers、env locks 等不該進 artifact 的資訊？

### G. Ownership evidence capture

- 若本次準備正式 writeback，是否已依 `ownership-evidence-template.md` 補齊最小 ownership evidence？
- 這份 ownership evidence 是否已準備寫入 invoking repo/workspace 內的 canonical location，而不是 global skills 路徑？

若任一題答案不安全，先停止正式 writeback，回到 `concurrent-writable-lanes.md` 重新判斷。

若要做 deterministic gate，可執行：

```bash
python ~/.config/opencode/skills/shared-governance/scripts/validate_governance_writeback.py \
  --workspace <invoking-workspace> \
  --target-surface <folder-tests|workspace-tests|specs|rtm|shared-governance> \
  --evidence-file <repo-local-evidence-file> \
  --expect-scope-token <lane-or-artifact-scope-token> \
  --upstream <path> --upstream <path>
```

若這個 script 回傳失敗，**禁止**進行 governance writeback；必須先修正 invoking workspace 內的 evidence / upstream 問題，再重跑。

script 也會輸出 deterministic upstream classifications，幫助判斷為什麼這次 writeback 被擋下。
