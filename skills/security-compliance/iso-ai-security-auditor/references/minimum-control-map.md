# Minimum Control Map

This map is a compact internal-audit aid. It uses CNS 27001, CNS 27002, and CNS 42001 as local calibration sources, but it is not a substitute for the standards.

Local calibration sources used when this skill was authored:

- `temp/pdf-html/CNS27001-zh_TW.html`
- `temp/pdf-html/CNS27002-zh_TW.html`
- `temp/pdf-html/CNS42001-zh_TW.html`
- NIST AI RMF / NIST AI 600-1 official URLs listed in `legal-regulatory-map.md`
- Official legal/regulatory sources selected during the audit; start with `legal-regulatory-map.md` for EU AI Act, GDPR/ePrivacy, Taiwan, Colorado, EU cyber/product/digital-service overlays, US market triggers, and sector overlays.

Reference URLs are centralized in `legal-regulatory-map.md` under "Source URL Register".

When the user provides newer or official documents, prefer those over this summary.

## Jurisdiction and Industry Baseline

When organization documents are missing, use a conservative assumed baseline rather than stopping the audit. The assumed baseline should reflect:

- the country or region where the organization operates or serves users,
- applicable country law and regulator expectations for that jurisdiction,
- sector obligations such as finance, healthcare, education, public sector, critical infrastructure, or consumer SaaS,
- data sensitivity, especially personal data, credentials, payment data, regulated records, confidential business data, or safety-impacting AI outputs,
- whether the AI system makes or supports decisions about people.
- organization profile such as Taiwan-registered, manufacturing/global marketing, information services, and US-listed/not-US-listed status.

If country/sector law is material to the finding, verify current requirements from official or primary sources when possible. If not verified, label the row `assumed-baseline` and add an owner/legal-confirmation action.

For legal/regulatory controls, do not rely only on CNS/ISO management controls. Add law-specific evidence rows for notice, legal basis, data subject/consumer rights, impact assessments, high-risk AI classification, appeal/human review, public disclosure, reporting, breach/incident notification, cross-border transfer, and sector regulator obligations when applicable.

When the user provides a profile such as Taiwan-registered manufacturer / global marketer / information-service provider / not US-listed, read `applicability-profiles.md` before selecting law-specific rows.

## A. Management-System Foundation

Anchors: CNS 27001 clauses 4-10; CNS 42001 clauses 4-10.

| Area | Minimum Evidence | Repo Signals | Typical Gaps |
|---|---|---|---|
| Scope and context | ISMS/AIMS scope, boundaries, interested parties, legal/contract requirements | architecture docs, deployment docs, data-flow docs | repo exists but no system boundary or AI scope |
| Leadership and policy | security policy, AI policy, management commitment, policy review | policy docs, owner files, governance docs | policy exists but not tied to system scope |
| Roles and responsibilities | security owner, risk owner, AI owner, incident owner, data owner, supplier owner | CODEOWNERS, runbooks, escalation docs | no accountable owner for AI/model/data risks |
| Risk process | risk methodology, risk register, acceptance criteria, treatment plan | threat model, risk docs, issue log | threat model only, no organizational risk acceptance |
| Objectives and planning | security/AI objectives, measures, improvement plan | roadmap, KPIs, review artifacts | goals are generic and not measurable |
| Support and competence | training, awareness, competency records | onboarding docs, secure coding guide | no evidence of training or role competence |
| Document control | versioning, approval, retention, change control | docs versioned in git, review process | no approval/freshness evidence |
| Operation | operational controls, change/deploy process, access process | CI/CD, IaC, runbooks, release workflow | local scripts but no controlled production process |
| Performance evaluation | monitoring, internal audit, management review, metrics | dashboards, alerts, review reports | logs exist but no audit or management review |
| Improvement | corrective actions, nonconformity handling, lessons learned | issue log, postmortems, retro reports | bugs fixed but no corrective-action trail |

## B. Security Control Baseline

Anchors: CNS 27002 control themes: organizational, people, physical, technological controls; CNS 27001 Annex A control reference.

