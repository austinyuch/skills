# Phase 4: Technical Specification Generation

## 目標 (Objective)

根據 BRD 內容生成技術規格文件，支援多種規格類型以滿足不同開發場景需求。

## 輸入要求 (Input Requirements)

### 必要輸入 (Required)
- **BRD 文件**: `.opencode/ba-specs/{project-name}/brd/BRD.md`
  - 包含完整的商業需求定義
  - 8 個標準章節齊全
  
### 可選輸入 (Optional but Helpful)
- **BA 規格輸出**: `.opencode/ba-specs/{spec-name}/`
  - 提供更詳細的需求分析背景
- **會議記錄**: `.opencode/ba-meetings/`
  - 提供額外的業務脈絡

## 規格類型選擇 (Spec Type Selection)

### 決策樹 (Decision Tree)

```
BRD 是否存在?
├─ Yes → 分析 BRD 內容，建議規格類型
│   ├─ 需要外部系統整合? → Interface Spec
│   ├─ 需要內部功能邏輯? → Function Spec
│   ├─ 需要資料報表/分析? → Report Spec
│   └─ 需要產品級文件? → PRD
└─ No → 錯誤: 請先執行 Phase 3 生成 BRD
```

### 規格類型說明

| 規格類型 | 適用場景 | 使用工具 | 輸出位置 |
|---------|---------|---------|---------|
| **Interface Spec** | 外部系統整合、API 設計、資料交換格式 | ba-analyst-skill (interface mode) | `.opencode/ba-specs/{project}/interface/` |
| **Function Spec** | 內部功能邏輯、業務流程、演算法設計 | ba-analyst-skill (function mode) | `.opencode/ba-specs/{project}/function/` |
| **Report Spec** | 資料報表、儀表板、分析需求 | ba-analyst-skill (report mode) | `.opencode/ba-specs/{project}/report/` |
| **PRD** | B 端供應鏈產品、完整產品需求 | prd-skill | `.opencode/prd/{project}/PRD.md` |

## 執行步驟 (Execution Steps)

### Step 1: 驗證 BRD 存在

**執行動作**:
```bash
# 檢查 BRD 是否存在
if [ -f ~/.opencode/ba-specs/{project-name}/brd/BRD.md ]; then
  echo "✅ BRD 已找到"
  BRD_PATH="$HOME/.opencode/ba-specs/${project-name}/brd/BRD.md"
else
  echo "❌ BRD 不存在，請先執行 Phase 3"
  exit 1
fi
```

**驗證內容**:
```bash
# 檢查 BRD 大小
BRD_SIZE=$(stat -c%s "$BRD_PATH" 2>/dev/null || stat -f%z "$BRD_PATH")
if [ "$BRD_SIZE" -lt 1024 ]; then
  echo "⚠️ BRD 大小過小，可能不完整"
fi

# 檢查 BRD 章節
SECTION_COUNT=$(grep -E "^## [0-9]\." "$BRD_PATH" | wc -l)
if [ "$SECTION_COUNT" -lt 8 ]; then
  echo "⚠️ BRD 章節不完整 (只有 $SECTION_COUNT / 8)"
fi
```

### Step 2: 分析 BRD 並建議規格類型

**執行動作**:
```markdown
根據 BRD 內容分析，我建議生成以下規格:

[讀取並分析 BRD.md 內容，重點關注:]
- Business Requirements (功能需求)
- Technical Requirements (技術需求)
- Integration Requirements (整合需求)
- Reporting Requirements (報表需求)

[根據分析結果提供建議:]

**建議的規格類型**: {推薦的規格類型}

**理由**:
- {分析理由 1}
- {分析理由 2}
- {分析理由 3}

**其他可能需要的規格**:
- {其他規格類型 1} - {說明}
- {其他規格類型 2} - {說明}
```

**詢問使用者**:
```
請選擇要生成的規格類型:

1. Interface Spec (介面規格) - 外部系統整合、API 設計
2. Function Spec (功能規格) - 內部功能邏輯、業務流程
3. Report Spec (報表規格) - 資料報表、儀表板設計
4. PRD (產品需求文件) - B 端供應鏈產品需求
5. 多種規格 (依序生成) - 同時生成多個規格

或輸入自訂選擇: {使用者輸入}
```

### Step 3: 路由到對應 Skill

#### Route 3A: ba-analyst-skill (Interface/Function/Report Spec)

