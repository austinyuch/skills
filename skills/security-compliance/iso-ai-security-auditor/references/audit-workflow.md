# Audit Workflow

This workflow combines Inversion, Reviewer, Pipeline, and Generator patterns.

## Phase 1 - Intake and Boundary

Establish the audit scope before judging evidence.

- Identify the product/system/repository and business owner.
- Identify whether the audit covers ISMS, AI management, or both.
- Identify AI roles: developer, provider, deployer, user, monitor, integrator, data provider, or customer-facing operator.
- Identify deployment scope: local-only, SaaS, cloud, on-prem, mobile, embedded, internal tool, or public service.
- Identify whether regulated data, personal data, confidential data, safety-impacting decisions, automated decisions, or third-party AI services are in scope.
- Identify market and organization facts: registered jurisdiction, manufacturing/product scope, global marketing regions, information-service functions, public-company/reporting status, and payment/health/education/finance/children/employment triggers.

If scope is ambiguous, ask only the highest-impact missing question. Continue with conservative assumptions if the user asks to proceed.

If jurisdiction/country or industry sector is missing, infer the most likely baseline from the organization context, deployment market, data subjects, user location, and consequential-decision risk. Mark that inference as `assumed-baseline` and list what the organization must confirm. When legal/regulatory/framework coverage is in scope, read `legal-regulatory-map.md`.

When the user provides an organization profile such as Taiwan-registered, manufacturing/global marketing, information services, and not US-listed, read `applicability-profiles.md` and produce an applicability matrix before judging individual controls.

## Phase 2 - Organization Evidence Intake

Request the organization documents listed in `SKILL.md`. Build a document evidence index:

| Evidence ID | Document/System | Owner | Date/Version | Scope Fit | Notes |
|---|---|---|---|---|

If no organization documents are supplied, still create the inventory using a conservative baseline:

- general industry security practice,
- applicable country law or regulatory expectations for the likely operating jurisdiction,
- sector expectations for finance, healthcare, education, public sector, critical infrastructure, consumer SaaS, or other known sector,
- the system's data sensitivity and AI risk profile,
- framework/legal lenses such as NIST AI RMF, NIST AI 600-1, EU AI Act, GDPR, Taiwan PDPA/cybersecurity law, Colorado AI Act, or sector/state privacy rules when triggered by scope.
- log governance needs, including PII/secrets in logs, AI prompt/output/tool-call logs, retention/access controls, and incident evidence preservation.

Mark the expected requirement as `assumed-baseline`; mark the organization's actual implementation evidence as `missing-evidence` until documents or owner attestations are supplied.

## Phase 3 - Repository Evidence Collection

Inspect the repository for security and AI governance signals.

- Read README, docs, architecture, AGENTS, specs, deployment, CI/CD, auth, API, database, infra, logging, and test files.
- Search for policy-as-code, IaC, CI security jobs, secret scanning, dependency scanning, SAST, SBOM, signing, approval workflows, audit logs, data retention, privacy, log masking/redaction, model/data cards, prompt/tool safety, AI operation logging, and AI evaluation artifacts.
- If useful, run `scripts/collect_repo_evidence.sh` and read the generated files.

Repository evidence can prove that design/implementation hooks exist. It usually cannot prove that the organization operates the process.

## Phase 4 - Map Evidence to Minimum Control Areas

Use `minimum-control-map.md` to map each area to:

- organization evidence,
- repository evidence,
- external system evidence,
- missing evidence,
- status,
- remediation.

Use clause/control IDs as anchors, but do not quote or reproduce standard text beyond short labels.

## Phase 5 - Judge Implementation Posture

Classify each control area:

- `implemented`: repo and/or organization evidence shows the control is designed and operating for the stated scope.
- `external-implemented`: evidence shows the control is delegated to a named external system or provider with a defined owner and interface.
- `partial`: some design or evidence exists, but coverage, owner, operation, or audit trail is incomplete.
- `planned`: explicit plan exists but no implemented evidence.
- `missing-evidence`: no supplied evidence for implementation or operation.
- `not-applicable`: scope rationale is explicit and reasonable.
- `assumed-baseline`: requirement is inferred from industry/regulatory baseline, but the organization has not confirmed applicability or supplied evidence.

## Phase 6 - Produce Audit Inventory

Use `assets/audit-table-template.md`. Prioritize the backlog by:

1. controls needed for risk assessment and scope,
2. access/secrets/logging/incident basics,
3. PII/secrets-in-log, retention, and audit-trail integrity gaps,
4. AI inventory, data provenance, evaluation, oversight, and monitoring,
5. third-party responsibility gaps,
6. documentation and evidence freshness.

## Phase 7 - Caveats

Always include:

- `not a certification verdict`,
- evidence age and scope limitations,
- standards/source limitations,
- controls that require human/process proof outside the repo,
- external dependencies that need owner confirmation,
- any country/sector legal requirement that was assumed rather than verified from current official sources.
