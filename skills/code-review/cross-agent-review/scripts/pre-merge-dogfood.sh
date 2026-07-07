#!/usr/bin/env sh
# pre-merge-dogfood.sh — turn the "cross-family review before merge" discipline into a runnable GATE.
# The last four CRs each had a different-family peer catch a real defect green tests missed; this makes
# that step executable and enforceable instead of a habit. Two checks:
#   (1) CAP-8 capability gate — run eval-cap8-security.sh (the security-lens matrix). If it FAILs, the
#       reviewer capability regressed → BLOCK. If it cannot run (no peer / grader unavailable → exit 77),
#       enforce mode also BLOCKS by default (fail-closed; see below) — override with --allow-degraded.
#   (2) Diff review — drive a different-family peer over the ACTUAL change (git diff BASE...HEAD) with an
#       adversarial security+correctness lens, then a strict model-verdict: BLOCK only on a real
#       HIGH-severity finding (leak / injection / traversal / fail-open / data-loss / crash), ALLOW for
#       style/nits/none. On a peer error the diff review warns (does not block).
# Default ENFORCE (non-zero exit blocks a pre-push hook); --advisory downgrades to warn-only.
# Wire as .git/hooks/pre-push, or run manually before opening the merge PR.
# [CR-2026-07-04-074, promoting the CR-070..073 dogfood cadence to a gate]
#
# FAIL-CLOSED for the security-capability check: if the CAP-8 matrix cannot run (no peer / grader
# unavailable → exit 77), enforce mode BLOCKS by default — a security gate that silently degrades to
# warn-only when its checker is down is itself a hole. Use --allow-degraded to knowingly accept that
# risk (e.g. peer CLI temporarily offline), or --advisory to warn on everything.
#
# Usage: pre-merge-dogfood.sh [--base REF] [--peer NAME] [--advisory] [--allow-degraded] [--quick]
#   --base REF        diff base (default: origin/main, else main)
#   --peer NAME       force peer CLI (codex|claude|opencode; default: first found)
#   --advisory        warn on findings but always exit 0 (for gradual rollout)
#   --allow-degraded  a peer-unavailable CAP-8 SKIP warns instead of blocking (fail-open, opt-in)
#   --quick           skip the CAP-8 capability matrix (slow, ~6 peer calls); run only the diff
#                     review. For a fast pre-push hook — the CAP-8 matrix belongs in the pre-MERGE run.
# Exit: 0 = allowed · 1 = BLOCKED (enforce mode) · 2 = usage
set -eu
here=$(dirname -- "$0"); here=$(cd -- "$here" && pwd)

base=""; peer=""; advisory=0; allow_degraded=0; quick=0
while [ $# -gt 0 ]; do
  case "$1" in
    --base) [ $# -ge 2 ] || { echo "--base needs a value" >&2; exit 2; }; base="$2"; shift 2 ;;
    --peer) [ $# -ge 2 ] || { echo "--peer needs a value" >&2; exit 2; }; peer="$2"; shift 2 ;;
    --advisory) advisory=1; shift ;;
    --allow-degraded) allow_degraded=1; shift ;;
    --quick) quick=1; shift ;;
    -h|--help) echo "usage: pre-merge-dogfood.sh [--base REF] [--peer NAME] [--advisory] [--allow-degraded] [--quick]"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$base" ]; then
  if git rev-parse --verify -q origin/main >/dev/null; then base="origin/main"; else base="main"; fi
fi
if [ -z "$peer" ]; then
  for cand in codex claude opencode; do
    if command -v "$cand" >/dev/null 2>&1; then peer="$cand"; break; fi
  done
fi

blocked=0

if [ "$quick" -eq 1 ]; then
  echo "=== [1/2] CAP-8 capability gate — SKIPPED (--quick; run the full gate before merging) ==="
