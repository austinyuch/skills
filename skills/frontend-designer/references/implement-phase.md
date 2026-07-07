# Phase 2 — Implement（執行前端實作）

先用 SKILL.md 的決策樹選一個 **render target**，再照下面對應段落實作。所有 target 共通要求：套用 Phase 1 的 tokens（CSS vars）、真實內容（禁 lorem ipsum）、responsive、`prefers-color-scheme` dark、`prefers-reduced-motion`、a11y（見 anti-slop-checklist）。路徑見 [resources.md](resources.md)。

> **先判 niche delegation**：若任務其實是 **B2B 供應鏈 PRD → 互動 HTML 原型**（採購/庫存/物流、AT-UI/AntD/Element Plus、CRUD/表單驗證/mock data），這是 `ui-skill` 的本業 → **透過 Skill tool 整段 delegate 回 `ui-skill`**，本 skill 只在其產出上補 design-system / anti-slop / a11y 把關。其餘一般 web UI 才走下面的 render target。依 SKILL.md 的 Delegation Contract，凡調用了 sub-skill，收尾在 `Composed via:` 行標明。

## Target A — shadcn / React（專案有 `components.json` 或要做 React app）

主力：**透過 Skill tool 調用 `shadcn`**（元件組合 + design-system 規則）+ `frontend-patterns`（hooks / perf / forms / error boundary / a11y keyboard-focus）；本 skill 不重寫這兩者的細節，只負責把 Phase 1 tokens 餵進去並做 anti-slop 把關。`shadcn` 在場即 `invoked`；缺席時退到 `resource-fallback`（讀其 `rules/*` 自己套用），並在輸出標明。

- 用 shadcn CLI 加元件；遵守其 `rules/*`：**semantic token（禁 raw `bg-blue-500`）**、Field/InputGroup 組合、必要 a11y Title/`sr-only`。
- 把 Phase 1 tokens 映到 shadcn 的 CSS 變數（`--background`/`--foreground`/`--primary`…），不要在元件裡寫死顏色。
- 複雜、多元件、要 state/routing 的 claude.ai artifact → `web-artifacts-builder`（Vite+Tailwind+shadcn → 單檔 HTML）。

## Target B — open-design 版型（單檔可攜 HTML，且有對應 shape）

最快、零 API key。但**先確認該 shape 屬於哪一類**（實測差異很大）：

- **有完整 composer pipeline 的 shape**（ships `schema.ts` + `scripts/compose.ts` + `styles.css` + `inputs.example.json`）：目前主要是 **`open-design-landing`** 與 **`open-design-landing-deck`**。這類可直接跑：
  ```bash
  cd .vendor/open-design/design-templates/open-design-landing
  npx tsx scripts/placeholder.ts ./out/assets/             # $0 placeholder 圖（或 imagegen.ts 走 fal.ai）
  npx tsx scripts/compose.ts inputs.json ./out/index.html  # inputs + styles.css → 自包含 HTML
  ```
- **只有 `example.html` + `SKILL.md` 的 shape**（如 `saas-landing`、`dashboard`、`web-prototype`、`pricing-page` 等大多數）：**沒有 `scripts/compose.ts`，上面的 compose 命令會失敗**。改用其中一種：
  1. **Fork composer**：把 `open-design-landing/` 的 `schema.ts`+`scripts/compose.ts`+`styles.css` 複製過來，改其 styles/tokens 與 slots 對應目標 shape。
  2. **Hand-author from example.html**：以該 shape 的 `example.html` 為結構起點，照其 `SKILL.md` 的 `inputs`/`parameters` 契約填真實內容，手工產出單檔 HTML。

先 `ls <shape>/scripts/` 判斷屬哪類，別假設 `compose.ts` 一定存在。把版型 `styles.css` 當起點；換品牌就把 token 換成 Phase 1 選定的 `design-systems/<name>/tokens.css`。self-check：無 404 asset、reduced-motion 有效、responsive 到 560、對比 AA。

## Target C — gstack / Pretext（單檔 HTML，需真實 line-break / reflow / contenteditable 重排）

走 gstack `/design-html` 慣例（`.vendor/gstack/design-html/SKILL.md`）：

- render 引擎 **Pretext**（`vendor/pretext.js`，30KB 零依賴；inline 或 `https://esm.sh/@chenglou/pretext`）——做真實高度 / 斷行計算、`contenteditable` + MutationObserver 重排、ResizeObserver relayout。
- "Always include"：CSS 變數 tokens、Google Fonts via `<link>` + `document.fonts.ready` gate、語意 HTML5 + ARIA + heading 階層 + `focus-visible`、responsive 375/768/1024/1440、dark mode + reduced-motion、真實內容。
- 預設 vanilla self-contained HTML；偵測到 `package.json` 的 React/Svelte/Vue 才輸出框架版。

