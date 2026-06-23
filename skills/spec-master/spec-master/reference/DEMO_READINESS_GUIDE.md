# Live Demo Readiness Guide

當功能涉及 UI、manual、project review、dashboard、auth、E2E、demo script、screenshot、或任何要對利害關係人展示的流程時，請在 Phase 4 與 Phase 5 額外套用本指南。

若需要使用標準化 warning code，請對照共用 taxonomy：`../../docs/DEMO_RISK_WARNING_TAXONOMY.md`。

## 1. 先做風險分類

把目前驗證路徑標成以下其中一類：

| Tier | 定義 | 可回答的問題 | 仍回答不了的問題 |
| --- | --- | --- | --- |
| `mock-heavy` | 主要依賴 `page.route()`、HAR、mock helpers、fake providers、固定 API response、storageState、或 auth fixture | UI 有沒有照預期呈現？互動流程有沒有跑完？ | backend contract 有沒有漂移？真實 auth 有沒有通？demo data 會不會是假的？ |
| `hybrid` | 部分路徑打真實 backend 或真實 auth，其他仍用 mocks/fixtures 輔助 | 關鍵旅程大致是否可用？實際 API/schema 是否至少有一條路徑驗證？ | 還有哪些支線仍被 mock 掩蓋？demo artifact 會不會誤導？ |
| `full-integration` | 關鍵旅程以真實 backend、真實 auth、真實 service bundle 完成 smoke 或 manual 驗證 | live demo 主要風險是否已被實際證據覆蓋？ | 邊角情境與高成本支線仍可能未覆蓋 |

預設規則：`mock-heavy` **不能** 直接推出「live demo ready」。

## 2. 必查短路機制

若找到下列任一項，必須記錄它短路了哪些風險：

- `page.route()` / `browserContext.route()`
- `routeFromHAR()` / HAR replay
- `mock*` helpers / fake providers / canned responses
- `gotoAuthenticated`、`storageState`、預先灌入 cookies / tokens
- fixed API response / fallback response / silent "Mock response"
- screenshot fixtures / seeded demo payload / chart shell only screenshots

對每一項都回答三個問題：

1. 它是為了速度、穩定性，還是因為真實整合尚未可用？
2. 它讓哪些 backend / auth / data 問題無法被發現？
3. demo 前是否已有對應的 real-backend / real-auth smoke path 補回來？

## 3. 高風險關鍵旅程清單

以下路徑若存在，至少要有一條真實整合證據：

- login / logout / token refresh / SSO / MFA
- RBAC / impersonation / tenant switch
- dashboard data loading / chart rendering / summary counters
- 查詢列表 + 詳情頁的真實資料載入
- 任何 project review / user manual 會截圖展示的核心流程

如果上述任一路徑只有 fixture 或 mock 驗證，review 結論至少降為 `CONDITIONAL`。

## 4. Artifact 誠實標示規則

下列 artifact 若來自 mocks / fixtures，必須明確標示：

- project review HTML / executive summary screenshots
- user manual 截圖
- dashboard / chart evidence
- demo script 中引用的預期畫面

可接受的標示方式例如：

- `Evidence Source: fixture-backed UI regression screenshot`
- `Evidence Source: real-backend smoke run in demo env`

禁止把 fixture/mock 產生的畫面描述成「真實整合已驗證」。

## 5. Review Gate 結論規則

| Result | 何時使用 |
| --- | --- |
| `PASS` | 關鍵旅程已有 real-backend / real-auth evidence，mock 只扮演輔助角色，artifact 標示清楚 |
| `CONDITIONAL` | 主要功能大致可運作，但仍有局部 mock blind spot、auth fixture 耦合、或 artifact 標示不足 |
| `FAIL` | 目前仍主要靠 mock/fixture/fake auth 支撐，或 project review / manual artifact 足以誤導利害關係人 |

## 6. 代表性失敗訊號

- 測試只檢查 `waitForResponse(... status() === 200)`，沒有驗證資料內容
- fake provider 在未命中 pattern 時回傳預設成功內容
- storageState 讓測試跳過真正 login，但 review 沒有補 auth smoke
- screenshot 只有 chart shell / builder shell，卻被當成 dashboard evidence
- demo account / demo seed data 其實只存在於 CI fixture，不存在 demo env

## 7. 推薦補救順序

1. 先補一條 real-backend / real-auth smoke path
2. 再盤點 mock / fixture 仍保留的必要性
3. 最後更新 review / manual / project review artifact 標示，避免 false-green 敘述
