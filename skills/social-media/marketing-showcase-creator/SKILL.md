---
name: marketing-showcase-creator
description: 為「潛在使用者 / 潛在客戶」打造 value-driven、行銷導向的 showcase / demo 站台內容（公開首頁、landing、產品 demo 站、範例租戶），含明確的 value proposition、Amazon Working-Backwards PR/FAQ、與 gstack CEO/founder viewpoint 觀點陳述。當使用者說「強化 showcase」「showcase 要更行銷」「demo 站要 value-driven」「給潛在客戶看的內容」「公開首頁太工程味/太技術」「marketing copy」「landing page 文案」「把 demo 站寫得更有賣點」「value proposition」「價值主張」「working backwards / 未來新聞稿 / PR FAQ」「用 CEO 觀點陳述定位」「我們的範例站要能轉換」，或任何把面向潛在使用者的公開展示頁從內部/工程口吻改寫成 benefit-led、可轉換的行銷內容時，都應啟動此 skill——即使使用者沒有說出「行銷」二字。注意 audience 區分：本 skill 服務「潛在使用者」(showcase)；若要產出給「高階管理者/operator/評估者」看的 review/簡報，改用 project-review-skill。
---

# Marketing Showcase Creator — 面向潛在使用者的 value-driven showcase 生成器

把一個公開展示頁（showcase / demo 站 / 範例租戶的首頁與內頁）寫成**潛在使用者看了會想試用、會轉換**的行銷內容，而不是給工程師或評估者看的技術說明。

核心信念：**showcase 的讀者是潛在使用者，不是 operator。** 同一個專案，showcase（行銷、value-driven、benefit-led、conversion）與 manual/review（技術、evidence、claim-cap）是**兩種受眾、兩種語氣**，不可混用。把 DB 名稱、「page builder」「sections」「tenant」「manifest」這類內部機制寫進公開頁，就是把內部文件的口吻漏進了行銷面。

## 何時用哪個 skill

| 受眾 | 產物 | 用哪個 |
|---|---|---|
| 潛在使用者 / 客戶（想轉換） | 公開 showcase / demo 首頁與內頁、landing、範例站 | **本 skill** |
| 高階管理者 / operator / 評估者 | executive review、CEO perspective、readiness 報告 | `project-review-skill` |
| operator（怎麼操作） | user manual / how-to | `user-manual-skill` |

兩種受眾常常同時被要求。先分清楚這一頁是給誰看，再選 skill；不要用 review 的 evidence/claim-cap 口吻去寫 showcase，也不要用 showcase 的行銷口吻去寫 review。

> 與 `project-review-skill` 的關係：兩者都會用到 value proposition、Amazon Working-Backwards PR/FAQ、與 gstack CEO/founder lens——但**目的不同**。project-review 把它們寫成給 operator/管理者的**評估文件**（含 claim-cap、bet map、decision memo）；本 skill 把它們當成**萃取公開行銷文案的策略骨架**，最後輸出 benefit-led 的潛在使用者頁面（外加可選的 positioning brief）。

## Workflow（Inversion → Sharpen → Generator → Reviewer）

四階段：先問清楚定位（沒問清楚就會白寫），再用 value-prop / PR-FAQ / CEO viewpoint 把價值想尖，再產出 value-driven 文案，最後做 jargon sweep 並**對著上線後的實際畫面驗證**。

### Phase 1 — Positioning gate（先問，再寫）

定位決定每一句 headline。動筆前先確認**潛在使用者是誰、核心 value message 是什麼**——這通常是使用者的決定，不要自行假設。

問清楚（用具體選項讓使用者挑，附上 hero 文案範例最有效）：

