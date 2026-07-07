# SQL Server → PostgreSQL Rewrite Triggers

看到以下特徵時，不要把它當成「語法翻譯題」，而要升級為架構重寫或行為驗證題。

## 高風險觸發器

- `#temp` / temp-table chain
- `CURSOR`
- `WHILE` loop with row-by-row processing
- dynamic SQL（`EXEC`, `sp_executesql`）
- nested proc chain
- `MERGE`
- `TRY/CATCH` + custom transaction handling
- `@@TRANCOUNT`, `XACT_STATE`, savepoint-heavy patterns
- `OUTPUT` parameters / procedure-centric API shape
- table variables / table-valued parameters
- SQL Agent jobs / scheduler-specific behavior
- collation-dependent comparisons
- `IDENTITY` / sequence assumptions
- `DATETIME` / timezone / precision assumptions

## 代表什麼

- **temp tables / row-by-row loop**：常表示邏輯應重新 set-based 化，或外移到 application workflow
- **dynamic SQL**：常表示 schema polymorphism、search builder、或 security-sensitive query assembly，需要重新設計 interface
- **nested transactions**：需先釐清真實交易邊界，再決定保留或拆分
- **scheduler/job coupling**：通常不應原封不動搬進 PostgreSQL procedure

## 預設回應

看到這些 trigger 時，輸出應包含：

1. 這是哪一類 rewrite trigger
2. 為什麼不能安全 1:1 translation
3. 建議保留 / 抽離 / 重寫到哪一層
4. 需要哪些 characterization tests 保護行為
