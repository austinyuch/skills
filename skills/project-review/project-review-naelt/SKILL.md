---
name: project-review-naelt
description: 為當前 workspace 專案生成 NAELT (生命權平等協會) 高階管理者與倡議報告用的 HTML 文件。當使用者說「幫我做專案簡報」「生成產品介紹文件」「建立 review 文件」「給主管看的文件」「product review」「executive summary」「value proposition 文件」「Amazon PR FAQ」「給高管看」「捐款人報告」「夥伴簡報」「倡議成果報告」「管理層報告」，或任何涉及向 NGO/倡議組織高階管理者、合作夥伴、捐款人或公眾受眾介紹專案價值的場景，都應啟動此 skill。
---

# Project Review Skill — NAELT 高階管理者與倡議報告生成器

## 目標

分析當前 workspace 的專案內容，生成一份精美的 HTML 文件，包含：
- 價值主張（內部管理者 + 外部倡議受眾雙視角）
- Amazon style backwards PR/FAQ
- UX flow 視覺化
- 核心功能截圖或示意圖
- Gap 盤點（現有缺口 + 已修復項目）

輸出固定路徑：`docs/review/index.html`

**品牌邊界**：本 skill 的 NAELT 視覺與語氣設定依據 `brand-guidelines-naelt` 的 site-derived guidance，不應視為正式官方 CIS 手冊。

---

## Phase 1：探索專案內容

### 前置規則：Readiness Claim Cap

- `project-review-naelt` **不自行裁決** 某功能是否真正 demo-ready；它必須先以 active root 下的 `{.agents, .kiro, or .claude}/specs/SPECS.md` 與 `RTM.md`（若存在）決定 checklist 範圍，再回到 `{.agents, .kiro, or .claude}/specs/**/review.md` 或其他已存在的 review evidence 摘要，沿用其中的 `Live-Demo Readiness`、`Coverage Tier`、`Evidence Source`。`RTM.md` 只能提供 checklist / traceability context，不可提供 readiness authority。本專案目前以 `.agents` 為主。
- `RTM.md` 若存在，只可作為 cross-spec traceability / verification context 與 requirement-feature-scenario/e2e-evidence-business-value checklist bridge；不得被當成 readiness authority 或取代 `review.md`。
- 若 readiness/evidence 欄位不存在，必須把對應功能或畫面標示為 `not_assessed`，並視情況附上 `DEMO_NOT_ASSESSED` 或 `ARTIFACT_HONESTY_GAP`，而不是自行腦補成 ready。

從以下來源蒐集專案資訊（並行讀取，不存在的跳過）：

```
README.md / README_*.md          ← 主要功能描述、安裝方式
AGENTS.md                        ← agent 架構、工作流程
{.agents, .kiro, or .claude}/specs/SPECS.md         ← active specs registry（先決定盤點範圍）
{.agents, .kiro, or .claude}/specs/RTM.md           ← requirement-feature-scenario/e2e-evidence-business-value checklist bridge（若存在）
docs/*FEATURE*.md                ← derived / convenience / discovery feature 文件（不可當 authority）
docs/**/*.md                     ← 詳細文件
{.agents, .kiro, or .claude}/specs/**/*design*.md   ← 設計規格（active root / supported roots；本專案目前以 `.agents` 為主）
specs/**/*.md                    ← 通用規格
RELEASE_NOTES.md / CHANGELOG.md  ← 版本歷史、新功能
```

並執行：
```bash
git log --oneline -50             # 了解開發歷程與 commit 風格
git log --oneline --since="30 days ago" --name-only  # 近期活躍功能
```

**語言偵測**：以 README.md 主要語言決定文件主語言；若需 English 版本，需同步將 template 的固定文案與 section labels 一併翻譯。

在建立 review checklist 時，必須先用 `SPECS.md` + `RTM.md` 決定 feature / scenario / evidence / business value 範圍；`docs/*FEATURE*.md` 只能拿來做 grouping 或對外敘事補充，不可直接當盤點 authority。

---

## Phase 2：分析並建構內容架構

### 2a. 提取關鍵資訊

從探索結果中識別：

| 資訊維度 | 來源 | 說明 |
|----------|------|------|
| **核心功能列表** | README 的功能章節、AGENTS.md | 3-7 個主要功能 |
| **技術架構** | 目錄結構、AGENTS.md、specs | 服務、模組、資料流 |
| **目標用戶** | README 介紹段落 | 誰在用、解決什麼問題 |
| **版本進展** | RELEASE_NOTES / git log | 已完成里程碑 |
| **已知缺口** | TODO、NEXT_STEPS、specs 中的 ⏳ 標記 | 尚未完成的功能 |

### 2b. 服務啟動與截圖

按以下順序嘗試，失敗立即進入下一層：

