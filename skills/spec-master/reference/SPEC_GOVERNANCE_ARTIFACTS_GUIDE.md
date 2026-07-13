# Spec Governance Artifacts Guide

本文件定義 SDD 中 governance artifacts 的定位、生命週期與維護行為。它補足 phase 文件中的共用規則，避免 `ISSUE_LOG.md`、`SPECS.md`、`NEXT_STEPS.md`、`TESTS.md`、`RTM.md`、`review.md` 互相越界。

## 1. Artifact Roles

| Artifact | Role | Owns | Does Not Own |
|---|---|---|---|
| `ISSUE_LOG.md` | unresolved improvement holding surface | repeated findings, weak evidence, owner-resolution state, cluster / promotion candidate pointer | requirements, task plan, readiness verdict, registry state |
| `requirements.md` | requirement source of truth | requirement IDs, user stories, acceptance criteria, repo-local vs external boundary | test catalog, final readiness verdict, cross-spec registry |
| `design.md` | design and contract boundary truth | architecture, contracts, FMEA, traceability anchors, artifact authority model | task progress, runtime allocation state, final verdict |
| `tasks.md` | implementation plan truth | task IDs, requirement trace, eval checks, mitigation tasks, closeout tasks | requirement authoring, RTM authoring, verdict |
| `TESTS.md` | test catalog / evidence pointer authority | test IDs, canonical commands, owners, req/AC trace, evidence refs, freshness | readiness verdict, SPECS / RTM correction |
| `review.md` | acceptance / readiness verdict authority | PASS / CONDITIONAL / FAIL, residual risks, demo readiness, security and test conclusions | registry authoring, row-level test catalog |
| `RTM.md` | requirement traceability rollup | requirement → AC → design → tasks → tests → review / residual risk view | upstream truth, task progress, final verdict |
| `SPECS.md` | stable spec registry summary | spec lifecycle state, dependencies, impacts, open / closed CR summaries, stable acceptance summary | task board, runtime state, row-level test or RTM source |
| `NEXT_STEPS.md` | rolling operational memo | current phase, next action, blocker, resume hint, handoff / closure state | history log, task ledger, issue log, registry |

## 2. Lifecycle Flow

```text
ISSUE_LOG.md (holding, if owner unclear)
  -> owner resolution
  -> Folded into active spec / CR, or Promoted to new SDD spec
  -> requirements.md / design.md / tasks.md / reports / review.md
  -> TESTS.md row-level evidence authority
  -> workspace test rollup
  -> RTM.md requirement traceability rollup
  -> SPECS.md stable registry summary

NEXT_STEPS.md runs beside this flow as the current resume / blocker / handoff memo.
```

Core rules:

- Raw `ISSUE_LOG.md` rows do not become RTM requirements. They must first be folded / promoted and formalized through SDD artifacts.
- `RTM.md` reflects formalized requirement traceability. It does not create requirements, tasks, tests, or verdicts.
- `SPECS.md` summarizes stable spec / CR state. It does not create work or replace upstream evidence.
- `NEXT_STEPS.md` is overwritten as operational state changes. It does not preserve history.
- Derived artifacts never repair upstream artifacts.
- Reusable artifact schema, lifecycle wording, or migration behavior that should affect future customer repositories
  must be authored in the owning global skill source first. A target repo's local spec wording or product parser can
  record consumption evidence, but it is not by itself a reusable governance contract.

## 3. Maintenance Behavior by Phase

| Phase | Required Behavior |
|---|---|
| Phase 1 Requirements | Read `SPECS.md`, then `NEXT_STEPS.md`. If the request is an unresolved improvement, do owner resolution before opening a new spec. Create or update `requirements.md` only after deciding the lane. Do not author from `RTM.md`. |
| Phase 2 Design | Define artifact authority model in `design.md` when the work affects `TESTS.md`, `RTM.md`, `SPECS.md`, `ISSUE_LOG.md`, or stakeholder-facing summaries. Add traceability anchors for RTM. |
| Phase 3 Tasks | Mirror the Phase 1 / 2 authority boundary. Plan explicit closeout tasks for `TESTS.md`, RTM refresh, SPECS refresh, CR closure, and ISSUE_LOG fold/promote/close when applicable. |
| Phase 4 Implementation | Update upstream evidence first: code, tests, reports, task status. Update folder-level `TESTS.md` before workspace rollups. Keep `NEXT_STEPS.md` short and current. |
| Phase 5 Review | `review.md` records final verdict and residual risk. Check that `ISSUE_LOG.md` items were either folded, promoted, closed, or explicitly left as holding records. Check that RTM / SPECS refreshes are derived only from upstream truth. |
| Phase 6 Optimization | If repeated failures reveal systemic workflow gaps, decide whether the finding stays as spec-local lesson, enters `ISSUE_LOG.md`, folds into a CR, or becomes a promoted skill / process change candidate. |

