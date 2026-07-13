---
name: test-registry-manager
description: 管理 `TESTS.md` 與 test traceability 的專用 skill。當使用者要更新、盤點、刷新、reconcile、audit、clean up folder-level `TESTS.md` 或 workspace `.agents/specs/TESTS.md`，補 `Test ID`、`Owner`、`Canonical Command`、`Evidence Ref`、`Task / Spec Trace`、`Requirement / AC Trace`，處理 duplicate test IDs、stale rows、`unmapped_to_spec`、missing evidence，或在 spec closeout 前刷新測試治理時，都應優先使用此 skill，即使使用者沒有明說 skill 名稱。若工作同時涉及 open CR、review-pending baseline change、或需要重新判定 critical test evidence freshness，也應使用此 skill。不要用在新 spec authoring、`SPECS.md` registry sync、`RTM.md` authoring、最終 readiness verdict、或 local env / runtime work。
---

# Test Registry Manager

這個 skill 專注於 `TESTS.md` 的治理與收斂。它負責維護 **folder-level `TESTS.md`** 的 row-level test traceability，以及 **workspace-level `.agents/specs/TESTS.md`** 的高階 rollup。

它不是 readiness verdict skill，也不是 `SPECS.md` registry manager。

## 角色定位

你負責：

- 掃描 workspace 中的 folder-level `TESTS.md` 與對應 test artifacts
- 維護或補齊 row-level test catalog 欄位
- 更新 canonical command、evidence refs、owner、trace refs、stale markers
- 依 folder-level catalogs 生成或刷新 `.agents/specs/TESTS.md` 高階摘要
- 發現 drift、duplicate IDs、缺 evidence、缺 owner、derived-to-source 衝突

你不負責：

- 決定最終 acceptance / readiness verdict（那屬於 `review.md`）
- 管理 `SPECS.md`（那屬於 `spec-registry-manager`）
- 把 `RTM.md` 當成 authoring source
- 根據 workspace rollup 反向覆寫 folder-level `TESTS.md`
- 管理 local runtime registry、ports、stack names、或 infra allocation

## Authority Boundary

請嚴格遵守以下 one-way authority graph：

```text
requirements.md / design.md / tasks.md / review.md / test reports
        └──> folder-level TESTS.md         (row-level authority)
                └──> workspace .agents/specs/TESTS.md   (derived rollup)
                └──> workspace RTM.md                 (derived rollup)
                └──> workspace SPECS.md               (derived rollup)
```

核心規則：

- folder-level `TESTS.md` 是 **row-level authority**
- `.agents/specs/TESTS.md` 是 **repo-wide registry / pointer summary**
- `RTM.md` 是 **traceability rollup**，不是 test catalog
- `SPECS.md` 是 **spec registry**，不是 test registry
- `review.md` 才是最終 verdict authority
- reusable `TESTS.md` schema / alias / migration policy 的 authority 是這個 skill 的 source；
  target repo 內的 ad hoc parser、local spec wording、或單次手工 patch 只能是 consumer evidence，
  不可被宣稱為未來 customer repository 的新格式契約

禁止：

- `SPECS.md -> TESTS.md`
- `RTM.md -> TESTS.md`
- `.agents/specs/TESTS.md -> folder-level TESTS.md`
- derived-to-derived sync

若 snapshot 欄位互相矛盾，必須回到 upstream authority（`review.md`、test reports、spec-local source、folder-level `TESTS.md`）重新生成。

## 何時使用

- 使用者說「更新 TESTS.md」
- 使用者說「補 test traceability」
- 使用者說「整理 test catalog」
- spec closeout 前需要刷新 test registry
- TDD / implementation / UAT / review 後需要回寫 evidence refs 與 execution status
- 需要盤點 duplicate test IDs、stale rows、missing owner、missing command、missing evidence

## 何時不要使用

- 單純更新 `SPECS.md` → 交給 `spec-registry-manager`
- 單純建立 / 續做 branch spec → 交給 `spec-driven-development`
- 要裁決 PASS / FAIL / CONDITIONAL readiness → 回到 `review.md`
- 要啟動 runtime / E2E stack → 交給 `local-infra-registry-governance`

## 核心工作流程

### 1. Discover authoritative sources

先找：

- folder-level `TESTS.md`
- test reports / execution logs / screenshots / CI refs
- spec-local `requirements.md`, `design.md`, `tasks.md`, `review.md`
- workspace `.agents/specs/TESTS.md`（若存在）

不要先讀 `SPECS.md` / `RTM.md` 來推回 row-level truth。

### 2. Reconcile folder-level catalogs

對每個 folder-level `TESTS.md`：

- 保留 stable `Test ID`
- 檢查 `Owner`
- 檢查 `Canonical Command`
- 檢查 `Evidence Ref`
- 檢查 `Requirement / AC Trace`
- 檢查 `Task / Spec Trace`
- 檢查 lifecycle / stale markers
- 先用 legacy-compatible alias recognition 讀取既有欄位；不要要求 customer repository 先破壞式改表頭

