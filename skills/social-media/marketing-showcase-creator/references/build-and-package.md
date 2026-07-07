# Build & Package（把文案交付成可用的產物）

Phase 1–4 決定「寫什麼」；這份 reference 是 Phase 5「交付成什麼」。目標：潛在客戶手上真的能開、能切語言、能列印成傳單、能收到附件。

參照原則：本檔提到的路徑 / 檔名於實作時再讀取細節；下面的 CSS / HTML 片段是**模式示範**，class 名稱依專案既有樣式調整，不是硬規定。若專案已有 showcase HTML/template，所有 print-friendly 改動都必須以 **additive patch** 方式套入：保留既有 screen UI、section 結構、class、品牌樣式與互動，只新增 Print control、`printShowcase()` handler、以及 `@media print` CSS。

先分流工作模式：

- **Full regeneration / template-first showcase**：使用者說「重新產生 showcase」「use showcase 產生」「以 template 為主」「正常美觀的 HTML」時，先重新建立完整螢幕版 showcase。screen UI 是主產物：hero、真實截圖、benefit story、visual workbench、proof/gallery、CTA、manual/review links、雙語草稿與 guide 都要跟著更新；print-friendly 是 alternative function。
- **Print-only additive patch**：只有使用者明確說只要修 print-friendly、列印失蹤、PDF 跑版時，才只補 Print control / handler / print CSS。這時不能覆蓋原本 template。

不要把 full regeneration 做成 print-only patch，也不要為了 print-friendly 把一個正常 showcase 改成像純紙本文件。

---

## 1. 交付檔案佈局

Showcase 建議輸出到專案的 `docs/showcase/`（或既有站台的公開頁位置）。一組完整交付物：

```
docs/showcase/
├── index.html            # 中英雙語同頁；引用 style.css + showcase.js
├── style.css             # 版面樣式 + 內含（或 @import）print 區塊
├── showcase.js           # 語言 toggle（記住偏好）+ Print 按鈕 handler
├── SHOWCASE_DRAFT.md     # 雙語文案 SSOT（Phase 3 先落成，審過再進 HTML）
└── GENERATION_GUIDE.md   # 生成備忘：怎麼重生成這份 showcase
```

單檔情境（要能單獨寄出 / 內嵌）也可把 CSS / JS inline 進 `index.html`；此時 print 區塊就放在同一個 `<style>` 內。

---

## 2. `SHOWCASE_DRAFT.md`（markdown 草稿 = 文案 SSOT）

**為什麼要先有草稿**：HTML 難以審閱、難以 diff；先把文案寫成好讀的 markdown，讓使用者一眼看完整條說服路徑、也讓下一次更新有 source of truth，而不是從 render 好的 HTML 反推。

形狀：依 Phase 3 的敘事弧（Hero → 痛點 → 核心價值 → proof → how-it-works → 次級 → 信任 → Final CTA），**每個 section 一段，雙語並列**。範例：

```markdown
## Hero（位置 1）
- **EN headline:** Launch a beautiful, AI-powered website — in days, not months.
- **ZH 標題:** 幾天內，就上線一個 AI 驅動的漂亮網站。
- **EN subhead:** …
- **ZH 副標:** …
- **CTA:** Start free →（token: @cms/signup）

## 痛點（位置 2）
| # | EN | ZH |
|---|----|----|
| 1 | … | … |
```

草稿定稿後，HTML 的每個雙語節點都應能回溯到草稿的對應行——這也讓 jargon sweep（Phase 4）先在 markdown 上跑一輪更快。

---

## 3. `GENERATION_GUIDE.md`（生成備忘）

一份讓「非作者也能照著重生成」的操作備忘。不是行銷文，是給維護者的。建議涵蓋：

1. **Content authority sources** — 這份 showcase 的文案 / 數據來自哪裡（`SHOWCASE_DRAFT.md`、value-prop brief、真實截圖、review evidence）；哪些 metric 是真實可佐證、哪些是能力描述。
2. **Brand rules** — 色票、字體、logo 用法（若專案有 CIS / brand skill 就引用它）。
3. **Bilingual pattern** — 雙語節點慣例（見下節），預設語言，切換行為。
4. **Section 順序（canonical order）** — 每個 section 的 id 與上下順序，以及哪些配對必須同步（例如「痛點 ↔ 價值主張」一對一）。
5. **manual / review 連結** — 有哪些外部參照按鈕、指向哪個相對路徑、偵測規則。
6. **Print rules** — print CSS 從哪來、Print 按鈕放哪裡、列印時哪些元素隱藏、列印對比修正規則、驗證方式（實際匯出 PDF + agent visual regression）。重點是 contrast/readability，不是重置或移除所有 screen styles。
7. **Output / regeneration steps** — 逐步：改草稿 → 重生 HTML → jargon sweep 對 live render → `check_showcase_contract.py` 結構檢查 → 列印驗證 → 打包 zip。
8. **誠實邊界** — 不可捏造的東西、claim 上限。