1. **誰是潛在使用者？** 例如：平台本身的 B2B 客戶（「打造你自己的站」）／某個垂直服務的終端客戶（例如家教站賣給學生家長）／代理商客群。不同答案 → 完全不同的 headline。
2. **核心 value message / 一句話定位**是什麼？（通常是 outcome，不是 feature；mission-driven / B2B / NGO 也可能是一句信念 / 立場——「為何這件事該被改變」）
3. **主要轉換動作（CTA）**是什麼？（註冊、預約、聯絡、看更多 demo）

若使用者沒給方向，提出一個推薦定位 + 1–2 個替代，各附一段 hero 文案草稿讓他挑，再開始。**定位錯，後面整頁都要重寫。**

> 也順手確認：這是 **data-only 內容變更**（沿用既有元件 / 版型，只改文案）還是需要新元件？改既有元件的文案多半是純資料變更（seed → DB），不需要重建 image；只有引入新元件才需要重建。先確認，避免誤判工作量。

### Phase 2 — Sharpen the value（value proposition + Working-Backwards PR/FAQ + CEO viewpoint）

載入 `references/value-prop-prfaq-ceo.md`。在寫頁面文案之前，先把價值想尖——產出三件**策略骨架**，它們直接餵養 Phase 3 的 headline / benefit / CTA / 見證：

1. **Value proposition** — 填 canvas（for whom / pain / category / outcome / unlike / proof），壓成一句話（→ hero subhead）。
2. **Amazon Working-Backwards PR/FAQ** — 從**客戶視角**寫一頁未來新聞稿（headline / sub / problem / solution / customer quote / how-to-start）+ 外部 5 問 FAQ。PR headline → hero headline 候選；customer quote → 見證語氣；how-to-start → CTA；FAQ → feature/objection copy。
3. **gstack CEO / founder viewpoint** — 用 wedge（為何明顯更好）、10-star vision（北極星）、why-now、golden-age gain（複雜變簡單/快/便宜 → 使用者 gain）寫 3–5 句觀點陳述，確保定位夠大、夠尖、非 me-too。觀點 adapted from Garry Tan 的 gstack（見 reference 的 attribution；公開頁不需印出）。

**誠實邊界**：行銷可 aspirational，但不得捏造假數據 / 假客戶 / 假見證；無真實數字就用具體能力描述。內部用的 kill-assumption 不進公開頁。

可選交付：把這三件整理成一份 **positioning brief** 給使用者，作為團隊對齊與後續文案的 SSOT（公開頁只放 benefit 版本，strategic backbone 留 brief）。

### Phase 3 — 生成 value-driven 文案（Generator）

載入 `references/value-copy-guide.md` 取得**語氣、版面上下順序（conversion 敘事流）、與各區塊配方**，並把 Phase 2 的骨架落地。

**先定上下順序，再填內容。** 公開頁是一條由上而下的說服路徑——預設用敘事弧排列 sections：Hero → 痛點/現況 → 核心價值(3 benefits) → 社會證明/outcome stats → how-it-works → 次級功能/垂直範例 → 信任 → Final CTA（與 hero 同一個主要轉換）。這是原則不是死模板，可依專案合併增刪；重排既有頁只是重排 sections 陣列 = data-only，不需重建。細節與各位置理由見 value-copy-guide「版面上下順序」。

核心原則：

- **Outcome-first headline。** Hero 標題講「使用者會得到什麼結果」，不是「這是什麼/它怎麼運作」。（壞：「Showcase Studio — 一個 sample tenant」；好：「在幾天內，上線一個 AI 驅動的漂亮網站」。）通常就是 PR headline 或 value-prop 一句話的精煉。
- **Benefit，不是 mechanism。** 每個 feature 翻成使用者的好處。（壞：「每個區塊都是 database-stored section，由 page builder 渲染」；好：「描述你要的，AI 幫你排好版，幾分鐘就能發布」。）
- **第二人稱、具體、可驗證的賣點。** 用「你」、具體數字（0 rebuilds、live in days）、不空泛。
- **CTA 是轉換動作**，不是內部導覽。Hero / final CTA 指向註冊 / 預約 / 看 demo（對應 PR 的 how-to-start）。
- **隱藏實作細節。** 公開頁不出現：DB / schema 名稱、「tenant」「demo tenant」「sample」、「page builder / sections / manifest / SSOT」、framework 名稱（Next.js / Ent / GraphQL 等）、「fictional studio」、任何只有內部人懂的機制。詳見 checklist。

