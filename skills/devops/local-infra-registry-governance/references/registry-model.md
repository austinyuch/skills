# Registry Model

## 目的

local infra registry 是 **authoritative state**，負責記錄誰在什麼 stage 佔用了哪些 local infra resources。

它要回答的是 inventory / ownership / lifecycle 問題，而不是 feature planning 問題。

## Terminology

- **local infra**：指 machine-local runtime infrastructure（Podman、localhost ports、networks、compose stacks）
- **global registry path**：指 machine-scoped path outside the workspace，不是多機共享 registry
- **workspace guidance**：指 workspace-scoped `AGENTS.md` 或 designated workspace file，用來保存 stable naming / alias / bundle policy

## Global Physical Layout

預設 machine-local 根目錄：

```text
~/.config/opencode/local-infra/
```

最小但完整的實體結構：

```text
~/.config/opencode/local-infra/
├── registry.json              # Single Source of Truth
├── registry.lock              # Global lock
├── observed/
│   ├── podman.ps.json
│   └── podman.networks.json
├── instances/
│   └── <project-instance>/
│       ├── instance.json
│       └── last_reconcile.txt
├── locks/
│   ├── ports.lock
│   └── networks.lock
├── gc/
│   └── candidates.json
└── logs/
    └── reconcile.log
```

重點：

- `registry.json` 才是權威
- `observed/*` 只是 reconcile 輔助快取
- `instances/*` 是 inspection/debug 友善的 per-instance 補充
- 整個 `local-infra/` 都是 machine-local runtime state，應被 git 忽略

## 資料維度

## 分層模型

這個治理系統至少要區分兩層：

1. **Project metadata**：stable canonical identity、workspace aliases、declared stages、required service bundles、designated guidance file
2. **Project-instance lifecycle**：某個具體 runtime env instance 的 owner、TTL、resources、`status.phase`

### Project metadata

- `canonical_project`
- `aliases[]`（只允許 deterministic alias，不允許 agent 臨場猜測）
- `declared_stages[]`
- `helper_script`（optional, 該 project 的 governed local infra helper 腳本絕對路徑）
- `service_bundles{}`（per-stage 或 per-profile 的 bundle 定義，見下方 schema）
- `workspace_guidance_path`（例如 workspace-scoped `AGENTS.md` 或指定 resolver file）

#### `helper_script`

指向該 project 的 governed local infra 腳本（例如 `scripts/local_infra.py`）。
所有 lifecycle 動作（deploy / start / stop / status / release）都應透過此腳本執行，而非直接 `podman compose`。

#### `service_bundles{}` schema

`service_bundles` 是一個 map，key 為 profile name（如 `uat`、`e2e-basic`、`e2e-gac`），value 為該 profile 的完整 bundle 定義。

每個 bundle 至少應包含：

```json
{
  "compose_entrypoint": "docker-compose.yml",
  "additional_compose_files": ["docker-compose.e2e.gac.yml"],
  "conditional_compose_files": [
    {
      "file": "docker-compose.uat.dns.yml",
      "condition": "UAT_PODMAN_DNS nonempty"
    }
  ],
  "environment_files": [".env", ".env.compose"],
  "preferred_command": "python3 scripts/local_infra.py run-uat deploy",
  "status_command": "python3 scripts/local_infra.py run-uat status",
  "release_command": "python3 scripts/local_infra.py release --stage uat",
  "public_ports": [3040, 3041],
  "required_services": ["caddy", "api", "frontend", "db", "valkey", "minio"],
  "required_readiness_checks": [
    "https://localhost:3041/health returns 200",
    "https://localhost:3041/ reachable"
  ],
  "surface_service": "caddy",
  "surface_health_url": "https://localhost:3041/health",
  "callback_url": "https://localhost:3041/oauth2/callback",
  "startup_strategy": "rootless-podman-compose",
  "notes": ["..."]
}
```

欄位說明：

| 欄位 | 必要 | 說明 |
|------|------|------|
| `compose_entrypoint` | ✅ | 主要 compose file |
| `additional_compose_files` | ❌ | 固定疊加的 compose override files |
| `conditional_compose_files` | ❌ | 依環境變數條件疊加的 compose files |
| `environment_files` | ✅ | 該 profile 需要的 env 檔案 |
| `preferred_command` | ✅ | governed 啟動命令 |
| `status_command` | ✅ | governed 狀態查詢命令 |
| `release_command` | ✅ | governed 釋放命令 |
| `public_ports` | ✅ | 對外暴露的 host ports |
| `required_services` | ✅ | bundle readiness 所需的全部 services |
| `required_readiness_checks` | ✅ | 人類可讀的 readiness 條件 |
| `surface_service` | ✅ | 使用者面向的主要 service |
| `surface_health_url` | ✅ | 主要 health check URL |
| `callback_url` | ❌ | OAuth2 callback（若適用） |
| `startup_strategy` | ✅ | 啟動策略（如 `rootless-podman-compose`、`playwright-webserver`） |
| `notes` | ❌ | 補充說明 |