**執行指令**:
```markdown
請使用 ba-analyst-skill 為專案 "{project-name}" 生成 {spec-type} 規格。

**輸入來源**:
- BRD: .opencode/ba-specs/{project-name}/brd/BRD.md
- BA 規格: .opencode/ba-specs/{project-name}/ [如果存在]
- 會議記錄: .opencode/ba-meetings/ [如果存在]

**輸出位置**:
- .opencode/ba-specs/{project-name}/{spec-type}/

**規格要求**:
- 完整的 {spec-type} 文件結構
- 包含所有必要章節
- 通過 DoR 審查

請按照 ba-analyst-skill 的標準工作流程執行。
```

**監控執行**:
```
等待 ba-analyst-skill 完成:
- Phase 1: 問題空間分析
- Phase 2: 需求收集
- Phase 3: 需求確認
- Phase 4: 規格撰寫
- Phase 5: DoR 審查

監控狀態並處理任何錯誤或中斷。
```

#### Route 3B: prd-skill (PRD Generation)

**執行指令**:
```markdown
請使用 prd-skill 為專案 "{project-name}" 生成產品需求文件 (PRD)。

**輸入來源**:
- BRD: .opencode/ba-specs/{project-name}/brd/BRD.md
- BA 規格: .opencode/ba-specs/{project-name}/ [如果存在]
- 會議記錄: .opencode/ba-meetings/ [如果存在]

**輸出位置**:
- .opencode/prd/{project-name}/PRD.md

**PRD 要求**:
- 完整的產品需求定義
- 包含功能模組設計
- 包含使用者體驗設計
- 包含技術架構建議

請按照 prd-skill 的標準工作流程執行。
```

**監控執行**:
```
等待 prd-skill 完成:
- Phase 1: 需求整理
- Phase 2: 資訊架構設計
- Phase 3: PRD 撰寫
- Phase 4: PRD 審查
- Phase 5: PRD 優化

監控狀態並處理任何錯誤或中斷。
```

#### Route 3C: 多規格生成 (Sequential Generation)

**執行策略**:
```
如果使用者選擇生成多種規格:

FOR EACH spec_type IN selected_spec_types:
  1. 調用對應的 skill 生成規格
  2. 等待完成並驗證
  3. 更新工作流程狀態
  4. 繼續下一個規格

輸出位置:
.opencode/ba-specs/{project-name}/
├── interface/
├── function/
└── report/

或

.opencode/prd/{project-name}/PRD.md
```

### Step 4: 驗證規格生成

**驗證檢查 (for ba-analyst)**:
```bash
# 1. 檢查規格目錄是否存在
SPEC_DIR="$HOME/.opencode/ba-specs/${PROJECT_NAME}/${SPEC_TYPE}"
test -d "$SPEC_DIR" && echo "✅ 規格目錄已建立"

# 2. 檢查必要文件
REQUIRED_FILES=(
  "requirements.md"
  "design.md"
  "tasks.md"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ -f "$SPEC_DIR/$file" ]; then
    echo "✅ $file 已建立"
  else
    echo "❌ $file 缺失"
  fi
done

# 3. 檢查 DoR 狀態
if [ -f "$SPEC_DIR/dor_audit_result.json" ]; then
  DOR_STATUS=$(jq -r '.decision' "$SPEC_DIR/dor_audit_result.json")
  if [ "$DOR_STATUS" = "PASSED" ]; then
    echo "✅ DoR 審查通過"
  else
    echo "⚠️ DoR 審查未通過: $DOR_STATUS"
  fi
fi
```

**驗證檢查 (for prd-skill)**:
```bash
# 1. 檢查 PRD 檔案是否存在
PRD_PATH="$HOME/.opencode/prd/${PROJECT_NAME}/PRD.md"
test -f "$PRD_PATH" && echo "✅ PRD 已生成"

# 2. 檢查 PRD 大小
PRD_SIZE=$(stat -c%s "$PRD_PATH" 2>/dev/null || stat -f%z "$PRD_PATH")
if [ "$PRD_SIZE" -gt 2048 ]; then
  echo "✅ PRD 大小合理 ($PRD_SIZE bytes)"
else
  echo "⚠️ PRD 大小過小 ($PRD_SIZE bytes)"
fi

# 3. 檢查 PRD 章節
SECTION_COUNT=$(grep -E "^#+ " "$PRD_PATH" | wc -l)
echo "📊 PRD 包含 $SECTION_COUNT 個章節"

# 4. 檢查 INDEX 是否更新
grep "${PROJECT_NAME}" "$HOME/.opencode/prd/INDEX.md" && echo "✅ INDEX 已更新"
```

