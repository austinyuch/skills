---
name: user-manual-skill
description: 為當前專案生成基於 UX flow、Use case 與真實產品操作面的使用者手冊 (User Manual)。當使用者要求「建立操作手冊」、「生成使用說明」、「建立 manual 文件」、「更新系統手冊」，或任何需要把 Web App、Backend/API、CLI Tool、Operator Workflow、Report Artifact、Governance/Readiness surface 整理成可操作文件的場景時，應啟動此 skill。對 Web App 優先結合 E2E/Playwright 截圖；對 Backend/Tool/CLI 產品則改用命令、輸出、報告 artifact 與 review/governance evidence 作為主要證據，不可強迫套用 screenshot/VRT-first 標準。
---

# User Manual Skill — 使用者操作手冊生成器

## 目標

分析當前 workspace 的專案規格、UX 流程與主要產品操作面，生成一份高質量的使用者手冊。包含：

- 基於 UX Flow 與 Use Case 的操作動線說明。
- 對 Web App：逐個功能頁面的詳細解說（特別針對列表頁、詳情頁及各類按鈕功能），必要時結合 E2E 測試（如 Playwright）自動擷取畫面截圖，並可作為 VRT 的防呆基準。
- 對 Backend / Tool / CLI：以命令範例、結構化輸出、報告 artifact、API/contract、review/governance 文件作為主要證據，不可用「缺少瀏覽器截圖」直接推論產品不真實或不具 production relevance。
- 對 Hybrid 系統：同時保留瀏覽器畫面與 backend/tool evidence，但必須分開標示，不可把局部 evidence 自動上升為整個產品的 production status。
- 整合 `.agents/specs/SPECS.md`、`docs/*FEATURE*.md`、`docs/*SPECS*.md` 中的規格內容。

輸出固定路徑：`docs/manual/` 及其子目錄（如 `docs/manual/index.html` 或 `.md`）。

## Scope Boundary

- 此 skill 的責任是產出 **artifact-honest** 的操作手冊，讓讀者理解如何操作、觀察、解讀產品 surface。
- 此 skill **不是** live-demo readiness authority；不得自行裁決某個產品、功能或系統是否 production-ready。
- 權威的 `PASS / CONDITIONAL / FAIL` 仍來自 `.agents/specs/**/review.md` 或其他 runtime-backed review artifact。
- 若文件中某一節使用 screenshot、CLI output、report artifact、API payload、ASCII illustration 或 placeholder，這些 evidence 只描述 **該節 / 該 artifact** 的證據強度，不自動等於整個產品的 production status。

## Benchmark / Sandbox Mode

- 若當前工作是 **skill benchmark、sandbox smoke run、prompt evaluation、manual dry-run、或任何明確要求不要影響 production 文件** 的情境，必須進入 **non-destructive benchmark mode**。
- 在 benchmark mode 中，既有 `docs/manual/**`、`docs/review/**`、專案內的 `MANUAL_GENERATION_GUIDE.md`、以及其他 tracked production artifact 都只可作為 **read-only input**。
- benchmark mode 的所有輸出必須寫入明確的 sandbox root（例如 `{repo}/temp/manual-skill-benchmark/<run_id>/`），不可直接寫回 production manual 路徑。
- 若 benchmark / dry-run prompt 已提供 output contract，必須先滿足該 contract，再決定是否產生額外 repo-specific artifacts。
- 除非使用者明確要求 in-place 更新 production manual，否則在存在既有 manual 的專案中，優先問自己：「這次是要正式更新，還是先做 sandbox benchmark？」若答案不明，預設採 sandbox benchmark。

---

## Phase 1：探索規格與分析 UX 流程

**前置作業 (Pre-flight Check)**:
強制檢查當前 workspace 是否存在專案專屬的 `docs/manual/MANUAL_GENERATION_GUIDE.md`。
- 每個專案 (Workspace) **必須**維護一份專屬的 Manual 規範文件，定義該專案特有的 UX flow、角色權限、截圖目標及測試資料。
- 如果專案內不存在，你**必須**先參考 `~/.config/opencode/skills/user-manual-skill/references/MANUAL_GENERATION_GUIDE.md` 自動生成一份初始的專案級規範至 `docs/manual/MANUAL_GENERATION_GUIDE.md`，再繼續後續流程。

### 前置規則：樣本資料與 Fixture 管理

