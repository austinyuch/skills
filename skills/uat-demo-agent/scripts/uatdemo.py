#!/usr/bin/env python3
"""Cross-platform wrapper for the bundled or installed uatdemo CLI."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath


SCRIPT_DIR = Path(__file__).resolve().parent
HOME = Path.home()
SKILL_INSTALL_ROOTS = [
    HOME / ".config" / "opencode" / "skills",
    HOME / ".claude" / "skills",
    HOME / ".gemini" / "config" / "skills",
    HOME / ".kiro" / "skills",
]


def read_config_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def expand_config_path(raw: str) -> Path:
    expanded = os.path.expandvars(raw)
    return Path(expanded).expanduser()


def detect_binary_name() -> str | None:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        arch = "amd64"
    elif machine in {"aarch64", "arm64"}:
        arch = "arm64"
    else:
        return None
    mapping = {
        "linux": f"uatdemo-linux-{arch}",
        "darwin": f"uatdemo-darwin-{arch}",
        "windows": f"uatdemo-windows-{arch}.exe",
    }
    return mapping.get(system)


def resolve_binary() -> list[str]:
    env_override = os.environ.get("UATDEMO_BIN", "").strip()
    if env_override:
        return [resolve_command_value(project_root(), env_override)]
    global_cfg = read_config_file(global_config_path(project_root()))
    global_bin = global_cfg.get("UATDEMO_BIN", "").strip()
    if global_bin:
        return [resolve_command_value(project_root(), global_bin)]
    bundled_name = detect_binary_name()
    if bundled_name:
        bundled = SCRIPT_DIR / bundled_name
        if bundled.exists():
            return [str(bundled)]
        # ISSUE-DIST-004: the platform binaries are delivered as GitHub release assets, not
        # committed to git. If this host's binary is absent, self-heal by fetching it from the
        # release (SHA-256-verified) into SCRIPT_DIR on first use, then use it.
        fetched = try_fetch_bundle_binary(bundled_name)
        if fetched is not None:
            return [str(fetched)]
    path_binary = shutil.which("uatdemo")
    if path_binary:
        return [path_binary]
    raise SystemExit(
        "uatdemo wrapper could not resolve a CLI binary via UATDEMO_BIN, global config, bundled "
        "binaries, PATH, or a GitHub-release fetch. Run "
        "`bash install-bundle.sh gh:<owner/repo>@latest <scripts-dir>` or set UATDEMO_BIN."
    )


def bundle_release_pointer() -> dict:
    """Read the committed bundle-release.json pointer (where release binaries live)."""
    path = SCRIPT_DIR / "bundle-release.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def bundle_sources() -> list[str]:
    """Ordered candidate sources for fetching this host's uatdemo binary.

    UATDEMO_BUNDLE_SOURCE overrides everything (a local dir / https prefix / gh:owner/repo@tag);
    otherwise derive from the pointer: prefer the latest release, then a pinned tag if set.
    """
    override = os.environ.get("UATDEMO_BUNDLE_SOURCE", "").strip()
    if override:
        return [override]
    pointer = bundle_release_pointer()
    repo = str(pointer.get("repo", "")).strip()
    sources: list[str] = []
    if repo:
        if pointer.get("preferLatest", True):
            sources.append(f"gh:{repo}@latest")
        pinned = pointer.get("pinnedTag")
        if pinned:
            sources.append(f"gh:{repo}@{pinned}")
    return sources


def try_fetch_bundle_binary(binary_name: str) -> Path | None:
    """Best-effort fetch of the host binary from a release into SCRIPT_DIR; None on failure."""
    installer = SCRIPT_DIR / "install-bundle.sh"
    if not installer.exists() or shutil.which("bash") is None:
        return None
    for source in bundle_sources():
        print(f"uatdemo: binary not bundled; fetching from {source} ...", file=sys.stderr)
        try:
            subprocess.run(
                ["bash", str(installer), source, str(SCRIPT_DIR)],
                check=True,
                stdout=sys.stderr,
                stderr=sys.stderr,
            )
        except (subprocess.CalledProcessError, OSError):
            continue
        candidate = SCRIPT_DIR / binary_name
        if candidate.exists():
            return candidate
    return None


def discover_project_root(start: Path) -> Path:
    current = start.resolve()
    while True:
        if current.name == "admin-ui" and (current / "src").exists():
            return current.parent.resolve()
        if (current / ".uatdemo").exists() or (current / "admin-ui" / "src").exists() or (current / "go.mod").exists():
            return current.resolve()
        if current.parent == current:
            return start.resolve()
        current = current.parent


def project_root() -> Path:
    explicit_project_config = explicit_project_config_path()
    if explicit_project_config is not None:
        return infer_project_root(explicit_project_config)
    return discover_project_root(Path.cwd().resolve())


def explicit_project_config_path() -> Path | None:
    raw = os.environ.get("UATDEMO_PROJECT_CONFIG", "").strip()
    if not raw:
        return None
    return resolve_project_relative_path(discover_project_root(Path.cwd().resolve()), raw)


def global_config_path(root: Path) -> Path:
    raw = os.environ.get("UATDEMO_GLOBAL_CONFIG", "").strip()
    if raw:
        return resolve_project_relative_path(root, raw)
    return HOME / ".config" / "uatdemo" / "config.env"


def infer_project_root(config_path: Path) -> Path:
    if config_path.parent.name == ".uatdemo":
        return config_path.parent.parent.resolve()
    return config_path.parent.resolve()


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def is_skill_install_path(root: Path) -> bool:
    return any(is_within(root, candidate) for candidate in SKILL_INSTALL_ROOTS)


def should_use_project_local_defaults(root: Path) -> bool:
    return not is_skill_install_path(root)


def project_config_path(root: Path) -> Path | None:
    explicit = explicit_project_config_path()
    if explicit is not None:
        return explicit
    if should_use_project_local_defaults(root):
        return root / ".uatdemo" / "config.env"
    return None


def read_project_config(root: Path) -> dict[str, str]:
    path = project_config_path(root)
    if path is None:
        return {}
    return read_config_file(path)


def default_user_state_dir() -> Path:
    xdg_state_home = os.environ.get("XDG_STATE_HOME", "").strip()
    if xdg_state_home:
        return expand_config_path(xdg_state_home) / "uatdemo"
    system = platform.system().lower()
    if system == "windows":
        local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
        if local_app_data:
            return expand_config_path(local_app_data) / "uatdemo"
    if system == "darwin":
        return HOME / "Library" / "Application Support" / "uatdemo"
    return HOME / ".local" / "state" / "uatdemo"


def resolve_command_value(root: Path, raw: str) -> str:
    if os.sep not in raw and (os.altsep is None or os.altsep not in raw) and not raw.startswith((".", "~", "$", "%")):
        return raw
    return str(resolve_project_relative_path(root, raw))


def resolve_runtime_state_dir(root: Path) -> Path:
    env_state = os.environ.get("UATDEMO_STATE_DIR", "").strip()
    if env_state:
        return resolve_project_relative_path(root, env_state)

    global_cfg = read_config_file(global_config_path(root))
    project_cfg = read_project_config(root)
    project_state = project_cfg.get("UATDEMO_STATE_DIR", "").strip()
    global_state = global_cfg.get("UATDEMO_STATE_DIR", "").strip()
    if project_state:
        return resolve_project_relative_path(root, project_state)
    if global_state:
        return resolve_project_relative_path(root, global_state)
    if should_use_project_local_defaults(root):
        return root / ".uatdemo"
    return default_user_state_dir()


def resolve_project_relative_path(root: Path, raw: str) -> Path:
    candidate = expand_config_path(raw)
    if candidate.is_absolute():
        return candidate.resolve()
    return (root / candidate).resolve()


def runtime_gitignore_entries(relative_dir: str) -> set[str]:
    accepted: set[str] = set()
    parts = PurePosixPath(relative_dir).parts
    current: list[str] = []
    for part in parts:
        current.append(part)
        prefix = "/".join(current)
        accepted.update({prefix, f"{prefix}/", f"/{prefix}", f"/{prefix}/"})
    return accepted


def read_gitignore_entries(path: Path) -> set[str]:
    entries: set[str] = set()
    if not path.exists():
        return entries
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            entries.add(line)
    return entries


def ensure_project_runtime_dir_ignored(root: Path, state_dir: Path) -> None:
    try:
        relative_dir = state_dir.relative_to(root).as_posix()
    except ValueError:
        return
    if not relative_dir or relative_dir == ".":
        return

    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        accepted = sorted(runtime_gitignore_entries(relative_dir))
        raise SystemExit(
            f"uatdemo wrapper requires {gitignore_path} to ignore runtime directory '{relative_dir}/'. "
            f"Add one of: {', '.join(accepted)}"
        )

    configured_entries = read_gitignore_entries(gitignore_path)
    accepted_entries = runtime_gitignore_entries(relative_dir)
    if configured_entries & accepted_entries:
        return

    accepted = sorted(accepted_entries)
    raise SystemExit(
        f"uatdemo wrapper requires {gitignore_path} to ignore runtime directory '{relative_dir}/'. "
        f"Add one of: {', '.join(accepted)}"
    )


def main(argv: list[str]) -> int:
    root = project_root()
    state_dir = resolve_runtime_state_dir(root)
    os.environ["UATDEMO_STATE_DIR"] = str(state_dir)
    if os.environ.get("UATDEMO_SKIP_GITIGNORE_CHECK", "").strip() != "1":
        ensure_project_runtime_dir_ignored(root, state_dir)
    cmd = resolve_binary() + argv[1:]
    completed = subprocess.run(cmd, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
