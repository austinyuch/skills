# Reconcile Lifecycle

## 為什麼要 reconcile

registry 記錄的是 **宣告的 ownership**，但 local infra 可能已經被人工操作、異常退出、或長時間閒置。

reconcile 的任務，是比較：

- registry 的 declared state
- Podman / network inspect 的 observed state

然後推導出目前最合理的 lifecycle status。

## 何時必須 reconcile

- request 新 instance 前
- bootstrap register current state 前後
- reuse 舊 instance 前，且對其健康狀態沒有把握
- release 或 gc 前
- 出現 port / network 衝突時
- registry 顯示存在，但 `podman ps` 看起來不像真的在運作時

## 推導狀態

| 條件 | `status.phase` | 解讀 |
|---|---|---|
| TTL 有效，且 `required_services[]` 全部 observed 正常 | `active` | 可繼續使用 |
| 所有相關 containers 已 exited | `stale` | 應審查是否可釋放 |
| TTL 已超過 | `expired` | 優先列入 release / gc 候選 |
| registry 有紀錄，但 observed resources 不存在 | `orphaned` | registry 與 reality 脫鉤，需收斂 |

若 evidence 不足以安全分類，應標記為 **inconclusive** 並停止 destructive action，而不是硬判成上述任一狀態。

若只有部分 services 存活，或無法證明 `required_services[]` bundle 已全部 ready，也應優先視為 **inconclusive**，而不是 `active`。

若 target project-instance 尚無 registry entry，但 observed current state 足以辨識，就應先進入 **bootstrap registration**，而不是直接把它視為普通 orphaned event。

## 重要原則

### Reconcile ≠ Auto Delete

reconcile 只負責標記與解釋狀態，不自動替你做所有破壞性操作。

後續是否要：
- reuse
- release
- gc

應由 registry-governed tool 與明確意圖來執行。

### `podman ps` 不是 source of truth

`podman ps` 無法告訴你：

- 這個 env 屬於哪個 project-instance
- TTL 是否已過期
- 是否允許另一個 agent 接手 reuse
- 哪些 port 是正式鎖定的，哪些只是殘留 process

因此你不能跳過 registry 直接用 observed state 做 allocation 決策。

### Exact Match → Resolver → HITL

在進入 reuse / release / gc 前：

1. 先做 exact canonical instance match
2. 若沒有 exact match，再看 deterministic resolver 是否回傳唯一 canonical target
3. 若同 project 下仍有多個 plausible candidates，必須先進 developer HITL selection

不可因為名稱相似或 stage 看起來接近，就自行推論兩個 instances 等價。

## TTL 與狀態轉換由誰負責

TTL 不是靠 agent 記憶維持的。正確責任應為：

- registry-governed tool 在 read / request / reuse / release / gc 前重新計算 TTL
- agent 只負責要求進行這個檢查，不自行假設 TTL 已被背景程序處理

如果沒有這樣的 tool，就必須把 TTL enforcement 視為 open implementation gap。

## Out-of-Sync Resolution

若 declared state 與 observed reality 明顯不一致：

- 不要直接做新 allocation
- 不要直接當成可 reuse env
- 應優先標記為 `orphaned` 候選，或在證據不足時標記為 `inconclusive`
- 先回報治理事件，再等待收斂工具或人類決策

若 exact match 不存在，但 project 存在多個 candidate instances，也不應直接挑一個 reuse；先列出 candidates，再走 deterministic resolver 或 HITL。

## Human-Operator Bypass

若 observed state 存在，但 registry 沒有對應 entry，這通常表示：

- human 直接操作 compose / podman
- 舊流程繞過 registry
- runtime state 漏寫或 registry 已損毀

此時不可直接接手 reuse。正確做法是：

1. 先判斷這是否是 transition period 中可 bootstrap-register 的 current state
2. 若可辨識 target project-instance / stage，先取得 lock / ownership evidence
3. 先 reconcile observed current state，確認它適合被正式登錄
4. 再做 bootstrap registration，之後回到正常 lifecycle 流程
5. 若 evidence 不足，才視為 orphaned candidate 或 inconclusive governance event
6. 不可在沒有 registry entry 的情況下直接接手 reuse

## Transition Bootstrap

bootstrap registration 適用於：

- project-instance 已有可辨識 current state
- registry 尚未建立對應 entry
- 現在的目標是把「既有現況」納入治理，而不是直接當成未知垃圾清掉
- current state 能被唯一綁定到某個 canonical project-instance / stage，而不是多個模糊候選

bootstrap registration 不適用於：

- 只有零散 process，但無法辨識 project-instance / stage
- evidence 不足以安全判斷 ownership
- 其實沒有現況，只是需要 request 新 env

## 回報格式建議

完成 reconcile 後，回報至少包含：

- target instance / stage
- derived `status.phase`
- observed evidence（running / exited / missing）
- authority evidence（registry entry / ownership / TTL）
- candidate instances（若 exact match 不存在）
- 建議下一步（bootstrap register / reuse / request new / release / gc / wait for approval / developer selection）

讓後續 agent 或 human 可以延續治理流程，而不是重新猜一次。
