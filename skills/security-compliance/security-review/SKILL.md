---
name: security-review
description: Use this skill whenever code changes touch authentication, authorization, sessions, secrets, untrusted input, API endpoints, AI/agent integrations, CI/CD, cloud infrastructure, dependency supply chain, or other sensitive trust boundaries. It routes the agent to deeper review lanes by workflow, app layer, language, platform, and zero-day / assume-breach posture while preserving the existing benchmark tooling.
---

# Security Review

Use this skill to turn a vague “check security” request into a focused review. Do not try to carry the whole checklist in this file; route immediately to the narrowest deep references that match the change.

## Start here

1. Read `references/review-workflow.md` first.
2. Select the app-layer lane from `references/app-api-data.md`.
3. Add the trust-boundary lane from `references/authn-authz-session.md`, `references/ai-agent-mcp.md`, or `references/infrastructure-supply-chain.md`.
4. Add one language lane from `references/languages/` and one platform overlay from `references/platforms/` when they apply.
5. If the change expands blast radius or depends on partial trust, also read `references/zero-day-resilience.md`.

## Lane selector

### Core workflow

- `references/review-workflow.md` — default review sequence, evidence expectations, and exit criteria.
- `references/zero-day-resilience.md` — assume-breach, zero-trust, resilience, rollback, and containment guidance.

### Identity and session boundaries

- `references/authn-authz-session.md` — authentication, authorization, session lifecycle, tokens, cookies, impersonation, tenancy, MFA.

### Application layers

- `references/app-api-data.md` — input validation, files, APIs, SSRF, deserialization, database access, queues, caches, logging, privacy.
- `references/ai-agent-mcp.md` — prompt injection, tool misuse, capability scoping, MCP safety, retrieval poisoning, output handling.
- `references/infrastructure-supply-chain.md` — CI/CD, artifact trust, SBOMs, provenance, secrets delivery, cloud controls, incident hooks.

### Language lanes

- `references/languages/go.md`
- `references/languages/javascript-typescript.md`
- `references/languages/python.md`
- `references/languages/dotnet-csharp.md`

### Platform overlays

- `references/platforms/github-actions.md`
- `references/platforms/aws-core.md`
- `references/platforms/vercel-nextjs.md`
- `references/platforms/supabase.md`

### Worked examples

- `assets/examples/pr-code-review.md` — worked pull-request review with evidence and review comments.
- `assets/examples/threat-model-assume-breach.md` — compact threat model using assume-breach posture.

## Minimum output contract

Return a review that is specific to the changed trust boundaries, not a generic wall of bullets.

- State what was reviewed.
- Name the main risks that are real for this change.
- Separate confirmed issues from “verify before merge” concerns.
- Give concrete remediations with file or layer hints.
- Note what evidence was checked: tests, policies, config, code paths, or deployment settings.

## Benchmarking and provenance

Keep the existing benchmark tooling intact.

- Benchmark runner: `scripts/run_security_benchmark.py`
- Local benchmark docs: `evals/BENCHMARKING.md`
- Copy alignment helper: `scripts/sync_copies.py`

Do not write benchmark state into the installed skill directory. Preserve the existing provenance behavior instead of inventing a new storage policy.

## Compatibility note

`cloud-infrastructure-security.md` is retained as a stub for older references. Treat the deep infrastructure guidance in `references/infrastructure-supply-chain.md` plus the platform overlays as the canonical source.
