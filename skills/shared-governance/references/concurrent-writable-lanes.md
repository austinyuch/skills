## Concurrent Writable Lanes

這份 reference 專門處理：當多條 lane 可能同時碰到同一份 authoritative artifact 時，要如何避免衝突與錯誤 writeback。

### 1. 核心原則

- 同一份 authoritative artifact，同時間只能有 **一條 authoritative writable lane**
- 其他 lanes 可以盤點、比對、提出 draft、產出報告，但不得搶先正式 writeback
- 若 ownership 不清楚，預設 **降級為 audit-only**，而不是繼續寫

### 2. 典型衝突面

這套規則主要用在：

- `SPECS.md`
- `RTM.md`
- workspace `.agents/specs/TESTS.md`
- folder-level `TESTS.md`
- shared governance references / repo-owned global skill wording

### 3. 進場前判斷

在寫入前先回答：

1. 這份 artifact 的 upstream authority 是什麼？
2. 目前哪一條 lane 擁有正式 writeback 權？
3. 我這條 lane 是 authoring lane、registry/test-governance lane，還是只是 compare/audit lane？
4. 若另一條 lane 正在改同一份 artifact，我是否應停寫並轉成 audit-only？

### 4. Mandatory downgrade conditions

若出現以下任一情況，必須停止正式 writeback，改成 **audit-only / reconcile-first**：

- 發現另一條 writable lane 已明確擁有同一份 authoritative artifact
- 欲重用 worktree 時，發現它被其他 session / agent 佔用
- worktree 不乾淨，且未提交內容不屬於當前 lane 的合法上下文
- detached audit lane 已累積變更，但尚未被正式提升為新的 authoring lane
- 你手上的 upstream authority 已被較新的 branch-spec / report / evidence 推翻
- 使用者提供了更新的事實，讓舊 lane identity 或 writeback 假設不再成立

### 5. Conflict handling workflow

#### Case A: 另一條 lane 已擁有 writeback 權

- 停止本 lane 的正式寫入
- 將本 lane 降級為 compare / audit lane
- 只輸出：drift findings、draft summary、conflict note、或 reconcile 建議
- 由 authoritative writable lane 吸收這些發現

#### Case B: 我方 lane 是 authoritative，但 upstream 已變

- 停止當前 writeback
- 重讀 upstream authority
- 重新生成 snapshot / rollup
- 不得在舊 snapshot 上做 incremental patch 後硬寫回

#### Case C: 兩條 lane 都聲稱自己是 authoritative

- 視為治理衝突
- 暫停雙方正式 writeback
- 回到 owner / scope / latest-fact resolution
- 明確指定唯一 writable lane 前，不得繼續寫入 authoritative artifact

### 6. Per-artifact guidance

#### `SPECS.md` / `RTM.md`

- 同時間只允許一條 registry writeback lane
- compare lane 可 detached/read-only
- 若 implementation / CR lane 同時也碰 registry，implementation lane 預設不擁有 registry 最終 writeback 權，除非明確聲明它就是當前 registry lane

#### workspace `.agents/specs/TESTS.md`

- 只能由 test-governance lane 做最終 rollup writeback
- implementation lanes 可提供 upstream evidence、draft rows、stale markers 建議，但不應搶寫 workspace rollup

#### folder-level `TESTS.md`

- 仍屬 row-level authority
- 若多條 lanes 同時會改同一份 catalog，必須先收斂唯一 writer

#### shared governance references / global skills

- 同時間只允許一條 repo-owned governance authoring lane
- 其他 lanes 只能 review / compare / propose wording

### 7. Output discipline

當 lane 被降級或停止 writeback 時，至少留下：

- 目前為何不能正式寫入
- 哪條 lane 被視為 authoritative
- 需要重讀哪些 upstream authorities
- 下一步是 reconcile、handoff，還是等待 owner resolution

### 7.5 Evidence requirements

- 正式 writeback 前，應先留下 `./ownership-evidence-template.md` 所要求的最小 ownership evidence
- formal review / closeout 時，應使用 `./conflict-evidence-review-checklist.md` 檢查本次治理是否真的成立
- 若更新會牽涉多份 derived artifacts，必須同時遵守 `./cross-artifact-regeneration-order.md`
- ownership / conflict evidence 必須落在 invoking repo/workspace 內的治理 artifact surface，而不是 global skills 安裝目錄

### 8. Forbidden moves

- 發現衝突後仍繼續對 authoritative file 直接 patch
- 在 detached audit lane 長期累積變更，最後直接當正式 writeback
- 讓 derived artifact 回填另一個 derived artifact，試圖「就地收斂」
- 用 machine-local worktree path 當成 ownership 記號寫進治理 artifact
