# Analysis Levels

先依規模選擇分析深度，並在輸出開頭宣告採用的 Level。

## Level 1 — 微觀視角

適用：內容大約 **< 500 行**，或 procedure 數量很少，足以逐支分析。

目標：

- 逐支拆解 procedure
- 指出 T-SQL / PostgreSQL / application logic 的具體邊界
- 建議 transaction boundary
- 提供小型 EDD / characterization test baseline

輸出重點：

- 每支 procedure 的責任
- 應留在 DB / 應移至 Go service 的理由
- 明確的 refactor slice

## Level 2 — 模組視角

適用：內容大約 **500 ~ 2000 行**，或可辨識出一個中型模組。

目標：

- 盤點 table schema、I/O contract、CRUD dependency
- 標出 dynamic SQL、cursor、temp table、nested proc call 等地雷
- 做 architecture triage，而非逐行改寫

輸出重點：

- CRUD matrix
- 模組邊界
- rewrite trigger map
- Go service / worker / retained SQL 的落點建議

## Level 3 — 巨獸視角

適用：內容 **> 2000 行**、上萬行 dump、或多個 bounded context 混在一起。

目標：

- **禁止逐行翻譯**
- 先做 physical split strategy
- 萃取 metadata：proc 名稱、I/O、涉及 tables、依賴深度
- 找出 leaf-node CRUD 候選
- 產出後續拆解 workflow

輸出重點：

- 檔案切割方式
- bounded context / naming cluster
- 第一波應優先深潛的檔案或 procedures
- modernization roadmap，而不是逐支 rewrite

## 額外規則

- 行數只是 proxy；若行數不高但相依非常深，仍可升級分析等級。
- 若內容混雜 DDL、DML、jobs、triggers、reporting logic，優先偏向較高等級。
- 若使用者只貼局部片段，不要假裝知道全局；明確說明目前只是局部分析。
