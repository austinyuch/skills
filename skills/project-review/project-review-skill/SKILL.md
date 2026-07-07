---
name: project-review-skill
description: 為當前 workspace 專案生成高階管理者用的產品介紹與 CEO/founder-depth project review HTML 文件。當使用者說「幫我做專案簡報」「生成產品介紹文件」「建立 review 文件」「給主管看的文件」「product review」「executive summary」「value proposition 文件」「Amazon PR FAQ」「給高管看」「投資人簡報」「管理層報告」「CEO perspective」「founder review」「全專案 review 深度」，或任何涉及向高階管理者/外部受眾介紹專案價值、策略判斷、產品 thesis、投資/暫緩決策，且需要誠實呈現 live-demo readiness / mock-vs-real evidence 邊界的場景，都應啟動此 skill。
---

# Project Review Skill — 高階管理者產品介紹文件生成器

## 目標

分析當前 workspace 的專案內容，生成一份精美的 HTML 文件，包含：

- 價值主張（內部管理者 + 外部客戶雙視角）
- CEO / founder perspective（產品 thesis、策略賭注、10-star gap、投資決策）
- Amazon style backwards PR/FAQ
- UX flow 視覺化
- 核心功能截圖或示意圖
- Gap 盤點（現有缺口 + 已修復項目）

輸出固定路徑：`docs/review/index.html`

---

## Phase 1：探索專案內容

**前置作業 (Pre-flight Check)**:
強制檢查當前 workspace 是否存在專案專屬的 `docs/PROJECT_REVIEW_GUIDE.md` (或其他形式的生成規範)。
- 每個專案 (Workspace) **建議**維護一份專屬的 Review 規範文件，定義該專案特有的價值主張重點、關鍵競爭對手、高階主管關注的指標與特殊的截圖需求。

### 前置規則：Canonical Scenario 與 Review Evidence

- Review 截圖與示範資料不得依賴 `temp/`、單次 session 產物、或行內常數；若某個業務情境會被重複拿來做 review / manual / demo / e2e，必須沉澱成 **canonical scenario**。
- 真實截圖流程應透過 helper / adapter 層讀取 canonical scenario，而不是在每個 review 腳本中各自維護一份資料。
- 專案級 review guide 應記錄具體的啟動命令、截圖輸出目錄、樣本資料位置與驗證步驟；global skill 僅定義這種分層原則。
- 💡 **原因 (WHY)**：讓 review 文件可重現、可驗證，並避免因為多份樣本資料版本不一致而導致 evidence 漂移。

### 前置規則：Readiness Claim Cap

- `project-review-skill` **不自行裁決** 某功能是否真正 demo-ready；它必須優先讀取 `.agents/specs/**/review.md`、`SPECS.md`、或其他已存在的 review evidence 摘要，沿用其中的 `Live-Demo Readiness`、`Coverage Tier`、`Evidence Source`。
- `RTM.md` 若存在，只可作為 cross-spec traceability / verification context；不得被當成 readiness authority 或取代 `review.md`。
- 若 readiness/evidence 欄位不存在，必須把對應功能或畫面標示為 `not_assessed`，並視情況附上 `DEMO_NOT_ASSESSED` 或 `ARTIFACT_HONESTY_GAP`，而不是自行腦補成 ready。
- executive artifact 的責任是 **claim cap**：限制對外措辭。凡是 mock-backed / illustrative / fixture-backed evidence，應優先使用 `MOCK_DOMINANT_EVIDENCE`、`ARTIFACT_HONESTY_GAP`、或 `AUTH_FIXTURE_COUPLING` 等 canonical codes 來標示風險，而不是只用模糊形容詞。
- warning code 與 evidence label 命名請與共用 taxonomy 對齊：`../../docs/DEMO_RISK_WARNING_TAXONOMY.md`。
- `project-review-skill` **不得**根據 task 完成度、task counters、`NEXT_STEPS.md` 的 execution hint、或 RTM progress 摘要去推導 readiness verdict。若缺少 authoritative evidence，它只能保守降級，而不能補推論。

