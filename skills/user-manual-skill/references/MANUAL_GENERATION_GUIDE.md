# Manual Generation Guide (使用者手冊生成指南)

> **⚠️ 重要規定 (Workspace-Specific Override)**
> 每個專案 (Workspace) **必須**在其根目錄的 `docs/manual/MANUAL_GENERATION_GUIDE.md` 建立並維護專屬的生成指南。
> 本文件作為全局的基礎範本，當建立新的專案手冊時，請將此範本複製至專案中，並依據該專案特有的 UX flow、角色權限劃分與特殊的截圖需求進行客製化。
> 生成手冊的 Agent 必須以專案內的這份備忘為最高指導原則。

本指南規範了如何為專案自動生成高質量的「使用者手冊 (User Manual)」。生成的目標是建立一份結構化、圖文並茂，且基於實際 UX Flow、Use Case 與主要產品操作面的操作說明文件。若專案主要是 Web App，適合依賴自動化 E2E 測試（如 Playwright）維持截圖與 UI 同步，並視情況做為 VRT 基線；若專案主要是 Backend / API / CLI / Tool，則主要證據應改為命令、輸出、報告 artifact 與 review/governance 文件，而不是強迫採用 screenshot/VRT-first 模式。

## 1. 核心概念與結構

使用者手冊必須依照以下維度進行組織：
- **UX Flow (使用者體驗流程)**: 將單獨的功能串聯為具備商業價值的操作流程（例如：「從建立採購單到核准的完整流程」）。
- **Use Case (使用案例)**: 依照特定角色的特定目的進行章節劃分。
- **Product Surface (產品操作面)**: 先判斷主要是 Web UI、Backend/API、CLI Tool、Report/Artifact，還是 Hybrid；手冊 evidence 必須配合實際操作面。
- **功能詳解**: 若是 Web UI，常見的「列表頁 (List)」與「詳情頁 (Detail)」應有欄位與按鈕操作說明；若是 CLI / Backend / Tool，則以 command / output / report / governance surface 的等價章節取代。

## 2. 文件與規格整合

在生成手冊前，需先整合專案內的現有規格文件：
- 讀取 `.agents/specs/SPECS.md` (spec-driven-development標準spec 登錄表) 
- 讀取 `docs/*FEATURE*.md` (功能清單文件)
- 讀取 `docs/*SPECS*.md`,  或 `.kiro/specs/**/*design*.md` (設計規格文件)

手冊內容應與上述文件對齊，確保手冊中所描述的行為與最新規格一致。

## 3. Evidence Capture 與產品操作面對齊

為了保持手冊 evidence 與實際產品 surface 對齊，先做產品分類：

1. **Web-App Dominant**：主證據是截圖、頁面 flow、Playwright / screenshot / 視覺驗證。
2. **Backend / Tool / CLI Dominant**：主證據是 command output、API payload、report artifact、review/governance 文件。
3. **Hybrid**：同時保留兩者，但分開標示，不可混淆 section-level evidence 與 product-level status。

只有在 Web-App Dominant 時，才把 E2E screenshot/VRT 當成主要 evidence pipeline。

### 3.0 Runtime Governance Boundary

- 若截圖流程需要啟動或重用 local dev / UAT / E2E 服務，必須先走 `local-infra-registry-governance`。
- `manual-screenshots.spec.ts`、helper scripts、或 project guide 都不應直接成為 host port / compose stack allocation authority。
- 若 governed runtime context 不存在，但 current state 可辨識為同一個 project-instance，應先交由 `local-infra-registry-governance` 做 bootstrap registration；若仍無法建立 governed context，才停止真實截圖，改用非-runtime fallback，或回報 blocker；不要自行猜 localhost port 後直接截圖。
- 若 project 已識別但 exact instance 不存在，必須先列出 candidate instances 做 developer HITL selection 或明確新建，才可進入手冊截圖流程。
- 截圖前應確認 required service bundle 全部 ready，而不是只看到某一個 service / port 存活。

