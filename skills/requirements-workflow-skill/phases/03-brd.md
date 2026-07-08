# Phase 3: Business Requirements Document (BRD) Generation

## 目標 (Objective)

從會議記錄和需求分析結果生成標準化的商業需求文件 (BRD)。

## 輸入要求 (Input Requirements)

### 必要輸入 (Required)
- **BA 規格輸出**: `.opencode/ba-specs/{spec-name}/`
  - 必須包含 DoR PASSED 的需求分析結果
  - 包含問題空間、需求、驗收標準等
  
### 建議輸入 (Recommended)
- **會議記錄**: `.opencode/ba-meetings/by-user/{user}/{topic}/`
  - 包含完整的對話記錄和會議摘要
  - 提供額外的業務背景和脈絡

## 輸入驗證策略 (Input Validation Strategy)

### 驗證步驟

1. **檢查 BA 規格是否存在**
   ```bash
   # 尋找最近的 ba-specs
   ls -t ~/.opencode/ba-specs/
   ```

2. **檢查會議記錄是否存在**
   ```bash
   # 尋找相關的會議記錄
   ls -la ~/.opencode/ba-meetings/by-topic/
   ```

3. **驗證 DoR 狀態**
   ```bash
   # 確認 DoR 已通過
   cat ~/.opencode/ba-specs/{spec-name}/dor_audit_result.json
   # 應包含: "decision": "PASSED"
   ```

### 容錯策略

| 情境 | 處理方式 |
|------|---------|
| BA 規格存在 + 會議記錄存在 | ✅ 理想情況，使用兩者生成 BRD |
| BA 規格存在 + 會議記錄不存在 | ⚠️ 僅使用 BA 規格生成 BRD，提示使用者會議記錄可提升品質 |
| BA 規格不存在 | ❌ 無法生成 BRD，引導使用者執行 Phase 1 |
| DoR 未通過 | ❌ BRD 需求不完整，建議完成 DoR 審查後再生成 |

## 執行步驟 (Execution Steps)

### Step 1: 輸入探索與驗證

**執行動作**:
```bash
# 1. 列出所有 ba-specs
ls -t ~/.opencode/ba-specs/

# 2. 詢問使用者選擇或確認專案
"我找到以下需求分析結果：
1. {spec-name-1} (最近修改)
2. {spec-name-2}
3. {spec-name-3}

請選擇要生成 BRD 的專案，或輸入新專案名稱："

# 3. 驗證 DoR 狀態
cat ~/.opencode/ba-specs/{selected-spec}/dor_audit_result.json
```

**預期輸出**:
- 確認的專案名稱: `{project-name}`
- BA 規格路徑: `.opencode/ba-specs/{project-name}/`
- DoR 狀態: PASSED ✅

### Step 2: 檢查會議記錄

**執行動作**:
```bash
# 搜尋相關會議記錄
find ~/.opencode/ba-meetings/by-topic/ -name "*{project-name}*"
```

**條件判斷**:
```
IF 找到會議記錄:
  → 記錄路徑: {meeting-docs-path}
  → 提示使用者: "找到相關會議記錄，將結合使用以提升 BRD 品質"
ELSE:
  → 提示使用者: "未找到會議記錄，將僅使用需求分析結果生成 BRD"
  → 建議: "如需更完整的 BRD，可先執行 Phase 2 記錄會議"
  → 詢問: "是否繼續生成 BRD? (y/n)"
```

### Step 3: 調用 brd-writer-skill

**執行指令**:
```markdown
請使用 brd-writer-skill 為專案 "{project-name}" 生成商業需求文件 (BRD)。

**輸入來源**:
- BA 規格: .opencode/ba-specs/{project-name}/
- 會議記錄: {meeting-docs-path} [如果存在]

**輸出位置**:
- .opencode/ba-specs/{project-name}/brd/BRD.md

請確保 BRD 包含完整的 8 個標準章節。
```

**監控 brd-writer-skill 執行**:
- 等待 brd-writer-skill 完成所有 4 個策略
- 監控輸出訊息，確認無錯誤

### Step 4: 驗證 BRD 生成

**驗證檢查**:
```bash
# 1. 檢查 BRD 檔案是否存在
test -f ~/.opencode/ba-specs/{project-name}/brd/BRD.md && echo "✅ BRD 已生成"

# 2. 檢查 BRD 大小 (應 > 1KB)
ls -lh ~/.opencode/ba-specs/{project-name}/brd/BRD.md

# 3. 檢查 BRD 章節完整性
grep -E "^## [0-9]\." ~/.opencode/ba-specs/{project-name}/brd/BRD.md | wc -l
# 應輸出: 8 (8 個標準章節)

# 4. 檢查 INDEX 是否更新
grep "{project-name}" ~/.opencode/ba-specs/{project-name}/brd/INDEX.md
```

