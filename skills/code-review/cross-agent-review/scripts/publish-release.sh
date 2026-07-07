#!/usr/bin/env sh
# Package a native tool bundle for a DOWNLOAD-ON-INSTALL release: stage the platform
# binaries + a platforms-shape <tool>-bundle-manifest.json + a SHA256SUMS file into a
# release dir, then PRINT the exact `gh release create` command. Producer host-side of the
# fetch chain (binaries → emit-bundle-manifest.sh → THIS → install-bundle.sh), so a consumer
# can fetch a single checksum-verified binary from a release URL instead of LFS-committing all.
# [CR-2026-07-03-020; tool-parameterized per CR-2026-07-04-072, completes CR-2026-07-04-071]
#
# Host-agnostic: you pass the tag and (to actually publish) the repo. By DEFAULT it only
# STAGES + PRINTS the command — creating a real release is an outward action, run explicitly.
#
# Usage: publish-release.sh <tag> [--tool NAME] [--from <dir>] [--repo <owner/repo>] [--out <dir>] [--create]
#   <tag>            release tag, e.g. review-cli-v2026.07.04 (or the bundle version)
#   --tool NAME      binary family to release (default: xreview). Also stages a bare arch-less
#                    artifact named exactly <tool> (e.g. embedding-runner) when present.
#   --from <dir>     dir holding the <tool> binaries (default: this script's dir). Point this
#                    at the code-review skill's scripts/ to release review-cli/embedding-runner.
#   --repo <r>       target GitHub repo (required only with --create)
#   --out <dir>      staging dir (default: <scripts>/.release-stage)
#   --create         actually run `gh release create` (outward — omit to just stage+print)
set -eu

here=$(dirname -- "$0"); here=$(cd -- "$here" && pwd)
tag="${1:-}"
if [ -z "$tag" ] || [ "$tag" = "--help" ]; then
  echo "usage: publish-release.sh <tag> [--tool NAME] [--from <dir>] [--repo <owner/repo>] [--out <dir>] [--create]" >&2
  exit 2
fi
shift
tool=xreview; from="$here"; repo=""; out="$here/.release-stage"; create=0
while [ $# -gt 0 ]; do
  case "$1" in
    --tool) [ $# -ge 2 ] || { echo "--tool needs a value" >&2; exit 2; }; tool="$2"; shift 2 ;;
    --from) [ $# -ge 2 ] || { echo "--from needs a value" >&2; exit 2; }; from="$2"; shift 2 ;;
    --repo) [ $# -ge 2 ] || { echo "--repo needs a value" >&2; exit 2; }; repo="$2"; shift 2 ;;
    --out) [ $# -ge 2 ] || { echo "--out needs a value" >&2; exit 2; }; out="$2"; shift 2 ;;
    --create) create=1; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
# Same filename-safety guard as install-bundle.sh / emit-bundle-manifest.sh.
case "$tool" in
  *[!A-Za-z0-9._-]*|""|.*|*/*) echo "invalid tool name: $tool" >&2; exit 2 ;;
esac
[ -d "$from" ] || { echo "not a directory: $from" >&2; exit 1; }

# Collect artifacts. A per-platform tool MUST ship the full 6-platform set (a partial set is a
# fail-open release — consumers on the missing platforms silently can't install); an arch-less
# tool (e.g. embedding-runner) ships only the bare <tool>. So: if ANY per-platform artifact is
# present, require ALL 6. The bare artifact is optional/independent.
platforms="${tool}-linux-amd64 ${tool}-linux-arm64 ${tool}-darwin-amd64 ${tool}-darwin-arm64 \
           ${tool}-windows-amd64.exe ${tool}-windows-arm64.exe"
present=""; missing=""
for f in $platforms; do
  if [ -f "$from/$f" ]; then present="$present $f"; else missing="$missing $f"; fi
done
bins=""
if [ -n "$present" ]; then
  [ -z "$missing" ] || { echo "incomplete $tool platform set in $from — missing:$missing" >&2; exit 1; }
  bins="$platforms"
fi
[ -f "$from/$tool" ] && bins="$bins $tool"
[ -n "$bins" ] || { echo "no $tool binaries found in $from — build them first" >&2; exit 1; }

# (Re)generate the platforms-shape manifest from the actual binaries so it never drifts.
manifest="${tool}-bundle-manifest.json"
sh "$here/emit-bundle-manifest.sh" "$tool" "$from" --version "$tag" --out "$from/$manifest" >&2

rm -rf "$out"; mkdir -p "$out"
for f in $bins; do cp "$from/$f" "$out/$f"; done
cp "$from/$manifest" "$out/$manifest"

# SHA256SUMS over the release assets (portable). $bins/$sha_cmd are intentional word-splits.
sha_cmd="sha256sum"; command -v sha256sum >/dev/null 2>&1 || sha_cmd="shasum -a 256"
# shellcheck disable=SC2086
( cd "$out" && $sha_cmd $bins "$manifest" > SHA256SUMS )

assets=""
for f in $bins "$manifest" SHA256SUMS; do assets="$assets \"$out/$f\""; done
echo "staged $tool release '$tag' → $out"
echo "  assets: $(cd "$out" && printf '%s ' *)"
ghcmd="gh release create \"$tag\"${repo:+ --repo \"$repo\"} --title \"$tool $tag\" --notes \"$tool bundle + $manifest + SHA256SUMS. Install one platform binary: install-bundle.sh <release-download-url> <dest-scripts-dir> $tool (or gh://<owner>/<repo>@$tag <dest> $tool for a private release).\"$assets"

if [ "$create" = 1 ]; then
  [ -n "$repo" ] || { echo "--create requires --repo <owner/repo>" >&2; exit 2; }
  echo "creating release…"; eval "$ghcmd"
else
  echo "dry-run — to publish, run (fill --repo if omitted):"
  echo "  $ghcmd"
fi