> 這份 guide 是 **per-project 生成備忘**，不是本 skill 的一部分；它會跟 showcase 一起放在專案裡，隨內容演進更新。

---

## 4. 中英雙語同頁 HTML（English + 繁體中文）

**同一份 HTML 承載兩種語言**，不拆檔、不拆站。每一處要雙語的文字都寫成**成對節點**，用 class 區分，JS toggle 切換顯示，並記住偏好。

### HTML 節點模式

```html
<h1>
  <span class="lang-zh">幾天內，上線一個 AI 驅動的漂亮網站</span>
  <span class="lang-en" hidden>Launch a beautiful, AI-powered website in days</span>
</h1>
```

- 用 `hidden`（或初始 inline `style="display:none"`）讓非預設語言先藏起來，避免載入瞬間兩語同閃。
- **成對、數量一致**：每個 `.lang-zh` 都要有對應 `.lang-en`（反之亦然）。漏配對 = 切語言時該處缺字。生成後可 grep 兩者數量比對（範例：`grep -o 'lang-en\|lang-zh' index.html | sort | uniq -c` 應相等）。
- `<html lang="…">` 屬性隨 toggle 更新（利於 SEO / 螢幕閱讀器）。
- CSS 必須保護 `hidden`：加入全域 `[hidden]{display:none!important}`，並在 print media 內也明確保留 `[hidden], .lang-zh[hidden], .lang-en[hidden]{display:none!important}`。這可避免 print CSS 的廣泛 `span` / `color` / layout 規則讓未選語言在 PDF 裡露出。

### Nav controls（language toggle + Print）

在既有 nav/header/action 區補上語言切換與 Print 按鈕。Print 是正式 template control，不是額外 nice-to-have；潛在客戶或 sales 同事拿到 HTML 時，應能直接按按鈕輸出 PDF。

**重要：這段是 patch pattern，不是 replacement template。** 若原本 HTML 已有 `nav`、hero、cards、grid、CTA、動畫、品牌色、`ui-skill` 產出的 class，全部保留。只把 Print button 插進既有 action group；若沒有 action group，才新增一個小的 `data-noprint` wrapper。不要用下面的簡化 nav 覆蓋原本 template。

```html
<nav class="site-nav" aria-label="Primary">
  <!-- Keep the existing brand / links / layout exactly as generated. -->
  <a class="brand" href="./index.html">Showcase</a>
  <div class="nav-actions" data-noprint>
    <!-- Keep existing controls, then append Print. -->
    <button id="lang-toggle" class="btn-ghost" type="button" onclick="toggleLang()" aria-label="Switch language">
      English
    </button>
    <button id="print-button" class="btn-ghost" type="button" onclick="printShowcase()" aria-label="Print this showcase">
      <span class="lang-zh">列印</span>
      <span class="lang-en" hidden>Print</span>
    </button>
  </div>
</nav>
```

- `type="button"` 避免在被嵌入 form 的情境意外 submit。
- 用真 `<button>`，不要用只綁 click 的 `<div>`；鍵盤、螢幕閱讀器與高對比模式會比較穩。
- `data-noprint` 讓整組互動 chrome 在紙面隱藏；print CSS 仍會額外指定 `#print-button`，避免 template 改動時漏掉。
- 若專案使用 icon library，可在文字旁加 print icon，但文字標籤不可只靠 icon。
- 若是在修既有 showcase，驗收 screen diff：除新增 Print control / 必要的 `data-noprint` 標記外，不應移除原本的 hero、cards、resource links、visual sections、CSS class 或品牌樣式。

### Toggle / print script（`showcase.js`）

```js
(function () {
  var saved = localStorage.getItem('showcase-lang') || 'zh'; // 預設 = 專案主要語言
  applyLang(saved);
})();
function toggleLang() {
  var cur = document.documentElement.getAttribute('lang');
  applyLang(cur === 'en' ? 'zh' : 'en');
}
function applyLang(lang) {
  var root = document.documentElement, btn = document.getElementById('lang-toggle');
  var en = lang === 'en';
  root.setAttribute('lang', en ? 'en' : 'zh-TW');
  if (btn) btn.textContent = en ? '繁體中文' : 'English';
  document.querySelectorAll('.lang-en').forEach(function (el) { el.hidden = !en; });
  document.querySelectorAll('.lang-zh').forEach(function (el) { el.hidden = en; });
  localStorage.setItem('showcase-lang', en ? 'en' : 'zh');
}
function printShowcase() {
  window.print();
}
```