**驗證結果**:
```
IF 所有檢查通過:
  → 狀態: phase3_brd_complete = true
  → 繼續下一步
ELSE:
  → 報告錯誤詳情
  → 提供除錯建議
  → 停止工作流程
```

### Step 5: 更新工作流程狀態

**狀態更新**:
```json
{
  "workflow_id": "{project-name}-{timestamp}",
  "project": "{project-name}",
  "current_phase": 3,
  "phases_complete": {
    "phase1_analysis": true,
    "phase2_meeting": true,
    "phase3_brd": true,
    "phase4_spec": false,
    "phase5_handoff": false
  },
  "artifacts": {
    "ba_specs": ".opencode/ba-specs/{project-name}/",
    "meeting_docs": "{meeting-docs-path}",
    "brd": ".opencode/ba-specs/{project-name}/brd/BRD.md",
    "specs": null
  },
  "last_update": "{ISO-8601-timestamp}"
}
```

**儲存位置**: `.opencode/workflow/{project-name}/state.json`

## 輸出 (Outputs)

### 主要輸出
1. **BRD 文件**: `.opencode/ba-specs/{project-name}/brd/BRD.md`
   - 包含 8 個標準章節
   - 整合 BA 規格和會議記錄內容
   
2. **BRD 索引**: `.opencode/ba-specs/{project-name}/brd/INDEX.md`
   - 自動更新，加入新生成的 BRD

3. **工作流程狀態**: `.opencode/workflow/{project-name}/state.json`
   - phase3_brd_complete = true
   - 記錄 BRD 路徑

### 輸出驗證
- ✅ BRD.md 檔案存在且大小 > 1KB
- ✅ 包含完整 8 個章節
- ✅ INDEX.md 已更新
- ✅ 工作流程狀態已保存

## 錯誤處理 (Error Handling)

### 錯誤情境與處理

| 錯誤代碼 | 情境 | 處理方式 |
|---------|------|---------|
| `ERR_NO_BA_SPECS` | 找不到 BA 規格 | 提示執行 Phase 1 進行需求分析 |
| `ERR_DOR_NOT_PASSED` | DoR 審查未通過 | 建議回到 ba-analyst 完成 DoR 審查 |
| `ERR_BRD_GENERATION_FAILED` | brd-writer-skill 執行失敗 | 檢查錯誤訊息，提供除錯建議 |
| `ERR_BRD_INCOMPLETE` | BRD 章節不完整 | 要求 brd-writer 重新生成缺失章節 |
| `ERR_STATE_SAVE_FAILED` | 無法保存工作流程狀態 | 檢查磁碟空間和權限 |

### 錯誤訊息範例

```markdown
❌ **錯誤: 找不到 BA 規格**

在 `.opencode/ba-specs/` 中找不到專案 "{project-name}" 的需求分析結果。

**建議操作**:
1. 執行 Phase 1: `"開始需求分析"`
2. 完成 ba-analyst 工作流程
3. 確保 DoR 審查通過 (PASSED)
4. 再回來執行 Phase 3

**或者**:
- 如果已有 BA 規格，請確認路徑是否正確
- 檢查 `.opencode/ba-specs/` 目錄權限
```

## 下一步建議 (Next Step Suggestion)

### 成功完成時

```markdown
✅ **Phase 3 完成: BRD 已成功生成**

**生成的文件**:
- 📄 BRD: .opencode/ba-specs/{project-name}/brd/BRD.md
- 📑 索引: .opencode/ba-specs/{project-name}/brd/INDEX.md

**BRD 內容概覽**:
- ✅ 8 個標準章節完整
- ✅ 整合需求分析結果
- ✅ [如有] 包含會議記錄脈絡

---

**準備進入 Phase 4: 技術規格撰寫**

您可以選擇生成以下規格類型:

1. **Interface Spec** (介面規格)
   - 適用於: 外部系統整合、API 設計
   - 工具: ba-analyst-skill (interface mode)

2. **Function Spec** (功能規格)
   - 適用於: 內部功能邏輯、業務流程
   - 工具: ba-analyst-skill (function mode)

3. **Report Spec** (報表規格)
   - 適用於: 資料報表、儀表板設計
   - 工具: ba-analyst-skill (report mode)

4. **PRD** (產品需求文件)
   - 適用於: B 端供應鏈產品設計
   - 工具: prd-skill

---

**下一步指令**:
- 繼續工作流程: `"進入 Phase 4"` 或 `"生成技術規格"`
- 指定規格類型: `"生成 Interface Spec"` 或 `"生成 PRD"`
- 暫停工作流程: `"暫停，我需要先檢視 BRD"`

**提示**: 如果不確定要生成哪種規格，我可以根據 BRD 內容提供建議。
```

