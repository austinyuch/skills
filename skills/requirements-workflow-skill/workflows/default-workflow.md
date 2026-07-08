# Default Requirements Management Workflow (A→B→C)

**Version**: 1.0.0  
**Created**: 2026-02-06  
**Workflow Type**: Sequential with Checkpoint Recovery

---

## 工作流程總覽 (Workflow Overview)

這是完整的需求管理自動化工作流程，實現從分析 (Analysis) → 文件 (Documentation) → 規格 (Specification) 的完整循環。

```
┌─────────────────────────────────────────────────────────────┐
│                  A → B → C Workflow                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: ANALYSIS (需求分析)                                │
│  ├─ 使用: ba-analyst-skill                                  │
│  ├─ 輸入: 使用者需求、業務問題                                │
│  ├─ 輸出: .opencode/ba-specs/{project}/                     │
│  └─ 檢查點: DoR PASSED                                       │
│                                                             │
│  ↓ (自動觸發)                                                │
│                                                             │
│  Phase 2: MEETING DOCUMENTATION (會議記錄)                   │
│  ├─ 使用: meeting-ba-skill                                  │
│  ├─ 輸入: ba-analyst 對話記錄                                │
│  ├─ 輸出: .opencode/ba-meetings/                            │
│  └─ 檢查點: 分層文件已建立                                    │
│                                                             │
│  ↓ (建議下一步)                                              │
│                                                             │
│  Phase 3: BRD GENERATION (商業需求文件)                      │
│  ├─ 使用: brd-writer-skill                                  │
│  ├─ 輸入: BA specs + Meeting docs                          │
│  ├─ 輸出: .opencode/ba-specs/{project}/brd/BRD.md            │
│  └─ 檢查點: 8 章節完整                                       │
│                                                             │
│  ↓ (建議規格類型)                                            │
│                                                             │
│  Phase 4: SPECIFICATION (技術規格)                           │
│  ├─ 使用: ba-analyst-skill OR prd-skill                     │
│  ├─ 輸入: BRD + BA specs                                    │
│  ├─ 輸出: .opencode/ba-specs/{project}/{spec-type}/         │
│  │         OR .opencode/prd/{project}/PRD.md                │
│  └─ 檢查點: 規格完整 + DoR PASSED (if applicable)            │
│                                                             │
│  ↓ (自動進入)                                                │
│                                                             │
│  Phase 5: HANDOFF (交付彙整)                                 │
│  ├─ 使用: requirements-workflow-skill (內建)                 │
│  ├─ 輸入: 所有前置階段輸出                                    │
│  ├─ 輸出: .opencode/handoff/{project}/                      │
│  └─ 完成: 工作流程結束                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 工作流程執行模式 (Execution Modes)

### Mode 1: 自動化模式 (Automated Mode)

使用者單一指令啟動，系統自動執行所有階段：

```
使用者: "啟動需求工作流程" 或 "start requirements workflow"

系統執行:
1. Phase 1: ba-analyst → DoR PASSED
2. Phase 2: meeting-ba-skill → 文件已建立
3. Phase 3: brd-writer-skill → BRD 已生成
4. Phase 4: [詢問使用者選擇規格類型] → 規格已生成
5. Phase 5: 自動彙整 → 交付包已建立

結果: 完整的需求管理交付包
```

**適用場景**:
- 新專案完整需求流程
- 標準化需求管理
- 需要完整文件追溯

### Mode 2: 手動模式 (Manual Mode)

使用者逐步執行每個階段：

```
使用者: "我要做需求分析"
→ Phase 1 完成

使用者: "記錄這次會議"
→ Phase 2 完成

使用者: "生成 BRD"
→ Phase 3 完成

使用者: "生成 Interface Spec"
→ Phase 4 完成

使用者: "進入 Phase 5"
→ Phase 5 完成
```

**適用場景**:
- 需要逐步檢視結果
- 需要在階段間做決策
- 只需要部分階段

### Mode 3: 檢查點恢復模式 (Checkpoint Recovery Mode)

工作流程中斷後，從檢查點恢復：

```
系統檢測到:
- Phase 1: ✅ 完成
- Phase 2: ✅ 完成
- Phase 3: ❌ 中斷

使用者: "繼續需求工作流程" 或 "resume workflow"

系統: "檢測到工作流程在 Phase 3 中斷，繼續執行..."
→ 從 Phase 3 開始執行
→ 完成後續所有階段
```

**適用場景**:
- 工作流程意外中斷
- 需要暫停後繼續
- 分批次執行

---

## 狀態管理 (State Management)

### 工作流程狀態文件

**位置**: `.opencode/workflow/{project-name}/state.json`

**格式**:
```json
{
  "workflow_id": "{project-name}-{timestamp}",
  "project": "{project-name}",
  "workflow_version": "1.0.0",
  "mode": "automated|manual|recovery",
  "current_phase": 1,
  "status": "in_progress|paused|complete|failed",
  "phases_complete": {
    "phase1_analysis": false,
    "phase2_meeting": false,
    "phase3_brd": false,
    "phase4_spec": false,
    "phase5_handoff": false
  },
  "artifacts": {
    "ba_specs": null,
    "meeting_docs": null,
    "brd": null,
    "specs": {},
    "handoff_package": null
  },
  "spec_types_generated": [],
  "started_at": "{ISO-8601-timestamp}",
  "last_update": "{ISO-8601-timestamp}",
  "completed_at": null,
  "total_duration": null,
  "checkpoints": [
    {
      "phase": 1,
      "timestamp": "{ISO-8601-timestamp}",
      "status": "complete",
      "artifacts": [".opencode/ba-specs/{project}/"]
    }
  ],
  "errors": []
}
```

### 狀態轉換 (State Transitions)

```
[START]
  ↓
