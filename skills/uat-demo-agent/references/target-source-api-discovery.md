# Target Source/API Discovery

Use this guide as the source/API discovery preflight when a target repository has
source code available and the current plan is blocked because the agent does not
yet know the target's real UI/API contract. This lane is required before
declaring "not enough data" for browser-executable UAT steps.

This guide is intentionally a skill-native discovery workflow. It does not add
runtime readiness claims and it does not replace `plan validate`, `run uat`, or
report verification.

## Discovery Flow

1. Read the target repository's local instructions first (`AGENTS.md`, specs,
   README, and UAT/runbook files when present).
2. Run `code-review` graph preflight from the target root using local SQLite
   state. Prefer an existing repo-owned graph if it is queryable; otherwise
   record the preflight output and fall back to direct source scan.
   When the graph is queryable, run focused graph-only `search-code` queries
   before direct scan to accelerate route, contract, and browser-harness
   discovery.
3. Inspect source/API evidence before authoring executable UAT semantics:
   - OpenAPI, Swagger, generated contract manifest, schema, or doc-route source
   - Playwright configuration and browser e2e harness files
   - frontend/backend binding env vars such as server host/port
   - backend route handlers or API server entrypoints
   - assistant-generation runtime, provider/model, no-reply boundary, and
     browser assistant-message evidence when the requested proof is richer than
     persisted user-message visibility
4. Inspect `preflightDecision`; if `sourceAvailable=true`, do not end the work
   with an insufficient-data verdict unless the graph preflight and direct
   source scan have both been recorded.
5. Convert discovered evidence into assertion candidates. A candidate is not a
   pass claim; it only says there is enough source evidence to author a concrete
   UI/API assertion.
6. Feed the evidence into a project profile or a hand-authored plan, then run the
   normal `uatdemo` gates.

## Helper Command

From a checkout of the skill bundle:

```bash
python3 .agents/skills/uat-demo-agent/scripts/inspect-target-source-api.py \
  --target-root /path/to/target/repo \
  --out temp/target-source-api-discovery/<target-id>.json
```

To create a target-maintainer handoff without claiming runtime readiness, also
write a Markdown summary:

```bash
python3 .agents/skills/uat-demo-agent/scripts/inspect-target-source-api.py \
  --target-root /path/to/target/repo \
  --out temp/target-source-api-discovery/<target-id>.json \
  --handoff-md temp/target-source-api-discovery/<target-id>-handoff.md
```

When the Markdown will be attached to a cross-repo CR or issue, redact the
machine-local absolute target path from the handoff while keeping the JSON
diagnostic local:

```bash
python3 .agents/skills/uat-demo-agent/scripts/inspect-target-source-api.py \
  --target-root /path/to/target/repo \
  --out temp/target-source-api-discovery/<target-id>.json \
  --handoff-md temp/target-source-api-discovery/<target-id>-handoff.md \
  --handoff-redact-local-root
```

If `code-review` is installed in a nonstandard place, pass:

```bash
python3 .agents/skills/uat-demo-agent/scripts/inspect-target-source-api.py \
  --target-root /path/to/target/repo \
  --review-cli /path/to/review-cli-linux-amd64
```

The helper emits `uatdemo-target-source-api-discovery/v1` JSON with:

- `codeReviewGraph`: graph preflight result and queryability boundary
- `codeReviewGraphQueries`: focused graph-only query results, or a skipped
  reason when graph state is not queryable
- `preflightDecision`: machine-readable instruction that direct source scan was
  required/completed and that an insufficient-data verdict is not allowed before
  this preflight is recorded
- `apiContracts`: API contract/doc-route candidates
- `frontendSurfaces`: Playwright or browser harness candidates
- `frontendBackendBindings`: env/config evidence that binds frontend to backend
- `assistantGenerationSurfaces`: static evidence for provider-backed assistant
  generation, browser assistant-message fixtures, and no-reply boundaries that
  must not be confused with generated assistant responses
- `candidateAssertions`: assertion families that can be authored next
- `blockedAssertions`: assertion families that are still missing evidence
- `claimBoundary`: static-analysis-only authority statement

The optional Markdown handoff repeats the same static-analysis boundary, lists
candidate/blocked assertions, and adds target-owned gates for assistant-generation
UI journeys. Use it for CR handoff to the target repo; do not treat it as a
`run uat` result or stakeholder-facing readiness proof.

## Code-Review Boundary

`code-review` graph output is static-analysis evidence. It can accelerate source
discovery and reduce broad manual search, but it cannot prove runtime readiness.

If graph preflight returns `graph_queryable=false` or recommends
`direct-source-only-until-indexed`, do not stop at "no data." Run the direct
source scan and record the graph gap as a discovery boundary. Refreshing the
graph is useful, but it is not required before producing bounded assertion
candidates from checked-out source files.

## `aclab-opencode` Example

For `<workspace-root>/projects/aclab/aclab-opencode`, the relevant target slice is the
original OpenCode web interface with `packages/gocode` as backend. Discovery
should look for:

- `packages/gocode/contracts/dist/manifest.json`
- `packages/gocode/internal/server/doc_handler.go`
- `packages/app/playwright.config.gocode.ts`
- `packages/gocode/e2e/run-web-e2e.ts`
- frontend env bindings such as `PLAYWRIGHT_SERVER_HOST`,
  `PLAYWRIGHT_SERVER_PORT`, and `VITE_OPENCODE_SERVER_HOST`

When those files are present, the next step is to author concrete API response
shape or UI visible-state assertions. Do not claim `aclab-opencode` browser UAT
has passed until the generated or hand-authored plan validates and `run uat`
produces verified report evidence.

For assistant-generation UI journeys, the helper may emit an
`assistant-generation-ui-journey` candidate only when checked-out source contains
both backend/session generation evidence and browser/UI evidence. That candidate
is still static-analysis-only: the target repo must define provider or
deterministic generation posture, assistant-response markers, selectors, live
`uatdemo plan validate` / `uatdemo run uat` evidence, screenshot bytes, and a
fail-closed report guard before any assistant-generation readiness claim.