### 部分成功時 (無會議記錄)

```markdown
⚠️ **Phase 3 完成: BRD 已生成 (基於需求分析)**

**生成的文件**:
- 📄 BRD: .opencode/ba-specs/{project-name}/brd/BRD.md

**品質提示**:
- ✅ 基於完整的需求分析結果
- ⚠️ 未整合會議記錄 (可能缺少業務背景脈絡)

**建議改進**:
如需更完整的 BRD，可執行以下步驟:
1. 回到 Phase 2: `"記錄這次會議"`
2. 重新生成 BRD: `"重新生成 BRD"`

**或直接繼續**:
- 繼續工作流程: `"進入 Phase 4"`
```

## 與其他 Phase 的整合

### 輸入依賴
- **Phase 1 (Analysis)**: 提供 BA 規格 `.opencode/ba-specs/{project}/`
- **Phase 2 (Meeting Doc)**: 提供會議記錄 `.opencode/ba-meetings/` (可選)

### 輸出供應
- **Phase 4 (Spec)**: BRD 作為技術規格的輸入參考
- **Phase 5 (Handoff)**: BRD 作為交付物件之一

### 跳過條件
如果 BRD 已存在且使用者確認不需重新生成:
```bash
# 檢查 BRD 是否存在
if [ -f ~/.opencode/ba-specs/{project-name}/brd/BRD.md ]; then
  # 詢問使用者
  "檢測到 BRD 已存在。是否要:
  1. 跳過此步驟，使用現有 BRD
  2. 重新生成 BRD (覆蓋現有版本)
  3. 生成新版本並保留舊版 (BRD_v2.md)"
fi
```

## 品質檢查 (Quality Checks)

### BRD 完整性檢查

```bash
#!/bin/bash
# 檢查 BRD 8 個標準章節

BRD_PATH="$HOME/.opencode/ba-specs/${PROJECT_NAME}/brd/BRD.md"

REQUIRED_SECTIONS=(
  "Executive Summary"
  "Business Background"
  "Business Objectives"
  "Stakeholders"
  "Business Requirements"
  "Constraints and Assumptions"
  "Success Criteria"
  "Risks and Dependencies"
)

echo "檢查 BRD 章節完整性..."
MISSING_SECTIONS=()

for section in "${REQUIRED_SECTIONS[@]}"; do
  if ! grep -q "$section" "$BRD_PATH"; then
    MISSING_SECTIONS+=("$section")
  fi
done

if [ ${#MISSING_SECTIONS[@]} -eq 0 ]; then
  echo "✅ BRD 所有章節完整"
  exit 0
else
  echo "❌ BRD 缺少以下章節:"
  printf '%s\n' "${MISSING_SECTIONS[@]}"
  exit 1
fi
```

### BRD 內容品質檢查

```bash
# 檢查 BRD 是否包含實質內容
MIN_SIZE=1024  # 1KB
ACTUAL_SIZE=$(stat -f%z "$BRD_PATH" 2>/dev/null || stat -c%s "$BRD_PATH")

if [ "$ACTUAL_SIZE" -lt "$MIN_SIZE" ]; then
  echo "⚠️ BRD 大小過小 ($ACTUAL_SIZE bytes)，可能內容不完整"
  exit 1
fi

# 檢查是否包含 TODO 或 placeholder
if grep -q "TODO\|XXX\|PLACEHOLDER" "$BRD_PATH"; then
  echo "⚠️ BRD 包含未完成的內容標記"
  exit 1
fi

echo "✅ BRD 內容品質檢查通過"
```

## 時間估算 (Time Estimates)

| 步驟 | 預估時間 |
|------|---------|
| 輸入驗證 | 30 秒 |
| 調用 brd-writer-skill | 2-5 分鐘 |
| BRD 生成 | 3-8 分鐘 |
| 驗證與狀態更新 | 30 秒 |
| **總計** | **6-14 分鐘** |

*實際時間取決於專案複雜度和 LLM 回應速度*

## 參考文件

- **BRD 模板**: `~/.config/opencode/skills/brd-writer-skill/templates/BRD_TEMPLATE.md`
- **BRD Writer Skill**: `~/.config/opencode/skills/brd-writer-skill/SKILL.md`
- **BA Analyst 輸出格式**: `~/.config/opencode/skills/business/ba-analyst-skill/README.md`
- **Meeting BA Skill 輸出**: `~/.config/opencode/skills/meeting-ba-skill/templates/`

---

*最後更新: 2026-02-06*
*Phase 狀態: COMPLETE*
