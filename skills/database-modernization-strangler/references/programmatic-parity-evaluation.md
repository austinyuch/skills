# Programmatic Parity Evaluation

可以，而且在真實 modernization 中，**parity 應盡量程式化**，不要只靠人工閱讀報表。

## 1. Golden-Master Corpus

建立一組可重播的 fixture：

- procedure input params
- 初始資料狀態
- 預期 result sets / output params

對同一批 fixture：

1. 跑舊的 SQL Server implementation
2. 跑新的 PostgreSQL / service implementation
3. 把結果標準化後輸出為 JSON
4. 做機器 diff

## 2. Side-Effect Parity

不要只比「回傳值」。也要比：

- touched rows
- status transitions
- ledger / audit inserts
- outbox / event rows
- notification scheduling side effects

最實用的做法是把每次執行前後的 canonical tables snapshot 成 JSON，再做 delta compare。

## 3. Transaction-Behavior Tests

在流程中注入故障點，例如：

- inventory update 之後失敗
- ledger write 之前失敗
- external notification dispatch 之前失敗

然後比較：

- 是否有 partial write
- rollback 邊界是否一致
- 是否需要 compensating event

## 4. Idempotency / Retry Parity

對 batch / worker / settlement 類流程：

- 重播同一 command 兩次
- 模擬 worker retry
- 檢查是否產生 double invoice / double ledger / double notification

## 5. Type / Semantics Parity

專門針對易出錯的差異建立 machine-checkable assertions：

- null semantics
- money rounding
- datetime precision / timezone
- UUID / identity behavior
- collation / case sensitivity
- ordering assumptions

## 6. Dual-Run Diff Harness

高風險路徑可採用雙跑：

1. 同一批 fixture 同時餵給 old path / new path
2. 把 outputs / side effects 序列化成統一格式
3. 允許白名單差異（例如 timestamp precision）
4. 對非白名單差異直接 fail

## 建議輸出格式

每個 parity case 至少包含：

- Case ID
- Input fixture
- Old result JSON
- New result JSON
- Table delta summary
- Allowed diffs
- Unexpected diffs
- Verdict: pass / fail / needs review

## 什麼情況不能只做人工驗證

- settlement / ledger / billing
- batch rebuild / backfill
- 有 hidden triggers / jobs
- 有 external side effects
- 有 timezone / rounding / collation 差異風險

這些情況若沒有 programmatic parity，應降低 modernization 信心。
