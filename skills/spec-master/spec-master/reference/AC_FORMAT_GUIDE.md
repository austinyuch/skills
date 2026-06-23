# Acceptance Criteria Format Guide

本文件定義 SDD Phase 1 產出的驗收標準 (AC) canonical format，供 AC parser 可靠提取，同時說明 legacy format 的向後相容策略。

---

## Canonical Format（新 spec 必須遵循）

```markdown
#### 驗收標準

1. 當[事件]時，那麼[系統]應該[響應]
2. 如果[前置條件]，那麼[系統]應該[響應]
3. [系統]應該[行為描述]
```

### 規則

| 元素 | 規定 | 說明 |
|------|------|------|
| Header | `#### 驗收標準` 或 `#### Acceptance Criteria` | 必須為四級標題（H4） |
| 列表格式 | 編號列表（`1.` `2.` `3.`） | 禁止 dash list (`-`) 或 bullet (`*`) |
| 項目格式 | 建議 EARS 格式 | When/If/While 開頭，但不強制 |
| 位置 | 緊接在需求用戶故事之後 | 每個 REQ 區塊各有獨立 AC 節 |

### 禁止的格式

- ❌ `**驗收標準**:` （bold inline header）
- ❌ `**Acceptance Criteria:**` （bold inline header）
- ❌ 使用 dash list (`- 當...`) 作為 AC 容器
- ❌ 使用三級標題 `### 驗收標準` 作為 AC header
- ❌ AC 項目混用編號與非編號列表

---

## Legacy Format 對照表

以下為跨專案取樣（8 projects, ~150+ specs）觀察到的既有格式。AC parser 應以 best-effort heuristic 處理這些格式，但新 spec 不得使用。

| 格式 | 出現率 | Parser 支援 | 範例 |
|------|--------|-------------|------|
| H4 + 編號列表（canonical） | ~85% | ✅ Primary target | `#### 驗收標準\n1. ...` |
| H3 + 編號列表 | ~5% | ⚠️ Best-effort | `### 驗收標準\n1. ...` |
| Bold inline + 編號列表 | ~3% | ⚠️ Best-effort | `**驗收標準:**\n1. ...` |
| FR-style（無獨立 AC 節） | ~5% | ❌ 無法提取 | AC 散落在需求描述中 |
| H4 + dash list | ~2% | ⚠️ Best-effort | `#### 驗收標準\n- ...` |

### Parser 優先順序

1. 精確匹配 H4 canonical header → 提取後續編號列表
2. Fallback: H3 variant → 提取後續編號列表
3. Fallback: Bold inline variant → 提取後續編號列表
4. Fallback: H4 + dash list → 轉換為編號列表後提取
5. 無法匹配 → 標記為 `AC_NOT_FOUND`，不做猜測

---

## Migration Guidance

### 何時 migrate

- **新 spec**：必須使用 canonical format，無例外。
- **既有 spec（active / in-progress）**：建議在下次編輯時順手升級，但不強制。
- **已完成 spec（completed）**：不需要 migrate，parser 以 best-effort 處理。

### 如何 migrate

1. 將 AC header 改為 `#### 驗收標準`（H4）
2. 將 dash list 改為編號列表
3. 確認每個 AC 項目獨立成行，不與其他內容混排

### 範例：Before → After

**Before（legacy bold inline + dash list）：**
```markdown
**驗收標準:**
- 系統應該在 3 秒內回應
- 錯誤時顯示友善訊息
```

**After（canonical）：**
```markdown
#### 驗收標準

1. 系統應該在 3 秒內回應。
2. 當發生錯誤時，系統應該顯示友善的錯誤訊息。
```
