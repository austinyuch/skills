---
name: issue-log-manager
description: 管理 workspace `ISSUE_LOG.md` 的專用 skill。當使用者要記錄尚未能安全歸入既有 owned spec / active lane 的改善項、整理 repeated issue、做 cluster / owner resolution、判斷 issue 應留在 issue log、fold 回既有 spec/CR、或提升為新 spec / shared skill change candidate 時使用。不要用在正式 spec authoring、`SPECS.md` registry sync、`RTM.md` bridge authoring、最終 readiness verdict、或 `TESTS.md` row-level 維護。
---

# Issue Log Manager

這個 skill 專注於 workspace-scoped `ISSUE_LOG.md` 的治理與收斂。

它負責維護尚未能安全歸入既有 owned spec / active lane 的改善項，但不取代 `SPECS.md`、`NEXT_STEPS.md`、`RTM.md`、`review.md`、或 `TESTS.md`。

## 角色定位

你負責：

- 建立或維護 `{workspace}/.agents/specs/ISSUE_LOG.md`
- 為 unresolved improvement items 建立 stable issue rows
- 補齊 source trigger、candidate owner、cluster key、root-cause hypothesis、evidence refs、promotion threshold
- 做 issue clustering / owner resolution / disposition maintenance
- 判斷 issue 應留在 issue log、fold 回既有 active spec / CR、或升級為新 spec / shared process / skill candidate

你不負責：

- 直接撰寫正式 `requirements.md` / `design.md` / `tasks.md` / `review.md`
- 管理 `SPECS.md`（那屬於 `spec-registry-manager`）
- 管理 `RTM.md` 主橋接表（那屬於 `spec-driven-development` / spec-local truth）
- 決定最終 acceptance / readiness verdict（那屬於 `review.md`）
- 維護 `TESTS.md` row-level authority（那屬於 `test-registry-manager`）

## Authority Boundary

請嚴格區分以下 surfaces：

- `ISSUE_LOG.md`：unresolved improvement holding surface
- `SPECS.md`：stable spec registry
- `NEXT_STEPS.md`：rolling operational memo
- `RTM.md`：requirement / feature / scenario / evidence bridge
- `review.md`：final verdict authority
- `TESTS.md`：test catalog / evidence pointer authority

核心規則：

- `ISSUE_LOG.md` 不是第二個 `SPECS.md`
- `ISSUE_LOG.md` 不是第二個 `NEXT_STEPS.md`
- `ISSUE_LOG.md` 不是 new-spec queue
- `ISSUE_LOG.md` 不能取代正式 spec authoring

## 何時使用

- 使用者說「這個 issue 先不要開 spec，先記起來」
- 需要整理 repeated governance issue / repeated review rejection / repeated retro finding
- 要做 unresolved issue 的 cluster / owner resolution
- 要判斷某個 issue 是留在 issue log、fold 回既有 spec / CR，還是升級成新 spec / skill candidate

### 正向 trigger examples

- 「這個 repeated review finding 還沒有明確 owner，先不要開 spec，幫我收納起來」
- 「把這幾個相似的 governance gap cluster 起來，看要不要之後再升級」
- 「這個 issue 現在證據太弱，不要直接改 skill，先記到 issue log」
- 「幫我判斷這個 unresolved issue 應該留在 issue log，還是已經可以 fold 回某個 active spec / CR」

## 何時不要使用

- 單純建立新 spec → `spec-driven-development`
- 單純更新 `SPECS.md` → `spec-registry-manager`
- 單純更新 `NEXT_STEPS.md` → 由 active workflow / `spec-driven-development` 處理
- 單純更新 `RTM.md` bridge row → `spec-driven-development`
- 單純維護 `TESTS.md` → `test-registry-manager`

### 反向 / non-trigger examples

- 「為這個新功能建立 spec」→ 不要用；交給 `spec-driven-development`
- 「這是 completed baseline 的 follow-up，請建 CR」→ 不要先記 issue log；先走 CR overlay
- 「更新 `TESTS.md` 的 stale evidence」→ 不要用；交給 `test-registry-manager`
- 「更新 `SPECS.md` 狀態摘要」→ 不要用；交給 `spec-registry-manager`
- 「根據已存在的 active spec 直接繼續做 implementation」→ 不要用；交給現有 active spec lane

