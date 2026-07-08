#!/bin/bash
# =============================================================================
# Cross-Agents Symlink Bridge — sync-claude-md.sh (Linux / macOS)
#
# Recursively scans for AGENTS.md files and creates CLAUDE.md → AGENTS.md
# symlinks in each directory. Supports full-scan and git-diff modes.
#
# Modes:
#   (no args)  Full scan — find all AGENTS.md recursively
#   --staged   Git diff mode — only process staged AGENTS.md changes
#
# Conflict policy:
#   - CLAUDE.md is correct symlink → keep
#   - CLAUDE.md is real file (not symlink) → warn & skip
#   - CLAUDE.md doesn't exist → create symlink
#
# .gitignore policy:
#   - Rewrite a dedicated managed section for generated CLAUDE.md symlinks
#   - Do not git-add generated symlinks
# =============================================================================
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'

MODE="full"
SECTION_BEGIN="# cross-agents symlink bridge: claude-md begin"
SECTION_END="# cross-agents symlink bridge: claude-md end"

if [ "${1:-}" = "--staged" ]; then
    MODE="staged"
fi

declare -a AGENTS_FILES=()
declare -a MANAGED_CLAUDE=()

FIND_PRUNE_EXPR=( \( -path './.git' -o -path './node_modules' -o -path './.claude' -o -path './.kiro' -o -path './.codex' \) -prune -o )

append_unique() {
    local value="$1"
    local existing
    for existing in "${MANAGED_CLAUDE[@]:-}"; do
        if [ "$existing" = "$value" ]; then
            return 0
        fi
    done
    MANAGED_CLAUDE+=("$value")
}

rewrite_gitignore_section() {
    local begin_marker="$1"
    local end_marker="$2"
    shift 2
    local entries=("$@")
    local tmp_file

    [ -f .gitignore ] || touch .gitignore
    tmp_file="$(mktemp)"

    awk -v begin="$begin_marker" -v end="$end_marker" '
        BEGIN { skip = 0 }
        $0 == begin { skip = 1; next }
        $0 == end { skip = 0; next }
        !skip { print }
    ' .gitignore > "$tmp_file"

    if [ ${#entries[@]} -gt 0 ]; then
        printf "\n%s\n" "$begin_marker" >> "$tmp_file"
        printf "%s\n" "${entries[@]}" >> "$tmp_file"
        printf "%s\n" "$end_marker" >> "$tmp_file"
    fi

    mv "$tmp_file" .gitignore
}

collect_managed_claude_symlinks() {
    MANAGED_CLAUDE=()

    while IFS= read -r file; do
        local normalized="${file#./}"
        if [ -L "$normalized" ] && [ "$(readlink "$normalized" 2>/dev/null || echo "")" = "AGENTS.md" ]; then
            append_unique "$normalized"
        fi
    done < <(find . "${FIND_PRUNE_EXPR[@]}" -name "CLAUDE.md" -print 2>/dev/null | sort)
}

echo "🔍 Scanning ${MODE} directories for AGENTS.md..."

if [ "$MODE" = "staged" ]; then
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}❌ ERROR: Not a git repository. --staged mode requires git.${NC}"
        exit 1
    fi

    while IFS= read -r file; do
        if echo "$file" | grep -q '/AGENTS\.md$\|^AGENTS\.md$'; then
            AGENTS_FILES+=("$file")
        fi
    done < <(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)
else
    while IFS= read -r file; do
        AGENTS_FILES+=("$file")
    done < <(find . "${FIND_PRUNE_EXPR[@]}" -name "AGENTS.md" -print 2>/dev/null | sort)
fi

if [ ${#AGENTS_FILES[@]} -eq 0 ]; then
    echo "   No AGENTS.md files found."

    if [ "$MODE" = "staged" ]; then
        echo "   Preserving managed CLAUDE.md entries from current symlink state."
        collect_managed_claude_symlinks
        rewrite_gitignore_section "$SECTION_BEGIN" "$SECTION_END" "${MANAGED_CLAUDE[@]}"
        exit 0
    fi

    rewrite_gitignore_section "$SECTION_BEGIN" "$SECTION_END"
    exit 0
fi

echo "   Found ${#AGENTS_FILES[@]} AGENTS.md file(s)"
echo ""

CREATED=0
SKIPPED_CORRECT=0
SKIPPED_CONFLICT=0

for agents_file in "${AGENTS_FILES[@]}"; do
    dir="$(dirname "$agents_file")"
    claude_file="$dir/CLAUDE.md"
    claude_file="${claude_file#./}"

    if [ -L "$claude_file" ]; then
        current_target="$(readlink "$claude_file" 2>/dev/null || echo "")"
        if [ "$current_target" = "AGENTS.md" ]; then
            echo -e "   ${GREEN}✅${NC} $claude_file -> AGENTS.md (correct)"
            append_unique "$claude_file"
            SKIPPED_CORRECT=$((SKIPPED_CORRECT + 1))
            continue
        fi

        echo -e "   ${YELLOW}⚠️${NC}  $claude_file -> $current_target, replacing..."
        rm "$claude_file"
    elif [ -f "$claude_file" ]; then
        echo -e "   ${YELLOW}⚠️${NC}  $claude_file is a real file — skipping (not overwriting)"
        SKIPPED_CONFLICT=$((SKIPPED_CONFLICT + 1))
        continue
    fi

    (
        cd "$dir"
        ln -sn "AGENTS.md" "CLAUDE.md"
    )

    echo -e "   ${GREEN}🔗 Created:${NC} $claude_file -> AGENTS.md"
    append_unique "$claude_file"
    CREATED=$((CREATED + 1))
done

collect_managed_claude_symlinks
rewrite_gitignore_section "$SECTION_BEGIN" "$SECTION_END" "${MANAGED_CLAUDE[@]}"

echo ""
echo -e "   Created: ${GREEN}$CREATED${NC}  |  Skipped (correct): ${CYAN}$SKIPPED_CORRECT${NC}  |  Skipped (conflict): ${YELLOW}$SKIPPED_CONFLICT${NC}"
