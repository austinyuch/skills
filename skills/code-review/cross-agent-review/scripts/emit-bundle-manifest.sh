#!/usr/bin/env sh
# Emit a platforms-shape bundle manifest for ONE tool family, so install-bundle.sh can
# fetch + SHA-256-verify a single platform binary from a (public or PRIVATE) release.
# Generic over the tool: xreview, review-cli, uatdemo (per-platform), and embedding-runner
# (arch-less, single artifact). This is the producer-side complement to install-bundle.sh's
# tool parameterization — the code-review / uat-demo release flows own their binaries but
# emit a differently-shaped manifest, so this fills the platforms-shape gap they need.
# [CR-2026-07-04-072, completes the CR-2026-07-04-071 multi-tool distribution chain]
#
# Usage: emit-bundle-manifest.sh <tool> <bundle-dir> [--version V] [--out FILE]
#   <tool>        binary family, e.g. review-cli, xreview, embedding-runner, uatdemo
#   <bundle-dir>  dir holding "<tool>-<os>-<arch>[.exe]" artifacts and/or a bare "<tool>"
#   --version V   version stamp recorded in the manifest (default: git short SHA of the dir,
#                 else "dev"). Date/time is intentionally NOT used (non-reproducible).
#   --out FILE    output path (default: <bundle-dir>/<tool>-bundle-manifest.json)
#
# Output shape (exactly what install-bundle.sh consumes):
#   { "tool":"<tool>", "version":"<v>", "platforms": {
#       "<file>": { "sha256":"<hex>", "bytes":<n> }, ... } }
set -eu

tool="${1:-}"; dir="${2:-}"
if [ -z "$tool" ] || [ -z "$dir" ]; then
  echo "usage: emit-bundle-manifest.sh <tool> <bundle-dir> [--version V] [--out FILE]" >&2
  exit 2
fi
shift 2
# Same filename-safety guard as install-bundle.sh (tool becomes a filename + JSON value).
case "$tool" in
  *[!A-Za-z0-9._-]*|""|.*|*/*) echo "invalid tool name: $tool" >&2; exit 2 ;;
esac
[ -d "$dir" ] || { echo "not a directory: $dir" >&2; exit 1; }

version=""; out="$dir/${tool}-bundle-manifest.json"
while [ $# -gt 0 ]; do
  case "$1" in
    --version) [ $# -ge 2 ] || { echo "--version needs a value" >&2; exit 2; }; version="$2"; shift 2 ;;
    --out) [ $# -ge 2 ] || { echo "--out needs a value" >&2; exit 2; }; out="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
if [ -z "$version" ]; then
  version="$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo dev)"
fi
# The version is emitted RAW into JSON, so reject anything that could break the string /
# inject a key (quote, backslash, control char). Typical tags (git refs) already satisfy this.
case "$version" in
  *[!A-Za-z0-9._+/-]*|"") echo "invalid version (allowed: A-Za-z0-9._+/-): $version" >&2; exit 2 ;;
esac

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}';
  else shasum -a 256 "$1" | awk '{print $1}'; fi
}
bytes_of() { wc -c < "$1" | tr -d ' '; }

# Collect the artifacts that actually exist: the 6 per-platform names + a bare arch-less one.
candidates="${tool}-linux-amd64 ${tool}-linux-arm64 ${tool}-darwin-amd64 ${tool}-darwin-arm64 \
            ${tool}-windows-amd64.exe ${tool}-windows-arm64.exe ${tool}"
found=""
for f in $candidates; do
  [ -f "$dir/$f" ] && found="$found $f"
done
if [ -z "$found" ]; then
  echo "no artifacts for tool '$tool' in $dir (looked for <tool>-<os>-<arch> and bare <tool>)" >&2
  exit 1
fi

{
  printf '{\n  "tool": "%s",\n  "version": "%s",\n  "platforms": {\n' "$tool" "$version"
  first=1
  for f in $found; do
    [ "$first" = 1 ] || printf ',\n'; first=0
    printf '    "%s": { "sha256": "%s", "bytes": %s }' "$f" "$(sha256_of "$dir/$f")" "$(bytes_of "$dir/$f")"
  done
  printf '\n  }\n}\n'
} > "$out"
echo "wrote $out (tool=$tool version=$version, $(printf '%s' "$found" | wc -w | tr -d ' ') artifact(s))"