| Area | Minimum Evidence | Repo Signals | External-Control Examples |
|---|---|---|---|
| Asset and data inventory | information assets, owners, classification, data flows | schema docs, data catalog, migrations, storage config | CMDB, cloud inventory, data catalog |
| Acceptable use and handling | classification, labeling, transfer, retention, disposal | data handling docs, retention jobs | DLP, MDM, archive platform |
| Identity and access | IAM policy, MFA, least privilege, access review | auth code, RBAC tests, IAM IaC | IdP, SSO, PAM, cloud IAM |
| Secrets and cryptography | secret storage, key management, rotation, TLS | secret scanning config, KMS config, no committed secrets | KMS, Vault, cloud secrets manager |
| Secure SDLC | security requirements, code review, change control, dependency controls | tests, CI, SAST, dependency scan, SBOM | GitHub Advanced Security, Snyk, Dependabot |
| Vulnerability management | scanning, triage, patching SLA, exceptions | audit outputs, advisory files, CI gates | scanner, SOC, managed vulnerability service |
| Logging and monitoring | audit logs, event collection, alerting, retention, PII/secrets controls | structured logs, audit events, telemetry config, log redaction tests | SIEM, SOC, cloud logging |
| Incident management | reporting, response, decision, lessons learned | incident runbook, postmortems | ITSM, SOC playbooks |
| Supplier security | supplier inventory, agreements, monitoring, exit | provider docs, integration config | SOC reports, DPAs, vendor risk platform |
| Business continuity | backup, restore test, DR/BCP, availability objectives | backup scripts, restore tests, runbooks | cloud backup, managed DB backups |
| Privacy and legal requirements | legal register, PII/personal-data handling, privacy impact, contracts | privacy docs, consent flows, data minimization | DPO process, privacy tooling |

## C. AI Management and AI Security Baseline

Anchors: CNS 42001 clauses 4-10 and Annex A themes A.2-A.10; NIST AI RMF Govern, Map, Measure, Manage; NIST AI RMF trustworthiness characteristics; NIST AI 600-1 when generative AI is in scope.

| Area | Minimum Evidence | Repo Signals | Typical Gaps |
|---|---|---|---|
| AI inventory and scope | AI system inventory, role, intended use, users, lifecycle stage | model/prompt/tool docs, AI feature docs | AI use is embedded but undocumented |
| AI policy and objectives | AI policy, responsible AI objectives, review cadence | policy docs, eval requirements | broad principles without system-specific measures |
| AI roles and reporting | AI owner, data owner, model owner, human oversight owner, concern reporting | CODEOWNERS, runbooks, escalation paths | no owner for model behavior or data quality |
| NIST AI Govern | AI risk framework selection, accountability, risk tolerance, policy integration, independent review, residual-risk acceptance | governance docs, risk acceptance records, release gates | framework named but no owner, criteria, or acceptance evidence |
| NIST AI Map | context, intended use, affected stakeholders, impact scope, lifecycle stage, operating environment, foreseeable misuse | product docs, data-flow docs, architecture docs, threat model | no documented context for who can be harmed or how outputs are used |
| NIST AI Measure | evaluation/verification/validation against validity, reliability, safety, security, resilience, privacy, explainability, and fairness criteria | eval harness, test datasets, red-team reports, model release notes | only happy-path prompts tested; no bias, robustness, privacy, or misuse evaluation |
| NIST AI Manage | risk prioritization, treatment, monitoring, incident thresholds, rollback, human review, and improvement records | monitoring jobs, incident runbooks, feedback loops, issue backlog | risks identified but no treatment owner or operational monitoring |
| AI resources | data, tools, models, compute, people, provider inventory | model cards, dependency manifests, provider config | third-party model used without responsibility split |
| AI impact assessment | individual/group/social impact assessment, update criteria | assessment docs, risk notes | no impact assessment for user-facing AI |
| AI risk assessment/treatment | AI risk register, treatment controls, acceptance, residual risk | threat model, prompt injection mitigations | security-only review misses fairness/oversight/data risk |
| Responsible development | requirements, design, validation, deployment gates | eval harness, test datasets, model release notes | evals are ad hoc or prompt-only |
| AI lifecycle monitoring | production monitoring, drift/performance checks, incident thresholds | telemetry, evaluation jobs, feedback loops | no operational AI monitoring |
| Data governance for AI | source, rights, provenance, quality, preparation, retention | dataset cards, pipelines, privacy docs | training/test/prod data lineage absent |
| Transparency and stakeholder information | user docs, AI disclosure, limitations, reporting channel | UI copy, docs, terms, support workflow | users cannot report AI harm or appeal outputs |
| AI incident and external reporting | incident communication plan and obligations | runbooks, status page process | generic incident process lacks AI-specific triggers |
| Third-party AI controls | provider terms, DPAs, model/provider risk, exit strategy | provider SDK/config, vendor docs | provider controls assumed but not evidenced |
| Generative AI profile | NIST AI 600-1 risk/evidence profile for hallucination, information integrity, cybersecurity misuse, prompt injection/tool misuse, privacy leakage, provenance/disclosure, red-team testing, human review, abuse monitoring, and incident response | RAG evals, prompt/tool boundary tests, content filters, disclosure UI, abuse telemetry | generative AI shipped with no profile-specific risk register or eval evidence |

