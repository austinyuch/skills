---
name: frontend-designer
description: 整合的前端「設計 + 工程 + 視覺複核」domain expert。當使用者要設計前端 / 排版 / 視覺效果、實作 web UI（頁面、元件、landing、dashboard、artifact）、選用 shadcn / open-design / gstack / A2UI 產出並 render UI、或在 code review 時需要有人以前端專家身分審查 CSS/JS/HTML/JSX 與「畫面實際長怎樣」（含 Playwright 截圖、排版、階層、對比、無障礙、design-system/品牌一致性）時，都應使用此 skill——即使使用者只說「這個畫面很醜 / 很 AI / 排版怪怪的」「幫我把 UI 做好看」「這頁能不能過 design review」「幫我看看前端這段」。此 skill 是既有前端 / 設計 skills（frontend-design-skill、shadcn、brand-guideline-company、web-artifacts-builder、frontend-patterns、theme-factory、webapp-testing、uat-demo-agent）的 orchestrator 與 code-review 家族的前端 domain-expert sibling，不重造它們。也用在需要為 spec / code-review 補上「render 出來看一眼」的視覺複核 gate 時。
---

# Frontend Designer / Engineer

一個把「設計品味 → 前端實作 → 視覺複核」串成單一 workflow 的整合 skill。它存在的原因是：目前的 spec → implement → review 管線**全是文字 / AST，沒有任何一步真的 render 出來看**，而設計能力散在 8+ 個彼此重疊、又都是 optional 的 skill 裡，`code-review` 家族則**完全不審前端**（不看 CSS/HTML、不看畫面、不看無障礙、不查 design-system 一致性）。結果就是：一段語法乾淨、通過 security/test 的 React，畫面可能又醜又不符品牌又排版壞掉又不可無障礙，**而沒有任何 reviewer 會發現**。

本 skill 補上這個缺口。核心信念：**設計方法論 + anti-slop + a11y 是共用內核；shadcn / open-design / gstack-Pretext / A2UI 只是可選的 render target。**

## 三大職責（對應三個 phase）

| Phase | 職責 | 讀取 |
|---|---|---|
| **1. Design** | 設計前端、排版、視覺效果：建立 / 讀取 design system → tokens（CSS custom properties）→ layout；套用 craft 準則與 anti-slop | [references/design-phase.md](references/design-phase.md) |
| **2. Implement** | 執行前端實作：依情境選 render target（shadcn / open-design template / gstack-Pretext / A2UI），套 tokens、真實內容、responsive、dark mode、a11y | [references/implement-phase.md](references/implement-phase.md) |
| **3. Review** | 作為 `code-review` 的前端 domain expert：static（審 CSS/JS/HTML/JSX 對 design-system 的遵循）+ visual（render → 截圖 → 評 layout/階層/對比/品牌）+ a11y | [review-phase.md](references/review-phase.md)、[visual-probes.md](references/visual-probes.md)（render bridge + 可執行 probe code + 缺工具降級）、[anti-slop-checklist.md](references/anti-slop-checklist.md) |

三個 phase 不一定都跑：使用者要「設計 / 做 UI」就走 1→2；要「審前端」就走 3；要「從無到有且要過複核」就 1→2→3。

## 共用內核：先確立 design system，再動手

任何前端工作**之前**，先確立單一 design-system source of truth（避免每次重造品味、產生 AI slop）。優先序：

1. **既有 `DESIGN.md`**（gstack 慣例；若 repo 有就讀它，通常已被 `CLAUDE.md` 要求先讀）。
2. **公司 CIS** → 交給 `brand-guideline-company`（company 官方色 / 字 / logo / grid 為 authoritative）。
3. **open-design token 系統** → 讀 `~/projects/open-design/design-systems/<name>/{DESIGN.md,tokens.css}`（152 套品牌 token，直接採用其 hex / type / radius，不要自己發明）。
4. **都沒有** → 走 direction-pick：`frontend-design-skill`（aesthetic 方向）+ open-design `craft/*.md` + gstack 的品味 taxonomy，產出一份最小 design direction + tokens。

無論來源為何，**tokens 一律輸出成 CSS custom properties**，並套用共用 craft 準則（見 anti-slop-checklist）。資源實際路徑與消費方式見 [references/resources.md](references/resources.md)。

## Phase 2 — Render-target 決策樹（先選 target，再實作）

> A2UI ≠ gstack render：gstack 用 **Pretext**；A2UI 來自 openclaw / giant-orchestrator，是「agent 送 JSON message → renderer 畫出來」的協定。四者是**並列的 render target**，依情境選一。

