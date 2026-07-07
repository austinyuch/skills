# Graph-Assisted Planning（見樹又見林）

本文件定義在 SDD Phase 2 / Phase 3 中，如何將 `code-review` 的 **code graph（GraphRAG）** 能力用於**設計輔助**與**測試規劃輔助**。

> **定位**：graph = **見林**（先看整體結構、相依、blast-radius），targeted file reads = **見樹**（再看關鍵檔案的實作細節）。兩者互補；graph 讓你在動筆前先看到整片森林，避免只讀到幾棵樹就下設計決策。
>
> **邊界**：本能力是 **non-blocking enhancement**。不執行 graph 分析不算治理違規；一旦執行，結果必須被標示為輔助洞察，而不是自動事實。graph evidence **不得**覆蓋 checked-out code、active specs、或 runtime proof。

## 0. Agent Graph Dogfooding Default（non-trivial work 的 preflight 紀律）

對「架構探索 / 專案設計 / 影響分析 / 廣域 code retrieval / spec handoff / 非瑣碎實作規劃」這類 **non-trivial** 工作，agent 應把 local code graph 當成 **default context bootstrap**，而不是可有可無的加值。這是一條 init/preflight 要求。判定與 SKILL.md Global Constraint #14 的 `code-review` availability 一致（workspace / global skill home / 已發布 bundle 內 binary 任一命中即可用）。

**Non-trivial 工作的必經序列：**

1. **Preflight graph lifecycle**：先看 repo 是否有 tracked 的 `.code-review/graph.sqlite` / `vector.sqlite` / `manifest.json` snapshot——有的話先看 manifest 並跑 repo 記載的 status / doctor；沒有 repo-local 命令時跑 `review-cli-<os>-<arch> init <project-path> --graph`（或 `graph init`）。query 命令若支援 `--graph-init`，預設用 `auto`，已知 stale 時用 `always`，只有在刻意 read-only 且既有 graph 仍可查詢時才用 `skip`。
2. **Run focused queries**：依「你當下要下的決策」跑一到多個聚焦查詢（見 §1 verb table），而不是盲目全量重建。
3. **Select a trigger strategy**：為後續編輯選一種 freshness 觸發方式——repo-owned refresh 命令、`review-cli watch . --once --json`（一次性 working-tree 刷新）、long-running `review-cli watch .`（active edit session）、或 `review-cli graph hook status` / `graph hook install`（policy 允許時的 post-commit 刷新）。若不使用任何 trigger，記錄原因。
4. **Rebuild only when needed**：只有在 status/manifest 顯示 stale / missing / 不可查詢 / 對當前問題過於 partial 時才重建或刷新。
5. **Record it**：把 graph query 與 trigger/preflight 結果（或**跳過的理由**）寫進本階段產出的 `design.md` / `review.md`。這讓 graph 的使用可被人工審視，也避免「宣稱看過森林但其實沒跑」的 false-green。

**何時可以只用直接 file reads（見樹即可）**：任務明顯狹窄、相關檔案已知、或 graph state 缺失且重建成本高於任務本身時。此時**仍要**在 design/review notes 簡短說明「本次以直接讀檔為主、未跑 graph」，而不是無聲跳過。

**Repo-specific bootstrap**：若某 target repo 反覆需要專屬的 graph bootstrap 規則、snapshot ownership、或 trigger policy，應建議該 repo 更新自己的 constitution（`AGENTS.md` / Kiro steering / `CLAUDE.md`）作為 governance patch，而不是從本 skill 單方面改寫別的 repo 規則。

## 1. Command / Query Reference

