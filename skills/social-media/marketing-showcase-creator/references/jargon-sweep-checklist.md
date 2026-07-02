# Jargon Sweep + Verify-Live Checklist (Reviewer)

把公開 showcase 頁面掃乾淨：零內部詞彙、CTA 正確解析、對著上線畫面驗證。

## 禁用內部詞彙（公開頁不該出現）

掃描時把這些當紅旗。它們是內部 / 工程口吻，會讓行銷頁失分：

- **DB / schema 名稱**：任何 `cms_*`、`*_db`、實際資料庫 / schema 名。
- **租戶機制詞**：`tenant`、`demo tenant`、`sample tenant`、`fictional studio`、`multi-tenant-ready`、`database-per-site`、`tenancy tier`。
- **page-builder 機制詞**：`page builder`（當機制講時）、`sections` / `database-stored section`、`DB-driven`、`manifest`、`SSOT`、`component manifest`、`forked code`、`themeless` / `themeless-first`、`re-renders from the DB`、`page-built`。
- **framework / 技術棧**：`Next.js`、`React`、`Ent`、`GraphQL`、`RLS`、`pgvector`、`gqlgen`、`mutation`、`resolver`、`schema`、`seed`（當技術詞講時）。
- **元件原始名稱當標題**：`HeroSection`、`ContentSection — filter/sort/paginate`、`EnhancedContentList — controls + virtual scroll` 等。
- **內部佐證 / readiness 詞**：`claim-cap`、`coverage tier`、`evidence`、`mock`、`PR #`、`spec`——這些屬於 review，不屬於 showcase。

> 例外：少數已成行業通用、對買家也成立的詞可保留（例如把 "multi-tenant CMS" 當產品類別、"drag-in page builder — no developers" 當賣點）。判準：**潛在使用者看得懂且覺得是好處**就留；**只有內部人懂或暴露機制**就改。

## Jargon → Value 翻譯對照

| 內部詞 | 改寫成（value） |
|---|---|
| DB-driven / no rebuild | edit any time, no developers / publish instantly |
| multi-tenant / database-per-site | run all your sites from one place / your own isolated space |
| database-stored sections / page builder mechanics | build pages from ready-made blocks |
| manifest / SSOT / component catalog | every building block, ready to use |
| access-gated / signed URL | free previews; paid content stays protected |
| agent-friendly SEO / llms.txt / MCP | found by AI assistants and search |
| BYOK secrets | your provider, your keys |
| demo tenant / sample / fictional studio | an example brand showing what you can build |
| themeless-first, themed later | on-brand in minutes — apply your colors and go |

## 逐層掃描順序（jargon 藏在多層）

每層都掃。修完一層常露出下一層——真實案例需要三輪才乾淨。

1. **Hero + 主要 section 文案**（最明顯，先掃）。
2. **頁面層級 SEO `description` / `meta`**（不顯示在 body 但會進 `<meta>`，且常被遺忘）。
3. **關聯內容**：被列表 / gallery 元件帶出來的**文章、活動、項目**的 title / body / 摘要（例如首頁「精選作品」其實是 articles → 它們的 body 可能寫著 "database-stored sections"）。這是最容易漏的一層，因為它不在 page seed 裡，在 content 資料表。
4. **巢狀清單**：resource grid / link list / nav 內的 title 與 description。
5. **Gallery 區塊標題**：用元件原始名稱當標題的地方。
6. **CTA 文案與 href**（見下節驗證）。

## Live-render 驗證（不可只看 source）

改完 seed / DB / source 後，**抓上線後的真實 HTML** 再驗一次——內容常來自 join 的資料表，grep source 會漏。

對每個受眾頁面：

1. 取得 live HTML（例如 `curl -s <url>`）。
2. 對禁用詞清單做 sweep；**目標：零命中**。任何命中 → 回到對應層修，再驗。
3. 確認每個 CTA 的**實際 `<a href>` 已解析**：
   - cross-app 連結應是解析後 URL（例：`https://admin.<domain>/signup/...`），不是原始 token。
   - **注意**：原始 token（如 `@cms/...`）出現在 RSC / flight payload 裡是**無害**的（它只是 React key），不要誤判；只看實際 `<a ... href="...">`。
4. 確認**沒有寫死正式網域**在 committed 內容裡（網域應由 env / token 在 render 時帶入）。

## 套用變更的注意事項

- **Data-only**：改既有元件的文案 / 既有內容，多半是純資料變更（seed → DB upsert），**不需重建 image**。若有多個資料庫（例如 mgmt + runtime）要保持 parity，兩邊都要更新。
- **需要重建**：只有引入**新元件 / 新前端能力**才需要重建並重新部署。
- 對 production 資料做寫入前，先 read-only 確認目標列、用 transaction、逐列 assert 影響筆數，並在前後比對。production 內容寫入是對外、不易回復的動作，先確認再做。

## 通過條件（definition of done）

- [ ] 所有受眾頁面的 **live HTML** 對禁用詞清單零命中。
- [ ] 每個 CTA 的實際 href 正確解析、無寫死網域。
- [ ] 關聯內容（文章 / 活動 / 項目）也已掃過並改寫。
- [ ] 文案是 outcome-first、benefit-led、第二人稱。
- [ ] 變更已正確判定為 data-only 或需重建，並據此套用 / 部署 + 驗證。
