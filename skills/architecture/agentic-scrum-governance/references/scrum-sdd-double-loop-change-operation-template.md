# Scrum SDD Double Loop Change Operation Template

Use this template when proposing a future change to the integrated `spec-driven-development + Scrum + double-loop improvement` operating model.

> Important: Filling this template does **not** itself authorize editing any skill.

---

## 1. Change Identity

- Change Title:
- Date:
- Owner:
- Related Sprint / Spec / Epic:
- Trigger Type: `delivery issue` / `retro finding` / `governance gap` / `runtime friction` / `skill candidate`

## 2. Trigger Summary

Describe what happened.

- What was observed?
- Where did it happen?
- Was it a one-off or repeated pattern?
- What delivery impact did it cause?

## 3. Current State

Describe the current workflow or rule.

- Current tool / skill / artifact involved:
- Current expected behavior:
- Current known limitation:

## 4. Desired State

Describe the target behavior.

- What should work differently?
- What should become clearer?
- What should become harder to do incorrectly?

## 5. External Research / Agentic Context

Summarize any external context that should influence the change.

- Is this problem specific to human-era Scrum assumptions?
- Does the problem emerge because agents are session-bounded, parallel, or role-specialized?
- Do external agentic-engineering patterns suggest a better default?
- Which external sources were reviewed?

Suggested source types:

- agentic engineering practice writeups
- multi-agent software engineering case studies
- research papers on team-based autonomous software engineering

## 6. Human vs Agent Responsibility Check

Clarify which responsibility should belong to the human and which should belong to the swarm.

- Human role in this problem:
- Orchestrator role:
- Worker agent role:
- Reviewer / QA role:

Decision rule:

- Do not solve a human governance problem only by pushing more responsibility down to implementation agents.

## 7. Scope Classification

Mark all that apply.

- [ ] spec-local process only
- [ ] Scrum ceremony mapping
- [ ] test governance (`TESTS.md`)
- [ ] spec registry (`SPECS.md`)
- [ ] operational memo (`NEXT_STEPS.md`)
- [ ] issue log
- [ ] traceability rollup (`RTM.md`)
- [ ] project architecture docs (`docs/architecture.md`, `docs/architecture/index.html`, `system-architect`)
- [ ] runtime governance (local infra registry)
- [ ] shared checklist/template
- [ ] skill description or skill behavior candidate

## 8. Planning Unit Shift Check

In agentic Scrum, check whether the requested change should shift planning from story-centric to contract/evidence/risk-centric handling.

- Does the change affect acceptance criteria quality?
- Does it affect dependency isolation?
- Does it affect evidence capture?
- Does it affect review or integration gates?

## 9. Non-Goals

List what this change must **not** do.

-
-
-

## 10. Authority Boundary Check

Fill this before deciding any action.

| Surface | Is it affected? | Allowed change? | Notes |
|---|---|---|---|
| `review.md` |  |  | final verdict only |
| folder `TESTS.md` |  |  | row-level evidence authority |
| workspace `.agents/specs/TESTS.md` |  |  | rollup only |
| `SPECS.md` |  |  | registry summary only |
| `NEXT_STEPS.md` |  |  | rolling memo only |
| `RTM.md` |  |  | traceability snapshot only |
| `docs/architecture.md` / `docs/architecture/index.html` |  |  | cross-spec communication snapshot only; `system-architect` owns workflow |
| local infra registry |  |  | runtime authority only |

Decision rule:

- If the proposed change mixes verdict, registry, evidence, and runtime authority, stop and redesign.

## 11. Repetition Check

Use this to decide whether the issue should stay local or be promoted.

- Number of occurrences:
- Across how many specs/sprints:
- Same root cause each time? `yes/no/unclear`
- Existing checklist already covers it? `yes/no`

### Promotion Rule

- If it is one-off or weakly evidenced → keep spec-local.
- If it has no clear existing owner and evidence is still too weak for a new spec / shared skill change → put it in the issue log first.
- If it repeats across multiple specs/sprints with the same root cause → candidate for shared process or skill refinement.

Canonical holding path when the workspace adopts one:

- `{workspace}/.agents/specs/ISSUE_LOG.md`

## 11.5 Owner Resolution Check

Before proposing a new spec or skill change, answer:

