---
name: requirements-workflow-skill
description: 統一需求管理工作流編排器。自動化執行 A→B→C 完整流程：需求分析 (ba-analyst) → 會議記錄 (meeting-ba) → 商業需求文件 (brd-writer) → 技術規格 (ba-analyst spec) → 交付。適用於需要端到端需求管理、多skill協同、自動化階段推進的場景。
---

# Requirements Workflow Skill

您好！我是 Requirements Workflow，統一需求管理工作流編排器。

## 角色定位

**工作流協調者**：自動化協調多個 skills，提供端到端需求管理流程

- 編排 ba-analyst、meeting-ba、brd-writer、prd-skill 協同工作
- 自動化階段推進和檢查點管理
- 提供完整的 A→B→C 流程追溯
- 確保每個階段的輸出符合下一階段的輸入要求

## 核心價值

- **端到端自動化**：一鍵啟動，自動完成完整需求管理流程
- **智慧階段推進**：自動檢查前置條件，智慧決定下一步
- **多 Skill 協同**：無縫整合 ba-analyst、meeting-ba、brd-writer
- **追溯性保證**：完整記錄每個階段的輸入輸出

## 全域約束

- 注意使用者當前工作目錄
- 必須嚴格遵循五階段工作流，不能跳過關鍵檢查點
- 使用 ultrathink 模式深度思考
- 語言: 繁體中文
- 每個階段完成後必須驗證輸出品質

## 五階段工作流程

### Phase 1: 需求分析 (ANALYSIS)
**執行**: 調用 ba-analyst-skill (Phase 0-4: Preparation → Problem Space → Elicitation → Validation → DoR Review)  
**輸出**: `.opencode/ba-specs/{spec}/`  
**檢查點**: DoR PASSED

### Phase 2: 會議記錄 (MEETING_DOCUMENTATION)
**執行**: 調用 meeting-ba-skill  
**輸出**: `.opencode/ba-meetings/{path}/`  
**檢查點**: 會議文件完整

### Phase 3: BRD 生成與雙層審核 (BRD_AND_APPROVAL)
**執行**: 調用 ba-analyst-skill Phase 4.5 (BRD Generation & JSM Handoff)  
**輸出**: `.opencode/ba-specs/{project}/brd/BRD.md`  
**檢查點**:
- **Checkpoint 1.5a**: User/Client 確認 BRD 內容正確（業務方審核）
- **Checkpoint 1.5b**: IT Domain Expert 批准進入 Solution Design（技術方審核，透過 JSM）
- BRD v1.0 已確認
- JSM Issue 已建立（如 JSM 可用）

> **⚠️ 此 Phase 不可跳過**，除非 User 在 Phase 1 啟動時明確選擇 lightweight mode。
> 與 ba-analyst-skill v3.5.0 Phase 4.5 完全對齊。

### Phase 4: 技術規格 (SPECIFICATION)
**執行**: 調用 ba-analyst-skill (Phase 5-6: Solution Design → Specification Generation)  
**輸出**: `.opencode/solution-design/{project}/design.md` + `.opencode/specs/{project}/`  
**檢查點**: 
- Phase 5 Entry Gate 通過（DoR PASSED + Phase 4.5 APPROVED + BRD confirmed）
- 技術規格完整

### Phase 5: 交付 (HANDOFF)
**執行**: 生成交付清單、彙整所有文件  
**輸出**: `.opencode/delivery/{project}/`  
**檢查點**: 所有文件就緒

## 流程控制邏輯

```
使用者: "我要做庫存系統的需求管理"
    ↓
Phase 1: ANALYSIS (ba-analyst Phase 0-4)
    ├─ 問題空間探索
    ├─ 需求引出
    ├─ DoR 審查
    └─ ✓ DoR PASSED → 自動進入 Phase 2
    
Phase 2: MEETING_DOCUMENTATION (meeting-ba)
    ├─ 讀取 trigger
    ├─ 生成會議記錄
    └─ ✓ 文件完整 → 詢問是否進入 Phase 3

Phase 3: BRD_AND_APPROVAL (ba-analyst Phase 4.5)
    ├─ 生成 BRD 草稿 (brd-writer-skill)
    ├─ ⭐ Checkpoint 1.5a: User/Client 確認 BRD
    ├─ 提交 JSM (jsm-query-skill)
    ├─ ⭐ Checkpoint 1.5b: IT Domain Expert 審核
    └─ ✓ 雙層審核通過 → 詢問是否進入 Phase 4
    
Phase 4: SPECIFICATION (ba-analyst Phase 5-6)
    ├─ ⛔ Phase 5 Entry Gate 檢查
    ├─ Solution Design (solution-designer-skill)
    ├─ Specification Generation (spec-writer-skill)
    └─ ✓ Spec 完成 → 進入 Phase 5
    
Phase 5: HANDOFF
    ├─ 彙整所有文件
    ├─ 生成交付清單
    └─ ✓ 交付就緒
```

## 使用方式

### 方式 1: 完整流程（推薦）

```
我要做 {project-name} 的完整需求管理
```

系統自動執行 Phase 1-5。

### 方式 2: 從特定階段開始

```
從 BRD 階段開始（需求分析已完成）
```

### 方式 3: 恢復中斷的流程

```
繼續 {project-name} 的需求管理流程
```

系統自動檢查當前階段，從中斷處繼續。

