# Generic Project-Profile Onboarding

Use this guide when you need the **generic project-profile onboarding lane** for a target repository.

This lane is for reusable onboarding across repositories. It is not the repo-local maintainer lane used by `dogfood-self.md`.

## Inputs

Prepare a project profile JSON that conforms to `contract/project-profile.schema.json`.

The profile should describe:

- target project identity
- selected source documents
- manual/review path mapping
- fallback matrix
- bounded planning defaults

## Preparation Flow

If the target source repository is available and the profile needs executable
UI/API assertions, run target source/API discovery first:

```bash
python3 .agents/skills/uat-demo-agent/scripts/inspect-target-source-api.py \
  --target-root /path/to/target/repo \
  --out temp/target-source-api-discovery/<profile-id>.json
```

Use the resulting `candidateAssertions` and `blockedAssertions` to decide which
documents and fallback cases belong in the project profile. Do not convert a
candidate into an executable web step unless the evidence identifies concrete
route, locator, visible state, endpoint, status, or response-shape semantics.

From a workspace copy of the packaged skill bundle:

```bash
python3 .agents/skills/uat-demo-agent/scripts/prepare-project-profile-inputs.py \
  --profile temp/project-profile.json
```

This emits:

- `<profile-id>-manifest.json`
- `<profile-id>-request.json`

Then run:

```bash
${UATDEMO_BIN:-uatdemo} plan generate --manifest <profile-id>-manifest.json --request <profile-id>-request.json
${UATDEMO_BIN:-uatdemo} plan validate --file <generated-plan.json>
```

## Claim Boundary

Treat this lane as a reusable onboarding / draft-planning / bounded-validation surface.

Do **not** describe it as executable demo/UAT readiness unless later evidence proves the target repo also satisfies its runtime, manual, review, and target-owned completeness requirements.

For repo-local maintainer validation of `aclab-uat-demo-agent` itself, use `dogfood-self.md` instead.