依專案語言（偵測現有頁面 / README 主要語言）產出對應語言的文案。

### Phase 4 — Jargon sweep + verify-live（Reviewer）

載入 `references/jargon-sweep-checklist.md`，逐層掃描並**對著上線後的真實畫面驗證**，不要只 grep source。

最重要的兩個教訓：

1. **Jargon 藏在多層，要逐層掃。** 它不只在 hero——還會躲在：頁面層級的 SEO description / meta、被列表元件帶出來的**關聯內容**（文章 / 活動的 body 與摘要）、巢狀的 resource / link 清單、以及用「元件原始名稱」當標題的 gallery 區塊。本 skill 的真實案例需要**三輪**才掃乾淨，因為每修一層就露出下一層。
2. **對著 live render 驗證，不是只看 seed。** 內容常來自 join 的資料表（例如首頁「精選作品」列表其實是 articles）。改完 seed / DB 後，務必抓一次上線頁面的 HTML 做 jargon sweep，並確認 **CTA 的實際 `<a href>` 有解析**（cross-app 連結用 env token 時，原始 token 出現在 RSC payload 是無害的，但實際 href 必須是解析後的 URL；兩者要分清）。

通過條件：所有受眾頁面的 live HTML 對禁用詞清單**零命中**，且每個 CTA 的 href 正確解析、無寫死網域。

## 反模式（不要做）

- 不要把 showcase 寫成 feature list / spec dump（那是 review 的事）。
- 不要在公開頁暴露 DB 名稱、internal tenancy 詞彙、framework、page-builder 機制。
- 不要寫死正式環境網域到 committed 內容裡——cross-app 連結用 env-resolved token / 相對路徑。
- 不要只 grep seed 就宣稱乾淨；一定要驗 live render（jargon 會從關聯內容漏出來）。
- 不要在沒確認定位前就開始寫整頁。
- 不要隨機堆疊 section；依敘事弧排上下順序，proof/stats 不要落在頁尾沒人看到，Final CTA 要與 hero 一致。
- 不要捏造假數據 / 假見證；行銷可 aspirational，但 proof 要誠實。
- 不要把 PR/FAQ 的內部 FAQ、CEO viewpoint 的 kill-assumption 放進公開頁。
- 不要把「信念 / 為何」升級成第四個具名框架。它是刻意隱性內建在 hero 變體與 Problem 段的受眾分支（讓使命型受眾的「為何」鋪到 outcome 之前）；本 skill 已引用夠多 value-driven 框架，再加具名框架只會變大雜燴。維護時用 skill 既有詞彙（信念 / 立場、為何、value message），不要寫出新框架名或新增 attribution。

## Bundled references

- `references/value-prop-prfaq-ceo.md` — Sharpen：value proposition canvas + Amazon Working-Backwards PR/FAQ 模板 + gstack CEO/founder viewpoint lens（含 attribution）。
- `references/value-copy-guide.md` — Generator：語氣、結構、各 section（hero / feature grid / stats / CTA / 內頁）的 value-driven 配方與 before→after 範例。
- `references/jargon-sweep-checklist.md` — Reviewer：禁用內部詞彙清單、逐層掃描順序、live-render 驗證步驟、jargon→value 翻譯對照表。

## Attribution

CEO/founder viewpoint adapted from Garry Tan's gstack CEO review workflow & Builder Ethos (https://github.com/garrytan/gstack；本機 `~/projects/gstack`). 用「adapted from / inspired by」措辭，不宣稱 Garry Tan / YC / gstack 背書；生成的公開 showcase 不需輸出此 attribution。
