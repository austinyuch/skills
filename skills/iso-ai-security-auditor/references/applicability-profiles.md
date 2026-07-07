# Applicability Profiles

Use this reference after `legal-regulatory-map.md` when the organization profile is known. These profiles are routing aids, not legal advice.

## Profile: Taiwan-Registered Organization, Manufacturing Global Marketing, Information Services, Not US Public Company

Apply this profile when the user states or the evidence suggests:

- the organization is registered or established in Taiwan,
- the organization is a manufacturer marketing or selling globally,
- the organization also provides information services, SaaS, platform, API, data-processing, system-integration, managed service, or AI-enabled service,
- the organization is not listed in the United States and is not an SEC reporting company.

### Default Baseline

Treat these as default audit lenses unless the user or counsel excludes them:

| Lens | Why It Applies | Minimum Evidence |
|---|---|---|
| Taiwan PDPA | Taiwan organization, employees, customers, suppliers, website leads, marketing contacts, support records, telemetry, and logs may contain personal data | personal-data inventory, collection/use purpose, notice, consent or lawful basis, rights process, retention/deletion, breach notification, commissioned-party supervision, cross-border transfer review |
| Taiwan cybersecurity trigger check | General private organizations may not have full Cyber Security Management Act duties, but critical infrastructure, specific non-government agencies, public-sector suppliers, and regulated-sector entities need screening | designation/sector memo, government/customer cybersecurity clauses, maintenance plan if covered, CISO/security owner if covered, incident reporting path |
| CNS/ISO security and AI management baseline | Useful internal-control baseline for Taiwan and customer audits | ISMS/AIMS scope, risk register, SoA/equivalent, policy, roles, internal audit, management review, corrective actions |
| NIST AI RMF / NIST AI 600-1 | Practical cross-sector AI risk framework for manufacturing AI, quality inspection, forecasting, GenAI, RAG, agents, and AI-enabled information services | AI inventory, AI risk framework mapping, Govern/Map/Measure/Manage evidence, GenAI profile evidence when applicable |
| Log governance | Logs often contain PII, secrets, security events, AI prompts/outputs, and incident evidence | log inventory, PII/secrets masking, access control, retention/deletion, tamper resistance, incident timeline, AI operation log policy |

### Manufacturing and Global Marketing Triggers

Add these lenses when facts trigger them:

| Lens | Trigger | URL |
|---|---|---|
| GDPR | EU/EEA individuals are targeted, monitored, sold to, supported, tracked, or included in CRM/marketing/support data | `https://eur-lex.europa.eu/eli/reg/2016/679/oj` |
| EU ePrivacy / cookie rules | EU website visitors, cookies, tracking pixels, email/SMS marketing, or electronic communications metadata | `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32002L0058` |
| EU AI Act | AI system is placed on the EU market, put into service in the EU, used by EU deployers, embedded in products, or outputs are used in the EU | `https://eur-lex.europa.eu/eli/reg/2024/1689/oj` |
| EU Cyber Resilience Act | connected hardware, software, IoT, device-management software, edge product, firmware, or product with digital elements is sold into the EU | `https://eur-lex.europa.eu/eli/reg/2024/2847/oj` |
| EU NIS2 | EU establishment or covered EU customer/sector dependency exists; manufacturer is in a covered critical-product supply chain or digital infrastructure context | `https://eur-lex.europa.eu/eli/dir/2022/2555/oj` |
| EU Data Act | connected product or related service generates user/product usage data, or cloud/data-switching obligations are relevant | `https://eur-lex.europa.eu/eli/reg/2023/2854/oj` |
| Product safety / product liability | AI or software affects physical safety, machinery, vehicles, medical devices, industrial control, or consumer products | verify sector-specific EU/Taiwan/customer requirements |

### Information Services Triggers

Add these lenses when facts trigger them:

| Lens | Trigger | URL |
|---|---|---|
| NIS2 digital services | managed service provider, managed security service provider, cloud, data center, DNS, CDN, trust service, online marketplace, search, or social platform exposure in the EU | `https://digital-strategy.ec.europa.eu/en/policies/nis2-directive` |
| EU Digital Services Act | hosting, marketplace, user-generated content, search, content moderation, notice-and-action, or public platform functions | `https://eur-lex.europa.eu/eli/reg/2022/2065/oj` |
| CCPA/CPRA | California residents and statutory business thresholds or sale/share/sensitive personal information triggers are present | `https://oag.ca.gov/privacy/ccpa` |
| Colorado Privacy Act | Colorado consumers, controller/processor duties, sensitive data, targeted advertising, sale, or profiling | `https://coag.gov/resources/colorado-privacy-act/` |
| Colorado AI Act | high-risk AI used for consequential decisions involving Colorado consumers | `https://leg.colorado.gov/bills/sb24-205` |
| FTC privacy/security and AI claim risk | US consumers, public privacy/security claims, AI claims, unfair/deceptive practice risk, or data-security commitments | `https://www.ftc.gov/business-guidance/privacy-security` |
| China PIPL / DSL / CSL / GenAI Measures | mainland China users, China operations, China personal information, important data, network products/services, or public GenAI services | `https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm` |

### Deprioritized Unless Triggered

Do not include these as default findings for this profile unless evidence triggers them:

| Lens | Default Treatment |
|---|---|
| SEC cybersecurity disclosure rules | `not-applicable` or watch-list because the organization is not US-listed or an SEC reporting company |
| SOX ITGC | `not-applicable` unless US public-company reporting, IPO readiness, group audit, or customer contract requires it |
| HIPAA | trigger only for protected health information / covered entity / business associate context |
| GLBA | trigger only for financial institution customer information or financial-service activity |
| FERPA / COPPA | trigger only for student records, education services, or children under relevant age thresholds |
| FCRA | trigger only for consumer reports, eligibility, credit, employment, insurance, tenant screening, or similar decisions |
| PCI DSS | trigger when payment card data is stored, processed, transmitted, or contractually in scope |
| EU DORA | trigger for EU financial entities or ICT third-party providers to EU financial entities |

## Log Governance Lens

Apply this lens whenever application, infrastructure, security, analytics, support, AI, or audit logs exist.

Check at least:

- log inventory: application, access, admin, database, cloud, CI/CD, security, AI prompt/output/tool-call, retrieval, support, and vendor logs,
- PII/secrets minimization: no raw passwords, tokens, credentials, unnecessary PII, sensitive personal data, confidential prompts, or customer secrets,
- masking and redaction: deterministic rules for common identifiers and prompt/output data,
- purpose and retention: retention schedule aligned to PDPA/GDPR/contract/security needs; deletion or anonymization path,
- access control: least privilege, break-glass, review, segregation of duties, and vendor support access,
- integrity: tamper resistance, clock sync, trace ID, immutable or append-only storage where needed,
- incident evidence: breach timeline, alert, triage, containment, notification evidence, and preserved records,
- AI operation traceability: model/version, prompt template, retrieved sources, tool calls, policy decisions, human override, appeal/complaint, and safety filter result,
- cross-border and vendor handling: log storage region, processor/subprocessor contract, and customer DPA/security addendum.

Classify log controls as `implemented` only when both design and operational evidence exist. If logs exist but PII/secrets handling, retention, or access review is unclear, mark `partial` or `missing-evidence`.
