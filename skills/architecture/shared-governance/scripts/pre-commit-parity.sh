#!/usr/bin/env bash
# Pre-commit parity hook for aclab-opencode-config.
#
# Runs the repo's parity guards so shared-content drift is caught at commit time
# instead of silently shipping:
#   1) mirror parity  — spec-master ↔ spec-driven-development byte-identical shared refs
#   2) print parity   — stakeholder-artifact skills all carry the disappearing-bug print fix
# (ISSUE_LOG ISS-2026-004; extended to the print cluster by shared-print-parity-hardening.)
#
# INSTALL (git core.hooksPath — tracked, no per-clone copy needed):
#   git config core.hooksPath skills/shared-governance/scripts/githooks
#   # this file is symlinked/copied as githooks/pre-commit (see that dir)
# OR classic (per-clone, .git not tracked):
#   ln -sf ../../skills/shared-governance/scripts/pre-commit-parity.sh .git/hooks/pre-commit
#
# Skip once (emergency):  PARITY_SKIP=1 git commit ...
set -u

if [ "${PARITY_SKIP:-0}" = "1" ]; then
  echo "pre-commit-parity: skipped (PARITY_SKIP=1)"; exit 0
fi

# repo root = two levels up from skills/shared-governance/scripts/
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"

rc=0
echo "── mirror parity (spec-master ↔ spec-driven-development) ──"
bash "$ROOT/skills/spec-master/scripts/check_mirror_parity.sh" || rc=1
echo "── print parity (stakeholder-artifact skills) ──"
bash "$ROOT/skills/shared-governance/scripts/check_print_parity.sh" || rc=1

if [ "$rc" -ne 0 ]; then
  echo ""
  echo "pre-commit-parity: FAIL — shared content drifted. Fix, or 'PARITY_SKIP=1 git commit' to override."
fi
exit "$rc"
