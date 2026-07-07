# Visual Review — render bridge + probes (concrete code)

review-phase.md 說「這些要自己補」；本檔給可直接用的做法，消除「拿到概念但沒有 code」的落差。也涵蓋「被審的是 React 元件、不是靜態 HTML」這個最常見的第一道卡點。

> **Turnkey**：§1 multi-viewport + §2 computed-CSS probe 已封裝成可直接跑的
> [`scripts/visual-review.mjs`](../scripts/visual-review.mjs)：
> `node scripts/visual-review.mjs <url> [--out DIR] [--selector CSS] [--viewports 375,768,1440]`
> → 產出各 viewport 的 `review-<w>.png`（+ 選擇性 element 圖）與 `metrics.json`（overflow / computed sizes / colors）。playwright 缺席時**誠實 fail**、提示只跑 Lane 1。之後仍要 **Read 每張 PNG** 親自評、用 metrics 佐證。

## 0. Render bridge — 把被審的東西變成一個可截圖的 URL

截圖前必須先有一個 render 出來的頁面。依被審物型態選路徑（起任何本地 runtime 前，先遵守 `local-infra-registry-governance` 取得 port）：

- **靜態 HTML（open-design / gstack 產物）**：直接 `file://<abs>/index.html`，或用 uat-demo-agent 的 `prove_..._bundle.py` 起本地 server 服務它。
- **React / Vue / Svelte 元件或頁面**：
  1. 專案已有 dev server（Vite/Next）→ 經 `local-infra-registry-governance` 起 `npm run dev`，截該路由的 URL。
  2. 要**單獨**看一個元件 → 建一個最小 harness page（import 該元件、給代表性 props、mount 到 `#root`），用 `web-artifacts-builder` 打包成單檔 HTML 再 `file://` 截；或若專案有 Storybook，截該 story 的 iframe URL。
  3. 只要 diff 對應的畫面 → 用代表性 props/state 呈現 empty / loading / error / 長內容 多個狀態各截一張（見 open-design `craft/state-coverage.md`）。
- **selector 怎麼來**：讀元件 JSX / 模板，取其根容器的 `data-testid` / class / role 當 `captureSelector`；`readySelector` 用「載入完成才會出現」的元素（如主要內容容器）。

## 1. Multi-viewport 截圖（375 / 768 / 1440）

uat-demo-agent 無 viewport preset；用 Playwright 直接驅動不同寬度：

```js
// node: npx playwright；每個寬度截一張
const { chromium } = require('playwright');
(async () => {
  const url = process.argv[2];
  const browser = await chromium.launch();
  for (const w of [375, 768, 1440]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.screenshot({ path: `review-${w}.png`, fullPage: true });
    await ctx.close();
  }
  await browser.close();
})();
```
截完**逐張 Read PNG** 親眼評（layout/階層/對比/品牌/anti-slop）。

## 2. Computed-CSS probe（用量測佐證 layout / 溢出，而非只靠肉眼）

```js
// 在 page 上跑，回傳結構化 metrics
const probe = await page.evaluate(() => {
  const doc = document.documentElement;
  const overflowX = doc.scrollWidth > doc.clientWidth;              // 水平溢出 = 破版訊號
  const sel = (q) => { const el = document.querySelector(q); if (!el) return null;
    const cs = getComputedStyle(el); const r = el.getBoundingClientRect();
    return { color: cs.color, bg: cs.backgroundColor, font: cs.fontFamily,
             size: cs.fontSize, radius: cs.borderRadius, box: { w: r.width, h: r.height } }; };
  return { overflowX, body: sel('body'), heading: sel('h1'), cta: sel('button, .btn, [role=button]') };
});
```
用 `overflowX===true`、body `size < 16px`、或量到的顏色 / 圓角**與 design-system token 不符**來把「肉眼覺得怪」升級成可引用的證據。

## 3. Brand-token 一致性（量測 rendered 值 vs token）

讀設計來源的 token（`DESIGN.md` / CIS / open-design `tokens.css`）取期望 hex / font / radius，與 probe 量到的 computed 值比對。不一致就開 `[HIGH] (brand/design-system)` finding，附「期望 X、實際 Y」。避免品牌審查只停在「感覺不像」。

## 4. Baseline pixel-diff（有 golden 才做）

uat-demo-agent 只有 uniqueness hash。要真 VRT：存一張核可 baseline PNG，與本次截圖用 `pixelmatch`（`npm i pixelmatch pngjs`）逐像素比，diff 比例超過門檻（如 >1%）就開 finding。無 baseline 時**不要**假裝有 regression 判斷——標記「no baseline，僅新截圖」。

## 5. Resource-absent fallback（外部 repo / 工具不在時誠實降級）

本 skill 大量依賴 `~/projects/*`（uat-demo-agent / open-design / gstack / giant-orchestrator）與 Playwright。任一缺席時**誠實降級、不靜默跳過**：

- **無 Playwright / uat-demo-agent / webapp-testing** → 無法跑 Lane 2 visual：只做 Lane 1 static，於 findings 明記「visual review unavailable（no render backend）」，並建議補上。
- **無 open-design / gstack** → craft 規則 / 版型來源缺席：改用 anti-slop-checklist.md（已內建於本 skill，不依賴外部）當最小準則，記「external craft sources absent」。
- **無品牌來源（DESIGN.md/CIS/tokens）** → 只能審通用 craft + a11y，不能下品牌一致性 finding，明記「no brand source to compare against」。

原則：能跑的 lane 照跑，缺的部分誠實標記為 unavailable，絕不因缺工具就假裝審過（false-green）。

## 附：webapp-testing 一行替代

若不用 `uatdemo`，可直接用本 repo `webapp-testing` skill 的 Playwright toolkit 做 navigate + screenshot + DOM/console（受 `local-infra-registry-governance` gate）；其 `computed-CSS probe` 同 §2。