```
需要什麼樣的前端產物？
├─ React app / 已有 components.json 的專案
│    → shadcn（元件組合 + design-system 規則）+ frontend-patterns（hooks/perf/forms/a11y）
│      複雜多元件 artifact → web-artifacts-builder（Vite+Tailwind+shadcn 打包成單檔）
├─ 單檔可攜 HTML（landing / prototype / 交付物），且有對應版型
│    → open-design design-templates/<shape>：填 schema.ts 的 inputs.json → npx tsx scripts/compose.ts（零 API key，placeholder 圖片）
├─ 單檔可攜 HTML，需要真實 line-break / reflow / contenteditable 重排
│    → gstack /design-html：Pretext-native HTML（vendor/pretext.js）
└─ agent 動態產生 / server 端 emit 的 UI（catalog-driven、可 patch）
     → A2UI：compose ServerMessage[]（createSurface→updateComponents→updateDataModel）
       render target 二選一：
         · React/shadcn renderer（giant_catalog.json，A2UI 元件名 → shadcn resolver）
         · Lit web-components renderer（@a2ui/lit，standard catalog）
```

細節、確切命令、A2UI message 形狀與 catalog 見 [references/implement-phase.md](references/implement-phase.md)。

## Phase 3 — 前端視覺複核 gate（本 skill 最關鍵的新增能力）

`code-review` 家族沒有任何一步 render UI。本 phase 就是那個缺失的 gate，作為 `code-review` 的前端 domain-expert sibling（與 `test-quality-reviewer` / `security-risk-reviewer` 同一個 pattern：提供 findings 餵給 review，**不自行下 PASS/FAIL**，`review.md` 仍是 verdict authority）。

當 review 觸及前端變更（`.css`/`.scss`/`.html`/`.jsx`/`.tsx`/`.vue`/`.svelte`/樣式或版型）時：

1. **Static 審查**：對照 design-system 規則——tokens 用 CSS var 而非 raw hex、shadcn 組合規則、font/AI-slop blacklist、a11y baseline（見 anti-slop-checklist）。
2. **Visual 審查（render → 截圖 → 評）**：用 `uat-demo-agent`（`uatdemo` Playwright binary）或 `webapp-testing` 把頁面 / 元件 render 出來截圖（page + 關鍵元件 + 多個 viewport），**Read 那張 PNG**，評 layout / 視覺階層 / 間距 / 對比 / 品牌一致性。本 skill 需自行補上：computed-CSS probe（Playwright `evaluate` 取 box-model/overflow）、multi-viewport、以及有 baseline 時的 pixel-diff。
3. **輸出**：結構化 findings（severity + 具體位置 + 建議），折進 review 的「程式碼品質 / 設計一致性」維度。

完整流程、Playwright 命令、findings 格式見 [references/review-phase.md](references/review-phase.md)。

## 調用既有 skills：Delegation Contract（Compose，不重造）

本 skill 是 orchestrator + 前端 domain expert，**不自帶**元件庫、截圖引擎或品牌資產；這些能力一律**透過 Skill tool 調用對應的 owning skill** 來完成。核心規則：**能調用該 skill 就調用它，不要在本 skill 內重寫它的細節，也不要把它的產出當成本 skill 自製。**

| 能力需求（觸發） | 調用（owning skill） | 該 skill 擁有什麼（attribution 對象） |
|---|---|---|
| React app / repo 有 `components.json` | `shadcn` | 元件 add/search/fix、semantic-token 規則、Field/InputGroup 組合、a11y Title |
| 前端工程 patterns（hooks/perf/forms/error boundary） | `frontend-patterns` | 前端工程慣例 |
| 複雜多元件 React artifact 打包成單檔 | `web-artifacts-builder` | Vite+Tailwind+shadcn → 單檔 HTML |
| B2B 供應鏈 PRD → 互動 HTML 原型（採購/庫存/物流；AT-UI/AntD/Element Plus） | `ui-skill` | 該 niche 的 PRD→HTML generator（CRUD/表單驗證/mock data）。**命中此 niche 時整段 delegate 回 `ui-skill`**，本 skill 只補 design-system / anti-slop 把關 |
| render 頁面/元件並截圖、抓 console/DOM | `webapp-testing`（或 `uat-demo-agent`） | Playwright 截圖 / 互動 / log（受 `local-infra-registry-governance` gate） |
| 公司 CIS（官方色/字/logo/grid） | `brand-guideline-company` | 品牌權威；在場時 supersede `theme-factory` |
| 從零建立 aesthetic 方向 | `frontend-design-skill` | distinctive 視覺方向（避免 generic AI 味） |
| fallback palette/font（無品牌/DESIGN.md 時） | `theme-factory` | 通用 palette/font |

（`canvas-design` 不列入：它只做靜態 PNG/PDF 藝術，與 web UI 不重疊；`uat-demo-agent` 是 `webapp-testing` 之外的 render+screenshot 後端，二者擇一。）

### open-design 設計 lens skills（path-reference / capability-gated）

