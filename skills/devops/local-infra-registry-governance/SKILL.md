---
name: local-infra-registry-governance
description: Registry-first local development infrastructure governance. Use whenever work needs to start, inspect, request, reuse, release, or reconcile local dev/UAT/E2E services, localhost ports, networks, compose stacks, or per-project environment instances—even if the user only says “run the stack”, “reuse this env”, “clean up stale local services”, or asks about local port conflicts. Also use before launching or coordinating any GPU workload on this host's shared single GB10 GPU (vLLM/local-nemotron, DoMINO/PhysicsNeMo, model training)—including any cross-project request to avoid GPU memory OOM, or when a non-aclab-middlewares project (e.g. giant-aero) needs the GPU and must coordinate with aclab-middlewares' vLLM first. Direct infra actions that bypass the local infra registry are forbidden.
---

# Local Infra Registry Governance

這個 skill 專注於 **local development infrastructure governance**，不是單純的容器操作技巧。

## Terminology (避免 local / global 語意混淆)

這裡的幾個詞，必須固定這樣理解：

- **local infra**：從 infra / runtime 角度來看，指 **machine-local infrastructure runtime**，也就是這台電腦上的 Podman、localhost ports、networks、compose stacks、per-instance env。
- **global registry path**：從 agent / repo 邊界角度來看，指 **machine-scoped path outside the workspace**。也就是「整台電腦共用，但不屬於單一 workspace」的 registry 檔案位置。
- **workspace-scoped**：只屬於當前 repo / workspace 的穩定文件，例如 workspace `AGENTS.md`。

所以：

- `local` **不是** 指 workspace-local
- `global` **不是** 指 organization-wide 或 multi-machine shared service
- `workspace-scoped AGENTS.md` 與 machine-scoped registry 是兩個不同層級

真正需要被嚴格一致化的是 **local infra registry**；agent、workflow skill、script、human operator 都只是 client。只要 infra 行為繞過 registry，該行為就不合法。

在導入初期允許 **transition bootstrap**：若 target project-instance 的 current state 已存在，但 registry 尚未建立對應 entry，必須先把 current state 登錄進 registry，再做 reuse / release / gc 等 lifecycle 決策。

## Global Registry Path (Machine-scoped, outside workspace)

這裡的 global local infra registry 指的是：

- Root: `~/.config/opencode/local-infra/`
- SSOT JSON: `~/.config/opencode/local-infra/registry.json`
- Global lock: `~/.config/opencode/local-infra/registry.lock`

這是 **machine-local runtime state**，而且它位於 **workspace 之外**；不是 workspace artifact，也不是 feature registry。

- 應由 repo `.gitignore` 忽略
- 不得把它搬進 `SPECS.md`、`NEXT_STEPS.md`、或 global / workspace `AGENTS.md` 當 runtime ledger
- workspace `AGENTS.md` 只保存 stable canonical naming / alias / service bundle policy，不保存 `registry.json` 的 live contents

## 何時使用

- 需要啟動、重用、釋放或回收 local dev / UAT / E2E 環境
- 需要處理 localhost port 衝突、network 衝突、compose stack 命名衝突
- 需要判斷某個 project-instance 是否仍然有效，或是否已 stale / expired / orphaned
- 使用者要求「幫我跑 backend + frontend」、「把 e2e stack 跑起來」、「看看哪些 local env 可以回收」
- workflow skill 需要決定是否應該 request 新 instance、reuse 舊 instance、或先做 reconcile

## 已確認的治理決策

- **project metadata** 與 **project-instance lifecycle** 必須分開治理
- `project-instance` 的 reuse / release / gc 只能依據 **exact match**、**resolver 明確結果**、或 **HITL 明確選擇**
- ambiguous candidate 不可由 agent 自行猜測；應列出同 project 的候選 instances，交由 developer 做 HITL 選擇，或明確選擇新建
- canonical project naming / alias / service bundle 規則只能寫回 **workspace-scoped `AGENTS.md`** 或該 workspace 指定的穩定檔案，不得寫入 global `AGENTS.md`
- runtime success 以 **1..n required services 的 bundle readiness** 為準，不可只用單一 port / 單一 container 存活判定為可用