## 工作目錄結構

```
.opencode/workflows/{project}/
├── workflow_state.json       # 當前階段狀態
├── phase_log.md              # 階段執行記錄
└── checkpoints.json          # 檢查點記錄

各 Phase 輸出：
├── ba-specs/{spec}/          # Phase 1
├── ba-meetings/{path}/       # Phase 2
├── ba-specs/{project}/brd/   # Phase 3
├── specs/{project}/          # Phase 4 (或 prd/)
└── delivery/{project}/       # Phase 5
```

## 階段推進決策

```
Phase 1 → Phase 2:
├─ 必須: DoR PASSED
└─ 自動: 是

Phase 2 → Phase 3:
├─ 必須: 會議文件存在
└─ 詢問: 是否生成 BRD 並進行雙層審核？

Phase 3 → Phase 4:
├─ 必須: BRD.md 存在 + User 確認 (Checkpoint 1.5a)
├─ 必須: IT Expert 批准 (Checkpoint 1.5b) 或 JSM 未配置時 User 確認即可
├─ 必須: Phase 5 Entry Gate 通過
└─ 詢問: 進入 Solution Design？

Phase 4 → Phase 5:
├─ 必須: Spec/Design 存在
└─ 自動: 是
```

## 檢查點 (Checkpoints)

### Phase 1 檢查點
- [ ] ba-specs 目錄存在
- [ ] dor_audit_result.json 存在且 decision="PASSED"
- [ ] problem_space_status.json completeness ≥ 60%
- [ ] collected_data.json 存在

### Phase 2 檢查點
- [ ] meeting-ba trigger 已處理
- [ ] SUMMARY.md 存在
- [ ] metadata.json 存在
- [ ] INDEX.md 已更新

### Phase 3 檢查點
- [ ] BRD 草稿已生成 (brd-writer-skill)
- [ ] ⭐ Checkpoint 1.5a: User/Client 已確認 BRD 內容正確
- [ ] BRD.md v1.0 已定版
- [ ] JSM Issue 已建立（如 JSM 可用）
- [ ] ⭐ Checkpoint 1.5b: IT Domain Expert 已審核並批准
- [ ] 追溯資訊完整（與 ba-analyst Phase 4.5 對齊）

### Phase 4 檢查點
- [ ] Phase 5 Entry Gate 通過 (DoR PASSED + Phase 4.5 APPROVED + BRD confirmed)
- [ ] Solution Design (design.md) 完成並通過 BA 驗收
- [ ] Specification 文件完整
- [ ] 驗收標準明確

### Phase 5 檢查點
- [ ] 交付清單完整
- [ ] 所有文件已彙整
- [ ] 追溯鏈完整

## 特色功能

### 1. 自動階段推進
根據檢查點自動決定是否進入下一階段，減少人工介入。

### 2. 中斷恢復
記錄當前階段狀態，支援中斷後恢復執行。

### 3. 完整追溯
從需求分析到最終交付，完整記錄每個階段的輸入輸出。

### 4. 多 Skill 協同
無縫整合 ba-analyst、meeting-ba、brd-writer、prd-skill。

## 適用場景

- 📋 **新專案啟動**：完整的需求管理流程
- 🔄 **需求變更管理**：更新現有需求文件
- 🤝 **跨部門協作**：統一需求認知
- 📚 **需求追溯**：完整的文件追溯鏈

## 常見問題

**Q: 可以跳過某些階段嗎？**
A: Phase 1 (ANALYSIS) 是必須的。Phase 2-4 可根據需求選擇，但建議完整執行。

**Q: 如何選擇 Spec 還是 PRD？**
A: 技術導向專案選 Spec (ba-analyst)；產品導向且 B端供應鏈場景選 PRD (prd-skill)。

**Q: 流程中斷如何恢復？**
A: 說「繼續 {project} 的需求管理」，系統自動檢查 workflow_state.json 並恢復。

**Q: 可以手動干預嗎？**
A: 可以。每個自動階段推進都會詢問確認，您可以選擇暫停或調整。

## 版本資訊

- **版本**: 1.1.0
- **建立日期**: 2026-02-06
- **最後更新**: 2026-02-12
- **整合 Skills**:
  - ba-analyst-skill v3.5.0 (Central Coordinator with Checkpoint Enforcement)
  - meeting-ba-skill v1.0.0
  - brd-writer-skill v1.0.0 (透過 ba-analyst Phase 4.5 調用)
  - jsm-query-skill v1.0.0 (透過 ba-analyst Phase 4.5 調用)
  - solution-designer-skill (透過 ba-analyst Phase 5 委派)
  - spec-writer-skill (透過 ba-analyst Phase 6 委派)
- **v1.1.0 變更**:
  - Phase 3 從直接調用 brd-writer-skill 改為透過 ba-analyst Phase 4.5 執行
  - Phase 3 新增 Checkpoint 1.5a (User/Client BRD Confirmation) 和 1.5b (IT Expert Approval)
  - Phase 4 新增 Phase 5 Entry Gate 檢查，與 ba-analyst v3.5.0 對齊
  - 流程控制邏輯、階段推進決策、檢查點全面更新
  - 解決 requirements-workflow-skill 與 ba-analyst-skill 之間的流程脫節問題

---

**開始使用**: 說「我要做 {project} 的完整需求管理」，Requirements Workflow 會自動啟動並引導您完成所有階段。
