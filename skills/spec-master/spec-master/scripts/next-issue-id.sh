#!/usr/bin/env bash
# next-issue-id.sh — print the next free ISS-YYYY-NNN across ALL branches, not just
# the current one. Parallel spec lanes each append ISSUE_LOG rows on divergent bases,
# so looking only at the local ISSUE_LOG collides (this session hit exactly that).
# This scans every local + remote branch's ISSUE_LOG.md so the allocated id is globally free.
#
# Usage:  bash skills/spec-master/scripts/next-issue-id.sh [YEAR]
#         (YEAR defaults to the current year)
set -u

year="${1:-$(date +%Y 2>/dev/null || echo 2026)}"

# All refs whose committed ISSUE_LOG.md we should scan.
refs="$(git for-each-ref --format='%(refname)' refs/heads refs/remotes 2>/dev/null)"

ids="$(
  {
    # committed ISSUE_LOG.md on every branch
    [ -n "$refs" ] && git grep -hoE "ISS-${year}-[0-9]{3}" $refs -- '*ISSUE_LOG.md' 2>/dev/null
    # plus any uncommitted working-tree ISSUE_LOG in this worktree
    grep -rhoE "ISS-${year}-[0-9]{3}" .agents/specs/ISSUE_LOG.md 2>/dev/null
  } | grep -oE '[0-9]{3}$' | sort -un
)"

if [ -z "$ids" ]; then
  echo "No ISS-${year}-NNN found on any branch. Next free: ISS-${year}-001"
  exit 0
fi

max="$(printf '%s\n' "$ids" | tail -1)"
next="$(printf '%03d' $((10#$max + 1)))"
echo "Scanned $(printf '%s\n' "$refs" | grep -c . 2>/dev/null) branches."
echo "Highest used: ISS-${year}-${max}"
echo "NEXT FREE:    ISS-${year}-${next}"
echo
echo "(Allocate this id on your lane. If your branch's ISSUE_LOG is behind, add a"
echo " merge-reconciliation note — see skills/spec-master/references/concurrent-governance.md)"
