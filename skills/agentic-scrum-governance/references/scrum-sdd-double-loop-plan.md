# Scrum SDD Double Loop Plan

Date: 2026-05-28
Status: Drafted as current working model
Scope: Record the current integrated operating model for `spec-driven-development + Scrum + double-loop improvement`
Non-goal: This document does **not** authorize direct edits to any skill in `skills/`

## 1. Purpose

This plan records the current recommended way to run project delivery when the main execution model is:

- `spec-driven-development` for delivery truth
- Scrum for cadence, coordination, and review rhythm
- a separate double-loop for agent/process improvement

The goal is to keep delivery authority, test authority, registry authority, and runtime authority clearly separated.

## 2. Proper Name and File Naming

For this version, the proper name is:

- `scrum-sdd-double-loop`

This plan is intentionally recorded in this skill-local reference as:

- `scrum-sdd-double-loop-plan.md`

The naming style mirrors the existing action-plan / log artifact pattern in this workspace, while the storage location is intentionally moved under a formal global skill folder:

- `skills/agentic-scrum-governance/references/`

so future global skills can reference the same repo-owned asset through a proper skill-local `references/` path.

## 3. Operating Model Summary

The integrated model uses three layers.

### Layer A — Delivery Layer

Owned by `spec-driven-development` and spec-local artifacts:

- `requirements.md`
- `design.md`
- `tasks.md`
- `review.md`

This layer decides what is being built, how it is built, what work is active, and whether a spec is actually ready.

### Layer B — Cadence Layer

Owned by Scrum ceremonies and task coordination:

- Sprint Planning
- Daily Scrum
- Sprint Review
- Sprint Retrospective
- `scrum-master-skill`
- `scrum-developer-skill`

This layer controls timing, coordination, dispatch, blockers, and feedback rhythm.

### Layer C — Improvement Layer

Owned by double-loop learning and process refinement:

- retrospective outputs
- repeated-failure analysis
- lesson extraction
- checklist/process/skill evolution candidates

This layer improves how agents work without rewriting delivery truth surfaces on every issue.

## 4. External Research Synthesis (Agentic Scrum / Agent Swarm)

This planning model is also informed by external agentic-engineering research and practice notes gathered during this task.

### Key synthesis

1. Scrum should not disappear in the agentic era; it should shift from **human capacity coordination** to **orchestration, contract clarity, evidence flow, and governance**.
2. Backlog units should become more **contract/evidence/risk-centric** than story-point-centric. The key planning question is less “how many hours?” and more “what contract, what gate, what dependency, what proof?”
3. The orchestrator / coordinator should stay separate from implementers. Multiple sources emphasize that once the coordinator can also write production code, it tends to bypass planning discipline.
4. Async written state becomes mandatory because agent memory is session-bounded. Standups, plans, retros, and demos need durable markdown or issue-tracker artifacts.
5. Sprint planning is the highest-reasoning step and should use stronger reasoning capacity, while scoped implementation can often run cheaper/faster in parallel.
6. Reproducible demos and tests matter more than live presentation. In agent teams, demo artifacts should double as regression evidence where possible.
7. Retrospectives become more analytical and less social: recurring defects, environment friction, unclear contracts, and missed gates are the useful inputs.
8. Swarm self-upgrade should happen primarily through better specs, prompts, memory/problem repositories, review gates, and role design before escalating to actual skill edits.

### How this changes Scrum in practice

- Sprint Planning becomes a **risk and dependency design step**.
- Daily Scrum becomes an **async state/evidence checkpoint**.
- Sprint Review becomes a **contract-and-evidence review**, not only a visual demo.
- Sprint Retro becomes the system’s **self-upgrade control loop**.

### External references used in this planning round

- Microsoft Developer Blog — *Agentic-Agile: Why Agent Development Needs Agile (Not Just Prompts)*  
  <https://developer.microsoft.com/blog/agentic-agile-why-agent-development-needs-agile-not-just-prompts>
- Naren Yellavula — *What Running a Multi-Agent Software Project Actually Looks Like*  
  <https://www.yella.dev/blog/run-multi-agent-software-project/>
- Lance Ennen — *Rethinking Agile for AI Engineering Teams*  
  <https://www.lanceennen.com/blog/rethinking-agile-for-ai-engineering-teams>
- EngineeringExec — *AI-Scrum: Can Proven Agile Principles Work for Agent Teams?*  
  <https://engineeringexec.tech/posts/ai-scrum-can-proven-agile-principles-work-for-agent-teams>
- Agyn paper — *Agyn: A Multi-Agent System for Team-Based Autonomous Software Engineering*  
  <https://arxiv.org/html/2602.01465v2>

## 5. Authority Boundaries

