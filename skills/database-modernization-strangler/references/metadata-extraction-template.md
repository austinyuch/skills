# Metadata Extraction Template

Level 3 大型 dump 模式下，先做 metadata extraction，不要先逐行翻譯。

每支 procedure 或函式，至少記錄：

| Field | Meaning |
|---|---|
| Object Name | proc / function 名稱 |
| Domain Guess | 所屬 bounded context 或 naming cluster |
| Inputs | 主要 input params |
| Outputs | output params / result sets |
| Touched Tables | 主要涉及 tables |
| Nested Calls | 是否呼叫其他 proc/function |
| Control Flow Markers | temp table / cursor / loop / dynamic SQL / TRY-CATCH |
| External Side Effects | email / webhook / queue / file / scheduler coupling |
| Initial Classification | leaf CRUD / orchestration / reporting / batch / integration |
| Confidence | high / medium / low |

## 目的

- 找 leaf-node 候選
- 找重寫 trigger 熱區
- 找最適合第一批 modernization slice 的對象
