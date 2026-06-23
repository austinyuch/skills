# Classification Taxonomy

所有 stored procedure / function / job logic，都先分類再決定落點。

## 1. Leaf CRUD

特徵：

- 單一 table 或單一 aggregate 為主
- 無外部 I/O
- 幾乎沒有 branching
- 無 dynamic SQL / temp-table chain / cursor
- 不呼叫其他高階 orchestration proc

典型落點：

- Repository / query object
- 薄 SQL layer
- 在必要時保留為 PostgreSQL-side helper

## 2. Validation / Invariant Helper

特徵：

- 驗證欄位、狀態、存在性、唯一性
- 維護局部 business invariant
- 常被其他 proc 重複呼叫

典型落點：

- DB constraint / trigger / function（若是資料完整性）
- Domain service / validator class（若屬業務規則而非純資料約束）

## 3. Business Orchestration

特徵：

- 多表協調
- 有 branching / retries / workflow state
- 同時碰到 order、inventory、ledger、approval 等不同子領域
- 可能伴隨通知、事件、external side effects

典型落點：

- Go application service / workflow service
- 需要明確的 transaction boundary 與 idempotency strategy

## 4. Reporting / Aggregation

特徵：

- 報表、彙總、重查詢、批量讀取
- 有較複雜的 join / grouping / window logic
- 常偏 read-heavy

典型落點：

- 保留 SQL 查詢邏輯，但透過 query layer / read model 管理
- 若耗時或排程性高，轉至 batch worker

## 5. Batch / Backfill / Settlement Job

特徵：

- 長時間執行
- fan-out、大量資料掃描、重試、補算
- 可能與 scheduler 綁定

典型落點：

- Queue + worker（例如 SQS + Fargate）
- 或其他可重試的 background execution layer

## 6. Integration Adapter

特徵：

- 直接或間接處理外部檔案、API、queue、email、webhook
- 對 DB 只是 side effect 的一部分

典型落點：

- Anti-corruption layer
- Integration service / event handler
- 不應塞在長 DB transaction 中

## 快速判定問題

對每支 procedure 至少回答：

1. touched tables 有幾個？
2. 是否有 branching / loop / cursor？
3. 是否有 dynamic SQL？
4. 是否呼叫其他 procedures？
5. 是否存在 external side effect？
6. 是否有 retry / scheduling / batch semantics？
7. 若拆出 DB，最小可保真的 transaction boundary 是什麼？
