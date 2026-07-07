# Extraction Patterns

完成分類後，選擇最小但可維護的落點。

## Repository / Query Object

適合：

- Leaf CRUD
- 單表 / 單 aggregate persistence
- 可清楚以 input/output contract 表示的資料操作

## Domain / Application Service

適合：

- 多步驟 business orchestration
- 需要明確語意命名的業務流程
- 跨多個 repository 的交易協調

## Background Worker

適合：

- batch / backfill / settlement / reporting refresh
- 高耗時 / 可重試 / 非同步流程
- 需要 observability 與 retry policy 的工作

## Lambda / Event Handler

適合：

- 輕量事件回應
- 小型 side effect
- 可被明確事件觸發的處理

## DB-side Retention

適合：

- set-based data manipulation
- local invariant enforcement
- 對 latency 或 atomicity 很敏感、且範圍局部的邏輯

## Anti-Patterns

- 把所有 proc 都外移成 service method，卻沒保住資料完整性
- 把外部 side effect 繼續藏在 DB layer
- 把報表批次直接塞進同步 API request
- 把 scheduler semantics 假裝成普通 CRUD
