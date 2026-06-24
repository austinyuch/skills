#!/usr/bin/env python3
"""aclab-skills — cross-platform skill installer (Python stdlib only).

  uvx --from git+https://github.com/austinyuch/skills aclab-skills <agent>
  pipx run --spec git+https://github.com/austinyuch/skills aclab-skills <agent>
  python3 bin/aclab_skills.py <agent>            (from a checkout)

<agent> = opencode | claude | codex | kiro   (default: opencode)
Override the destination with --target <dir> or SKILLS_TARGET=<dir>.

When run as an installed tool (uvx/pipx) outside a checkout, the skill data is
not bundled in the wheel, so the CLI shallow-clones the repo into a cache dir.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/austinyuch/skills"

AGENT_HOMES = {
    "opencode": lambda: (Path(os.environ["XDG_CONFIG_HOME"]) / "opencode" / "skills")
    if os.environ.get("XDG_CONFIG_HOME")
    else Path.home() / ".config" / "opencode" / "skills",
    "claude": lambda: Path.home() / ".claude" / "skills",
    "codex": lambda: Path.home() / ".codex" / "skills",
    "kiro": lambda: Path.home() / ".kiro" / "skills",
}


def find_data_root(start: Path) -> Path | None:
    """Walk up from `start` to find a dir holding skills-manifest.json + skills/."""
    for d in [start, *start.parents]:
        if (d / "skills-manifest.json").is_file() and (d / "skills").is_dir():
            return d
    return None


def cache_clone() -> Path:
    """Shallow-clone (or refresh) the repo into a stable cache dir, return its path."""
    base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "aclab-skills"
    repo = base / "repo"
    base.mkdir(parents=True, exist_ok=True)
    if (repo / "skills-manifest.json").is_file():
        subprocess.run(["git", "-C", str(repo), "pull", "--ff-only", "--depth", "1"],
                       check=False, capture_output=True)
    else:
        print(f"⬇️  fetching skills from {REPO_URL} …")
        subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(repo)], check=True)
    return repo


def main() -> int:
    p = argparse.ArgumentParser(prog="aclab-skills", description="Install aclab skills into a coding agent's skill home.")
    p.add_argument("agent", nargs="?", default="opencode", help="opencode | claude | codex | kiro")
    p.add_argument("--target", help="explicit destination dir (wins over <agent>)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    target = args.target or os.environ.get("SKILLS_TARGET")
    if not target:
        if args.agent not in AGENT_HOMES:
            p.error(f"unknown agent: {args.agent} (use opencode|claude|codex|kiro, or --target)")
        target = str(AGENT_HOMES[args.agent]())
    target = Path(target)

    root = find_data_root(Path(__file__).resolve().parent)
    if root is None:
        root = cache_clone()
    manifest = json.loads((root / "skills-manifest.json").read_text(encoding="utf-8"))
    source = root / "skills"

    print(f"📦 aclab skills from: {root}")
    print(f"🤖 Agent: {'custom' if args.target or os.environ.get('SKILLS_TARGET') else args.agent}")
    print(f"🎯 Target: {target}{'  (dry-run)' if args.dry_run else ''}\n")
    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    installed = missing = 0

    def copy_dir(src: Path, dst: Path, name: str) -> None:
        nonlocal installed, missing
        if not src.is_dir():
            print(f"   ⚠️  missing: {name}"); missing += 1; return
        if not args.dry_run:
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        print(f"   ✅ {name}"); installed += 1

    for group in ("families", "categories"):
        for key, val in (manifest.get(group) or {}).items():
            for skill in val.get("skills", []):
                copy_dir(source / key / skill, target / skill, skill)

    for row in manifest.get("standalone_files", []):
        src = source / row["category"] / row["target_path"]
        dst = target / row["file"]
        if not src.is_file():
            print(f"   ⚠️  missing file: {row['file']}"); missing += 1; continue
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        print(f"   ✅ {row['file']}"); installed += 1

    print("\n" + "━" * 32)
    print(f"📊 {'Would install' if args.dry_run else 'Installed'}: {installed}   ⚠️  Missing: {missing}")
    print("━" * 32)
    print(f"Skills {'would be' if args.dry_run else 'are now'} in: {target}")
    if (target / "code-review").exists():
        print('ℹ️  code-review needs a review-cli-<os>-<arch> binary (not bundled) — see README "Native binaries".')
    return 0


if __name__ == "__main__":
    sys.exit(main())