- 不得使用 `temp/` 或行內常數作為長期樣本資料來源；若手冊截圖、示範帳號、或畫面 seed data 需要重複使用，必須沉澱成 **canonical scenario**。
- E2E / screenshot 測試應透過 fixture / helper / adapter 層讀取這些 canonical scenarios，不應在每支 screenshot spec 中重複硬編 JSON 或路徑。
- 專案專屬的 `MANUAL_GENERATION_GUIDE.md` 應記錄具體的樣本資料位置、截圖輸出目錄、與生成命令；global skill 只提供原則，不承載專案硬編路徑。
- 💡 **原因 (WHY)**：避免手冊生成過程依賴暫存檔或 session 內即興資料，並確保 manual / demo / review / e2e 使用同一套真實情境。

### 前置規則：Readiness Claim Cap

- `user-manual-skill` **不自行裁決** 某功能是否真正 demo-ready；它必須優先讀取 `.agents/specs/**/review.md`、`SPECS.md`、或其他已存在的 review evidence 摘要，沿用其中的 `Live-Demo Readiness`、`Coverage Tier`、`Evidence Source`。
- `RTM.md` 若存在，只可作為 cross-spec traceability / verification context；不得被當成 readiness authority 或取代 `review.md`。
- 若 readiness/evidence 欄位不存在，必須把對應畫面標示為 `not_assessed`，並視情況附上 `DEMO_NOT_ASSESSED` 或 `ARTIFACT_HONESTY_GAP`，而不是自行腦補成 ready。
- 手冊屬於 stakeholder-facing artifact，對外說明必須採取 claim cap：mock-backed / illustrative / fixture-backed screenshots 不可被包裝成真實整合證據。
- warning code 與 evidence label 命名請與共用 taxonomy 對齊：`../../docs/DEMO_RISK_WARNING_TAXONOMY.md`。
- 共用 evidence 欄位語意、caption/alert 呈現要求與 claim-cap 邊界，請對照 `../../docs/EVIDENCE_METADATA_CONTRACT.md`。

### 前置規則：Benchmark Output Contract（當 benchmark mode 啟用時）

若當前是 benchmark / smoke run / sandbox evaluation，至少應產出下列最小工件集合，除非使用者或專案 contract 明確改寫：

1. `benchmark-manual-plan.md`
2. `notes/run-note.md`
3. `notes/benchmark-summary.md`
4. `outputs/benchmark-evidence-map.json`

允許額外的 repo-specific artifact（例如 `claim-cap-summary.md`、`outputs/en/index.md`、`outputs/zh-tw/index.md`、`mcp-tool-surface-draft.md`），但它們不可取代上述四個 minimum artifacts。

### 產品操作面分類 (Product Surface Classification) — Mandatory

在進入 Phase 2 任何截圖或 artifact 擷取前，先判斷此手冊的主要產品操作面，並選擇對應 lane：

1. **Web-App Dominant**
   - 主要操作面是瀏覽器 UI、頁面 flow、表單、列表/詳情、互動元件。
   - 主要 evidence 可來自 Playwright / screenshot / 視覺流程驗證。

2. **Backend / Tool / CLI Dominant**
   - 主要操作面是 CLI command、API behavior、daemon/service startup、machine-readable report、governance/readiness contract、local/runtime/bootstrap command。
   - 主要 evidence 應來自 command transcripts、structured outputs、report artifacts、contract / review 文件，而不是瀏覽器截圖。

3. **Hybrid**
   - 同時包含可操作 UI 與 backend/tool surfaces。
   - 需同時採集 browser evidence 與 backend/tool evidence，但必須分開標示，不可把其中一面的局部證據自動升格成整體產品狀態。

若專案主體為 Backend / Tool / CLI Dominant，**不得**要求 screenshot / VRT 成為主要 production evidence gate；瀏覽器截圖在這類產品中只能是次要或可選證據。

從以下來源蒐集專案資訊（並行讀取，不存在的跳過）：

```text
docs/manual/MANUAL_GENERATION_GUIDE.md  ← [必須] 專案專屬的 manual 生成與截圖規範
README.md / README_*.md                 ← 專案介紹、目標受眾
docs/*FEATURE*.md                       ← 功能清單文件
docs/*SPEC*.md                   ← Spec清單文件
.agents/specs/SPECS.md           ← 主要 Spec 清單與設計
docs/**/*.md                     ← 其他設計文件
.kiro/specs/**/*design*.md       ← 介面設計與互動規格
```

