## Ownership Evidence Template

在任何 lane 對 authoritative artifact 做正式 writeback 前，應先留下最小 ownership evidence。

這不是要把 machine-local 細節寫進治理 artifact，而是要在 **實際調用該 skill 的 repo/workspace 內** 的 report / reconcile note / review evidence 中，留下足夠的治理證據，證明這條 lane 為何有資格寫入。

## Canonical Record Location

ownership/conflict evidence **不得**寫回 global skill 安裝目錄；必須落在 invoking repo/workspace 內。

預設使用以下位置：

### A. Spec-scoped lane

若本次工作明確屬於某個 `{spec-directory}`：

- `{workspace}/.agents/specs/{spec-directory}/reports/ownership-evidence-<scope>.md`

這適用於：

- branch-spec authoring lane
- spec-local CR overlay
- 與某個 active spec 強綁定的 shared governance wording 變更

### B. Workspace-scoped governance lane

若本次工作不是單一 spec，而是 workspace 級治理 lane：

- `{workspace}/.agents/specs/governance/ownership-evidence/<lane-id>.md`

這適用於：

- `SPECS.md` registry refresh
- workspace `.agents/specs/TESTS.md` rollup refresh
- `RTM.md` rollup refresh
- 跨 spec 的 shared governance wording / shared global skill 維護

### C. Conflict / reconcile note

若本 lane 已被降級為 audit-only、或需要把衝突交棒給另一條 authoritative lane：

- `{workspace}/.agents/specs/governance/conflicts/<lane-id>.md`

或若它屬於某個 spec：

- `{workspace}/.agents/specs/{spec-directory}/reports/conflict-note-<scope>.md`

重點不是檔名必須完全一致，而是：

- record 必須在 invoking repo/workspace 內
- reviewer 可以從 repo 內 artifact 追到它
- 它不能只存在於對話上下文或 global skills 目錄中

## Lane ID and Evidence Filename Convention

### Lane ID

使用 branch namespace 對應的 lane ID：

- `spec/<spec-name>`
- `cr/<cr-id-or-name>`
- `tests/<scope>`
- `registry/<scope>`
- `review/<scope>`
- `shared-governance/<scope>`

### Evidence filename slug

將 lane ID 的 `/` 轉成 `--`，形成 filename slug。

範例：

- `registry/demo-readiness-summary` -> `registry--demo-readiness-summary.md`
- `tests/workspace-rollup` -> `tests--workspace-rollup.md`

若是 spec-scoped record，可再加上簡短 suffix：

- `ownership-evidence-tests--workspace-rollup.md`
- `conflict-note-registry--demo-readiness-summary.md`

## Minimal Fields

至少記錄：

1. **Lane Identity**
   - 例如：`registry/<scope>`、`tests/<scope>`、`spec/<spec-name>`

2. **Branch Identity**
   - 只記 branch name，不記 worktree path

3. **Lane Role**
   - `authoritative writable lane` | `audit-only lane`

4. **Artifact / Scope Owned**
   - 例如：`SPECS.md whole file`
   - 或：`workspace TESTS rollup`
   - 或：`shared governance wording for shared-governance refs`

5. **Upstream Authority Basis**
   - 這次 writeback 依據哪些 upstream sources
   - 例如：`requirements.md + review.md + folder-level TESTS.md`

6. **Freshness Check Point**
   - 最後一次重讀 upstream authority 的時間點 / commit / session note
   - 只需可追溯，不需 machine-local path

7. **Conflict Status**
   - `no competing writable lane detected`
   - 或 `competing lane detected -> downgraded to audit-only`

8. **Owner / Handoff Owner**
   - 是哪個 lane / session / maintainer 負責最終 writeback 或後續吸收

9. **Next Action**
   - `proceed writeback`
   - `downgrade to audit-only`
   - `reconcile-first`
   - `await owner resolution`

## Example

```markdown
- Lane Identity: `registry/demo-readiness-summary`
- Branch Identity: `registry/demo-readiness-summary`
- Lane Role: `authoritative writable lane`
- Artifact / Scope Owned: `SPECS.md whole file`
- Upstream Authority Basis: `requirements.md`, `review.md`, workspace `TESTS.md` inputs
- Freshness Check Point: re-read upstream after latest baseline-touch on current branch
- Conflict Status: no competing writable lane detected
- Owner / Handoff Owner: current registry lane owner
- Next Action: proceed writeback
```

## Forbidden as Ownership Proof

以下資訊不能當成正式 ownership evidence，也不應寫進治理 artifact：

- worktree path
- detached compare 目錄
- 暫時草稿絕對路徑
- localhost ports / containers / env locks
- 「我剛剛先改了所以算我擁有」這種事後占位邏輯
