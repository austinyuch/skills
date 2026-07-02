---
name: system-architect
description: 建立、維護與審查跨 spec 的專案整體系統架構與 steering 文件。當使用者要求 project/system architecture、系統設計書、architecture.md、架構 HTML、`.agents/steering/product|tech|structure`、跨 spec 架構盤點、架構質疑、architecture review、project start 系統設計、或 project-review 前需要整理整體架構觀點時使用。此 skill 從 spec-master / spec-driven-development / project-review / code-review evidence 綜整 `.agents/steering/{product,tech,structure}.md` 與同名 HTML，提供 SAA good-parts vocabulary、Agile/YAGNI 邊界、stale/overclaim 檢查、以及給 code-review 的高階 architecture context packet；不取代 spec-local `design.md` 或 `review.md` authority。
---

# System Architect

## Overview

Use this skill as the authoring and maintenance owner for project-level steering architecture documents. It reconciles accepted branch-spec designs into `.agents/steering/` files inspired by Kiro's foundational steering pattern and challenges architecture choices before they become expensive.

It does not replace:

- `spec-master`: routing front door and lane identity resolution.
- `spec-driven-development`: branch-spec requirements / design / tasks / review truth.
- `project-review-skill`: executive narrative and readiness claim cap.
- `code-review`: graph-backed code structure, impact, bounded-context, and static review tooling.

## Workflow

### 1. Route and Load Authority Sources

Start from `spec-master` when the request is part of spec governance, project start planning, or project review preparation.

Read these, if present:

- `AGENTS.md`
- `.agents/specs/SPECS.md`
- `.agents/specs/NEXT_STEPS.md`
- `.agents/specs/RTM.md`
- `.agents/specs/**/requirements.md`
- `.agents/specs/**/design.md`
- `.agents/specs/**/review.md`
- `docs/PROJECT_REVIEW_GUIDE.md`
- existing `.agents/steering/product.md`, `.agents/steering/tech.md`, `.agents/steering/structure.md`
- existing `.agents/steering/product.html`, `.agents/steering/tech.html`, `.agents/steering/structure.html`
- legacy/equivalent `docs/architecture.md`, `docs/architecture/index.md`, `docs/architecture/index.html`
- `skills/spec-driven-development/references/system-architecture-lifecycle.md`

When the workspace uses another active spec root, use that root. Do not create a parallel architecture surface when the repo already declares an equivalent path. Prefer `.agents/steering/` for new OpenCode workspaces; treat `docs/architecture*` as legacy/equivalent input unless repo instructions explicitly keep it canonical.

### 2. Decide the Architecture Doc State

Classify the project-level architecture docs:

- `current`: docs match accepted design and review evidence.
- `needs_update`: docs exist but miss material accepted changes.
- `missing_but_required`: no docs exist and accepted evidence is stable enough.
- `not_yet_required`: project is too small, prototype-only, or evidence-thin.
- `stale_or_overclaiming`: docs present planned, mock-backed, or historical state as current executed truth.

If state is `not_yet_required`, leave a short note in the active spec or review. Do not create a large architecture doc just to satisfy ceremony.

### 3. Challenge the Architecture

Use the gstack-inspired engineering-manager posture before writing:

- What already solves this subproblem?
- What is the minimum architecture that supports the current slice?
- What is the blast radius if this choice is wrong?
- Which decisions are one-way doors: data model, public API, auth boundary, deployment topology, durable storage?
- Which decisions are two-way doors and can be made incrementally?
- Is this boring by default, or spending an innovation token deliberately?
- Does the design serve tired humans at 3am: observability, runbooks, failure handoff, rollback?
- Does org/team ownership match the proposed architecture boundaries?
- Does this create accidental complexity that the project invented for itself?

For high-stakes uncertainty, ask one focused question or record an explicit `Open Question`; do not invent certainty.

### 4. Apply IBM SAA Good Parts

Use SAA only as vocabulary for consistency:

- **Common User Access**: shared workflow language, UI/operator conventions, user journey names.
- **Common Programming Interface**: stable APIs, schemas, events, MCP/tool contracts, adapters, extension points.
- **Common Communications Support**: protocols, auth/session boundary, jobs/queues, service-to-service contracts, observability and failure handoff.
- **Cross-platform consistency**: deployment contexts, runtime assumptions, portability constraints, agent/tool boundaries.

Never turn SAA into a heavyweight enterprise blueprint. Keep first-slice docs short and evidence-backed.

### 5. Use Code-Review as Architecture Evidence

For non-trivial architecture work, coordinate with `code-review` if available:

- Run or request graph preflight/status before relying on graph data.
- Use focused queries such as `architecture`, `bounded-context`, `impact`, `dependency-path`, `developer-routing`, `capability-inventory`, or `search-code --graph-only`.
- Treat graph output as evidence input, not authority over checked-out code or accepted spec artifacts.
- Record graph query names and limitations in the architecture doc or review.

Produce an **Architecture Context Packet** for downstream review. Prefer storing it in `.agents/steering/tech.md`, `.agents/steering/structure.md`, or a spec-local report when it is too detailed for product-level steering:

```markdown
## Architecture Context Packet

- System boundary:
- Main modules / services:
- Bounded contexts:
- Critical data flows:
- Public contracts:
- Trust boundaries:
- High-blast-radius files or components:
- Expected graph/code-review queries:
- Open architecture questions:
- Evidence refs:
```

`code-review` can use this packet to focus graph and static analysis; it does not need to rediscover the whole system from scratch.

### 6. Write or Refresh Architecture Artifacts

Default outputs:

- Product steering markdown: `.agents/steering/product.md`
- Product steering HTML: `.agents/steering/product.html`
- Technical steering markdown: `.agents/steering/tech.md`
- Technical steering HTML: `.agents/steering/tech.html`
- Structure steering markdown: `.agents/steering/structure.md`
- Structure steering HTML: `.agents/steering/structure.html`
- Optional evidence map: `.agents/steering/assets/evidence-map.json`

Use source-first order:

1. Update upstream truth first: accepted `requirements.md`, `design.md`, code evidence, test evidence, `review.md`.
2. Update steering markdown sources from those accepted sources.
3. Generate or update same-name HTML presentations from markdown.
4. Update derived snapshots (`RTM.md`, `SPECS.md`) only as one-way summaries if required.

Never use steering HTML to reverse-author requirements, design, review, TESTS, RTM, or SPECS.

For document structure, read [references/architecture-doc-contract.md](references/architecture-doc-contract.md). For review gates, read [references/architecture-review-checklist.md](references/architecture-review-checklist.md). For code-review handoff, read [references/code-review-collaboration.md](references/code-review-collaboration.md).

### 7. Project Review Integration

Before `project-review-skill` generates executive HTML, ensure architecture doc state is known. If architecture docs are stale or missing-but-required, either refresh them first or require project review to show a visible gap/warning.

Project review can consume architecture docs as narrative input, but readiness and evidence claims remain capped by `review.md`, `SPECS.md`, `RTM.md`, and evidence metadata.

## Output Style

Be direct and skeptical. Prefer diagrams, tables, and source refs over long prose. Label uncertainty instead of smoothing it over.

Use Mermaid where useful, but compact ASCII diagrams are acceptable when they make data flow or ownership clearer.
