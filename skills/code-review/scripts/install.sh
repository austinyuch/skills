#!/usr/bin/env sh
# Download-on-install for the review-cli binary. The six `review-cli-<os>-<arch>` binaries
# (~300 MB total) are NO LONGER committed to the repo via git-LFS — they are published as a
# GitHub release and fetched on demand. This script downloads + SHA-256-verifies ONLY the
# single binary for THIS host (from review-cli-bundle-manifest.json, which travels with the
# bundle), so a clone / skill-home install carries just one platform binary, not all six.
# [CR-2026-07-06 binaries-gh-release-migration; wraps the CR-073 install-bundle.sh chain]
#
# Run once after cloning or installing the skill, before the first `review-cli ...` call:
#     sh scripts/install.sh
#
# Source resolution (override with REVIEW_CLI_RELEASE):
#   gh://OWNER/REPO@TAG   → `gh release download` (uses gh auth; reaches PRIVATE release assets)
#   https://BASE/         → curl (Bearer $GH_TOKEN/$GITHUB_TOKEN for github.com hosts)
#   /local/dir            → cp (offline / air-gapped mirror)
# The fetched binary is a verified build artifact and is gitignored — never commit it back.
set -eu

here=$(dirname -- "$0"); here=$(cd -- "$here" && pwd)
release="${REVIEW_CLI_RELEASE:-https://github.com/austinyuch/aclab-code-review/releases/download/v0.16.1/}"

if [ ! -f "$here/install-bundle.sh" ]; then
  echo "install.sh: missing install-bundle.sh next to it (bundle incomplete)" >&2
  exit 1
fi

echo "review-cli: fetching this host's binary from $release ..." >&2
sh "$here/install-bundle.sh" "$release" "$here" --tool review-cli
echo "review-cli: ready (run: $here/review-cli-\$(uname -s)-\$(uname -m) --help)" >&2

# ONNX embedding model bundle (model.onnx + tokenizer + configs, ~127 MB). Needed for local
# semantic search; fetched as ONE sha-verified .zip from the SAME release and unzipped into
# assets/models/. Skip with REVIEW_CLI_SKIP_ONNX=1 if you only use review-cli without semantic
# search (the download is idempotent — re-running install.sh does not re-fetch it). [CR-097]
if [ "${REVIEW_CLI_SKIP_ONNX:-0}" = 1 ]; then
  echo "onnx model: skipped (REVIEW_CLI_SKIP_ONNX=1) — semantic search will be unavailable until installed" >&2
elif [ -f "$here/install-model-bundle.sh" ]; then
  echo "onnx model: fetching embedding bundle from $release ..." >&2
  sh "$here/install-model-bundle.sh" "$release" "$here/.."
else
  echo "onnx model: install-model-bundle.sh missing next to install.sh — skipping model fetch" >&2
fi