## D. Log Governance Baseline

Anchors: CNS 27001/27002 logging, monitoring, access control, privacy, incident, and evidence-retention themes; PDPA/GDPR breach and rights evidence when personal data is present; AI Act / NIST AI traceability when AI is in scope; sector and contract overlays when triggered.

| Area | Minimum Evidence | Repo Signals | Typical Gaps |
|---|---|---|---|
| Log inventory and purpose | inventory of application, access, admin, database, cloud, CI/CD, security, AI, support, and vendor logs with purpose and owner | logging config, observability docs, telemetry schemas | logs exist but no owner, purpose, or scope |
| PII/secrets minimization | rules preventing raw credentials, tokens, secrets, unnecessary PII, sensitive personal data, and confidential prompts from logs | redaction middleware, logger wrappers, tests, secret scan config | request/response bodies or prompts logged without masking |
| Retention and deletion | retention schedule, deletion/anonymization, legal hold, cross-border storage, customer contract fit | lifecycle policies, log retention IaC, storage config | indefinite retention or no deletion evidence |
| Access and integrity | least privilege, privileged access review, tamper resistance, time sync, trace IDs, immutable storage where needed | IAM/IaC, SIEM routing, audit event schema | many operators can read/export logs; no access review |
| Security audit trail | auth, RBAC, admin action, data export, configuration, deployment, incident, and vendor/support events | audit log code, event catalog, alerts | business-critical actions lack audit events |
| AI operation traceability | model/version, prompt template, retrieved sources, tool calls, policy decision, safety filter, human override, appeal/complaint | AI telemetry, eval traces, RAG source logs | AI outputs cannot be traced or reproduced |
| Incident evidence | alert, triage, containment, notification, corrective action, and preserved incident records | incident runbooks, postmortem refs, ticket links | breach facts cannot be reconstructed from retained evidence |

## E. Minimum "Good Enough For Internal Inventory" Set

If time is limited, cover these first:

1. Scope: what system and AI functions are in audit scope.
2. Asset/data/AI inventory: what is processed, where, by whom, and with which providers.
3. Risk: security risk and AI risk assessment with treatment owner.
4. Access/secrets: authentication, authorization, secrets, keys, and privileged access.
5. Secure SDLC: code review, dependency/vulnerability scanning, tests, deploy approval.
6. Logging/incident: audit logs, PII/secrets in logs, retention/access controls, monitoring, incident response, AI incident trigger.
7. AI lifecycle: intended use, data provenance/quality, evaluation, deployment, monitoring, human oversight.
8. Supplier: provider responsibility split and contractual/security evidence.
9. Evidence freshness: owner, date, version, and scope fit.