**層級 1：Playwright 真實截圖**
1. 若需要真實截圖，先遵守 `local-infra-registry-governance`，確認 governed runtime allocation、ownership、與 required service bundle readiness。
2. 只能在 governed runtime 已就緒時，用 Playwright 截取：首頁、主要功能頁、最多 4 張截圖。
3. 截圖儲存至 `docs/review/assets/screenshot-*.png`。

**層級 2：CSS 精美示意圖（fallback）**
若啟動失敗或無法偵測 port，為每個核心功能生成一張**視覺精緻的 CSS/SVG 示意圖**，需包含：
- 功能名稱、圖示（emoji 或 SVG icon）
- 2-3 個說明點（bulleted）
- 配色符合 NAELT 品牌色 (參考 brand-guidelines-naelt)
- 不得使用純色矩形佔位，必須設計感強烈

示意圖以 inline HTML 直接嵌入 feature card，不依賴外部圖片檔。

### 2c. Gap 自動剖析

從以下來源自動提取 Gap 資訊（不詢問使用者）：

```bash
# 搜尋尚未完成的標記
grep -r "⏳\|TODO\|FIXME\|NEXT_STEPS\|WIP\|pending\|計劃中\|待實作" \
  README.md NEXT_STEPS.md docs/ {.agents,.kiro,.claude}/specs/ specs/ 2>/dev/null

# 從 git log 找最近被標記為 fix 但可能殘留的問題
git log --oneline --since="90 days ago" | grep -i "fix\|hotfix\|patch\|workaround"
```

**分類邏輯**：
- ✅ **已修復** — 來自 RELEASE_NOTES 的「已解決」、git log 中 `fix:` commit、README 中帶 ✅ 的項目
- ⏳ **待解決** — `⏳`/`TODO`/`NEXT_STEPS` 標記、README 中 `Coming Soon`/`Planned`、spec 中尚未完成的 task

每個 gap 條目包含：標題、簡短描述、嚴重程度（High/Medium/Low）。

### Amazon Backwards Press Release（反向新聞稿）

以「今天宣布」的語氣，站在**產品已經成功**的未來視角撰寫：

```
標題：[公司名] 宣布推出 [產品名]，讓 [目標用戶] 能夠 [核心價值]

[城市]，[日期] —— [公司名] 今天宣布推出 [產品名]，
這是一個 [一句話描述]。

[引用：虛擬 CEO/PM 的話，說明為什麼這個產品重要]

[問題段落：目前用戶面臨的痛點]

[解決方案段落：產品如何解決這些問題]

[功能段落：2-3 個核心功能的簡要說明]

[可用性：如何取得/使用]
```

### FAQ（常見問題）

針對兩種受眾各寫 3-4 個問題：

**內部管理者 FAQ**（維護成本、安全性、倡議效益）：
- Q: 這個系統需要多少人力維護？
- Q: 導入後預計可節省多少時間/成本？
- Q: 資安合規性如何確保？

**外部倡議受眾/捐款人 FAQ**（功能、差異化、路線圖）：
- Q: 與市面上其他方案相比，差異在哪？
- Q: 支援哪些整合？
- Q: 未來 6 個月的發展路線圖是什麼？

### UX Flow

用 Mermaid 語法描述使用者主要操作流程，轉換為 HTML 內嵌 SVG（或使用 Mermaid.js CDN 渲染）。

---

## Phase 4：生成 HTML 文件

參考 `code/report-template.html` 作為 HTML 骨架。套用以下設計規範：

**NAELT 品牌色彩**（參考 brand-guidelines-naelt）：
- 主色：`#C53030`（NAELT Red）
- 輔色：`#4A5568`（NAELT Gray）
- 強調：`#DD6B20`（NAELT Orange）
- 狀態色：`#97D700`（僅用於完成 / 正向狀態，不視為 NAELT 官方品牌色）
- 文字：`#1A202C`（NAELT Dark）

**通用設計原則**：
- 深色英雄區塊（紅色漸層）搭配白色標題
- 卡片式功能展示，微陰影效果
- 統計數字大字顯示（功能數量、覆蓋率、版本等）
- 截圖以圓角卡片呈現，搭配說明文字
- RWD 友好，支援列印

**必含區塊**（依序）：
1. **Hero** — 專案名稱、一句話定位、關鍵指標（3個數字統計）
2. **Value Proposition** — 內部 vs 外部雙視角價值卡片
3. **Press Release** — Amazon backwards PR
4. **FAQ** — 雙受眾 FAQ accordion
5. **Core Features** — 功能卡片 + 截圖/示意圖
6. **UX Flow** — 流程圖（Mermaid 或 SVG）
7. **Gap Analysis** — 已修復 ✅ vs 待解決 ⏳ 清單
8. **Roadmap** — 近期里程碑時間軸
9. **Footer** — 生成時間、版本、來源

確保生成後將路徑告知使用者：`docs/review/index.html` 已生成，可用瀏覽器直接開啟。