## Target D — A2UI（agent 送 JSON message，renderer 畫出 catalog 元件；可 patch）

適合 server/agent 動態產生、需要增量 patch、catalog-driven 的 UI。**先選 renderer，再對其 exact catalog compose。**

**Compose**：產出有序 `ServerMessage[]`——`createSurface`（綁 catalog）→ `updateComponents`（flat 樹，parent 用字串 id 參照 child）→ `updateDataModel`（JSON Pointer 綁資料）。root 元件 `id:"root"`。範例（standard catalog，contact form）：

```jsonl
{"createSurface":{"surfaceId":"s1","catalogId":"https://a2ui.dev/specification/0.9/standard_catalog_definition.json"}}
{"updateComponents":{"surfaceId":"s1","components":[
  {"id":"root","component":"Column","children":["lbl","fld","btn"]},
  {"id":"lbl","component":"Text","text":"Email"},
  {"id":"fld","component":"TextField","label":"Email","text":{"path":"/contact/email"},"usageHint":"shortText"},
  {"id":"btn_l","component":"Text","text":"Submit"},
  {"id":"btn","component":"Button","child":"btn_l","action":{"name":"submitContactForm"}}]}}
{"updateDataModel":{"surfaceId":"s1","path":"/contact","op":"replace","value":{"email":"a@b.com"}}}
```

**Render target 二選一**：

- **React / shadcn**（要品牌 + shadcn 外觀，最推薦做 web）：對 `giant_catalog.json`（v0.10）compose——元件 `Container/Text/Image/ChartWidget/DataGrid/HeroBanner/Section/ColumnsLayout` + `stylePreset` 品牌 + functions（`formatTWD`…）。
  - ⚠️ **Giant catalog 是 display-only：沒有 form / input 元件**（無 `TextField`/`Button`/`Select`/`Checkbox`）。若要做**表單 / 互動輸入**，二選一：(a) 用 **standard/Lit catalog**（它有 `TextField`/`Button`/`CheckBox`/`Slider`/`ChoicePicker`）——但那走 Lit renderer，不是 shadcn 外觀；或 (b) **擴 `giant_catalog.json`** 加上表單元件定義 **並**在 `catalog.ts` `CATALOG_RESOLVERS` 加對應 shadcn resolver（`ShadcnInput`/`ShadcnButton`…）——這是 build 步驟，不是「填了就 render」。做表單前先確認要走哪條。
  - **Giant 品牌 token 不在 open-design**（152 套裡沒有 `giant`）：來自 catalog 的 `stylePreset` + `brand-guideline-company` skill（公司 CIS）。不要去 open-design 找 giant token。
  - Compose：Go fluent composer `a2ui.NewSurface(id, GiantCatalogID).SetData(...).AddComponents(...).Build()`；或直接寫對 `giant_catalog.json` 的 JSONL（root `id:"root"`，用 `Container/Section/...`，非 standard catalog 的 `Column/TextField`——本檔上方 JSONL 範例是 standard/Lit dialect，Giant dialect 元件名不同）。
  - **Patch lifecycle**：之後 patch = 再送一批 message：`updateComponents` 換掉某些 id 的元件、`updateDataModel`（`op: replace|add|remove` + JSON Pointer path）改資料；`A2UIRenderer.process(msgs)` 對同一 surface 增量套用（draft 流程用 `preview`→`commit`/`discard`）。
  - Render + 看：`new A2UIRenderer().process(msgs)` → `renderSurface(id)`（`frontend/lib/a2ui/`，站點 `frontend/app/agent/page.tsx`）。要跑起來看：`cd .vendor/giant-template-orchestrator/frontend && pnpm install && pnpm dev`（:3000；經 `local-infra-registry-governance` 取 port）。
- **Lit web-components**（WebView / native canvas）：對 `standard_catalog_definition.json` compose。`pnpm canvas:a2ui:bundle` → 開 `src/canvas-host/a2ui/index.html` → `window.openclawA2UI.applyMessages(msgs)`；`reset()` 清空。

## 共通收尾

- 跑一次 Phase 1 tokens 的一致性檢查（沒有 raw hex 漏網）。
- 自我對照 anti-slop-checklist 的「必避 / 必含」。
- 進 Phase 3 前，先把畫面 render 出來截一張圖自己看一眼（見 [review-phase.md](review-phase.md)）——這一步就是整個管線以前缺的。
