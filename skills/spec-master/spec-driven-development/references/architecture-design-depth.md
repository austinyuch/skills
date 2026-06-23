# 架構設計與複核深度 (Architecture Design & Review Depth)

本檔是 Phase 2 (Design) 與 Phase 5 (Review) 的**架構設計深度方法論**。目的：在既有 contract-first / FMEA / Ponytail ladder 之上，補上「設計品質的高階思考」與「複核時的架構深度與防誤報紀律」。

- **Part A — Design 深度**：實作方案比較、deep module / seam 品質視角、輕量 domain modeling、架構認知模式。
- **Part B — Review 深度**：架構複核維度、deep-module 複核視角、per-finding confidence + verbatim-quote 防誤報 gate。

> 來源與授權見本檔末「Attribution」。內容改編自 garrytan/gstack（`plan-eng-review` / `office-hours` / ETHOS）與 mattpocock/skills（`codebase-design` / `domain-modeling`），兩者皆 MIT License。本檔僅取精選子集，不照搬完整 11 節 review 或全部 cognitive patterns。

**與既有機制的分工（不重複）：**

- Contract-first / SSOT 仍是介面定義的權威；本檔的 seam / deep-module 是「介面該長什麼形狀」的設計品質視角，不取代 `contract/` 的 SSOT。
- FMEA 仍負責 failure-mode 風險登錄；本檔的架構複核維度是 design/review 時的 checklist，FMEA 是其產出之一。
- Ponytail ladder 仍負責「該不該存在 / 用更少程式碼」；本檔負責「結構是否夠深、介面是否夠乾淨」。
- `code-review` 家族（`code-refactoring-advisor` 等）仍是複核期的工具偵測；本檔是人類/agent 的架構判斷視角。

---

# Part A — Design 階段深度

## A1. 實作方案比較 (Implementation Alternatives) — 條件式啟動

**何時啟動**：僅當設計屬於**架構顯著 / 非 trivial**時才要求；判準（任一即觸發）：預計觸碰 >8 檔案、引入新服務 / 新抽象、跨模組契約變更、或選型本身就是風險。小改動跳過，避免每個小設計都被迫走重流程（KISS / YAGNI）。

啟動時，產出 **2–3 個彼此明顯不同**的實作方案（不是同一想法的三種口味）。每個方案固定欄位：

```
方案 A：[名稱]
  摘要：  [1–2 句]
  Effort：[S/M/L/XL]
  Risk：  [Low/Med/High]
  Pros：  [2–3 點]
  Cons：  [2–3 點]
  Reuses：[沿用了哪些既有程式碼 / 模式]
```

**讓方案覆蓋解空間的規則：**

- 至少 2 個；非 trivial 設計建議 3 個。
- 一個必須是 **minimal viable**（最少檔案、最小 diff、最快交付）。
- 一個必須是 **ideal architecture**（最佳長期軌跡、最乾淨）。這兩者**等重**——不要因為 minimal 比較小就預設選它；若正解是 rewrite 就說「scrap it and do this instead」。
- 一個*可選* **creative / lateral**（重新 framing 問題的非典型解）。
- 收尾：**RECOMMENDATION：選 [X]，因為 [對應到需求目標 / 工程偏好的一行理由]**。
- **Design It Twice**：第一個想法通常不是最好的。逼自己在不同約束下想出「介面截然不同」的版本，再比較。

**STOP**：把方案以單一決策呈現給使用者選擇，等明確批准後才定稿 design。「明顯勝出的方案」仍是需要使用者拍板的決策——直接寫成 prose 繼續做，正是要避免的失敗模式。若只有一個可行方案，必須具體說明其他方案為何被排除。

## A2. Deep Module 與 Seam（介面品質視角）

設計介面時的核心目標：**對 caller 是 leverage、對 maintainer 是 locality、對所有人是 testability。**

