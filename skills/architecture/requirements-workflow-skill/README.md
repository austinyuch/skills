# requirements-workflow-skill

統一需求管理工作流編排器，自動化 A→B→C 完整流程。

## 快速開始

```
我要做 {project} 的完整需求管理
```

系統自動執行：
1. Phase 1: 需求分析 (ba-analyst)
2. Phase 2: 會議記錄 (meeting-ba)
3. Phase 3: 商業需求文件 (brd-writer)
4. Phase 4: 技術規格 (ba-analyst/prd)
5. Phase 5: 交付彙整

## 輸出

```
.opencode/
├── ba-specs/{spec}/          # Phase 1
├── ba-meetings/{path}/       # Phase 2
├── ba-specs/{project}/brd/   # Phase 3
├── specs/{project}/          # Phase 4
└── delivery/{project}/       # Phase 5
```

## 文檔

- [SKILL.md](./SKILL.md) - 完整說明
- [phases/](./phases/) - 5 個階段指南
- [workflows/default-workflow.md](./workflows/default-workflow.md) - 流程定義

## 版本

v1.0.0 (2026-02-06)
