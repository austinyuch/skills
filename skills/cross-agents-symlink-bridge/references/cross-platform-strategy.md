# Cross-Platform Strategy: Symlink vs Junction vs Sync

本文件說明 cross-agents-symlink-bridge 在不同作業系統上的技術選擇、限制與故障排除。

> 本 skill 現在採用 **hybrid strategy**：
>
> - repo-local `skills/` 一律走 symlink / Junction，避免重複副本
> - repo-local `specs/` 可選擇 **sync** 或 **symlink**
> - 其他 `.claude/.kiro/.codex` 內容保持 real directory / real files，避免權限與 runtime state 被 whole-directory link 接管

---

## 機制選擇

| 平台 | `skills/` 機制 | `specs/` 機制 | `CLAUDE.md` 機制 | 權限需求 |
|---|---|---|---|---|
| Linux | `ln -s` (symlink) | `rsync` 或 `ln -s` | `ln -s` | 無 |
| macOS | `ln -s` (symlink) | `rsync` 或 `ln -s` | `ln -s` | 無 |
| Windows | `mklink /j` (Junction) | `robocopy` 或 `mklink /j` | `mklink` | Junction 無需管理員 |

### 為什麼 Windows 使用 Junction 而非 Symlink？

- **Junction** (`mklink /j`) — 不需要系統管理員權限，對開發者最友善
- **Symlink** (`mklink /d`) — 需先開啟 Windows 開發者模式

限制：Junction 只能在同一個磁碟上運作。若專案跨磁碟，需改用 Symlink。

---

## 限制與故障排除

### 1. Junction 跨磁碟失敗

若 `mklink /j` 因跨磁碟而失敗，`init.ps1` 會自動提示使用 `mklink /d`。

手動改用 Symlink（需先開啟開發者模式）：

```powershell
cmd /c "mklink /d .claude\skills ..\.agents\skills"
cmd /c "mklink /d .kiro\skills ..\.agents\skills"
cmd /c "mklink /d .codex\skills ..\.agents\skills"
```

### 2. Git clone 後 Symlink 變成文字檔（Windows）

若 Windows 開發者在未設定 `core.symlinks true` 的情況下 clone 包含 symlink 的 repo，連結會被還原為普通文字檔。

**預防**：在 clone 前設定 `git config --global core.symlinks true`

**修復**：刪除壞掉的檔案，重新執行 `init.ps1`

### 3. Whole-directory agent roots 不再建議 symlink

若 repo 內已有 whole-directory `.claude/`、`.kiro/`、`.codex/` symlink，初始化腳本會先把這些 root 恢復成 real directories，再只管理 `skills/` 與（可選）`specs/` 子路徑。

這樣做的原因是：Claude / Codex 的 permission、approval、sandbox、runtime state 常常不適合被整個 symlink root 接管。

注意：這個切換只保證新的 hybrid bridge 成立；它**不會自動把舊 whole-root bridge 底下的 local config state 複製回新 root**。若團隊原本依賴另外一條 sync workflow 來填入 repo-local settings，切換後要重新執行該 sync。

### 4. IDE / Plugin 沙箱限制

少數 AI 插件可能拒絕讀取 symlink。若遇到 repo-local `skills/` 讀不到內容：

```bash
rm -rf .claude/skills .kiro/skills .codex/skills
cp -r .agents/skills .claude/skills
cp -r .agents/skills .kiro/skills
cp -r .agents/skills .codex/skills
```

但這失去 symlink 的即時同步優勢，僅作為最後手段。

### 5. Git for Windows 的 Symlink 支援

Git for Windows 預設不處理 symlink。若團隊決定將 generated symlink 納入版控，所有 Windows 成員需設定：

```bash
git config --global core.symlinks true
```

本 skill 預設採用「腳本生成方案」（generated symlink 不進版控），避免此問題。

---

## `.gitignore` 策略

本 skill 使用「只忽略成功建立的 generated symlink」策略：

- `.claude/skills`、`.kiro/skills`、`.codex/skills` 一旦建立成功，就加入 `.gitignore`
- `.claude/specs`、`.kiro/specs`、`.codex/specs` **只有在 specs-mode = symlink** 時才加入 `.gitignore`
- `CLAUDE.md` 由獨立 managed section 管理，避免和 bridge paths 混在一起留下 stale entries

這樣確保：

- skills 不會在 `.claude/.kiro/.codex` 之間重複複製
- whole-directory symlink 不再接管 Claude / Codex 的 permission 或 runtime state
- generated symlink 不會在不同 OS 上造成 Git 衝突
- 每個開發者 clone 後只需執行 init 腳本即可

### specs mode caveat

若你選擇 `specs-mode=symlink` 且 `.claude/specs`、`.kiro/specs`、`.codex/specs` 原本存在實體目錄，腳本會先把目標內容 merge 回 `.agents/specs/`，再建立 symlink。若同路徑檔案衝突，最後一次同步進去的內容會覆蓋先前版本，因此在切換成 symlink 前最好先 review 差異。

### tracked file caveat

`.gitignore` 只會影響尚未被追蹤的路徑。若 `.claude/skills`、`.kiro/skills`、`.codex/skills` 或 `CLAUDE.md` 先前已進入 git history，建立 ignore 規則後仍可能在 `git status` 中顯示刪除 / 變更；這需要人工決定是否保留、untrack，或重新整理工作樹。

另外，`sync-claude-md` 的 full scan 會刻意排除 `.claude/`、`.kiro/`、`.codex/` 子樹，避免在 generated agent directories 裡再次生成 `CLAUDE.md`。