### Step 5: 更新工作流程狀態

**狀態更新**:
```json
{
  "workflow_id": "{project-name}-{timestamp}",
  "project": "{project-name}",
  "current_phase": 4,
  "phases_complete": {
    "phase1_analysis": true,
    "phase2_meeting": true,
    "phase3_brd": true,
    "phase4_spec": true,
    "phase5_handoff": false
  },
  "artifacts": {
    "ba_specs": ".opencode/ba-specs/{project-name}/",
    "meeting_docs": "{meeting-docs-path}",
    "brd": ".opencode/ba-specs/{project-name}/brd/BRD.md",
    "specs": {
      "interface": ".opencode/ba-specs/{project-name}/interface/",
      "function": ".opencode/ba-specs/{project-name}/function/",
      "report": ".opencode/ba-specs/{project-name}/report/",
      "prd": ".opencode/prd/{project-name}/PRD.md"
    }
  },
  "spec_types_generated": ["interface", "function"],
  "last_update": "{ISO-8601-timestamp}"
}
```

**儲存位置**: `.opencode/workflow/{project-name}/state.json`

## 輸出 (Outputs)

### 主要輸出 (ba-analyst)

1. **Interface Spec**:
   - `.opencode/ba-specs/{project}/interface/requirements.md`
   - `.opencode/ba-specs/{project}/interface/design.md`
   - `.opencode/ba-specs/{project}/interface/tasks.md`
   - `.opencode/ba-specs/{project}/interface/dor_audit_result.json`

2. **Function Spec**:
   - `.opencode/ba-specs/{project}/function/requirements.md`
   - `.opencode/ba-specs/{project}/function/design.md`
   - `.opencode/ba-specs/{project}/function/tasks.md`
   - `.opencode/ba-specs/{project}/function/dor_audit_result.json`

3. **Report Spec**:
   - `.opencode/ba-specs/{project}/report/requirements.md`
   - `.opencode/ba-specs/{project}/report/design.md`
   - `.opencode/ba-specs/{project}/report/tasks.md`
   - `.opencode/ba-specs/{project}/report/dor_audit_result.json`

### 主要輸出 (prd-skill)

1. **PRD 文件**: `.opencode/prd/{project-name}/PRD.md`
   - 完整的產品需求定義
   - 功能模組設計
   - 使用者體驗設計
   - 技術架構建議

2. **PRD 索引**: `.opencode/prd/INDEX.md`
   - 自動更新，加入新生成的 PRD

### 輸出驗證
- ✅ 所有必要文件已生成
- ✅ 規格內容完整且結構正確
- ✅ DoR 審查通過 (ba-analyst)
- ✅ 工作流程狀態已更新

## 錯誤處理 (Error Handling)

### 錯誤情境與處理

| 錯誤代碼 | 情境 | 處理方式 |
|---------|------|---------|
| `ERR_NO_BRD` | 找不到 BRD 文件 | 提示執行 Phase 3 生成 BRD |
| `ERR_BRD_INCOMPLETE` | BRD 內容不完整 | 建議重新生成 BRD 或補充缺失章節 |
| `ERR_SPEC_GENERATION_FAILED` | 規格生成失敗 | 檢查錯誤訊息，提供除錯建議 |
| `ERR_DOR_NOT_PASSED` | DoR 審查未通過 | 要求 ba-analyst 修正並重新審查 |
| `ERR_INVALID_SPEC_TYPE` | 無效的規格類型 | 顯示有效選項，要求重新選擇 |
| `ERR_STATE_SAVE_FAILED` | 無法保存狀態 | 檢查磁碟空間和權限 |

### 錯誤訊息範例

```markdown
❌ **錯誤: 找不到 BRD 文件**

在 `.opencode/ba-specs/{project-name}/brd/` 中找不到 BRD.md。

**建議操作**:
1. 執行 Phase 3: `"生成 BRD"`
2. 確保 BRD 生成成功
3. 再回來執行 Phase 4

**或者**:
- 如果已有 BRD，請確認路徑是否正確
- 檢查 `.opencode/ba-specs/{project-name}/brd/` 目錄權限
```

## 下一步建議 (Next Step Suggestion)

### 成功完成時 (單一規格)