#### `service_bundles` 與 workspace `runtime-profiles.json` 的關係

- workspace 的 `infra/runtime-profiles.json` 是 **workspace-scoped authoritative source**，定義 profile 的 compose files、env assertions、readiness 條件
- machine registry 的 `service_bundles` 是 **machine-scoped operational mirror**，供 registry governance 做 lifecycle 決策時使用
- 兩者應保持一致；若有衝突，以 workspace `runtime-profiles.json` 為準，並更新 registry

### Project-instance lifecycle

每個 project-instance 至少應能描述：

- `project`
- `instance`
- `stage` (`dev`, `uat`, `e2e` ...)
- `owner`（agent / human）
- `registration_mode`（`bootstrap` | `requested`）
- `created_at`
- `last_used_at`
- `last_observed_at`（optional, 供 reconcile 記錄最近一次觀測時間）
- `last_reconciled_at`（optional, 供治理流程判斷狀態是否過舊）
- `ttl`
- `resources.ports[]`
- `resources.networks[]`
- `resources.compose.stack`
- `resources.compose.services[]`
- `status.phase`
- `registration_source`（optional, 例如 `podman_ps+network_inspect`）
- `required_services[]`（此 instance 要被視為 ready / reusable 時，必須全部健康的 service bundle）

### `registry.json` top-level shape

除了 project / instance 資料之外，至少還應包含：

- `version`
- `last_reconciled_at`
- `projects`

## 最小 schema 範例

```json
{
  "version": "v1",
  "last_reconciled_at": "2026-04-13T10:10:00+08:00",
  "projects": {
    "project-a": {
      "instances": {
        "project-a-e2e-003": {
          "project": "project-a",
          "instance": "project-a-e2e-003",
          "stage": "e2e",
          "owner": "agent:opencode",
          "registration_mode": "bootstrap",
          "ttl_seconds": 7200,
          "registration_source": "podman_ps+network_inspect",
          "required_services": ["frontend", "backend"],
          "resources": {
            "ports": [49152, 49153],
            "networks": ["project-a-e2e-net"],
            "compose": {
              "stack": "project-a-e2e-003",
              "services": ["frontend", "backend"]
            }
          },
          "status": {
            "phase": "active"
          }
        }
      }
    }
  }
}
```

### `instances/<project-instance>/instance.json`

這是 per-instance 補充，不取代 `registry.json`：

```json
{
  "env_id": "project-a-e2e-003",
  "project": "project-a",
  "stage": "e2e",
  "compose_file": "compose.rendered.yaml",
  "last_reconcile_result": "active"
}
```

## Authoritative vs Observed

### Authoritative state

- 誰宣告鎖定了 resource
- TTL 與生命周期責任
- 哪個 project-instance 應該存在
- 這個 entry 是 bootstrap 登錄還是 request 建立
- stable canonical project identity 與 aliases 是什麼
- 某個 stage 需要哪一組 `required_services[]`

### Observed state

- `podman ps`
- `podman network ls`
- service 是否正在跑
- container 是否 exited / missing

Observed state 用來 **reconcile**，不是用來直接覆蓋 authority，也不能單靠單一 service / 單一 port 判定整個 bundle 已 ready。

## Lock 模型

- **global registry lock**：保證 registry read/write 的一致性
- **resource locks**：避免同時 allocate 同一組 ports / networks

若實作需要追蹤 lock provenance，可加上：

- `lock_owner`
- `lock_acquired_at`

最重要的是順序：

1. query authoritative state
2. 若 target entry 不存在，先判斷是否應 bootstrap register current state
3. acquire lock
4. reconcile observed state
5. allocate / bootstrap-register / reuse / release / gc
6. update authoritative state

## Update Lifecycle (Write Path)

任何會改變 registry state 的動作，都應遵守以下更新方式：

1. acquire `registry.lock`
2. 讀取 `registry.json`
3. 收集 / 更新 `observed/*`
4. 解析 project metadata、instance selection、bundle readiness
5. 做 reconcile
6. 決定 action（bootstrap register / request / reuse / release / gc）
7. 以 **atomic write** 更新 `registry.json`（先寫 temp，再 rename）
8. 必要時同步更新 `instances/<project-instance>/instance.json`
9. 釋放 lock

### Atomic write requirement

不可直接原地改寫一半的 `registry.json`。至少應採：

1. 寫入 `registry.json.tmp`
2. fsync / close
3. rename 覆蓋 `registry.json`

這樣才能避免 agent / shell / crash 中斷留下半份壞 JSON。

## 這個 registry 不應承擔什麼

- 不應承載 feature spec 依賴地圖
- 不應成為 `SPECS.md` 的替代品
- 不應被 agent 記憶或臨時 prompt 內容取代

若需要治理 feature / contract 變更，請回到 `spec-registry-manager` 與 `spec-driven-development`。
