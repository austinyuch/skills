# Security Risk Analysis: Docker vs Podman for KIND

> Date: 2026-03-05
> Context: Choosing container runtime for local Kubernetes development

## Threat Model

**Scenario:** Developer account is compromised (malicious dependency, phishing, etc.)

## Option 1: Docker-based KIND

### Attack Surface

**Docker Group Membership = Root Equivalent**

```bash
# Attacker gains access to your shell
whoami  # your-username
groups  # ... docker ...

# Escalate to root
docker run -v /:/host -it alpine chroot /host

# Now effectively root:
cat /host/etc/shadow
useradd -m -G sudo attacker
# Install backdoor, modify system files, etc.
```

### Why This Works

1. Docker daemon runs as root
2. Docker group members can communicate with daemon
3. Can mount any host path into container
4. Can run privileged containers
5. No audit trail (appears as legitimate docker usage)

### Real-World Impact

- **CVE-2019-5736**: runc container escape (affects Docker)
- **CVE-2020-15257**: containerd host network access
- Docker group = root is documented security anti-pattern
- Many corporate policies explicitly forbid docker group membership

## Option 2: Podman Rootless + Systemd Delegation

### Attack Surface

**Limited to User Namespace**

```bash
# Attacker gains access to your shell
whoami  # your-username
groups  # ... (no docker group) ...

# Try to escalate
podman run -v /:/host -it alpine chroot /host
# Error: permission denied (rootless can't mount /)

# Try to access root files
podman run -v /etc/shadow:/shadow:ro alpine cat /shadow
# Error: permission denied

# Try privileged container
podman run --privileged alpine
# Runs, but "privileged" only within user namespace
# Cannot access host resources outside user's permissions
```

### Systemd Delegation Risk

**What attacker CAN do:**
- Manipulate cgroups for your user's processes
- Create resource hierarchies (CPU, memory limits)
- Potentially DoS your own user session

**What attacker CANNOT do:**
- Escape user namespace to root
- Access other users' files
- Modify system configuration
- Install system-wide backdoors
- Affect system services

### Defense in Depth

Even with delegation, multiple barriers exist:
1. User namespace isolation
2. SELinux/AppArmor policies (if enabled)
3. Seccomp filters
4. Capability dropping
5. Resource quotas

## Comparison Matrix

| Attack Vector | Docker | Podman + Delegation |
|--------------|--------|---------------------|
| Mount host root | ✅ Succeeds | ❌ Denied |
| Read /etc/shadow | ✅ Succeeds | ❌ Denied |
| Write to /usr/bin | ✅ Succeeds | ❌ Denied |
| Create system user | ✅ Succeeds | ❌ Denied |
| Install rootkit | ✅ Succeeds | ❌ Denied |
| DoS user session | ✅ Succeeds | ⚠️ Possible (cgroups) |
| Persist across reboot | ✅ Easy | ❌ Difficult |

## Corporate Environment Considerations

### AD Domain Context

**Docker risks:**
- Domain admin might audit docker group membership
- Violates principle of least privilege
- Hard to justify in security review
- May trigger compliance alerts

**Podman + delegation:**
- Standard rootless container setup
- Aligns with zero-trust principles
- Defensible in security audits
- Minimal system changes (one systemd unit)

### Incident Response

**Docker compromise:**
- Assume full system compromise
- Requires full system rebuild
- Potential domain credential theft
- Lateral movement risk

**Podman compromise:**
- Isolated to user account
- Reset user password
- Review user's files
- No system rebuild needed

## Recommendation

**Use Podman + Systemd Delegation** because:

1. **Defense in depth**: Multiple isolation layers
2. **Blast radius**: Compromise limited to user account
3. **Compliance**: Aligns with corporate security policies
4. **Auditability**: Clear separation of privileges
5. **Best practice**: Industry standard for rootless containers

**One-time reboot cost is worth the security improvement.**

## References

- Docker security: https://docs.docker.com/engine/security/#docker-daemon-attack-surface
- Podman rootless: https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md
- NIST SP 800-190: Application Container Security Guide
- CIS Docker Benchmark: Recommends against docker group membership
