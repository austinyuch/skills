# Test Governance Guide

本文件定義 QA/QC 治理中與測試相關的核心 artifact、欄位、判定規則與更新時機。

> 本文件是 `spec-driven-development` 的 reference artifact。它提供 authoritative guidance，但不直接取代 `requirements.md`、`design.md`、`tasks.md`、`review.md` 的 spec-level truth。

## 1. Artifact Boundary

| Artifact | 角色 | 可否作為 machine input | 不可做什麼 |
|---|---|---|---|
| `requirements.md` | 需求 truth | Yes | 不可由 rollup 回寫 |
| `design.md` | 設計 truth | Yes | 不可由 rollup 回寫 |
| `tasks.md` | 任務 truth | Yes | 不可由 rollup 回寫 |
| `review.md` | 最終 acceptance / readiness authority | Yes | 不可被 `SPECS.md` / `RTM.md` 取代 |
| `TESTS.md` | test catalog / evidence pointer authority | Yes | 不可根據 `SPECS.md` / `RTM.md` 自動回填 |
| `ISSUE_LOG.md` | unresolved improvement holding surface | Yes | 不可直接產生 required tests 或 RTM requirements |
| `NEXT_STEPS.md` | rolling operational memo | Yes | 不可成為 test status / progress source |
| `SPECS.md` | stable registry summary | No | 不可當成 verdict authority |
| `RTM.md` | workspace synthesized traceability rollup | No | 不可當成 authoring source |

核心規則：

- `TESTS.md` 擁有 test IDs、test ownership、canonical commands、evidence refs。
- `review.md` 擁有最終 acceptance / readiness verdict。
- `SPECS.md` / `RTM.md` 只能保留 derived snapshots，且不得互相回寫，也不得回頭更新 upstream authority。
- `ISSUE_LOG.md` 中的 unresolved issue 只有在 folded / promoted 並經 SDD 正式化後，才能透過 requirement / AC / task 進入 test planning；不可直接從 raw issue row 生成 `TESTS.md` required tests。
- `NEXT_STEPS.md` 只可作為 resume hint，不可作為 test freshness、test result 或 coverage authority。

## 2. TESTS.md Dual-Level Model

### 2.1 Workspace-Level

路徑：`.agents/specs/TESTS.md`

用途：repo-wide test registry、per-spec test summary、cross-spec integration test register。

### 2.2 Package / Folder-Level

路徑：`{module}/TESTS.md`

用途：test decision table、req/AC ↔ test scenario ↔ test case mapping、out-of-repo integration evidence。

## 3. Test Decision Table Template

```markdown
| Test ID | Type Tag | Scenario | Req Trace | Owner | Canonical Command | Status | Risk | Last Run | Result | Evidence Ref |
|---------|----------|----------|-----------|-------|-------------------|--------|------|----------|--------|--------------|
| T-AUTH-001 | smoke,security | Login with valid credentials | REQ-AUTH-001:AC1 | auth-team | npm test -- auth.login.valid | real-wired | 4 | 2026-05-25 | PASS | reports/auth-login.md |
```

欄位說明：

- `Test ID`: `T-{MODULE}-{NNN}`，必須與 test function/class naming 一致。
- `Req Trace`: `REQ-XXX:AC{N}` 格式。
- `Status`: `none | mock | stub | fixture | real-wired`。
- `Risk`: `1..5`。
- `Result`: `PASS | FAIL | PASS* | SKIP | BLOCKED`。
- `Evidence Ref`: 指向 test report、execution log、或 screenshot/artifact path。

## 3.5 Lifecycle Crosswalk

對於 improvement / CR 類工作，test posture 應至少能被拆成三軸理解：

- `Traceability`: `mapped | partial | unmapped_to_spec`
- `Execution`: `not_run | pass | fail | blocked`
- `Evidence`: `missing | fresh | stale`

最小規則：

- 若 impacted CR 為 `Open` 或 `Review Pending`，critical tests 的 `Evidence` 不得沿用舊 snapshot 自動視為 `fresh`。
- 若 evidence 早於造成 CR 的 relevant change，應保守標示為 `stale`，直到有新的 upstream evidence。
- `review.md` 仍是 acceptance / readiness verdict authority；test lifecycle crosswalk 只用來避免 false-green。

## 4. Acceptance Status Rules

### 4.1 Per-REQ (`RTM.md` rollup)