| Surface | Authority | Must Not Become |
|---|---|---|
| `review.md` | Final readiness / QA / UAT / demo verdict | registry, task board, runtime ledger |
| folder-level `TESTS.md` | test catalog, canonical commands, evidence refs, trace mapping | PASS/FAIL authority |
| workspace `.agents/specs/TESTS.md` | test rollup / summary | row-level source of truth |
| `SPECS.md` | stable spec registry summary | live execution board |
| `NEXT_STEPS.md` | rolling operational memo | stable registry or final verdict |
| `RTM.md` | traceability rollup | independent readiness authority |
| `docs/architecture.md` / `docs/architecture/index.html` | cross-spec architecture communication snapshot owned by `system-architect` workflow | readiness verdict, branch-spec design authority, or static-analysis substitute |
| local infra registry | runtime allocation and governed env state | spec registry |

## 6. Ceremony-to-Artifact Mapping

### Sprint Planning

Inputs:

- `requirements.md`
- `design.md`
- `tasks.md`
- dependency / blocker status

Outputs:

- selected sprint scope
- task dispatch order
- explicit unresolved blockers

Rule:

- Sprint Planning selects work from spec truth surfaces; it does not redefine them.
- Sprint Planning should optimize for contract clarity, dependency isolation, risk sequencing, and verification readiness more than raw story-point throughput.

### Daily Scrum

Inputs:

- active task status
- dependency blockers
- runtime availability if real env is needed

Outputs:

- unblock actions
- sequencing adjustments
- escalation needs

Rule:

- Runtime facts must come from the local infra registry, not from `SPECS.md` or `NEXT_STEPS.md` guesswork.
- In agent-first teams, Daily Scrum should usually be async and artifact-backed.

### Sprint Review

Inputs:

- completed increments
- demo evidence
- test evidence
- relevant `review.md`
- architecture doc state when the increment changes module boundaries, shared contracts, runtime topology, trust boundaries, or cross-spec ownership

Outputs:

- stakeholder feedback
- accepted / rejected / changed expectations
- possible CR or follow-up spec
- architecture doc refresh or `system-architect` follow-up when drift is detected

Rule:

- Sprint Review may influence the next change, but the formal readiness verdict remains in spec-local `review.md`.
- Prefer reproducible demo/test artifacts over one-time verbal walkthroughs.
- Architecture docs help humans understand the system, but stale diagrams or architecture HTML must not upgrade readiness claims.

### Sprint Retrospective

Inputs:

- missed handoffs
- false-green cases
- test evidence gaps
- repetitive coordination pain
- runtime governance friction
- architecture drift, stale architecture docs, unclear cross-spec ownership, or repeated architecture handoff gaps
- clarification loops / rework patterns

Outputs:

- spec-local follow-up
- process change candidate
- checklist candidate
- skill update candidate
- `system-architect` refresh/review candidate when the issue is architecture communication or cross-spec coherence

Rule:

- Retro improves the system of work; it does not rewrite historical delivery evidence.
- Retro outputs should be phrased as changes to contracts, docs, prompts, gates, role boundaries, or memory structures before they are phrased as “change the skill.”

## 7. Role of Scrum Skills

### `scrum-master-skill`

Use for:

- epic/task breakdown
- dependency-aware dispatch
- QC coordination
- clarification escalation
- retro lesson extraction

Must not do:

- replace `review.md` as verdict authority
- rewrite registry truth surfaces directly
- treat runtime observations as authoritative without infra governance

Additional interpretation for the agentic era:

- act as orchestrator / coordinator / process keeper
- favor explicit task decomposition, dependency mapping, QC handoffs, and retro extraction
- avoid becoming a silent implementer

### `scrum-developer-skill`

Use for:

- task understanding
- TDD execution
- implementation evidence generation
- quality checks and documentation support

Must not do:

- treat implementation completion as equivalent to spec acceptance
- bypass test registry or review closeout rules

Additional interpretation for the agentic era:

- worker agents should optimize for narrow scope, TDD evidence, and structured handoff
- implementation agents should not own final system truth alone

## 8. End-to-End Delivery Flow

1. Route request through `spec-master`.
2. Use `spec-driven-development` to define / resume the correct spec lane.
3. Use Sprint Planning to select ready work from `tasks.md`.
4. Use `scrum-master-skill` to dispatch and monitor execution.
5. Use `scrum-developer-skill` to implement via TDD and produce evidence.
6. Refresh folder-level `TESTS.md` if test catalog/evidence changed.
7. Use `system-architect` when the increment materially changes project-level architecture docs or code-review architecture context.
8. Refresh workspace `.agents/specs/TESTS.md` when rollup is needed.
9. Update `RTM.md` / `SPECS.md` only as derived snapshots after upstream authority is complete.
10. Decide actual readiness in `review.md`.
11. Use Sprint Review for stakeholder validation.
12. Use Sprint Retrospective for process/agent improvement.

