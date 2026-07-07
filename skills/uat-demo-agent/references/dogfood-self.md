# Self-Dogfood Inputs

Use `bash .agents/skills/uat-demo-agent/scripts/prepare-self-dogfood-inputs.sh` when you want to exercise the packaged `uatdemo` skill surface against this repository itself.

This is a **repo-local project-profile lane** for maintainers of `aclab-uat-demo-agent`.

Treat it as a maintainer validation harness for this workspace's own specs/manual/review surfaces, not as the generic default path for other target repositories.

Suggested follow-on:

```bash
bash ./scripts/uatdemo.sh plan generate \
  --manifest temp/uat-demo-self-dogfood-manifest.json \
  --request temp/uat-demo-self-dogfood-request.json \
  > temp/uat-demo-self-dogfood-plan.json
bash ./scripts/uatdemo.sh plan validate --file temp/uat-demo-self-dogfood-plan.json
bash .agents/skills/uat-demo-agent/scripts/classify-self-dogfood-plan.sh \
  temp/uat-demo-self-dogfood-plan.json
```

The script emits:

- `temp/uat-demo-self-dogfood-manifest.json`
- `temp/uat-demo-self-dogfood-request.json`

The generated manifest anchors the planner to this workspace's current productization chain:

- `.agents/specs/SPECS.md`
- `.agents/specs/uat-demo-uat-evidence-and-recording/{requirements,design}.md`
- `.agents/specs/uat-demo-manual-review-evidence-publishing/{requirements,design}.md`
- `.agents/specs/uat-demo-manual-review-storytelling-automation/{requirements,design}.md`
- `.agents/specs/uat-demo-manual-dual-language-generation/{requirements,design}.md`
- `docs/review/index.html`
- `docs/manual/en/index.html`
- `docs/manual/zh-tw/index.html`

## Classification Rule

Treat this lane as **planning/validation proof** first.

This lane is intentionally narrower than the generic cross-project product surface. It proves that this repository can prepare its own self-dogfood inputs and classify the resulting draft honestly; it does not define the generic onboarding contract for arbitrary target repos.

Classify the result as `valid-draft` when all of the following are true:

1. `plan generate` produces `temp/uat-demo-self-dogfood-plan.json`
2. `plan validate` succeeds for that file
3. `bash .agents/skills/uat-demo-agent/scripts/classify-self-dogfood-plan.sh temp/uat-demo-self-dogfood-plan.json` prints `valid-draft`

Do **not** describe this result as `run demo` / `run uat` readiness unless a later follow-on changes planner behavior and verification evidence accordingly.

Do **not** describe this repo-local maintainer lane as the generic success path for cross-project adoption. If a future target repo needs reusable onboarding, that should be handled through a dedicated generic project-profile mechanism rather than by copying this self-dogfood helper wholesale.
