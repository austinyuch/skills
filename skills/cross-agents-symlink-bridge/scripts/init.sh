#!/bin/bash
# =============================================================================
# Cross-Agents Symlink Bridge — init.sh (Linux / macOS)
#
# Hybrid initialization for repo-local agent surfaces:
#   1. Keep .claude/, .kiro/, .codex/ as real directories
#   2. Symlink only <agent>/skills -> ../.agents/skills
#   3. Manage <agent>/specs via explicit mode: sync | symlink | skip
#   4. Leave all other config / permission surfaces untouched so an existing
#      sync workflow can continue owning them
#   5. Recursively create CLAUDE.md -> AGENTS.md symlinks
#   6. Rewrite managed .gitignore sections to avoid stale bridge entries
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; NC='\033[0m'

SPEC_MODE="sync"
# Canonical skill source lives under the workspace agent home (.agents/skills),
# NOT a repo-root skills/. A top-level skills/ is only a convention for GLOBAL
# config homes (e.g. ~/.config/opencode/, ~/.claude/). Inside a repo, skills are
# owned by .agents/skills and bridged into .claude/.kiro/.codex — mirroring how
# specs are owned by .agents/specs.
SOURCE_SKILLS=".agents/skills"
SOURCE_SPECS=".agents/specs"
AGENT_ROOTS=(".claude" ".kiro" ".codex")
SKILLS_LINK_SOURCE="../.agents/skills"
SPECS_LINK_SOURCE="../.agents/specs"
BRIDGE_BEGIN="# cross-agents symlink bridge: managed begin"
BRIDGE_END="# cross-agents symlink bridge: managed end"

usage() {
    cat <<'EOF'
Usage:
  bash scripts/init.sh [--specs-mode sync|symlink|skip]

Modes:
  sync     Keep <agent>/specs as real directories and rsync from .agents/specs (default)
  symlink  Link <agent>/specs -> ../.agents/specs
  skip     Leave <agent>/specs untouched
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --specs-mode)
            if [ $# -lt 2 ]; then
                echo -e "${RED}❌ ERROR:${NC} --specs-mode requires sync, symlink, or skip"
                exit 1
            fi
            SPEC_MODE="$2"
            shift 2
            ;;
        --specs-mode=*)
            SPEC_MODE="${1#*=}"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ ERROR:${NC} Unknown argument: $1"
            usage
            exit 1
            ;;
    esac
done

case "$SPEC_MODE" in
    sync|symlink|skip) ;;
    *)
        echo -e "${RED}❌ ERROR:${NC} Invalid --specs-mode '$SPEC_MODE'. Use sync, symlink, or skip."
        exit 1
        ;;
esac

echo "🔍 Cross-Agents Symlink Bridge — Initialization"
echo "   Project root: $PROJECT_ROOT"
echo "   Skills mode: symlink-only"
echo "   Specs mode:  $SPEC_MODE"
echo ""

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  WARNING: Not a git repository. Paths will be created, but .gitignore won't be managed.${NC}"
    IS_GIT=false
else
    IS_GIT=true
fi

declare -a MANAGED_LINKS=()

