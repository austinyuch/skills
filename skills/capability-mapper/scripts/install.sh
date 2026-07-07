#!/usr/bin/env bash
# Install the capability-mapper skill from its canonical repo source to the global
# Agent Skills dir the runtime reads (Spec #54). Idempotent.
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_DIR="${OPENCODE_SKILLS_DIR:-$HOME/.config/opencode/skills}/capability-mapper"

mkdir -p "$DEST_DIR/scripts"
cp "$SRC_DIR/SKILL.md" "$DEST_DIR/SKILL.md"
cp "$SRC_DIR/scripts/run.py" "$DEST_DIR/scripts/run.py"
cp "$SRC_DIR/scripts/test_run.py" "$DEST_DIR/scripts/test_run.py"
chmod +x "$DEST_DIR/scripts/run.py"

echo "installed capability-mapper -> $DEST_DIR"
echo "run.py: $DEST_DIR/scripts/run.py"
