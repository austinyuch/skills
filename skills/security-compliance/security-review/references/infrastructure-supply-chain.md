# Infrastructure and supply chain lane

Use this lane for CI/CD, cloud IAM, deployment identity, secrets delivery, dependencies, containers, SBOMs, attestations, and runtime hardening.

## Identity and secret flow

- Prefer short-lived federated identity (OIDC, workload identity) over stored cloud keys.
- Separate build, deploy, and runtime identities.
- Keep secrets out of build args, image layers, logs, and client bundles.

## CI/CD checks

- Minimize workflow permissions.
- Pin actions and reusable workflows to trusted refs or SHAs.
- Protect release branches and environments.
- Verify artifact promotion path from build to deploy.

## Dependency and artifact checks

- Use lockfiles and reproducible install commands.
- Run vulnerability and license scans, but also review reachability and exploitability.
- Prefer signed packages, attestations, or provenance where the ecosystem supports it.
- Generate or preserve SBOM output for release artifacts.

## Container and runtime checks

- Non-root where possible.
- Read-only root filesystem where possible.
- Drop unused Linux capabilities.
- Limit network egress for workers that do not need arbitrary internet access.

## Cloud control checks

- IAM should be least-privilege and resource-scoped.
- Security groups, firewalls, and service policies should default deny.
- Logging should capture auth failures, admin actions, and deploy events.
- Backup and restore path should be tested, not just declared.

## Incident hooks

- Key rotation path documented and automatable.
- Feature flags or kill switches for risky integrations.
- Rollback path for bad releases and poisoned artifacts.
- Emergency disable path for compromised automation principals.

## Common failure patterns

- pipeline has `contents: write` or cloud-admin for the whole job
- action pinned only to a mutable tag
- secrets baked into a container image at build time
- deploy role can read unrelated production data stores
- vulnerability scanner exists but failed results are non-blocking and ignored
