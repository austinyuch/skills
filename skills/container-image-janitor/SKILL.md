---
name: container-image-janitor
description: 盤點與清理 Docker / Podman images 與本機 container runtime 空間的 global skill。當使用者想列出 docker/podman images、只保留每個 repository 最新 N 個 images、找出 untagged / dangling images、輸出可編輯的 UTF-8-SIG CSV 審核清單、依 CSV 安全刪除 image、盤點 Docker/KIND/Podman 空間、清理 Docker BuildKit build cache、清理 Docker unused volumes，或評估 KIND cluster 是否可釋放空間時使用。特別適合需要先 inventory/dry-run/確認、再保守清理的 container image 與 disk cleanup workflow。
---

# Container Image Janitor

## Overview

用這個 skill 處理兩類工作：

1. Docker / Podman image 清理：先盤點並輸出可編輯 CSV，再依 CSV dry-run 或實際刪除。
2. Container runtime 空間清理：盤點 Docker/KIND/Podman 空間，並在使用者明確要求時清理 Docker build cache 或 unused volumes。

優先使用 bundled Python script 處理 image inventory / CSV-driven cleanup，避免臨時 shell one-liner 造成誤刪。這個 skill 的預設行為是保守的：先產生清單或盤點，不直接刪除。

## Image Cleanup Workflow

### 1. Inventory / export CSV

當使用者要盤點 images、保留最新 3 個、或列出 `<none>` images 時：

1. 若使用者沒有指定輸出路徑，先選一個明確路徑，優先使用目前工作區的 `temp/`。
2. 執行：

```bash
python ~/.config/opencode/skills/container-image-janitor/scripts/manage_images.py inventory --runtime all --keep-latest 3 --output <csv-path>
```

3. 回報：
   - 掃描了哪些 runtime
   - 產生了哪個 CSV
   - 匯出了多少建議刪除 rows
   - 是否有 multi-repository images 被保守略過
   - 哪些 rows 在 inventory 階段被標示為 `blocked-by-container` 或 `blocked-by-child-image`
4. 告訴使用者去編輯 CSV 的 `approved` 欄位。只有 `approved=yes` 的 rows 之後才會被刪除。

### 2. Explain CSV columns when needed

若使用者問 CSV 欄位代表什麼，讀取 `references/csv-schema.md`。

### 3. Preview deletions from edited CSV

當使用者說他已經編輯好 CSV、想先看會刪掉什麼時：

```bash
python ~/.config/opencode/skills/container-image-janitor/scripts/manage_images.py apply --csv <csv-path>
```

這是 dry-run。它只會列出 `approved=yes` 的 rows，以及對應的 `docker image rm ...` / `podman rmi ...` 計畫，不會真的刪除。

### 4. Execute deletions only on explicit request

只有當使用者明確要求真的刪除時，才執行：

```bash
python ~/.config/opencode/skills/container-image-janitor/scripts/manage_images.py apply --csv <csv-path> --execute
```

執行前仍要在對話中清楚說明：

- 將刪除幾個 images
- 哪些 runtime 會受影響
- 只會刪除 `approved=yes` 的 rows
- 這次執行是否有 stale / blocked rows 需要先重新 inventory

只有在你已經把完整 dry-run 計畫展示給使用者、也收到明確最終確認時，才可額外加上 `--yes` 略過 script 內的互動確認。

### 5. Podman external-container follow-up

Podman image removal 可能被 normal `podman ps` 看不到的 external / `Storage` containers 擋住。當 Podman `rmi` 回報 image in use，或 inventory 結果與刪除結果不一致時：

```bash
podman ps -a --external --format '{{.ID}} {{.Image}} {{.Names}} {{.Status}}'
```

不要 force-remove image。先回報 blockers；如果刪掉 child layers 後有 parent layers 新變成 eligible，可以重新 inventory，重新建立 approved-only CSV，再 dry-run/execute。多輪清理仍必須遵守 dry-run 與確認流程。

## Runtime Space Cleanup Workflow

### 1. Audit first

