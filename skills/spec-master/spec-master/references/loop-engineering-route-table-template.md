# Loop Engineering Route Table Template

Use this template when `Loop Engineering Intake` is selected.

## Route Table

| Lane | Why now | Authority surface | Downstream skill | Required evidence | Stop condition | Must not do yet |
|---|---|---|---|---|---|---|
| `<lane>` | `<evidence from request or repo state>` | `<files/runtime source>` | `<owning skill>` | `<evidence needed before write/action>` | `<done-enough condition>` | `<guardrail>` |

## Allowed Lanes

- `resume-preflight`
- `next-gap-ranking`
- `readiness-hardening`
- `manual-review-refresh`
- `runtime-e2e-vrt`
- `traceability-rollup`
- `closeout-publish`

## Handoff Text

```text
Loop Engineering Intake selected lane: <lane>.
Authority surface: <files/runtime source>.
Required evidence before write/action: <evidence>.
Stop condition: <condition>.
Guardrail: <must-not-do-yet>.
```

## Guardrails

- Do not open a new spec before owner resolution.
- Do not continue stale `NEXT_STEPS.md` if `SPECS.md` and spec-local closure artifacts show completion.
- Do not route runtime allocation through registry sync or SDD authoring.
- Do not generate stakeholder claims beyond evidence.
- Do not commit broad dirty worktree state.