**分析任務**：
1. 提取系統中的核心 **Use Cases** 與 **UX Flows**。
2. 判斷主導操作面是 Web-App Dominant、Backend / Tool / CLI Dominant，還是 Hybrid。
3. 若存在 UI，辨識所有關鍵的 UI 頁面（特別標註「列表頁 List」與「詳情頁 Detail」）。
4. 若存在 CLI / Backend / Tool surface，盤點核心 command、API route、report artifact、runtime/governance command 與其輸出型態。
5. 盤點每個主要 surface 中的關鍵操作：按鈕、命令、旗標、輸出區塊、readiness / governance 解讀點。

---

## Phase 2：準備與執行 Evidence Capture

為確保手冊中的 evidence 與產品真實操作面一致，依產品分類選擇對應的 evidence capture 方式。Web-App Dominant 才以 Playwright / screenshot 為主；Backend / Tool / CLI Dominant 則以 command、輸出、報告 artifact 與 contract/review evidence 為主。

### 2.0 Registry-first runtime preflight (Mandatory)

- 若手冊 evidence capture 需要真實啟動、重用、或操作 local dev / UAT / E2E 服務（包含 screenshot flow、CLI / bootstrap command、API / report artifact capture），必須先遵守 `local-infra-registry-governance`。
- 不可在手冊流程中自行猜測 localhost ports、compose stack names、或直接用 ad-hoc 指令啟動服務。
- 若專案已有 registry-governed env allocation，應優先 reuse；若當前 project-instance 尚無 registry entry，但 current state 可辨識，應先交由 `local-infra-registry-governance` 做 bootstrap registration；若 allocation 不明、registry 不可讀、或 tool 缺失，才停止真實 evidence capture，改走明確的 non-runtime fallback，或回報 blocker，而不是繞過治理流程。
- 若 exact instance 不存在但 project 下仍有多個 plausible candidates，必須先做 developer HITL selection 或明確新建，不能由 agent 自行推論同意詞 / 可重用 instance。

### 2a. Web-App Dominant：自動化生成截圖腳本 (Mandatory)
必須檢查 `tests/e2e/` (或專案對應的 E2E 目錄) 是否存在專為手冊截圖設計的測試檔（如 `manual-screenshots.spec.ts`）。
若不存在或不完整，**你必須自動生成或更新該 Playwright 測試腳本**，並滿足以下要求：
- 掛載穩定的 Mock Data。
- 依循 UX Flow 進行逐步操作（如：登入 -> 進入列表 -> 點擊第一筆進入詳情 -> 點擊編輯按鈕）。
- **嚴格的截圖命名與路徑規範**：
  - 截圖必須輸出至 `docs/manual/assets/` 目錄。
  - 命名格式必須為：`{feature}-{usecase}-{step}.png`。
  - 範例：`page.screenshot({ path: 'docs/manual/assets/order-management-review-01-list.png' })`。
- 確保腳本中同時包含 VRT 斷言 `expect(page).toHaveScreenshot()`。
- 對每張截圖，必須依 `../../docs/EVIDENCE_METADATA_CONTRACT.md` 同步產生 evidence metadata（直接嵌入手冊章節或相鄰 caption/alert，不可只留在生成過程）。
- 若截圖流程涉及登入、SSO、session refresh、RBAC、impersonation、或任何需要 auth context 的畫面，必須額外確認 auth state 來源：
  - 是真實 auth flow / 真實 token / 真實 demo account
  - 還是 storageState / fixture / 預先注入的 session
- 若是後者，必須明確標記 `AUTH_FIXTURE_COUPLING`，不要只寫模糊說明。

### 2b. Web-App Dominant：執行截圖擷取
執行對應的測試指令（如 `npx playwright test tests/e2e/manual-screenshots.spec.ts`）前，必須先確認 runtime 已在 governed allocation 內就緒。只有在 allocation / ownership / TTL 都明確，且 required service bundle 全部 ready 時，才等待截圖生成於 `docs/manual/assets/` 目錄中；否則應改走 non-runtime fallback 或回報 blocker。

若進入 non-runtime fallback（例如示意圖、placeholder、既有 fixture-backed screenshot），必須在最終手冊中對該畫面附上清楚標示：`Illustrative Only — live runtime unavailable`，並同步標記 `DEMO_NOT_ASSESSED` 或 `ARTIFACT_HONESTY_GAP`（依情境）與 `Fallback Reason`。fallback 只能補足說明，不可冒充真實 evidence。

