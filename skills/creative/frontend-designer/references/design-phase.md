# Phase 1 — Design（設計前端、排版、視覺效果）

目標：在動任何一行前端之前，確立**單一 design-system source of truth** + 一組 tokens（CSS custom properties）+ 一份 layout 計畫，讓後面的實作有品味、一致、不 AI slop。

## 1. 確立 design system（優先序）

按序找，找到就停：

1. **repo 內既有 `DESIGN.md`**（gstack 慣例）→ 直接讀它，當作硬約束。通常 `CLAUDE.md` 已要求所有 agent 先讀。
2. **公司 / 組織 CIS 在場**（company 產物、品牌交付）→ 交給 `brand-guideline-company`，其官方色 / 字 / logo / grid 為 authoritative；此時 **supersede `theme-factory`**。
3. **想用某個既成品牌語言** → 讀 open-design `design-systems/<name>/DESIGN.md` + `tokens.css`，**採用它的 exact hex / type scale / radius，不要自己發明**。
4. **全都沒有** → 走 direction-pick（下節），產出最小可用 design direction + `DESIGN.md` 草稿。

不論來源，最終要有：一組 **named tokens**（見下）與一份 anti-slop 承諾（見 anti-slop-checklist）。

## 2. Direction-pick（從零建立設計方向時）

當沒有既有設計系統，用這三個來源合成一個**有主張、非通用**的方向（避免「menu 一堆選項讓使用者選」——propose，don't menu）：

- **aesthetic 方向**：`frontend-design-skill`（本 repo）給 distinctive 視覺方向；gstack `design-consultation/sections/proposal-and-preview.md` 的 aesthetic/decoration/color/motion taxonomy 可佐證。
- **具體 palette + 字**：挑一個 open-design `design-systems/<name>` 當基底（讀其 `tokens.css`），或 gstack 的 font 推薦（**避開 font blacklist**）。
- **craft 準則**：open-design `craft/{typography,color,laws-of-ux}.md` 決定 type scale、對比、間距節奏。

產出一份精簡 `DESIGN.md`（沿用 gstack schema）：aesthetic direction、decoration level、mood、reference sites、typography（display/body/mono 具名字體 + px scale）、color（accent + neutrals + 語意色 + light/dark surface hex）、spacing（4px base + 具名 scale）、layout（grid + max width + radius scale）、motion（easing + duration）、anti-patterns。

## 3. Tokens：一律 CSS custom properties

把設計決策落成 CSS 變數（不要散落 raw hex / 魔術數字）。最小集合：

```css
:root {
  /* color */
  --bg: …; --surface: …; --fg: …; --muted: …; --accent: …; --border: …;
  /* type */
  --font-display: "…"; --font-body: "…"; --font-mono: "…";
  --text-hero: 72px; --text-h1: 48px; /* … --text-nano: 11px */
  --tracking-display: -0.02em;
  /* space (4px base) */
  --space-2xs: 4px; --space-xs: 8px; /* … --space-3xl: 96px */
  /* radius / motion */
  --radius-sm: …; --radius-md: …; --ease: cubic-bezier(…); --dur: 200ms;
}
```
若採用 open-design `tokens.css` 或某 `DESIGN.md`，直接複製其變數名與值，別改名。

## 4. Layout 計畫

- 選一個 layout shape：open-design `design-templates/<shape>`（有現成 `styles.css`/`example.html` 可 fork）、gstack `DESIGN.md` 的 grid 慣例、或自訂。
- 定義 responsive breakpoints（gstack 慣例：375 / 768 / 1024 / 1440；open-design landing：1280/1080/880/560）。
- 規劃視覺階層（一個明確的主焦點、清楚的 heading 階層、間距節奏），並先把 anti-slop-checklist 的「必避」項讀一遍再排版。

## 5. 交棒給 Phase 2

輸出：design direction + tokens（CSS vars）+ layout 計畫 + 選定的 render target 傾向。進入 [implement-phase.md](implement-phase.md)。

## 反模式（本 phase 常見錯誤）

- 沒讀既有 `DESIGN.md` / 品牌就自己配色 → 產生不一致、off-brand 畫面。
- tokens 散成 raw hex → Phase 3 一定被挑。
- 用 `theme-factory` 蓋過公司品牌 → 錯：有 CIS 時 `brand-guideline-company` 優先。
- 一次丟十個風格選項給使用者 → 應該 propose 一個有理由的方向。