## 9. Agent Swarm Scrum Model

If a project is primarily delivered by an agent swarm, Scrum should be interpreted as follows:

### Human role

The human is primarily:

- strategy owner
- guardrail owner
- architecture approver
- exception handler
- final acceptor for high-risk boundaries

The human is less “daily implementer” and more “manager of a virtual engineering organization.”

### Swarm role structure

Recommended minimum swarm roles:

- Orchestrator / Scrum Master agent
- Planner / PM agent
- Implementation agents by domain
- QA / verification agent
- Reviewer / adversarial review agent

Optional:

- Security specialist
- Infra/runtime specialist
- Design/UX reviewer
- Researcher agent

### Swarm sprint unit

The planning unit should be:

- a contract
- a dependency island
- a verification unit
- an evidence package

rather than only a prose story.

### Swarm definition of done

Swarm work is done only when:

- code/test changes exist
- evidence exists
- integration risk is reviewed
- `review.md` verdict is written where required

## 10. Double-Loop Cadence

### Loop 1 — Delivery Loop

`spec -> task -> implement -> test/evidence -> review.md verdict`

This loop optimizes for shipping a validated increment.

### Loop 2 — Improvement Loop

`retro finding -> pattern confirmation -> process/skill/checklist candidate -> next sprint validation`

This loop optimizes for improving how the team/agents work.

### Preferred self-upgrade order for an agent swarm

When the swarm finds a recurring problem, prefer this order:

1. clarify backlog/spec contract
2. improve written operating docs / prompts / playbooks
3. improve memory / problem repository / evidence capture
4. improve review/test/runtime gates
5. adjust role boundaries or agent roster
6. only then consider changing or creating a shared skill

## 11. Promotion Rules for Improvements

### Keep Spec-Local

Keep an issue local when it is:

- a one-off implementation detail
- tied to one spec’s business rule
- caused by temporary external conditions
- already covered by current governance but simply not executed well once

### Promote to Shared Process / Skill Candidate

Promote only when the pattern:

- repeats across multiple specs or sprints
- creates real delivery delay or false-green risk
- exposes a missing checklist or routing rule
- shows that the current skill boundary is unclear or insufficient

## 12. Future Change Buckets

The following buckets are allowed as future change candidates, but none are approved for edit by this plan alone.

### A. Ceremony Mapping Changes

Examples:

- add a standard Sprint Review evidence checklist
- add a standard Sprint Retro decision template
- add an async standup/report artifact format for agent sessions
- define stronger contract/evidence/risk-oriented planning prompts
- add a standard architecture drift / ownership / handoff review prompt that delegates document refresh to `system-architect`

### B. Routing Boundary Changes

Examples:

- clarify when `spec-master` should hand off earlier
- clarify when `scrum-master-skill` should request `test-registry-manager`

### C. Evidence Governance Changes

Examples:

- strengthen `TESTS.md` refresh timing
- refine `review.md` closeout expectations

### D. Runtime Governance Changes

Examples:

- define when sprint work must query governed runtime state
- define when runtime blockers should stop delivery claims

### E. Skill Surface Changes

Examples:

- tighten skill descriptions
- add a reusable retrospective checklist
- add stronger anti-mixing guidance to selected skills

Rule:

- Skill changes require a later explicit decision and a separate change operation record.

## 13. Guardrails

Do not do the following:

1. Let `SPECS.md`, `RTM.md`, workspace `TESTS.md`, or Sprint Review become final PASS/FAIL authority.
2. Store live ports, compose stacks, runtime locks, or container allocation state in spec registries.
3. Do derived-to-derived sync between `SPECS.md`, `RTM.md`, and `TESTS.md`.
4. Promote every retro complaint into a global skill/process change.
5. Let the orchestrator silently become an implementation shortcut.

## 14. Success Criteria

This model is working correctly when:

- Sprint scope is traceable to spec-local tasks
- readiness claims are always backed by `review.md`
- test evidence is discoverable through `TESTS.md`
- registry summaries are consistent but clearly derived
- runtime allocation facts come only from local infra governance
- retrospectives produce fewer repeated failures over time
- planning effort is focused on risk/contract/evidence rather than vague story sizing alone
- swarm improvements appear first as better artifacts, gates, and memory before broad skill churn

## 15. Next Safe Step

If future refinement is requested, use:

- `skills/agentic-scrum-governance/references/scrum-sdd-double-loop-change-operation-template.md`

to assess whether the change belongs to:

- spec process
- Scrum cadence
- test governance
- registry wording
- infra governance
- or a later skill edit