### 2c. Backend / Tool / CLI Dominant：Evidence Capture (Mandatory)

若主要產品操作面不是瀏覽器 UI，而是 backend / tool / CLI，必須改採下列 evidence capture 方式作為主路徑：

- **Command examples**：實際存在於產品 surface 的命令、子命令、flag、參數與路徑。
- **Command outputs / structured payloads**：stdout、stderr、JSON、YAML、report snippet、machine-readable artifact。
- **Runtime / bootstrap / governance outputs**：health check、bootstrap command、provider/gateway policy、review/governance 文件中的可操作證據。
- **Spec review evidence**：`.agents/specs/**/review.md`、`SPECS.md`、其他已存在的 readiness / governance 文檔。

可接受的 artifact 類型包含但不限於：

- `docs/manual/assets/{section}-{command}-{step}.txt`
- `docs/manual/assets/{section}-{artifact}-{step}.json`
- `docs/manual/assets/{section}-{artifact}-{step}.md`
- `docs/manual/assets/{section}-{artifact}-{step}.png`（僅當 CLI output 以 terminal screenshot 呈現或系統確有 UI 輔助時）

對 Backend / Tool / CLI lane，驗證重點不是 `toHaveScreenshot()`，而是：

- 命令 / 路徑 / API 示例是否真的是產品 surface 的一部分。
- 輸出範例是否對應真實 command / artifact，而不是憑空手寫模板。
- 內容是否清楚區分 executable surface、illustrative diagram、以及治理文件摘要。
- evidence metadata 是否貼合該 artifact，而非沿用 web-app screenshot 的語意偷換。

若 runtime 無法取得或 command 無法安全執行，可使用 fallback artifact（例如 illustrative output sample、ASCII flow、static placeholder），但必須明確標記 `Illustrative Only`、`Fallback Reason`，以及 `DEMO_NOT_ASSESSED` / `ARTIFACT_HONESTY_GAP` 等 canonical code。

### 2d. Hybrid：雙 lane evidence capture

若系統同時包含 UI 與 backend/tool/CLI surfaces：

- Web UI 依 2a / 2b 處理。
- Backend / Tool / CLI 依 2c 處理。
- 在手冊中明確標示哪一節是 UI evidence、哪一節是 backend/tool evidence。
- 不可因為某張 screenshot 存在，就推論同流程中的 CLI / API / report 已完成真實整合；反之亦然。

---

## Phase 3：撰寫與組裝手冊內容

根據擷取到的截圖與規格文件，生成操作手冊的內容。

### 3.0 Benchmark mode minimum outputs

若 benchmark mode 啟用，請先穩定產出最小比較工件，再決定是否進入完整 manual generation：

- `benchmark-manual-plan.md`：本次 sample repo 的 manual strategy、surface classification、claim-cap 邊界與產出計畫。
- `notes/run-note.md`：本次選了哪些 surface、避開了哪些 production paths、如何保持 section-level 與 product-level 邊界。
- `notes/benchmark-summary.md`：success signal checklist、minimum artifact 是否齊備、主要觀察與下一輪改善建議。
- `outputs/benchmark-evidence-map.json`：machine-readable 的 section → artifact → evidence metadata 對照表。

只有在 benchmark 目標明確要求評估完整 manual composition 時，才繼續產生 `outputs/en/index.md`、`outputs/zh-tw/index.md`、HTML、截圖、或其他更重的 artifact。

### 3a. 目錄結構與導覽 (Index)
建立手冊首頁 `docs/manual/index.md` (或 HTML)，包含：
- 系統簡介
- 依據目標受眾劃分的快速導覽
- UX 流程清單

### 3a.1 Starter Assets / Getting Started 區塊 (Mandatory)
手冊首頁或前段章節必須包含一個明確的 **Getting Started / Starter Assets** 區塊，幫助使用者快速開始，而不是假設使用者已經擁有正確的 template 與 sample data。

此區塊至少要說明：
- 可以直接開始使用的 template 範例（例如 DOCX / XLSX）
- 可搭配的 sample data / render payload / scenario data
- 每個樣本的用途（template upload、render input、page-builder state、expected output）
- 使用者如何下載這些樣本

如果專案已經有 git-tracked 的 canonical samples，手冊應優先連到這些檔案，而不是只用文字提及檔名。

