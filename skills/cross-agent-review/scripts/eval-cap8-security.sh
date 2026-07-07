#!/usr/bin/env sh
# eval-cap8-security.sh — RUNNABLE CAP-8 adversarial-security eval MATRIX for the Localhost method.
# Promotes the CAP-8 lens from prose (references/eval.md) into an executable gate over a MATRIX of
# seeded defect classes — not one. For each case it seeds a script diff carrying a real security
# defect, drives a DIFFERENT-family peer CLI with a security-specific prompt, and grades (via a
# model-grader, authoritative) that the review NAMES the defect + its failure mode. This is the
# "what leaks / where can it write / what can be injected / what fails open?" question capability
# evals don't ask unless prompted. [CR-2026-07-04-073 (single case); CR-2026-07-04-074 (matrix)]
#
# Cases (3 defect + 1 false-positive guard):
#   leak-traversal    auth token sent to an arbitrary host + unvalidated name into a path (CR-071 class)
#   command-injection caller-controlled input interpolated into `sh -c` (shell command injection)
#   fail-open         a checksum mismatch that only WARNS and installs anyway (fail-open verification)
#   clean             a BENIGN change — the review must NOT fabricate a defect (cry-wolf guard, CAP-3 analogue)
#
# Exit codes (autotools-style so CI can distinguish a real fail from an unavailable peer):
#   0  = PASS (every run case's peer named its defect)
#   1  = FAIL (some case's peer reviewed but missed it — a genuine regression)
#   2  = usage error
#   77 = SKIP (no peer CLI, or every case skipped because the peer errored) — reported LOUDLY
#
# Usage: eval-cap8-security.sh [--peer codex|claude|opencode] [--case NAME] [--keep]
#   --peer NAME  force a peer CLI (default: first of codex, claude, opencode found on PATH)
#   --case NAME  run only one case (default: all three)
#   --keep       keep temp seed dirs for inspection (default: clean up)
set -eu

peer=""
keep=0
only_case=""
while [ $# -gt 0 ]; do
  case "$1" in
    --peer) [ $# -ge 2 ] || { echo "--peer needs a value" >&2; exit 2; }; peer="$2"; shift 2 ;;
    --case) [ $# -ge 2 ] || { echo "--case needs a value" >&2; exit 2; }; only_case="$2"; shift 2 ;;
    --keep) keep=1; shift ;;
    -h|--help) echo "usage: eval-cap8-security.sh [--peer codex|claude|opencode] [--case NAME] [--keep]"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Resolve a peer CLI. The seed code here is SYNTHETIC (authored by no model), so "same-family"
# independence does not apply to grading this eval — we just pick an available peer and record
# which one. When wiring CAP-8 into a real author→review flow, pass --peer for a family DIFFERENT
# from whatever produced the code (the independence invariant the SKILL.md Localhost method
# enforces; this standalone eval only checks the security LENS works).
if [ -z "$peer" ]; then
  for cand in codex claude opencode; do
    if command -v "$cand" >/dev/null 2>&1; then peer="$cand"; break; fi
  done
fi
if [ -z "$peer" ] || ! command -v "$peer" >/dev/null 2>&1; then
  echo "SKIP: no peer CLI on PATH (codex/claude/opencode). CAP-8 needs a different-family reviewer" >&2
  echo "SKIP: to drive — install one or pass --peer. Skipping LOUDLY (not a pass)." >&2
  exit 77
fi

workroot=$(mktemp -d 2>/dev/null || mktemp -d -t cap8)
if [ "$keep" -eq 0 ]; then
  trap 'rm -rf "$workroot"' EXIT HUP INT TERM
else
  echo "keeping work dir: $workroot" >&2
fi

# drive_peer <prompt> <outfile> → 0 + writes review, or non-zero on peer error (caller SKIPs).
drive_peer() {
  _p="$1"; _out="$2"; _rc=0
  case "$peer" in
    codex)    codex exec --skip-git-repo-check "$_p" < /dev/null > "$_out" 2>/dev/null || _rc=$? ;;
    claude)   claude -p "$_p" < /dev/null > "$_out" 2>/dev/null || _rc=$? ;;
    opencode) opencode run "$_p" < /dev/null > "$_out" 2>/dev/null || _rc=$? ;;
    *) echo "unsupported peer: $peer" >&2; return 2 ;;
  esac
  [ "$_rc" -eq 0 ] && [ -s "$_out" ]
}

