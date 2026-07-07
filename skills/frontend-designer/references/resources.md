# Resources — canonical map + how an agent consumes each

這些是**外部專案 / 資源**，本 skill 讀取 / 複製 / 呼叫它們，不修改它們（upstream 為 source-of-truth）。

路徑寫法：**所有外部資源 repo 一律透過 repo 根目錄的 gitignored `.vendor/<repo>/<sub>` symlink 存取**（`open-design`、`gstack`、`openclaw`、`giant-template-orchestrator`、`go-cms-ai-site`、`aclab-uat-demo-agent`）。這些 symlink 由 `scripts/link-resources.sh` 建立，指向機器本地 clone（預設 `~/projects/…`，各以 `OPEN_DESIGN_HOME`/`GSTACK_HOME`/`OPENCLAW_HOME`/`GIANT_HOME`/`GOCMS_HOME`/`UATDEMO_HOME` 覆寫）。若 `.vendor/…` 不存在＝該機器尚未跑 bootstrap 或未 clone 該 repo → 視為 `unavailable`（三態降級，不得硬相依）。**skill 文件不再出現 `~/projects/…` 絕對路徑。**（唯一例外是 `code-review` 家族的 upstream repo 名稱，那是 governance「迴向去哪」的指標，不是本 skill 讀取的資源路徑。）

## open-design（design tokens + craft 準則 + 版型）— 最重要的設計資源

存取入口：`.vendor/open-design/`（gitignored symlink → 本機 open-design clone；`aclab-open-design` 只是 build 產物，忽略）。**用 file-based 消費，不要跑那個 app。**

- **品牌 token 層（152 套）**：`.vendor/open-design/design-systems/<name>/`
  - `DESIGN.md`（9 段：color/type/spacing/layout/components/motion/voice/brand/anti-patterns）
  - `tokens.css`（`--bg`/`--surface`/`--fg`/`--accent`/`--radius-*`/`--tracking-*` 等 CSS 變數）
  - 範例：`linear-app/`、`atelier-zero/`（editorial，landing 版型用它）、`default/`（有 `manifest.json`+`USAGE.md`，schema 最完整）；其它：`apple` `notion` `stripe` `vercel` `claude` `cursor` `supabase` `bento` `brutalism` `claymorphism` `cosmic` `editorial`…
- **通用 craft 準則（brand-agnostic，12 份）**：`.vendor/open-design/craft/*.md`
  - `typography.md` `typography-hierarchy.md` `color.md` `animation-discipline.md` **`anti-ai-slop.md`** **`accessibility-baseline.md`** `form-validation.md` `laws-of-ux.md` `state-coverage.md` `rtl-and-bidi.md`
  - `craft/README.md` 說明「3 軸模型」與 `od.craft.requires: [...]` opt-in
- **可 render 版型（111 套）**：`.vendor/open-design/design-templates/<shape>/`
  - 每個含 `SKILL.md`(agent 契約) + `schema.ts`(typed inputs) + `styles.css` + `example.html` + `scripts/compose.ts`
  - shapes：`saas-landing` `web-prototype` `dashboard` `pricing-page` `mobile-app` `magazine-poster` `social-carousel`；品味變體 `web-prototype-taste-{brutalist,editorial,soft}`；`html-ppt-*`（20+ 簡報）
  - 你問過的兩個：`open-design-landing/`（Atelier Zero editorial landing，完整參數化）、`open-design-landing-deck/`（同系統的橫向 slide deck）

**消費方式（零 API key）**：
```bash
cd .vendor/open-design/design-templates/open-design-landing
npx tsx scripts/placeholder.ts ./out/assets/            # $0 SVG 紙紋 placeholder 圖
npx tsx scripts/compose.ts inputs.example.json ./out/index.html   # inputs+styles → 單檔 HTML
```
沒有發佈 `@open-design/*` npm 給 consumer，所以路徑是「讀 md/css + copy 版型 + 跑該版型的 tsx composer」。

## gstack（DESIGN.md 方法論 + Pretext render + anti-slop 清單）

存取入口：`.vendor/gstack/`（gitignored symlink → 本機 gstack clone）。CLI/skill 工具箱，**framework-agnostic、token-driven**，render 用 **Pretext**（非 A2UI）。

- `.vendor/gstack/DESIGN.md` — canonical design-system 範例 + 每個專案該產出的 exact schema（aesthetic/type/color/spacing/layout/motion/grain + Decisions Log）
- `.vendor/gstack/design-consultation/sections/proposal-and-preview.md` — **最richest**：DESIGN.md template、font blacklist、aesthetic/color/motion taxonomy、AI-slop 清單
- `.vendor/gstack/design-consultation/SKILL.md` — design-system 建立流程（propose-don't-menu、coherence 規則）
- `.vendor/gstack/design-html/SKILL.md` — production HTML 慣例、Pretext API cheatsheet、"Always/Never include" 清單
- `.vendor/gstack/design-html/vendor/pretext.js` — 30KB 零依賴 render 引擎（inline 或 `https://esm.sh/@chenglou/pretext`）
- `.vendor/gstack/review/design-checklist.md` — **grep 得到的前端 anti-pattern 複核清單**（confidence tier + AUTO-FIX/ASK 分類）→ Phase 3 直接用