- **預設語言**：偵測專案現有頁面 / README 主要語言；台灣專案通常預設 `zh-TW`。
- toggle / Print 按鈕放 nav 右側，`aria-label` 兩語都寫或使用能隨語言切換的 visible text。
- 切換用 `el.hidden`（布林屬性）比操作 `style.display` 乾淨；print CSS 也能直接靠 `[hidden]` 判斷。

---

## 5. manual / review 快速參照連結（條件式）

若專案已有操作手冊 / review HTML，在 showcase 裡放**連結按鈕**方便一鍵跳去參照。

### 偵測

只有檔案真的存在才加按鈕（偵測不到就不放死連結）：

```bash
ls docs/manual/**/*.html docs/review/**/*.html 2>/dev/null
# 常見位置：
#   docs/manual/en/index.html
#   docs/manual/zh-tw/index.html
#   docs/review/index.html
```

對每個存在的目標，決定一個**相對路徑**（showcase 在 `docs/showcase/`，manual/review 是手足目錄）：

- 手冊（中）：`../manual/zh-tw/index.html`
- 手冊（英）：`../manual/en/index.html`
- Review：`../review/index.html`

### 放置

放 nav 或 footer 的「resources / 更多資訊」區，雙語標籤，`target="_blank" rel="noopener"`：

```html
<div class="resource-links">
  <a class="btn-outline" href="../manual/zh-tw/index.html" target="_blank" rel="noopener">
    <span class="lang-zh">操作手冊</span><span class="lang-en" hidden>User Manual</span>
  </a>
  <a class="btn-outline" href="../review/index.html" target="_blank" rel="noopener">
    <span class="lang-zh">產品 Review</span><span class="lang-en" hidden>Product Review</span>
  </a>
</div>
```

- 語言變體（en / zh-TW 手冊）可依目前 showcase 語言指向對應版本，或兩個都列。
- 這些按鈕在 print 時可保留為純文字參照，或隱藏——見 print CSS。

---

## 6. Print-friendly（可快速印成 PDF 傳單）

### 根因：為什麼「部份 rendered 在 print 時會失蹤」

Showcase 常有**深色 section**（hero、stats bar、`.bg-dark`、CTA），做法是**深色 / 漸層背景 + 白字**。瀏覽器列印時**預設不印背景色與背景圖**（省墨），於是：

> 背景被丟棄 → 只剩白字 → 白字落在白紙上 → **整段看起來消失了**。

這正是 giant-template-orchestrator `docs/showcase/` 的症狀：它完全沒有 `@media print`，所以 hero / stats / CTA 在列印時空白。

### 修法

把 `assets/showcase-print.css` 的 `@media print` 區塊納入 showcase 樣式（append 進 `style.css`，或 inline 進 `<style>`）。**只納入 `@media print` 層；不要用這份 CSS 取代原本 `style.css`，也不要把列印對比修正套到螢幕版。** 核心手段：

1. **`print-color-adjust: exact`（+ `-webkit-` 前綴）** 作為防消失保險，避免瀏覽器丟棄必要背景時造成白字落在白紙上。
2. **Scoped contrast repair**：列印時對暗底 / 漸層 / 高風險區塊套用安全的深字淺底對比（例如 `#111827` / `#fff`），避免白字失蹤或低對比。不要把所有 card/grid/section 都改成白卡、不要移除全部背景/邊框/品牌樣式；只修會造成 contrast failure 的區塊。
3. **sticky nav 改 static**：`position:sticky` 在列印會重複 / 遮住內容；改 `static` 或直接 `display:none`。
4. **隱藏互動 chrome**：語言 toggle、Print 按鈕、hover-only 元素、非參照用的按鈕。
5. **只印目前語言**：`[hidden]` 的另一語言本來就不印；確保 print 不會意外把兩語都顯示。
6. **分頁控制**：卡片 / feature block `break-inside: avoid`，避免一張卡被切兩頁；大 section 允許跨頁。
7. **圖片**：`max-width:100%`，避免超出紙寬被裁。

### 驗證（必做）

**不要只看螢幕就宣稱可列印。** 必須跑 agent skill-based visual regression loop，然後實際用瀏覽器「列印 → 另存 PDF」（或 headless Chrome）匯出一次，逐頁目視。

