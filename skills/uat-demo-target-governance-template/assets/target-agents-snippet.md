## UAT Demo Workflow

- 使用 `spec-master` 做 routing / truth-surface selection。
- 使用 `spec-driven-development` 做 spec authoring 與 phase execution。
- 使用 `uat-demo-agent` 做 execution / evidence flow。
- 若需要 governed bootstrap，轉交 `local-infra-registry-governance`。
- 只把這個 target repo 的 instantiated target-repo state 保留在本 repo。
