#!/usr/bin/env bash
# Print-parity guard for the stakeholder-artifact skill family.
#
# WHY: several skills generate SELF-CONTAINED HTML (inline <style>), so they cannot
# <link> the canonical print block at shared-governance/assets/print-friendly.css —
# each INLINES a copy. The core fix for the "dark bands print white-on-white /
# disappear" bug is `print-color-adjust: exact` inside an `@media print` rule. If a
# future edit drops or breaks that copy, the bug silently returns in one artifact.
# This guard fails when any curated print consumer is missing the fix.
# (Extends ISSUE_LOG ISS-2026-004 to the print cluster in aclab-opencode-config.)
#
# It is an INVARIANT check, not byte-identity: the inlined blocks legitimately differ
# in indentation and skill-specific extra rules, so we assert the disappearing-bug
# INVARIANT (an @media print rule + `print-color-adjust: exact`) is present, rather
# than forcing whitespace-exact copies (which would be fragile and false-positive).
#
# Usage:  bash skills/shared-governance/scripts/check_print_parity.sh
# Exit:   0 = every consumer carries the fix; 1 = a consumer is missing it.
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Canonical source of truth (must itself carry the invariant).
CANONICAL="shared-governance/assets/print-friendly.css"

# Self-contained HTML print consumers that MUST inline the fix.
# Add a file here when a new stakeholder-artifact generator adopts the canonical block.
CONSUMERS=(
  "shared-governance/assets/print-friendly.css"
  "marketing-showcase-creator/assets/showcase-print.css"
  "project-review-skill/code/report-template.html"
  "project-review-naelt/code/report-template.html"
  "user-manual-skill/assets/manual-template.html"
  "ba-analyst-skill/index.html"
  "ba-analyst-skill/templates/report-problem-domain.html"
  "ba-analyst-skill/templates/report-solution-domain.html"
  "spec-master/index.html"
  "spec-master/manual.html"
  "spec-driven-development/index.html"
  "spec-driven-development/manual.html"
)

fail=0
for rel in "${CONSUMERS[@]}"; do
  f="$SKILLS_DIR/$rel"
  if [ ! -f "$f" ]; then
    echo "MISSING  $rel (listed consumer not found)"; fail=1; continue
  fi
  if ! grep -q "@media print" "$f"; then
    echo "NO-PRINT $rel (no @media print block)"; fail=1; continue
  fi
  if ! grep -q "print-color-adjust: *exact" "$f"; then
    echo "NO-FIX   $rel (@media print present but missing print-color-adjust:exact)"; fail=1; continue
  fi
  echo "OK       $rel"
done

echo "----"
if [ "$fail" -eq 0 ]; then
  echo "print-parity: all ${#CONSUMERS[@]} consumers carry the disappearing-bug fix."
else
  echo "print-parity: FAIL — a consumer is missing the print-color-adjust:exact fix (see above)."
fi
exit "$fail"
