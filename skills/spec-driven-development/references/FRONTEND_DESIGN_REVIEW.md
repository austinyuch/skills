# Frontend Design / Engineer / Visual Review（`frontend-designer`）

本文件定義 SDD 如何在 **Phase 2（設計）/ Phase 4（實作）/ Phase 5（複核）** 導引到 `frontend-designer` skill，補上 `code-review` 家族**完全不審前端**的缺口（不看 CSS/HTML、不 render、不查 layout/對比/a11y/design-system）。

> **一句話**：`code-review` 家族審程式碼結構、測試、安全，但**沒有一步 render UI**。當本 spec 有前端產出時，`frontend-designer` 就是那個缺失的前端 domain expert——設計端建立 design system、實作端選 render target、複核端 render→截圖→評。它與 `security-risk-reviewer` 同一層級：**提供 findings 餵給 review，不自行下 verdict**。

## 1. 何時觸發（capability-gated）

**只在本 spec 有前端產出時**才觸發，避免對純後端 / CLI / 治理 slice 誤套視覺標準：

- 產出或變更 web UI：頁面 / 元件 / landing / dashboard / artifact / prototype；
- 變更 `.css`/`.scss`/`.less`、`.html`、`.jsx`/`.tsx`、`.vue`/`.svelte`、Tailwind class、樣式 / 版型檔；
- 或使用者說「這畫面很醜 / 很 AI / 排版怪 / 過不過 design review」。

Availability 判定與 Global Constraint #14 相同（workspace-local / global skill home 任一命中即可用）。皆不可用時沿用既有內建評估，於 `review.md` 記 `frontend-designer unavailable`，不得 silent skip。

## 2. 定位與 Authority 邊界

- `frontend-designer` 是**整合的前端 orchestrator + domain expert**；它 **composes** 既有前端 skills（`shadcn`、`brand-guideline-company`、`web-artifacts-builder`、`frontend-patterns`、`theme-factory`、`webapp-testing`、`uat-demo-agent`），SDD **不 re-implement、不重造**。
- **這條 lane 的 owner 是 `frontend-designer` skill**——SDD 只負責「何時觸發、傳 scope、把結果寫回 `design.md` / `review.md`」，並導引過去。
- **Phase 5 視覺複核只提供 findings，不下 PASS/FAIL**（與 `security-risk-reviewer` 同 pattern）；`review.md` / `security-review` / SonarQube 的 authority 不被稀釋。
- 視覺 lane 需 Playwright backend（`uat-demo-agent` / `webapp-testing`）；若要起本地 runtime，遵守 `local-infra-registry-governance`；render 屬 read-only observation，不得亂改被審 repo。

## 3. 三個 Phase 的導引

### Phase 2 — Design（前端設計輸入，advisory）

在 `design.md` 加入前端設計決策：確立 design system 的單一 source of truth（既有 `DESIGN.md` → 公司 CIS via `brand-guideline-company` → open-design token 系統 → 否則 direction-pick）→ tokens 一律 **CSS custom properties** → layout 計畫 → 內建 anti-slop（font/AI-slop blacklist）與 a11y baseline（AA 對比、ARIA、focus、reduced-motion、responsive）。這是 advisory 設計輸入，不是 gate。

### Phase 4 — Implementation（前端 left-shift，conditionally required）

實作前端時以 `frontend-designer` 的 render-target 決策樹選一：**shadcn**（React）/ **open-design 版型**（compose.ts 單檔 HTML）/ **gstack-Pretext**（framework-agnostic HTML）/ **A2UI**（agent 動態 catalog-driven UI）。tokens 用 CSS var、真實內容、responsive / dark mode / a11y，並對照 anti-slop-checklist。與 `code-refactoring-advisor` 的 left-shift 同層級（有前端產出時 conditionally required）。

### Phase 5 — Review（前端視覺複核，required input，findings-only）

當 review 觸及前端變更，`frontend-designer` 的 Phase 3 為 **required input**（非 verdict），兩條 lane 都要跑：

1. **Static**：審 CSS/JS/HTML/JSX 對 design-system 的遵循——tokens 用 CSS var 而非 raw hex、shadcn 組合規則、font/AI-slop blacklist、a11y baseline。
2. **Visual**：render → 截圖（page + 關鍵元件 + 多 viewport）→ **Read 那張 PNG** 親自評 layout / 視覺階層 / 間距 / 對比 / 品牌一致性 / anti-slop。可用其 turnkey `scripts/visual-review.mjs`（multi-viewport + computed-CSS probe）。

findings 以 `[SEVERITY] (dimension) 位置 — 描述 + 建議` 格式併入 `review.md` 的「設計一致性 / 程式碼品質」維度，附截圖證據。**不得**自行改寫成 `PASS`/`FAIL`。三態誠實記錄：`ran` / `unavailable`（skill 皆無）/ `dependency-not-configured`（無 Playwright backend）。

## 4. `review.md` 應記錄的 Frontend Review Summary

- **Availability**：`ran` / `unavailable` / `dependency-not-configured`（三態不可混記）。
- **Static findings**：design-system 遵循、anti-slop、a11y 的違反項與 severity。
- **Visual findings**：layout / 階層 / 對比 / 品牌 / responsive 的問題 + 截圖路徑；能用 computed-CSS 佐證的標明。
- **Render backend**：用了 `uat-demo-agent` 還是 `webapp-testing`；若無 backend → visual lane unavailable，明記，不假裝審過（false-green）。

## 5. Forbidden Anti-Patterns

- 對純後端 / CLI slice 硬套視覺 / a11y 標準（只在有前端產出時觸發）。
- Phase 5 視覺複核直接下 `PASS`/`FAIL`（越權；只給 findings）。
- 只做 static、不 render 就宣稱審過前端（回到「看不見畫面」的老問題）。
- 在 SDD 內 re-implement `frontend-designer` 或它 compose 的子 skill（應導引過去）。
- 為截圖亂啟動 / 亂改被審 repo runtime（違反 `local-infra-registry-governance`）。

## 6. Why

💡 **原因 (WHY)**：SDD 已把 `code-review` 家族接成各階段的 capability-gated 輔助輸入，但那個家族**不含任何前端 / 視覺維度**，導致「畫面又醜又不符品牌又破版又不可無障礙，而沒有任何 reviewer 會發現」。把 `frontend-designer` 以同一 capability-gate + findings-only pattern 接進 Phase 2/4/5、且**只在有前端產出時觸發**，就能在不 hard-couple、不越權、不誤套的前提下，讓 spec 工作流真正對前端「設計得好、做得對、看得到」。
