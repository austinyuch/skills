---
name: cross-agents-symlink-bridge
description: 為 git 管控的專案建立跨 AI agent 的 hybrid bridge：repo-local `skills` 用 symlink / Junction 避免重複，`specs` 可選擇 sync 或 symlink，其餘 `.claude`、`.kiro`、`.codex` 內的設定 / 權限檔維持 real-directory + sync workflow。當使用者提到「設定 cross-agents symlinks」「初始化 agents 設定」「skills 不要重複」「保留 Claude/Codex 權限檔」「specs 要可切換 sync 或 symlink」「CLAUDE.md symlink」或要整理 cross-agent `.gitignore` 規則時使用此 skill。
---

# Cross-Agents Symlink Bridge

在多 AI agent（OpenCode、Claude Code、Kiro、Codex）並存的專案中，這個 skill 採用 **hybrid bridge**：

- `.agents/skills/`（workspace agent home）是共享 skill source，讓 `.claude/skills`、`.kiro/skills`、`.codex/skills` 指向同一份內容；**repo root 不應出現獨立的 `skills/`**（那是 `~/.config/opencode/`、`~/.claude/` 這類 global config home 的慣例）
- `.agents/specs/` 同樣是 workspace-level spec source，但 `.claude/.kiro/.codex` 下的 `specs/` 可以選擇 **sync** 或 **symlink**
- 其餘設定、權限、approval、sandbox 相關檔案保持 **real directory / real files**，交給既有 sync flow 或各 agent 自己管理，避免再出現 whole-directory symlink 導致的權限問題

**關鍵差異：Kiro / Codex vs Claude**：

- **Kiro**：repo-local `skills/` 建議用 symlink / Junction，`specs/` 可 sync 或 symlink，其他內容保持 real dir
- **Codex**：與 Kiro 相同；重點是不要再讓整個 `.codex/` 指向 `.agents/`，避免權限 / runtime state 被整包接管
- **Claude Code**：除了 `skills/` / `specs/` hybrid bridge，仍需要遞迴建立 `CLAUDE.md → AGENTS.md` symlink，因為 Claude 只直接讀 `CLAUDE.md`

## 核心設計原則

1. **只有 `skills/` 預設一定是 link surface** — 目標是消除 repo-local skill duplication，而不是讓整個 agent root 變成 symlink。canonical source 是 `.agents/skills`（與 `.agents/specs` 對稱），**不是 repo root 的 `skills/`**
2. **`.claude/`、`.kiro/`、`.codex/` 本身保持 real directories** — 這樣權限檔、approval state、sandbox config、MCP config 才不會被 whole-directory symlink 綁架
3. **`specs/` 是 mode-based surface** — 使用者可明確選擇 `sync`（預設）、`symlink` 或 `skip`
4. **其他 config / permission surfaces 不由這個 skill 轉成 symlink** — 它們應沿用既有 sync workflow 或各 agent 自身管理方式
5. **`.gitignore` 只忽略成功建立的 generated symlink paths** — 不忽略整個 agent root
6. **CLAUDE.md 遞迴處理** — 專案內任何目錄有 `AGENTS.md` 就自動建立 `CLAUDE.md → AGENTS.md` symlink
7. **雙平台腳本** — 所有操作皆有 `.sh`（Linux/macOS）和 `.ps1`（Windows）版本

## 操作決策樹（優先閱讀）

| 使用者措辭關鍵字 | 對應 Phase | 執行指令 |
|---|---|---|
| 「初始化」「setup」「first time」「設定 symlink bridge」 | **Phase 1** | `bash scripts/init.sh` |
| 「specs 也要 symlink」「specs 改回 sync」「specs 可切換」 | **Phase 1** | `bash scripts/init.sh --specs-mode symlink` / `--specs-mode sync` |
| 「sync」「更新 CLAUDE.md」「新增了 AGENTS.md」 | **Phase 2** | `bash scripts/sync-claude-md.sh` |
| 「裝 hook」「pre-commit」「自動同步」 | **Phase 3** | `bash scripts/install-hook.sh` |

若使用者只說「處理 cross-agents」而無明確指定，預設從 Phase 1 開始，並使用 `--specs-mode sync`。

## 工作流程