若某個 test 仍無法可靠映射到 spec / REQ / AC，應保守標成：

- `unmapped`
- `unmapped_to_spec`
- `partial`
- `stale`

不要硬補假的 traceability。

### 2.1 Legacy-compatible schema recognition

本 skill 必須用 **normalize first, rewrite later** 的策略處理 legacy `TESTS.md`：

- 先建立 normalized row view，讓下游 selector / rollup / audit consumer 可以讀取一致欄位。
- 常見表頭 alias 必須被視為相容輸入，而不是要求 target repo 立即改名：
  - `Type`, `Type Tag`, `Test Type` -> `Test Type`
  - `Command`, `Canonical Command`, `Run`, `How to Run` -> `Canonical Command`
  - `Req / Trace`, `Req Trace`, `Requirement / AC Trace`, `Requirement Trace` -> `Requirement / AC Trace`
  - `Evidence`, `Evidence Ref`, `Evidence Summary`, `Latest Evidence` -> `Evidence Ref`
  - `Task Trace`, `Task / Spec Trace`, `Spec Trace` -> `Task / Spec Trace`
  - `Status`, `Execution`, `Execution Status` -> `Execution Status`
- 若欄位缺失但 row 可識別，輸出 `missing_field` / `recommended_add_column` 類 advisory；不得自動補假的 command、owner、evidence、REQ。
- 下游 product code 可以 consume normalized view；但新的 reusable schema / tier metadata / migration behavior
  必須先在此 skill source 記錄，不能只在某個 target repo 的產品 parser 中發明。

### 2.2 Advisory update mechanism

當需要建議或套用 `TESTS.md` 更新時：

- 預設輸出 recommendation plan；只有使用者明確要求或 repo workflow 明確允許時才 writeback。
- 自動 rewrite 必須 idempotent，且保留 user-authored prose、comments、section order。
- 對 managed insertion 使用 marker block 只能用於新增 summary / generated section；不可包住或覆寫整份手寫 catalog。
- 高風險 rewrite 前建立 `.bak` 或等價備份；若 repo 禁止備份檔入版控，備份路徑需留在本機 temp 並在報告中說明。
- 回報結果必須區分 `recommended`, `applied`, `blocked`, `not_applicable`。
- Legacy repos 應先得到 compatibility diagnostics 與 migration suggestion；fresh repos 才使用 preferred template 初始化。

### 2.5 Lifecycle Crosswalk

對 improvement / CR 類工作，至少要把 test posture 拆成三軸理解：

- `Traceability`: `mapped | partial | unmapped_to_spec`
- `Execution`: `not_run | pass | fail | blocked`
- `Evidence`: `missing | fresh | stale`

最小規則：

- 若 impacted CR 為 `Open` 或 `Review Pending`，critical tests 的 `Evidence` 不得沿用舊 snapshot 自動視為 `fresh`。
- 若 evidence 早於相關 baseline-touch / CR 變更，應保守標示為 `stale`，直到有新的 upstream evidence。
- 這些 lifecycle posture 是 test governance input，不等同於最終 readiness verdict；最終 verdict 仍屬於 `review.md`。

### 3. Refresh workspace rollup

`.agents/specs/TESTS.md` 只應摘要：

- spec / subsystem / package
- catalog path
- summary counts
- high-risk or cross-spec test dependencies
- canonical commands
- latest evidence pointer summary
- warning / drift summary

不要把 folder-level 的每一列完整複製進 workspace rollup。

### 4. Report drift and governance gaps

至少找出：

- duplicate `Test ID`
- missing `Owner`
- missing `Canonical Command`
- missing `Evidence Ref`
- stale evidence
- unmapped critical tests
- folder/workspace summary mismatch
- 任何想從 derived artifact 回填 authority 的企圖

### 5. Closeout discipline

在 implementation / review closeout 時，這個 skill 的輸出應支援：

1. folder-level `TESTS.md` 已刷新
2. `.agents/specs/TESTS.md` 已刷新
3. 需要時，把高階 trace summary 提供給 `RTM.md` / `SPECS.md` 的 maintainer
4. 不自行產生 readiness verdict
5. 若存在 open CR 或 review-pending baseline change，確認 impacted critical tests 的 evidence freshness posture 已重新標示，再交由 rollup / registry maintainer 消費摘要

## Profile Tag Recognition（Execution Profile 標籤識別）

當 workspace 採用 `spec-driven-development` 的 Execution Profile 機制時，`TESTS.md` 可能包含 `[PROTOTYPE]` 或 `[HARDEN]` 標籤。本 skill 必須識別這些標籤並調整 evidence 規則：

| 標籤 | 識別行為 | Evidence 要求 | 生命周期規則 |
|---|---|---|---|
| `[PROTOTYPE]` | 允許手動 / Mock evidence | Screenshot、manual test log、mock report 均可接受 | 可被對應的 `[HARDEN]` 測試標記為 `superseded` |
| `[HARDEN]` | 要求自動化 CI evidence | 必須提供 CI report、coverage report、SAST scan result | 取代對應的 `[PROTOTYPE]` 測試，保留歷史但標記為 `active` |