- **Deep module**：小介面背後藏大量行為。**Depth 是介面的屬性，不是實作的屬性**——deep module 內部仍可由小而可替換的零件組成，那些只是不暴露在介面上。
- **Interface = caller 必須知道的一切**：不只型別簽章，還包括 invariants、ordering 限制、error modes、必要設定、效能特性。
- **Deletion test**：想像刪掉這個 module。若複雜度*消失*→它只是 pass-through（shallow，該移除）；若複雜度*在 N 個 caller 間重新冒出來*→它有在做事（值得保留）。
- **The interface is the test surface**：caller 與 test 穿過同一個 seam。若你需要測「介面之後」的東西，代表 module 形狀不對。
- **Seam 放哪是獨立決策**：seam 是「能在不修改該處的情況下改變行為」的位置。**用最高的 seam、優先沿用既有 seam，seam 越少越好（理想是一個）**。
- **One adapter = 假 seam；two adapters = 真 seam**：除非真的有東西在 seam 兩側變動（通常是 production + test），否則別硬切 seam，那只是 indirection。
- **可測試性三規則**：(a) 注入依賴、不要在內部 `new`；(b) 回傳結果、不要產生 side effect；(c) 小介面（少 method / 少參數 = 少測試）。這與 contract-first 的注入式契約相容。
- **依賴分類決定怎麼測 seam**：in-process（純計算，直接測介面）/ local-substitutable（如 PGLite，內部 seam）/ remote-but-owned（定義 port，prod 用 transport adapter、test 用 in-memory）/ true-external（如 Stripe，注入 port + mock）。

## A3. 輕量 Domain Modeling（Ubiquitous Language + ADR）

設計時對模糊/重疊術語挑一個 canonical 詞、並在重大不可逆取捨時寫 ADR——這屬於 SDD 的**統一術語治理**，完整規則（含與既有 warning-code taxonomy 的分工）見單一入口：[`references/terminology-governance.md`](./terminology-governance.md) 的 **Kind 2**。

重點：glossary 與 contract-first 互補（contract 管機器定義、glossary 管語彙共識）；opinionated 選一詞、被拒詞列 `_Avoid_`、lazy 建立；ADR 只在「難回退 + 會讓人意外 + 有真實取捨」三條件全中時才寫，A1 被排除的方案理由常是好素材。

## A4. 架構認知模式 (Architecture Cognitive Patterns) — 精選

這些是設計時的**思考本能**，不是逐條打勾；內化它們、用來挑戰自己的設計：

1. **Boring by default（創新額度）**：每個專案大約只有「三個創新額度」。核心難題才用新技術，其餘用 proven tech。每個新 dependency / 新架構都問：這值得花一個創新額度嗎？
2. **Incremental over revolutionary**：strangler fig 而非 big bang；canary 而非全域 rollout；refactor 而非 rewrite。
3. **Reversibility preference（可逆優先）**：feature flag、A/B、漸進 rollout，讓「猜錯的成本」變低。先分辨單向門 vs 雙向門。
4. **Single points of failure**：把 SPOF 標出來。每個新整合點描述一個*真實*的 production 失敗情境（timeout / cascade / 資料損毀 / auth 失敗），並說明設計是否涵蓋。
5. **Essential vs accidental complexity（Brooks）**：這是在解真實問題，還是在解我們自己製造的問題？
6. **Make the change easy, then make the easy change（Beck）**：先 refactor 讓改動變容易，再做改動；不要同時做結構變更與行為變更。
7. **Systems over heroes**：為「凌晨三點疲憊的人」設計，而不是為「你最強工程師的最佳狀態」設計。
8. **Blast radius**：最壞情況是什麼？會影響多少系統 / 多少人？
9. **6-month future**：若此設計解了今天的問題卻製造下一季的噩夢，明講出來。
10. **What's intentionally not here**：明確記錄*刻意不做*的東西（各附一行理由）本身就是設計紀律。

---

# Part B — Review 階段深度

## B1. 架構深度複核維度 (Architecture-Depth Review Dimensions)

複核時，除既有評分維度外，逐項評估（零發現就寫「無問題」，但必須評估）：

