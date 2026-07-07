# Eval Harness Plan

此文件把 `database-modernization-strangler` 的 skill-creator evals，提升為較正式的 eval-harness workflow。

## Baseline

- `iteration-1` 是 **manual fallback smoke eval**，不是高信心 benchmark。
- source: `temp/skill-evals/database-modernization-strangler/iteration-1/`
- claim ceiling: `CONDITIONAL / MANUAL_FALLBACK_REFERENCE`

## Eval Layers

### 1. Smoke Evals

目的：確認 skill 至少會做對這些事：

- 宣告 analysis level
- 先做 evidence sufficiency 判定
- 拒絕 blind 1:1 translation
- 不把 query tuning 誤當 modernization orchestration
- 對 hidden trigger/job side effects 保守降級

建議 smoke cases：

- eval 4: name-only evidence refusal
- eval 5: query tuning non-trigger
- eval 6: pushback on blind 1:1 translation
- eval 7: hidden trigger / job side effects

### 2. Parity-Oriented Evals

目的：確認 skill 會要求可程式化 parity，而不是只做口頭建議。

重點檢查：

- golden-master corpus
- side-effect parity
- transaction-behavior tests
- idempotency / retry parity
- type / semantic parity
- dual-run diff harness

### 3. Adversarial Evals

目的：驗證 skill 不會：

- 由名稱過度自信分類
- 在 evidence 不足時給出過度具體的 architecture decision
- 在 unknown caller / rollback / reconciliation 情況下做 cutover overclaim

## Grading Policy

優先使用 code-based / schema-based assertions；若做不到，至少要：

- 要求 `text + passed + evidence`
- 把 caveats 記錄到 `user_notes_summary`
- 區分 `PASS`, `FAIL`, `NEEDS_REVIEW`

## Metrics Policy

- 若 subagent / automation 正常：可追求 `pass@1`, `pass@3`, `pass^3`
- 若 subagent auth 失敗：只能記為 `manual fallback smoke pass`
- manual fallback 不得宣稱 full benchmark confidence

## Claim Policy

只允許以下狀態：

- `SMOKE_PASS`
- `PARITY_CANDIDATE`
- `CONDITIONAL`
- `MANUAL_FALLBACK_REFERENCE`

禁止把 manual fallback 報告寫成 production-readiness 證據。