### Phase 1：初次初始化

當使用者想在專案中初次設定 cross-agents hybrid bridge：

1. 確認當前工作目錄是專案根目錄
2. 執行 init 腳本：
   - Linux/macOS：`bash scripts/init.sh`
   - Windows：`powershell -ExecutionPolicy Bypass -File scripts/init.ps1`
3. init 腳本會：
   - 將 `.claude/`、`.kiro/`、`.codex/` 正規化為 **real directories**
   - 建立 `.claude/skills`、`.kiro/skills`、`.codex/skills` → `.agents/skills/` 的 symlink / Junction（若 `.agents/skills/` 不存在會自動建立）
   - 依 `--specs-mode` 處理 `.claude/.kiro/.codex/specs`
     - `sync`（預設）：從 `.agents/specs/` 同步到各 agent root
     - `symlink`：讓各 agent 的 `specs/` 指向 `.agents/specs/`
     - `skip`：完全不碰 `specs/`
   - **不**處理其他設定 / 權限檔的 symlink 化
   - 遞迴同步 `CLAUDE.md → AGENTS.md`
   - 更新 `.gitignore` 的 managed symlink sections

### Phase 2：CLAUDE.md 同步（手動觸發）

當使用者在現有專案中新增了 `AGENTS.md`，或想重新掃描：

- Linux/macOS：`bash scripts/sync-claude-md.sh`
- Windows：`powershell -ExecutionPolicy Bypass -File scripts/sync-claude-md.ps1`

sync 腳本支援兩種模式：

| 模式 | 觸發方式 | 行為 |
|---|---|---|
| **Full scan** | 直接執行，無參數 | 掃描整個 repo 所有目錄 |
| **Git diff mode** | `--staged` 參數 | 只處理 `git diff --cached` 中的 AGENTS.md；若本次 commit 沒有 staged `AGENTS.md`，仍會從目前 repo 內有效的 `CLAUDE.md -> AGENTS.md` symlink 狀態重建 managed `.gitignore` section，避免把既有 entries 洗掉 |

> Full scan 會排除 `.git/`、`node_modules/`、`vendor/`，以及 generated `.claude/`、`.kiro/`、`.codex/` 子樹，避免在 agent mirror / bridge 目錄或第三方 vendored code 內重複生成 `CLAUDE.md`。

### Phase 3：安裝 pre-commit hook（可選）

讓 git commit 時自動確保 CLAUDE.md symlink 與 AGENTS.md 保持同步：

- Linux/macOS：`bash scripts/install-hook.sh`
- Windows：`powershell -ExecutionPolicy Bypass -File scripts/install-hook.ps1`

## 重要規則

### 衝突處理

| 情境 | 行為 |
|---|---|
| `.claude/`、`.kiro/`、`.codex/` 是 whole-directory symlink | 備份 symlink，自動改回 real directory，再只建立 `skills/` 子路徑 symlink |
| `.claude/skills`、`.kiro/skills`、`.codex/skills` 已是正確 symlink | 跳過，輸出 ✅ |
| `.claude/skills`、`.kiro/skills`、`.codex/skills` 是實體目錄 | 先 backup，再建立指向 `.agents/skills/` 的 symlink / Junction |
| `.claude/specs`、`.kiro/specs`、`.codex/specs` 使用 sync mode | 保持 real directory，從 `.agents/specs/` rsync / robocopy mirror |
| `.claude/specs`、`.kiro/specs`、`.codex/specs` 使用 symlink mode | 若已有實體目錄，先 merge 回 `.agents/specs/`，再建立 symlink / Junction |
| `CLAUDE.md` 已是正確 symlink | 跳過 |
| `CLAUDE.md` 是實體檔案（有內容） | **警告並跳過**，不覆蓋 |
| `CLAUDE.md` 不存在 | 建立 symlink，並將路徑加入 `.gitignore` |

### `.gitignore` 規則

