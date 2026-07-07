# GStack CEO Perspective Reference

Use this reference when generating an executive project review that should go deeper than a product brochure. It adapts the public gstack founder/CEO review posture into a project-level review artifact while preserving this skill's evidence and claim-cap rules.

## Sources To Credit

This skill bundle credits the source methodology in `../README.md`. Generated project review reports should not include gstack citation by default; include it only when the user explicitly asks for citation inside that report.

Attribution text for the skill bundle:

- "CEO/founder perspective adapted from Garry Tan's gstack CEO review workflow and Builder Ethos. Source: https://github.com/garrytan/gstack"
- Local source paths consulted during this skill update: `~/projects/gstack/README.md`, `~/projects/gstack/ETHOS.md`, and `~/projects/gstack/plan-ceo-review/sections/review-sections.md`.

Do not imply endorsement by Garry Tan, YC, or gstack. Use "inspired by" or "adapted from" language only.

## CEO Review Lens

Apply these lenses before writing the final narrative:

1. **Problem truth before feature truth**: identify the real pain, the status quo, who suffers from it, and why now. If the project only lists features, infer the unsolved business problem conservatively and label weak evidence as an open question.
2. **Ten-star product challenge**: state what would make the product obviously excellent, not merely functional. Separate must-have execution gaps from optional ambition.
3. **Scope mode**: classify the recommended executive posture as one of:
   - `EXPAND`: the current project is under-ambitious relative to the discovered opportunity.
   - `SELECTIVE_EXPAND`: keep the core scope but add a few high-leverage capabilities.
   - `HOLD_SCOPE`: the scope is right; depth, reliability, and proof are the constraint.
   - `REDUCE`: the project needs a sharper wedge before scaling.
4. **Search-before-building check**: identify whether the project uses standard, battle-tested patterns where appropriate, and where it has a first-principles reason to diverge.
5. **Completeness economics**: evaluate whether missing tests, edge cases, docs, operations, or UX states are still worth completing because AI-assisted execution lowers marginal cost. Do not use this to justify unrelated scope creep.
6. **User sovereignty**: present strategic recommendations as options with rationale. Do not rewrite the user's stated direction as if the review has final authority.

## Required Executive Depth Additions

Add these sections or weave them into existing sections when the report format is tight:

### Founder Thesis

Answer:

- What is the wedge?
- Why is this project meaningfully better than the current workaround?
- What user or operator behavior would prove demand?
- What assumption would kill the thesis if false?

### Strategic Bet Map

Create a compact table:

| Bet | Evidence | Confidence | Kill/Risk Signal | Next Proof |
| --- | --- | --- | --- | --- |

Rules:

- `Evidence` must point to repo artifacts, live evidence, specs, logs, screenshots, or explicitly marked assumptions.
- `Confidence` should be `High`, `Medium`, or `Low`; never inflate weak evidence.
- `Next Proof` should be a concrete validation action, not a vague roadmap item.

### 10-Star Gap Analysis

Differentiate:

- **Execution gaps**: bugs, missing tests, mock-heavy paths, readiness blockers, incomplete integrations.
- **Product gaps**: missing workflows, unclear user value, weak differentiation, poor UX state coverage.
- **Operating gaps**: observability, rollout, support, documentation, ownership, maintenance cost.
- **Strategic gaps**: unclear wedge, weak demand proof, no distribution path, no measurable adoption signal.

### Decision Memo

End with one of:

- `Invest`: evidence supports deeper buildout.
- `Hold and harden`: value is plausible, but reliability/proof is the gating issue.
- `Narrow the wedge`: reduce scope to a more provable path.
- `Pause`: the thesis is not supported by current evidence.

Always include:

- Recommended decision
- One-paragraph rationale
- Top 3 next actions
- Evidence limits / open questions

## Evidence Discipline

This reference never overrides the skill's readiness claim cap:

- Do not turn `CONDITIONAL`, `mock-heavy`, `fixture-backed screenshot`, or `not_assessed` evidence into a success claim.
- Use the existing warning taxonomy and feature evidence metadata.
- If CEO perspective creates a stronger narrative than the evidence supports, keep the narrative but label it as a hypothesis or bet.
- Cite source refs for feature proof in the generated report when useful. Keep gstack method attribution in the skill README/reference by default.

## Copy Patterns

Use direct, executive language:

- "The product thesis is strong, but the proof is currently mock-heavy."
- "The right next move is not more surface area; it is one real integrated workflow that proves the wedge."
- "This is a `HOLD_SCOPE` project: the ambition is sufficient, but reliability and evidence are not yet board-ready."
- "The 10-star version is not a prettier dashboard. It is an operator workflow that closes the loop from signal to action."

Avoid:

- "Fully validated" unless live evidence says so.
- "Production ready" unless authoritative review evidence says so.
- Attributing claims to gstack, Garry Tan, or YC.