## 不要用在這些情況

- 已經有明確 allocation，現在只需要決定 compose / Podman 的落地細節 → 交給 `devops-container-orchestration`
- 純 feature / contract / spec 治理工作，沒有 live local infra 動作 → 留在 `spec-driven-development` / `spec-registry-manager`
- 單純閱讀 code、寫文件、跑不依賴真實服務的 unit test

## 先讀什麼

- 需要知道 registry.json / lock / observed / instances 的實體位置 → 讀 [references/registry-model.md](references/registry-model.md)
- 需要理解資料模型、TTL、resource ownership → 讀 [references/registry-model.md](references/registry-model.md)
- 需要判斷 `active / stale / expired / orphaned` → 讀 [references/reconcile-lifecycle.md](references/reconcile-lifecycle.md)
- 需要規劃 tool invocation 或回報格式 → 讀 [references/tool-contract.md](references/tool-contract.md)
- 需要判斷哪些資訊該放進 `SPECS.md` / `NEXT_STEPS.md` → 讀 [references/integration-boundaries.md](references/integration-boundaries.md)
- 需要在共用 GB10 GPU 上啟動 / 協調 GPU workload（vLLM、DoMINO/PhysicsNeMo、GPU 訓練），或跨專案避免 GPU 記憶體 OOM → 讀 [references/shared-gpu-coordination.md](references/shared-gpu-coordination.md)

## 核心不變量

1. **No registry entry → no lifecycle decision until bootstrap registration or governed request completes**
2. **No registry query / lock / reconcile / bootstrap → no start / reuse / release / gc**
3. **`podman ps` 是 observed reality，不是 authoritative state**
4. **不可手動猜測或私自分配 host ports / networks / stack names**
5. **runtime allocation state 不可寫進 `SPECS.md` 當成 feature registry**
6. **workspace-scoped `AGENTS.md` 只能保存穩定 canonical naming / alias / bundle policy，不得保存 live instance inventory**
7. **Repo-side governed runtime preparation (本地準備) 與 actual external runtime execution (外部執行) 必須嚴格區分。**
   - 當 local infra 僅用於準備外部交接包（如 arm64 驗證、CI 驗證）時，不可在 repo docs 中假裝外部執行已在本地發生。
   - `request/reuse/release` 工作若僅為本地準備，必須明確標示為 `completed-handoff` 或 `external-blocked`，而非 `completed-local`。
   - 確保 `NEXT_STEPS.md` 中只有唯一權威的 handoff path，不可同時存在「completed handoff」與「still active local work」。
8. **若使用者明確表示 external execution 已在別處完成，必須立即 hard-stop local infra flow。**
   - 此時不得再 request / reuse / bootstrap / release 來「補做一次本地驗證」。
   - 應改為回報 stale-state reconciliation 需要更新的 repo artifacts，並把 canonical lifecycle state 留給 shared spec governance taxonomy 判定。

## 標準執行順序（Pipeline）

依序執行，前一步未滿足就停止：

1. **確認真的需要 local infra**
2. **查詢 authoritative registry state**
3. **判斷是否存在可 bootstrap-register 的 current state**
4. **取得 lock / ownership evidence**
5. **reconcile observed state**
6. **若符合條件，先做 bootstrap registration**
7. **選擇唯一合法動作**：`registry status` / bootstrap register / request / reuse / release / gc
8. **執行後做 reviewer self-check**，確認沒有 bypass、沒有 guessed resources、沒有把 live state 寫進治理文件

若任何一步失敗，停止 infra action，改做 blocker 回報。

若在進入或執行途中發現「外部執行其實已在別處完成」，也要停止 infra action；接下來只能回報 repo-side reconciliation / handoff state，不可繼續 local lifecycle 動作。

## 你的責任

### 1. 先判斷是否真的需要 local infra

如果任務只是在讀文件、改程式碼、寫 spec、跑 unit test，通常不需要啟動 local stack。

