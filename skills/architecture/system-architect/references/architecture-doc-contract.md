# Steering Architecture Document Contract

Use this when creating or refreshing OpenCode steering architecture docs under `.agents/steering/`. The product / tech / structure split is inspired by Kiro's foundational steering files, adapted here for OpenCode project governance and dual markdown/HTML output.

Canonical OpenCode paths:

- `.agents/steering/product.md` and `.agents/steering/product.html`
- `.agents/steering/tech.md` and `.agents/steering/tech.html`
- `.agents/steering/structure.md` and `.agents/steering/structure.html`

Treat `docs/architecture.md` and `docs/architecture/index.html` as legacy/equivalent inputs unless repo instructions explicitly keep them canonical.

Use the bundled templates before drafting from scratch:

- Markdown: `assets/templates/steering/product.md`, `tech.md`, `structure.md`
- HTML: `assets/templates/steering/product.html`, `tech.html`, `structure.html`

## Product Steering

Recommended `.agents/steering/product.md` outline:

```markdown
# Product Overview

## Status

- State: current | needs_update | missing_but_required | not_yet_required | stale_or_overclaiming
- Last reviewed: YYYY-MM-DD
- Source refs:
- Review refs:
- Known gaps:

## What This Project Is

Short, evidence-backed product and system purpose.

## Core Capabilities

User-visible and operator-visible capabilities, with source refs.

## Target Users and Operators

Who uses, operates, reviews, or integrates with the system.

## Common User Access

Shared workflow language, UX/operator conventions, recurring journeys, and user-facing terms.

## Evidence and Freshness

Links to specs, reviews, screenshots, runtime proof, or explicit `not_assessed`.
```

## Technical Steering

Recommended `.agents/steering/tech.md` outline:

```markdown
# Technology Stack

## Status

- State:
- Last reviewed:
- Source refs:
- Review refs:
- Known gaps:

## System Context

Major services, agents, data stores, external systems, and out-of-scope boundaries.

## Architecture Map

Mermaid or ASCII diagram of major modules/services/agents/data stores/external systems.

## Common Programming Interface

APIs, schemas, events, MCP/tools, adapters, extension points, contract authority.

## Common Communications Support

Protocols, auth/session boundary, jobs/queues, observability signals, failure handoff.

## Cross-Platform / Runtime Consistency

Deployment contexts, runtime assumptions, portability constraints, local/CI/cloud boundaries.

## Data and Trust Boundaries

PII/secrets/data stores, authz/authn boundary, execution boundary, third-party boundary.

## Critical Flows

For each flow: trigger -> components -> data -> failure modes -> evidence refs.

## Code-Review Context Packet

Bounded contexts, high-blast-radius areas, graph query suggestions, open questions.
```

## Structure Steering

Recommended `.agents/steering/structure.md` outline:

```markdown
# Project Structure

## Status

- State:
- Last reviewed:
- Source refs:
- Review refs:
- Known gaps:

## Repository / Workspace Shape

Major directories, packages, services, agents, specs, docs, generated artifacts, and ownership boundaries.

## Bounded Contexts and Ownership

Domain/module boundaries, owners, handoff paths, and cross-spec impacts.

## Architecture Decisions

Only hard-to-reverse, surprising, or cross-spec decisions. Include alternatives rejected.

## Source and Artifact Flow

How requirements/design/tasks/review/test evidence become steering markdown, steering HTML, project review, RTM, and SPECS snapshots.

## Naming and Layout Conventions

Project-specific naming, package, test, generated-output, and documentation conventions.

## Evidence and Freshness

Links to specs, reviews, tests, runtime proof, or explicit `not_assessed`.
```

## HTML Presentation Contract

Each `.agents/steering/*.html` file is a presentation snapshot of its same-name markdown source. It should:

- show source refs and freshness visibly;
- show steering doc state visibly;
- include diagrams or dense tables for scanning;
- preserve warning labels such as `not_assessed`, `needs_update`, and `stale_or_overclaiming`;
- avoid marketing claims that exceed `review.md`.

If there is no rendering pipeline, a hand-maintained single-file HTML is acceptable. Keep the markdown source authoritative.

## Evidence Rules

- Planned design != executed implementation.
- Mock-backed journey != full integration.
- Historical architecture != current architecture.
- RTM/SPECS summary != source truth.
- Code graph evidence != runtime readiness.

Use `not_assessed` when evidence is missing.
