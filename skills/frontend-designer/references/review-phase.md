# Phase 3 — Frontend Visual + Static Review（前端 domain-expert 複核）

這是本 skill 最關鍵的新增能力：`code-review` 家族**沒有任何一步 render UI**，本 phase 補上那個 gate。定位與 `security-risk-reviewer` 相同——**提供 findings 餵給 review，不自行下 PASS/FAIL**；`review.md` / `code-review` 仍是 verdict authority。

## 何時觸發

review 觸及前端變更：`.css`/`.scss`/`.less`、`.html`、`.jsx`/`.tsx`、`.vue`/`.svelte`、Tailwind class、樣式或版型檔、或任何「畫面長相」會變的 diff。也在使用者說「這畫面很醜 / 很 AI / 排版怪 / 過不過 design review」時觸發。

## 兩條 review lane（都要跑）

### Lane 1 — Static（審 code 對 design-system 的遵循）

對照規則，逐項給 finding：

- **Tokens**：顏色 / 間距 / 圓角是否用 CSS var / design-system token，而非 raw hex / 魔術數字。
- **shadcn 規則**（若專案用 shadcn）：semantic token（禁 `bg-blue-500`）、Field/InputGroup 正確組合、必要 a11y Title/`sr-only`。來源：`shadcn` skill `rules/*`。
- **Anti-slop**：font blacklist、AI-slop blacklist（見 [anti-slop-checklist.md](anti-slop-checklist.md)）。gstack `.vendor/gstack/review/design-checklist.md` 是 grep 得到的清單，可直接對照。
- **WCAG POUR baseline**：對照 [anti-slop-checklist.md](anti-slop-checklist.md) §C（WCAG 2.2 AA / POUR）逐項——文字對比 4.5:1、**非文字 / 相鄰色對比 ≥ 3:1（contrast 不能太近）**、不可只靠顏色、heading 階層、ARIA、`focus-visible`、`prefers-reduced-motion`、target size。來源整合 open-design `craft/accessibility-baseline.md` + WCAG SC 編號。

### Lane 2 — Visual（render → 截圖 → 用眼睛評）

這是文字審查看不出來的部分。截圖能力**不自帶**：**透過 Skill tool 調用 `webapp-testing`**（Playwright 截圖 / DOM / console，`invoked`）render 並截圖；或用 `uat-demo-agent` 的 `uatdemo` binary 當替代後端。皆不可用時退到 `resource-fallback`（直接跑本 skill `scripts/visual-review.mjs`）或 `unavailable`（只能做 Lane 1 static，於 findings 明記 visual 未跑）。收尾在 `Composed via:` 標明截圖來源 skill。取得 PNG 後 **Read 那張 PNG** 親自評。

> **先過 render bridge**：被審的若是 React/Vue 元件（不是靜態 HTML），截圖前要先把它變成一個可截圖的 URL（dev server / 最小 harness / `web-artifacts-builder` 打包 / Storybook）。render bridge、multi-viewport driver、computed-CSS probe、brand-token 量測、pixel-diff、以及**工具 / 外部 repo 缺席時的誠實降級**，全部有可直接用的 code：見 [visual-probes.md](visual-probes.md)。

**最快：服務本地 build 的 HTML 再截圖**（適合複核本地前端產物）：
```bash
# prove_..._bundle.py 會起本地 HTTP server 服務你的 HTML，跑 Playwright，strict-verify
python .vendor/aclab-uat-demo-agent/scripts/prove_external_computer_use_runtime_bundle.py \
  --target-url http://localhost:<port>/<page>  --ready-selector <css> --capture-selector <css> \
  --work-dir temp/frontend-review
# → JSON: bundlePath / reportPath / 截圖 PNG（bytes ok）
```

**對任意 URL / 已跑起來的頁面**：寫一份最小 web plan 給 `uatdemo run uat --file plan.json`（step 欄位 `url`/`readySelector`/`captureSelector`/`loginConfig`），或直接用 `webapp-testing` 的 Playwright 截圖。BINARY：`.vendor/aclab-uat-demo-agent/skills/uat-demo-agent/scripts/uatdemo-<os>-<arch>`。

截好圖後，Read PNG 並評：
- **Layout**：有無重疊 / 破版 / 溢出 / 對齊亂 / 空間節奏不對。
- **視覺階層**：主焦點是否明確；heading 大小 / 對比是否建立階層。
- **對比 & 可讀**：文字對背景是否達 AA；body ≥ 16px。
- **品牌一致**：色 / 字 / 圓角 / 間距是否符合 Phase 1 design system（有 `DESIGN.md` / CIS 就逐項比對）。
- **AI slop**：紫藍漸層、三欄圓圈 icon、置中一切、統一大圓角、漸層 CTA、裝飾 blob…（見 checklist）。

**建議加做（本 skill 需自補，uat-demo-agent 沒提供）**：
- **Multi-viewport**：對 375 / 768 / 1440 各截一張（用不同 context/plan 驅動不同寬度）。
- **元件級截圖**：`captureSelector` 只截被改的元件（如改動的 nav / card），聚焦。
- **Computed-CSS probe**：用 Playwright `evaluate` 取 `getComputedStyle` / box-model / `scrollWidth>clientWidth`（溢出）來佐證 layout finding，而非只靠肉眼。
- **對比量測 probe（WCAG 1.4.3 / 1.4.11）**：用 `evaluate` 取相關元素的 computed `color` / `background-color` / border 色，算對比比值——文字 < 4.5:1（大字 < 3:1）、或**相鄰 surface / 狀態 / 邊框 < 3:1（contrast 太近）**即記 finding，附實測比值當證據（比肉眼可信）。
- **RWD 選單 probe（SC 1.4.10 + 導覽收合）**：在 375 寬度截圖 + `evaluate` 檢查——hamburger 鈕存在且 `aria-expanded` 隨點擊切換、展開後選單可見不溢出、`scrollWidth<=clientWidth`、非只靠 `:hover`。桌面 1440 與行動 375 兩態各留一張圖對照。
- **Baseline diff**：若有 golden 截圖，做 pixel-diff 判是否 regress（uat-demo-agent 只有 uniqueness hash，需自補 image-diff）。

## Findings 格式（折進 review）

每條 finding：`[SEVERITY] (dimension) file:line 或 元件/畫面位置 — 描述 + 具體建議`。dimension ∈ {layout, hierarchy, contrast/a11y, brand/design-system, anti-slop, responsive}。附上截圖路徑當證據。Visual finding 若能用 computed-CSS 佐證就標明（提高可信度）。

把 findings 併入 review 的「設計一致性 / 程式碼品質」維度。**不要**自己改寫成 `PASS`/`FAIL`。

## 與 code-review 家族的接法（迴向注意）

理想上本 skill 作為 `code-review` 的前端 domain-expert sibling（如 `test-quality-reviewer`）。但要**正式讓 `code-review` 自動把它當 sibling input**，是改 `code-review` 家族行為——其 source-of-truth 在 upstream repo（`aclab-code-review-private`），該變更必須以 change-request **迴向該 repo 適當位置**，不可只改本 workspace 的 vendored 副本。在 wiring 完成前，spec Phase 5 可手動呼叫本 skill 當前端複核輸入。（此為 governance 指標，非資源路徑。）

## 反模式

- 只做 static、不 render → 又回到「看不到畫面」的老問題。
- 截了圖不 Read / 不評，只當證據貼著 → 沒有真正複核。
- 本 phase 直接給 verdict → 越權；只給 findings。
- 為了截圖亂改 / 亂啟動被審 repo 的 runtime → 違反 `local-infra-registry-governance`；render 屬 read-only observation。
