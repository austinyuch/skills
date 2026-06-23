## Git Branch / Worktree Guide for Shared Governance

這份 guide 定義 spec / CR / registry / test-governance 工作何時應使用獨立 branch 與 `git worktree`。

它的目的不是把每個 skill 變成 Git 教學，而是避免多條治理 lane 在同一個工作目錄互相污染。

### 1. 何時預設要用獨立 branch + worktree

遇到下列情況，預設採用 **一條 lane = 一個 branch = 一個 writable worktree**：

- branch-spec authoring 與既有 active spec 並行
- completed baseline 的 CR overlay
- repo-owned global skill / shared governance wording 變更
- 大型 `TESTS.md` reconciliation 或 workspace `.agents/specs/TESTS.md` rollup refresh
- 大型 `SPECS.md` / `RTM.md` registry refresh
- 需要同時保留 implementation lane 與 review / audit lane

若只是單一 lane、低衝突、小幅本地修改，且目前 worktree 已乾淨、沒有平行治理工作，可沿用現有 branch / worktree。

### 2. Writable vs Read-only lane

- **Writable worktree**：真正要編輯檔案、產生 commit、更新 authoritative artifact 的 lane
- **Detached / read-only worktree**：只做盤點、diff、審閱、比對、報告驗證，不承擔正式 writeback

規則：

- 同一個 branch 同時間只保留 **一個 writable worktree**
- read-only audit 可使用 detached worktree
- 若要從 audit lane 轉為正式修改，應切換到新的 topic branch / writable worktree，不要直接在 detached state 長期累積變更

### 3. Branch namespace and layout

branch namespace 與 worktree layout 的 canonical shared template 由 `./git-worktree-templates.md` 提供。

- 先使用 global skill 內建 template
- 若 repo 未來真的提供更明確的專案級 override，再以 repo-local policy 補充

branch name 仍必須可通過 `git-check-ref-format --branch` 的規則；不要包含空白、模糊縮寫或機器隨機 suffix，除非 workflow 明確需要。

### 4. 建立 / 重用 / 清理流程

#### 建立前先檢查

先檢查：

- `git worktree list --porcelain`
- 目前 branch 是否已有對應 worktree
- 欲重用的 worktree 是否乾淨、是否仍屬於當前 lane owner

#### 重用既有 worktree

僅在以下條件同時成立時可重用：

- branch 與 lane identity 一致
- worktree 乾淨或其未提交內容就是本次 lane 的合法續做上下文
- 沒有其他 agent / session 把它當成另一條 writable lane 使用

#### 建立新的 writable worktree

適用於新的 spec / CR / registry / tests lane。優先使用新的 topic branch，不要讓多個治理目標共用同一條 writable branch。

#### 建立 detached audit worktree

適用於：

- read-only inventory
- registry / TESTS baseline comparison
- review / QA / report 驗證
- 不應產生正式 writeback 的分析工作

#### 清理

lane 完成後：

- 正常移除：`git worktree remove <path>`
- 若目錄曾被手動移除或路徑失效，補做：`git worktree prune`

不要把已失效的 worktree registration 留在 repo 中，避免後續 lane 誤判。

### 5. Artifact boundary

worktree 是 **machine-local execution surface**，不是 spec/governance artifact。

因此：

- 不要把 worktree 絕對路徑寫進 `SPECS.md`、`NEXT_STEPS.md`、`RTM.md`、`TESTS.md` 或 `review.md`
- 可以在 report / handoff 中記錄「需要獨立 worktree」這件事
- 若需要可重現的 lane 規則，優先引用 global skill 內建的 templates；repo-local guide 只作為補充 override，而不是唯一來源

### 6. Conflict-sensitive extensions

當 authoritative artifact 可能被多條 lane 同時碰到時，這份 guide 只提供進場規則；具體衝突降級與 ownership 處理，必須再讀：

- `./concurrent-writable-lanes.md`
- `./pre-write-conflict-checklist.md`

### 7. 各技能的使用方式

- `spec-master`：判斷這次工作是否應先隔離成獨立 lane，再交給下游 skill
- `spec-driven-development`：在 tasks / implementation / review 中規劃、使用並驗證 branch/worktree hygiene
- `test-registry-manager`：允許用 detached worktree 做盤點，但 authoritative row-level / rollup writeback 只能來自單一 writable lane
- `spec-registry-manager`：允許用 detached worktree 做 inventory / compare，但 `SPECS.md` / `RTM.md` writeback 只能來自單一 writable lane

若需要具體 branch namespace、layout、命令片段、handoff checklist，直接讀取 `./git-worktree-templates.md`。

### 8. Anti-patterns

避免以下做法：

- 在同一個 writable worktree 同時做多條 spec / CR / registry lane
- 把 detached audit lane 直接當成長期 authoring lane
- 手動 `rm -rf` worktree 後不做 `git worktree prune`
- 讓多個 branch 共用同一個「看起來方便」的工作目錄
- 把本機 worktree path、暫存檔位置、container/runtime 狀態寫進治理 artifact
- 在 registry / test rollup 還沒收斂前，讓多個 writable lanes 同時修改同一份 authoritative file
