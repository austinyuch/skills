# Value-Driven Copy Guide (Generator)

面向潛在使用者的 showcase 文案配方。目標：讀者看完想試用、想轉換。語言依專案現有頁面 / README 主要語言。

## 語氣原則

| 原則 | 說明 |
|---|---|
| **Outcome-first** | 先講使用者得到的結果，再講功能。標題是承諾，不是描述。 |
| **第二人稱** | 用「你 / your」。讓讀者看見自己。 |
| **具體勝於形容詞** | 「live in days」「0 rebuilds」「no developers」勝過「powerful」「flexible」「seamless」。 |
| **Benefit 不是 mechanism** | 每個技術能力翻成「對你的好處」。讀者不在乎它怎麼實作。 |
| **一個賣點一句話** | 不要把三個概念塞進一句。短、強、可掃讀。 |
| **CTA 是動作** | 動詞開頭、低摩擦：「Create your own site」「Watch a free lesson」「Book a session」。 |

## 版面上下順序（conversion 敘事流）

公開頁是**從上往下被讀的一條說服路徑**，不是 section 的隨機堆疊。預設用這個敘事弧（hook → 為何 → 價值 → 證明 → 怎麼做 → 深度 → 信任 → 行動）排列，讓讀者每往下捲一屏就更想轉換：

| # | 區塊 | 角色（為何放這個位置） |
|---|---|---|
| 1 | **Hero** | Hook：outcome headline + 一句 value prop + 雙 CTA。3 秒內接住「這對我有什麼好處」。 |
| 2 | **Problem / 現況** | 共鳴：點出今天的痛 / workaround，讓讀者「對，就是這個」。（B2C 可省，B2B/NGO 很有效） |
| 3 | **核心價值 — 3 benefits** | 主張：最重要的 3 個好處，benefit 標題 + 一句使用者語言。 |
| 4 | **社會證明 / outcome stats** | 取信：把主張變可信——outcome 數字、見證、logo。**緊接價值之後**趁讀者還熱。 |
| 5 | **How it works（3 步）** | 降低門檻：證明「很簡單、我也能做到」，消除「聽起來很難」的顧慮。 |
| 6 | **次級功能 / 垂直範例** | 深度：給還在猶豫的人更多理由 / 具體場景；放後面，不稀釋前面的主訊息。 |
| 7 | **信任（安全 / 你的資料 / 無鎖定）** | 解除最後顧慮：把常見反對意見（資料安全、被綁死）在 CTA 前處理掉。 |
| 8 | **Final CTA** | 收網：重申**與 hero 相同**的主要轉換動作。讀到底的人意圖最高。 |

**原則 > 模板**：要守的是這條敘事弧（hook → 為何 → 價值 → 證明 → 怎麼做 → 深度 → 信任 → 行動），不是死板的 8 格。可依專案合併 / 增刪：

- 沒有真實 proof 時，第 4 區用具體能力（「0 rebuilds」「8 built-in capabilities」）代替假數據 / 假見證——不要捏造。
- 垂直 demo 頁（家教 / 商店）：第 2~3 區換成該垂直的痛與好處，第 5 區常是「3 步開始（看 → 試 → 約）」。
- 短 landing 可壓成 Hero → 3 benefits → proof → CTA。
- **關鍵錯誤要避免**：proof / stats 落在頁尾（沒人看到）、Final CTA 與 hero 不一致、功能清單（第 6 區）排在價值與證明之前稀釋主訊息。

> **重排既有頁 = data-only**：調整上下順序只是重排 `pages.sections` 陣列的順序（不新增元件），屬純資料變更（seed → DB upsert），**不需要重建 image**。仍要照 jargon-sweep checklist 對 live render 驗證。

## 各區塊配方

每個 section 都要 value-driven。對照上面的上下順序使用。

