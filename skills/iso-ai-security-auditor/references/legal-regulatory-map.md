# Legal and Regulatory Map

Use this reference when the audit scope includes privacy, AI law, consumer protection, consequential decisions, cross-border data, regulated sectors, or country-specific obligations.

This is a routing and evidence map, not legal advice. Laws change. For current obligations, verify official or primary sources during the audit and record the checked date.

## Source URL Register

| Regime | Official / Primary URL | Use |
|---|---|---|
| NIST AI Risk Management Framework | `https://www.nist.gov/itl/ai-risk-management-framework` | cross-sector AI risk management baseline and official entry point |
| NIST AI RMF 1.0 | `https://doi.org/10.6028/NIST.AI.100-1` | AI trustworthiness characteristics and Govern/Map/Measure/Manage functions |
| NIST AI RMF Playbook | `https://airc.nist.gov/airmf-resources/playbook/` | implementation questions/actions for AI RMF outcomes |
| NIST AI 600-1 GenAI Profile | `https://doi.org/10.6028/NIST.AI.600-1` | generative AI profile for AI RMF risks and actions |
| EU AI Act | `https://eur-lex.europa.eu/eli/reg/2024/1689/oj` | AI role, prohibited/high-risk/GPAI/transparency/post-market obligations |
| GDPR | `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679` | personal-data processing, controller/processor, rights, security, DPIA, breach, transfers |
| EU ePrivacy Directive | `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32002L0058` | cookies, tracking, electronic communications confidentiality, direct marketing |
| EU NIS2 Directive | `https://eur-lex.europa.eu/eli/dir/2022/2555/oj` | EU cybersecurity risk management and incident reporting for covered sectors/entities |
| EU Cyber Resilience Act | `https://eur-lex.europa.eu/eli/reg/2024/2847/oj` | cybersecurity obligations for products with digital elements placed on the EU market |
| EU Digital Services Act | `https://eur-lex.europa.eu/eli/reg/2022/2065/oj` | hosting, platforms, marketplaces, search, content governance, notice/action |
| EU Data Act | `https://eur-lex.europa.eu/eli/reg/2023/2854/oj` | connected product data, related services, data access/sharing, cloud switching |
| EU DORA | `https://eur-lex.europa.eu/eli/reg/2022/2554/oj` | EU financial-sector ICT risk, incident reporting, resilience testing, third-party risk |
| Taiwan Personal Data Protection Act | `https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=I0050021` | Taiwan personal-data collection, processing, use, security, notification, cross-border transfer |
| Taiwan Cyber Security Management Act | `https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=A0030297` | Taiwan public-sector, critical-infrastructure, and specific non-government cybersecurity duties |
| FTC privacy and security guidance | `https://www.ftc.gov/business-guidance/privacy-security` | US consumer privacy/security and unfair/deceptive practice claim-risk baseline |
| California CCPA / CPRA | `https://oag.ca.gov/privacy/ccpa` | California personal information, sensitive personal information, consumer rights, notices, opt-out, deletion/correction |
| California Privacy Protection Agency regulations | `https://cppa.ca.gov/regulations/` | current CCPA/CPRA regulations and rulemaking |
| Colorado Privacy Act | `https://coag.gov/resources/colorado-privacy-act/` | Colorado consumer personal-data rights and controller obligations |
| Colorado SB24-205 / Colorado AI Act | `https://leg.colorado.gov/bills/sb24-205` | high-risk AI, consequential decisions, algorithmic discrimination, notice, impact assessment, review |
| Virginia Consumer Data Protection Act | `https://law.lis.virginia.gov/vacodefull/title59.1/chapter53/` | Virginia consumer personal-data rights and controller/processor duties |
| HIPAA Privacy/Security Rules | `https://www.hhs.gov/hipaa/for-professionals/index.html` | US protected health information privacy/security duties |
| FTC GLBA resources | `https://www.ftc.gov/business-guidance/privacy-security/gramm-leach-bliley-act` | US financial institution customer information safeguards and privacy duties |
| FTC COPPA Rule | `https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa` | US children's online personal information under 13 |
| US Department of Education FERPA | `https://studentprivacy.ed.gov/ferpa` | US student education records privacy |
| FTC FCRA resources | `https://www.ftc.gov/legal-library/browse/statutes/fair-credit-reporting-act` | US consumer report / credit reporting data duties |
| SEC cybersecurity disclosure rules | `https://www.sec.gov/newsroom/press-releases/2023-139` | US public-company cybersecurity governance, risk management, strategy, and incident disclosure |
| PCI Security Standards | `https://www.pcisecuritystandards.org/standards/` | payment-card contractual/security baseline including logging and access-control expectations |
| China GenAI Interim Measures | `https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm` | China public generative AI service trigger lead; verify China PIPL/DSL/CSL separately when in scope |
| Taiwan law database search | `https://law.moj.gov.tw/ENG/` | verify whether newer Taiwan AI-specific laws or sector rules apply |
| EUR-Lex search | `https://eur-lex.europa.eu/` | verify EU adjacent laws and current consolidated text |

