#!/bin/bash
# Install this repo's skills into an OpenCode skill home (flat single-level layout).
# Prefer `scripts/install.sh opencode`; this remains as a direct opencode installer.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MANIFEST="$REPO_ROOT/skills-manifest.json"

TARGET="${SKILLS_TARGET:-${OPENCODE_SKILLS:-$HOME/.config/opencode/skills}}"
SOURCE="$REPO_ROOT/skills"

echo "📦 Installing skills from: $REPO_ROOT"
echo "🎯 Target: $TARGET"
echo "🧭 Layout: flat (single-level)"
echo ""

[ -f "$MANIFEST" ] || { echo "❌ Manifest not found: $MANIFEST"; exit 1; }
command -v jq >/dev/null || { echo "❌ jq is required"; exit 1; }
mkdir -p "$TARGET"

INSTALLED=0
SKIPPED=0
MISSING=0

echo "🔧 Installing skills..."
for skill in $(jq -r '.skills[]' "$MANIFEST" 2>/dev/null); do
    src="$SOURCE/$skill"
    dst="$TARGET/$skill"

    if [ ! -d "$src" ]; then
        echo "   ⚠️  Missing: $skill"
        ((MISSING++)) || true
        continue
    fi

    if [ -d "$dst" ] && diff -rq "$src" "$dst" > /dev/null 2>&1; then
        echo "   ⏭️  Unchanged: $skill"
        ((SKIPPED++)) || true
        continue
    fi

    rsync -a --delete "$src/" "$dst/"
    echo "   ✅ Installed: $skill"
    ((INSTALLED++)) || true
done

echo ""
echo "📄 Installing standalone files..."
for row in $(jq -c '.standalone_files[]' "$MANIFEST" 2>/dev/null); do
    file=$(echo "$row" | jq -r '.file')
    target_path=$(echo "$row" | jq -r '.target_path')

    src="$SOURCE/$file"
    dst="$TARGET/$target_path"

    if [ ! -f "$src" ]; then
        echo "   ⚠️  Missing file: $file"
        ((MISSING++)) || true
        continue
    fi

    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    echo "   ✅ Installed: ${dst#$TARGET/}"
    ((INSTALLED++)) || true
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Install Summary"
echo "   ✅ Installed: $INSTALLED"
echo "   ⏭️  Skipped:   $SKIPPED"
echo "   ⚠️  Missing:   $MISSING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Skills are now available in: $TARGET"