- **耦合與依賴圖**：哪些原本不耦合的元件現在耦合了？合理嗎？畫 before/after 依賴圖（ASCII 即可）。
- **資料流四路徑**：每條新資料流追 happy / nil / empty / error 四路；各路是否有處理、是否有測試？（與 FMEA 互補）
- **State machine**：每個新的有狀態物件，列出合法轉移與被阻擋的非法轉移。
- **Production 失敗情境**：每個新整合點至少一個真實失敗情境 + 設計是否涵蓋。
- **Rollback posture**：若上線即壞，回退程序是什麼（git revert / feature flag / DB migration rollback）？多久？
- **Scaling / SPOF**：10x / 100x 負載下什麼先壞？SPOF 在哪？
- **Observability as scope**：新 codepath 是否有 log / metric / trace？把可觀測性當交付項，不是事後清理。

## B2. Deep-Module / Seam 複核視角

- 對新增的 module / wrapper / 抽象套用 **deletion test**：刪掉它會*集中*複雜度（值得留）還是只是*搬移*複雜度（shallow，建議移除）？
- **Shallow module smell**：介面幾乎和實作一樣複雜 → 標記為 over-indirection。
- **介面即測試面**：若測試必須穿過介面去測內部，代表 module 形狀不對。
- 與 Ponytail over-engineering check 併入「程式碼品質評估」。

## B3. Per-Finding Confidence + Verbatim-Quote 防誤報 Gate

複核發現以下列格式記錄，**大幅降低臆測型誤報**：

```
[SEVERITY] (confidence: N/10) file:line — 描述
```

- **Confidence 校準**：9–10 已讀程式碼確認、7–8 高信心 pattern、5–6 中等（附「需驗證」caveat）、3–4 低（壓到附錄）、1–2 純臆測（除非 P0 否則不報）。
- **Pre-emit verification gate（提報前 gate）**：任何 finding 在升級為正式問題前，**必須能逐字引用觸發它的原始程式碼行 (file:line)**。若引用不出來，強制把 confidence 降到 4–5（只進附錄）。這條專門殺掉「欄位其實存在」「`dict.get` 可能是 None（但實際有預設）」這類誤報。
  - Framework-meta 提醒：若 symbol 由 metaclass / migration / decorator 生成，引用「生成它的那段」，不是 class body。
- **Severity → action**：P1 阻擋 ship；P2 應在同一 branch 修掉；P3 為後續 TODO。每個 task 都要能追溯到一個具體 finding（沒有 finding 就不要硬湊 task）。
- 此 gate 與既有 0–10 評分機制**並存**：confidence 是「這條 finding 有多可信」，評分是「這個維度有多好」，兩者不同軸。

## B4. Anti-Shortcut 條款

`review.md` 是互動式複核的*產出*，不是複核的*替代品*。把所有 finding 一次性寫進一個檔案、然後宣告完成，正是要辨識並停止的失敗模式：有非 trivial finding 時，從 finding 到「完成」的路徑必須經過與使用者的逐項確認 / 決策，而不是單向 dump。

---

## Attribution

本方法論改編自下列兩個 MIT License 開源專案，在此致謝並標註來源以尊重智慧財產權：

- **架構複核維度、實作方案比較、架構認知模式、per-finding confidence + verbatim-quote gate、anti-shortcut 條款**：改編自 [garrytan/gstack](https://github.com/garrytan/gstack) 的 `plan-eng-review` / `office-hours` / `ETHOS.md`。MIT License, Copyright (c) 2026 Garry Tan。本檔僅取精選子集，未照搬完整 11 節 deep review 或全部 cognitive patterns。
- **Deep module / seam / deletion test / interface-as-test-surface / Design It Twice、ubiquitous language 詞彙表、ADR 三條件**：改編自 [mattpocock/skills](https://github.com/mattpocock/skills) 的 `codebase-design` / `domain-modeling` skill。MIT License, Copyright (c) 2026 Matt Pocock。
