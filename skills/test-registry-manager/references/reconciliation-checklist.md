# Reconciliation Checklist

在更新 `TESTS.md` 前後，至少確認以下檢查點：

## Authority

- [ ] folder-level `TESTS.md` 是 row-level authority
- [ ] workspace `.agents/specs/TESTS.md` 只是 derived rollup
- [ ] `RTM.md` 沒有回填 `TESTS.md`
- [ ] `SPECS.md` 沒有回填 `TESTS.md`
- [ ] `review.md` verdict 僅被引用，不被覆寫

## Row integrity

- [ ] 每個 row 有 stable `Test ID`
- [ ] `Canonical Command` 存在
- [ ] `Evidence Ref` 存在或明確標 unknown / pending
- [ ] `Owner` 存在
- [ ] `Task / Spec Trace` 與 `Requirement / AC Trace` 有證據支撐

## Drift handling

- [ ] duplicate `Test ID` 已標示
- [ ] stale rows 已標示，不是靜默刪除
- [ ] unmapped critical tests 已顯示 gap，而不是假映射
- [ ] folder summary 與 workspace rollup 沒有矛盾

## Closeout

- [ ] folder-level `TESTS.md` 先更新
- [ ] workspace `.agents/specs/TESTS.md` 再更新
- [ ] 若需 `RTM.md` / `SPECS.md` writeback，交由對應 maintainer 在 single snapshot flow 中完成