### Hero（位置 1）
- **Headline = outcome promise。** 「使用者最想要的結果」+ 可選差異化（速度 / 無痛 / 無鎖定）。常是 PR headline 或 value-prop 一句話的精煉。
- **Mission-driven / B2B / NGO 變體：** headline 可先用一句**信念 / 立場句**點出「為何這件事值得改變」，把 outcome 收進 subhead——對使命型受眾，先給「為何」比先給「結果」更容易黏住。信念可 aspirational，但不可捏造使命 / 立場。
- **Subhead = 能力的好處**串成一句。
- **CTA × 2：** 主要 = 最高意圖轉換（註冊 / 開始）；次要 = 低承諾探索（看 demo / 看範例）。

### Problem / 現況（位置 2）
- 一句點出痛 + 一句點出舊 workaround 的代價（慢 / 貴 / 要工程師）。簡短，別變抱怨文。
- 使命型受眾可把這段框成「為何現狀該被改變」的立場，承接 hero 的信念句後再進入價值，讓「為何」一路鋪到「能做什麼」。

### Feature grid / 核心價值（位置 3）
- 標題講「你能做到什麼」（例：「Everything you need to launch and grow」），不是「它有什麼」。
- 每張卡：benefit 標題 + 一句使用者語言；把 mechanism 翻成 outcome。

### Stats / proof（位置 4）
- 用 outcome 數字，不是內部指標。壞：「99% DB-driven」「12 tenants onboarded」；好：「0 rebuilds to publish」「live in days」「100% your data & keys」。

### How it works（位置 5）
- 3 步，動詞開頭，每步一句。讓人覺得「今天就能開始」。

### 次級功能 / 垂直範例（位置 6）
- 場景化的補充理由；可放 gallery（仍用使用者語言標題，見內頁規則）。

### 信任（位置 7）
- 安全 / 你的資料 / 無鎖定 / 支援。針對最常見的購買顧慮。

### Final CTA（位置 8）
- 一句「準備好了嗎？」+ 重申主要轉換動作，和 hero 主 CTA 一致。

### 內頁（about / 子產品 / gallery）
- **about**：講「你能用它做到什麼」與信任點，不要講「fictional studio / demo tenant」。
- **垂直 demo 內頁**：用該垂直終端客戶語言，底部一句不喧賓奪主的「built with …」信任註。
- **component / capability gallery**（常是內部 durable requirement）：仍用使用者語言標題（「Browse & filter your content」而非「ContentSection — filter/sort/paginate」），框成「看看你能打造什麼」。

## Before → After 範例（真實案例）

| Before（內部 / 工程口吻） | After（value-driven） |
|---|---|
| Showcase Studio — a sample tenant; its content lives in its own database (cms_showcase), rendered from DB-driven page sections. | Launch a beautiful, AI-powered website — run every site from one place. |
| Every block on this page is a database-stored section rendered by the platform page builder. | Describe what you want and AI drafts the content and lays out pages you can publish in minutes. |
| Studio in numbers — 99% DB-driven · 12 tenants onboarded | Why it works — 0 rebuilds to publish · 8 built-in capabilities · 100% your data & keys |
| This is a demo tenant — its data is isolated in cms_showcase. | Ready to launch your site? Spin up your own site in minutes — no developers required. |
| A fast campaign microsite assembled entirely from database-stored sections, themeless-first. | A fast campaign microsite built and launched in days — refined on the fly, no rebuilds. |
| ContentSection — filter/sort/paginate | Browse & filter your content |
| Multi-tenant model — database-per-site isolation. | Run many sites — manage every site you launch from one place. |

## CTA / 連結原則（部署中立）

- **同 app 連結**用相對路徑（`/examples`）。
- **跨 app 連結**（註冊 / docs）用 **env-resolved token**（例如 `@cms/signup/...`），由 render 時解析；**不要把正式網域寫死進 committed 內容**。原因：部署網域因環境而異，寫死會在換環境 / 本機瀏覽時壞掉。
- 產出後務必確認 token 在實際 `<a href>` 解析成 URL（見 jargon-sweep-checklist 的 live 驗證）。
