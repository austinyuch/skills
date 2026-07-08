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

# code-review's native CLI lives in GitHub Releases (the repo is private, so the
# download is authenticated via `gh`). Bump CLI_TAG when a new binary is released.
CLI_REPO = "austinyuch/skills"
CLI_TAG = "review-cli-v0.16.1"


def review_cli_asset() -> str | None:
    import platform
    o = {"darwin": "darwin", "linux": "linux", "windows": "windows"}.get(platform.system().lower())
    m = platform.machine().lower()
    a = "arm64" if m in ("arm64", "aarch64") else ("amd64" if m in ("x86_64", "amd64") else None)
    if not o or not a:
        return None
    return f"review-cli-{o}-{a}" + (".exe" if o == "windows" else "")


def fetch_review_cli(target: Path) -> None:
    asset = review_cli_asset()
    dest = target / "code-review" / "scripts"
    if not asset:
        print("   ⚠️  unsupported platform for review-cli"); return
    if not dest.exists():
        print("   ⚠️  code-review not installed — skipping --with-cli"); return
    cmd = ["gh", "release", "download", CLI_TAG, "-R", CLI_REPO, "-p", asset, "-D", str(dest), "--clobber"]
    try:
        print(f"⬇️  fetching {asset} from {CLI_REPO}@{CLI_TAG} (gh) …")
        subprocess.run(cmd, check=True)
        f = dest / asset
        if os.name != "nt":
            f.chmod(0o755)
        print(f"   ✅ review-cli installed: {f}")
    except FileNotFoundError:
        print("   ⚠️  GitHub CLI (gh) not found. Install gh + auth, then:")
        print(f'      gh release download {CLI_TAG} -R {CLI_REPO} -p {asset} -D "{dest}" --clobber')
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  could not fetch review-cli (gh exit {e.returncode}).")
        print(f'      gh release download {CLI_TAG} -R {CLI_REPO} -p {asset} -D "{dest}" --clobber')

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
    p.add_argument("--with-cli", action="store_true", help="also fetch code-review's review-cli binary via gh (needs auth)")
    # --layout kept for backward compatibility: flat is the only supported layout
    # (one-level loaders like Claude Code cannot discover a nested category tree).
    p.add_argument("--layout", choices=("flat",), default="flat", help=argparse.SUPPRESS)
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
    print("🧭 Layout: flat (single-level)\n")
    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    installed = missing = 0

    def copy_dir(src: Path, dst: Path, name: str) -> None:
        nonlocal installed, missing
        if not src.is_dir():
            print(f"   ⚠️  missing: {name}"); missing += 1; return
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        print(f"   ✅ {name}"); installed += 1

    for skill in manifest.get("skills", []):
        copy_dir(source / skill, target / skill, skill)

    for row in manifest.get("standalone_files", []):
        src = source / row["file"]
        dst = target / row["target_path"]
        if not src.is_file():
            print(f"   ⚠️  missing file: {row['file']}"); missing += 1; continue
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        print(f"   ✅ {dst.relative_to(target)}"); installed += 1

    print("\n" + "━" * 32)
    print(f"📊 {'Would install' if args.dry_run else 'Installed'}: {installed}   ⚠️  Missing: {missing}")
    print("━" * 32)
    print(f"Skills {'would be' if args.dry_run else 'are now'} in: {target}")
    if (target / "code-review").exists() and not args.dry_run:
        if args.with_cli:
            fetch_review_cli(target)
        else:
            print('ℹ️  code-review\'s review-cli binary is not bundled — re-run with --with-cli to fetch it '
                  '(needs gh auth; the repo is private). See README "Native binaries".')
    return 0


if __name__ == "__main__":
    sys.exit(main())
