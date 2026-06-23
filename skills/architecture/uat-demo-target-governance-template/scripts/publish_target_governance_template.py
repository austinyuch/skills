#!/usr/bin/env python3
"""Workspace-local wrapper for publishing the target-governance template skill."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install_target_governance_template_skill.py"


def main() -> int:
    result = subprocess.run([sys.executable, str(INSTALL_SCRIPT)], cwd=str(REPO_ROOT))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