### Agent visual regression loop（修改循環）

1. **Screen baseline**：修既有 showcase 前，先用 `webapp-testing` / `frontend-designer` 的 Playwright screenshot pattern 對 screen 版在 390 / 768 / 1440 取 baseline（靜態 HTML 可直接 `file://`；動態 app 先走 local runtime governance）。保存到 `temp/showcase-print-visual/baseline/`。
2. **Additive patch**：只新增 Print button、`printShowcase()`、`@media print` contrast repair；不替換 template。
3. **結構檢查**：跑 `check_showcase_contract.py`，先擋掉缺 Print button、缺 `window.print()`、缺 `@media print` 這類 template 漏洞。
4. **Print visual/contrast check**：跑本 skill 的 visual helper，產生 screen + print screenshots 與 computed contrast report：

   ```bash
   python skills/social-media/marketing-showcase-creator/scripts/check_showcase_print_visual.py \
     docs/showcase/index.html \
     --out temp/showcase-print-visual/current
   ```

   這會輸出 `screen-<width>.png`、`print-<width>.png`、`report.json`，並在 print media 下檢查可見文字對有效背景的 WCAG contrast（一般文字 4.5:1，大字 3:1）、水平溢出、以及 Print button 是否在 print 中隱藏。
5. **Agent readback**：逐張讀 `screen-*.png` 與 `print-*.png`。screen 圖只能出現「新增 Print control」這類小差異；print 圖不得有白字消失、低對比、互動 chrome、水平溢出、或被切到不可讀的卡片。
6. **修改循環**：只要 `report.json` 有 contrast failure，或 agent 讀圖發現 layout/section 消失，就回到 CSS/HTML 做最小修正，再重跑第 3–5 步。不得在失敗狀態宣稱 print-friendly 完成。

通過後，再做 PDF 目視：

- 深色 section 的字**都看得到**（沒有白紙空段）。
- 一般段落、卡片、stat、CTA 的文字在紙面上有足夠對比；暗底/漸層區塊不會因背景未列印而白字消失。
- 沒有段落被 sticky nav 遮住 / 重複。
- 卡片沒有被硬切在分頁線上到不可讀。
- Print / language toggle 等互動按鈕沒有出現在 PDF；manual/review resource links 若保留，應有底線或可辨識 URL/文字。
- 只出現目前語言；抽查 hero、timeline/card、CTA，不得把 `.lang-zh` 與 `.lang-en` 同時印出。
- 螢幕版仍保留原本 UI/template；除了多一個 Print control，hero、cards、grid、brand styling、CTA 與原本互動沒有被換成 print-only layout，也沒有因 print-friendly 修正而被「清樣式」。

headless 驗證（若環境有 chromium）：

```bash
chromium --headless --disable-gpu --no-sandbox \
  --print-to-pdf=/tmp/showcase.pdf --print-to-pdf-no-header \
  "file://$PWD/docs/showcase/index.html"
```

結構檢查（不能取代 PDF 目視，但能先擋掉 template 漏洞）：

```bash
python skills/social-media/marketing-showcase-creator/scripts/check_showcase_contract.py docs/showcase/index.html
```

檢查內容包含：`#print-button`、`printShowcase()` + `window.print()`、`.lang-en` / `.lang-zh` 數量一致、`@media print`、`print-color-adjust: exact`、隱藏 Print 按鈕、列印對比修正與底線連結。

結構檢查只能擋掉 print contract 漏洞，不能替代 screen UI preservation review。若你是在既有 showcase 上補 print-friendly，必須跑上面的 visual regression loop，確認不是把原 template 覆蓋成列印版。

---

## 7. 打包成可寄 email 的 zip

用 `scripts/package_showcase.py` 把 showcase 與（若存在）manual / review 收進單一 zip 當附件：

```bash
# 自動偵測 docs/ 底下的 showcase / manual / review
python scripts/check_showcase_contract.py docs/showcase/index.html
python scripts/package_showcase.py --docs docs -o showcase-bundle.zip

# 或明確指定要收哪些目錄
python scripts/check_showcase_contract.py docs/showcase/index.html
python scripts/package_showcase.py \
  --include docs/showcase --include docs/manual --include docs/review \
  -o showcase-bundle.zip
```

- 只收 web / 文件資產（html / css / js / 圖片 / md / json / pdf / 字體），跳過 node_modules、.git、暫存檔。
- 印出 manifest（收了哪些檔、總大小），方便寄前確認。
- 純 Python 標準庫、跨平台，無第三方依賴。
