#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MANIFEST="$REPO_ROOT/skills-manifest.json"
SANITIZE_RULES="$SCRIPT_DIR/sanitize-rules.sed"

SOURCE="${OPENCODE_SKILLS:-$HOME/.config/opencode/skills}"
TARGET="$REPO_ROOT/skills"

# Text file extensions the sanitizer is allowed to rewrite in place (never binaries).
TEXT_EXT="md json txt sh mjs js py html yaml yml toml css"

# Repo-managed paths that are NOT present upstream (added during open-sourcing) or are
# compiled artifacts the repo pins. The sync must never delete/overwrite these:
#   LICENSE / NOTICE  — Apache-2.0 files carried by the code-review family
#   viewer            — pre-built graph-explorer webapp bundle (hashed assets pinned in
#                       .gitleaksignore); refresh it deliberately, not via routine sync.
#   model payloads    — code-review ships model/tokenizer payloads through release bundles,
#                       not this public source repo; keep only README.md + manifest.json.
MODEL_PAYLOAD_EXCLUDES=(
    --exclude=assets/models/baai-bge-small-en-v1-5/model.onnx
    --exclude=assets/models/baai-bge-small-en-v1-5/config.json
    --exclude=assets/models/baai-bge-small-en-v1-5/special_tokens_map.json
    --exclude=assets/models/baai-bge-small-en-v1-5/tokenizer.json
    --exclude=assets/models/baai-bge-small-en-v1-5/tokenizer_config.json
    --exclude=assets/models/baai-bge-small-en-v1-5/vocab.txt
)
RSYNC_EXCLUDES=( --exclude=LICENSE --exclude=NOTICE --exclude=viewer "${MODEL_PAYLOAD_EXCLUDES[@]}" )
DIFF_EXCLUDES=( --exclude=LICENSE --exclude=NOTICE --exclude=viewer "${MODEL_PAYLOAD_EXCLUDES[@]}" )

echo "🔄 Syncing skills from: $SOURCE"
echo "📦 Target repo: $REPO_ROOT"
if [ -f "$SANITIZE_RULES" ]; then
    echo "🧼 Sanitize rules: $SANITIZE_RULES"
else
    echo "⚠️  No sanitize rules found ($SANITIZE_RULES) — syncing raw upstream."
fi
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

# Staging area for sanitized copies (compared against target before deploy).
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# sanitize_tree <dir> — redact machine identifiers in text files under <dir>, in place.
sanitize_tree() {
    local dir="$1"
    [ -f "$SANITIZE_RULES" ] || return 0
    local find_args=() first=1
    for ext in $TEXT_EXT; do
        if [ "$first" -eq 1 ]; then find_args+=( -name "*.$ext" ); first=0
        else find_args+=( -o -name "*.$ext" ); fi
    done
    find "$dir" -type f \( "${find_args[@]}" \) -print0 \
        | xargs -0 -r sed -i -f "$SANITIZE_RULES"
}

# deploy_skill <label> <src-dir> <dst-dir>
# Builds a sanitized staging copy of src, deploys to dst only if it differs.
deploy_skill() {
    local label="$1" src="$2" dst="$3"

    if [ ! -d "$src" ]; then
        echo "   ⚠️  Missing: $label"
        ((MISSING++)) || true
        return
    fi

    local tmp="$STAGE/skill"
    rm -rf "$tmp"; mkdir -p "$tmp"
    rsync -a "$src/" "$tmp/"
    sanitize_tree "$tmp"

    if [ -d "$dst" ] && diff -rq "${DIFF_EXCLUDES[@]}" "$tmp" "$dst" > /dev/null 2>&1; then
        echo "   ⏭️  Unchanged: $label"
        ((SKIPPED++)) || true
        return
    fi

    rsync -a --delete "${RSYNC_EXCLUDES[@]}" "$tmp/" "$dst/"
    echo "   ✅ Synced: $label"
    ((SYNCED++)) || true
}

# source_skill_dir <category-or-family> <skill>
# The live OpenCode source now uses the same multi-level layout as this public
# repo. Keep a flat fallback during migration so older machines can still sync.
source_skill_dir() {
    local group="$1" skill="$2"
    if [ -d "$SOURCE/$group/$skill" ]; then
        printf '%s\n' "$SOURCE/$group/$skill"
    else
        printf '%s\n' "$SOURCE/$skill"
    fi
}

source_standalone_file() {
    local file="$1" category="$2" target_path="$3"
    if [ -f "$SOURCE/$category/$target_path" ]; then
        printf '%s\n' "$SOURCE/$category/$target_path"
    else
        printf '%s\n' "$SOURCE/$file"
    fi
}

# Sync family skills
echo "📂 Syncing family skills..."

for family in $(jq -r '.families | keys[]' "$MANIFEST" 2>/dev/null); do
    family_dir="$TARGET/$family"
    mkdir -p "$family_dir"

    for skill in $(jq -r --arg f "$family" '.families[$f].skills[]' "$MANIFEST" 2>/dev/null); do
        deploy_skill "$family/$skill" "$(source_skill_dir "$family" "$skill")" "$family_dir/$skill"
    done
done

echo ""

# Sync categorized skills
echo "📂 Syncing categorized skills..."

for category in $(jq -r '.categories | keys[]' "$MANIFEST"); do
    category_dir="$TARGET/$category"
    mkdir -p "$category_dir"

    for skill in $(jq -r --arg c "$category" '.categories[$c].skills[]' "$MANIFEST" 2>/dev/null); do
        deploy_skill "$category/$skill" "$(source_skill_dir "$category" "$skill")" "$category_dir/$skill"
    done
done

echo ""
echo "📄 Syncing standalone files..."

for row in $(jq -c '.standalone_files[]' "$MANIFEST" 2>/dev/null); do
    file=$(echo "$row" | jq -r '.file')
    category=$(echo "$row" | jq -r '.category')
    target_path=$(echo "$row" | jq -r '.target_path')

    src="$(source_standalone_file "$file" "$category" "$target_path")"
    dst="$TARGET/$category/$target_path"

    if [ ! -f "$src" ]; then
        echo "   ⚠️  Missing file: $file"
        ((MISSING++)) || true
        continue
    fi

    # Sanitize a staging copy, then deploy only if changed.
    tmp="$STAGE/$(basename "$file")"
    cp "$src" "$tmp"
    [ -f "$SANITIZE_RULES" ] && sed -i -f "$SANITIZE_RULES" "$tmp"
    if [ -f "$dst" ] && diff -q "$tmp" "$dst" > /dev/null 2>&1; then
        echo "   ⏭️  Unchanged: $category/$target_path"
        ((SKIPPED++)) || true
        rm -f "$tmp"
        continue
    fi
    mkdir -p "$(dirname "$dst")"
    cp "$tmp" "$dst"
    rm -f "$tmp"
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
