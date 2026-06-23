# Manual HTML Template Usage

這份文件說明 `assets/manual-template.html` 如何被 `user-manual-skill` 使用。它的目的不是教 agent 從零寫 HTML，而是讓 agent **把內容填進既有 template**，快速生成一致、可讀、可驗證的 manual HTML。

## 1. Canonical Template Path

- Template file: `assets/manual-template.html`
- Scope: OpenCode global `user-manual-skill`
- Release format: template 本身屬於 global skill folder 的正式資產，不是額外 package

## 2. Placeholder Tokens

| Token | Required | Purpose | Example |
|---|---|---|---|
| `{{LANG}}` | Yes | `<html lang>` | `en`, `zh-TW` |
| `{{TITLE}}` | Yes | Browser page title | `Product X — User Manual` |
| `{{FONT_FAMILY}}` | Yes | Body font stack | `'Noto Sans', Arial, sans-serif` |
| `{{HEADING_FONT_FAMILY}}` | Yes | Heading font stack | `'Lato', Arial, sans-serif` |
| `{{EXTRA_HEAD}}` | Optional | Extra meta, favicon, extra style overrides | `<meta name="robots" content="noindex">` |
| `{{KICKER}}` | Yes | Hero kicker line | `UAT conditional · evidence refresh 2026-04-29` |
| `{{PRODUCT_NAME}}` | Yes | Main hero heading | `Template Orchestrator` |
| `{{PRODUCT_SUBTITLE}}` | Yes | Hero subtitle | `User Manual & Operations Guide` |
| `{{PAGE_BADGES}}` | Optional | Status / evidence badges in hero | `<span class="status-pill status-conditional">CONDITIONAL</span>` |
| `{{NAV_TITLE}}` | Yes | Sidebar navigation heading | `Navigation`, `導覽` |
| `{{SIDEBAR_NAV_ITEMS}}` | Yes | Sidebar `<li>` items | `<li><a href="#getting-started">1. Getting Started</a></li>` |
| `{{SECTION_CARDS}}` | Optional | Quick-start / audience cards | `<section class="section">...</section>` |
| `{{CONTENT_SECTIONS}}` | Yes | Main manual sections | `<section id="getting-started" class="section">...</section>` |
| `{{FOOTER_TEXT}}` | Optional | Footer text | `Generated from governed evidence on 2026-04-29` |
| `{{OPTIONAL_MERMAID_SCRIPT}}` | Optional | Mermaid CDN loader when diagrams exist | `<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>` |
| `{{EXTRA_SCRIPTS}}` | Optional | Extra inline scripts | `<script>...</script>` |

## 3. Required Component Mapping

The template already includes CSS + HTML hooks for these SKILL requirements:

- `.sidebar` → fixed navigation tree / side menu
- `.section-cards`, `.quick-card` → homepage quick-start / audience cards
- `.card`, `.card-caption`, `.caption-meta` → screenshot cards with caption and evidence meta
- `.status-pill` + `.status-pass|conditional|fail` → readiness / evidence badges
- `.alert`, `.warn` → note / warning banners
- `.evidence-grid`, `.evidence-card` → evidence summary cards
- `.gap-table` → `What Still Needs Proof` inventory table
- `.asset-list`, `.download-btn` → starter-assets / download mechanism
- `.api-table` → concise API/Swagger reference table
- `.cmd` → CLI / backend command examples

Agent 不應重新發明對應 class 名稱；若要呈現這些內容，應優先使用上述既有 class。

## 4. Generation Workflow

### 4.1 Default path

1. 產出完整 Markdown / structured content outline
2. 把首頁 quick cards、sidebar items、content sections 組成 HTML fragments
3. 將 fragments 填入 `manual-template.html`
4. 只在必要時覆蓋 `:root` CSS variables；不要重寫整份 CSS

### 4.2 EN / ZH-TW variants

使用同一份 template，同步生成：

- `docs/manual/en/index.html`
- `docs/manual/zh-tw/index.html`

差異通常只有：

- `{{LANG}}`
- `{{TITLE}}`
- `{{FONT_FAMILY}}`
- `{{HEADING_FONT_FAMILY}}`
- 文案內容 fragments

## 5. Mermaid Rules

如果 manual 有 UX flow diagrams：

1. 在 `{{OPTIONAL_MERMAID_SCRIPT}}` 放入 Mermaid loader
2. 在每個 diagram block 中加入 `accTitle` 與 `accDescr`
3. 在圖後加一段 plain-language summary
4. 不以顏色作為唯一語意

如果 manual 沒有 diagram，`{{OPTIONAL_MERMAID_SCRIPT}}` 可以留空。

## 6. What to Preserve from Reference Manuals

這份 template 主要抽取自兩份 reference manual：

- `~/projects/template-orchestrator/docs/manual/{lang}/index.html`
- `~/projects/llm-agent-gateway/docs/manual/en/index.html`

要保留的是：

- Corporate Identity System 視覺語言
- sticky sidebar + scrollspy navigation
- screenshot / evidence card presentation
- backend-heavy manual 對 CLI / readiness / warnings 的支撐能力

不要保留的是：

- 專案特定內容
- 專案特定路徑
- 專案特定 screenshot / sample asset links

## 7. Agent Constraints

- 若這份 template 能滿足需求，**不要從零生成 HTML shell**
- 若需要擴充，優先：
  - 新增 section content
  - 覆蓋 CSS variables
  - 在 `{{EXTRA_HEAD}}` 或 `{{EXTRA_SCRIPTS}}` 放最小補充
- 若真的需要新 layout pattern，先說明為什麼既有 template 不足，再做最小擴充
