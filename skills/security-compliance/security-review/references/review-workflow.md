# Review workflow

Read this file first. It gives the sequence for turning a security request into an evidence-based review instead of a generic checklist.

## 1. Scope the trust boundary

Identify what changed:

- identity boundary: login, session, role, tenant, secret, privilege escalation
- data boundary: user input, files, queues, cache, database, analytics, logs
- execution boundary: background jobs, third-party APIs, webhooks, shells, code execution
- infrastructure boundary: CI/CD, cloud roles, deploy config, runtime identity, artifact provenance
- agent boundary: prompts, tools, memory, retrieval, MCP servers, autonomous actions

Name the highest-impact boundary first. That becomes the primary review lane.

## 2. Map entry points and sinks

For each changed path, note:

- entry point: route, handler, worker, webhook, CLI, pipeline step
- privilege context: anonymous, user, admin, service account, cloud role
- sinks: database, filesystem, network call, tool execution, secrets, logs
- side effects: write, delete, enqueue, deploy, notify, mutate policy

If you cannot trace entry point to sink, keep reading code until you can.

## 3. Select deep lanes

- Always read the matching app or infrastructure lane.
- Add one language lane to match framework-specific footguns.
- Add one platform overlay when hosted behavior matters.
- Add `zero-day-resilience.md` when the design assumes a control can fail.

## 4. Review by attack path

Prefer “how would this be abused?” over category dumping.

Example attack path structure:

1. attacker controls `input X`
2. service trusts `X` too early
3. privileged sink accepts `X`
4. result is data exposure, state change, or lateral movement

This keeps the review concrete.

## 5. Gather evidence

Use evidence, not intuition:

- validation schemas and parser placement
- authn/authz middleware and fallback behavior
- database policies, parameterization, row filters
- cookie flags, token TTL, key rotation, replay defenses
- outbound allowlists, SSRF guards, webhook signing
- CI permissions, OIDC setup, artifact attestations, lockfiles
- tests covering deny paths, tenant breaks, and failure modes

## 6. Classify findings

Use three buckets only:

- **Confirmed issue** — exploit path is present or control is missing.
- **Risk to verify before merge** — intent looks right but evidence is incomplete.
- **Acceptable with rationale** — residual risk is known and bounded.

Avoid speculative “maybe insecure” notes without naming the missing evidence.

## 7. Exit criteria

The review is ready when it includes:

- changed trust boundaries
- top attack paths
- concrete findings or explicit evidence of absence
- remediation steps matched to code or config layers
- verification notes: tests, policies, scans, or deployment checks

## Quick prompts for yourself

- What input becomes authority here?
- What privileged action happens after trust is granted?
- If one control fails, what contains the blast radius?
- If a secret leaks or token is replayed, what stops lateral movement?
- If the newest dependency or pipeline step is hostile, how do we know?