## Source Priority

1. Official law text or regulator guidance.
2. Organization counsel/compliance memo with date and scope.
3. Sector regulator instructions.
4. Reputable secondary summaries only as leads, never as final authority.

## Default Legal Baseline Selection

If documents are missing, infer a baseline from:

- where the organization is established,
- where users/data subjects/consumers are located,
- where the service is offered,
- whether the system makes or materially supports consequential decisions,
- whether personal, sensitive, biometric, health, financial, children's, employment, education, housing, insurance, government service, or legal-service data is processed,
- whether the organization is public sector, critical infrastructure, financial, healthcare, education, insurance, or employment-related.
- whether products with digital elements, connected products, hosted platforms, managed services, cloud/data services, or public GenAI services are offered in regulated markets,
- whether public-company, financial reporting, payment-card, government procurement, or customer-contract obligations apply.

Mark inferred legal requirements as `assumed-baseline` until confirmed.

If the organization is Taiwan-registered, globally markets manufactured products, provides information services, and is not US-listed, also read `applicability-profiles.md`.

## NIST AI RMF Lens

Official sources:

- NIST AI Risk Management Framework official entry point: `https://www.nist.gov/itl/ai-risk-management-framework`
- NIST AI RMF 1.0: `https://doi.org/10.6028/NIST.AI.100-1`
- NIST AI RMF Playbook: `https://airc.nist.gov/airmf-resources/playbook/`
- NIST AI 600-1, Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile: `https://doi.org/10.6028/NIST.AI.600-1`

Use as a cross-sector AI risk-management baseline when AI systems, models, RAG, copilots, autonomous agents, automated decision support, or generative AI are in scope. NIST AI RMF is a voluntary framework/profile baseline by itself; classify it as a legal or contractual requirement only when adopted by law, regulator guidance, procurement, customer contract, internal policy, or board-approved risk framework.

Check at least:

- AI governance: policies, roles, accountability, risk tolerance, escalation, independent review, and risk acceptance,
- AI inventory and context: intended purpose, users, affected stakeholders, lifecycle stage, operating environment, foreseeable misuse, and system boundaries,
- trustworthy AI characteristics: valid/reliable, safe, secure/resilient, accountable/transparent, explainable/interpretable, privacy-enhanced, and fair/bias-managed,
- AI RMF core functions: Govern, Map, Measure, and Manage with owners, evidence, and residual-risk decisions,
- test/evaluation/verification/validation records, including security, privacy, performance, robustness, bias/fairness, human oversight, and incident thresholds,
- monitoring and change management for model, data, prompt, retrieval, tool, and provider changes,
- third-party AI/provider responsibility split, terms, data-processing controls, logging, retention, and exit/rollback strategy.

When generative AI is in scope, also apply NIST AI 600-1 as a profile. Check for evidence around generated-content risks, hallucination and information integrity, harmful or illegal content, cybersecurity misuse, prompt injection and tool misuse, privacy and confidential-data leakage, provenance/watermarking or disclosure where applicable, red-team/evaluation records, human review, user reporting, abuse monitoring, and incident response.

Evidence examples: AI RMF crosswalk, AI risk framework selection memo, AI use-case register, model/data cards, impact assessments, evaluation reports, red-team reports, telemetry/monitoring dashboards, incident playbooks, provider responsibility matrix, and residual-risk acceptance records.