### 3b. UX Flow 完整教學
為每個核心使用案例建立獨立章節（例如 `docs/manual/flows/order-processing.md`）。
每個流程需包含：
- **情境描述**：誰在什麼情況下需要執行此流程。
- **步驟 evidence**：按順序置入 Phase 2 產生的截圖、command outputs、report artifacts 或其他對應 evidence，並附上具體的操作說明。
- **相對路徑嵌入**：所有圖片引用必須使用相對路徑（如 `![步驟一](../assets/01-order-management-01-list.png)`），以確保輸出至 HTML 時破圖風險降到最低。
- 若當前 evidence 不是最貼近產品 surface 的 live evidence（例如 `live_screenshot`、live command output、真實 report artifact），步驟說明必須採用保守措辭，並搭配 canonical code（例如 `MOCK_DOMINANT_EVIDENCE` 或 `DEMO_NOT_ASSESSED`），而不是暗示該流程已完成真實整合驗證。

若相關 spec 在 `SPECS.md` 中有 `Open Change Requests`、`CROSS_SPEC_DEMO_DEPENDENCY`、或 `Live-Demo Readiness != PASS`，手冊仍可生成，但對應章節必須誠實揭露此限制，不可寫成已完整驗證的正式操作基準。

若手冊章節宣稱具備 BI / dashboard / chart 功能，所使用的截圖必須證明圖表已實際渲染資料，而不是只有 builder 中的 chart 區塊或空白外框。

### 3b.1 Evidence Scope Rule — Mandatory

必須在手冊撰寫時明確區分：

- **Section-level evidence**：此截圖、此 command output、此 report artifact、此 API payload 只證明該節描述的操作面或 artifact。
- **Product-level production status**：整個產品 / 功能 / journey 是否 ready，只能沿用 `review.md` 或其他權威 runtime-backed artifact 的結論。

因此：

- `Coverage Tier` 與 `Evidence Source` 首先描述的是 **這一節 / 這一張圖 / 這一段輸出** 的證據。
- 它們 **不自動等於** 整個產品 implementation 的總結。
- 一張 `css_illustration` 或 fallback CLI sample 可以是 `mock-heavy`，但背後對應的 backend/CLI feature 仍可能在別處由 `hybrid` 或更強 evidence 支撐；反之亦然。
- 任何 `ready`、`validated`、`full-integration` 類措辭，只能在 product-level authority 已明確給出對應結論時使用。

### 3b.2 Evidence Map Vocabulary (Recommended)

若需要產出 `benchmark-evidence-map.json` 或其他 machine-readable evidence index，建議使用下列 canonical lane values：

- `ui`
- `backend-tool-cli`
- `hybrid`
- `governance`

而 `coverage_tier` 應優先沿用：

- `full-integration`
- `hybrid`
- `mock-heavy`
- `not_assessed`

這些欄位是 section-level / artifact-level 證據語彙，不是產品總結 verdict。

### 3c. 功能與頁面詳解 (列表與詳情)
針對共通的頁面模式（如 List-Detail），建立詳細說明（例如 `docs/manual/features/list-and-detail.md`）：
- **列表頁 (List Page)**：
  - 截圖展示。
  - 欄位定義對照表。
  - 篩選器、分頁、排序功能的使用說明。
  - 批次操作與各單行操作按鈕的功能。
- **詳情頁 (Detail Page)**：
  - 截圖展示。
  - 資料區塊說明。
  - 狀態變更按鈕（核准、退回等）的操作結果。

若產品操作面主要不是列表/詳情頁，而是 CLI / Tool / Backend flow，則以等價的產品 surface 章節取代，例如：

- **CLI Workflow**：command syntax、flag behavior、output interpretation、error handling。
- **API / Contract Workflow**：request / response shape、governance/readiness interpretation、artifact path。
- **Report / Artifact Interpretation**：如何讀取報告欄位、warning code、decision output、runtime/gateway policy。

### 3d. Download Mechanism (Mandatory)

手冊若提到 template、sample data、starter payload、builder scenario 或 expected output，應提供具體的下載機制：

- **Markdown**：使用相對路徑連結到可下載檔案。
- **HTML**：使用明確的下載按鈕 / 卡片 / 連結，讓使用者可直接取得檔案。

不要只列出檔名而沒有下載方式；對初次使用者而言，能否取得正確的 starter assets 直接影響手冊的可用性。

---

## Phase 4：生成與輸出 (四象限強制輸出：雙格式 × 雙語系)

