#!/usr/bin/env sh
# verify-bundle.sh — round-trip self-test of the download-on-install chain for ONE tool.
# Proves emit-bundle-manifest.sh -> install-bundle.sh end to end with NO network: it stages
# the tool's artifacts into a temp release dir, emits the manifest, installs the host-platform
# binary via the local-dir (cp) source, and asserts the installed bytes are SHA-256-identical
# to the ORIGINAL source artifact. install-bundle.sh already verifies the fetched bytes against
# the manifest (fail-closed); this additionally proves the manifest's recorded sha equals the
# real source bytes, closing the loop producer->manifest->fetch->bytes. A one-command
# regression guard for the bundle chain (previously hand-rolled shell each CR).
# [CR-2026-07-04-073, hardening the CR-071/072 distribution chain]
#
# Usage: verify-bundle.sh <tool> <bundle-dir> [--version V]
#   <tool>        binary family, e.g. review-cli, xreview, embedding-runner
#   <bundle-dir>  dir holding "<tool>-<os>-<arch>[.exe]" and/or a bare "<tool>"
#   --version V   version stamp passed through to emit-bundle-manifest.sh (optional)
# Exit 0 = round-trip verified; non-zero = a break anywhere in emit/install/sha.
set -eu
here=$(dirname -- "$0"); here=$(cd -- "$here" && pwd)

tool="${1:-}"; dir="${2:-}"
if [ -z "$tool" ] || [ -z "$dir" ]; then
  echo "usage: verify-bundle.sh <tool> <bundle-dir> [--version V]" >&2
  exit 2
fi
shift 2
# Same filename-safety guard as install-bundle.sh / emit-bundle-manifest.sh: $tool is
# interpolated into candidate paths + cp destinations, so reject path separators / leading
# dots / glob-or-shell metacharacters (no traversal outside <bundle-dir> or the temp stage).
case "$tool" in
  *[!A-Za-z0-9._-]*|""|.*|*/*) echo "invalid tool name: $tool" >&2; exit 2 ;;
esac
version=""
while [ $# -gt 0 ]; do
  case "$1" in
    --version) [ $# -ge 2 ] || { echo "--version needs a value" >&2; exit 2; }; version="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
[ -d "$dir" ] || { echo "not a directory: $dir" >&2; exit 1; }
dir=$(cd -- "$dir" && pwd)

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}';
  else shasum -a 256 "$1" | awk '{print $1}'; fi
}

# Stage a temp release dir with only this tool's artifacts, so we never mutate <bundle-dir>
# (emit-bundle-manifest.sh writes its manifest into the dir it scans).
stage=$(mktemp -d 2>/dev/null || mktemp -d -t verifybundle)
dest=$(mktemp -d 2>/dev/null || mktemp -d -t verifybundledest)
trap 'rm -rf "$stage" "$dest"' EXIT HUP INT TERM

candidates="${tool}-linux-amd64 ${tool}-linux-arm64 ${tool}-darwin-amd64 ${tool}-darwin-arm64 \
            ${tool}-windows-amd64.exe ${tool}-windows-arm64.exe ${tool}"
staged=0
for f in $candidates; do
  if [ -f "$dir/$f" ]; then cp "$dir/$f" "$stage/$f"; staged=$((staged + 1)); fi
done
[ "$staged" -gt 0 ] || { echo "no artifacts for tool '$tool' in $dir" >&2; exit 1; }

# 1) emit the platforms-shape manifest into the stage
if [ -n "$version" ]; then
  sh "$here/emit-bundle-manifest.sh" "$tool" "$stage" --version "$version" >&2
else
  sh "$here/emit-bundle-manifest.sh" "$tool" "$stage" >&2
fi

# 2) install the host-platform binary from the stage (local-dir cp source) into a temp dest
out=$(sh "$here/install-bundle.sh" "$stage" "$dest" "$tool")
echo "$out" >&2
bin=$(printf '%s\n' "$out" | sed -n 's/^installed \([^ ]*\) .*/\1/p')
[ -n "$bin" ] || { echo "could not determine installed binary name from install output" >&2; exit 1; }

# 3) assert installed bytes == original source bytes (independent of the manifest)
[ -f "$dest/$bin" ] || { echo "installed binary missing: $dest/$bin" >&2; exit 1; }
[ -f "$dir/$bin" ]  || { echo "source artifact missing: $dir/$bin" >&2; exit 1; }
src_sha=$(sha256_of "$dir/$bin")
got_sha=$(sha256_of "$dest/$bin")
if [ "$src_sha" != "$got_sha" ]; then
  echo "ROUND-TRIP FAILED: installed $bin sha $got_sha != source $src_sha" >&2
  exit 1
fi
echo "OK: $tool round-trip verified — installed $bin sha256=$got_sha matches source"