## EU AI Act Lens

Official source: Regulation (EU) 2024/1689, EUR-Lex: `https://eur-lex.europa.eu/eli/reg/2024/1689/oj`

Use when AI systems are placed on the EU market, put into service in the EU, used by EU deployers, or outputs are used in the EU. Check at least:

- role: provider, deployer, importer, distributor, product manufacturer, authorized representative, GPAI model provider,
- AI system inventory and intended purpose,
- prohibited-practice screening,
- high-risk classification and Annex/category trigger,
- risk management, data governance, technical documentation, logging, transparency, human oversight, accuracy/robustness/cybersecurity,
- post-market monitoring and serious incident handling,
- GPAI/model-provider obligations when foundation/general-purpose models are used or provided,
- deployer notices, human oversight, input data governance, and monitoring obligations.

Evidence examples: AI inventory, role classification memo, high-risk assessment, technical documentation, model/data governance, logs, monitoring, incident process, user instructions, provider/deployer responsibility split.

## GDPR Lens

Official source: Regulation (EU) 2016/679, EUR-Lex: `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679`

Use when personal data of people in the EU/EEA is processed or EU establishment/targeting/monitoring may apply. Check at least:

- controller/processor role and processing register,
- lawful basis and purpose limitation,
- notice/transparency and data subject rights,
- special-category data and children data handling,
- data minimization, retention, accuracy, security, and access controls,
- processor agreements and subprocessor management,
- cross-border transfer mechanism,
- breach detection/notification playbook,
- DPIA and automated decision-making/profiling review when applicable.

Evidence examples: ROPA, privacy notice, DPA, DPIA, consent/legal-basis matrix, retention schedule, rights request process, breach runbook, transfer impact assessment.

## PII / Personal Data Protection Lens

Use this lens whenever the system processes information that identifies, relates to, describes, can be associated with, or can reasonably be linked to a person, household, account, device, student, patient, consumer, employee, applicant, child, or other data subject.

At minimum, check PII/personal-data inventory, data-flow map, data categories, sensitive-data flags, data subject location, controller/processor/service-provider role, collection notice, purpose, legal basis, rights workflow, sale/share/targeted-advertising/profiling flags, retention/deletion, security measures, breach notification, cross-border transfer, and vendor/subprocessor contracts.

Common overlays include CCPA/CPRA, Colorado Privacy Act, Virginia CDPA, HIPAA, GLBA, COPPA, FERPA, and FCRA. Treat applicability as `assumed-baseline` until jurisdiction, sector, data subjects, and counsel/owner confirmation are known.

## Log Governance Lens

Use this lens whenever system, security, analytics, support, AI, or audit logs are collected. Logs can be evidence for security and incident response, but they can also create privacy, secrecy, cross-border, and retention risk.

Check at least:

- log inventory covering application, access, admin, database, cloud, CI/CD, security, AI prompt/output/tool-call, retrieval, support, and vendor logs,
- PII, sensitive personal data, credentials, tokens, secrets, confidential prompts, customer data, and regulated records in logs,
- masking/redaction rules, retention/deletion, legal hold, and anonymization/pseudonymization,
- access control, privileged access review, vendor/support access, SIEM/SOC routing, and tamper resistance,
- security audit trail coverage for authentication, authorization, admin actions, data export, configuration changes, incident handling, and AI/model/provider changes,
- AI traceability fields: model/version, prompt template, retrieved sources, tool calls, policy decision, human override, appeal/complaint, and safety filter result,
- breach/incident record preservation and notification evidence.

Use law-specific overlays when triggered: PDPA/GDPR breach and rights evidence, EU AI Act high-risk logging, PCI DSS payment-card logging, HIPAA audit controls, NYDFS/financial logging, DORA/NIS2 incident evidence, and customer contract retention/security commitments.

## EU Cyber / Product / Digital-Service Lenses

Use these as conditional overlays for global manufacturing and information services:

