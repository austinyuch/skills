# Podman Rootless 快速參考

## 常用命令

```bash
# 基本操作 (與 Docker 相同)
podman run -d --name myapp nginx
podman ps
podman logs -f myapp
podman exec -it myapp sh
podman stop myapp
podman rm myapp

# Compose
podman-compose up -d
podman-compose down -v

# 或使用內建 (Podman 4.0+)
podman compose up -d
```

## 關鍵差異

### Port Mapping
```bash
# ❌ 特權 port 會失敗
podman run -p 80:80 nginx

# ✅ 使用非特權 port
podman run -p 8080:80 nginx
```

### Volume 權限
```bash
# ❌ 直接 bind mount 可能權限錯誤
-v ./data:/data

# ✅ 使用 SELinux label
-v ./data:/data:Z

# ✅ 或自動 chown
-v ./data:/data:U

# ✅ 或保持 UID
--userns=keep-id -v ./data:/data
```

### UID Mapping
```bash
# 查看 mapping 範圍
grep $USER /etc/subuid /etc/subgid

# 進入 user namespace
podman unshare

# 調整檔案擁有者 (在 namespace 內)
podman unshare chown -R 0:0 ./data
```

## Systemd 整合

```bash
# 1. 建立容器
podman create --name myapp -p 8080:8080 myapp:latest

# 2. 生成 systemd unit
podman generate systemd --new --name myapp \
  > ~/.config/systemd/user/myapp.service

# 3. 啟用服務
systemctl --user daemon-reload
systemctl --user enable --now myapp.service

# 4. 允許登出後繼續執行
loginctl enable-linger $USER

# 5. 管理服務
systemctl --user status myapp
systemctl --user restart myapp
journalctl --user -u myapp -f
```

## Compose 範例

```yaml
version: '3.8'

services:
  app:
    build: .
    userns_mode: "keep-id"  # 保持 UID
    ports:
      - "8080:8080"         # 非特權 port
    volumes:
      - ./src:/app/src:Z    # SELinux label
    environment:
      - DATABASE_URL=postgresql://db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:17-alpine
    volumes:
      - db_data:/var/lib/postgresql/data:U  # 自動 chown
    environment:
      - POSTGRES_PASSWORD=secret

volumes:
  db_data:
```

## 除錯

```bash
# 檢查容器 UID
podman exec myapp id

# 檢查 volume 權限 (宿主機視角)
podman unshare ls -la ./data

# 檢查 volume 權限 (容器視角)
podman exec myapp ls -la /data

# 檢查 network
podman network ls
podman network inspect <network>

# 檢查 port
ss -tlnp | grep podman
```

## 最佳實踐

✅ **DO**:
- 使用 `:Z` 或 `:U` flag 處理 volume 權限
- Port mapping 使用 > 1024
- 使用 `userns_mode: "keep-id"` 簡化權限
- 生產環境用 systemd user services
- 使用 `loginctl enable-linger` 保持服務執行

❌ **DON'T**:
- 不要硬編碼容器內 UID
- 不要假設可綁定特權 port
- 不要在 Dockerfile 使用 `USER root`
- 不要忘記 SELinux context (RHEL/Fedora)

## 參考
- 完整指南: `skills/podman-rootless/SKILL.md`
- K3S 整合: `skills/podman-rootless/examples/k3s-integration.md`