REVIEW_LENS="You are an INDEPENDENT code reviewer from a DIFFERENT model family. Review ONLY the diff below with an ADVERSARIAL SECURITY lens: what does this code leak, where can it write, what can an attacker inject, what fails open (silently succeeds when it should fail)? List findings as '- file:line — issue', most severe first. If nothing material, say 'no material findings'. Do not restate the diff."

# run_case <id> <defects-for-grader> — seeds the case's vuln file into $workroot/<id> (already
# git-initialised by the caller), reviews + model-grades. Echoes PASS/FAIL/SKIP for the case.
# Returns 0 PASS, 1 FAIL, 77 SKIP.
run_case() {
  _id="$1"; _defects="$2"; _dir="$workroot/$_id"
  echo "--- CASE $_id: driving peer '$peer' ---" >&2
  _prompt="$REVIEW_LENS

$(cd "$_dir" && git diff)"
  _review="$_dir/review.txt"
  if ! drive_peer "$_prompt" "$_review"; then
    echo "SKIP $_id: peer errored / no output (auth/offline?)." >&2
    return 77
  fi
  echo "----- review ($_id) -----" >&2; cat "$_review" >&2; echo "-------------------------" >&2

  if [ "$_id" = clean ]; then
    # FALSE-POSITIVE GUARD (the CAP-3 analogue): the seed is BENIGN, so the correct review invents
    # NO security defect. A gate that cries wolf on clean changes gets disabled — prove it doesn't.
    _grade_prompt="Grade a security code review of a BENIGN change that has NO security defect. Did the review correctly AVOID inventing a security vulnerability (finding nothing material, or only trivial style, is correct; fabricating a leak/injection/traversal/etc. is wrong)? Answer EXACTLY PASS (did not fabricate) or FAIL (fabricated a security issue) on the first line, then one short reason.

REVIEW:
$(cat "$_review")"
  else
    _low=$(tr '[:upper:]' '[:lower:]' < "$_review")
    case "$_low" in
      *leak*|*token*|*secret*|*traversal*|*"../"*|*inject*|*unsanit*|*unvalidat*|*"fail open"*|*"fail-open"*|*"does not"*|*"not verified"*|*checksum*|*exfiltrat*) : ;;
      *) echo "FAIL $_id: names no security term at all." >&2; return 1 ;;
    esac
    _grade_prompt="Grade a security code review. The reviewed code has this real defect: $_defects. Did the review correctly IDENTIFY it as a PROBLEM (NOT merely mention the words while concluding there is no issue)? Answer EXACTLY PASS or FAIL on the first line, then one short reason.

REVIEW:
$(cat "$_review")"
  fi
  _verdict="$_dir/verdict.txt"
  if ! drive_peer "$_grade_prompt" "$_verdict"; then
    # Model-grader unavailable → we CANNOT authoritatively grade THIS case. Fail-closed: SKIP.
    # (A deterministic keyword fallback would false-PASS a review that named the WRONG defect for
    # this case — e.g. a review saying "leak" passing the fail-open case. So don't pass on keywords.)
    echo "SKIP $_id: model-grader unavailable; cannot authoritatively grade (NOT a pass)." >&2
    return 77
  fi
  _first=$(sed -n '1p' "$_verdict" | tr '[:lower:]' '[:upper:]')
  _what="named the defect"; [ "$_id" = clean ] && _what="did not fabricate a defect"
  case "$_first" in
    *FAIL*) echo "FAIL $_id: model-grader says the review was WRONG ($_what expected)." >&2; return 1 ;;
    *PASS*) echo "PASS $_id: model-grader confirms the review $_what."; return 0 ;;
    *) echo "SKIP $_id: unparseable grader verdict ('$_first')." >&2; return 77 ;;
  esac
}