- **ePrivacy**: EU cookies, tracking pixels, electronic marketing, or communications metadata.
- **NIS2**: covered EU sectors/entities, managed services, managed security services, cloud/data center/DNS/CDN/trust services, marketplaces, search, social platforms, or critical manufacturing/product supply-chain triggers.
- **Cyber Resilience Act**: products with digital elements, connected hardware/software, IoT, firmware, device-management software, or other digital products placed on the EU market.
- **Digital Services Act**: hosting, marketplaces, user-generated content, online platforms, search, notice/action, content moderation, or trader traceability.
- **Data Act**: connected product data, related services, user access to generated data, data sharing, or cloud/data-processing service switching.
- **DORA**: EU financial entity or ICT third-party provider to EU financial entities.

For each triggered lens, record applicability rationale, role, affected product/service, EU market touchpoint, required evidence, and owner.

## US Public-Company Exclusion and US Market Triggers

If the organization is not listed in the United States and is not an SEC reporting company, classify SEC cybersecurity disclosure and SOX ITGC as `not-applicable` or watch-list unless IPO readiness, parent-company reporting, group audit, lender requirement, or customer contract evidence says otherwise.

US market activity can still trigger non-public-company privacy, cyber, or AI lenses. Check CCPA/CPRA, Colorado Privacy Act, Colorado AI Act, FTC privacy/security claim risk, sector laws, and payment-card obligations based on users, consumers, data, transaction type, and thresholds.

## Taiwan Lens

Official sources:

- Personal Data Protection Act, Laws & Regulations Database of the Republic of China (Taiwan): `https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=I0050021`
- Cyber Security Management Act, Laws & Regulations Database of the Republic of China (Taiwan): `https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=A0030297`

Use when the organization operates in Taiwan, serves Taiwan data subjects, is a Taiwan public agency, is designated critical infrastructure/specific non-government agency, or handles Taiwan personal data. Check at least:

- PDPA collection/processing/use purpose and legal basis,
- notice to data subjects and rights handling,
- sensitive personal data handling,
- security and maintenance measures for personal data files,
- incident/breach notification and response records,
- cross-border transfer restrictions,
- processor/commissioned-party supervision,
- for covered public/specific non-government agencies: cybersecurity responsibility level, maintenance plan, dedicated personnel/CISO, reporting, audit, drills, and outsourcing controls.

Taiwan AI-specific laws or binding AI regulations must be verified from official sources during the audit. If no official enacted law is available, treat AI-specific Taiwan requirements as `assumed-baseline` from CNS 42001, sector guidance, PDPA, cybersecurity law, and organization policy.

## Colorado AI Act Lens

Official source: Colorado SB24-205, Consumer Protections for Artificial Intelligence: `https://leg.colorado.gov/bills/sb24-205`

Use when doing business in Colorado and developing, deploying, or making available high-risk AI systems or consumer-facing AI interactions. Check at least:

- developer vs deployer role,
- high-risk system and consequential decision scope,
- algorithmic discrimination risk management,
- impact assessment,
- annual deployment review,
- consumer notice, correction, appeal, and human review process where applicable,
- public statement on high-risk AI systems and risk management,
- disclosure that a consumer is interacting with AI,
- attorney general disclosure/reporting triggers,
- recognized AI risk management framework evidence when used as a defense posture.

Evidence examples: high-risk AI register, impact assessments, consumer notice/appeal workflows, public statement, annual review record, discrimination testing, incident/reporting playbook.

## Other Laws and Sector Overlays

Add additional lenses when facts trigger them. Common examples:

- US state privacy laws: California CCPA/CPRA, Colorado Privacy Act, Virginia, Connecticut, Utah, Texas, Oregon, and similar state laws.
- US sector laws: HIPAA, GLBA, FCRA, COPPA, FERPA, employment and housing discrimination laws.
- EU adjacent laws: ePrivacy, NIS2, Cyber Resilience Act, Digital Services Act, Data Act, DORA, product safety/liability rules.
- Taiwan sector rules: financial, medical, telecom, public-sector, critical infrastructure, outsourcing, and cross-border data rules.
- China overlays: PIPL, Data Security Law, Cybersecurity Law, and generative AI/service-specific rules when China users, operations, data, important data, or public GenAI services are in scope.
- Contractual obligations: customer DPAs, enterprise security addenda, procurement security requirements, SOC/ISO commitments, model-provider terms.

For each overlay, record: source, applicability trigger, evidence needed, owner, and confidence.
