# CR-SKILL-SOURCE-GEMINI-ROOT-001 — update upstream Gemini/Antigravity profile root

- **Status**: Closed — source merged and global copies republished/verified
- **Date**: 2026-07-11
- **Source issue**: `ISSUE-CU-145`
- **Requester / source repo**: `aclab-uat-demo-agent-private`
- **Target repo**: `aclab/skills`
- **Change type**: cross-repo skill-source governance / profile-root correction

## Context

This repository's repo-owned `uat-demo-agent` publisher now uses Gemini/Antigravity's
canonical relocated skill root:

```text
~/.gemini/config/skills
```

This is a Gemini/Antigravity profile-root correction, not a request to add or
keep a separate global publish folder. The legacy Antigravity-specific path:

```text
~/.gemini/antigravity/skills
```

is not a current publish or discovery target. A follow-up source scan found
stale Gemini/Antigravity path references in the upstream skill-source
repository, not in this repository's repo-owned publish target catalog.

## Observed Stale References

Current read-only source scan on 2026-07-11 confirmed `/home/ac/projects/aclab/skills`
was clean on `main` at `e868116fd130d4f25994629dd9d0d8c5fab68243`
(`origin/main` same commit). The target remote currently exposes `main` plus
`fix/cross-agents-bridge-hook-regression`; there is no `origin/dev` head to
compare for this CR. The `main` source still contained these active stale
references:

- `skills/spec-master/WORKFLOW.md:312`
- `skills/spec-driven-development/SKILL.md:433`
- `skills/code-review/CODE_REVIEW_LINEAGE.md:24`
- `skills/code-review/CODE_REVIEW_LINEAGE.md:57`
- `skills/cross-agent-review/scripts/publish.sh:43`

Current stale pattern:

```text
~/.gemini/antigravity/skills
```

Expected canonical pattern:

```text
~/.gemini/config/skills
```

Installed global copies are currently mixed: installed `code-review` and
`cross-agent-review` copies already mention `~/.gemini/config/skills`, while
installed `spec-master` and `spec-driven-development` copies under both
`~/.codex/skills` and `~/.agents/skills` still mention
`~/.gemini/antigravity/skills`. Source-owned republish is still required.

## Requested Delta

1. Replace the legacy Gemini/Antigravity skill root in source-owned docs,
   workflow guidance, lineage diagrams, and publish scripts with the relocated
   `~/.gemini/config/skills` profile root.
2. Ensure generated or published global skill copies are refreshed from the
   source repo after the source change lands.
3. Preserve any currently supported non-Gemini roots unless the owning repo has
   separate evidence that they changed.
4. Add or update a regression check so future source changes do not reintroduce
   `~/.gemini/antigravity/skills` as a publish/discovery target or global root.
5. Prefer source-first republish over direct hand-patching installed global
   copies, so the source repo and published copies do not drift.

## Acceptance Criteria

1. Source grep in the target repo finds no active publish/discovery target that
   points at `~/.gemini/antigravity/skills`.
2. The canonical Gemini/Antigravity profile root is `~/.gemini/config/skills`.
3. Published global copies of `spec-master`, `spec-driven-development`,
   `code-review`, and `cross-agent-review` no longer teach the stale path.
4. Any remaining legacy-path mention is explicitly labeled historical or
   excluded, not a target to write or scan.
5. Source-owned verification records the grep command/result used to prove the
   stale path is gone from active target files.

## Source Repo Boundary

This source repo should not patch the target repo or installed global runtime
copies directly. The target repo owns its skill-source files and publish flow.
Until the target repo lands and republishes this change, this repo should treat
the stale upstream references as an open cross-repo governance gap, not as a
`uat-demo-agent` publish defect.

## Non-Claims

- This CR does not prove Gemini/Antigravity runtime discovery.
- This CR does not request another `uat-demo-agent` binary rebuild.
- This CR does not authorize publishing maintainer-only skills.
- This CR does not change the target-owned `ISSUE-CU-138` assistant-generation
  proof boundary.

## Source Repo Refresh Evidence

See
`.agents/specs/uat-demo-repo-owned-skill-publisher/reports/2026-07-11-skill-source-gemini-root-cr-refresh.md`.

## Target Implementation

Target-owned implementation now corrects the active references in
`skills/spec-master/WORKFLOW.md` and
`skills/spec-driven-development/SKILL.md` to
`~/.gemini/config/skills`.

`scripts/ci-checks.sh` now includes a fail-closed repo-wide policy check that
rejects the legacy Antigravity-specific skill root under active skill, script,
CLI, and documentation sources. The sentinel is assembled at runtime so the
guard itself does not preserve a complete legacy target literal in source.

Pre-merge verification:

- `bash scripts/ci-checks.sh`: PASS (8/8 sections).
- `quick_validate.py skills/spec-master`: PASS.
- `quick_validate.py skills/spec-driven-development`: PASS.
- active-source legacy-root grep: no matches.
- `git diff --check`: PASS.

## Closure Evidence

The implementation merged to target `main` through PR #5 at
`960073c0f062f455c24dd203f061c516f7e49775`.

From that merged source, `spec-master` and `spec-driven-development` were
republished in flat layout to:

- `~/.codex/skills`
- `~/.claude/skills`
- `~/.config/opencode/skills`
- `~/.kiro/skills`
- `~/.agents/skills`
- `~/.gemini/config/skills`

Each installed skill directory is byte-for-byte aligned with merged source by
`diff -qr`. Cross-root readback recorded these stable hashes:

- `spec-master/WORKFLOW.md`: `6889b1272aeeae89e23c6eb1e2dbe99aa6939ebbf4d026e514fd0961c531ed5b`
- `spec-driven-development/SKILL.md`: `550f1d39216c585f6cda72289efecee1743eb1858a8d4d70b4f6c6bff940b26f`

No installed affected copy teaches the legacy Antigravity-specific path, and
no `spec-master` or `spec-driven-development` directory was published beneath
`~/.gemini/antigravity/skills`.

See
`.agents/specs/change-requests/reports/2026-07-11-gemini-config-root-closeout.md`.
