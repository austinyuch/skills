---
name: container-image-janitor
description: 盤點與清理 Docker / Podman images 的 global skill。當使用者想列出 docker images 或 podman images、只保留每個 repository 最新 N 個 images、找出 `<none>` / dangling images、輸出可編輯的 UTF-8-SIG CSV 審核清單，或依使用者已編輯的 CSV 執行 image removal 時使用。特別適合需要「先產生核准清單、再安全刪除」的 container image cleanup workflow。
---

# Container Image Janitor

## Overview

用這個 skill 處理 Docker / Podman image 清理的兩階段流程：先盤點並輸出可編輯 CSV，再依 CSV 做 dry-run 或實際刪除。

優先使用 bundled Python script，避免臨時 shell one-liner 造成誤刪。這個 skill 的預設行為是保守的：先產生清單，不直接刪除。

## Workflow

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
   - 哪些 rows 在 inventory 階段就被標示為 `blocked-by-container` 或 `blocked-by-child-image`
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

## Safety rules

- 不要在未經使用者明確同意前執行 `--execute`。
- 預設保留 script 的互動確認；`--yes` 只用在已經完成對話內最終確認的情況。
- 不要直接用 tag 刪除；優先使用 CSV 內的 full image ID。
- 如果使用者只是要盤點或預覽，停在 inventory / dry-run。
- 如果 docker / podman 其中一個 runtime 不存在，照 script 的偵測結果回報，不要假裝兩者都有掃描。
- 若 script 回報 multi-repository image 被略過，先把這件事告訴使用者，不要自行放寬規則。
- 如果 apply 階段把某些 approved rows 標成 blocked，先要求重新 inventory 或重新審核 CSV，不要強行刪除。
- inventory 產生的 `dependency_risk` / `recommended_action` 是 review 輔助欄位；如果它們已經顯示有依賴，預設不要鼓勵使用者直接批准刪除。

## Bundled resources

- `scripts/manage_images.py`: inventory / CSV export / CSV-driven cleanup 的主程式
- `references/csv-schema.md`: CSV 欄位說明與編輯規則
