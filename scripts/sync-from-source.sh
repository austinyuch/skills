#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MANIFEST="$REPO_ROOT/skills-manifest.json"

SOURCE="${OPENCODE_SKILLS:-$HOME/.config/opencode/skills}"
TARGET="$REPO_ROOT/skills"

echo "🔄 Syncing skills from: $SOURCE"
echo "📦 Target repo: $REPO_ROOT"
echo ""

if [ ! -f "$MANIFEST" ]; then
    echo "❌ Manifest not found: $MANIFEST"
    exit 1
fi

if [ ! -d "$SOURCE" ]; then
    echo "❌ Source directory not found: $SOURCE"
    echo "   Set OPENCODE_SKILLS env var or ensure ~/.config/opencode/skills exists"
    exit 1
fi

SYNCED=0
SKIPPED=0
MISSING=0

# Sync family skills
echo "📂 Syncing family skills..."

for family in $(jq -r '.families | keys[]' "$MANIFEST" 2>/dev/null); do
    family_dir="$TARGET/$family"
    mkdir -p "$family_dir"
    
    for skill in $(jq -r ".families.$family.skills[]" "$MANIFEST" 2>/dev/null); do
        src="$SOURCE/$skill"
        dst="$family_dir/$skill"
        
        if [ ! -d "$src" ]; then
            echo "   ⚠️  Missing: $family/$skill"
            ((MISSING++)) || true
            continue
        fi
        
        if [ -d "$dst" ] && diff -rq "$src" "$dst" > /dev/null 2>&1; then
            echo "   ⏭️  Unchanged: $family/$skill"
            ((SKIPPED++)) || true
            continue
        fi
        
        rsync -a --delete "$src/" "$dst/"
        echo "   ✅ Synced: $family/$skill"
        ((SYNCED++)) || true
    done
done

echo ""

# Sync categorized skills
echo "📂 Syncing categorized skills..."

for category in $(jq -r '.categories | keys[]' "$MANIFEST"); do
    category_dir="$TARGET/$category"
    mkdir -p "$category_dir"
    
    for skill in $(jq -r ".categories.$category.skills[]" "$MANIFEST" 2>/dev/null); do
        src="$SOURCE/$skill"
        dst="$category_dir/$skill"
        
        if [ ! -d "$src" ]; then
            echo "   ⚠️  Missing: $category/$skill"
            ((MISSING++)) || true
            continue
        fi
        
        if [ -d "$dst" ] && diff -rq "$src" "$dst" > /dev/null 2>&1; then
            echo "   ⏭️  Unchanged: $category/$skill"
            ((SKIPPED++)) || true
            continue
        fi
        
        rsync -a --delete "$src/" "$dst/"
        echo "   ✅ Synced: $category/$skill"
        ((SYNCED++)) || true
    done
done

echo ""
echo "📄 Syncing standalone files..."

for row in $(jq -c '.standalone_files[]' "$MANIFEST" 2>/dev/null); do
    file=$(echo "$row" | jq -r '.file')
    category=$(echo "$row" | jq -r '.category')
    target_path=$(echo "$row" | jq -r '.target_path')
    
    src="$SOURCE/$file"
    dst="$TARGET/$category/$target_path"
    
    if [ ! -f "$src" ]; then
        echo "   ⚠️  Missing file: $file"
        ((MISSING++)) || true
        continue
    fi
    
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    echo "   ✅ Synced: $category/$target_path"
    ((SYNCED++)) || true
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Sync Summary"
echo "   ✅ Synced:  $SYNCED"
echo "   ⏭️  Skipped: $SKIPPED"
echo "   ⚠️  Missing: $MISSING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "   1. Review changes: git status"
echo "   2. Commit: git add skills/ && git commit -m 'sync: update skills $(date +%Y-%m-%d)'"
echo "   3. Push: git push origin main"
