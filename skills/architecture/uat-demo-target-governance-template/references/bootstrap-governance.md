# Bootstrap Governance

這份 reference 只定義 reusable bootstrap semantics，不定義任何 target repo 的具體 service commands。

## Boundary

- `local-infra-registry-governance` 是 runtime allocation authority。
- companion template skill 只提供 start / stop / restart / reconcile 的治理語意與模板。
- target repo 自己填入具體 service bundle、commands、health checks、與例外條件。

## Reusable semantics

1. `start`: 請求或重用 target stage 所需的 governed service bundle。
2. `stop`: 釋放或停止當前 owner 明確持有的 service bundle。
3. `restart`: 對同一 service bundle 進行 stop + start 或 reconcile。
4. `reconcile`: 在 existing runtime state 與 target repo 預期之間做 governed 對齊。

## Handoff rule

以下情況必須直接導向 `local-infra-registry-governance`，不要在 companion skill 內自行處理：

1. 需要 live runtime allocation
2. 需要 bundle ownership / reuse / release 判斷
3. 需要治理多服務 required bundle readiness
4. 需要在 UAT/E2E/demo 前確認真實 runtime state

## Template posture

1. companion skill 可以提供 `<service-bundle-name>`、`<target-start-command>`、`<target-stop-command>` 類型的 placeholders。
2. companion skill 不應硬編 `docker compose up`、`podman compose up` 或任何特定 target repo service 名稱。