## Lifecycle

`Captured → Triaged → Clustered → Owner-Resolved → Promotion-Candidate → Promoted / Folded / Closed / Dropped`

### State meanings

- `Captured`：已被觀察到，但尚未完成 triage
- `Triaged`：已補齊最小欄位，知道它不是立即 new spec
- `Clustered`：已與其他相似 issue 建立 cluster key / repeated root-cause 假說
- `Owner-Resolved`：已找到 active spec / CR / existing owner，待 fold-back
- `Promotion-Candidate`：證據足夠，可考慮升級成新 spec / shared process / skill change
- `Promoted`：已正式升級，且應指向新 owner
- `Folded`：已被既有 spec / CR 吸收
- `Closed`：已不再需要處理
- `Dropped`：問題不成立、或不值得再維護

## Row Schema

最小 row 應回答：

- 這是什麼 issue
- 從哪裡觀察到
- 目前有沒有既有 owner
- cluster key 是什麼
- root-cause hypothesis 是什麼
- 證據在哪裡
- 升級門檻是什麼
- 現在狀態是什麼
- 最終 disposition 是什麼

建議欄位還可補充：

- `Last Reviewed At`
- `Reviewer / Maintainer`
- `Routing Recommendation`
- `Superseded By / Folded Into`

## Promotion Rule

先做 owner resolution，再決定 promotion：

1. 若已有 active spec 可承接 → `Folded`
2. 若是 completed baseline follow-up → 優先變成 CR overlay
3. 若只是 spec-local lesson / optimization follow-up → 留在既有 lane
4. 若沒有 owner 且證據仍弱 → 留在 issue log
5. 只有 repeated root cause + clear cluster + enough evidence 都成立時，才允許升級為新 spec / shared process / skill change candidate

`new spec` 是最後選項，不是預設答案。

### Owner-resolution heuristics

優先順序：

1. 已有 active spec 可吸收 → 不進 issue log，或進 issue log 後立刻 `Folded`
2. 已知是 completed baseline follow-up → 優先轉成 CR overlay
3. 只是單一 spec 的 lesson / optimization → 留在原 spec lane
4. 沒有 owner、證據又不夠 → 留在 issue log
5. repeated root cause + enough evidence + no suitable owner → `Promotion-Candidate`

若同一 issue 在兩次以上 review / retro / governance scan 中仍無法 owner-resolve，至少要：

- 更新 `Cluster Key`
- 更新 `Root-Cause Hypothesis`
- 重新確認是否仍然不適合 active spec / CR
- 明確寫出下一次 review checkpoint

## Safe maintenance flow

1. 讀取 `ISSUE_LOG.md`
2. 讀取相關 evidence refs / active spec / CR pointer
3. 更新 row state / owner / disposition
4. 若 issue 已升級或 fold-back，留下 pointer，不要刪掉歷史脈絡
5. 若 workspace 其他 derived surfaces 需要知道它，只提供 pointer / warning summary，不直接把 row-level內容灌進 `SPECS.md` 或 `RTM.md`

## Prototype → Harden Conversion（技術債轉化）

當 workspace 採用 `spec-driven-development` 的 Execution Profile 機制，且 Prototype Spec 準備進入 Harden phase 時：

### 自動轉化流程

1. **掃描 Prototype-phase 技術債**
   - 讀取 `ISSUE_LOG.md` 中標記為 `prototype-phase` 或來自 Prototype review 的 issue rows。
   - 篩選 `State = Triaged | Clustered | Owner-Resolved` 且尚未 `Folded` / `Promoted` / `Closed` 的項目。

2. **生成 `[HARDEN]` 任務建議**
   - 對每個符合條件的 issue，自動生成對應的 `[HARDEN]` 任務描述。
   - 任務格式：`[HARDEN] {issue description} (from ISSUE_LOG.md {issue-id})`
   - 任務應對應到 Harden phase 的具體活動（Backfill TDD、Refactor Domain Model、Enable SAST 等）。

