# Gemini Config Skill Root Closeout

## Scope

Close `CR-SKILL-SOURCE-GEMINI-ROOT-001` by correcting target-owned source,
adding a recurrence guard, and republishing the affected skills from merged
source.

## Implementation

- Replaced active `~/.gemini/antigravity/skills` guidance in
  `skills/spec-master/WORKFLOW.md` and
  `skills/spec-driven-development/SKILL.md` with
  `~/.gemini/config/skills`.
- Added a repo-wide fail-closed check to `scripts/ci-checks.sh`. The check scans
  active skill, script, CLI, and documentation sources for the legacy target.
- Merged implementation PR #5 to `main` at
  `960073c0f062f455c24dd203f061c516f7e49775`.

## Verification

- `bash scripts/ci-checks.sh`: PASS, including the new eighth policy section.
- Skill Creator `quick_validate.py`: PASS for `spec-master` and
  `spec-driven-development`.
- Pre-commit hook: PASS.
- Pre-push hook: PASS; optional `security-risk-reviewer` was unavailable and
  explicitly skipped.
- Hosted PR `repo checks`: PASS.
- Active-source fixed-string grep for the complete legacy path: no matches.
- `git diff --check`: PASS.

## Global Publish Readback

Published only `spec-master` and `spec-driven-development` from merged source
to the six canonical roots:

```text
~/.codex/skills
~/.claude/skills
~/.config/opencode/skills
~/.kiro/skills
~/.agents/skills
~/.gemini/config/skills
```

For every root, `diff -qr` against merged source passed. Cross-root SHA-256
readback:

```text
spec-master/WORKFLOW.md
6889b1272aeeae89e23c6eb1e2dbe99aa6939ebbf4d026e514fd0961c531ed5b

spec-driven-development/SKILL.md
550f1d39216c585f6cda72289efecee1743eb1858a8d4d70b4f6c6bff940b26f
```

No affected installed copy contains the legacy path. No affected skill was
published under `~/.gemini/antigravity/skills`.

## Review And Retrospective

The original CR correctly separated profile-root guidance from runtime
discovery. The source fix was small, but direct global patching would have left
the repository stale. Merging first and publishing only the two affected skill
directories kept source authority intact and avoided reinstalling unrelated
skills or deleting out-of-band binaries.

The recurrence guard initially matched its own full legacy sentinel. Building
the runtime sentinel from source fragments preserves exact fail-closed matching
without retaining a misleading complete target literal in the repository.

## Non-Claims

- This does not prove Gemini or Antigravity runtime skill discovery.
- This does not alter other target-owned Gemini roots listed by other skills.
- This does not rebuild or publish `review-cli`, `xreview`, or `uatdemo`
  binaries.
- This does not publish maintainer-only UAT skills.
