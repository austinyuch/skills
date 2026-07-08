---
name: iso-ai-security-auditor
description: Use this skill when the user asks to inventory, audit, gap-check, or prepare internal audit evidence for repository security, cybersec, privacy, PII/personal-data protection, logging, regulatory, and AI governance against CNS/ISO 27001, CNS/ISO 27002, CNS/ISO 42001, NIST AI RMF, NIST AI 600-1 GenAI Profile, EU AI Act, GDPR/ePrivacy, Taiwan PDPA/cybersecurity law, CCPA/CPRA, US state privacy laws, Colorado AI Act, NIS2, EU Cyber Resilience Act, Digital Services Act, Data Act, HIPAA, GLBA, COPPA, FERPA, FCRA, ISMS, AI management systems, AI security, AI compliance, AI risk, SoA, internal audit, or minimum security/AI compliance requirements. This skill helps collect organization documents plus repo evidence, distinguish code-implemented controls from externally operated controls, and produce an audit-ready gap table; it is not a certification or legal verdict.
---

# ISO AI Security Auditor

Use this skill to run a lightweight internal-audit readiness inventory for Security, cybersec, PII/personal-data protection, privacy, logging, legal/regulatory, and AI governance. The goal is to help an organization see whether its system and provided documents cover the minimum expected control evidence inspired by CNS 27001, CNS 27002, CNS 42001, NIST AI RMF / GenAI Profile, and applicable law.

Do not present the result as certification, legal advice, or complete ISO/CNS conformity. Treat it as an evidence-based internal audit aid.

## Maintainer Source

This repository is the canonical maintainer source for the skill:
`aclab-code-review-private/.agents/skills/iso-ai-security-auditor`.

Global skill-home copies are published artifacts. Do not edit global copies directly; update this
repo-owned source, run the publisher, and let `scripts/publish_code_review_skill.py` distribute the
refreshed copy to global skill homes.

## Start Here

1. Read `references/audit-workflow.md`.
2. Read `references/minimum-control-map.md`.
3. Read `references/legal-regulatory-map.md` when jurisdiction, privacy, AI law, consumer protection, employment, healthcare, finance, education, public sector, or consequential-decision compliance is in scope.
4. Read `references/applicability-profiles.md` when the user gives an organization profile such as Taiwan-registered, manufacturing/global marketing, information services, US-listed/not-US-listed, or other market/sector facts.
5. If auditing a repository, read `references/repo-evidence-patterns.md`.
6. If the user wants a durable report, use `assets/audit-table-template.md`.
7. Optionally run `scripts/collect_repo_evidence.sh <repo> <output-dir>` to collect search evidence before judging.

## Required Inputs

Ask for these inputs when missing. If the user cannot provide them, continue with a clear `assumed-baseline` for expected requirements and `missing-evidence` for implementation proof.

- Target repository path and system scope.
- Jurisdiction/country, industry sector, markets served, product/service type, and public-company/reporting status. If absent, infer a conservative baseline from the operating context and mark it `assumed-baseline`.
- Organization documents: ISMS/AI scope, policies, risk methodology, risk register, Statement of Applicability or equivalent, asset and data inventory, AI system inventory, supplier/outsourcing records, incident process, access control policy, SDLC/change process, logging/monitoring evidence, BCP/backup evidence, training/awareness records, internal audit/management review records.
- Regulatory evidence: PII/personal-data inventory, legal basis / legitimate purpose analysis, privacy notices, data subject or consumer rights process, DPIA/PIA, AI impact assessment, high-risk AI classification, consumer notice/appeal process, cross-border transfer assessment, breach/incident notification playbook, sector regulator obligations, and counsel/owner signoff.
- AI-specific documents when applicable: AI policy, AI roles/responsibilities, AI use-case register, model/data cards, dataset provenance, data quality criteria, NIST AI RMF profile or equivalent AI risk framework mapping, AI impact assessment, AI risk assessment/treatment, human oversight plan, evaluation/validation records, deployment/monitoring plan, incident/appeal/reporting channel, third-party/model provider responsibilities.
- Log governance evidence: log inventory, retention schedule, access review, masking/redaction rules, PII/secrets-in-log review, audit trail integrity, SIEM/alert routing, incident evidence preservation, AI prompt/output/tool-call logging policy, and vendor log storage/location.
- External-control evidence: cloud provider controls, IdP/MFA, SIEM/SOC, MDM, ticketing/ITSM, CI/CD security platform, DLP, vulnerability scanner, model provider controls, data processing agreements, SLAs, or SOC/ISO reports.

## Evidence Rules

- Base every status on observed documents, repo files, commands, or explicit user-provided evidence.
- If organization documents are absent, do not stop. Build a conservative `assumed-baseline` using general industry practice plus applicable country/sector regulatory expectations; mark those requirements as assumptions needing organization or legal confirmation.
- When applying country or sector regulation, verify current requirements from official or primary sources when available. If not verified, state that the legal/regulatory mapping is unverified.
- Treat legal/regulatory coverage as a compliance inventory, not legal advice. Prefer official law/regulator sources and record the checked date.
- Treat NIST AI RMF and NIST AI 600-1 as framework/profile baselines, not legal mandates by themselves unless adopted by contract, policy, regulator, or applicable law.
- Treat public-company-only rules such as SEC cybersecurity disclosure and SOX ITGC as `not-applicable` or watch-list unless public listing, reporting, IPO readiness, group audit, or contract evidence triggers them.
- Mark outsourced or platform controls as `external-implemented` only when the owner, system, interface, and evidence are named.
- Mark planned work as `planned`, not `implemented`.
- Mark absent or unprovided evidence as `missing-evidence`, not failure by default.
- Separate repository design evidence from organization-process evidence. Code alone cannot prove management-system operation.
- Call out overclaim risk when README/docs imply a control exists but no repo or organization evidence supports it.

## Output Contract

Return a concise internal-audit inventory with these sections:

1. Scope and inputs reviewed.
2. Executive gap summary.
3. Control inventory table.
4. Repository evidence findings.
5. Organization-document gaps.
6. External-control dependency table.
7. Priority remediation backlog.
8. Residual risk and audit caveats.

Use status values only from:

- `implemented`
- `external-implemented`
- `partial`
- `planned`
- `missing-evidence`
- `not-applicable`
- `assumed-baseline`

## Composition

For code-level security findings, compose with `security-review`. For architecture documentation gaps, compose with `system-architect`. For formal spec/governance changes in this repo, route through `spec-master`.
