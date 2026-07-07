#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MANIFEST="$REPO_ROOT/skills-manifest.json"

TARGET="${SKILLS_TARGET:-${OPENCODE_SKILLS:-$HOME/.config/opencode/skills}}"
SOURCE="$REPO_ROOT/skills"
LAYOUT="${SKILLS_LAYOUT:-hierarchical}"

echo "📦 Installing skills from: $REPO_ROOT"
echo "🎯 Target: $TARGET"
echo "🧭 Layout: $LAYOUT"
echo ""

if [ ! -f "$MANIFEST" ]; then
    echo "❌ Manifest not found: $MANIFEST"
    exit 1
fi

mkdir -p "$TARGET"

case "$LAYOUT" in
    flat|hierarchical) ;;
    *) echo "❌ Invalid SKILLS_LAYOUT: $LAYOUT (use flat|hierarchical)"; exit 1 ;;
esac

skill_dst() {
    local group="$1" skill="$2"
    if [ "$LAYOUT" = "flat" ]; then
        printf '%s\n' "$TARGET/$skill"
    else
        printf '%s\n' "$TARGET/$group/$skill"
    fi
}

standalone_dst() {
    local file="$1" category="$2" target_path="$3"
    if [ "$LAYOUT" = "flat" ]; then
        printf '%s\n' "$TARGET/$file"
    else
        printf '%s\n' "$TARGET/$category/$target_path"
    fi
}

INSTALLED=0
SKIPPED=0
MISSING=0

echo "🔧 Installing family skills..."

for family in $(jq -r '.families | keys[]' "$MANIFEST" 2>/dev/null); do
    family_dir="$SOURCE/$family"
    
    for skill in $(jq -r --arg f "$family" '.families[$f].skills[]' "$MANIFEST" 2>/dev/null); do
        src="$family_dir/$skill"
        dst="$(skill_dst "$family" "$skill")"
        
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
        
        mkdir -p "$(dirname "$dst")"
        rsync -a --delete "$src/" "$dst/"
        echo "   ✅ Installed: $family/$skill"
        ((INSTALLED++)) || true
    done
done

echo ""
echo "🔧 Installing categorized skills..."

for category in $(jq -r '.categories | keys[]' "$MANIFEST"); do
    category_dir="$SOURCE/$category"
    
    for skill in $(jq -r --arg c "$category" '.categories[$c].skills[]' "$MANIFEST" 2>/dev/null); do
        src="$category_dir/$skill"
        dst="$(skill_dst "$category" "$skill")"
        
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
        
        mkdir -p "$(dirname "$dst")"
        rsync -a --delete "$src/" "$dst/"
        echo "   ✅ Installed: $category/$skill"
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
    dst="$(standalone_dst "$file" "$category" "$target_path")"
    
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