如果使用者已明確說明 external execution 已在別處完成，也不需要 local infra；此 skill 在該情況下只能協助描述目前是否存在 repo-side handoff / stale-state 清理需求。

只有在以下情況才進入 infra flow：
- 需要真實啟動 backend / frontend / worker / database
- 需要 E2E 或 manual QA
- 需要檢查既有 instance 是否仍可 reuse
- 需要清理過期或失效的 local env

### 2. 任何 infra 動作前，先查 registry

你必須先取得下列資訊，而不是直接執行 compose / podman：

- 哪些 resources 已被鎖定
- 這些 resources 屬於哪個 `project-instance` / `stage`
- 本 project 是否已有可 reuse 的 instance
- 目前的 target project 是否已有 stable metadata / alias / service bundle 定義
- 是否存在 `stale` / `expired` / `orphaned` 候選
- 現在要做的是 `bootstrap register`、`request`、`reuse`、`release` 還是 `gc`

### 2.2 Project metadata 與 instance lifecycle 分離

- **project metadata**：描述 stable canonical project identity、workspace-scoped aliases、declared stages、required service bundles（per-profile 定義）、helper_script（governed 腳本路徑）、以及 designated guidance file path。詳見 [references/registry-model.md](references/registry-model.md) 的 `service_bundles{}` schema。
- **project-instance lifecycle**：描述某個具體 env instance 的 owner、TTL、resources、`status.phase`、與是否可 reuse / release / gc。

缺少 project metadata，不等於應直接建立新的 runtime instance。先補 metadata，再判斷 instance lifecycle 動作。

### 2.3 Exact Match → Resolver → HITL

當你要做 reuse / bootstrap / release / gc 時，遵循以下順序：

1. **Exact match**：canonical `project + instance + stage` 完全匹配
2. **Deterministic resolve**：registry-governed resolver 或 alias map 能明確回傳唯一 canonical target
3. **HITL selection**：若仍有多個合理 candidates，列出該 project 下所有候選 instances，讓 developer 明確選「用哪一個」或「新建」

禁止做法：
- 根據名稱相似度、自行猜測 synonym、prefix、縮寫
- 根據「看起來最像」就直接 reuse
- 在 ambiguous state 下默默 bootstrap 到你認為合理的 instance

### 2.4 1..n Service Bundle Readiness

runtime success 不是「某個 port 打得開」就算成立。

- 每個 project 或 project-instance 應宣告一組 **required services[]**
- 只有當該 bundle 中 **所有 required services 都 ready**，才可視為 `active` / reusable
- 若只啟動了部分 services，應視為 **bundle not ready**，並進入 `inconclusive` 或其他更合適的非成功判定，而不是當成可直接 reuse 的 env

### 2.5 Transition bootstrap：先登錄現況

導入初期，某些 project-instance 可能已經有 local infra 在跑，但 registry 還沒有 entry。這時不能直接把它視為 blocker，也不能直接跳過 registry 接手使用。

正確做法是：

1. 先確認這是一個 **缺少 registry entry 的 current state**，而不是單純的未知 process
2. 取得 lock / ownership evidence
3. reconcile observed state，確認這個 current state 足以安全登錄
4. 用 registry-governed tool 將目前 observed state bootstrap-register 成正式 entry
5. bootstrap 完成後，再進入正常的 reconcile / reuse / release / gc 流程

如果 current state 只能辨識到 project，但無法唯一辨識 instance，先列出該 project 下的候選 instances 做 HITL；不可由 agent 自行決定要 bootstrap 到哪個 instance 名稱。

bootstrap 不是 workaround，而是 transition period 的正式治理步驟。

### 3. 將 action 限制在 registry-governed tool contract 內

允許的高階意圖只有：

- `registry status`
- `bootstrap register`
- `env request`
- `env reuse`
- `env release`
- `gc`

如果沒有可用的 registry-governed tool，就回報缺口，不可自行繞過。

### 4. 先 reconcile，再做破壞性或配置性動作

