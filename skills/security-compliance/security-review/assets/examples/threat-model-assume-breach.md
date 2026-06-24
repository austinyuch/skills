# Worked example: threat model with assume-breach posture

## Scenario

A GitHub Actions workflow builds a container, pushes it to a registry, and deploys to AWS using OIDC. The application later calls an internal MCP server for file and ticket operations.

## Assume-breach exercise

### Assumption 1: a third-party GitHub Action is compromised

- **Primary effect:** attacker gains workflow execution in CI.
- **Blast radius question:** can that job read deploy secrets, write source, approve release, or publish artifacts?
- **Desired containment:** OIDC role limited to deploy-only for a single environment, immutable artifact promotion, no long-lived secrets, environment approval gate.

### Assumption 2: runtime access token leaks from application logs

- **Primary effect:** attacker can call internal APIs or MCP server.
- **Blast radius question:** does one token grant broad tenant access or broad filesystem/tool access?
- **Desired containment:** short TTL, token audience checks, resource-scoped authorization inside the MCP server, rapid revocation path.

### Assumption 3: retrieved issue content prompt-injects the agent

- **Primary effect:** agent attempts destructive tool usage.
- **Blast radius question:** can issue text trigger arbitrary file writes, ticket closure, or secret reads?
- **Desired containment:** strict tool schemas, approval gates for mutations, path/domain allowlists, audit logs of tool calls.

## Example final note

Even if CI or retrieval content is hostile, the design should still limit production impact through short-lived identity, scoped deploy roles, approval-gated mutations, and server-side authorization inside the MCP boundary. If any one of those layers is absent, treat the change as high-risk until containment is added.