## 4. ISSUE_LOG Promotion Rules

Use this order before creating a new spec:

1. Active spec can absorb it → fold into active spec.
2. Completed baseline is impacted → create / update CR overlay.
3. Single-spec lesson / optimization → keep in that spec lane.
4. Owner unclear and evidence weak → keep in `ISSUE_LOG.md`.
5. Repeated root cause + clear cluster + enough evidence + no owner → promote to new spec or shared skill / process change candidate.

When an issue is folded or promoted:

- Keep the issue row as historical pointer.
- Move detailed requirements / tasks / verdicts to SDD artifacts.
- Reflect it in RTM only after it becomes formal requirement / AC / task / test / review evidence.
- Reflect it in SPECS only after it becomes formal spec / CR state.

## 5. NEXT_STEPS Lifecycle

`NEXT_STEPS.md` is read after `SPECS.md` and before opening detailed active spec artifacts. It is updated at:

- phase exit,
- pause / handoff,
- blocker / circuit breaker,
- CR / impact triage change,
- external execution handoff or closure,
- optimization round transition.

It should contain only:

- current phase,
- active spec,
- work classification,
- next action,
- blockers / waiting on,
- resume hint,
- related artifact paths,
- optional repo-side / external execution state when truly relevant.

It must not contain:

- full task lists,
- detailed task progress,
- copied requirements / design / review content,
- historical changelog,
- unresolved issue rows,
- registry summary,
- runtime allocation inventory.

If it is stale, overwrite it with the latest operational state. Do not append contradictory states.

## 6. RTM Requirement Traceability

RTM is a需求管理(requirements management) view. For each requirement, it should allow a reviewer to answer:

- Which acceptance criteria define success?
- Which design section or contract supports it?
- Which task implements it?
- Which test or evidence verifies it?
- What did `review.md` conclude?
- What residual risk or gap remains?

Refresh RTM only after upstream artifacts and test evidence are current. If RTM exposes a gap, fix the upstream artifact first, then regenerate RTM.

## 7. Forbidden Flows

- `ISSUE_LOG.md -> RTM.md` as direct requirements.
- `ISSUE_LOG.md -> SPECS.md` as direct spec entries.
- `SPECS.md -> RTM.md` as generation source.
- `RTM.md -> TESTS.md` as test catalog source.
- `SPECS.md -> TESTS.md` as required-test generator.
- `NEXT_STEPS.md -> tasks.md` as task progress source.
- `NEXT_STEPS.md -> SPECS.md` as registry truth.
- Runtime allocation state -> `SPECS.md` / `RTM.md`.
- Target-repo-only artifact format change -> future customer repository contract.
- Product parser implementation -> governance schema authority.

## 8. Closeout Order

When a spec affects governance artifacts, use this order:

1. Resolve issue-log disposition if applicable: `Folded`, `Promoted`, `Closed`, `Dropped`, or explicit holding state.
2. Update upstream SDD artifacts: `requirements.md`, `design.md`, `tasks.md`, reports, code evidence, test output, `review.md`.
3. Update folder-level `TESTS.md`.
4. Refresh workspace `.agents/specs/TESTS.md` through `test-registry-manager` when used.
5. Refresh `RTM.md` from upstream artifacts and test authority.
6. Refresh `SPECS.md` stable summary through `spec-registry-manager`.
7. Update `NEXT_STEPS.md` to current resume / closure / handoff state only.

## 9. Reusable Governance Contract Changes

When a branch spec discovers that artifact rules themselves need to change:

1. Decide the owning skill:
   - `test-registry-manager` owns `TESTS.md` schema, aliases, row reconciliation, evidence posture, and update recommendations.
   - `spec-driven-development` / `spec-master` own SDD lifecycle, RTM, NEXT_STEPS, and phase closeout ordering.
   - `spec-registry-manager` owns `SPECS.md` registry semantics and warning summaries.
2. Update the canonical skill source or file a CR/handoff before claiming customer-repo impact.
3. Keep legacy compatibility explicit. Existing repositories should get normalized reads and advisory migration plans before destructive rewrites.
4. In the target repo, record only what was consumed or verified locally; do not claim global inheritance until the skill source is published/installed.
