# Integration Boundaries

這個 skill 最重要的工作之一，是避免把 **不同層級的 registry / memo / governance artifact** 混在一起。

術語提醒：

- `local infra registry` = machine-local runtime authority
- `global registry path` = machine-scoped、workspace 之外的檔案位置
- `workspace-scoped AGENTS.md` = 只屬於單一 workspace 的穩定 guidance

## 四者的責任分界

| Artifact | 角色 | 該放什麼 | 不該放什麼 |
|---|---|---|---|
| local infra registry (`~/.config/opencode/local-infra/registry.json`) | live runtime allocation authority | ports、networks、compose stacks、TTL、env ownership | feature requirements、contract governance、CR inventory |
| workspace-scoped `AGENTS.md` / designated workspace guide | stable runtime policy & naming memory | canonical project naming、aliases、service bundle policy、tool path hints | active instance IDs、TTL snapshots、ports、container health tables |
| `SPECS.md` | feature / contract governance registry | spec status、Depends On、Impacts、Open CR summaries、external provenance | live port allocation、current running containers、podman observed state |
| `NEXT_STEPS.md` | rolling operational memo | active spec、next action、blockers、resume hints | live infra inventory、resource locks、container health tables |

## 對 workspace `AGENTS.md` 的要求

- 只能保存 **workspace-scoped** 的 stable canonical naming / alias / required service bundle policy
- 不得把 global `~/.config/opencode/AGENTS.md` 當成 project-instance canonical mapping 的存放處
- 不得把某次 session 選到的 active instance ID、TTL、ports、container health、或 lock inventory 寫進 `AGENTS.md`

## 對 `spec-driven-development` 的要求

- design 階段若知道未來需要 local infra，應描述 **需求與治理方式**，不是直接手配 port
- tasks 階段應安排 registry query / reconcile / governed release 的工作
- implementation 階段不得直接繞過 registry 啟動 local stacks
- review 階段應檢查是否有 bypass 行為

## 對 `spec-registry-manager` 的要求

- 不得把 local infra registry 視為 `SPECS.md` 的來源之一
- 不得把 runtime allocation state 寫進 feature registry
- 可以在 spec 或 CR 中記錄高層 infra 假設，但不可維護 live inventory

## 對 `devops-container-orchestration` 的要求

- 它負責 compose / Podman / multi-instance pattern
- 但 allocation authority 必須來自 local infra registry
- 換句話說：**先決定能不能用，再決定怎麼用**

## 常見錯誤示例

### 錯誤 1：在 `SPECS.md` 記錄目前使用中的 port

這會把穩定治理文件變成高衝突的 runtime dashboard。

### 錯誤 2：在 `NEXT_STEPS.md` 保留整份 env allocation 表

`NEXT_STEPS.md` 應只記「下一步要做什麼」，不是 live registry dump。

❌ 不該這樣寫：

```markdown
- Ports: 49152, 49153
- Containers: backend=running, frontend=exited
- Lock owner: project-a-e2e-003
```

✅ 應改成這樣：

```markdown
- Local infra blocker: existing e2e env needs registry reconcile before reuse
- Resume hint: verify ownership / TTL through registry-governed tool, then decide reuse or release
```

### 錯誤 2.5：在 `SPECS.md` 保留 live allocation 摘要

❌ 不該這樣寫：

```markdown
- Backend currently uses localhost:49152
- Frontend currently uses localhost:49153
```

✅ 應改成這樣：

```markdown
- This feature requires local dev/UAT/E2E infra governed by the local infra registry.
- Runtime allocation details are intentionally excluded from `SPECS.md`.
```

### 錯誤 2.75：在 global `AGENTS.md` 或 workspace `AGENTS.md` 保留 live instance 選擇結果

❌ 不該這樣寫：

```markdown
- Use project-a-uat-003 next time
- Ports: 49152, 49153
- Current chosen instance is still alive
```

✅ 應改成這樣：

```markdown
- Canonical project: project-a
- Alias: proj-a -> project-a
- UAT requires service bundle: [frontend, backend]
- For ambiguous instance selection, use registry status + HITL selection
```

### 錯誤 3：在 workflow skill 內重新定義一套 port pool 規則

workflow skill 應尊重 authoritative registry，而不是各自發展 allocation 邏輯。
