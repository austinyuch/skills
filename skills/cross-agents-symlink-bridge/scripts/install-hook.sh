#!/bin/bash
# =============================================================================
# Cross-Agents Symlink Bridge — install-hook.sh (Linux / macOS)
#
# Installs a git pre-commit hook that automatically runs sync-claude-md --staged
# to keep CLAUDE.md symlinks in sync with AGENTS.md on every commit.
#
# If a pre-commit hook already exists, the cross-agents sync logic is appended
# after a clearly marked section. Never overwrites existing hook logic.
#
# Usage:
#   cd <project-root>
#   bash scripts/install-hook.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'

echo "🔧 Cross-Agents Symlink Bridge — Hook Installer"
echo ""

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Not a git repository.${NC}"
    exit 1
fi

HOOK_PATH=".git/hooks/pre-commit"

SYNC_SCRIPT="$SCRIPT_DIR/sync-claude-md.sh"
if [ ! -f "$SYNC_SCRIPT" ]; then
    echo -e "${RED}❌ ERROR: sync-claude-md.sh not found at $SYNC_SCRIPT${NC}"
    exit 1
fi

MARKER="# === cross-agents-symlink-bridge (auto-generated) ==="

HOOK_CONTENT=$(cat <<HEREDOC
$MARKER
# Auto-sync CLAUDE.md -> AGENTS.md symlinks on each commit.
# Runs in --staged mode: only processes files in the current commit.
# Does NOT block commit on failure — warnings only.
SCRIPT_DIR_HOOK="$SCRIPT_DIR"
if [ -f "\$SCRIPT_DIR_HOOK/sync-claude-md.sh" ]; then
    bash "\$SCRIPT_DIR_HOOK/sync-claude-md.sh" --staged || true
fi
# === end cross-agents-symlink-bridge ===
HEREDOC
)

if [ -f "$HOOK_PATH" ]; then
    if grep -qF "$MARKER" "$HOOK_PATH"; then
        echo -e "${GREEN}✅ pre-commit hook already contains cross-agents sync logic.${NC}"
    else
        echo -e "${YELLOW}⚠️  pre-commit hook exists. Appending cross-agents sync logic...${NC}"
        echo "" >> "$HOOK_PATH"
        echo "$HOOK_CONTENT" >> "$HOOK_PATH"
        echo -e "${GREEN}✅ Appended to existing hook.${NC}"
    fi
else
    echo "#!/bin/bash" > "$HOOK_PATH"
    echo "" >> "$HOOK_PATH"
    echo "$HOOK_CONTENT" >> "$HOOK_PATH"
    echo -e "${GREEN}✅ Created .git/hooks/pre-commit with cross-agents sync logic.${NC}"
fi

chmod +x "$HOOK_PATH"
echo -e "${GREEN}🔗 hook is now executable.${NC}"
echo ""
echo "   On each commit, CLAUDE.md symlinks will be synced from staged AGENTS.md changes."
