---
name: podman-rootless
description: Podman Rootless 開發指南。涵蓋 User Namespace、UID/GID mapping、網路配置、Volume 權限、K3s 整合等 rootless 容器開發最佳實踐。
---

# Podman Rootless 開發指南

## 核心概念

### Rootless vs Rootful
- **Rootless**: 以一般使用者身份執行，無需 root 權限
- **User Namespace**: UID/GID mapping (容器內 uid 0 → 宿主機 uid 100000+)
- **安全性**: 容器逃逸只影響當前使用者，不影響系統
- **限制**: 無法綁定 < 1024 port，需要 slirp4netns 網路

### 與 Docker 差異

| 特性 | Docker | Podman Rootless |
|------|--------|-----------------|
| Daemon | 需要 dockerd (root) | 無 daemon |
| 權限 | 需要 root 或 docker group | 一般使用者 |
| UID Mapping | 直接映射 | User namespace mapping |
| Port < 1024 | 可直接綁定 | 需要 port mapping |
| systemd | Docker service | User systemd |
| Socket | `/var/run/docker.sock` | `$XDG_RUNTIME_DIR/podman/podman.sock` |

---

## Podman Compose

### 安裝
```bash
# Fedora/RHEL
sudo dnf install podman-compose

# Ubuntu/Debian
pip3 install podman-compose

# 或使用 Podman 內建
podman compose  # Podman 4.0+
```

### 基本使用
```bash
# 與 docker-compose 語法相同
podman-compose up -d
podman-compose ps
podman-compose logs -f
podman-compose down
```

---

## 常見問題與解決

### 1. UID/GID Mapping

**問題**: Volume 權限錯誤
```bash
# 容器內 uid 1000 → 宿主機 uid 101000
# 檔案擁有者不匹配
```

**解決方案**:

**A. 使用 :Z 或 :z flag (推薦)**
```yaml
volumes:
  - ./data:/data:Z      # SELinux relabel, 私有
  - ./config:/config:z  # SELinux relabel, 共享
```

**B. 使用 :U flag (自動 chown)**
```yaml
volumes:
  - ./data:/data:U      # Podman 自動調整權限
```

**C. 手動調整宿主機權限**
```bash
# 查看 subuid 範圍
grep $USER /etc/subuid
# ac:100000:65536

# 調整目錄擁有者
podman unshare chown -R 0:0 ./data
# 容器內看到 root:root，宿主機是 100000:100000
```

**D. 使用 userns=keep-id**
```yaml
services:
  app:
    userns_mode: "keep-id"  # 保持宿主機 UID
    volumes:
      - ./data:/data
```

### 2. Port Binding < 1024

**問題**: 無法綁定特權 port
```bash
podman run -p 80:80 nginx
# Error: cannot listen on privileged port
```

**解決方案**:

**A. Port mapping (推薦)**
```yaml
ports:
  - "8080:80"  # 宿主機 8080 → 容器 80
```

**B. 使用 net.ipv4.ip_unprivileged_port_start**
```bash
# 允許綁定 port 80+
sudo sysctl net.ipv4.ip_unprivileged_port_start=80
```

**C. 使用 Nginx/Traefik 反向代理**
```bash
# 系統級 Nginx 監聽 80 → Podman 容器 8080
```

### 3. Network 模式

**問題**: 預設使用 slirp4netns，效能較差

**解決方案**:

**A. 使用 pasta (Podman 4.4+, 推薦)**
```bash
podman run --network pasta nginx
# 更好的效能
```

**B. 使用 host network**
```yaml
network_mode: "host"  # 直接使用宿主機網路
```

**C. 使用 bridge (需要額外設定)**
```bash
# 需要 netavark 或 CNI plugins
```

### 4. Systemd 整合

**問題**: 容器需要開機自動啟動

**解決方案**:

**A. User systemd (推薦)**
```bash
# 生成 systemd unit
podman generate systemd --new --name myapp > ~/.config/systemd/user/myapp.service

# 啟用服務
systemctl --user enable myapp.service
systemctl --user start myapp.service

# 允許使用者登出後繼續執行
loginctl enable-linger $USER
```

