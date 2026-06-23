---
name: uat-demo-target-governance-template
description: 當使用者要把 `uat-demo` 與 SDD/spec 治理流程一般化到 target repo、需要 reusable governance templates、釐清 `spec-master` 與 `spec-driven-development` 邊界、或規範 bootstrap / UAT-to-demo handoff 時使用。這個 skill 提供 repo-owned 的 reusable guidance 與 templates，不取代 `spec-master`、`spec-driven-development`、`uat-demo-agent`、或 `local-infra-registry-governance`。
---

# UAT Demo Target Governance Template

這是一個 reusable governance/template skill，不是新的 execution engine，也不是新的 spec authoring workflow。

這類 reusable routing / governance logic 屬於 global skill layer，應維持在 machine-scoped global skill roots，例如：

1. `~/.codex/skills/`
2. `~/.config/opencode/skills/`

target repo 只應持有 instantiated target-repo state，不應複製完整 cross-skill routing policy。

## 角色定位

使用這個 skill 來：

1. 套用 target repo 的 governance/bootstrap templates
2. 說清楚 routing / authority 仍由既有 global skills 持有
3. 產生 target repo 只需填入 instantiated target-repo state 的範本

不要用這個 skill 來：

1. 重寫 `spec-master` 的 routing / triage authority
2. 重寫 `spec-driven-development` 的 phase-authoring authority
3. 重寫 `uat-demo-agent` 的 execution/evidence authority
4. 自行執行 live runtime allocation 或 service control

## Authority Map

- `spec-master`: routing / triage authority
- `spec-driven-development`: phase-authoring authority
- `spec-registry-manager`: registry authority
- `uat-demo-agent`: execution / evidence authority
- `local-infra-registry-governance`: runtime allocation authority
- `webapp-testing`: browser validation authority
- `user-manual-skill`: manual / demo-support authority
- `verification-loop`: final verification authority

## Workflow

這個 skill 使用 Pipeline + Generator pattern。

1. 先讀 [references/routing-boundary.md](./references/routing-boundary.md)。
2. 若需求涉及 bootstrap，讀 [references/bootstrap-governance.md](./references/bootstrap-governance.md)。
3. 若需求涉及 target repo 要保留哪些治理檔，讀 [references/target-governance-artifacts.md](./references/target-governance-artifacts.md)。
4. 若需求涉及從 UAT iteration 切到 demo preparation，讀 [references/uat-to-demo-transition.md](./references/uat-to-demo-transition.md)。
5. 只有在需要產生 target repo 片段時，才讀取 `assets/` 下的模板。

## Generator Assets

- `assets/target-agents-snippet.md`
- `assets/target-next-steps-template.md`
- `assets/target-bootstrap-template.md`

## Guardrails

1. 保持 target repo 只持有 instantiated target-repo state。
2. `uat-demo-agent` 只負責 execution/evidence surface；不要把 post-UAT remediation 說成它的責任。
3. 任何 live bootstrap / reconcile / reuse / release 判斷，一律交給 `local-infra-registry-governance`。
4. 若需要真正開 spec 或續做 spec phase，交回 `spec-driven-development`。
5. target repo 只保留 repo-local inputs；完整 routing logic 應維持在 `~/.codex/skills/` 與 `~/.config/opencode/skills/` 的 relevant global skills。
