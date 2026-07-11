#!/usr/bin/env sh
# One-command publish for the cross-agent-review skill: build the native binaries
# from the Go source of truth, then copy the whole skill (SKILL.md + references +
# scripts + freshly built binaries) into the local agent skill homes as real dirs
# — the same home set and layout as the code-review skill.
#
# Usage:
#   publish.sh [path-to-go-review-service]
# Overrides:
#   XREVIEW_GO_DIR      path to go-review-service (else the arg, else auto-detected)
#   XREVIEW_SKILL_HOMES space-separated skills dirs to publish into (else the 9 defaults)
#   XREVIEW_SKILL_REL   destination path under each skills dir (default: cross-agent-review)
#   XREVIEW_NO_BUILD=1  skip the rebuild and publish whatever binaries are present
#
# Idempotent: each target is removed and re-copied. Verifies each published copy
# resolves an executable binary.
set -eu

here="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"   # .../cross-agent-review/scripts
skill_dir="$(CDPATH= cd -- "$here/.." && pwd)"        # .../cross-agent-review
skill_name="$(basename "$skill_dir")"                  # cross-agent-review

# 1) Build the six platform binaries into scripts/ (unless told to skip).
if [ "${XREVIEW_NO_BUILD:-}" != "1" ]; then
  go_dir="${1:-${XREVIEW_GO_DIR:-}}"
  if [ -z "$go_dir" ]; then
    # scripts/ -> cross-agent-review -> skills -> .agents -> <repo-root>/go-review-service
    guess="$(CDPATH= cd -- "$here/../../../.." 2>/dev/null && pwd)/go-review-service"
    [ -d "$guess" ] && go_dir="$guess"
  fi
  if [ -z "${go_dir:-}" ] || [ ! -d "$go_dir" ]; then
    echo "error: cannot locate go-review-service — pass it: publish.sh <path> (or set XREVIEW_GO_DIR, or XREVIEW_NO_BUILD=1)" >&2
    exit 2
  fi
  echo "==> building binaries from $go_dir"
  sh "$here/build-binaries.sh" "$go_dir"
else
  echo "==> XREVIEW_NO_BUILD=1 — publishing existing binaries in $here"
fi

# 2) Publish to the agent skill homes (real dirs; mirrors code-review's home set).
: "${HOME:?HOME must be set}"
homes="${XREVIEW_SKILL_HOMES:-$HOME/.agents/skills $HOME/.claude/skills $HOME/.kiro/skills $HOME/.config/opencode/skills $HOME/.codex/skills $HOME/.gemini/skills $HOME/.gemini/config/skills $HOME/.copilot/skills $HOME/.cline/skills}"
skill_rel="${XREVIEW_SKILL_REL:-$skill_name}"

published=0
for base in $homes; do
  mkdir -p "$base"
  dest="$base/$skill_rel"
  rm -rf "$dest"
  mkdir -p "$(dirname "$dest")"
  cp -R "$skill_dir" "$dest"
  bin="$(sh "$dest/scripts/xreview-bin.sh")"
  if [ -x "$bin" ]; then
    echo "  ok   $dest  (bin: $(basename "$bin"))"
    published=$((published + 1))
  else
    echo "  WARN $dest  (binary not executable/missing: $bin)" >&2
  fi
done

echo "==> published $skill_name to $published home(s)"
