#!/usr/bin/env bash
# Install this code-review helper skill from its canonical repo source to the global
# Agent Skills dir the runtime reads. Self-naming (derives the skill name from its own
# directory) and idempotent.
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="$(basename "$SRC_DIR")"
DEST_DIR="${OPENCODE_SKILLS_DIR:-$HOME/.config/opencode/skills}/$SKILL_NAME"

mkdir -p "$DEST_DIR/scripts" "$DEST_DIR/references"
cp "$SRC_DIR/SKILL.md" "$DEST_DIR/SKILL.md"
cp "$SRC_DIR"/scripts/run.py "$SRC_DIR"/scripts/llm_provider.py "$SRC_DIR"/scripts/test_run.py "$DEST_DIR/scripts/"
chmod +x "$DEST_DIR/scripts/run.py"
if compgen -G "$SRC_DIR/references/*" > /dev/null; then
  cp "$SRC_DIR"/references/* "$DEST_DIR/references/"
fi

echo "installed $SKILL_NAME -> $DEST_DIR"
echo "run.py: $DEST_DIR/scripts/run.py"