- Is there an active spec that can absorb this?
- Is this actually a completed-baseline follow-up that should become a CR overlay?
- Is this only a spec-local lesson / optimization follow-up?
- If no clear owner exists yet, should it be held in the issue log until a stronger cluster emerges?

Decision rule:

- `new spec` is the last option, not the default.

## 12. Evidence Required

List the evidence needed before any change is accepted.

- relevant `review.md` sections:
- related `TESTS.md` rows / evidence refs:
- architecture doc state / `system-architect` review refs, if architecture drift is involved:
- Sprint Review notes:
- Sprint Retro notes:
- runtime evidence from local infra registry (if applicable):
- reports / logs:

## 13. Swarm Self-Upgrade Path

Before proposing a skill change, check whether the swarm should upgrade itself in a cheaper/more local way first.

- [ ] improve spec or backlog structure
- [ ] use the issue log before promoting weakly evidenced issues
- [ ] improve prompt / operating doc / playbook
- [ ] improve memory / problem repository / lesson capture
- [ ] improve test or review gate
- [ ] improve architecture doc freshness or Architecture Context Packet through `system-architect`
- [ ] improve runtime/env governance usage
- [ ] adjust role boundaries or role roster
- [ ] only then consider a shared skill update

## 14. Proposed Change Type

Choose one primary type.

- [ ] update ceremony checklist
- [ ] update operating guide / markdown plan
- [ ] update reusable template
- [ ] update routing rule
- [ ] update test governance practice
- [ ] update registry wording rule
- [ ] update infra-governance handoff rule
- [ ] prepare later skill edit proposal

## 15. Affected Surfaces

List the exact files or skills that would be touched **if approved later**.

### Files

-
-

### Skills

-
-

### Commands / templates / guides

-
-

## 16. Skill-Edit Decision Gate

Answer all questions before allowing any skill change.

- Is the problem repeated enough to justify shared behavior change?
- Can the issue be solved by a plan/template/checklist instead?
- Is the issue actually caused by unclear routing rather than missing skill content?
- Would a skill edit risk expanding authority into the wrong surface?
- Can the problem be solved by better contracts, memory, or evidence flow instead?

Decision:

- [ ] No skill edit needed; solve with docs/checklist/process
- [ ] Skill edit candidate; prepare separate approved change plan later

## 17. Runtime / Registry Check

Only fill if runtime is part of the problem.

- Did the issue involve real env allocation, reuse, release, or stale runtime state?
- Was the local infra registry consulted?
- Was any runtime fact incorrectly copied into a spec or registry file?

Rule:

- Runtime state must remain governed by the local infra registry, never by `SPECS.md`, `RTM.md`, `NEXT_STEPS.md`, or `review.md` summaries.

## 18. TDD-Oriented Acceptance Criteria

Write acceptance criteria for the process change itself.

### Red

What failure or ambiguity exists today?

-

### Green

What would make this clearly improved?

-

### Refactor

How will we simplify or normalize the workflow after improvement?

-

## 19. Execution Plan

Describe the minimum safe sequence.

1.
2.
3.
4.

## 20. Research-Informed Review Questions

Use these when the change is about agentic Scrum itself.

- Does this make async written state stronger?
- Does this improve contract clarity before execution?
- Does this preserve orchestrator/worker separation?
- Does this increase evidence-backed review rather than opinion-only review?
- Does this make cross-spec architecture drift visible without turning architecture docs into readiness authority?
- Does this help the swarm self-upgrade without unnecessary skill churn?

## 21. Review Checklist

Before accepting the change, confirm:

- [ ] authority boundaries are still clean
- [ ] no runtime state leaked into spec registry surfaces
- [ ] no derived-to-derived sync rule was introduced
- [ ] readiness verdict still belongs to `review.md`
- [ ] test evidence still points back to `TESTS.md`
- [ ] architecture docs remain communication snapshots owned by `system-architect`
- [ ] the change is proportionate to the repeated problem
- [ ] the change improves agentic coordination rather than just adding ceremony overhead

## 22. Final Recommendation

- Recommended action:
- Why this action is enough:
- Why larger changes are not yet justified:

## 23. Final Status

- [ ] recorded only
- [ ] ready for future docs-only update
- [ ] ready for process change review
- [ ] candidate for separate skill-edit planning

## 24. Notes

-
