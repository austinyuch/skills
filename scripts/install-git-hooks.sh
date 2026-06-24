#!/bin/bash
# Install DevSecOps git hooks for aclab/skills.
#
# Mirrors aclab-middlewares: the versioned hook sources live in
# scripts/git-hooks/ and are COPIED into $(git rev-parse --git-dir)/hooks
# (NOT committed into .git/hooks, NOT symlinked). Re-run anytime; idempotent.
#
# Usage:
#   ./scripts/install-git-hooks.sh            # install / refresh hooks
#   ./scripts/install-git-hooks.sh --uninstall  # remove the installed hooks
#
# Bypass at commit/push time:  --no-verify   or   SKIP_HOOKS=1

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/git-hooks"
GIT_HOOKS_DIR="$(git rev-parse --git-dir)/hooks"
HOOKS=(pre-commit pre-push)
MARKER="# DevSecOps pre-"   # signature line our hooks carry

if [ "${1:-}" = "--uninstall" ]; then
    echo -e "${BLUE}Uninstalling aclab/skills git hooks...${NC}"
    for h in "${HOOKS[@]}"; do
        dest="$GIT_HOOKS_DIR/$h"
        if [ -f "$dest" ] && grep -q "$MARKER" "$dest" 2>/dev/null; then
            rm -f "$dest"; echo -e "  ${GREEN}removed${NC} $h"
        else
            echo -e "  ${YELLOW}skip${NC}   $h (not ours / absent)"
        fi
    done
    echo "Done."
    exit 0
fi

echo -e "${BLUE}Installing aclab/skills DevSecOps git hooks...${NC}"
echo "  source: scripts/git-hooks/"
echo "  target: $GIT_HOOKS_DIR/"

for h in "${HOOKS[@]}"; do
    src="$SRC_DIR/$h"; dest="$GIT_HOOKS_DIR/$h"
    if [ ! -f "$src" ]; then
        echo -e "  ${RED}error${NC} missing source: $src"; exit 1
    fi
    # Warn (don't clobber silently) if a foreign hook is already there.
    if [ -f "$dest" ] && ! grep -q "$MARKER" "$dest" 2>/dev/null; then
        echo -e "  ${YELLOW}note${NC}  overwriting existing non-ours $h (backed up to $h.bak)"
        cp "$dest" "$dest.bak"
    fi
    cp "$src" "$dest"
    chmod +x "$dest"
    echo -e "  ${GREEN}installed${NC} $h"
done

echo
echo -e "${GREEN}Git hooks installed.${NC}"
echo "  pre-commit : secret/path/denylist/JSON/conflict/shell/python/bilingual/twin checks (staged)"
echo "  pre-push   : security-risk-reviewer scan, manifest<->fs consistency, broken-link scan (push range)"
echo
echo "  Bypass once:  git commit --no-verify   |   git push --no-verify"
echo "  Bypass env :  SKIP_HOOKS=1 git commit ...   |   SKIP_HOOKS=1 git push ..."
echo "  Uninstall  :  ./scripts/install-git-hooks.sh --uninstall"
