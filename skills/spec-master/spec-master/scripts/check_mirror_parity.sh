#!/usr/bin/env bash
# Mirror-parity guard for the spec-master ↔ spec-driven-development skill pair.
#
# WHY: spec-master (router) and spec-driven-development (workflow) intentionally keep
# byte-identical copies of several shared reference docs. Every edit must be mirrored by
# hand, so they silently drift. This guard fails on drift for the CURATED list below.
# (Implements ISSUE_LOG ISS-2026-004 in aclab-opencode-config.)
#
# It is deliberately an ALLOWLIST, not "all same-named files": some same-named files
# legitimately differ (e.g. GIT_WORKTREE_* — see KNOWN_DIFFERS) and must NOT be forced equal.
#
# Usage:  bash skills/spec-master/scripts/check_mirror_parity.sh
# Exit:   0 = all mirrors identical; 1 = drift found (prints the diffs).
set -u

# skills root = two levels up from this script's dir (skills/spec-master/scripts/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
A="$SKILLS_DIR/spec-master"
B="$SKILLS_DIR/spec-driven-development"

# Files (relative to each skill root) that MUST be byte-identical across both skills.
MIRRORS=(
  "references/CROSS_AGENT_REVIEW.md"
  "references/FRONTEND_DESIGN_REVIEW.md"
  "reference/GRAPH_ASSISTED_PLANNING.md"
  "references/ponytail-yagni-ladder.md"
  "references/requirement-interview-depth.md"
  "reference/AC_FORMAT_GUIDE.md"
  "reference/DEMO_READINESS_GUIDE.md"
  "reference/NEXT_STEPS_TEMPLATE.md"
  "reference/SPEC_GOVERNANCE_ARTIFACTS_GUIDE.md"
  "reference/TEST_GOVERNANCE_GUIDE.md"
  # Adjudicated 2026-07-03 (ISS-2026-004): the prior drift in these two was only
  # pointer STYLE (prose "shared-governance skill 的 …" vs relative "../../shared-governance/…")
  # pointing at the same shared-governance refs — cosmetic, not substantive. Unified on the
  # prose style (layout-independent, matches WORKFLOW.md) and now enforced as mirrors.
  "reference/GIT_WORKTREE_GUIDE.md"
  "reference/GIT_WORKTREE_TEMPLATES.md"
)

# Same-named files that currently DIFFER and are NOT asserted equal here. If a future
# review decides these should mirror, move them into MIRRORS; if they are intentionally
# distinct, leave them here so the guard's scope stays honest.
KNOWN_DIFFERS=(
  # (empty) — the former GIT_WORKTREE entries were adjudicated as cosmetic drift and
  # promoted to MIRRORS above (ISS-2026-004 sub-item (b), closed 2026-07-03).
)

fail=0
missing=0
for rel in "${MIRRORS[@]}"; do
  fa="$A/$rel"; fb="$B/$rel"
  if [ ! -f "$fa" ] || [ ! -f "$fb" ]; then
    echo "MISSING  $rel (expected in both skills)"; missing=1; continue
  fi
  if diff -q "$fa" "$fb" >/dev/null 2>&1; then
    echo "OK       $rel"
  else
    echo "DRIFT    $rel"
    diff -u "$fa" "$fb" | sed 's/^/    /' | head -40
    fail=1
  fi
done

echo "----"
if [ "${#KNOWN_DIFFERS[@]}" -gt 0 ]; then
  echo "note: ${#KNOWN_DIFFERS[@]} same-named file(s) intentionally excluded (not asserted equal): ${KNOWN_DIFFERS[*]}"
fi

if [ "$fail" -ne 0 ] || [ "$missing" -ne 0 ]; then
  echo "RESULT: FAIL — mirror drift or missing file. Re-sync the two skills before commit."
  exit 1
fi
echo "RESULT: PASS — all ${#MIRRORS[@]} curated mirrors are byte-identical."
exit 0