gstack 慣例：`DESIGN.md` 為 single source of truth（`CLAUDE.md` 已要求先讀）；tokens 用 CSS custom properties；vanilla self-contained HTML 為預設，React/Svelte/Vue 依 `package.json` 偵測。

## shadcn（React 元件庫 + design-system 規則）

本 repo skill：`~/.config/opencode/skills/shadcn/`（CLI-driven，`components.json`）。強制規則：semantic token（禁 raw `bg-blue-500`）、Field/InputGroup 組合、a11y 必要 Title/`sr-only`。**Phase 2 React 實作主力 + implement-side lint 來源**。

## A2UI（agent 送 JSON → renderer 畫 UI）

- 協定 / spec：`.vendor/openclaw/vendor/a2ui/README.md`、`.../specification/0.9/json/*.json`、範例 `.../0.9/json/contact_form_example.jsonl`
- Lit renderer（standard catalog）：`.vendor/openclaw/vendor/a2ui/renderers/lit/`（`@a2ui/lit`）；host `.vendor/openclaw/src/canvas-host/a2ui/index.html`；bundle `pnpm canvas:a2ui:bundle`（`scripts/bundle-a2ui.sh`）；render 呼叫 `window.openclawA2UI.applyMessages(msgs)`
- **React/shadcn renderer（Giant v0.10，A2UI 元件名 → shadcn resolver）**：
  - catalog：`.vendor/giant-template-orchestrator/configs/a2ui/giant_catalog.json`（Container/Text/Image/ChartWidget/DataGrid/HeroBanner/Section/ColumnsLayout + `stylePreset` 品牌 + functions `formatTWD`…）
  - renderer：`.vendor/giant-template-orchestrator/frontend/lib/a2ui/{renderer.ts,catalog.ts,binding.ts}`；render 站點 `frontend/app/agent/page.tsx`（`new A2UIRenderer().process(msgs)` → `renderSurface(id)`）
  - Go composer（fluent）：`.vendor/giant-template-orchestrator/internal/adkagent/a2ui/{builder.go,types.go}`（`NewSurface(id, GiantCatalogID).SetData(...).AddComponents(...).Build()`）
- 輕量 CMS 方言（非 Google wire format）：`.vendor/go-cms-ai-site/skills/a2ui-protocol/SKILL.md`（`uiType`/`targetMutation`/`mutationVariables`）

**三方言**：Google standard(Lit) / Giant v0.10(React/shadcn) / go-cms-ai-site(CMS)。先選 renderer，再對其 exact catalog compose。root 元件 `id:"root"`。

## uat-demo-agent（Playwright render + 截圖後端）— Phase 3 視覺複核主力

Repo：`.vendor/aclab-uat-demo-agent/`。Go `uatdemo` binary（headless Chromium via `playwright-go`）。

- 打包好的 binary（免 build）：`.vendor/aclab-uat-demo-agent/skills/uat-demo-agent/scripts/uatdemo-{linux-amd64,linux-arm64,darwin-amd64,darwin-arm64,windows-amd64.exe}`（+ `uatdemo.py` wrapper）
- 命令：`uatdemo run uat --file plan.json`（web step 欄位：`url`/`readySelector`/`captureSelector`/`loginConfig`）；`report show --bundle <p>`；`report verify-computer-use-bundle --bundle <p> [--min-unique-screenshots N]`
- **服務本地 build 的 HTML 再截圖**（最適合複核本地前端）：`scripts/prove_external_computer_use_runtime_bundle.py` 可起 `ThreadingHTTPServer` 服務生成的 HTML，跑 Playwright，strict-verify → 產出 PNG + report + bundle
- 證據：PNG（element/page level）+ `renderReplayHTML` 的 `<runId>-replay.html` + review `index.html`（`internal/publishing/publisher.go`）
- 可 reuse 的 Go 套件：`internal/webrunner`（`Runner`/`PlaywrightFactory`/`Page`/`executeCaptureStep`/`validateScreenshotPNG`）
- **缺、需自行補**：baseline pixel-diff VRT（只有 uniqueness hash）、web path 的 computed-CSS/DOM 抽取、multi-viewport preset

本 repo 亦有 `webapp-testing` skill（Playwright 截圖/DOM/console），受 `local-infra-registry-governance` gate。
