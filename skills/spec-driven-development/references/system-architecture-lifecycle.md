# System Architecture Document Lifecycle

Use this reference when a project is starting, when Phase 2 design changes system shape, or when project review needs to explain the system to humans.

## Purpose

Maintain one lightweight system architecture narrative that survives across specs without turning SDD into waterfall planning. The steering architecture documents are communication and coherence artifacts; branch specs remain the change authority. Use `system-architect` as the dedicated authoring and maintenance skill when the repo needs actual `.agents/steering/{product,tech,structure}` markdown/HTML creation, refresh, stale-doc review, or code-review architecture context packets.

When a spec has AI, security, privacy, PII/personal-data, logging, external-control, or regulatory-compliance scope, compose with `iso-ai-security-auditor` so architecture docs capture the relevant data flows, trust boundaries, AI component boundaries, log/telemetry flows, external-control dependencies, and missing evidence. This is an architecture evidence lens, not certification or legal advice.

## SAA Good Parts, Agile Boundary

Adopt only the useful parts of IBM Systems Application Architecture:

- **Common user access idea**: name shared interaction patterns, user-facing conventions, and workflow vocabulary so product, design, QA, and engineering use the same words.
- **Common programming interface idea**: describe stable contracts, APIs, events, data models, extension points, and compatibility expectations.
- **Common communications support idea**: describe service-to-service communication, integration protocols, auth boundaries, observability signals, and failure handoffs.
- **Cross-platform consistency idea**: make portability, deployment contexts, and agent/runtime boundaries explicit where they matter.

Do not adopt SAA as a heavyweight enterprise blueprint. Avoid big upfront completeness, platform monoculture, or large canonical taxonomies that are not needed for the current slice. Apply the Ponytail/YAGNI ladder before adding new architecture sections.

## Canonical Artifacts

Prefer Kiro-like steering markdown source plus generated or hand-maintained HTML:

- Product steering: `.agents/steering/product.md` and `.agents/steering/product.html`
- Technical steering: `.agents/steering/tech.md` and `.agents/steering/tech.html`
- Structure steering: `.agents/steering/structure.md` and `.agents/steering/structure.html`
- Optional evidence map: `.agents/steering/assets/evidence-map.json`
- Legacy/equivalent input: `docs/architecture.md` or `docs/architecture/index.html`
- Spec-local architecture deltas: `{spec-directory}/design.md`

If a repo already has an equivalent architecture path, keep the existing path and record it in `docs/PROJECT_REVIEW_GUIDE.md`, `AGENTS.md`, or the active spec design. Do not create a duplicate architecture surface.

## Authority Model

- `requirements.md`: business need and acceptance criteria.
- `design.md`: spec-local design truth, architecture deltas, contracts, FMEA, and decisions for the current change.
- `system-architect`: workflow owner for cross-spec architecture document creation, refresh, challenge questions, and code-review context packets.
- `.agents/steering/{product,tech,structure}.md`: human-readable system architecture steering snapshots synthesized from current accepted design sources.
- `.agents/steering/{product,tech,structure}.html`: stakeholder-friendly rendering of the same-name markdown source.
- `review.md`: checks whether the architecture docs exist, are current enough for the slice, and accurately reflect implemented evidence.
- `SPECS.md` / `RTM.md`: derived registry and traceability snapshots only.

Never let architecture HTML or RTM invent requirements, readiness verdicts, or contract truth. If a project review finds drift, update upstream spec/design/review evidence first, then regenerate the architecture snapshot.

## Minimum Architecture Content

Keep first-slice architecture documents short. Include only sections that are supported by current evidence:

1. System context and user/operator audiences.
2. Major modules, services, agents, data stores, and external systems.
3. Common user access / workflow conventions when the product has repeated user flows.
4. Common programming interfaces: API, event, schema, MCP/tool, or adapter contract summary with source refs.
5. Common communications: protocol, auth/session boundary, queues/jobs, observability, and failure handoff.
6. Runtime/deployment topology at the level of service responsibilities, not guessed live ports.
7. Data and trust boundaries, including secrets and PII handling.
8. AI/security/privacy/log compliance boundaries when in scope: AI components, model/provider interfaces, PII flows, log retention/redaction assumptions, audit trails, external-control owners, and `iso-ai-security-auditor` evidence refs.
9. Cross-spec decision log: only decisions that are hard to reverse, surprising, or likely to affect multiple specs.
10. Evidence and freshness: source specs, review refs, last reviewed date, and known gaps.

## Lifecycle Hooks

- **Project start / Phase 1**: decide whether a system architecture doc is needed now. Create only a placeholder if the project has no stable architecture evidence yet.
- **Phase 2 design**: when the design changes module boundaries, shared contracts, runtime topology, or communication patterns, add an "Architecture Documentation Impact" section to `design.md`.
- **Phase 2 design with compliance scope**: if `iso-ai-security-auditor` applies, add the design-time architecture implications from its inventory to the "Architecture Documentation Impact" section without claiming implementation or legal readiness.
- **Phase 3 tasks**: plan a task to update steering markdown and HTML docs when the design impact is material, stakeholder-facing, or compliance-relevant.
- **Phase 4 implementation**: use `system-architect` to update architecture docs after upstream code/spec evidence exists; do not document planned work as executed.
- **Phase 5 review**: use `system-architect` to evaluate whether architecture docs are missing, stale, overclaiming, or inconsistent with `design.md` / `review.md`. If missing and needed, create or schedule them.
- **Project review**: consume architecture markdown/HTML as communication input, but claim-cap it against `review.md`, `SPECS.md`, and evidence metadata.

## Review Outcomes

Use one of these states:

- `current`: architecture docs match accepted design and evidence for the reviewed slice.
- `needs_update`: docs exist but omit material accepted changes or still describe retired components.
- `missing_but_required`: no architecture doc exists and the project has enough stable evidence to justify one.
- `not_yet_required`: project is too small, prototype-only, or has insufficient stable evidence.
- `stale_or_overclaiming`: docs present planned, mock-backed, or historical behavior as current executed truth.

`stale_or_overclaiming` must downgrade project review language and should create a concrete follow-up task or issue.