**B. Podman Compose systemd**
```bash
# 為整個 compose 專案生成 systemd
cd /path/to/compose
podman-compose up -d
podman generate systemd --new --name project_app_1 > ~/.config/systemd/user/project-app.service
```

### 5. Volume 效能

**問題**: Bind mount 效能較差

**解決方案**:

**A. 使用 named volumes**
```yaml
volumes:
  db_data:  # Podman 管理的 volume

services:
  db:
    volumes:
      - db_data:/var/lib/postgresql/data
```

**B. 使用 :O flag (overlay)**
```yaml
volumes:
  - ./src:/app/src:O  # Overlay mount, 更好效能
```

### 6. 容器間通訊

**問題**: 預設 network 隔離

**解決方案**:

**A. 使用 podman-compose (自動建立 network)**
```yaml
# podman-compose 自動建立 network
services:
  app:
    depends_on:
      - db
  db:
    # app 可用 'db' hostname 連線
```

**B. 手動建立 network**
```bash
podman network create mynet
podman run --network mynet --name db postgres
podman run --network mynet --name app myapp
```

---

## 最佳實踐

### Compose 檔案範例

```yaml
version: '3.8'

services:
  app:
    build: .
    userns_mode: "keep-id"  # 保持 UID
    volumes:
      - ./src:/app/src:Z    # SELinux label
    ports:
      - "8080:8080"         # 避免特權 port
    environment:
      - DATABASE_URL=postgresql://db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:17-alpine
    volumes:
      - db_data:/var/lib/postgresql/data:Z
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password

volumes:
  db_data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### 開發工作流程

```bash
# 1. 啟動服務
podman-compose up -d

# 2. 查看日誌
podman-compose logs -f app

# 3. 進入容器
podman-compose exec app sh

# 4. 重啟服務
podman-compose restart app

# 5. 停止並清理
podman-compose down -v
```

### 生產環境部署

```bash
# 1. 建構映像
podman build -t myapp:latest .

# 2. 生成 systemd unit
podman create --name myapp \
  -p 8080:8080 \
  -v myapp_data:/data:Z \
  myapp:latest

podman generate systemd --new --name myapp \
  > ~/.config/systemd/user/myapp.service

# 3. 啟用服務
systemctl --user enable --now myapp.service

# 4. 允許登出後繼續執行
loginctl enable-linger $USER

# 5. 檢查狀態
systemctl --user status myapp.service
```

---

## 除錯技巧

### 檢查 UID Mapping
```bash
# 查看 subuid/subgid 範圍
grep $USER /etc/subuid /etc/subgid

# 進入 user namespace
podman unshare

# 在 namespace 內檢查
id
ls -ln /path/to/volume
```

### 檢查 Volume 權限
```bash
# 容器內
podman exec myapp ls -la /data

# 宿主機 (在 user namespace)
podman unshare ls -la ./data
```

### 檢查 Network
```bash
# 列出 networks
podman network ls

# 檢查 network 詳情
podman network inspect <network>

# 測試連線
podman exec app ping db
```

---

## 遷移指南

### 從 Docker 遷移到 Podman

```bash
# 1. 安裝 Podman
sudo dnf install podman podman-compose

# 2. 設定 alias (可選)
alias docker=podman
alias docker-compose=podman-compose

# 3. 修改 compose 檔案
# - 加入 :Z flag 到 volumes
# - 使用 userns_mode: "keep-id"
# - Port mapping 避免 < 1024

# 4. 測試
podman-compose up -d
podman-compose ps

# 5. 生產環境使用 systemd
podman generate systemd --new --name myapp
```

### 相容性檢查清單
- ✅ Volume 使用 :Z 或 :U flag
- ✅ Port mapping 避免特權 port
- ✅ 使用 userns_mode: "keep-id" 或不指定 UID
- ✅ Network 使用 compose 自動建立
- ✅ Secrets 使用 file-based
- ✅ 測試 systemd 整合

---

## 參考資料

- [Podman Rootless](https://docs.podman.io/en/latest/markdown/podman.1.html#rootless-mode)
- [Podman Compose](https://github.com/containers/podman-compose)
- [User Namespaces](https://man7.org/linux/man-pages/man7/user_namespaces.7.html)
- [Systemd Integration](https://docs.podman.io/en/latest/markdown/podman-generate-systemd.1.html)
