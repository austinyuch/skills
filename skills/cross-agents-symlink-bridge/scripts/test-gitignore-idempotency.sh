#!/bin/bash
# Regression checks for cross-agents .gitignore managed-section idempotency.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync-claude-md.sh"
INIT_SCRIPT="$SCRIPT_DIR/init.sh"

make_repo() {
    local prefix="$1"
    local work
    work="$(mktemp -d "/tmp/${prefix}.XXXXXX")"
    cd "$work"
    git init -q
    git config user.email test@example.invalid
    git config user.name Test
    printf "root instructions\n" > AGENTS.md
    mkdir -p vendor/pkg
    printf "vendored instructions\n" > vendor/pkg/AGENTS.md
    printf "vendored claude\n" > vendor/pkg/CLAUDE.md
    git add AGENTS.md vendor/pkg/AGENTS.md vendor/pkg/CLAUDE.md
    git commit -q -m init
    printf "%s\n" "$work"
}

assert_sync_idempotent() {
    local work
    work="$(make_repo bridge-sync-repro)"
    cd "$work"

    bash "$SYNC_SCRIPT" >/dev/null
    grep -qx "/CLAUDE.md" .gitignore
    if grep -qx "CLAUDE.md" .gitignore; then
        echo "found unanchored CLAUDE.md" >&2
        return 1
    fi
    if git check-ignore -q vendor/pkg/CLAUDE.md; then
        echo "vendored CLAUDE.md is ignored" >&2
        return 1
    fi
    if [ -L vendor/pkg/CLAUDE.md ]; then
        echo "vendored CLAUDE.md symlink was generated" >&2
        return 1
    fi

    git add .gitignore
    git add -f CLAUDE.md
    git commit -q -m bridge-sync

    bash "$SYNC_SCRIPT" >/dev/null
    git diff --exit-code -- .gitignore >/dev/null

    bash "$SYNC_SCRIPT" --staged >/dev/null
    git diff --exit-code -- .gitignore >/dev/null

    git rm -q CLAUDE.md
    bash "$SYNC_SCRIPT" --staged >/dev/null
    git diff --exit-code -- .gitignore >/dev/null

    if git ls-files -i -c --exclude-standard -- vendor/ | grep -q .; then
        echo "tracked vendor files are ignored" >&2
        git ls-files -i -c --exclude-standard -- vendor/ >&2
        return 1
    fi
}

assert_init_idempotent() {
    local work
    work="$(make_repo bridge-init-repro)"
    cd "$work"
    mkdir -p .agents/skills .agents/specs
    touch .agents/skills/.keep .agents/specs/.keep
    git add .agents
    git commit -q -m agents-root

    bash "$INIT_SCRIPT" --specs-mode symlink >/dev/null
    grep -qx "/.claude/specs" .gitignore
    if grep -qx ".claude/specs" .gitignore; then
        echo "found unanchored .claude/specs" >&2
        return 1
    fi

    git add .gitignore .claude .kiro .codex
    git add -f CLAUDE.md
    git commit -q -m bridge-init

    bash "$INIT_SCRIPT" --specs-mode symlink >/dev/null
    git diff --exit-code -- .gitignore >/dev/null
}

assert_sync_idempotent
assert_init_idempotent
echo "status=ok"
