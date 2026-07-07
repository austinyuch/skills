# GitHub Actions overlay

Use this overlay for workflow YAML, reusable workflows, release automation, and repo-integrated CI/CD.

## Checks

- minimal `permissions:` per job
- prefer OIDC federation over stored cloud credentials
- pin third-party actions to SHAs or strongly governed refs
- restrict `pull_request_target`, self-hosted runners, and untrusted fork execution
- protect environments, approvals, and deployment branches
- ensure secret-scanning and dependency review failures are actionable

## Common failure patterns

- workflow on forked PR can reach deploy secrets
- action pinned to `@main`
- one workflow has write access to code, packages, and production deploy