**測試演進追蹤**：
- 當同一條測試從 `[PROTOTYPE]` 升級為 `[HARDEN]` 時，應保留原始 `[PROTOTYPE]` 記錄但標記為 `superseded`。
- 新增 `[HARDEN]` 記錄，標記為 `active`，並在 `Superseded By` 欄位指向新的 `Test ID`。
- 範例：`T-042-01 [PROTOTYPE]` → `superseded by T-042-02 [HARDEN]`。

**與 spec-driven-development 的協作**：
- 不要自行判斷 Profile 轉換時機；當 `spec-driven-development` 進入 Harden phase 並產生 `[HARDEN]` 任務時，才觸發測試標籤升級。
- 若發現 `[PROTOTYPE]` 測試長期未被 `superseded`，應在 drift report 中標記為 `orphaned_prototype_test`。

---

## Suggested folder-level row schema

詳細模板請讀 `./references/tests-md-schema.md`。

最小 row 應回答：

- 這是什麼 test
- 測哪個 code surface
- 對應哪個 task/spec
- 對應哪個 REQ / AC
- 怎麼跑
- 最近證據在哪
- 目前狀態 / 風險是什麼

## Workspace rollup output expectations

workspace `.agents/specs/TESTS.md` 應保留：

- subsystem / package catalog pointers
- per-spec test summary
- cross-spec integration register
- evidence pointer summary
- unresolved drift / gap warnings

它不是 row-level source，也不是 review verdict。

## Safe update protocol

對大型 `TESTS.md` 文件，先產生 draft，再 review，再 merge。不要直接在長文件中進行高風險覆蓋式改寫。

## Git / Worktree Hygiene

- 若這次工作同時涉及多個 package 的 `TESTS.md`、workspace `.agents/specs/TESTS.md` rollup、或與 implementation lane 並行的 test governance refresh，預設使用 dedicated branch / worktree，避免把 row-level authority update 與其他 authoring lane 混在同一個工作目錄。
- 允許使用 detached / read-only worktree 做 inventory、diff、gap audit；但 folder-level `TESTS.md` 與 workspace rollup 的正式 writeback，只能由 **一條 authoritative writable lane** 進行。
- 若已有既有 worktree 可重用，必須先確認它對應同一條 lane、目前狀態乾淨且沒有其他 session 佔用；不要把別人的 writable lane 當成自己的 baseline。
- 不要把 machine-local worktree path、暫存檔位置、或本機 runtime 狀態寫進 `TESTS.md` / workspace rollup。需要具體規則時，讀取 `shared-governance` skill 的 `references/git-worktree-guide.md`、`references/git-worktree-templates.md`、`references/concurrent-writable-lanes.md`、`references/pre-write-conflict-checklist.md`、`references/ownership-evidence-template.md` 與 `references/cross-artifact-regeneration-order.md`。
- 若另一條 lane 已擁有同一份 folder-level `TESTS.md` 或 workspace rollup 的正式 writeback 權，當前 lane 必須降級為 audit-only，僅提交 drift / evidence / stale-marker findings，不得搶寫 authority。
- 正式刷新 workspace `.agents/specs/TESTS.md` 前，必須先留下 ownership evidence；這份 record 應落在 invoking workspace（預設 `.agents/specs/governance/ownership-evidence/` 或對應 spec reports），並依 cross-artifact regeneration order 先確認 folder-level authority 已更新完成。
- 若需要 deterministic gate，應在正式 writeback 前執行 `shared-governance` skill 的 `scripts/validate_governance_writeback.py`，至少檢查 evidence file 是否位於 invoking workspace、欄位是否完整且非空、是否提供 `--expect-scope-token` 綁定當前 lane/scope、以及 upstream 中是否包含 folder-level `TESTS.md` 而非 derived artifact。若 script 失敗，禁止正式 writeback，必須先修正 repo/workspace 內的 evidence 或 upstream 問題。

## Reference files

需要欄位與 reconciliation checklist 時讀：

- `./references/tests-md-schema.md`
- `./references/reconciliation-checklist.md`
- `shared-governance` skill 的 `references/git-worktree-guide.md`
- `shared-governance` skill 的 `references/git-worktree-templates.md`
- `shared-governance` skill 的 `references/concurrent-writable-lanes.md`
- `shared-governance` skill 的 `references/pre-write-conflict-checklist.md`
- `shared-governance` skill 的 `references/ownership-evidence-template.md`
- `shared-governance` skill 的 `references/conflict-evidence-review-checklist.md`
- `shared-governance` skill 的 `references/cross-artifact-regeneration-order.md`

若工作同時牽涉 SDD / registry boundary，也應回讀：

- `spec-master` skill 的 `reference/TEST_GOVERNANCE_GUIDE.md`
- `spec-registry-manager` skill 的 `SKILL.md`
- `spec-master` skill 的 `references/routing-matrix.md`
