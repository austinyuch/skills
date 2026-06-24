#!/bin/bash
# Install aclab skills into a coding agent's skill home.
# Usage:
#   bash scripts/install.sh [opencode|claude|codex|kiro] [--with-cli]
#   SKILLS_TARGET=/custom/path bash scripts/install.sh     # explicit target wins
#   --with-cli also fetches code-review's review-cli binary via `gh` (needs auth).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MANIFEST="$REPO_ROOT/skills-manifest.json"
SOURCE="$REPO_ROOT/skills"

CLI_REPO="austinyuch/skills"; CLI_TAG="review-cli-v0.11.0"
AGENT="opencode"; WITH_CLI=0
for a in "$@"; do
  case "$a" in
    --with-cli) WITH_CLI=1 ;;
    -*) echo "❌ Unknown flag: $a"; exit 1 ;;
    *) AGENT="$a" ;;
  esac
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
echo ""

[ -f "$MANIFEST" ] || { echo "❌ Manifest not found: $MANIFEST"; exit 1; }
command -v jq >/dev/null || { echo "❌ jq is required"; exit 1; }
mkdir -p "$TARGET"

INSTALLED=0; SKIPPED=0; MISSING=0

install_one() { # $1=group(families|categories) prints results
  local group="$1"
  for key in $(jq -r ".$group | keys[]" "$MANIFEST" 2>/dev/null); do
    local group_dir="$SOURCE/$key"
    for skill in $(jq -r ".$group.\"$key\".skills[]" "$MANIFEST" 2>/dev/null); do
      local src="$group_dir/$skill" dst="$TARGET/$skill"
      if [ ! -d "$src" ]; then echo "   ⚠️  Missing: $key/$skill"; ((MISSING++)) || true; continue; fi
      if [ -d "$dst" ] && diff -rq "$src" "$dst" >/dev/null 2>&1; then echo "   ⏭️  Unchanged: $skill"; ((SKIPPED++)) || true; continue; fi
      rsync -a --delete "$src/" "$dst/"; echo "   ✅ Installed: $skill"; ((INSTALLED++)) || true
    done
  done
}

echo "🔧 Installing family skills..."; install_one families
echo ""; echo "🔧 Installing categorized skills..."; install_one categories

echo ""; echo "📄 Installing standalone files..."
for row in $(jq -c '.standalone_files[]' "$MANIFEST" 2>/dev/null); do
  file=$(echo "$row" | jq -r '.file'); category=$(echo "$row" | jq -r '.category'); target_path=$(echo "$row" | jq -r '.target_path')
  src="$SOURCE/$category/$target_path"; dst="$TARGET/$file"
  if [ ! -f "$src" ]; then echo "   ⚠️  Missing file: $file"; ((MISSING++)) || true; continue; fi
  cp "$src" "$dst"; echo "   ✅ Installed: $file"; ((INSTALLED++)) || true
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Install Summary — ✅ $INSTALLED  ⏭️  $SKIPPED  ⚠️  $MISSING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Skills are now available in: $TARGET"

if [ -d "$TARGET/code-review" ]; then
  if [ "$WITH_CLI" = "1" ]; then
    os=$(uname -s | tr '[:upper:]' '[:lower:]'); case "$os" in darwin) os=darwin;; linux) os=linux;; *) os=unsupported;; esac
    m=$(uname -m); case "$m" in x86_64|amd64) arch=amd64;; arm64|aarch64) arch=arm64;; *) arch=unsupported;; esac
    asset="review-cli-${os}-${arch}"
    dest="$TARGET/code-review/scripts"
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
