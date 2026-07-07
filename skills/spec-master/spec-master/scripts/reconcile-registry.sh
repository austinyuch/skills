#!/usr/bin/env bash
# reconcile-registry.sh — pre-merge reconciliation aid for the structured governance
# files that CANNOT be union-merged (SPECS.md, NEXT_STEPS.md). With many parallel lanes,
# a big merge to main needs a map of "which branch declares which spec section / issue id",
# and where they collide. This is read-only reporting; it changes nothing.
#
# Usage:  bash skills/spec-master/scripts/reconcile-registry.sh [--year YYYY]
# Companion to next-issue-id.sh (ids) and concurrent-governance.md (protocol).
set -u

year="2026"
[ "${1:-}" = "--year" ] && year="${2:-2026}"

refs="$(git for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null)"
[ -z "$refs" ] && { echo "no local branches"; exit 0; }
total="$(printf '%s\n' "$refs" | grep -c .)"
# Interpretation: an item on ALL $total branches is the shared BASE (inherited, fine).
# An item on a SUBSET (1 < n < total) is DIVERGENT across lanes → ⚠ reconcile.
# An item on exactly 1 branch is that lane's own new work (fine).

echo "=================================================================="
echo "SPECS.md — spec sections declared per branch (### N. <name>)"
echo "=================================================================="
tmp="$(mktemp)"
for b in $refs; do
  # extract '### N. spec-name' headers from that branch's SPECS.md
  git show "$b:.agents/specs/SPECS.md" 2>/dev/null \
    | grep -oE '^### [0-9.]+\.? [a-z0-9-]+' \
    | sed -E 's/^### [0-9.]+\.? //' \
    | while read -r name; do echo "$name|$b"; done >> "$tmp"
done

echo "-- ⚠ = DIVERGENT (on a subset of lanes → reconcile); (base) = on all; else lane-own --"
cut -d'|' -f1 "$tmp" | sort -u | while read -r name; do
  [ -z "$name" ] && continue
  n="$(grep -cE "^${name}\|" "$tmp")"
  if [ "$n" -eq "$total" ]; then mark="  (base) "; brief="on all $total";
  elif [ "$n" -gt 1 ]; then mark="⚠ DIVERGE"; brief="$(grep -E "^${name}\|" "$tmp" | cut -d'|' -f2 | sort -u | paste -sd, -)";
  else mark="  lane   "; brief="$(grep -E "^${name}\|" "$tmp" | cut -d'|' -f2)"; fi
  printf "  %s %-42s %s\n" "$mark" "$name" "$brief"
done
rm -f "$tmp"

echo ""
echo "=================================================================="
echo "ISSUE_LOG — ISS-${year}-NNN ids per branch (duplicate id on 2 branches = collision)"
echo "=================================================================="
dtmp="$(mktemp)"
for b in $refs; do
  git show "$b:.agents/specs/ISSUE_LOG.md" 2>/dev/null \
    | grep -oE "ISS-${year}-[0-9]{3}" | sort -u \
    | while read -r id; do echo "$id|$b"; done >> "$dtmp"
done
echo "-- ⚠ = same id on a SUBSET of lanes (genuine collision → renumber one at merge);"
echo "   ids on all $total lanes are the shared base (same issue, fine) --"
anycol=0
for id in $(cut -d'|' -f1 "$dtmp" | sort -u); do
  [ -z "$id" ] && continue
  n="$(grep -cE "^${id}\|" "$dtmp")"
  if [ "$n" -gt 1 ] && [ "$n" -lt "$total" ]; then
    echo "  ⚠ $id : $(grep -E "^${id}\|" "$dtmp" | cut -d'|' -f2 | sort -u | paste -sd, -)"
    anycol=1
  fi
done
[ "$anycol" = "0" ] && echo "  (no divergent id collisions — good)"
rm -f "$dtmp"

echo ""
echo "First-pass aid: ⚠ includes branch-CHAIN inheritance (a lane branched off another"
echo "  inherits its rows). A TRUE collision = same id/spec on lanes that are NOT ancestors"
echo "  of each other with different content — confirm by ancestry/content before renumbering."
echo "NEXT_STEPS.md is a rolling memo — reconcile by hand to the LATEST lane's state."
echo "ISSUE_LOG.md / RTM.md auto-union on merge (.gitattributes); run a dedupe pass after."
echo "Protocol: skills/spec-master/references/concurrent-governance.md"
