# Skill Integration Notes

This file explains how the global governance/documentation skills cooperate with the `uat-demo-agent` source repository and its packaged skill surface.

## Authority split

1. Global routing remains in `spec-master`.
2. Branch-spec authoring remains in `spec-driven-development`.
3. Stable registry/governance reconciliation remains in `spec-registry-manager`.
4. Packaged CLI execution, bounded proof runs, and source-repo publish/deploy operator lanes live with `uat-demo-agent`.
5. Consumer-doc generation remains in `user-manual-skill` and `project-review-skill`, but they must read this repo's guides and fixed entrypoints instead of inventing repo-local routing.

## Source-repo role

`aclab-uat-demo-agent` is both:

- the source repository for the packaged `uat-demo-agent` skill bundle
- the workspace that publishes tracked review/manual artifacts and bounded CLI proofs

Because of that, repo-specific cooperation notes belong here under the maintained deliverable skill source, not in a duplicate local routing matrix.

## Repo-local truth surfaces

When the active workspace is this source repo, the cooperating global skills should anchor to:

- `.agents/specs/SPECS.md`
- `.agents/specs/NEXT_STEPS.md`
- `.agents/specs/RTM.md`
- `docs/MANUAL_GENERATION_GUIDE.md`
- `docs/PROJECT_REVIEW_GUIDE.md`
- `.agents/skills/uat-demo-agent/references/commands.md`

## Fixed entrypoints

### Spec / governance

- Use `spec-master` to route the request.
- Use `spec-driven-development` for new follow-ons, resume, implementation, review, and closeout.
- Use `spec-registry-manager` only when the primary authority surface is `SPECS.md` registry reconciliation.

### Packaged CLI / bounded proof

- `python3 scripts/prove_skip_binary_refresh.py`
- `python3 scripts/prove_global_skill_cooperation_alignment.py`
- `python3 scripts/publish_repo_owned_skills.py report --all --compatibility-summary --require-known-proof-sources`
- `python3 scripts/publish_repo_owned_skills.py publish --skill uat-demo-agent --install-global --skip-binary-refresh`

### Tracked consumer docs

- `bash scripts/refresh_tracked_consumer_docs.sh`

`user-manual-skill` and `project-review-skill` should treat that refresh script plus the repo guides as the canonical repo-local cooperation surface.

## Non-goals

Do not copy global cross-skill routing policy into this repository.

Do not let `uat-demo-agent` replace `spec-master`, `spec-driven-development`, or `spec-registry-manager`.

Do not let manual/review skills infer readiness from `NEXT_STEPS.md` or task progress; they still depend on authoritative `review.md` posture.