當使用者問 Docker/KIND/Podman 是否還能釋放空間，先盤點，不直接清理：

```bash
docker system df -v
podman system df
kind get clusters
```

若 KIND 可能相關，再查：

```bash
docker ps -a --filter label=io.x-k8s.kind.cluster --format '{{.ID}} {{.Names}} {{.Image}} {{.Status}} {{.Label "io.x-k8s.kind.cluster"}}'
docker inspect <kind-node-container> --format '{{range .Mounts}}{{.Type}} {{.Name}} {{.Source}} {{.Destination}}{{println}}{{end}}'
kubectl get pods -A
kubectl get pvc -A
```

回報時把可回收來源分開：images、build cache、unused volumes、KIND node volumes、KIND node image、Podman images/volumes。不要把它們混成同一個刪除建議。

### 2. Docker build cache cleanup

只有當使用者明確要求清理 Docker build cache 時，執行：

```bash
docker builder prune --all --force
```

執行前說明這只清 unused BuildKit cache，不會刪 running containers、volumes 或 images。完成後用 `docker system df` 驗證 `Build Cache` 是否降到 `0B` 或剩餘多少。

### 3. Docker unused volume cleanup

只有當使用者明確要求清理 Docker unused volumes 時，執行：

```bash
docker volume prune --all --force
```

執行前必須明確警告：這會刪除所有目前沒有被任何 container 掛載的 Docker named/anonymous volumes；其中可能包含舊專案資料，不只是 cache。不要用這個命令清理仍被 running 或 stopped containers 掛載的 volumes。完成後用 `docker system df` 驗證 `Local Volumes` reclaimable 是否降到 `0B` 或剩餘多少。

### 4. KIND cleanup decision

KIND 的 node image 可能顯示成 `<none>` tag，但如果有 `RepoDigests` 且正被 `kindest/node` containers 使用，就不是普通 dangling image。不要單獨刪除 running KIND node 的 anonymous `/var` volumes。

若使用者要釋放 KIND 空間，先確認：

- cluster name
- 是否有非系統 workloads
- 是否有 PVC
- node containers 與 `/var` volumes 大小
- `kindest/node` image 是否只被該 cluster 使用

只有使用者明確同意刪 cluster 時，才執行：

```bash
kind delete cluster --name <cluster-name>
```

cluster 刪除後，若 `kindest/node` image 不再被使用，才可考慮：

```bash
docker image rm <kindest-node-image-id-or-digest>
```

## Safety Rules

- 不要在未經使用者明確同意前執行 `--execute`、`docker builder prune`、`docker volume prune`、`kind delete cluster` 或任何 force removal。
- 預設保留 script 的互動確認；`--yes` 只用在已經完成對話內最終確認的情況。
- 不要直接用 tag 刪除 image；CSV-driven image cleanup 優先使用 full image ID。
- 如果使用者只是要盤點或預覽，停在 inventory / dry-run / audit。
- 如果 docker / podman / kind 其中一個 runtime 不存在，照偵測結果回報，不要假裝都有掃描。
- 若 script 回報 multi-repository image 被略過，先把這件事告訴使用者，不要自行放寬規則。
- 如果 apply 階段把某些 approved rows 標成 blocked，先要求重新 inventory 或重新審核 CSV，不要強行刪除。
- inventory 產生的 `dependency_risk` / `recommended_action` 是 review 輔助欄位；如果它們已經顯示有依賴，預設不要鼓勵使用者直接批准刪除。
- Docker `volume prune --all` 是資料刪除，不是單純 cache cleanup；執行前要清楚告知風險，執行後回報被刪 volume 數量或 Docker 回報的 reclaimed space。
- Podman external / `Storage` containers 可能讓 image 看似 dangling 但實際 in-use；遇到這種情況不要 force-remove，改列 blocker。
- KIND node volumes 由 cluster lifecycle 管理；除非刪 cluster，否則不要手動移除。

## Bundled resources

- `scripts/manage_images.py`: inventory / CSV export / CSV-driven cleanup 的主程式
- `references/csv-schema.md`: CSV 欄位說明與編輯規則