### 前置規則：System Architecture Documentation

- 當 project-level architecture / steering 文件需要建立、刷新、stale/overclaim 判斷、或需要給 `code-review` 的高階 Architecture Context Packet 時，應使用 `system-architect`；`project-review-skill` 只消費其輸出並做 claim cap。
- Project review 必須檢查是否存在 project-level system architecture steering 文件：`.agents/steering/product.md`、`.agents/steering/tech.md`、`.agents/steering/structure.md` 與同名 HTML，或 `docs/PROJECT_REVIEW_GUIDE.md` / `AGENTS.md` 宣告的等價路徑。
- 若不存在，必須根據 `skills/spec-driven-development/references/system-architecture-lifecycle.md` 與 `system-architect` 判斷狀態：`missing_but_required` 或 `not_yet_required`。只有當 repo 已有足夠 accepted design/review evidence 時，才建立或建議建立；不要為 prototype-only 或 evidence-thin repo 捏造完整架構。
- 若存在，project review 應讀取 architecture markdown/HTML 作為 human-facing architecture narrative，但必須用 `.agents/specs/**/design.md`、`review.md`、`SPECS.md`、`RTM.md`、與 evidence metadata 做 claim cap。
- Architecture review 應採用 SAA good parts vocabulary：common user access / common programming interface / common communications support / cross-platform consistency；同時明確保留 Agile/YAGNI boundary，避免把 project review 寫成 big-upfront architecture blueprint。
- 若 architecture docs 比 source evidence 更樂觀，標示 `stale_or_overclaiming`，並在 HTML review 中顯示 gap / warning；不得把 stale architecture diagram 當成已驗證系統狀態。

從以下來源蒐集專案資訊（並行讀取，不存在的跳過）：

```text
docs/PROJECT_REVIEW_GUIDE.md     ← 專案專屬的 review 生成與高階報告規範
README.md / README_*.md          ← 主要功能描述、安裝方式
AGENTS.md                        ← agent 架構、工作流程、重要文件位置
docs/*FEATURE*.md                ← 功能清單文件
docs/*SPEC*.md                   ← Spec清單文件
.agents/steering/product.md / tech.md / structure.md 與同名 HTML ← 系統架構 steering 文件（若存在；作為 narrative input，不是 readiness authority）
docs/architecture.md / docs/architecture/index.md / docs/architecture/index.html ← legacy/equivalent 系統架構文件（若存在；作為 narrative input，不是 readiness authority）
.agents/specs/SPECS.md           ← 主要 Spec 清單與設計
docs/**/*.md                     ← 詳細文件
.kiro/specs/**/*design*.md       ← 設計規格
.{agents,opencode,kiro}/specs/**/*design*.md   ← OpenCode 規格
specs/**/*.md                    ← 通用規格
RELEASE_NOTES.md / CHANGELOG.md  ← 版本歷史、新功能
```

並執行：

```bash
git log --oneline -50             # 了解開發歷程與 commit 風格
git log --oneline --since="30 days ago" --name-only  # 近期活躍功能
```

若使用者要求 CEO perspective、founder review、全專案 review 深度，或專案 review 需要超越一般功能介紹，必須讀取 `references/gstack-ceo-perspective.md`，並把其中的 Founder Thesis、Strategic Bet Map、10-Star Gap Analysis、Decision Memo 納入內容架構。gstack / Garry Tan 的方法論 attribution 保留在本 skill bundle 的 `README.md` 與 reference 文件中；生成的專案 review HTML 不需要輸出這段 citation，除非使用者在該次產出中特別要求。

**語言偵測**：以 README.md 主要語言決定文件語言（繁體中文 / English）。

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
| **已知缺口** | TODO、NEXT_STEPS、specs 中的 ⏳ 標記 | 尚未完成的功能；`NEXT_STEPS` 只可提供 backlog / gap hint，不可作為 readiness 或 completion authority |

若啟用 CEO / founder perspective，額外產生：

