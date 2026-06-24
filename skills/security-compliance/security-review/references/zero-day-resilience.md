# Zero-day and assume-breach lane

Use this lane when the system would suffer badly if one control fails, a dependency is compromised, or a new exploit appears before a patch exists.

## Core posture

Assume one of these is already true:

- a dependency is malicious or suddenly exploitable
- a session or secret leaks
- an internal service is reachable by an attacker
- a prompt or retrieved document is hostile
- a cloud role or CI token is abused

Then ask what still limits blast radius.

## Resilience checks

- strong segmentation between user, admin, build, and runtime identities
- narrow egress and service-to-service access
- short-lived credentials and fast revocation
- immutable deploys plus rapid rollback
- detection for unusual token use, privilege changes, or data access spikes
- kill switches for expensive or dangerous automations

## Zero-trust checks

- no trust based only on network location
- every service call authenticated and authorized
- tenant and role context derived from trusted identity, not forwarded user claims alone
- internal admin tools reviewed like internet-facing surfaces

## Dependency-compromise checks

- can the build be reproduced from known inputs?
- can a compromised action, package, or base image reach production secrets?
- can a poisoned artifact be quarantined or rolled back quickly?

## Review prompt

Write one short section in the final review:

1. **single-control failure** — what happens if the primary defense breaks?
2. **blast radius** — what data, tenants, or environments are exposed?
3. **containment** — what second-layer controls still help?
4. **operator action** — what can the team disable, rotate, or roll back within minutes?

## Common failure patterns

- “private VPC” treated as enough authorization
- one shared secret unlocks many systems
- deploy pipeline can both build and approve production release
- no way to disable an MCP tool or agent action without full outage
