# FMEA Review Checklist

這份 checklist 用來做 **Reviewer pattern** 的最後自檢。它不是額外 workflow，而是避免 skill 在高風險 local infra 場景下失真。

| Failure Mode | Effect | Detection Signal | Mitigation | Reviewer Check | S | O | D | RPN |
|---|---|---|---|---|---:|---:|---:|---:|
| 跳過 registry query / lock / reconcile | 直接產生 port / network / stack 衝突 | 回答裡直接出現 compose / podman 動作，但沒有 authority evidence | 停止動作，先補 registry-governed flow | 是否先說明 query / lock / reconcile 結果？ | 10 | 5 | 3 | 150 |
| 把 `podman ps` 當 source of truth | ownership / TTL / reuse 決策錯誤 | 只引用 observed state，沒有 registry state | 回到 reconcile，將 observed 當 evidence 而非 authority | 是否同時交代 authoritative 與 observed state？ | 9 | 5 | 4 | 180 |
| evidence 不足仍硬判 lifecycle | 誤 reuse、誤 release、或誤 gc | 狀態推論缺少 TTL / ownership / observed evidence 任一項 | 回報 evidence gap，不做 destructive action | 是否明確標記 inconclusive 狀態？ | 9 | 4 | 5 | 180 |
| 把 live state 寫進 `SPECS.md` / `NEXT_STEPS.md` | 污染治理文件，造成高衝突 runtime dump | 回答包含 port table、container health table、resource lock inventory | 改寫成高層 blocker / resume hint / governance 結論 | 是否把 live inventory 保留在 local infra registry？ | 8 | 6 | 4 | 192 |
| 導入初期把「沒 registry entry」直接當永久 blocker | 無法平滑接管既有 current state，遷移期卡死 | 回答只看到 missing entry 就停止，沒有評估 bootstrap register | 先判斷 current state 是否可辨識，再 bootstrap-register 後進入正常 lifecycle | 是否先評估 bootstrap registration，而不是直接卡住？ | 8 | 5 | 5 | 200 |
| ambiguous instance 沒有 exact match 卻直接猜測 reuse | 誤接手錯誤 env，造成 cross-instance side effect | 名稱相似但沒有 resolver / HITL evidence | exact match → deterministic resolve → HITL，禁止 agent 自行猜測 | 是否只在 exact/resolved/HITL 選定後才 reuse？ | 10 | 4 | 5 | 200 |
| 多服務 bundle 只憑單一 service / port 就判定 ready | 將部分可用的 env 誤當成整體可用 | frontend 起來了，但 backend/db 未 ready | 以 `required_services[]` bundle readiness 作為成功條件 | 是否確認整個 bundle，而不是單點存活？ | 9 | 5 | 5 | 225 |
| tool 缺失時直接繞過治理 | 破壞 registry-first 原則 | 回答出現「先用 podman / compose 頂著用」 | 依 discovery 順序找工具，找不到就 block | 是否有 blocker 回報而不是 workaround？ | 10 | 4 | 4 | 160 |
| 人工或外部流程造成無 entry current state 被直接 reuse | 接手未知環境，造成不可預期 side effect | observed state 存在，但 registry 沒有對應 entry | 先判斷是否可 bootstrap-register；若不行，再標記為 orphaned / inconclusive 並收斂 | 是否先評估 bootstrap registration，而不是直接接手或直接丟棄？ | 8 | 4 | 6 | 192 |

## 使用方式

完成回答前，快速問自己：

1. 我是否能指出 authoritative registry state？
2. 我是否能指出 observed evidence？
3. 我是否在證據不足時停止而不是猜？
4. 我是否把 runtime state 留在 local infra registry，而不是 feature governance 文件？

若任一題答案是否定，先修正回答，再輸出給使用者。