| 資訊維度 | 來源 | 說明 |
|----------|------|------|
| **Founder Thesis** | README、產品文件、spec、使用者 request | wedge、痛點、目標使用者、致命假設 |
| **Strategic Bet Map** | review evidence、spec、git log、docs | 每個策略賭注的 evidence、confidence、kill/risk signal、next proof |
| **Scope Mode** | `references/gstack-ceo-perspective.md` | `EXPAND` / `SELECTIVE_EXPAND` / `HOLD_SCOPE` / `REDUCE` |
| **10-Star Gap** | specs、UX evidence、readiness evidence、operational docs | execution/product/operating/strategic gaps |
| **Decision Memo** | 以上分析 | `Invest` / `Hold and harden` / `Narrow the wedge` / `Pause` |

CEO / founder perspective 不可覆蓋 evidence discipline：若 evidence 只支撐假設，必須寫成 thesis / bet / next proof，不得寫成已驗證成果。

### 2b. 服務啟動與截圖

按以下順序嘗試，失敗立即進入下一層：

**Registry-first preflight**:

- 若需要真實啟動 local backend / frontend / worker / database 來產生 review evidence，必須先遵守 `local-infra-registry-governance`。
- 不可直接根據 README 指令猜測 localhost ports、compose stack names、或自行決定重用既有 local env。
- 若當前 workspace 已有 registry-governed env allocation，才可在該 allocation 內執行啟動與截圖；若 allocation 不明或 tool 缺失，應停止真實截圖並進入 fallback evidence 流程。
- 若 exact instance 不存在但同 project 有多個 plausible candidates，必須先列出 instances 做 developer HITL selection 或明確新建，不能自行挑一個最像的。
- 若相關 spec 的 `Live-Demo Readiness != PASS`，仍可生成 review artifact，但功能 claim 必須降級，且頁面中需有可見標示（例如 `DEMO_NOT_ASSESSED`、`CROSS_SPEC_DEMO_DEPENDENCY`），不得讓高階主管誤以為該功能已經過真實整合驗證。

**層級 1：Playwright 真實截圖**

1. 先確認是否真的需要 live local infra；若只是靜態頁面或已有既有 evidence，不要多啟一套服務
2. 透過 `local-infra-registry-governance` 查詢 / bootstrap-register / request / reuse 合法 env allocation
3. 僅在 allocation 已明確時，才從 README 或專案 guide 提取對應啟動指令並進入該 governed env
4. 等待最多 30 秒確認 required service bundle 在已分配的 runtime context 內可用（不要把 `ss -tlnp` 當成 allocation authority）
5. 用 Playwright 截取：首頁、主要功能頁、最多 4 張截圖
6. 截圖儲存至 `docs/review/assets/screenshot-*.png`
7. 截圖對照: 說明截圖與實際功能, 如果有差異應該紀錄下來. 

對每個 feature card / screenshot，必須同步產生以下 evidence metadata（直接顯示在 HTML 中，而不是只留在生成過程）：

- `Evidence Source`: `live_screenshot` | `fixture-backed screenshot` | `css_illustration` | `static_placeholder`
- `Coverage Tier`: `full-integration` | `hybrid` | `mock-heavy` | `not_assessed`
- `Readiness State`: `PASS` | `CONDITIONAL` | `FAIL` | `not_assessed`
- `Source Ref`: 對應的 `review.md` / `SPECS.md` / guide 路徑
- `Fallback Reason`：只有在不是 `live_screenshot` 時才顯示

`{{FEATURES_HTML}}` 的實際結構、badge mapping、以及 disclaimer 規則，必須遵守 `./code/FEATURES_HTML_CONTRACT.md`，不可只靠 agent 即興決定。
共用 evidence 欄位語意與 claim-cap 邊界，請對照 `../../docs/EVIDENCE_METADATA_CONTRACT.md`。

若當前 evidence 不是 `live_screenshot`，功能描述必須採用較保守措辭，並搭配 canonical code（例如 `MOCK_DOMINANT_EVIDENCE` 或 `DEMO_NOT_ASSESSED`），而不是 `validated in live demo`。

