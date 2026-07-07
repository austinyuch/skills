#!/usr/bin/env sh
# Populate this skill's scripts/ with the 6-platform xreview binaries from the
# Go source of truth. Binaries are build artifacts, not committed raw (same
# native-binary release model as the code-review skill).
set -eu
here=$(dirname -- "$0"); here=$(cd -- "$here" && pwd)
repo="${1:-}"
if [ -z "$repo" ]; then
  echo "usage: build-binaries.sh <path-to-go-review-service>" >&2
  exit 2
fi
( cd "$repo" && make build-all-xreview )
bins="xreview-linux-amd64 xreview-linux-arm64 xreview-darwin-amd64 xreview-darwin-arm64 \
      xreview-windows-amd64.exe xreview-windows-arm64.exe"
for f in $bins; do
  cp "$repo/bin/$f" "$here/$f"
done
echo "populated $here with 6 platform binaries"

# Emit a SHA-256 + version manifest so a downstream consumer can fetch a single
# platform binary and verify it (download-on-install) instead of git-LFS-committing all
# six (~300 MB) into its own history. The manifest travels with the bundle to the skill
# homes (publish.sh copies scripts/); it is a build artifact (gitignored), not committed.
# [CR-2026-07-03-016, addressing aclab-opencode-config binary-distribution-lfs request]
sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}';
  else shasum -a 256 "$1" | awk '{print $1}'; fi
}
bytes_of() { wc -c < "$1" | tr -d ' '; }
version="$(git -C "$repo" rev-parse --short HEAD 2>/dev/null || echo dev)"
manifest="$here/bundle-manifest.json"
{
  printf '{\n  "tool": "xreview",\n  "version": "%s",\n  "platforms": {\n' "$version"
  first=1
  for f in $bins; do
    [ "$first" = 1 ] || printf ',\n'; first=0
    printf '    "%s": { "sha256": "%s", "bytes": %s }' "$f" "$(sha256_of "$here/$f")" "$(bytes_of "$here/$f")"
  done
  printf '\n  }\n}\n'
} > "$manifest"
# Also emit the tool-scoped manifest name so an install-bundle.sh consumer can host several
# tools' manifests (xreview / review-cli / uatdemo) side by side in ONE release directory
# without collision; install-bundle.sh prefers "<tool>-bundle-manifest.json" and falls back
# to the legacy "bundle-manifest.json". [CR-2026-07-04 install-bundle tool-parameterization]
cp "$manifest" "$here/xreview-bundle-manifest.json"
echo "wrote manifest $manifest (+ xreview-bundle-manifest.json) (version $version)"
