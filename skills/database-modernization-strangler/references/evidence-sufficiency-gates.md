# Evidence Sufficiency Gates

在任何 modernization 建議前，先判斷證據是否足夠。

## Input Classes

### 1. `name-only`

只有 object name、模糊口述、或沒有 SQL 內容。

允許：

- triage
- 假設列表
- 補件請求

禁止：

- 高信心 target-layer 決策
- cutover / rollback 具體建議

### 2. `partial SQL`

只看到一小段 SQL、單支 procedure 片段、或缺少相依。

允許：

- 局部風險判讀
- rewrite trigger 掃描
- 候選 modernization slice

禁止：

- 宣稱已掌握完整 side effects

### 3. `module dump`

看到一組相關 SQL，但仍可能缺 caller、job、trigger、scheduler。

允許：

- 模組級分類
- transaction-boundary 候選
- 初步 target-layer 建議

要求：

- 列出 unknowns

### 4. `full dump`

看到 schema + procedures + jobs + triggers + 相依面。

允許：

- 較高信心 modernization sequence
- FMEA 與 cutover strategy

## Decision Gate Checklist

在提出 extraction / cutover 建議前，至少檢查：

- caller known?
- hidden triggers/jobs known?
- transaction boundary known?
- parity baseline exists?
- rollback / reconciliation path known?

若多項答案為 `no`，結論應降級為：

- `hypothesis`
- `needs evidence`
- `unsafe to finalize`
