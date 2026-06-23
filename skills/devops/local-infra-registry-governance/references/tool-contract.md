# Registry-Governed Tool Contract

這個 skill 假設 local infra 的實際操作會透過一個 **registry-governed tool** 完成。

此文件定義的是 contract，不代表這個 repo 已經內建該工具。

## Global Registry Files

這裡的 **global** 指的是「整台電腦範圍、workspace 之外」，不是多台機器共享的 central service。

預設 global runtime registry 檔案位置：

- `~/.config/opencode/local-infra/registry.json`
- `~/.config/opencode/local-infra/registry.lock`

如果 workspace 使用其他 path，必須由 **workspace-scoped `AGENTS.md` 或 designated workspace guide** 明確覆寫；否則預設就是這個 global path。

## 允許的高階命令

### 1. `registry status`

用途：
- 列出目前 `active / stale / expired / orphaned` instances
- 顯示 project、stage、resources、last_used、ttl 摘要
- 若 exact instance 不存在但 project 存在，列出該 project 下所有 candidate instances 與其 `required_services[]` / bundle readiness 摘要

### 2. `bootstrap register`

用途：
- 在 transition period 中，為已存在但尚未登錄的 project-instance current state 建立正式 registry entry

必備前置：
- registry query 確認 target entry 不存在
- current-state evidence 足以辨識 target project-instance / stage
- lock acquisition
- reconcile-ready observed state

bootstrap register 不可用於解決「名稱看起來像」的 ambiguity。若同 project 下有多個 plausible candidates，但沒有 deterministic resolver 結果，必須轉入 HITL 選擇。

### 3. `env request`

用途：
- 為特定 `project + stage + services` 申請新的 local env

必備前置：
- registry query
- project metadata 已存在；若 project 完全沒有紀錄，先建立 project metadata
- lock acquisition
- reconcile

### 4. `env reuse`

用途：
- 在條件允許時重用既有 env

必備判斷：
- exact canonical instance 是否匹配；若否，resolver 是否回傳唯一 canonical target
- 若同 project 下仍有多個 plausible candidates，必須先做 developer HITL selection
- stage 是否匹配
- TTL 是否仍有效
- reconcile 結果不是 `stale / expired / orphaned`
- `required_services[]` bundle 全部 ready

### 5. `env release`

用途：
- 釋放指定 env 的 resources

必備前置：
- reconcile
- registry update

### 6. `gc`

用途：
- 清理 `stale / expired / orphaned` 候選

必備前置：
- registry status
- reconcile
- 明確 candidate selection

## Tool Discovery Order

在宣告「缺少 registry-governed tool」之前，應依序檢查：

1. workspace `AGENTS.md` / project guide / local scripts
2. repo-level skill / docs 中已約定的 tool path 或 command
3. 若 target project-instance 沒有 registry entry，先判斷是否可用同一組工具做 `bootstrap register`
4. 若以上都不存在，再回報 tool gap

不得跳過 discovery 直接說「沒有工具」，也不得把 compose / podman 包一層就自稱等價工具。

## 什麼才算等價的 registry-governed tool

只有同時滿足以下條件，才可視為等價：

1. 支援 `registry status`、`bootstrap register`、`env request`、`env reuse`、`env release`、`gc`
2. 有自己的 authoritative state，不是只包裝 `podman ps`
3. 能支援 query → lock → reconcile → action → update 的治理順序
4. 能支援 exact match / deterministic resolve / HITL escalation 的選擇邏輯

若無法證明這三點，agent 不可聲稱它是「等價的 registry-governed tool」。

## 回傳結果至少要有什麼

無論是哪個命令，回傳都應包含：

- `project`
- `instance`
- `stage`
- `action`
- `status.phase`
- `allocated_or_released_resources`
- `ttl_or_expiry_summary`
- `registration_source`（若 action = `bootstrap register`）
- `required_services[]` / bundle readiness 摘要
- `candidate_instances[]`（若 exact match 不存在且 project 存在）
- `selection_required`（若需要 developer HITL）

## Update Contract

任何會改變 registry state 的命令（`bootstrap register` / `env request` / `env release` / `gc`）都必須：

1. 取得 `registry.lock`
2. 讀取目前 `registry.json`
3. 更新 observed state / reconcile 結果
4. 以 atomic write 覆蓋 `registry.json`
5. 釋放 lock

不得：

- 無 lock 直接改 `registry.json`
- 修改一半就中斷
- 只改 `instances/*` 而不更新 `registry.json`

## 鐵律

- **No registry entry → bootstrap register current state or request new env before lifecycle action**
- **Registry out-of-date → reconcile first**
- **Observed conflicts → explain them through registry lifecycle language**
- **Inconclusive evidence → stop and escalate, do not guess lifecycle state**
- **No non-exact reuse without deterministic resolver or explicit HITL choice**

## 不可接受的替代做法

- 直接 `podman compose up -d`
- 先挑一組看起來沒人用的 port 再補 registry
- 直接根據 `podman ps` 判斷「應該可以 reuse」
- transition period 明明可以 bootstrap register，卻直接把「沒 registry entry」當成永久 blocker
- 因為名稱相似、prefix 相同或 human wording 接近，就自行把兩個 instance 當成同一個
- 只看到某一個 service 存活，就把整個 project-instance 視為 ready / reusable

如果工具還不存在，agent 應回報「缺少 registry-governed tool contract implementation」，而不是自行繞過。

若 registry state 不可讀、lock 無法取得、或 reconcile 結果不可信，也應視為同級 blocker。
