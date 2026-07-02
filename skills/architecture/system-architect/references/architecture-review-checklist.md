# Architecture Review Checklist

Use this to challenge architecture before or after writing `.agents/steering/product.md`, `.agents/steering/tech.md`, and `.agents/steering/structure.md`.

## Scope and Minimality

- Do these steering docs need to exist now?
- What existing component, spec, or platform capability already solves part of the problem?
- Can the current project slice be supported with fewer new services, abstractions, or dependencies?
- Is a proposed abstraction carrying real policy/lifecycle/security/domain boundaries, or just naming?

## Reversibility

- Which decisions are one-way doors?
- Which are two-way doors?
- Is the rollout incremental: feature flag, adapter, strangler, canary, or compatibility layer?
- Is rollback described for data, API, runtime, and user-facing changes?

## Blast Radius

- Which modules/services/data stores/users are affected if the design is wrong?
- Which files/components are high fan-in or high fan-out?
- Which external contracts can drift?
- Are cross-spec impacts recorded in `SPECS.md` / active spec design?

## Failure and Operations

- What happens on nil/empty/error paths?
- What does an operator see at 3am?
- Are logs, metrics, traces, alerts, and dashboards in scope or explicitly out of scope?
- Is there an authoritative handoff path for external execution or runtime proof?

## SAA Good Parts

- Common User Access: are workflow terms and journeys consistent?
- Common Programming Interface: are contracts named, versioned, and owned?
- Common Communications Support: are protocols, auth/session, retries, queues, and failure handoffs clear?
- Cross-platform consistency: are runtime assumptions and portability limits explicit?

## Source Consistency

- Do steering markdown files match accepted `design.md` and `review.md`?
- Do same-name steering HTML files match markdown?
- Are stale diagrams or old module names still present?
- Are mock/planned/historical states clearly labeled?
- Are `RTM.md` and `SPECS.md` used only as derived summaries?

## Verdict States

Use one:

- `current`
- `needs_update`
- `missing_but_required`
- `not_yet_required`
- `stale_or_overclaiming`

For `needs_update`, `missing_but_required`, or `stale_or_overclaiming`, create a concrete follow-up task or issue-log entry.