在以下情況，必須優先 reconcile：

- 即將 request 新 instance
- 即將 release 現有 instance
- 即將做 gc
- 懷疑 registry 與 podman observed state 已不同步
- 需要解釋 port / network 衝突原因

若 evidence 不足以安全判斷 `active / stale / expired / orphaned`，不得硬猜；應先回報 evidence gap。

### 5. 將結果回報成治理語言，而不是 shell 語言

回報時應包含：

- `project`
- `instance`
- `stage`
- action 類型（`registry status` / `bootstrap register` / request / reuse / release / gc）
- reconcile 結果（如 `active`, `stale`, `expired`, `orphaned`）
- `candidate_instances[]`（若 exact match 不存在但 project 存在）
- `selection_required`（若需要 developer HITL）
- `services[]` / bundle readiness 摘要
- 資源摘要（ports / networks / stack）
- 下一步（繼續使用、等待批准、可安全回收、外部執行交接）
- **外部執行狀態 (External Execution State)**：若 local infra 僅用於準備外部交接包，必須明確標示為 `completed-handoff` 或 `external-blocked`，並說明實際執行將在外部進行。

不要只回報「我跑了 podman-compose up」。

## 標準流程

### A. Registry Status / Inventory

1. 查詢 authoritative registry state
2. 必要時 reconcile observed state
3. 若 project exact match 不存在，但有 alias / metadata 候選，先透過 deterministic resolver 收斂
4. 若 project 找到但 instance 非 exact match，列出該 project 的所有 candidate instances 供 HITL 選擇
5. 將結果整理成治理語言，而不是 runtime dump
6. 回報 `project` / `instance` / `stage` / `status.phase` / `services[]` / next step

### B. Bootstrap Register Current State

1. 查 registry，確認 target project-instance 尚未有 entry
2. 確認 observed current state 的確存在，而且足以辨識為同一個 project-instance / stage
3. 取得 lock / ownership evidence
4. 先 reconcile observed current state，確認它適合被正式登錄
5. 透過 registry-governed tool 將 observed current state 登錄成正式 entry
6. bootstrap 完成後，立即做一次 reconcile
7. 回報 bootstrap source、registered resources、`status.phase` 與後續 next step

### C. Request New Instance

1. 確認任務真的需要 local infra
2. 先確認 project metadata 是否存在；若 project 完全沒有紀錄，先建立 project metadata
3. 查 registry，確認是否已有 exact-match instance 可 reuse
4. 若沒有 entry，先判斷是否應 bootstrap register current state；只有在無現況可登錄時才 request 新 instance
5. 若 exact match 不存在但同 project 有多個 candidate instances，列出候選並要求 HITL 選擇或明確新建
6. 先取得 resource lock / allocation evidence
7. reconcile 當前 state
8. 透過 registry-governed tool 建立 instance
9. 回報 env id、stage、locked resources、required `services[]`、TTL 與後續 cleanup 預期

### D. Reuse Existing Instance

1. 先做 exact match；若沒有，再看 deterministic resolver 是否能得到唯一 canonical instance
2. 若仍有多個 candidates，列出該 project 的所有 instance 給 developer 做 HITL 選擇
3. 確認 TTL 仍有效
4. reconcile observed state，確認不是 stale / orphaned，且 required `services[]` bundle 已 ready
5. 只有在條件成立時才 reuse
6. 回報 reuse 理由、candidate selection 根據、與 bundle readiness，而不是默默接手他人的 local env

### E. Release / GC

1. 先 reconcile
2. 只針對 `stale` / `expired` / `orphaned` 做 candidate 判定
3. release 後必須同步更新 registry
4. 回報釋放了哪些 resources，避免下一位 agent 重複誤判

## 成功輸出最小格式

當 action 合法且可前進時，優先用這種治理格式回報：

