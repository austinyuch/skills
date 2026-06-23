# Podman Rootless 與 K3S 整合範例

## 場景：aclab-middlewares 開發環境

使用 Podman rootless 執行 PostgreSQL 和 Valkey，搭配 K3S 執行應用服務。

---

## 架構

```
┌─────────────────────────────────────┐
│ 宿主機 (Rootless User)              │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Podman Rootless              │  │
│  │  - PostgreSQL (8432:5432)    │  │
│  │  - Valkey (8379:6379)        │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ K3S (containerd)             │  │
│  │  - sandbox-controller        │  │
│  │  - sandbox pods              │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## 步驟 1: Podman Compose 啟動中介軟體

### compose.yaml
```yaml
version: '3.8'

services:
  postgresql:
    image: postgres:17-alpine
    container_name: aclab-postgresql
    userns_mode: "keep-id"
    ports:
      - "8432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data:U
    environment:
      - POSTGRES_DB=devdb
      - POSTGRES_USER=devuser
      - POSTGRES_PASSWORD=devpass
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "devuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  valkey:
    image: valkey/valkey:7-alpine
    container_name: aclab-valkey
    userns_mode: "keep-id"
    ports:
      - "8379:6379"
    volumes:
      - valkey_data:/data:U
    command: valkey-server --appendonly yes
    healthcheck:
      test: ["CMD", "valkey-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  pg_data:
  valkey_data:
```

### 啟動
```bash
# 啟動中介軟體
podman-compose up -d

# 檢查狀態
podman-compose ps

# 測試連線
podman exec aclab-postgresql psql -U devuser -d devdb -c "SELECT 1"
podman exec aclab-valkey valkey-cli ping
```

### Systemd 整合 (開機自動啟動)
```bash
# 生成 systemd units
podman generate systemd --new --name aclab-postgresql \
  > ~/.config/systemd/user/aclab-postgresql.service

podman generate systemd --new --name aclab-valkey \
  > ~/.config/systemd/user/aclab-valkey.service

# 啟用服務
systemctl --user enable --now aclab-postgresql.service
systemctl --user enable --now aclab-valkey.service

# 允許登出後繼續執行
loginctl enable-linger $USER
```

---

## 步驟 2: K3S 連線到 Podman 服務

### 配置 (config-k3s-podman.yaml)
```yaml
provider:
  type: k3s
  k3s:
    kubeconfig: /etc/rancher/k3s/k3s.yaml
    ingress_class: traefik

database:
  host: 192.168.1.100  # 宿主機 IP
  port: 8432           # Podman 映射的 port
  database: devdb
  user: devuser
  password: devpass

cache:
  host: 192.168.1.100
  port: 8379
```

### 取得宿主機 IP
```bash
# 方法 1: 主要網路介面
ip -4 addr show | grep inet | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 | head -1

# 方法 2: 從 K3S node 查看
kubectl get nodes -o wide

# 方法 3: 使用 host.containers.internal (Podman 4.1+)
# 在 K3S Pod 內可用 host.containers.internal
```

### 網路連通性測試
```bash
# 從 K3S Pod 測試
kubectl run -it --rm debug --image=alpine --restart=Never -- sh

# 在 Pod 內
apk add postgresql-client redis
psql -h 192.168.1.100 -p 8432 -U devuser -d devdb
redis-cli -h 192.168.1.100 -p 8379 ping
```

---

## 步驟 3: 防火牆配置

### 允許 K3S 存取 Podman ports
```bash
# firewalld
sudo firewall-cmd --permanent --add-port=8432/tcp
sudo firewall-cmd --permanent --add-port=8379/tcp
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 8432 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8379 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4

# ufw
sudo ufw allow 8432/tcp
sudo ufw allow 8379/tcp
```

---

## 進階：使用 Podman Network

### 建立共享 network
```bash
# 建立 network
podman network create aclab-net

# 啟動容器加入 network
podman run -d --name postgresql \
  --network aclab-net \
  -p 8432:5432 \
  postgres:17-alpine

# K3S 可透過宿主機 IP + port 存取
```

---

## 故障排除

### 連線失敗
```bash
# 1. 檢查 Podman 容器狀態
podman ps

# 2. 檢查 port 監聽
ss -tlnp | grep -E "8432|8379"

# 3. 檢查防火牆
sudo firewall-cmd --list-ports

# 4. 測試本地連線
psql -h localhost -p 8432 -U devuser -d devdb
redis-cli -h localhost -p 8379 ping

# 5. 從 K3S 測試
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
```

### Volume 權限問題
```bash
# 進入 user namespace 檢查
podman unshare

# 在 namespace 內
ls -la /path/to/volume

# 調整權限
podman unshare chown -R 0:0 /path/to/volume
```

### Systemd 服務問題
```bash
# 檢查服務狀態
systemctl --user status aclab-postgresql.service

# 查看日誌
journalctl --user -u aclab-postgresql.service -f

# 重啟服務
systemctl --user restart aclab-postgresql.service
```

---

## 完整範例：開發環境設定

```bash
#!/bin/bash
# setup-podman-k3s-dev.sh

set -e

echo "🚀 設定 Podman + K3S 開發環境"

# 1. 啟動 Podman 中介軟體
echo "📦 啟動 Podman 中介軟體..."
podman-compose -f aclab-middlewares/compose.yaml up -d

# 2. 等待服務就緒
echo "⏳ 等待服務就緒..."
sleep 10

# 3. 測試連線
echo "🔍 測試連線..."
podman exec aclab-postgresql pg_isready -U devuser
podman exec aclab-valkey valkey-cli ping

# 4. 取得宿主機 IP
HOST_IP=$(ip -4 addr show | grep inet | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 | head -1)
echo "🌐 宿主機 IP: $HOST_IP"

# 5. 更新 K3S 配置
cat > config/config-k3s-podman.yaml <<EOF
provider:
  type: k3s
  k3s:
    kubeconfig: /etc/rancher/k3s/k3s.yaml
    ingress_class: traefik

database:
  host: $HOST_IP
  port: 8432
  database: devdb
  user: devuser
  password: devpass

cache:
  host: $HOST_IP
  port: 8379
EOF

echo "✅ 配置完成: config/config-k3s-podman.yaml"
echo "🚀 部署到 K3S: ./deploy/k3s/scripts/deploy.sh"
```

---

## 參考資料

- [Podman Rootless](https://docs.podman.io/en/latest/markdown/podman.1.html#rootless-mode)
- [Podman Compose](https://github.com/containers/podman-compose)
- [K3S Documentation](https://docs.k3s.io/)
- [User Namespaces](https://man7.org/linux/man-pages/man7/user_namespaces.7.html)
