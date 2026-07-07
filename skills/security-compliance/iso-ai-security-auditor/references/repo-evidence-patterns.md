# Repository Evidence Patterns

Use these patterns to find implementation and design evidence. Treat search results as leads; read the files before judging.

## High-Value Files and Directories

- Governance: `AGENTS.md`, `.agents/specs/`, `docs/`, `README*`, `SECURITY.md`, `CONTRIBUTING.md`
- Architecture: `docs/architecture*`, `.agents/steering/`, `design.md`, `requirements.md`, `review.md`
- CI/CD: `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `Makefile`, `scripts/`
- Infrastructure: `infra/`, `deploy/`, `terraform/`, `helm/`, `k8s/`, `docker-compose*`, `Dockerfile`
- Application security: auth, session, RBAC, CSRF, CORS, validation, rate limit, audit log, secrets, encryption
- Logging and observability: logger wrappers, telemetry, OpenTelemetry, SIEM routing, audit event catalog, retention policy, redaction/masking, trace IDs
- AI: prompts, tools, MCP, model/provider config, evals, guardrails, datasets, model cards, data cards, retrieval indexes
- Evidence: reports, test results, audit outputs, SBOM, dependency scan, SAST scan, secret scan, release attestations

## Search Leads

Security and governance:

```bash
rg -n "auth|authorization|RBAC|MFA|session|cookie|csrf|cors|rate.?limit|audit.?log|trace.?id|secret|vault|kms|encrypt|token|jwt|oauth|saml|oidc" .
rg -n "threat.?model|risk|incident|postmortem|vulnerability|dependency|SBOM|SAST|secret.?scan|signing|provenance|backup|restore|BCP|DR" .
```

AI-specific:

```bash
rg -n "AI|LLM|model|prompt|embedding|RAG|MCP|tool.?call|guardrail|eval|dataset|data.?card|model.?card|provenance|drift|human.?oversight|impact.?assessment" .
rg -n "prompt.?injection|data.?poison|model.?theft|model.?inversion|hallucination|PII|privacy|consent|retention" .
```

Log governance:

```bash
rg -n "log|logger|logging|audit.?event|audit.?trail|trace.?id|span.?id|OpenTelemetry|otel|SIEM|CloudTrail|retention|redact|mask|sanitize|scrub|PII|personal.?data|secret|token|password|prompt|completion|tool.?call" .
rg -n "request.?body|response.?body|headers|authorization|cookie|set-cookie|x-api-key|api.?key|bearer|session|email|phone|address|geolocation|national.?id|credit.?card" .
```

External-control evidence:

```bash
rg -n "Okta|Auth0|Azure AD|Entra|Cognito|CloudTrail|Security Hub|GuardDuty|SIEM|SOC|Snyk|Dependabot|Wiz|Vault|KMS|Datadog|Sentry|OpenTelemetry|DPA|SOC 2|ISO 27001" .
```

## Reading Rules

- Follow dependency injection and config chains to actual implementation.
- For auth/access checks, read router -> middleware -> service -> data layer.
- For AI/agent checks, read prompt/tool definitions -> tool permission boundary -> provider calls -> output handling -> logging.
- For external systems, record the integration point and the owner of external proof.
- Do not treat a package dependency as evidence of a control unless the repo config or code actually uses it.

## Evidence Quality Tags

- `strong`: implemented config/code plus tests or operational report.
- `medium`: implementation exists but tests or operating evidence missing.
- `weak`: design note, README claim, or unused config.
- `external`: delegated to a named external system with owner and proof pointer.
- `absent`: no relevant evidence found.
