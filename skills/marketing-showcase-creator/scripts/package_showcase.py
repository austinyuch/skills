#!/usr/bin/env python3
"""Package a value-driven showcase (plus manual/review, if present) into a
single email-ready zip.

Why: potential customers get one attachment they can open offline — the
bilingual showcase, and any operator manual / product review that lives
alongside it.

Cross-platform, standard library only (no third-party deps).

Usage
-----
Auto-detect showcase/manual/review under a docs directory:
    python package_showcase.py --docs docs -o showcase-bundle.zip

Explicitly choose which directories to include:
    python package_showcase.py \
        --include docs/showcase --include docs/manual --include docs/review \
        -o showcase-bundle.zip

Notes
-----
- Only web/document assets are packed (html/css/js/images/md/json/pdf/fonts).
- Junk (node_modules, .git, caches, OS cruft) is skipped.
- A manifest (files + sizes) is printed so you can eyeball it before sending.
"""
from __future__ import annotations

import argparse
import os
import sys
import zipfile

# Asset types worth shipping to a customer.
ALLOWED_EXT = {
    ".html", ".htm", ".css", ".js", ".mjs",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".md", ".json", ".pdf",
    ".woff", ".woff2", ".ttf", ".otf",
}

# Directory names never worth shipping.
SKIP_DIRS = {
    "node_modules", ".git", ".svn", "__pycache__",
    ".next", ".cache", ".turbo", "dist", "build", ".DS_Store",
}

# Auto-detect these subdirectories under --docs (order = manifest order).
AUTO_SUBDIRS = ["showcase", "manual", "review"]


def human(nbytes: int) -> str:
    size = float(nbytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f}{unit}" if unit != "B" else f"{int(size)}B"
        size /= 1024
    return f"{size:.1f}GB"


def collect(root: str) -> list[str]:
    """Return files under root worth packing, filtered by extension and skiplist.

    Symlinks (files or directories) are refused when their real target escapes
    ``root`` — otherwise a ``docs/showcase/leak.md`` symlink could copy content
    from outside the include tree into the customer zip.
    """
    picked: list[str] = []
    root_real = os.path.realpath(root)
    root_prefix = root_real + os.sep
    for dirpath, dirnames, filenames in os.walk(root):  # followlinks=False
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name == ".DS_Store":
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext not in ALLOWED_EXT:
                continue
            fpath = os.path.join(dirpath, name)
            real = os.path.realpath(fpath)
            if real != root_real and not real.startswith(root_prefix):
                print(f"  ! skip (symlink escapes {root}): {fpath}",
                      file=sys.stderr)
                continue
            picked.append(fpath)
    return picked


def resolve_includes(args: argparse.Namespace) -> list[str]:
    includes: list[str] = []
    if args.include:
        for path in args.include:
            if os.path.isdir(path):
                includes.append(os.path.normpath(path))
            else:
                print(f"  ! skip (not a directory): {path}", file=sys.stderr)
    if args.docs:
        for sub in AUTO_SUBDIRS:
            candidate = os.path.join(args.docs, sub)
            if os.path.isdir(candidate):
                norm = os.path.normpath(candidate)
                if norm not in includes:
                    includes.append(norm)
    return includes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs", help="docs directory to auto-detect "
                                    "showcase/manual/review under")
    ap.add_argument("--include", action="append",
                    help="explicit directory to include (repeatable)")
    ap.add_argument("-o", "--output", default="showcase-bundle.zip",
                    help="output zip path (default: showcase-bundle.zip)")
    ap.add_argument("--base", default=None,
                    help="path prefix to strip inside the zip "
                         "(default: common parent of included dirs)")
    args = ap.parse_args()

    if not args.docs and not args.include:
        ap.error("provide --docs and/or one or more --include directories")

    includes = resolve_includes(args)
    if not includes:
        print("No showcase/manual/review directories found to package.",
              file=sys.stderr)
        return 1

    # Arcname base: strip the common *parent* of the included dirs so each one
    # becomes a clean top-level dir in the zip (showcase/..., manual/...,
    # review/...). Using commonpath of the parents keeps this correct whether a
    # single dir or several sibling dirs are included -- os.path.commonpath of a
    # single dir returns that dir, and its dirname would otherwise strip one
    # level too many when multiple siblings collapse to their shared parent.
    base = args.base
    if base is None:
        base = os.path.commonpath([os.path.dirname(os.path.abspath(p))
                                   for p in includes])

    manifest: list[tuple[str, int]] = []
    total = 0
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as zf:
        for root in includes:
            files = collect(root)
            if not files:
                print(f"  ! no packable files under {root}", file=sys.stderr)
                continue
            for fpath in sorted(files):
                arc = os.path.relpath(os.path.abspath(fpath), base)
                arc = arc.replace(os.sep, "/")
                zf.write(fpath, arc)
                size = os.path.getsize(fpath)
                manifest.append((arc, size))
                total += size

    if not manifest:
        os.remove(args.output)
        print("Nothing packaged (no matching assets).", file=sys.stderr)
        return 1

    print(f"Packaged {len(manifest)} files -> {args.output} "
          f"({human(os.path.getsize(args.output))} zipped, "
          f"{human(total)} raw)\n")
    print("Manifest:")
    for arc, size in manifest:
        print(f"  {human(size):>8}  {arc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