```markdown
✅ **Phase 4 完成: {Spec Type} 已成功生成**

**生成的規格**:
- 📄 規格位置: {spec-path}
- 📋 DoR 狀態: PASSED ✅ [如適用]

**規格內容概覽**:
- ✅ Requirements 完整
- ✅ Design 詳細
- ✅ Tasks 可執行

---

**準備進入 Phase 5: 交付彙整**

系統將自動彙整以下交付物:
- ✅ BA 規格 (Phase 1)
- ✅ 會議記錄 (Phase 2)
- ✅ BRD (Phase 3)
- ✅ 技術規格 (Phase 4)

**下一步指令**:
- 繼續工作流程: `"進入 Phase 5"` 或 `"開始交付彙整"`
- 生成額外規格: `"還需要生成 Function Spec"`
- 檢視規格: `"顯示規格內容"`
- 暫停工作流程: `"暫停，我需要先檢視規格"`
```

### 成功完成時 (多規格)

```markdown
✅ **Phase 4 完成: 多個規格已成功生成**

**生成的規格清單**:
1. ✅ Interface Spec - .opencode/ba-specs/{project}/interface/
2. ✅ Function Spec - .opencode/ba-specs/{project}/function/
3. ✅ Report Spec - .opencode/ba-specs/{project}/report/

**所有規格狀態**:
- ✅ DoR 審查全部通過
- ✅ 規格結構完整
- ✅ 可直接進入開發階段

---

**準備進入 Phase 5: 交付彙整**

**下一步指令**:
- 繼續工作流程: `"進入 Phase 5"`
- 檢視特定規格: `"顯示 Interface Spec"`
```

### 部分失敗時

```markdown
⚠️ **Phase 4 部分完成: 某些規格生成失敗**

**成功生成**:
- ✅ Interface Spec - .opencode/ba-specs/{project}/interface/

**失敗項目**:
- ❌ Function Spec - {錯誤原因}

**建議操作**:
1. 檢查錯誤訊息並修正問題
2. 重新生成失敗的規格: `"重新生成 Function Spec"`
3. 或跳過失敗項目繼續: `"跳過 Function Spec，進入 Phase 5"`

**提示**: 您可以之後隨時回來補充生成失敗的規格。
```

## 與其他 Phase 的整合

### 輸入依賴
- **Phase 3 (BRD)**: 提供 BRD `.opencode/ba-specs/{project}/brd/BRD.md` (必要)
- **Phase 1 (Analysis)**: 提供 BA 規格 `.opencode/ba-specs/{project}/` (參考)
- **Phase 2 (Meeting Doc)**: 提供會議記錄 (參考)

### 輸出供應
- **Phase 5 (Handoff)**: 所有規格作為交付物件

### 跳過/重複執行條件

```bash
# 檢查規格是否已存在
if [ -d ~/.opencode/ba-specs/{project-name}/{spec-type}/ ] || [ -f ~/.opencode/prd/{project-name}/PRD.md ]; then
  # 詢問使用者
  "檢測到 {spec-type} 規格已存在。是否要:
  1. 跳過此步驟，使用現有規格
  2. 重新生成規格 (覆蓋現有版本)
  3. 生成新版本並保留舊版 (v2)
  4. 補充生成其他類型規格"
fi
```

## 時間估算 (Time Estimates)

| 步驟 | 預估時間 |
|------|---------|
| BRD 驗證與分析 | 1-2 分鐘 |
| 使用者選擇規格類型 | 1-3 分鐘 |
| ba-analyst-skill 生成 | 10-20 分鐘 |
| prd-skill 生成 | 8-15 分鐘 |
| 驗證與狀態更新 | 1 分鐘 |
| **總計 (單一規格)** | **12-25 分鐘** |
| **總計 (多規格)** | **30-60 分鐘** |

*實際時間取決於專案複雜度、規格類型和 LLM 回應速度*

## 參考文件

- **BA Analyst Skill**: `~/.config/opencode/skills/ba-analyst-skill/SKILL.md`
- **PRD Skill**: `~/.config/opencode/skills/prd-skill/SKILL.md`
- **BRD Template**: `~/.config/opencode/skills/brd-writer-skill/templates/BRD_TEMPLATE.md`
- **Spec 格式範例**: `~/.config/opencode/skills/ba-analyst-skill/examples/`

---

*最後更新: 2026-02-06*
*Phase 狀態: COMPLETE*