in_progress → Phase 1 執行中
  ↓
in_progress → Phase 2 執行中
  ↓
paused ← 使用者暫停 (可選)
  ↓
in_progress → Phase 3 執行中
  ↓
in_progress → Phase 4 執行中 (可能需要使用者輸入)
  ↓
in_progress → Phase 5 執行中
  ↓
complete → [END]

(如有錯誤)
  ↓
failed → 記錄錯誤 → 等待修復 → 恢復到上一個檢查點
```

---

## 命令參考 (Command Reference)

### 啟動命令

```bash
# 自動化模式 (完整執行)
"啟動需求工作流程"
"start requirements workflow"
"execute full workflow for {project-name}"

# 手動模式 (逐步執行)
"我要做 {project} 的需求分析"  # 僅 Phase 1
"記錄這次會議"                  # 僅 Phase 2
"生成 BRD"                      # 僅 Phase 3
"生成 {spec-type} 規格"        # 僅 Phase 4
"進入 Phase 5"                  # 僅 Phase 5
```

### 控制命令

```bash
# 暫停
"暫停工作流程"
"pause workflow"

# 恢復
"繼續需求工作流程"
"resume workflow"
"從 Phase {N} 繼續"

# 重試
"重新執行 Phase {N}"
"retry phase {N}"

# 跳過
"跳過 Phase {N}"
"skip phase {N}"

# 狀態查詢
"顯示工作流程狀態"
"show workflow status"
"工作流程進度"
```

### 檢視命令

```bash
# 查看交付物
"顯示 BA 規格"
"顯示 BRD"
"顯示 {spec-type} 規格"
"顯示交付包"

# 查看狀態
"工作流程狀態"
"檢查點列表"
"錯誤日誌"
```

---

## 最佳實踐 (Best Practices)

### 1. 完整執行所有 Phases
- ✅ 建議執行完整的 5 個 Phases
- ✅ Phase 2 雖然可選，但強烈建議執行以保留脈絡
- ✅ 確保每個 Phase 的輸出經過驗證

### 2. 及時保存檢查點
- ✅ 每個 Phase 完成後自動保存
- ✅ 長時間執行時定期手動保存
- ✅ 重要決策點建立額外檢查點

### 3. 善用恢復機制
- ✅ 中斷後使用 resume 而非重新開始
- ✅ 檢查工作流程狀態確認恢復點
- ✅ 修復錯誤後立即恢復，避免遺忘

### 4. 選擇適當的規格類型
- ✅ 根據 BRD 建議選擇
- ✅ 複雜專案可選擇多種規格
- ✅ 不確定時選擇 Interface + Function

### 5. 驗證交付包完整性
- ✅ 檢視 HANDOFF_CHECKLIST.md
- ✅ 確認 TRACEABILITY_MATRIX.md 完整
- ✅ 所有規格通過 DoR 審查

---

## 故障排除 (Troubleshooting)

### 常見問題

**Q: Phase 2 未觸發會議記錄**
A: 檢查 `.config/opencode/.triggers/ba-meetings/` 是否有觸發文件。如無，可手動執行 `"記錄這次會議"`。

**Q: Phase 4 無法選擇規格類型**
A: 確認 BRD 已正確生成。檢查 `.opencode/ba-specs/{project}/brd/BRD.md` 是否存在且大小 > 1KB。

**Q: 工作流程卡在某個 Phase**
A: 使用 `"顯示工作流程狀態"` 查看當前狀態。如有錯誤，使用 `"錯誤日誌"` 查看詳情。修復後使用 `"繼續工作流程"`。

**Q: 交付包缺少某些文件**
A: 檢查 `state.json` 中的 `artifacts` 欄位，確認所有 Phases 是否完成。如有缺失，回到對應 Phase 重新執行。

**Q: 如何重新生成某個 Phase 的輸出**
A: 使用 `"重新執行 Phase {N}"` 命令。系統會覆蓋現有輸出。

---

## 時間估算 (Time Estimates)

| Phase | 預估時間 | 說明 |
|-------|---------|------|
| Phase 1: Analysis | 1-2 hours | 取決於需求複雜度 |
| Phase 2: Meeting Doc | 5 minutes | 自動生成 |
| Phase 3: BRD | 6-14 minutes | 取決於輸入完整度 |
| Phase 4: Specification | 12-60 minutes | 取決於規格類型和數量 |
| Phase 5: Handoff | 18-23 minutes | 取決於交付物數量 |
| **總計** | **~2-3.5 hours** | 完整工作流程 |

---

## 版本歷史 (Version History)

### v1.0.0 (2026-02-06)
- ✅ 初始版本發布
- ✅ 實作完整 A→B→C 工作流程
- ✅ 支援自動化、手動、恢復三種模式
- ✅ 實作檢查點機制
- ✅ 實作狀態管理
- ✅ 實作錯誤處理與恢復

---

## 參考文件 (References)

- **Phase 1**: `phases/01-analysis.md`
- **Phase 2**: `phases/02-meeting-doc.md`
- **Phase 3**: `phases/03-brd.md`
- **Phase 4**: `phases/04-spec.md`
- **Phase 5**: `phases/05-handoff.md`
- **Skills**:
  - `skills/business/ba-analyst-skill/`
  - `skills/meeting-ba-skill/`
  - `skills/brd-writer-skill/`
  - `skills/prd-skill/`

---

*最後更新: 2026-02-06*
*Workflow 狀態: PRODUCTION READY*
*維護者: requirements-workflow-skill team*