若功能涉及登入、SSO、session refresh、RBAC、impersonation、或任何需要 auth context 的畫面，截圖前必須額外確認 auth state 來源：
- 是真實 auth flow / 真實 token / 真實 demo account
- 還是 storageState / fixture / 預先注入的 session

若是後者，必須明確標記 `AUTH_FIXTURE_COUPLING`，不要只寫等價說明。

若 review 聲稱具備 BI / dashboard / chart 能力，不能只驗證圖表容器存在；必須驗證圖表真的渲染出資料（例如 canvas 已出現且非錯誤狀態）。空白 chart shell、builder 容器或 shared page 骨架都不應作為 chart evidence。

**層級 2：CSS 精美示意圖（fallback）**
若 governed runtime unavailable、啟動失敗、或無法安全確認 allocation / port ownership，為每個核心功能生成一張**視覺精緻的 CSS/SVG 示意圖**，需包含：

- 功能名稱、圖示（emoji 或 SVG icon）
- 2-3 個說明點（bulleted）
- 配色符合 Corporate Identity System 或專案主題色
- 不得使用純色矩形佔位，必須設計感強烈

示意圖以 inline HTML 直接嵌入 feature card，不依賴外部圖片檔。

但每張示意圖都必須附上顯眼標示：`Illustrative Only — live runtime unavailable`，並同步標記 `DEMO_NOT_ASSESSED` 或 `ARTIFACT_HONESTY_GAP`（依情境）與 `Fallback Reason`。這個 fallback 只可補足版面與說明，不可被包裝成真實 evidence。

### 2c. Gap 自動剖析

從以下來源自動提取 Gap 資訊（不詢問使用者）：

```bash
# 搜尋尚未完成的標記（僅作 gap hint，不作 readiness authority）
grep -r "⏳\|TODO\|FIXME\|NEXT_STEPS\|WIP\|pending\|計劃中\|待實作" \
  README.md NEXT_STEPS.md docs/ .kiro/specs/ specs/ 2>/dev/null

# 從 git log 找最近被標記為 fix 但可能殘留的問題
git log --oneline --since="90 days ago" | grep -i "fix\|hotfix\|patch\|workaround"
```

**分類邏輯**：

- ✅ **已修復** — 來自 RELEASE_NOTES 的「已解決」、git log 中 `fix:` commit、README 中帶 ✅ 的項目
- ⏳ **待解決** — `⏳`/`TODO`/`NEXT_STEPS` 標記、README 中 `Coming Soon`/`Planned`、spec 中尚未完成的 task

此外必須額外 cross-check：若某項功能在 `SPECS.md` 中有 `Open Change Requests`、`CROSS_SPEC_DEMO_DEPENDENCY`、或 `Live-Demo Readiness != PASS`，不可把它寫成已完整落地的 value proof；應在 Gap Analysis 或 feature disclaimer 中誠實揭露。

注意：這個 cross-check 只可消費 authoritative evidence / registry summary。`NEXT_STEPS.md` 只能提供 backlog / gap hint，不可作為 readiness authority，也不可從 task progress、`NEXT_STEPS.md`、或 RTM count 類訊號反推 readiness。

每個 gap 條目包含：標題、簡短描述、嚴重程度（High/Medium/Low）。

若啟用 CEO / founder perspective，Gap Analysis 必須升級為 10-star gap analysis，至少分類：

- **Execution gaps** — bugs、缺測試、mock-heavy paths、readiness blockers、未完成 integrations
- **Product gaps** — 缺 workflow、使用者價值不清、差異化不足、UX state coverage 不足
- **Operating gaps** — observability、rollout、support、docs、ownership、維護成本
- **Strategic gaps** — wedge 不清、demand proof 弱、distribution path 不明、adoption signal 缺失

這些分類仍需保留原本的 evidence / readiness labels，不能把管理層敘事包裝成 proof。

### CEO / Founder Perspective Sections

當 `references/gstack-ceo-perspective.md` 被啟用時，HTML 必須包含或等價整合以下內容：