else
  echo "=== [1/2] CAP-8 capability gate (eval-cap8-security.sh) ==="
  cap_rc=0
  if [ -n "$peer" ]; then
    sh "$here/eval-cap8-security.sh" --peer "$peer" >&2 || cap_rc=$?
  else
    sh "$here/eval-cap8-security.sh" >&2 || cap_rc=$?
  fi
  case "$cap_rc" in
    0)  echo "  CAP-8: PASS" ;;
    77) if [ "$allow_degraded" -eq 1 ]; then
          echo "  CAP-8: SKIP (peer/grader unavailable) — WARN only (--allow-degraded)" >&2
        else
          echo "  CAP-8: SKIP (peer/grader unavailable) — cannot verify the security capability → BLOCK" >&2
          echo "  (fail-closed; pass --allow-degraded to knowingly proceed without the check)" >&2
          blocked=1
        fi ;;
    *)  echo "  CAP-8: FAIL — reviewer capability regressed → BLOCK" >&2; blocked=1 ;;
  esac
fi

echo "=== [2/2] diff review of the actual change (base=$base) ==="
diff=$(git diff "$base"...HEAD 2>/dev/null || git diff "$base" 2>/dev/null || true)
if [ -z "$diff" ]; then
  echo "  no diff vs $base — nothing to review" >&2
elif [ -z "$peer" ]; then
  echo "  no peer CLI on PATH — cannot review the diff. WARN only, not blocking." >&2
else
  review_prompt="You are an INDEPENDENT reviewer from a DIFFERENT model family. Review ONLY this diff for HIGH-severity security or correctness defects (leak, injection, path traversal, fail-open verification, data loss, crash, auth bypass). List each as '- file:line — issue'. If none, say 'no material findings'.

$diff"
  review=$(mktemp 2>/dev/null || echo /tmp/pmd_review.$$)
  rc=0
  case "$peer" in
    codex)    codex exec --skip-git-repo-check "$review_prompt" < /dev/null > "$review" 2>/dev/null || rc=$? ;;
    claude)   claude -p "$review_prompt" < /dev/null > "$review" 2>/dev/null || rc=$? ;;
    opencode) opencode run "$review_prompt" < /dev/null > "$review" 2>/dev/null || rc=$? ;;
  esac
  if [ "$rc" -ne 0 ] || [ ! -s "$review" ]; then
    echo "  peer '$peer' errored/no output — WARN only, not blocking." >&2
  else
    echo "----- peer diff review ($peer) -----" >&2; cat "$review" >&2; echo "------------------------------------" >&2
    verdict_prompt="Below is a security/correctness review of a code change. Does it contain at least one UNADDRESSED HIGH-severity defect (leak, injection, path traversal, fail-open, data loss, crash, auth bypass)? Answer EXACTLY BLOCK or ALLOW on the first line, then one short reason. Treat style/nits/no-findings as ALLOW.

REVIEW:
$(cat "$review")"
    verdict=$(mktemp 2>/dev/null || echo /tmp/pmd_verdict.$$)
    vrc=0
    case "$peer" in
      codex)    codex exec --skip-git-repo-check "$verdict_prompt" < /dev/null > "$verdict" 2>/dev/null || vrc=$? ;;
      claude)   claude -p "$verdict_prompt" < /dev/null > "$verdict" 2>/dev/null || vrc=$? ;;
      opencode) opencode run "$verdict_prompt" < /dev/null > "$verdict" 2>/dev/null || vrc=$? ;;
    esac
    if [ "$vrc" -ne 0 ] || [ ! -s "$verdict" ]; then
      echo "  diff-verdict grader errored — WARN only, not blocking." >&2
    else
      first=$(sed -n '1p' "$verdict" | tr '[:lower:]' '[:upper:]')
      echo "  diff verdict: $(sed -n '1,2p' "$verdict")" >&2
      case "$first" in
        *BLOCK*) echo "  diff review → BLOCK (high-severity finding)" >&2; blocked=1 ;;
        *ALLOW*) echo "  diff review → ALLOW" ;;
        *) echo "  diff verdict unparseable — WARN only, not blocking." >&2 ;;
      esac
    fi
    rm -f "$verdict"
  fi
  rm -f "$review"
fi

echo "=== pre-merge dogfood: $( [ "$blocked" -eq 0 ] && echo ALLOWED || echo BLOCKED ) ==="
if [ "$blocked" -ne 0 ] && [ "$advisory" -eq 0 ]; then
  echo "BLOCKED: resolve the findings above or re-run with --advisory to override." >&2
  exit 1
fi
[ "$blocked" -eq 0 ] || echo "(advisory mode: not blocking despite findings)" >&2
exit 0
