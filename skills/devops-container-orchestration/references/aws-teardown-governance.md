# AWS Teardown Governance for Container Orchestration

**Date**: 2026-04-22  
**Category**: DevOps / AWS Teardown  
**Applies To**: Any container orchestration that creates AWS resources (ECS/Fargate/EKS)

---

## Problem

When tearing down AWS container orchestration resources, Security Groups fail to delete with `DependencyViolation` errors even after all dependent resources are removed.

## Root Cause

Cross-SG `UserIdGroupPairs` references in ingress rules create circular dependencies that prevent SG deletion. This is common in container orchestration where:
- ALB SG allows inbound from internet
- Task SG allows inbound from ALB SG (via GroupId reference)
- Frontend SG allows inbound from ALB SG (via GroupId reference)

When ALB is deleted, the SG-to-SG rules persist on task/frontend SGs.

## Resolution Pattern

### 1. Before deleting any SG, scan for cross-references

```bash
aws ec2 describe-security-groups \
  --filters "Name=ip-permission.group-id,Values=<target-sg-id>" \
  --query 'SecurityGroups[?GroupId!=`<target-sg-id>`]'
```

### 2. Revoke all cross-SG ingress rules

```bash
aws ec2 revoke-security-group-ingress \
  --group-id <referencing-sg-id> \
  --ip-permissions '<exact-rule-structure>'
```

### 3. Add retry logic for transient dependencies

```python
import time

def delete_with_retry(delete_fn, max_retries=3, delay=5):
    for attempt in range(max_retries):
        try:
            return delete_fn()
        except Exception as e:
            if "DependencyViolation" in str(e) and attempt < max_retries - 1:
                time.sleep(delay)
                continue
            raise
```

### 4. Check for lingering ENIs

ECS tasks create ENIs that may persist briefly after task termination:

```bash
aws ec2 describe-network-interfaces \
  --filters "Name=group-id,Values=<sg-id>"
```

## Integration with Container Lifecycle

For any container orchestration workflow (KIND, Podman, Docker Compose, ECS):

| Phase | Action |
|-------|--------|
| **Request** | Record all SG IDs and their cross-references |
| **Reuse** | Verify no stale SG rules from previous runs |
| **Release** | Revoke cross-SG rules before deleting SGs |
| **GC** | Scan for orphaned ENIs and SGs |

## Related Skills

- `aws-agent-solution-architect`: Full AWS teardown patterns in `references/deployment-strategy.md`
- `local-infra-registry-governance`: Local container lifecycle governance
- `devops-container-orchestration`: This skill
