# Graph-Assisted Planning

本文件定義在 SDD Phase 2 / Phase 3 中，如何將 `code-review` 的 graph query 能力用於**設計輔助**與**測試規劃輔助**。

> 此能力是 **non-blocking enhancement**。不執行 graph 分析不算治理違規；一旦執行，結果必須被標示為輔助洞察，而不是自動事實。

## 1. Command Reference

| Command | 用途 | 何時使用 |
|---|---|---|
| `index --status` | 檢查 graph freshness | Phase 2 開始時 |
| `index --recursive` | 建立 / 更新 graph | freshness 不足時 |
| `architecture <dir>` | 看模組結構 / 相依關係 | 設計前 |
| `search-code <path> <query>` | 找既存模式、tests、consumers | Phase 2 / 3 |
| `developer-routing <artifact> <symbol>` | 分析上下游影響與 bounded evidence | 重構 / 影響分析 |
| `report <dir>` | 模組級 review baseline | 需要 code quality context |

## 2. Freshness Rules

- 先跑 `index --status`
- stale or missing → 可背景更新 graph
- `relation_coverage_status=partial` 時，結果只能作為保守提示，不能直接推論為完整 topology truth

## 3. Non-Blocking Rule

- graph 分析是 **輔助輸入**，不是 approval gate
- 不可因 graph 暫時不可用就阻塞設計
- 任何 graph 洞察都必須可被人工審視，不可自動下結論

## 4. Risk Pattern Tables

### A1. Structural

| Pattern | Risk | Typical Response |
|---|---|---|
| duplicate logic | drift | 提取共用模組 |
| circular dependency | coupling | 斷開依賴 / facade |
| deep call chain | fragility | flatten / boundary wrapper |
| high fan-out | blast radius | 增加 tests + impact review |

### A2. Race Condition

| Pattern | Risk | Typical Response |
|---|---|---|
| shared mutable state | data race | mutex / atomic / queue |
| read-check-write | TOCTOU | transaction / optimistic lock |
| async callback shared mutation | corruption | concurrent-safe structure |
| missing cancellation | leak | context / errgroup |
| competing resource access | deadlock | retry + timeout |

### A3. Stack Overflow & Memory

| Pattern | Risk | Typical Response |
|---|---|---|
| unbounded recursion | stack overflow | iterative / depth guard |
| infinite loop / blocking wait | exhaustion | timeout / deadline |
| load-all dataset | OOM | paging / streaming |
| unbounded queue/channel | leak | backpressure / limits |

### A4. OWASP / AI Security

| Pattern | Risk | Typical Response |
|---|---|---|
| SQL / NoSQL string concatenation | injection | parameterized query |
| `innerHTML` / unsafe HTML write | XSS | sanitization |
| missing server-side auth | access control | middleware / policy check |
| hardcoded secrets | secret exposure | env / secret manager |
| prompt injection path | LLM01 | validation / isolation |

### A5. Edge Condition

| Pattern | Risk | Typical Response |
|---|---|---|
| nil / undefined dereference | crash | guard clauses |
| boundary values not covered | incorrect behavior | boundary tests |
| type conversion ignored | hidden failure | error propagation |
| network timeout / no retry | instability | retry / circuit breaker |
| resource cleanup missing | leak | defer / finally |

## 5. Refactor Decision Tree

1. If graph shows duplicate logic → consider extraction
2. If graph shows circular dependency → refactor boundary first
3. If graph shows high fan-out → prioritize tests before refactor
4. If graph coverage is partial → document the uncertainty, do not overclaim certainty

## 6. Test Planning Expansion Rules

- `search-code` finds no tests → create baseline tests
- only mock tests found → plan real-wired smoke path
- many consumers found → add at least one integration scenario per critical consumer cluster
- cross-module flow detected → add cross-spec integration row

## 7. Example Workflow

```text
Phase 2:
  index --status
  if stale: run index in background
  architecture ./src/module
  search-code ./src "token refresh rotation"

Phase 3:
  search-code ./tests "auth token"
  developer-routing ./src/auth refreshToken --layers 2
  convert findings into refactor/test tasks
```

## 8. FMEA-06 / FMEA-07 Controls

- **FMEA-06**: graph insight is not authority; human confirms design decisions
- **FMEA-07**: graph-derived notes must not create recursive authority loops in `TESTS.md`, `SPECS.md`, `RTM.md`

## 9. Forbidden Anti-Patterns

- treating graph output as definitive fact
- using graph freshness timestamps to trigger endless governance rewrites
- writing graph-derived verdicts directly into `SPECS.md` without upstream confirmation

## 10. Why

💡 **原因 (WHY)**：graph analysis 可以幫助發現結構風險與 test gaps，但它本質上是輔助訊號，不是治理 authority。把它設計成 non-blocking enhancement，可以在提升精準度的同時避免過度自動化和 false certainty。
