# Output Contract

最終輸出使用以下結構。若資訊不足，可標示 `gap` / `assumption` / `hypothesis`，但不要省略章節。

## 0. Analysis Level

- 宣告 Level 1 / 2 / 3
- 說明為何採用這個分析深度

## 1. 架構輪廓與技術債

- Bounded contexts / naming clusters
- 核心 schema / module 概覽
- SQL Server 專屬地雷與 rewrite 風險

## 2. 核心邏輯與依賴圖譜

- Procedure / module classification summary
- CRUD dependency matrix
- nested proc / temp table / cursor / dynamic SQL / loop 標記

### 必備表格

至少提供一張 row-level decision table，欄位包含：

- Object / Procedure
- Classification
- Evidence
- Confidence
- Unknowns
- Candidate Target Layer
- Next Slice

## 3. 現代化落點建議

將邏輯分流到：

- application service / class
- PostgreSQL-side retained SQL / function / procedure
- async worker / queue consumer
- event handler

對每個重要建議都要附上原因。

## 4. Transaction Boundary 評估

- 哪些邏輯應保留短交易
- 哪些邏輯需要拆成 orchestration + outbox / async side effect
- 任何 isolation / retry / idempotency 風險

## 5. Next Steps

- 下一批應優先處理的檔案 / procedures / modules
- 建議切割方式
- characterization tests 建議
- 先做哪些小 slice 最有利

## 6. Decision Gates / Go-No-Go

至少回答：

- caller / scheduler 是否已知
- hidden side effects 是否已盤點
- parity baseline 是否已存在
- rollback / reconciliation path 是否已知

若答案是否定，請明確標示還不能 finalize 哪些建議。

## 7. FMEA / Risk Register

至少列出高風險 failure modes、偵測方式、緩解方式、與下一步要補的證據。

## 8. 若為 Level 3 額外必填

- physical split strategy
- metadata extraction summary
- leaf-node candidates
- 下一輪深潛應載入的檔案名單