# --- Seeds. Each writes a vuln file into a git-initialised case dir so `git diff` shows the add. ---
seed_case() {
  _id="$1"; _dir="$workroot/$_id"; mkdir -p "$_dir"
  ( cd "$_dir" && git init -q && git config user.email e@x && git config user.name x \
    && printf '#!/bin/sh\n# placeholder\n' > f.sh && git add -A && git commit -qm init )
  case "$_id" in
    leak-traversal)
      cat > "$_dir/f.sh" <<'S'
#!/bin/sh
# Download a release asset and install the selected tool binary.
base="$1"; tool="$2"; dest="$3"; asset="$4"
fetch() { curl -fsSL -H "Authorization: Bearer $GH_TOKEN" "$base/$1" -o "$2"; }
install() { fetch "$asset" "/tmp/dl"; cp "/tmp/dl" "$dest/$tool-$asset"; }
install
S
      ;;
    command-injection)
      cat > "$_dir/f.sh" <<'S'
#!/bin/sh
# Diagnostic: ping the host the caller asked for.
host="$1"
sh -c "ping -c1 $host"
S
      ;;
    fail-open)
      cat > "$_dir/f.sh" <<'S'
#!/bin/sh
# Verify a downloaded binary against an expected checksum, then install it.
want="$1"; file="$2"; dest="$3"
got=$(sha256sum "$file" | awk '{print $1}')
if [ "$got" != "$want" ]; then
  echo "warning: checksum mismatch for $file"
fi
cp "$file" "$dest"
S
      ;;
    clean)
      # BENIGN change — no security defect. The correct review invents nothing (false-positive guard).
      cat > "$_dir/f.sh" <<'S'
#!/bin/sh
# Print the tool version. Validates its input against a strict allow-list before use.
ver="$1"
case "$ver" in
  [0-9].[0-9].[0-9]) printf 'version %s\n' "$ver" ;;
  *) echo "invalid version format" >&2; exit 1 ;;
esac
S
      ;;
    *) echo "unknown case: $_id" >&2; return 2 ;;
  esac
}

case_defects() {
  case "$1" in
    leak-traversal)    echo "an auth token (Authorization: Bearer \$GH_TOKEN) sent to a caller-controlled/arbitrary host = token leak, AND caller-controlled names used unvalidated in a filesystem path = path traversal" ;;
    command-injection) echo "caller-controlled \$host interpolated into 'sh -c' = shell command injection" ;;
    fail-open)         echo "a checksum mismatch that only prints a warning and installs the file anyway = fail-open verification (an attacker-swapped binary is installed even though the sha does not match)" ;;
  esac
}

ALL_CASES="leak-traversal command-injection fail-open clean"
if [ -n "$only_case" ]; then
  case " $ALL_CASES " in *" $only_case "*) ALL_CASES="$only_case" ;; *) echo "unknown --case: $only_case (have: $ALL_CASES)" >&2; exit 2 ;; esac
fi

pass=0; failn=0; skip=0; failed_ids=""
for c in $ALL_CASES; do
  seed_case "$c"
  rc=0; run_case "$c" "$(case_defects "$c")" || rc=$?
  case "$rc" in
    0) pass=$((pass + 1)) ;;
    1) failn=$((failn + 1)); failed_ids="$failed_ids $c" ;;
    *) skip=$((skip + 1)) ;;
  esac
done

echo "=== CAP-8 matrix: PASS=$pass FAIL=$failn SKIP=$skip (of $(printf '%s' "$ALL_CASES" | wc -w | tr -d ' ')) ==="
if [ "$failn" -gt 0 ]; then
  echo "FAILED cases:$failed_ids" >&2
  exit 1
fi
# Fail-closed: PASS (exit 0) ONLY if EVERY case was gradeable and passed. Any SKIP means a seeded
# defect class was NOT authoritatively verified — an inconclusive matrix must NOT report clean PASS
# (a partial-skip masquerading as green is a false-green CAP-8 gate).
if [ "$skip" -gt 0 ]; then
  echo "SKIP: $skip case(s) could not be authoritatively graded — matrix INCONCLUSIVE (NOT a pass)." >&2
  exit 77
fi
echo "PASS: all $pass CAP-8 cases correct (defects named; clean guard not fabricated)."
exit 0
