#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MANIFEST="$REPO_ROOT/skills-manifest.json"

TARGET="${OPENCODE_SKILLS:-$HOME/.config/opencode/skills}"
SOURCE="$REPO_ROOT/skills"

echo "📦 Installing skills from: $REPO_ROOT"
echo "🎯 Target: $TARGET"
echo ""

if [ ! -f "$MANIFEST" ]; then
    echo "❌ Manifest not found: $MANIFEST"
    exit 1
fi

mkdir -p "$TARGET"

INSTALLED=0
SKIPPED=0
MISSING=0

echo "🔧 Installing family skills..."

for family in $(jq -r '.families | keys[]' "$MANIFEST" 2>/dev/null); do
    family_dir="$SOURCE/$family"
    
    for skill in $(jq -r ".families.$family.skills[]" "$MANIFEST" 2>/dev/null); do
        src="$family_dir/$skill"
        dst="$TARGET/$skill"
        
        if [ ! -d "$src" ]; then
            echo "   ⚠️  Missing: $family/$skill"
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
done

echo ""
echo "🔧 Installing categorized skills..."

for category in $(jq -r '.categories | keys[]' "$MANIFEST"); do
    category_dir="$SOURCE/$category"
    
    for skill in $(jq -r ".categories.$category.skills[]" "$MANIFEST" 2>/dev/null); do
        src="$category_dir/$skill"
        dst="$TARGET/$skill"
        
        if [ ! -d "$src" ]; then
            echo "   ⚠️  Missing: $category/$skill"
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
done

echo ""
echo "📄 Installing standalone files..."

for row in $(jq -c '.standalone_files[]' "$MANIFEST" 2>/dev/null); do
    file=$(echo "$row" | jq -r '.file')
    category=$(echo "$row" | jq -r '.category')
    target_path=$(echo "$row" | jq -r '.target_path')
    
    src="$SOURCE/$category/$target_path"
    dst="$TARGET/$file"
    
    if [ ! -f "$src" ]; then
        echo "   ⚠️  Missing file: $file"
        ((MISSING++)) || true
        continue
    fi
    
    cp "$src" "$dst"
    echo "   ✅ Installed: $file"
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