```text
Local infra action summary:
- project: <project>
- instance: <instance>
- stage: <stage>
- action: <registry status|bootstrap register|request|reuse|release|gc>
- status.phase: <active|stale|expired|orphaned|inconclusive>
- candidate_instances: <[] or summary>
- selection_required: <true|false>
- bundle_readiness: <required_services[] readiness summary>
- resource_summary: <ports/networks/stack 高層摘要>
- ttl_or_expiry: <ttl / expiry summary>
- next_step: <bootstrap register|developer selection|reuse|implement with devops-container-orchestration|release|wait>
```

## 常見錯誤與正確做法

### 錯誤：直接執行 compose / podman

> 「先把 backend 跑起來再說」

正確：
- 先查 registry
- 判斷 bootstrap register / request / reuse / release / gc
- 透過 registry-governed tool 執行

### 錯誤：導入初期看到沒 registry entry 就直接當 blocker

> 「沒有 registry，那就先擋住，等人手動補」

正確：
- 如果 current state 已存在，先 bootstrap-register 現況
- bootstrap 後再進入正常 lifecycle decision
- 只有在既無 entry、又無可辨識 current state、且 tool 也無法建立 request 時，才回報 blocker

### 錯誤：把 live port allocation 寫進 `SPECS.md`

> `SPECS.md` 應該記錄 feature / contract governance，不應記錄 `localhost:49152` 目前被誰佔用。

正確：
- runtime allocation state 留在 local infra registry
- `SPECS.md` 只保留高層治理與依賴資訊

### 錯誤：把 `podman ps` 視為唯一真相

> `podman ps` 只能告訴你 observed reality。它不能回答 ownership、TTL、歷史使用者、或是否應該釋放。

正確：
- 以 registry 為 authority
- 以 `podman ps` / network inspect 作為 reconcile input

## 與其他 skills 的邊界

- `devops-container-orchestration`：提供 compose / port / rootless Podman 的實作模式，但**不應取代 registry 決策**
- `spec-driven-development`：在 design / tasks / implementation / review 階段必須尊重此 skill 的治理規則
- `spec-registry-manager`：管理 `SPECS.md`，不是 live infra allocation registry
- shared spec governance taxonomy（`requirements.md` / `design.md` / `review.md` / `SPECS.md` / `NEXT_STEPS.md`）才是 canonical lifecycle / handoff state 的 authority；此 skill 只回報 runtime-side operational handoff posture，不負責改寫 canonical spec semantics

## Reviewer Self-Check

在完成任何 local infra 決策或建議前，讀取 [references/fmea-review-checklist.md](references/fmea-review-checklist.md) 並快速檢查：

- 是否跳過 registry query / lock / reconcile
- 是否把 `podman ps` 當成 source of truth
- 是否在 evidence 不足時硬做 lifecycle 判定
- 是否把 runtime allocation state 寫進 `SPECS.md` / `NEXT_STEPS.md`
- 是否在 tool 缺失時主動繞過治理流程
- 若使用者已聲明 external execution completed elsewhere，是否確實 hard-stop 而不是重新開 local runtime lane

## 無法安全前進時怎麼做

如果缺少下列任何一項，就應停止 infra action，回報缺口：

- registry state 不可讀
- lock acquisition 不可用
- reconcile 結果不可信
- registry-governed tool 不存在或 contract 不明
- transition bootstrap 所需的 current-state evidence 不足，且也無法安全 request 新 instance

尋找該工具時，優先順序應為：

1. 當前 workspace 的 `AGENTS.md` / project guide / local scripts
2. 已約定的 repo-level skill / docs 中提到的 tool path 或 command
3. 如果以上都不存在，再明確回報缺少 implementation，而不是自行繞過

此時應回報：
- 缺的是哪個治理前置條件
- 哪個 action 被阻擋
- 需要補什麼工具或決策

建議回報格式：

```text
Blocked by local infra governance gap:
- requested_action: <bootstrap register|request|reuse|release|gc>
- missing_precondition: <registry unreadable|lock unavailable|reconcile inconclusive|tool missing|bootstrap evidence missing>
- observed_evidence: <what was actually checked>
- safe_next_step: <what human/tooling must provide>
```

不要用臨時 port、臨時 stack name、或手動 compose up 當 workaround。
