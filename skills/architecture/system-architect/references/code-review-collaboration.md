# Code-Review Collaboration

Use this when system architecture work needs code graph, impact, or bounded-context evidence.

## Relationship

`system-architect` owns the cross-spec architecture narrative and questions. `code-review` owns graph-backed code structure, impact, bounded-context, and static review tooling. Neither replaces `review.md` readiness authority.

## Preflight

If `code-review` is available and the architecture work is non-trivial:

1. Check repo instructions for graph lifecycle.
2. Inspect `.code-review/manifest.json`, `.code-review/graph.sqlite`, or equivalent if present.
3. Run the repo-documented status/doctor command, or use `review-cli ... init --graph` / `graph init` if no repo-specific flow exists.
4. Record graph freshness and limitations.

Skip graph work only when the task is narrow, files are already known, or graph setup costs more than the task warrants. Say why in the architecture notes.

## Useful Query Intents

Ask focused questions:

- `architecture <dir>`: module structure and dependencies.
- `bounded-context`: business/module boundary discovery.
- `impact`: likely blast radius.
- `dependency-path`: why two components are coupled.
- `developer-routing`: owner/handoff hints.
- `capability-inventory`: business capability map when available.
- `search-code --graph-only`: exact structural search without embeddings.

## Architecture Context Packet

Write this into `.agents/steering/tech.md`, `.agents/steering/structure.md`, or a spec-local report when handing work to code-review:

```markdown
## Architecture Context Packet

- Purpose:
- Current architecture doc state:
- System boundary:
- Main modules/services:
- Bounded contexts:
- Critical data flows:
- Public contracts:
- Trust boundaries:
- High-blast-radius components:
- Suspected stale/overclaiming areas:
- Recommended code-review queries:
- Evidence refs:
- Open questions:
```

## Guardrails

- Do not use graph output to overrule checked-out code or accepted spec/review artifacts.
- Do not claim runtime readiness from static graph evidence.
- Do not paste giant graph dumps into architecture docs; summarize and link/report.
- If graph state is partial, label the architecture conclusion as partial.