1. **Founder Thesis** — wedge、痛點、current workaround、致命假設、需求證據。
2. **Strategic Bet Map** — 表格列出 Bet、Evidence、Confidence、Kill/Risk Signal、Next Proof。
3. **Scope Mode** — `EXPAND` / `SELECTIVE_EXPAND` / `HOLD_SCOPE` / `REDUCE`，並用 2-3 句說明原因。
4. **10-Star Gap Analysis** — 區分 execution/product/operating/strategic gaps。
5. **Decision Memo** — `Invest` / `Hold and harden` / `Narrow the wedge` / `Pause`，附 top 3 next actions 與 evidence limits。

若以上任何欄位缺少 repo evidence，標示為 `Open Question` 或 `Assumption`，並提出下一個驗證動作。

### Amazon Backwards Press Release（反向新聞稿）

以「今天宣布」的語氣，站在**產品已經成功**的未來視角撰寫：

```
標題：[公司名] 宣布推出 [產品名]，讓 [目標用戶] 能夠 [核心價值]

[城市]，[日期] —— [公司名] 今天宣布推出 [產品名]，
這是一個 [一句話描述價值主張]。

[引用：虛擬 CEO/PM 的話，說明為什麼這個產品重要]

[問題段落：目前用戶面臨的痛點]

[解決方案段落：產品如何解決這些問題]

[功能段落：2-3 個核心功能的簡要說明]

[可用性：如何取得/使用]
```

### FAQ（常見問題）

針對兩種受眾各寫 3-4 個問題：


**內部管理者 FAQ**（ROI、維護成本、安全性）：

- Q: 這個系統需要多少人力維護？
- Q: 導入後預計可節省多少時間/成本？
- Q: 資安合規性如何確保？

**外部客戶/投資人 FAQ**（功能、差異化、路線圖）：

- Q: 與市面上其他方案相比，差異在哪？
- Q: 支援哪些整合？
- Q: 未來 6 個月的發展路線圖是什麼？

**使用者 FAQ** 

- Q: 系統導入前以及導入後預計可達成什麼降本增效? 改善什麼痛點(if exists)?


### UX Flow

用 Mermaid 語法描述使用者主要操作流程，轉換為 HTML 內嵌 SVG（或使用 Mermaid.js CDN 渲染）。

---

## Phase 4：生成 HTML 文件

參考 `code/report-template.html` 作為 HTML 骨架。套用以下設計規範：

**the organization CIS 品牌色彩**（若為 組織相關專案）：

- 主色：`#005EB8`（Primary Blue）
- 輔色：`#04A9FB`（Blue Skies）
- 強調：`#FF6A39`（Orange Sunset）
- 正向：`#97D700`（Green Fields）
- 文字：`#3B4559`（Neutral Grey）

**通用設計原則**：

- 深色英雄區塊（`#0a0e1a` 漸層）搭配白色標題
- 卡片式功能展示，微陰影效果
- 統計數字大字顯示（功能數量、覆蓋率、版本等）
- 截圖以圓角卡片呈現，搭配說明文字
- RWD 友好，支援列印

**必含區塊**（依序）：

1. **Hero** — 專案名稱、一句話定位、關鍵指標（3個數字統計）
2. **Value Proposition** — 內部 vs 外部雙視角價值卡片
3. **CEO / Founder Perspective** — Founder Thesis、Strategic Bet Map、Scope Mode、Decision Memo（若未啟用 gstack reference，可省略或改為一般 strategy summary）
4. **Press Release** — Amazon backwards PR
5. **FAQ** — 雙受眾 FAQ accordion
6. **Core Features** — 功能卡片 + 截圖/示意圖
7. **UX Flow** — 流程圖（Mermaid 或 SVG）
8. **Gap Analysis** — 已修復 ✅ vs 待解決 ⏳ 清單；若啟用 CEO perspective，改為 10-star gap analysis
9. **Roadmap** — 近期里程碑時間軸
10. **Footer** — 生成時間、版本、來源

確保生成後將路徑告知使用者：`docs/review/index.html` 已生成，可用瀏覽器直接開啟。