append_unique() {
    local value="$1"
    case "$value" in
        /*) : ;;
        *)  value="/$value" ;;
    esac
    local existing
    for existing in "${MANAGED_LINKS[@]:-}"; do
        if [ "$existing" = "$value" ]; then
            return 0
        fi
    done
    MANAGED_LINKS+=("$value")
}

backup_path() {
    local target="$1"
    local backup_path="${target}.cross-agents-backup-$(date +%Y%m%d-%H%M%S)"
    mv "$target" "$backup_path"
    echo -e "   ${CYAN}📦${NC} Backed up $target -> $backup_path"
}

ensure_agent_root() {
    local root="$1"

    if [ -L "$root" ] || [ -f "$root" ]; then
        backup_path "$root"
        echo -e "   ${YELLOW}⚠️${NC}  Legacy root bridge for $root was backed up; non-skill config is not auto-copied. Re-run your normal sync flow if you need repo-local settings restored."
    fi

    if [ ! -d "$root" ]; then
        mkdir -p "$root"
        echo -e "   ${CYAN}ℹ️${NC}  Created real agent root $root/"
    fi
}

rewrite_gitignore_section() {
    local begin_marker="$1"
    local end_marker="$2"
    shift 2
    local entries=("$@")
    local tmp_file

    [ "$IS_GIT" = true ] || return 0

    [ -f .gitignore ] || touch .gitignore
    tmp_file="$(mktemp)"

    awk -v begin="$begin_marker" -v end="$end_marker" '
        BEGIN { skip = 0 }
        $0 == begin { skip = 1; next }
        $0 == end { skip = 0; next }
        !skip { print }
    ' .gitignore > "$tmp_file"

    # Idempotency: drop trailing blank lines left after removing the old section
    awk 'NF { last = NR } { buf[NR] = $0 } END { for (i = 1; i <= last; i++) print buf[i] }' \
        "$tmp_file" > "$tmp_file.trim" && mv "$tmp_file.trim" "$tmp_file"

    if [ ${#entries[@]} -gt 0 ]; then
        [ -s "$tmp_file" ] && printf "\n" >> "$tmp_file"   # one separator, only if non-empty
        printf "%s\n" "$begin_marker" >> "$tmp_file"
        printf "%s\n" "${entries[@]}" >> "$tmp_file"
        printf "%s\n" "$end_marker" >> "$tmp_file"
    fi

    mv "$tmp_file" .gitignore
}

rsync_directory() {
    local source_dir="$1"
    local target_dir="$2"

    if ! command -v rsync > /dev/null 2>&1; then
        echo -e "   ${RED}❌${NC} rsync is required for specs sync mode but is not installed"
        return 1
    fi

    mkdir -p "$target_dir"
    rsync -a --delete "$source_dir/" "$target_dir/"
}

ensure_symlink_target() {
    local target_path="$1"
    local link_source="$2"
    local display_source="$3"

    mkdir -p "$(dirname "$target_path")"

    if [ -L "$target_path" ]; then
        local current_target
        current_target="$(readlink "$target_path" 2>/dev/null || echo "")"
        if [ "$current_target" = "$link_source" ]; then
            echo -e "   ${GREEN}✅${NC} $target_path -> $display_source (already correct)"
            append_unique "$target_path"
            return 0
        fi

        echo -e "   ${YELLOW}⚠️${NC}  $target_path points to '$current_target', replacing with '$display_source'..."
        rm "$target_path"
    elif [ -e "$target_path" ]; then
        backup_path "$target_path"
    fi

    ln -sn "$link_source" "$target_path"
    echo -e "   ${GREEN}🔗 Created:${NC} $target_path -> $display_source"
    append_unique "$target_path"
}

handle_specs_target() {
    local root="$1"
    local target_path="$root/specs"

    case "$SPEC_MODE" in
        skip)
            echo -e "   ${CYAN}ℹ️${NC}  Leaving $target_path untouched (specs mode: skip)"
            return 0
            ;;
        sync)
            if [ ! -d "$SOURCE_SPECS" ]; then
                echo -e "   ${YELLOW}⚠️${NC}  Source $SOURCE_SPECS/ not found, skipping $target_path sync"
                return 0
            fi

            if [ -L "$target_path" ] || [ -f "$target_path" ]; then
                backup_path "$target_path"
            fi

            mkdir -p "$target_path"
            rsync_directory "$SOURCE_SPECS" "$target_path"
            echo -e "   ${GREEN}🔄 Synced:${NC} $target_path/ <= $SOURCE_SPECS/"
            ;;
        symlink)
            if [ ! -d "$SOURCE_SPECS" ]; then
                echo -e "   ${YELLOW}⚠️${NC}  Source $SOURCE_SPECS/ not found, skipping $target_path symlink"
                return 0
            fi

            if [ -d "$target_path" ] && [ ! -L "$target_path" ]; then
                echo -e "   ${CYAN}📥${NC} Merging existing $target_path/ into $SOURCE_SPECS/ before linking"
                rsync_directory "$target_path" "$SOURCE_SPECS"
                rm -rf "$target_path"  # agent-safety-allow: merged into source first, then remove (backup-before-delete)
            elif [ -e "$target_path" ] && [ ! -L "$target_path" ]; then
                backup_path "$target_path"
            fi

            ensure_symlink_target "$target_path" "$SPECS_LINK_SOURCE" "$SOURCE_SPECS"
            ;;
    esac
}

echo "── Step 1: Normalize agent roots ─────────────────"
echo ""

for root in "${AGENT_ROOTS[@]}"; do
    ensure_agent_root "$root"
done

echo ""
echo "── Step 2: Repo-local skills symlinks ────────────"
echo ""

if [ ! -d "$SOURCE_SKILLS" ]; then
    mkdir -p "$SOURCE_SKILLS"
    echo -e "   ${CYAN}ℹ️${NC}  Created canonical skills source $SOURCE_SKILLS/ (workspace agent home)"
fi

for root in "${AGENT_ROOTS[@]}"; do
    ensure_symlink_target "$root/skills" "$SKILLS_LINK_SOURCE" "$SOURCE_SKILLS"
done

echo ""
echo "── Step 3: Repo-local specs ($SPEC_MODE) ─────────"
echo ""

for root in "${AGENT_ROOTS[@]}"; do
    handle_specs_target "$root"
done

echo ""
echo "── Step 4: CLAUDE.md symlinks (recursive) ───────"
echo ""

claude_sync_script="$SCRIPT_DIR/sync-claude-md.sh"
if [ -f "$claude_sync_script" ]; then
    bash "$claude_sync_script"
else
    echo -e "   ${YELLOW}⚠️${NC}  sync-claude-md.sh not found at $claude_sync_script"
fi

echo ""
echo "── Step 5: .gitignore ───────────────────────────"
echo ""

if [ "$SPEC_MODE" = "symlink" ]; then
    append_unique ".claude/specs"
    append_unique ".kiro/specs"
    append_unique ".codex/specs"
fi

if [ "$IS_GIT" = false ]; then
    echo "   Skipped (not a git repository)"
else
    rewrite_gitignore_section "$BRIDGE_BEGIN" "$BRIDGE_END" "${MANAGED_LINKS[@]}"
    echo -e "   ${GREEN}📝${NC} Rewrote managed bridge entries in .gitignore"
fi

echo ""
echo "── Verification ──────────────────────────────────"
echo ""

ALL_OK=true
for root in "${AGENT_ROOTS[@]}"; do
    if [ ! -d "$root" ] || [ -L "$root" ]; then
        echo -e "   ${RED}❌${NC} $root must remain a real directory"
        ALL_OK=false
    else
        echo -e "   ${GREEN}✅${NC} $root/ is a real directory"
    fi

    if [ -L "$root/skills" ] && [ "$(readlink "$root/skills")" = "$SKILLS_LINK_SOURCE" ]; then
        echo -e "   ${GREEN}✅${NC} $root/skills -> $SOURCE_SKILLS"
    else
        echo -e "   ${RED}❌${NC} $root/skills is missing or points to the wrong target"
        ALL_OK=false
    fi

    case "$SPEC_MODE" in
        sync)
            if [ -d "$SOURCE_SPECS" ]; then
                if [ -d "$root/specs" ] && [ ! -L "$root/specs" ]; then
                    echo -e "   ${GREEN}✅${NC} $root/specs is a real synced directory"
                else
                    echo -e "   ${RED}❌${NC} $root/specs should be a real directory in sync mode"
                    ALL_OK=false
                fi
            fi
            ;;
        symlink)
            if [ -d "$SOURCE_SPECS" ]; then
                if [ -L "$root/specs" ] && [ "$(readlink "$root/specs")" = "$SPECS_LINK_SOURCE" ]; then
                    echo -e "   ${GREEN}✅${NC} $root/specs -> $SOURCE_SPECS"
                else
                    echo -e "   ${RED}❌${NC} $root/specs is missing or points to the wrong target"
                    ALL_OK=false
                fi
            fi
            ;;
    esac
done

echo ""
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}🎯 Hybrid bridge initialization completed successfully.${NC}"
else
    echo -e "${RED}❌ Verification failed. Review the output above.${NC}"
    exit 1
fi

echo ""
echo "── Notes ─────────────────────────────────────────"
echo "   • Only repo-local skills are symlinked by this workflow"
echo "   • specs mode is '$SPEC_MODE' and can be changed on the next run"
echo "   • Other config / permission surfaces are intentionally left real"
echo "   • Run scripts/install-hook.sh to auto-sync CLAUDE.md on commit"
