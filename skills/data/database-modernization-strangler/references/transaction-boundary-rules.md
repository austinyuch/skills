# Transaction Boundary Rules

在建議把邏輯移到 Go service / worker 前，先保住語意正確性。

## 核心規則

1. **短交易優先**：避免長交易包住大量商業流程或外部副作用。
2. **不要把 network call 放在 DB transaction 裡**：email、queue、webhook、HTTP call 都應拆出。
3. **單 aggregate / 強一致性** 的資料完整性邏輯，比較適合留在 DB 或緊鄰 persistence 層。
4. **跨 aggregate orchestration** 比較適合放在 application service / workflow 層。
5. **若需要 side effect**，優先考慮 outbox / event / background worker，而不是把 side effect 直接寫進 DB proc。

## 判定問題

- 這個 procedure 是否只維護一個 aggregate？
- 失敗回滾時，真正需要一起回滾的是哪些資料？
- 是否有 external side effect 不可能被 DB rollback？
- 是否需要重試？若要重試，重試單位是整支 proc 還是較小工作項？

## 常見結論

- **單 aggregate + set-based invariant**：可留 DB-side
- **多表協調但仍屬單一 request**：多半適合 Go service，DB 僅保留短交易 persistence
- **重試 / fan-out / scheduler / batch**：適合 worker / queue
- **外部 side effect**：應拆成 event/outbox + consumer
