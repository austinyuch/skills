---
name: devops-container-orchestration
description: 容器編排模式，涵蓋多實例服務部署、資料庫配置、基礎設施生命週期管理、KIND 叢集部署（Podman rootless）。當需要 (1) 部署多實例資料庫（如每個 app 獨立 Neo4j），(2) 在已獲得 registry-governed allocation 後配置服務資源，(3) 管理 Podman rootless 容器生命週期，(4) 設計共享開發基礎設施，(5) 設置 KIND 叢集並選擇 Podman/Docker 運行時，(6) 實作持久化儲存策略時使用。
---

# DevOps Container Orchestration

容器編排的實戰模式與最佳實踐。

## 與 Local Infra Registry 的邊界

這個 skill 負責 **allocation 之後** 的容器實作模式。

- 如果是 multi-project local dev / UAT / E2E 的 live host resource（ports、networks、stack names），必須先由 `local-infra-registry-governance` 或等價的 registry-governed tool 決定可用 allocation。
- 這個 skill 不應自行成為 allocation authority，也不應鼓勵 agent 直接猜測 localhost resources。
- 若 exact instance 不存在但 project 下有多個 plausible candidates，應交回 `local-infra-registry-governance` 做 deterministic resolve 或 developer HITL selection；這個 skill 不負責猜測要落在哪個 instance。
- 容器成功啟動不等於 env ready；對 multi-service local runtime，應以 required service bundle 全部健康為準。

## 多實例容器模式

### Port 分配策略

為每種服務類型預留 port 範圍，按 app 順序分配：

> 這些範圍是 implementation pattern，不是繞過 registry 後由 agent 自行硬選的理由。若存在 shared local infra registry，請先取得 allocation，再套用此處模式。

| 服務 | 基礎範圍 | 每實例 Ports |
|------|---------|-------------|
| Neo4j | 17475-17499 | 2 (HTTP + Bolt) |
| PostgreSQL | 15432 (共享) | 1 |
| 自訂服務 | 18000+ | 視需求 |

### docker-compose 模式

參考 [code/multi-instance-template.yaml](code/multi-instance-template.yaml) 查看完整範例。

**關鍵規則**：
1. 使用預設內部 port，映射到唯一 host port
2. Bind mount volumes 到 `.volumes/{service}-{app}/`
3. 每實例獨立密碼（透過 `.env`）
4. 考慮慢啟動服務（Neo4j ~90s）
5. 對跨專案共享的 local host resources，優先尊重 registry-governed ownership / TTL / reconcile flow

## 資料庫配置模式

### 共享 PostgreSQL 多資料庫

參考 [code/postgres-provisioning.go](code/postgres-provisioning.go) 查看實作。

**關鍵：DSN 操作**

始終使用 URL parsing，不要字串切割：
```go
// 正確
parsedDSN, _ := url.Parse(dsn)
parsedDSN.Path = "/" + newDB
result := parsedDSN.String()
```

## Credential 管理

### 每 App Credential 檔案

```
.env                    # 系統級 credentials
.env.{app-code}         # 每 app credentials (gitignored)
```

參考 [code/env-template.txt](code/env-template.txt) 查看格式範例。

## Sandbox-Station Spawn 模式參考

`opencode-sandbox-station` 專案實作 WorkloadController 模式用於隔離環境：

- `WorkloadController` 管理生命週期（create, exec, destroy）
- `ProcessReconciler` 處理 OS 級資源分配
- `PortPool` 動態 port 分配（範圍 4096-5096）
- `QuotaManager` 強制每用戶限制
- TaskBus 提供非同步任務執行

**適用於基礎設施生命週期**：
- 將短暫 workloads 替換為持久服務實例
- 使用 DB tables 而非 in-memory maps 儲存狀態
- 從 DB records 生成 podman-compose fragments
- Reconciler 模式實現 desired-state → actual-state 收斂

## Health Check 模式

參考 [code/healthcheck-patterns.yaml](code/healthcheck-patterns.yaml) 查看範例。

## KIND 叢集部署

### 安全性比較與選擇

**何時閱讀詳細分析**：選擇 Podman 或 Docker 作為 KIND 運行時前，閱讀 [references/docker-vs-podman-security.md](references/docker-vs-podman-security.md)。

**快速決策表**：

| 環境 | 推薦 | 原因 |
|-----|------|------|
| 企業/AD domain | Podman + delegation | 安全合規 |
| 個人開發 VM | Docker | 便利性 |
| 生產環境 | Podman rootless | 最小權限原則 |

### Podman Rootless 設置

**完整指南**：參考 [references/kind-podman-rootless.md](references/kind-podman-rootless.md)。

**快速設置**：
```bash
# 執行準備 script
./k8s/prepare-kind-podman.sh

# 重啟電腦（必須）

# 驗證
systemctl --user show --property=Delegate user@$(id -u).service
# 應顯示：Delegate=yes
```

### 持久化儲存策略

KIND 預設使用內部儲存（叢集刪除時遺失）。

**實作持久化**：
1. 在 `kind-cluster.yaml` 配置 extraMounts
2. 建立 PersistentVolumes 使用 hostPath
3. 目錄結構：`.volumes-k8s/` (KIND) vs `.volumes/` (compose)

參考 [code/kind-persistent-volumes.yaml](code/kind-persistent-volumes.yaml) 查看範例。

### 叢集管理 Script

建立 systemctl-like 介面：

```bash
./kind-services.py status     # 顯示叢集狀態
./kind-services.py deploy     # 部署所有服務
./kind-services.py restart    # 重啟所有服務
./kind-services.py stop       # 停止服務（保留叢集）
./kind-services.py teardown   # 完整清理
```

參考 [scripts/kind-services-template.py](scripts/kind-services-template.py) 查看實作模板。

## 相關資源

- Steering: `docker-standards` - Docker/Podman 基礎標準
- Steering: `devops-standards` - CI/CD 與部署
- Steering: `aws-teardown-governance` - AWS 資源拆除模式（Security Group 依賴違規、ENI 清理、跨 SG 規則撤銷）
- References: [references/aws-teardown-governance.md](references/aws-teardown-governance.md) - AWS teardown 實戰經驗
- Skill: `aws-agent-solution-architect` - 完整 AWS 部署策略（含 teardown 模式於 `references/deployment-strategy.md`）
