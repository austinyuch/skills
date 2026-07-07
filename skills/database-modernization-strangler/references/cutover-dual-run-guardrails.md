# Cutover / Dual-Run Guardrails

不要只規劃「如何重寫」，也要規劃「如何安全切換」。

## 最小必答問題

1. 切換單位是單一 procedure、單一 bounded context、還是一整批 job？
2. 有沒有 dual-run / parity window？
3. 失敗時 rollback 是 rollback code path、traffic route、還是 data state？
4. 觀測點是什麼？（錯誤率、資料差異、批次耗時、重試率）
5. 是否需要 reconciliation step？

## Guardrails

- 高風險流程先做 smoke parity，不要直接全量切換
- 若有 batch / settlement / ledger 類工作，先定義 reconciliation 與 idempotency
- 若 migration 期間會共存新舊邏輯，明確標示 source of truth 與停用條件
- 不要把「可回退」講得太輕鬆；要說清楚回退的是哪一層
