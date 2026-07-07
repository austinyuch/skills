# Concurrent-Governance Reconciliation

當多條 spec lane（branch / worktree）**同時**存在時，共用治理檔（`ISSUE_LOG.md` / `SPECS.md` / `NEXT_STEPS.md` / `RTM.md`）會各自被不同 lane 編輯，造成三種痛點：ID 碰撞（兩條 lane 都拿 `ISS-2026-007`）、table 版本分歧（某 branch 的 ISSUE_LOG 落後好幾列）、以及 merge 時的衝突債。本文件定義如何在**保留 per-lane 隔離**的前提下，讓這些檔案可安全並行。

## 1. 檔案分類（決定 merge 策略）

| 檔案 | 性質 | Merge 策略 |
|---|---|---|
| `ISSUE_LOG.md` | **append-only** issue rows | `merge=union`（`.gitattributes`）→ 兩側新增列自動合併，不衝突 |
| `RTM.md` | **append-mostly** requirement rows | `merge=union` |
| `SPECS.md` | per-spec **sections**，多為 append，但會 in-place 改狀態 | **手動 merge-time 重整**（不 union） |
| `NEXT_STEPS.md` | **rolling memo**，整段改寫 | **手動**（union 會製造矛盾；以最新 lane 事實為準） |

`merge=union` 對 append-only log 是淨賺；唯一副作用：若兩條 lane **改到同一列**（例如同一 issue 的 disposition），union 會保留兩份 → 事後手動 dedupe。對 append-mostly 檔可接受。

## 2. ID 配置（避免碰撞）

開新 issue row 前，用 helper 取「跨所有 branch」的下一個可用 ID，而不是只看本 branch 的檔案（本 branch 可能落後）：

```bash
bash skills/spec-master/scripts/next-issue-id.sh    # 掃 git 所有 ref 的 ISS-YYYY-NNN，印下一個
```

它掃 `git log --all` + 各 branch 的 `ISSUE_LOG.md`，回報目前最大 ID 與建議的下一個。這樣即使你的 branch 是舊 base，也不會撞到別條 lane 已用的 ID。

## 3. 標準流程（每條 lane）

1. **隔離**：每條 active spec lane 用**獨立 worktree / branch**（code + governance 都在自己的 tree 改，不動別人的）。
2. **開 issue / RTM row**：先跑 `next-issue-id.sh` 取非碰撞 ID，append 到本 branch 的 `ISSUE_LOG.md` / `RTM.md`。
3. **若本 branch base 落後**（缺其他 lane 的列）：在該檔頂端留一行 **merge-reconciliation note**（說明本 branch base + 缺哪些 ID 範圍在別條 lane），提醒 merge 時重整。
4. **SPECS / NEXT_STEPS**：只寫自己 lane 的 section / 只更新 rolling memo 指向自己 lane；不假裝覆蓋別條 lane 的 registry section。
5. **Merge 到 main**：`ISSUE_LOG` / `RTM` 由 union 自動合併（事後掃一次 duplicate ID / duplicate row）；`SPECS` / `NEXT_STEPS` 手動重整為單一 coherent 版本（append-only：不 renumber、不刪別條 lane 的 section）。

## 4. 反模式

- 只看本 branch 的 `ISSUE_LOG` 就配 ID → 撞號（本 branch 可能落後）。改用 `next-issue-id.sh`。
- 在別條 active lane 的 working tree 直接改治理檔 → concurrent-lane 破壞。改在自己的 worktree。
- 對 `NEXT_STEPS.md` / `SPECS.md` 開 union merge → 產生矛盾 / 重複 section。只 union append-only 檔。
- merge 後不掃 duplicate → union 可能留下同列兩份；merge 後要 dedupe pass。

## 5. Why

💡 **原因**：worktree 解決了 **code** 的並行隔離，但治理檔仍是所有 lane 的單一共用 surface，沒有並行策略。用「append-only 檔走 git union-merge + 跨 branch ID 配置 + 結構化檔手動 merge-time 重整」三招，就能在不放棄 per-lane 隔離、也不引入中央序列化瓶頸的前提下，讓 5+ 條 lane 並行編輯治理檔而不互撞。這直接消除本 session 反覆出現的 ID 碰撞與 table 分歧。
