# KIND with Podman Rootless - Lessons Learned

> Date: 2026-03-05
> Project: aclab-middlewares
> Context: Setting up KIND cluster for multi-database dev environment

## Problem

KIND (Kubernetes in Docker) requires either:
1. Docker daemon (runs as root, user in docker group = root-equivalent)
2. Podman with systemd delegation (rootless, requires system config + reboot)

## Decision: Podman + Systemd Delegation

### Why Not Docker?

**Security Risk in AD Domain Environment:**
- Docker group membership = root-equivalent access
- Compromised account can: `docker run -v /:/host alpine` → full filesystem access
- Can escape to root via privileged containers
- Not defensible in security audits

**Podman Rootless Advantages:**
- True rootless - containers run as user UID
- No daemon running as root
- Better isolation via user namespaces
- Principle of least privilege
- Corporate security compliance

### Systemd Delegation Risk Assessment

**What it enables:**
- User session can manage cgroups (CPU, memory, I/O limits)
- Required for Kubernetes pod resource management

**Security impact:**
- ✅ Only affects your user account
- ✅ Cannot escalate to root
- ✅ Cannot affect other users
- ⚠️ Can create resource hierarchies (limited to user quotas)
- ⚠️ Slightly larger attack surface (cgroup manipulation)

**Verdict:** Low risk, standard practice for rootless containers

## Implementation

### 1. Preparation Script

```bash
# /k8s/prepare-kind-podman.sh
sudo mkdir -p /etc/systemd/system/user@$(id -u).service.d/
sudo tee /etc/systemd/system/user@$(id -u).service.d/delegate.conf > /dev/null <<EOF
[Service]
Delegate=yes
EOF

sudo systemctl daemon-reload
sudo loginctl enable-linger $USER
echo "export KIND_EXPERIMENTAL_PROVIDER=podman" >> ~/.bashrc
```

### 2. Persistent Volumes

**Challenge:** KIND uses internal storage by default, lost on cluster delete

**Solution:** extraMounts + hostPath PersistentVolumes

```yaml
# config/kind-cluster.yaml
nodes:
  - role: control-plane
    extraMounts:
      - hostPath: <workspace-root>/projects
        containerPath: /host/projects
```

```yaml
# k8s/persistent-volumes.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgresql-pv
spec:
  hostPath:
    path: /host/projects/aclab-middlewares/.volumes-k8s/postgresql
    type: DirectoryOrCreate
```

**Directory structure:**
```
.volumes/          # Podman compose (existing services)
.volumes-k8s/      # KIND cluster (new, persistent)
```

### 3. Unified Management Script

Created `kind-services.py` - systemctl-like interface:
- `status` - Show cluster and pod status
- `deploy` - Full deployment with PV setup
- `restart` - Stop + deploy
- `stop` - Delete resources, keep cluster
- `teardown` - Complete cleanup

## Key Takeaways

1. **Reboot is mandatory** - Systemd delegation requires full restart
2. **Verify delegation** - `systemctl --user show --property=Delegate user@$(id -u).service`
3. **Separate volumes** - Don't mix compose and K8s data
4. **Security first** - Rootless is worth the setup complexity in corporate environments
5. **Plan extraMounts** - Can't add host paths after cluster creation

## Prerequisites

- cgroup v2 (check: `ls /sys/fs/cgroup/cgroup.controllers`)
- Podman rootless configured
- KIND v0.20.0+
- kubectl

## References

- KIND rootless docs: https://kind.sigs.k8s.io/docs/user/rootless/
- Systemd delegation: https://systemd.io/CGROUP_DELEGATION/
- Project: `<workspace-root>/projects/aclab-middlewares/k8s/`