- `PASS`: required scenarios 存在且以真實 evidence 通過。
- `CONDITIONAL`: scenarios 存在，但仍包含 mock/stub/fixture 或 accepted gaps。
- `FAIL`: 缺少 required scenarios 或存在 failing results。
- `NOT_STARTED`: 尚未建立對應 test。

### 4.2 Per-Spec (`SPECS.md` snapshot)

- `PASS`: 所有 REQ-level acceptance statuses 為 PASS 且 critical gaps = 0。
- `CONDITIONAL`: 沒有 missing requirement coverage，但仍存在 mock-heavy / accepted gaps。
- `FAIL`: 至少一條 REQ-level acceptance 為 FAIL。
- `NOT_ASSESSED`: `review.md` 尚未給出 verdict。

> `SPECS.md` 中的 acceptance 欄位是 summary-only / non-authoritative snapshot。若與 `review.md` 或 `TESTS.md` 衝突，upstream source wins。

## 5. One-Way Non-Cyclic Rollup Flow

```text
requirements.md / design.md / tasks.md / review.md / test reports
        ├──> TESTS.md (authoritative test catalog)
        ├──> RTM.md   (derived workspace traceability rollup)
        └──> SPECS.md (derived stable registry summary)
```

若來源是 `ISSUE_LOG.md`，必須先經：

```text
ISSUE_LOG.md -> owner resolution -> Folded / Promoted SDD lane -> requirements.md / tasks.md
```

才可進入上方 test-governance flow。

禁止：

- `SPECS.md -> RTM.md` 作為生成輸入。
- `RTM.md -> SPECS.md` 作為 verdict authority。
- `SPECS.md / RTM.md -> TESTS.md` 回填 test requirement / status。
- `ISSUE_LOG.md -> TESTS.md` 直接生成 required tests。
- `NEXT_STEPS.md -> TESTS.md` 作為 test status 或 freshness source。
- derived-to-derived sync。

若 `SPECS.md`、`TESTS.md`、`RTM.md` 的 snapshot 欄位互相矛盾，必須回到 `review.md`、test reports、與 spec-local source 重新生成。

## 5.5 Concrete Maintenance Flow

當工作會新增、採用、重命名、淘汰、或重新驗證 tests 時，建議使用以下固定順序：

1. 更新或建立最近的 folder-level `TESTS.md` row-level authority
2. 補齊 `Test ID`、trace refs、canonical command、evidence ref、owner、status
3. 若 workspace 採用 `.agents/specs/TESTS.md`，由 `test-registry-manager` 依 folder-level catalogs 刷新高階 rollup
4. 若 workspace 採用 `RTM.md` / `SPECS.md` snapshot，僅在 upstream authority 完整後再做 single snapshot write
5. 最終 acceptance / readiness verdict 只寫入 `review.md`
6. 若存在 `Open` / `Review Pending` CR，確認 impacted critical tests 的 evidence freshness 已重新判定，再進行 rollup

### Responsibility split

- `spec-driven-development`: 定義何時要刷新 `TESTS.md`，以及 closeout 前哪些 evidence 必須齊全
- `test-registry-manager`: discovery、reconciliation、duplicate/stale/missing-evidence 檢查、workspace `.agents/specs/TESTS.md` rollup refresh
- `spec-registry-manager`: 只消費 test summary 來生成 `SPECS.md` 摘要，不維護 row-level test catalogs

## 6. Manual QA Reminder

對治理文件的 Manual QA = 實際執行 grep / schema checks / path existence checks 並觀察結果，不只是主觀判斷。

## 7. Forbidden Anti-Patterns

- 將 `RTM.md` 當成 authoring spreadsheet。
- 將 `SPECS.md` 當成 sprint board 或 task progress source。
- 跳過 folder-level `TESTS.md`，直接修改 workspace `.agents/specs/TESTS.md` 來偽造 row-level traceability。
- 讓 `TESTS.md` 根據 `SPECS.md` readiness 自動生成 required tests。
- 讓 `TESTS.md` 根據 raw `ISSUE_LOG.md` row 自動生成 required tests；必須先經 SDD 正式化為 requirement / AC / task。
- 使用 `NEXT_STEPS.md` 的文字作為 test result / freshness / coverage truth。
- 根據 derived snapshots 自動修正 upstream authority。

## 8. Why

💡 **原因 (WHY)**：測試治理要可追溯、可聚合、可摘要，但不能讓摘要 artifact（`SPECS.md`, `RTM.md`）反過來污染或覆寫真正的 authority source。這是避免 false-green、summary drift、與 endless refresh 的必要條件。