為確保使用者手冊的完整覆蓋率，必須嚴格遵守以下四個實體檔案的產出規範：
1. **`docs/manual/en/index.md`**：純文字備查來源 (English)。
2. **`docs/manual/zh-tw/index.md`**：純文字備查來源 (Traditional Chinese, zh-tw)。
3. **`docs/manual/en/index.html`**：視覺化操作手冊 (English)。
4. **`docs/manual/zh-tw/index.html`**：視覺化操作手冊 (Traditional Chinese, zh-tw)。

### HTML 視覺化設計規範

在生成 HTML (`en/index.html`, `zh-tw/index.html`) 時，請強制呼叫相關的設計 skills (`brand-guideline-company`, `mermaid-brand-theme`, `frontend-design-skill`, `ui-skill`) 進行精美的 UI 轉換。HTML 排版應遵循：
- **the organization CIS 品牌色彩** (若為 組織相關專案，由 `brand-guideline-company` 控制)。
- **Mermaid 渲染與 WCAG 檢核**：
  - 手冊內的流程圖 (UX Flow) 應採用 Mermaid 渲染 (可搭配 `mermaid-brand-theme` 主題)。
  - **強烈要求符合 WCAG 無障礙規範**：請確保 Mermaid 圖表與 HTML 文字的色塊對比度足夠（例如：深色背景配白字，或淺色背景配深色字），文字大小適中（大於 14px），避免難以閱讀的情況。
- 清晰的版面結構（左側固定導航樹/側邊欄，右側為動態切換的教學內容區塊）。
- 圖文並茂的卡片式設計，截圖以微圓角 (border-radius) 與微陰影 (box-shadow) 呈現，下方必須有對齊的圖說（Caption）。
- 每張截圖 / 示意圖 / command output / report artifact 的 Caption 或相鄰 Alert 必須至少包含 `Evidence Source`、`Coverage Tier`、`Readiness State`；若存在 `AUTH_FIXTURE_COUPLING`、`MOCK_DOMINANT_EVIDENCE`、`DEMO_NOT_ASSESSED`、或 `ARTIFACT_HONESTY_GAP`，也必須可見呈現。
- 若要顯示 product-level readiness summary，必須明確標註其來源來自 `review.md` 或其他權威 artifact；不得把 section-level evidence label 偽裝成產品總結。
- 提醒與注意事項使用醒目的 Banner 或 Alert 元件標示（例如 `> ⚠️ 注意：...` 轉換為黃色/紅色的警告區塊）。
- 支援響應式網頁設計 (RWD)，確保在不同裝置上閱讀順暢。

---

## Phase 5：最終檢核 (Validation)

當四份文件 (Markdown/HTML, EN/ZH-TW) 建立完成後，必須進行最終檢核防呆：
1. **確認對應 lane 的 evidence capture 資產已生成**：
   - Web-App Dominant：確保 E2E `manual-screenshots.spec.ts` 已被建立或更新。
   - Backend / Tool / CLI Dominant：確保 command/output/report artifact samples 已寫入 `docs/manual/assets/`。
   - Hybrid：兩者都要存在，且章節分界清楚。
2. **確認專案專屬指南已生成**：確保 `docs/manual/MANUAL_GENERATION_GUIDE.md` 確實存在。
3. **進行 HTML / asset rendering 防呆**：
   - 使用 `playwright` 相關 tool 分別開啟 `docs/manual/en/index.html` 與 `docs/manual/zh-tw/index.html`。
   - 進行網頁全頁截圖 (`page.screenshot()`)。
   - 讀取並檢視截圖，確認：
     - CSS 是否正常載入（無破圖、無跑版）。
     - Mermaid 圖表是否正常渲染且文字清晰可見（符合 WCAG 對比度）。
     - Screenshot、command output、report artifact 等相對路徑是否正確顯示或可下載。
     - 每個 evidence block 是否正確顯示 `Evidence Source` / `Coverage Tier` / `Readiness State`，且 fallback / auth fixture / mock-dominant 情況有對應 canonical warning code。
     - 若手冊宣稱 chart/BI capability，圖表必須是真正渲染完成的 evidence，而不是空白 chart container。
     - 若顯示了 product-level readiness summary，來源必須清楚，且不可與 section-level evidence 混淆。
     - 若有版面問題，返回 Phase 4 修正 HTML。

完成後，向使用者回報：包含自動化腳本、指南、Markdown 及雙語 HTML 的手冊建立完畢。
