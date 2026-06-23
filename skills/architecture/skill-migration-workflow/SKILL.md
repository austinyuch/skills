---
name: skill-migration-workflow
description: 將外部 skill（如 ECC Claude Code skill、Anthropic quickstarts skill）遷移並合併到 opencode skill 的工作流。當使用者說「比較並更新 skill」「從 claude code 遷移 skill」「同步 skills 到 opencode」「更新 opencode skill」「把 ECC 的 skill 合進來」「盤點 skill 差異」或任何涉及 skill 來源比較、Gap 分析、opencode skill 更新的場景時使用。
---

# Skill Migration Workflow

將外部或新版 skill 遷移、比較並合併到 opencode `~/.config/opencode/skills/` 的標準工作流。

## 工作流程

### Phase 1：廣度盤點（先廣後深）

**目標**：快速識別所有候選 skill，建立 todo list，再逐個深入。

1. **列出來源 skill**
   ```bash
   ls <source-skills-dir>/
   ```

2. **列出目標 skill（opencode）**
   ```bash
   ls ~/.config/opencode/skills/
   ```

3. **找出同名交集**
   ```bash
   comm -12 <(ls <source> | sort) <(ls ~/.config/opencode/skills/ | sort)
   ```

4. **建立 TodoWrite 清單**：每個候選 skill 一條 todo，標記 pending

---

### Phase 2：逐 Skill 深度分析

針對每個候選 skill，依序完成：

#### 步驟 A：比較內容差異

同時讀取兩個版本：
```bash
# 行數比較（快速感知）
wc -l <source>/SKILL.md ~/.config/opencode/skills/<name>/SKILL.md

# 結構比對
diff <source>/SKILL.md ~/.config/opencode/skills/<name>/SKILL.md
```

#### 步驟 B：Gap 分析

評估以下面向：

| 面向 | 問題 |
|------|------|
| 章節缺失 | 新版有哪些 section 是舊版沒有的？ |
| 內容品質 | 新版是否有更清晰的說明、更好的範例？ |
| 觸發條件 | 新版的 `When to Activate` / `description` 是否更完整？ |
| 平台適配 | 新版是否需要調整 claude → opencode、.claude → .opencode 等路徑？ |

#### 步驟 C：Go/No-Go 決策

| 結論 | 條件 |
|------|------|
| ✅ GO（更新） | 新版有實質性新增內容（新 section、更完整的說明） |
| ❌ NO-GO（跳過） | opencode 版已包含所有新版內容，或 opencode 版更新 |
| ⚠️ 部分合併 | 各有優劣，選擇性取用新版的特定 section |

---

### Phase 3：執行更新

針對 GO 的 skill，進行更新。

#### 更新原則

1. **繁體中文優先**：所有說明文字改用繁體中文
   - 專有名詞保持英文：`SKILL.md`、`frontmatter`、`script`、`workflow`、框架名稱
   - 技術術語可保留英文：`function`、`class`、`variable`、`hook`
   - 路徑、指令、程式碼區塊保留英文

2. **平台路徑轉換**：
   ```
   ~/.claude/          → ~/.config/opencode/
   .claude/evals/      → .opencode/evals/
   claude Code session → OpenCode session
   Claude Code         → OpenCode（一般情境）
   ```

3. **保留 opencode 特有設定**：不覆蓋 opencode 版已有的 Hook 設定、Plugin 路徑等

4. **合併策略**：新增缺失的 section，不刪除 opencode 版已有的內容

#### 常見更新模式

**新增 When to Activate / 適用場景 section**（最常見的缺失）：
```markdown
## 適用場景

- [觸發情境 1]
- [觸發情境 2]
- [觸發情境 3]
```

**新增決策表格**（strategic-compact 類型）：
```markdown
## 決策指南

| 條件 | 建議 | 原因 |
|------|------|------|
| 情況 A | 動作 A | 理由 |
| 情況 B | 動作 B | 理由 |
```

**新增 What Survives 類型對照表**：
```markdown
## 資訊保留對照

| 保留 | 遺失 |
|------|------|
| 項目 A | 項目 X |
| 項目 B | 項目 Y |
```

---

### Phase 4：驗證

每個更新完成後確認：

- [ ] 繁體中文翻譯自然流暢
- [ ] 專有名詞維持英文
- [ ] 平台路徑已轉換（`.claude` → `.config/opencode`）
- [ ] 原有 opencode 版的特有設定未被覆蓋
- [ ] frontmatter 中的 `name` 和 `description` 正確

---

### Phase 5：建立遷移新 Skill（可選）

若來源目錄有 opencode 版完全沒有的 skill（非同名），評估是否需要使用 `claude-to-opencode-skill` 進行完整遷移。

---

## 快速決策矩陣

| 差異類型 | 處理方式 |
|---------|---------|
| 新版多了 `When to Activate` | 翻譯後補充到 opencode 版 |
| 新版多了決策表格 | 翻譯後補充 |
| 新版多了完整新 section | 翻譯後補充 |
| 兩版完全相同（僅格式差異）| NO-GO，跳過 |
| opencode 版更新（有 opencode 特有內容）| NO-GO，跳過 |
| 新版有 `.claude/` 路徑 | 遷移時轉換為 `.config/opencode/` |
| 新版有 `Claude Code` 字眼 | 視情境改為 `OpenCode` 或保留 |

## 輸出格式

完成後提供摘要報告：

```
## Skill 遷移摘要

### 已更新（GO）
- skill-name：補充 [描述變更]
- skill-name：大幅更新 [描述變更]

### 跳過（NO-GO）
- skill-name：opencode 版已更完整
- skill-name：內容完全相同

### 部分合併
- skill-name：取用新版的 [section 名稱]

---
總計：X 個 GO，Y 個 NO-GO，Z 個部分合併
```
