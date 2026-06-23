# Schema / Type Mapping Risks

SQL Server → PostgreSQL modernization 不只是 procedure 問題，schema/type 也常決定可否安全抽離。

## 常見風險點

- `UNIQUEIDENTIFIER` → UUID strategy
- `DATETIME` / `DATETIME2` → `timestamptz` / `timestamp` choice
- `MONEY` → `numeric` precision strategy
- `NVARCHAR` / collation-sensitive comparison
- `IDENTITY` → sequence / generated identity behavior
- computed columns / persisted computed logic
- table-valued parameters 對等替代方案
- default constraints / null semantics

## 使用方式

當某個 modernization slice 牽涉 schema 或 parameter contract 時，至少標示：

1. 哪個 type / schema feature 有遷移風險
2. 這個風險會影響 procedure rewrite、service extraction、還是雙寫/比對邏輯
3. 需要什麼驗證（fixture、parity、migration smoke）