| Command | 用途 | 何時使用 |
|---|---|---|
| repo status/doctor 或 `init <path> --graph` | preflight graph lifecycle | non-trivial 工作開始時 |
| `index --status` | 檢查 graph freshness | Phase 2 開始、rebuild 前 |
| `index --recursive [--resume]` | 建立 / 更新 graph（大 repo checkpointed） | freshness 不足時 |
| `search-code <path> <query> [--graph-only]` | 找既存模式、tests、consumers；`--graph-only` 為 no-embeddings 精確結構查詢 | Phase 2 / 3 |
| `architecture <dir>` | 看模組結構 / 相依關係（見林） | 設計前 |
| `bounded-context <path>` | 匯出某範圍的 bounded context / handoff 邊界 | 設計切分、spec handoff |
| `impact <artifact>` | blast-radius / 誰依賴它 | `[Impacts: …]` 宣告、FMEA blast-radius |
| `dependency-path <from> <to>` | 兩點之間的相依路徑 | 追耦合、斷循環依賴 |
| `developer-routing <artifact> <symbol> [--layers N]` | 上下游影響與 bounded evidence | 重構 / 影響分析 |
| `capability-inventory` / `summary` | 業務能力節點 / 檔案級摘要（需對應 enrichment skill） | 需求追溯、快速理解陌生模組 |
| `report <dir>` | 模組級 review baseline | 需要 code quality context |

> `--graph-only` / `index --no-embeddings` 是 **agent-only graph lane**：當 policy 或成本禁止 embeddings / pay-as-you-go provider API 時，仍能跑精確的結構查詢。這也讓 graph preflight 在無 provider 的環境下不被卡住。

## 2. Freshness Rules

- 先 preflight（tracked snapshot 的 doctor / `index --status`）
- stale or missing → 可背景更新 graph（non-blocking）
- 未提交的 working-tree 編輯會被 incremental index 納入；純行位移 / 純註解編輯不會製造 edge churn
- `relation_coverage_status=partial` 時，結果只能作為保守提示，不能直接推論為完整 topology truth

## 3. Non-Blocking Rule

- graph 分析是 **輔助輸入**，不是 approval gate
- 不可因 graph 暫時不可用就阻塞設計
- 任何 graph 洞察都必須可被人工審視，不可自動下結論
- graph evidence 不得覆蓋 checked-out code、active specs、或 runtime proof

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
- many consumers found (`impact` / high fan-out) → add at least one integration scenario per critical consumer cluster
- cross-module flow detected → add cross-spec integration row

## 7. Example Workflow

```text
Phase 2:
  # preflight (見林)
  inspect .code-review/manifest.json  (if tracked) → repo doctor/status
  else: init ./ --graph
  index --status ; if stale: index --recursive --resume (background)
  # focused queries for THIS decision
  architecture ./src/module
  impact ./src/auth/refreshToken        # blast-radius for [Impacts: …]
  search-code ./src "token refresh rotation" --graph-only
  # pick a trigger, then record what ran into design.md

Phase 3:
  search-code ./tests "auth token"
  developer-routing ./src/auth refreshToken --layers 2
  convert findings into refactor/test tasks
```

## 8. Recording Requirement（寫回 artifact）

non-trivial 工作若跑了 graph，`design.md`（Phase 2/3）或 `review.md`（Phase 5）至少要留下：

- 跑了哪些 graph query（verb + 目標）與得到的關鍵洞察
- 選了哪種 freshness trigger（或為何不用）
- `relation_coverage_status`（若 partial 要註明保守解讀）
- 若**未**跑 graph 而改用直接讀檔，一句話說明理由

這條紀錄本身是 derived note，不是 authority；不得反向覆寫 `SPECS.md` / `RTM.md` / `TESTS.md`。

## 9. FMEA-06 / FMEA-07 Controls

- **FMEA-06**: graph insight is not authority; human confirms design decisions
- **FMEA-07**: graph-derived notes must not create recursive authority loops in `TESTS.md`, `SPECS.md`, `RTM.md`

## 10. Forbidden Anti-Patterns

- treating graph output as definitive fact
- using graph freshness timestamps to trigger endless governance rewrites
- writing graph-derived verdicts directly into `SPECS.md` without upstream confirmation
- 用 graph evidence 推翻 checked-out code / active spec / runtime proof

## 11. Why

💡 **原因 (WHY)**：graph analysis 幫助在動筆前先看到整片森林（結構風險、blast-radius、test gaps），但它本質上是輔助訊號，不是治理 authority。把它設計成 **preflight-by-default 但 non-blocking、且必須寫回 artifact** 的紀律，可以同時：(1) 讓「見樹又見林」成為預設而非偶爾；(2) 用 record-in-artifact 消除「宣稱看過森林卻沒跑」的 false-green；(3) 用 non-blocking + not-authority 保住人工判斷與 runtime proof 的最終地位，避免過度自動化與 false certainty。
