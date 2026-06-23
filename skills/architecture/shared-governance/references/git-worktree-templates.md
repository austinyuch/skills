## Git Branch / Worktree Templates

這份檔案提供 **global skill 內建** 的可重用範本與操作片段。

目的：讓 agent 在沒有 repo-local `AGENTS.md` 或其他專案自訂規範時，仍然有一套可直接採用的共享 workflow。

若 repo 之後真的提供更強的專案級規範，才把它視為 override；不要把 `AGENTS.md` 當成這套流程的唯一承載位置。

### 1. Branch namespace template

預設命名空間：

- `spec/<spec-name>`
- `cr/<cr-id-or-spec-name>`
- `tests/<scope>`
- `registry/<scope>`
- `review/<scope>`

命名原則：

- 使用小寫與 `-`
- branch name 必須可通過 `git-check-ref-format --branch`
- branch name 要反映 lane identity，而不是 session identity

同一個 namespace 也應直接用作 lane ID；evidence filename 的 slug 規則請讀 `./ownership-evidence-template.md`。

### 2. Worktree layout template

若沒有明確 repo-local 規範，預設 worktree 位置：

- `<workspace>/../.worktrees/<repo-name>/<branch-slug>`

如果當前環境不適合使用這個 layout，也至少維持：

- worktree 與 main worktree 分離
- lane 目錄與 branch identity 可追溯
- 暫時 compare/audit lane 不混進正式 authoring 目錄

### 3. Decision template

#### 何時建立新的 writable worktree

- 新 spec lane
- CR overlay
- repo-owned global skill / shared governance wording 變更
- 大型 `TESTS.md` refresh
- 大型 `SPECS.md` / `RTM.md` refresh
- 與既有 implementation lane 並行的治理工作

#### 何時重用既有 writable worktree

只有以下條件都成立時：

- branch 與 lane identity 相同
- worktree 乾淨，或未提交內容就是合法續做上下文
- 沒有其他 session / agent 佔用

#### 何時使用 detached / read-only worktree

- inventory
- diff / compare
- QA / review / readback
- warning / drift audit
- 不應承擔正式 writeback 的分析工作

### 4. Command snippet template

以下是共用工作流範本，可直接被 skill 引用。

#### 建立新的 writable lane

```bash
git worktree add -b "spec/<spec-name>" "../.worktrees/<repo-name>/spec-<spec-name>" HEAD
```

#### 建立 detached audit lane

```bash
git worktree add --detach "../.worktrees/<repo-name>/audit-<scope>" HEAD
```

#### 檢查既有 worktrees

```bash
git worktree list --porcelain
```

#### 清理暫時 lane

```bash
git worktree remove "../.worktrees/<repo-name>/<lane>"
git worktree prune
```

### 5. Lane handoff checklist template

在任一治理 lane 暫停 / closeout 前，至少回答：

1. 這條 lane 的 branch identity 是什麼？
2. 它是 writable lane 還是 audit-only lane？
3. 是否還有未提交變更？
4. 是否仍由當前 session / owner 佔用？
5. 正式 writeback 是否已完成？
6. 暫時 worktree 是否應移除？
7. 若目錄曾被手動刪除，是否需要 `git worktree prune`？

### 6. Artifact hygiene template

以下資訊預設 **不得寫進** `SPECS.md`、`NEXT_STEPS.md`、`RTM.md`、`TESTS.md`、`review.md`：

- worktree path
- detached compare 目錄
- 暫時草稿絕對路徑
- 機器本地暫存位置
- localhost ports
- container / network / compose stack 名稱
- 其他 machine-local runtime state

若需要保留 lane 規則，請在 global skill 參照這份 template；若未來 repo 有更細的專案級 workflow，再把那份規範視為補充，而不是唯一來源。
