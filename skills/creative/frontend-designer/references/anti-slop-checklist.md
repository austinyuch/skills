# Anti-Slop + Accessibility Checklist（設計與複核的硬規則）

Phase 1 設計時自我約束、Phase 3 複核時逐項對照。整合自 gstack（`DESIGN.md` / `design-html` / `review/design-checklist.md`）與 open-design（`craft/anti-ai-slop.md`、`craft/accessibility-baseline.md`）。這些是**硬規則，不可妥協**（安全 / 驗證 / 無障礙永不精簡）。

## A. AI-Slop 黑名單（必避）

出現任一項，Phase 3 記為 finding；Phase 1/2 直接不要做：

- **紫 / 靛 / 藍紫漸層當 accent**（最典型 AI 味）。
- **三欄「圓圈裡放 icon」的 feature grid**。
- **什麼都置中**（center-everything layout）。
- **所有東西統一大圓角**（16px+ 一致 border-radius，毫無階層）。
- **漸層 CTA 按鈕**、裝飾性 blob / wave、stock-photo placeholder 灰塊。
- **`system-ui` / `-apple-system` 當主要 display/body 字體**（沒有挑字＝沒有設計）。
- **通用 hero 文案**：「Welcome to X」「Unlock the power of…」「Get Started / Learn More」。
- **body font-size < 16px**、**> 3 種字體家族**、**跳過 heading 階層**。
- 假內容 / lorem ipsum（要真實內容）。

## B. Font 黑名單（避免）

Papyrus、Comic Sans、以及被過度使用而失去識別度的 Inter / Roboto / Open Sans 當**主要 display** 字體（可當 body fallback，但 display 應挑有個性的具名字體，如 Satoshi / DM Sans / Playfair / Inter Tight 等，依 design system）。tracking 於 ALL CAPS 一律加寬。

## C. WCAG 無障礙原則（POUR，必含）

以 **WCAG 2.2 AA** 為 baseline，按四大原則 **POUR**（Perceivable / Operable / Understandable / Robust）逐項檢查。違反 = Phase 3 high finding。

### Perceivable（可感知）

- **文字對比（SC 1.4.3, AA）**：一般文字 ≥ **4.5:1**；大字（≥ 18.66px bold 或 ≥ 24px）≥ **3:1**。
- **非文字對比 / 「contrast 不能太近」（SC 1.4.11, AA）**：UI 元件邊界、input 邊框、`:focus` 指示、icon、圖表關鍵色，以及**相鄰色塊 / 相鄰狀態之間**須 ≥ **3:1**。這就是「不能太近」的量化條件——凡下列色對比值 < 3:1 一律記 finding：
  - 相鄰 surface（card vs 背景、header vs body）
  - hover / active vs default 態
  - disabled vs enabled（disabled 允許 < 4.5:1 對文字，但要能被辨識）
  - 相鄰資料色（chart series-1 vs series-2、tag 群）
- **不可只靠顏色（SC 1.4.1）**：狀態、連結、圖例不能只用顏色區分——另加底線 / 形狀 / icon / 文字。
- **色彩距離下限**：相鄰語意色（success/warning、多 series）除對比外，hue 不可太近而難分；優先採 design-system 既定 palette，別臨時挑兩個相近色。

### Operable（可操作）

- 鍵盤全可達；`:focus-visible` 明顯且對相鄰色 ≥ 3:1（SC 2.4.7 + 1.4.11）；modal/menu 有 focus trap + Esc，且非 keyboard trap（SC 2.1.2）。
- 觸控 / 點擊目標 ≥ **24×24 CSS px**（SC 2.5.8, AA；本 skill 建議 44px）。
- 動畫尊重 `prefers-reduced-motion`（SC 2.3.3）；無 > 3 次/秒閃爍（SC 2.3.1）。

### Understandable（可理解）

- heading 階層不跳級（h1→h2→h3）；控件與 label 關聯（`<label for>` / `aria-labelledby`）。
- 錯誤訊息具體、指出欄位與修正方式（SC 3.3.1/3.3.3）；`<html lang>` 已設；導覽 / 命名一致。

### Robust（穩健）

- 語意 HTML5 + 適當 ARIA role/label；icon-only 按鈕有 `aria-label` / `sr-only`；狀態用 `aria-expanded` / `aria-current` / `aria-selected`。
- dark mode（`prefers-color-scheme`）下所有對比門檻**仍須成立**（深色常見對比塌陷）；多語用 logical properties（避免寫死 left/right）。

## D. Responsive baseline（必含）

- **Reflow（SC 1.4.10）**：320px 寬（或桌面 400% zoom）不出現水平捲動、內容不被裁切。至少 375 / 768 / 1440 不破版（gstack 慣例含 1024；open-design landing 到 560）。
- 無水平溢出（`scrollWidth <= clientWidth`）——Phase 3 可用 computed-CSS probe 驗。
- **RWD 導覽選單檢查（高頻破口，必查）**：桌面橫向 nav 在窄寬度須收合成**可用的行動選單**——
  - 收合鈕（hamburger）是真 `<button>`，有 `aria-label`、`aria-expanded` 反映開/合、`aria-controls` 指向選單容器。
  - 展開後鍵盤可 Tab 進出、Esc 關閉、focus 管理正確；**不可只靠 CSS `:hover` 展開**（觸控裝置無 hover，會完全點不開）。
  - 選單不溢出視窗、不被裁切；展開時不造成水平捲動；項目 target ≥ 24px。
  - **桌面態與行動態都要截圖複核**（見 review-phase Lane 2 multi-viewport：375 收合、1440 展開各一張）。
- 觸控目標建議 ≥ 44px（最低 24px）。

## E. 品味 / craft（提升，非硬性但強烈建議）

- 一個畫面一個明確主焦點；用大小 / 對比 / 空間建立階層，而非顏色轟炸。
- accent 色**克制**使用（點綴，不是主色鋪滿）。
- 間距用一致的 scale（4px base），不是隨手數字。
- 真實資料狀態覆蓋：empty / loading / error / 長內容 / 多筆（open-design `craft/state-coverage.md`）。
- 動畫有紀律：短、目的性、easing 一致（open-design `craft/animation-discipline.md`）。

## 使用方式

- **Phase 1（設計）**：把 A/B/C/D 當「不要做 / 一定要有」的清單，內建進 design direction；C 的 WCAG POUR + 對比門檻要在挑色 / 排版時就先滿足，不要留到複核才發現相鄰色太近。
- **Phase 3（複核）**：逐項 grep / 肉眼 / computed-CSS / 對比量測 probe 檢查，違反項寫成 finding（severity 依影響：對比不足（含相鄰色 < 3:1）/ 破版 / RWD 選單點不開 = high；AI-slop 味 = medium；craft 建議 = low）。gstack `review/design-checklist.md` 提供可 grep 的 pattern 與 confidence tier；對比與 RWD 選單用 review-phase Lane 2 的 probe 自動量測。