### 3.1 Web-App Dominant：截圖腳本設計原則
1. **獨立的 Manual Test Suite**: 在 E2E 測試集中，建立專門用於擷取手冊截圖的測試檔（例如 `tests/e2e/manual-screenshots.spec.ts`）。
2. **模擬穩定資料 (Mock Data)**: 為了確保每次截圖的一致性與避免視覺回歸測試 (VRT) 誤報，截圖時必須掛載固定的 Mock Data，確保列表頁與詳情頁的資料狀態一致。
3. **明確的操作步驟截圖**:
   - **初始狀態**: 進入列表頁後的完整截圖。
   - **互動狀態**: 點擊展開的下拉選單、Hover 狀態的按鈕、填寫完畢的表單等。
   - **列表到詳情**: 點擊列表項目進入 Detail 頁面的過渡截圖。
4. **截圖命名規範**: 
   - `docs/manual/assets/{feature}-{usecase}-{step}.png` (例如: `docs/manual/assets/order-create-01-list.png`)

### 3.2 Web-App Dominant：Visual Regression Test (VRT) 雙重用途
透過設定 Playwright 的 Visual Comparisons (`expect(page).toHaveScreenshot()`)，這些為手冊特化的截圖測試，將同時作為 UI 防呆的基準線。
當 UI 發生非預期變更時，測試會失敗，並提醒開發者：
1. 是否為 Bug？若是，則修復。
2. 是否為預期內的 UI 變動？若是，則更新 VRT 基線，手冊中的截圖也會同步自動更新。

### 3.3 Backend / Tool / CLI Dominant：非瀏覽器 evidence 原則

若專案主要產品 surface 是 CLI、API、daemon、machine-readable report 或治理文件：

1. **以 executable surface 為主**：優先收錄真實命令、真實 API route、真實 artifact path，而不是畫面截圖。
2. **以輸出 / artifact 作為主要證據**：保留 stdout/stderr、JSON payload、report snippet、health check、review/governance evidence。
3. **命名規範一致**：建議使用 `docs/manual/assets/{section}-{artifact}-{step}.txt|json|md|png`。
4. **不要把缺少 screenshot 視為負面證據**：若產品本質上不是 web app，沒有瀏覽器截圖不代表它 mock-heavy 或不具 production relevance。
5. **保守聲明**：若輸出樣本不是來自真實執行，而是 fallback sample / illustration，必須標示 `Illustrative Only` 與對應 canonical warning code。

### 3.4 Evidence Scope Rule

- `Evidence Source`、`Coverage Tier`、`Readiness State` 先描述 **當前章節 / 當前 artifact** 的證據狀態。
- 它們 **不自動等於** 整個產品的 production status。
- 產品層級的 `PASS / CONDITIONAL / FAIL` 只能沿用 `.agents/specs/**/review.md` 或其他權威 runtime-backed artifact。
- 一個章節可以使用 `mock-heavy` illustration，但背後功能可能在別處已有更強 evidence；反之亦然。

## 4. 輸出格式與目錄結構

生成的文件應統一輸出至 `{workspace}/docs/manual/` 目錄。
建議的目錄結構：
```text
docs/manual/
├── index.html 或 README.md       # 手冊首頁與目錄
├── assets/                       # 自動生成的 E2E 截圖、CLI output、report artifact samples
├── flows/                        # 依據 UX Flow 劃分的章節
│   ├── order-management.md
│   └── user-registration.md
└── features/                     # 單一功能/頁面的詳細操作
    ├── list-views.md             # 列表頁通用的篩選、分頁操作
    └── detail-views.md           # 詳情頁的操作與按鈕
```

## 5. 手冊更新流程 (User Manual Skill)

當調用 OpenCode 的 `user-manual-skill` 時，Agent 將會：
1. 分析 `.agents/specs/SPECS.md`, or `docs/*FEATURE*.md` 和現有的 UX Flows。
2. 判斷主要產品操作面是 Web-App、Backend/Tool/CLI，還是 Hybrid。
3. 依 lane 檢查或產生對應的 evidence capture 資產：
   - Web-App → Playwright E2E 截圖腳本
   - Backend/Tool/CLI → command/output/report artifact samples
   - Hybrid → 兩者都要有
4. 組合 evidence 與規格文字，產出完整的 Markdown 或 HTML 操作手冊。