- **只在 generated symlink 建立成功後**才將對應路徑加入 `.gitignore`
- `skills` bridge 層級：`.claude/skills`、`.kiro/skills`、`.codex/skills`
- `specs` 只有在 **symlink mode** 時才加入 ignore：`.claude/specs`、`.kiro/specs`、`.codex/specs`
- `CLAUDE.md` 層級：每個成功建立的 `CLAUDE.md` symlink 的相對路徑（如 `docs/CLAUDE.md`）
- 若 `.gitignore` 不存在則自動建立
- 使用 **獨立 managed sections** 管理 bridge paths 與 `CLAUDE.md` paths，避免 stale entries 殘留
- managed entries 以 repo-root anchored 形式寫入（例如 `/CLAUDE.md`），避免 root 檔名規則誤傷 vendored `CLAUDE.md`
- `sync-claude-md --staged` 若本次沒有 staged `AGENTS.md`，不可把 `CLAUDE.md` managed section 重寫為空；應從目前有效 symlink 狀態重建該 section
- 若 `.claude/skills`、`.kiro/skills`、`.codex/skills` 曾被 git 追蹤，加入 `.gitignore` **不會自動 untrack**；agent 應提醒使用者檢查 `git status`

## 腳本說明

| 腳本 | 平台 | 用途 |
|---|---|---|
| `scripts/init.sh` | Linux/macOS | Hybrid 初始化（real agent roots + `skills/` symlink + `specs` sync/symlink + CLAUDE.md 同步 + `.gitignore`） |
| `scripts/init.ps1` | Windows | 同上，使用 Junction / Robocopy |
| `scripts/sync-claude-md.sh` | Linux/macOS | 遞迴同步 `CLAUDE.md` symlink，並重寫 dedicated `.gitignore` section |
| `scripts/sync-claude-md.ps1` | Windows | 同上 |
| `scripts/test-gitignore-idempotency.sh` | Linux/macOS | 驗證 managed `.gitignore` sections idempotent、root anchored，且 `vendor/` 不被掃描/忽略 |
| `scripts/install-hook.sh` | Linux/macOS | 安裝 git pre-commit hook |
| `scripts/install-hook.ps1` | Windows | 同上 |

### 執行慣例

- **一律從專案根目錄執行**
- agent 執行腳本後應讀取輸出，根據輸出中的 ✅/🔗/🔄/📦/⚠️/❌ 符號向使用者報告結果
- 若 init 或 sync 腳本回報任何 ❌，應向使用者說明問題並建議處理方式

## 常見問題處理

| 輸出符號 | 情境 | Agent 應對 |
|---|---|---|
| `📦 Backed up .claude` | 舊版 whole-directory symlink 或不相容實體路徑 | 告知使用者 root 已改回 real dir，避免權限狀態再被整包 symlink |
| `🔗 Created: .claude/skills -> .agents/skills` | repo-local skills bridge 建立成功 | 告知使用者 skills 不再重複複製 |
| `🔄 Synced: .claude/specs <= .agents/specs` | specs 使用 sync mode | 告知使用者目前仍採 real-directory sync，而非 symlink |
| `🔗 Created: .claude/specs -> .agents/specs` | specs 使用 symlink mode | 告知使用者這是明確 opt-in 行為 |
| `⚠️ CLAUDE.md is a real file` | 子目錄已有手寫的 `CLAUDE.md` | 告知使用者檢查內容是否需要保留，必要時合併到 `AGENTS.md` |
| `❌ Not a git repository` | `--staged` 模式下專案不是 git repo | 改用 full scan 模式（不加 `--staged`） |

## 與現有專案整合

- 優先檢查 `skills/` 子路徑狀態（`ls -la .claude/skills .kiro/skills .codex/skills`）而不是 whole root
- 若 repo-local `skills/` bridge 已正確存在，無需重新執行 init
- 若 repo 曾追蹤 `.claude/skills`、`.kiro/skills`、`.codex/skills`，提醒使用者檢查 `git status` 並自行決定是否需要 untrack 既有路徑
- 若使用者只新增了 `AGENTS.md`，只需執行 `sync-claude-md`
- 若使用者只想切換 `specs` 策略，可重跑 `init.sh --specs-mode sync|symlink|skip`
- 若 repo 先前真的依賴 whole-directory `.claude/.kiro/.codex -> .agents` 取得某些 local config，這些檔案在 backup 後**不會自動拷回新 root**；切換完成後應重新執行既有 sync flow 或人工核對需要保留的設定。
