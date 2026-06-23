---
name: k8s-security-patterns
description: Kubernetes 安全模式與最佳實踐。涵蓋 Podman Rootless、User Namespace、容器權限管理、Volume 權限處理等安全議題。
---

# Kubernetes Security Patterns

## Podman Rootless & User Namespace

### 問題
- Podman rootless 使用 user namespace mapping
- 容器內 uid 1000 → 宿主機 uid 101000
- 硬編碼 UID 導致 volume 權限問題

### 解決方案

**1. 移除硬編碼 UID (推薦)**
```yaml
securityContext:
  runAsNonRoot: true
  # 不指定 runAsUser，使用映像預設
```

**2. 使用映像實際 UID**
```bash
# 檢查映像預設 user
docker run --rm <image> id
```

**3. 動態配置**
```yaml
# 提供配置選項但不強制
security:
  run_as_user: null      # null = 使用映像預設
  fs_group: null
  allow_root: false
```

### 最佳實踐
- ✅ 使用 `runAsNonRoot: true` 強制非 root
- ✅ 移除 `runAsUser` 硬編碼
- ✅ 讓映像決定執行 UID
- ✅ 使用 `fsGroup` 僅在需要共享 volume 時
- ❌ 避免假設特定 UID 存在

## SecurityContext 層級

### Pod-level
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
```

### Container-level
```yaml
containers:
- securityContext:
    allowPrivilegeEscalation: false
    capabilities:
      drop: ["ALL"]
```

## 參考
- [Podman Rootless](https://docs.podman.io/en/latest/markdown/podman.1.html#rootless-mode)
- [K8s Security Context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)
