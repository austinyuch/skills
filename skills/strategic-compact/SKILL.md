---
name: strategic-compact
description: Suggests manual context compaction at logical intervals to preserve context through task phases rather than arbitrary auto-compaction.
---

# Strategic Compact Skill

Suggests manual `/compact` at strategic points in your workflow rather than relying on arbitrary auto-compaction.

## 適用場景

- 執行接近 context 上限的長時間 session（200K+ tokens）
- 處理多階段任務（研究 → 規劃 → 實作 → 測試）
- 在同一 session 中切換不相關的任務
- 完成重大里程碑並開始新工作後
- 回應速度變慢或品質下降時（context 壓力訊號）

## Why Strategic Compaction?

Auto-compaction triggers at arbitrary points:

- Often mid-task, losing important context
- No awareness of logical task boundaries
- Can interrupt complex multi-step operations

Strategic compaction at logical boundaries:

- **After exploration, before execution** - Compact research context, keep implementation plan
- **After completing a milestone** - Fresh start for next phase
- **Before major context shifts** - Clear exploration context before different task

## How It Works

The `suggest-compact.sh` script runs on PreToolUse (Edit/Write) and:

1. **Tracks tool calls** - Counts tool invocations in session
2. **Threshold detection** - Suggests at configurable threshold (default: 50 calls)
3. **Periodic reminders** - Reminds every 25 calls after threshold

## Hook Setup

Move script to opencode ~/.config/opencode/plugins/strategic-compact.ts

OR Add to your `~/.config/opencode/settings.json` :

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "tool == \"Edit\" || tool == \"Write\"",
        "hooks": [
          {
            "type": "command",
            "command": "~/.config/opencode/skills/strategic-compact/suggest-compact.sh"
          }
        ]
      }
    ]
  }
}
```

## Configuration

Environment variables:

- `COMPACT_THRESHOLD` - Tool calls before first suggestion (default: 50)

## Compaction Decision Guide

Use this table to decide when to compact:

| 階段轉換 | 是否壓縮？ | 原因 |
|---------|-----------|------|
| Research → Planning | 是 | 研究 context 龐大；規劃結果才是精華輸出 |
| Planning → Implementation | 是 | 規劃已存在 TodoWrite 或檔案中；釋放 context 給程式碼 |
| Implementation → Testing | 也許 | 若測試引用最近的程式碼則保留；切換焦點則壓縮 |
| Debugging → Next feature | 是 | Debug 追蹤記錄會污染不相關工作的 context |
| Mid-implementation | 否 | 遺失變數名稱、檔案路徑和部分狀態代價高昂 |
| After a failed approach | 是 | 嘗試新方向前清除死路推理 |

## What Survives Compaction

Understanding what persists helps you compact with confidence:

| 保留 | 遺失 |
|------|------|
| AGENTS.md 指示 | 中間推理與分析過程 |
| TodoWrite 任務清單 | 之前讀取的檔案內容 |
| 磁碟上的檔案 | 多步驟對話 context |
| Git 狀態（commits、branches） | Tool call 歷史與計數 |
| Memory 檔案 | 口頭表達的細微使用者偏好 |

## Best Practices

1. **Compact after planning** - Once plan is finalized, compact to start fresh
2. **Compact after debugging** - Clear error-resolution context before continuing
3. **Don't compact mid-implementation** - Preserve context for related changes
4. **Read the suggestion** - The hook tells you _when_, you decide _if_
5. **Write before compacting** - Save important context to files or memory before compacting
6. **Use `/compact` with a summary** - Add a custom message: `/compact Focus on implementing auth middleware next`

## Related

- [The Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) - Token optimization section
- Memory persistence hooks - For state that survives compaction
- `continuous-learning` skill - Extracts patterns before session ends
