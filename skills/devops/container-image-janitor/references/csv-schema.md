# CSV schema

`manage_images.py inventory` 會輸出 UTF-8-SIG CSV，欄位如下：

| Column | Meaning |
|---|---|
| `approved` | 由使用者編輯。只有 `yes` / `y` / `true` / `1` 會被視為核准刪除。 |
| `runtime` | `docker` 或 `podman`。 |
| `repository` | image repository 名稱；`<none>` 代表 dangling / untagged image。 |
| `image_id` | full image ID。實際刪除時用這個欄位。 |
| `tags` | 此 image 目前關聯的 tags，使用 `;` 串接。 |
| `created_at` | 原始建立時間字串。 |
| `created_epoch` | 便於排序的 Unix epoch seconds。 |
| `size_bytes` | image size，單位 bytes。 |
| `reason` | 建議刪除原因，例如 `older-than-keep-limit` 或 `dangling-none`。 |
| `group_key` | 保留策略使用的群組鍵，通常是 repository 名稱。 |
| `group_rank` | 在該 repository 內依新到舊排序的名次。 |
| `keep_limit` | 這次 inventory 套用的保留數量。預設為 3。 |
| `repository_count` | 這個 image 目前關聯到幾個 repositories。 |
| `tag_count` | 這個 image 目前關聯到幾個非 `<none>` tags。 |
| `group_size` | 此 repository 群組在 inventory 時共有幾個 images。 |
| `retained_newer_count` | 在此 candidate 前面、會被保留的較新 image 數量。 |
| `container_count` | 目前偵測到有幾個 containers 仍使用這個 image。 |
| `container_refs` | 使用中的 containers 摘要，格式為 `state:name:short-id`，以 `;` 串接。 |
| `child_image_count` | 目前偵測到有幾個 child images 依賴這個 image。 |
| `child_image_ids` | child image IDs，以 `;` 串接。 |
| `dependency_risk` | inventory 階段的 dependency 風險判斷，例如 `clear`、`in-use`、`has-child-images`。 |
| `recommended_action` | inventory 階段建議，例如 `safe-to-delete`、`blocked-by-container`、`blocked-by-child-image`。 |
| `delete_command` | 對應的刪除命令預覽。 |
| `notes` | 額外說明。 |

## Editing rule

最常見的編輯方式只有一個：修改 `approved` 欄位。

- 要刪除：填 `yes`
- 不刪除：留白或填任何非 truthy 值

其他欄位原則上不需要改。

## Immutable fields in normal use

在正常流程中，`runtime`、`repository`、`image_id`、`reason`、`group_key`、`group_rank`、`keep_limit`、`delete_command` 都應視為 inventory 產生的唯讀欄位。

同樣地，`repository_count`、`tag_count`、`group_size`、`retained_newer_count`、`container_count`、`container_refs`、`child_image_count`、`child_image_ids`、`dependency_risk`、`recommended_action` 也屬於 inventory 階段產生的唯讀 context 欄位。

`apply` 階段會重新驗證目前 runtime 狀態。若這些欄位被手動改壞、或 CSV 已經 stale，script 可能會：

- 拒絕該 row
- 將該 row 標成 blocked
- 要求重新 inventory 後再審核

因此，除非你正在做非常明確的人工修正，否則只改 `approved` 就好。

## How to read the new dependency columns

- `dependency_risk=clear` + `recommended_action=safe-to-delete`
  - 代表 inventory 當下沒有發現 container 或 child-image 依賴，通常是最直接的清理候選。
- `dependency_risk=in-use`
  - 代表至少一個 container 還在使用這個 image。
- `dependency_risk=has-child-images`
  - 代表至少一個 child image 依賴它。
- `dependency_risk=in-use-and-has-children`
  - 代表同時存在 container 與 child-image 依賴，通常不應直接刪除。
