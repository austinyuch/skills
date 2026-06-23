---
name: uat-demo-agent-packaging
description: Use this internal workspace skill when maintainers need to package, verify, release, or install the deliverable `uat-demo-agent` skill bundle from the canonical workspace bundle to the global opencode skills directory. Trigger when the user asks to release the skill, refresh bundled multi-arch binaries, install/update the global skill, or verify workspace/global bundle consistency.
---

# UAT Demo Agent Packaging

This is a **maintainer-only packaging skill** for the `uat-demo-agent` deliverable bundle. Use it for the deterministic release/install/verify pipeline, not for running demo/UAT plans themselves.

## What this skill owns

1. release the canonical workspace bundle from `.agents/skills/uat-demo-agent/`
2. verify required vs denied bundle content
3. publish a verified bundle to `dist/uat-demo-agent-*`
4. install the verified bundle to `~/.config/opencode/skills/uat-demo-agent/`
5. smoke-check workspace and global bundle states
6. maintain the bundled multi-arch binaries and their release hygiene contract

## Use this skill when

- the user asks to package or release the deliverable skill
- the bundled multi-arch binaries need refreshing
- the global skill install should be updated
- you need to verify that workspace and global bundles are consistent
- you need the current binary/release hygiene contract before publishing
- you need to understand when shared publisher `--skip-binary-refresh` is appropriate

## Do not use this skill when

- the user wants to generate/validate/run/show plans or reports — use `uat-demo-agent` instead
- the user wants planner/runtime/productization changes outside deploy/install/verify
- the user wants to review/publish the whole repo-owned skills matrix — use `uat-demo-skill-publisher` instead

## Canonical commands

- `make preflight-uat-demo-agent-skill`
- `python3 scripts/release_uatdemo_skill_bundle.py`
- `python3 scripts/release_uatdemo_skill_bundle.py --no-sync`
- `python3 scripts/verify_uatdemo_skill_bundle.py --bundle-root .agents/skills/uat-demo-agent`
- `python3 scripts/install_uatdemo_skill_bundle.py`
- `make install-uat-demo-agent-skill`
- `python3 scripts/verify_uatdemo_skill_bundle.py`
- `make preflight-uat-demo-target-governance-template-skill`
- `python3 scripts/release_target_governance_template_skill.py`
- `python3 scripts/verify_target_governance_template_skill.py`
- `python3 scripts/install_target_governance_template_skill.py`

## Release/verify/install workflow

1. Ensure the canonical workspace bundle under `.agents/skills/uat-demo-agent/` is up to date.
2. Run `make preflight-uat-demo-agent-skill` to execute the self-dogfood helper regression before packaging.
3. Run the release script to build the multi-arch `uatdemo` matrix, stage the bundle, verify it structurally, publish `dist/uat-demo-agent-*` outputs, and then authoritatively verify the published bundle against `release-manifest.json` and `checksums.txt`.
4. Use `python3 scripts/release_uatdemo_skill_bundle.py --no-sync` when you explicitly need a fresh verified bundle without syncing refreshed binaries back into `.agents/skills/uat-demo-agent/scripts/*`.
5. Run workspace-bundle verification if you need a direct check of the canonical source.
6. Install from the verified `dist/uat-demo-agent-latest/uat-demo-agent/` bundle into `~/.config/opencode/skills/uat-demo-agent/` using the backup-first installer helper. The previous global bundle should be preserved for rollback until the new install verifies cleanly.
7. Run global verification after install; do not treat PATH-only CLI smoke as proof that the global skill is installed correctly. Installed copies should carry release metadata so verification remains authoritative.
8. Read [references/release-hygiene.md](./references/release-hygiene.md) before changing bundled binaries, releasing from a dirty tree, or using the shared publisher lane to refresh `uat-demo-agent`.

## Guardrails

1. Keep the deliverable in folder-file structure. Do not convert it to a `.skill` single file.
2. Treat `.agents/skills/uat-demo-agent/` as the canonical workspace source of truth.
3. Install only from a verified release bundle, never by directly copying arbitrary live workspace state.
4. Multi-arch bundled binaries are required for the deliverable skill bundle.
5. The installed `uatdemo` wrapper now enforces target-project `.gitignore` coverage for its project-local runtime directory. Default `.uatdemo/` and configured `temp/...` state paths must be ignored in consumer projects.
6. Runtime state belongs in the target workspace or an agent-neutral user state directory, never under agent-specific skill install folders.
7. The companion `uat-demo-target-governance-template` bundle is template-only; keep its release/install/verify lane separate from the binary-oriented `uat-demo-agent` bundle, even though both are repo-owned.
8. `--no-sync` / shared publisher `--skip-binary-refresh` only controls workspace sync-back. It does not weaken preflight, dist verification, or install verification requirements.
