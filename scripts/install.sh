#!/bin/bash
# Install aclab skills into a coding agent's skill home.
# Usage:
#   bash scripts/install.sh [opencode|claude|codex|kiro] [--with-cli]
#   SKILLS_TARGET=/custom/path bash scripts/install.sh     # explicit target wins
#   --with-cli also fetches code-review's review-cli binary via `gh` (needs auth).
#
# Layout: FLAT single-level only — every skill installs to <target>/<skill>/SKILL.md.
#   One-level skill loaders (Claude Code, and most agent homes) only scan a single
#   directory level, so a nested <category>/<skill>/ tree would be invisible to them.
#   Flat also works on recursive loaders (OpenCode) since they discover depth-1 skills.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MANIFEST="$REPO_ROOT/skills-manifest.json"
SOURCE="$REPO_ROOT/skills"

CLI_REPO="austinyuch/skills"; CLI_TAG="review-cli-v0.15.0"
AGENT="opencode"; WITH_CLI=0
while [ "$#" -gt 0 ]; do
  a="$1"
  case "$a" in
    --with-cli) WITH_CLI=1 ;;
    # --layout kept for backward compatibility: flat is the only supported layout.
    --layout) shift; [ "${1:-}" = "flat" ] || { echo "❌ Only --layout flat is supported (skills are flat single-level); got '${1:-}'"; exit 1; } ;;
    --layout=*) [ "${a#--layout=}" = "flat" ] || { echo "❌ Only --layout flat is supported (skills are flat single-level); got '${a#--layout=}'"; exit 1; } ;;
    -*) echo "❌ Unknown flag: $a"; exit 1 ;;
    *) AGENT="$a" ;;
  esac
  shift
done
case "$AGENT" in
  opencode) DEFAULT_TARGET="$HOME/.config/opencode/skills" ;;
  claude)   DEFAULT_TARGET="$HOME/.claude/skills" ;;
  codex)    DEFAULT_TARGET="$HOME/.codex/skills" ;;
  kiro)     DEFAULT_TARGET="$HOME/.kiro/skills" ;;
  *) echo "❌ Unknown agent: $AGENT (use opencode|claude|codex|kiro, or set SKILLS_TARGET)"; exit 1 ;;
esac

# Precedence: SKILLS_TARGET > legacy OPENCODE_SKILLS > per-agent default
TARGET="${SKILLS_TARGET:-${OPENCODE_SKILLS:-$DEFAULT_TARGET}}"

echo "📦 Installing aclab skills from: $REPO_ROOT"
echo "🤖 Agent: $AGENT"
echo "🎯 Target: $TARGET"
echo "🧭 Layout: flat (single-level)"
echo ""

[ -f "$MANIFEST" ] || { echo "❌ Manifest not found: $MANIFEST"; exit 1; }
command -v jq >/dev/null || { echo "❌ jq is required"; exit 1; }
mkdir -p "$TARGET"

INSTALLED=0; SKIPPED=0; MISSING=0

echo "🔧 Installing skills..."
for skill in $(jq -r '.skills[]' "$MANIFEST" 2>/dev/null); do
  src="$SOURCE/$skill" dst="$TARGET/$skill"
  if [ ! -d "$src" ]; then echo "   ⚠️  Missing: $skill"; ((MISSING++)) || true; continue; fi
  if [ -d "$dst" ] && diff -rq "$src" "$dst" >/dev/null 2>&1; then echo "   ⏭️  Unchanged: $skill"; ((SKIPPED++)) || true; continue; fi
  rsync -a --delete "$src/" "$dst/"; echo "   ✅ Installed: $skill"; ((INSTALLED++)) || true
done

echo ""; echo "📄 Installing standalone files..."
for row in $(jq -c '.standalone_files[]' "$MANIFEST" 2>/dev/null); do
  file=$(echo "$row" | jq -r '.file'); target_path=$(echo "$row" | jq -r '.target_path')
  src="$SOURCE/$file"; dst="$TARGET/$target_path"
  if [ ! -f "$src" ]; then echo "   ⚠️  Missing file: $file"; ((MISSING++)) || true; continue; fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"; echo "   ✅ Installed: ${dst#$TARGET/}"; ((INSTALLED++)) || true
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Install Summary — ✅ $INSTALLED  ⏭️  $SKIPPED  ⚠️  $MISSING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Skills are now available in: $TARGET"

CODE_REVIEW_DIR="$TARGET/code-review"
if [ -d "$CODE_REVIEW_DIR" ]; then
  if [ "$WITH_CLI" = "1" ]; then
    os=$(uname -s | tr '[:upper:]' '[:lower:]'); case "$os" in darwin) os=darwin;; linux) os=linux;; *) os=unsupported;; esac
    m=$(uname -m); case "$m" in x86_64|amd64) arch=amd64;; arm64|aarch64) arch=arm64;; *) arch=unsupported;; esac
    asset="review-cli-${os}-${arch}"
    dest="$CODE_REVIEW_DIR/scripts"
    if [ "$os" = unsupported ] || [ "$arch" = unsupported ]; then
      echo "   ⚠️  unsupported platform for review-cli ($os/$m)"
    elif ! command -v gh >/dev/null; then
      echo "   ⚠️  GitHub CLI (gh) not found. Install gh + auth, then:"
      echo "      gh release download $CLI_TAG -R $CLI_REPO -p $asset -D \"$dest\" --clobber"
    else
      echo "⬇️  fetching $asset from $CLI_REPO@$CLI_TAG (gh) …"
      if gh release download "$CLI_TAG" -R "$CLI_REPO" -p "$asset" -D "$dest" --clobber; then
        chmod +x "$dest/$asset" 2>/dev/null || true
        echo "   ✅ review-cli installed: $dest/$asset"
      else
        echo "   ⚠️  download failed — retry: gh release download $CLI_TAG -R $CLI_REPO -p $asset -D \"$dest\" --clobber"
      fi
    fi
  else
    echo 'ℹ️  code-review'\''s review-cli binary is not bundled — re-run with --with-cli to fetch it (needs gh auth; repo is private). See README "Native binaries".'
  fi
fi