3. **更新 Issue Row 狀態**
   - 將原始 issue 標記為 `Folded`。
   - 在 `Superseded By / Folded Into` 欄位填入對應的 `[HARDEN]` 任務 ID 或 `tasks.md` 路徑。
   - 留下 pointer，不要刪除歷史脈絡。

### 轉化範例

```markdown
## ISSUE_LOG.md 原始項目
- **ID**: ISSUE-042
- **Description**: Domain Model is anemic (Rich Model required)
- **Source**: Prototype Phase 5 review
- **State**: Triaged

## 轉化後的 [HARDEN] 任務（寫入 tasks.md）
- [ ] [HARDEN] Refactor Anemic Domain Model → Rich Domain Model (from ISSUE_LOG.md ISSUE-042)
  - 回填 Value Objects
  - 建立 Aggregate Boundaries
  - 補齊 Domain Events
```

### 手動轉化指引

若自動轉化無法確定對應關係，至少提供：
- 明確的 `[HARDEN]` 任務描述模板
- 建議的 Phase（通常為 Phase 3 Backfill TDD 或 Phase 6 DevSecOps + Refactor）
- 相關的 `spec-driven-development` SKILL.md 參照章節

---

## Maintenance heuristics

- issue log 是 holding surface，不是永久倉庫；應定期做 review
- 若某筆 issue 長期停在 `Captured` / `Triaged`，代表 owner-resolution discipline 不足，應優先處理
- 若某筆 issue 已 `Folded` / `Promoted` / `Closed`，保留 pointer 即可，不要繼續當作活躍問題
- 若 issue row 開始出現 task ordering、implementation checklist、或 readiness claim，表示它越界了，應回退到對應 authority surface

## Git / Worktree 與 Writeback 紀律

`ISSUE_LOG.md` 是 workspace-shared file，與其他治理 surface 一樣會遇到並行寫入與 cross-machine drift 問題，因此沿用與 `spec-registry-manager` / `test-registry-manager` 相同的 shared-governance 紀律：

- 不要把 machine-local worktree path、暫存草稿絕對路徑、或本機 runtime 狀態寫進 `ISSUE_LOG.md`。需要操作規則時，優先回讀 global skill 內建的 `shared-governance` skill 的 `references/git-worktree-guide.md`、`shared-governance` skill 的 `references/git-worktree-templates.md`、`shared-governance` skill 的 `references/concurrent-writable-lanes.md`、`shared-governance` skill 的 `references/pre-write-conflict-checklist.md`、`shared-governance` skill 的 `references/ownership-evidence-template.md` 與 `shared-governance` skill 的 `references/cross-artifact-regeneration-order.md`。
- 大型 issue-log rollup / 重新分群 / 大量 disposition 變更屬於高衝突寫入，預設採用獨立 branch / worktree lane，再合併回去。
- 若需要 deterministic gate，可在正式 writeback 前執行 `shared-governance` skill 的 `scripts/validate_governance_writeback.py`，至少檢查 evidence file 是否位於 invoking workspace、欄位是否完整且非空、以及 upstream 方向是否違反 regeneration-order 規則。
- `ISSUE_LOG.md` 只持有 holding records 與 pointers；它仍不得反向 author `SPECS.md` / `RTM.md` / `NEXT_STEPS.md` / `TESTS.md` / `review.md`。

## Examples

### Example 1: stay in issue log

- Observation: repeated governance wording confusion, but only one weak evidence set exists
- Result: `Triaged` or `Clustered`
- Why: not enough evidence for new spec / skill change

### Example 2: fold into active spec

- Observation: same issue clearly belongs to the currently active auth-hardening spec
- Result: `Folded`
- Pointer: active spec path / task / CR ref

### Example 3: promote to CR overlay

- Observation: issue changes a completed baseline's workflow behavior
- Result: `Promotion-Candidate` → CR overlay created → issue becomes `Promoted` or `Folded`

### Example 4: promote to new spec

- Observation: repeated cross-spec issue, stable root cause, enough evidence, no current owner
- Result: `Promotion-Candidate` → approved new spec lane