以下設計 lens 來自 upstream `~/projects/open-design`（其 132-skill catalog）。**注意：opencode 的 skill loader 不會註冊 symlink 進來的 skill**（已用 `opencode debug skill` 驗證，symlink 目錄不進 registry），因此這些 open-design skills **不是**獨立的 Skill-tool registry 條目，而是以 **path-reference** 使用——需要時讀取 `~/projects/open-design/skills/<name>/SKILL.md` 並依其指引執行（即 Delegation Contract 的 `resource-fallback` 狀態）。upstream 為 source-of-truth；未 clone open-design 的機器視為 `unavailable`（三態降級，不得硬相依）。只列與前端設計相關的少數。

| 觸發 | open-design skill（讀其 SKILL.md by path） | 貢獻（attribution 對象） |
|---|---|---|
| Apple / native / HIG 風格 UI；design-review 要 HIG lens | `apple-hig` | Apple Human Interface Guidelines 遵循檢查 |
| Phase 1 從零定 aesthetic 方向 / decoration / motion taxonomy | `design-consultation` | 美學方向諮詢（本 skill design-phase 已按 path 引用，現可直接調用） |
| Phase 3 結構化設計複核清單 | `design-review` | design-review checklist lens（與本 skill Phase 3 findings 併用） |
| 挑色 / palette / 相鄰色可辨（配合 WCAG 對比） | `color-expert` | 色彩專業（補強 anti-slop §C 的對比門檻） |
| 高階創意方向 / brief 收斂 | `creative-director`、`design-brief` | 創意總監視角 + design brief 收斂 |

使用這些時走 `resource-fallback`（讀 upstream SKILL.md by path）或 `unavailable` 兩態，並在 `Composed via:` 標明來源（例：`Composed via: apple-hig(HIG) + color-expert(palette)`）。若要讓某個 open-design skill 成為 opencode registry 中可被 Skill tool 直接調用 / 自動觸發的正式條目，需在 skill home 放一個**真實 wrapper stub 目錄**（一個薄 `SKILL.md`，body 指向 upstream path 並要求讀取執行；**symlink 無效**）——預設不做，避免每個 registry 條目的 always-in-context 描述稅；需要時再逐一加。

### 獨立性（三態降級）

被組合的 skill 缺席時，本 skill 仍必須能獨立完成核心工作——**design 內核 + anti-slop + a11y baseline 是本 skill 自帶的**，不依賴任何 sub-skill。每個借用能力落在三態之一，並在輸出誠實標記：

- `invoked` — owning skill 在場 → 透過 Skill tool 調用它，由它執行。
- `resource-fallback` — 無法直接調用、但其資源路徑可讀 → 讀資源自己完成，標明來源 skill。
- `unavailable` — 皆無 → 用本 skill 內核最小完成，於輸出明記「以 fallback 完成、未經 `<skill>` 驗證」，**不得**宣稱已達該 skill 的品質。

### Attribution（每次產出 / 複核必附）

產出 UI 或給 review findings 時，附一行 **`Composed via:`**，記錄實際調用了哪些 skill、各自貢獻什麼（例：`Composed via: shadcn(元件規則) + webapp-testing(截圖) + brand-guideline-company(CIS token)`）。截圖、findings、打包產物須**註明來源 skill**。借來的能力不得當成本 skill 自製——能力 attribution 不實＝overclaim（對齊 CLAUDE.md 的 anti-overclaim 治理）。

## Guardrails

- **Delegation-first，不重造**：本 skill 是 orchestrator + 前端 domain expert；owning skill 在場就調用它（見上方 Delegation Contract），不要內嵌其細節或把其產出佔為己有。
- **獨立可跑**：任何 sub-skill 缺席都不得讓本 skill 失效；用三態降級誠實完成並標記。
- **tokens 一律 CSS custom properties**，禁止散落 raw hex / 魔術數字；有品牌 / DESIGN.md 就必須採用其 token。
- **anti-slop 為硬規則**：font blacklist、AI-slop blacklist、a11y baseline（AA 對比、ARIA、focus-visible、reduced-motion、responsive）不可妥協。見 anti-slop-checklist。
- **Review 不下 verdict**：Phase 3 只提供 findings；`review.md` / `code-review` 仍是 authority（與 `security-risk-reviewer` 同）。
- **Playwright 受 gate**：Phase 3 若要起本地 runtime，遵守 `local-infra-registry-governance`；截圖 render 屬 read-only observation，不要亂改被審 repo。
- **Attribution 不可省**：每次產出附 `Composed via:` 行；借來能力誠實標記三態，不得 overclaim。
- **迴向上游**：若要把本 skill 正式**接進 `code-review` 家族**（讓 code-review 自動把前端 domain expert 當 sibling input），該 `code-review` 變更的 source-of-truth 在 `~/projects/aclab/aclab-code-review-private/`，必須迴向該 repo 的適當位置，不可只改本 workspace 的 vendored 副本。
- **A2UI 三種方言**：Google standard（Lit）、Giant v0.10（React/shadcn，`giant_catalog.json`）、go-cms-ai-site 的 `uiType`/`mutationVariables`。**先選 renderer，再對該 renderer 的 exact catalog compose**。
