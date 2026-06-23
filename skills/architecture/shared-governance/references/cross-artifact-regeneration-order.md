## Cross-Artifact Regeneration Order

這份 reference 定義：當多個治理 artifact 彼此有 derived 關係時，正式更新順序必須如何進行，才能避免 stale snapshot 與 derived-to-derived sync。

## Core Rule

永遠從 **upstream authority** 重新生成下游摘要；不要讓一個 derived artifact 回填另一個 derived artifact。

## Canonical Order

### Test governance related

```text
requirements.md / design.md / tasks.md / review.md / test reports
        -> folder-level TESTS.md
        -> workspace .agents/specs/TESTS.md
        -> SPECS.md / RTM.md summary fields (if needed)
```

### Spec registry related

```text
requirements.md / design.md / tasks.md / review.md / canonical CR files / TESTS upstream summaries
        -> SPECS.md
same upstream authorities / TESTS upstream summaries
        -> RTM.md (if workspace rollup is required)
```

說明：`RTM.md` 可以在 `SPECS.md` 之後更新，但它**不是**從 `SPECS.md` 反推生成；兩者都必須由同一批 upstream authorities / TESTS upstream summaries 各自重新生成。

## Allowed Pattern

1. 重讀 upstream authority
2. 在記憶體內生成 summary / warning / snapshot
3. 一次性寫回對應 derived artifact
4. 若需要另一份 derived artifact，重新用 upstream authority 生成，不從剛寫出的 derived artifact 反推

## Forbidden Pattern

禁止：

- `SPECS.md -> RTM.md`
- `RTM.md -> TESTS.md`
- `SPECS.md / RTM.md -> folder-level TESTS.md`
- 先寫 `SPECS.md`，再讀 `SPECS.md` 去修 `RTM.md`
- 先寫 workspace `.agents/specs/TESTS.md`，再回頭把它當 row-level authority 修 package `TESTS.md`

## Conflict-aware Rule

若同時存在多條 lane：

- 只有擁有該 derived artifact writeback 權的 authoritative lane 可以執行最後一步寫回
- 其他 lanes 只能輸出 draft / findings / reconcile note
- 若上游 authority 在寫回前已被更新，必須停止 incremental patch，重新從 upstream regenerate

若要做 deterministic gate，可在 writeback 前使用 `../scripts/validate_governance_writeback.py` 檢查 evidence location、required fields、與 upstream 方向是否合法。

## Quick Examples

### Correct

- implementation lane 更新 test reports
- test-governance lane 依 test reports 刷新 folder-level `TESTS.md`
- 同一條 authoritative test-governance lane 再刷新 workspace `.agents/specs/TESTS.md`
- registry lane 依最新 upstream summary 更新 `SPECS.md`

### Incorrect

- registry lane 看到舊的 `SPECS.md` warning，就直接拿它去修 `RTM.md`
- implementation lane 更新 workspace `.agents/specs/TESTS.md`，再讓 test-governance lane 用它去反推 package `TESTS.md`

## End-to-End Example

1. implementation lane 發現 `workspace .agents/specs/TESTS.md` 需要刷新，但另一條 `tests/workspace-rollup` lane 已擁有正式 writeback 權。
2. implementation lane 依 `concurrent-writable-lanes.md` 降級成 audit-only，輸出 repo-local conflict note 與 drift findings。
3. authoritative `tests/workspace-rollup` lane 重讀 upstream authority：test reports、folder-level `TESTS.md`、必要的 `review.md`。
4. authoritative lane 依 `ownership-evidence-template.md` 在 invoking workspace 寫入 ownership evidence。
5. authoritative lane 執行 `validate_governance_writeback.py`：
   - 確認 evidence file 位於 invoking workspace
   - 確認 required fields 非空
   - 顯示 upstream classifications
   - 確認 regeneration order 沒有違規
6. validation pass 後，authoritative lane 才正式 write back workspace `.agents/specs/TESTS.md`。
7. 若後續還要更新 `SPECS.md` / `RTM.md`，必須再由對應 authoritative lane 依 canonical regeneration order，使用同一批 upstream authorities / TESTS upstream summaries 各自重新生成，而不是從剛寫出的 `SPECS.md` 反推 `RTM.md`。
