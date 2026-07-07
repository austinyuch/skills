#!/usr/bin/env sh
# Fetch-on-install for a native tool bundle: download (or copy) ONLY the host's single
# platform binary and verify it against the bundle manifest, so a downstream consumer
# need not git-LFS-commit all six (~300 MB) into its own history. Pairs with the manifest
# emitted by build-binaries.sh. [CR-2026-07-03-017, completes CR-2026-07-03-016 for the
# aclab-opencode-config binary-distribution-lfs request; auth-aware + tool-parameterized
# per CR-2026-07-04 install-bundle request Update]
#
# Usage: install-bundle.sh <source> <dest-scripts-dir> [tool] [--tool NAME]
#   <source> = one of:
#              - a base URL  ("https://…/")          → curl fetch; Bearer auth if a
#                                                       GH_TOKEN/GITHUB_TOKEN env var is set
#                                                       (private release assets served over http)
#              - a local dir ("./bundle", "/abs")    → cp
#              - "gh://OWNER/REPO@TAG"                → `gh release download` (uses gh's own
#                                                       auth, so it reaches PRIVATE release assets)
#   <dest>   = the skill scripts/ dir to place the resolved binary + manifest into.
#   [tool]   = binary family to install (default: xreview), as an optional 3rd positional
#              arg OR via --tool NAME. Selects the "<tool>-<os>-<arch>" binary name and the
#              "<tool>-bundle-manifest.json" (falls back to "bundle-manifest.json" for legacy
#              single-tool bundles). e.g. install-bundle.sh gh://o/r@v1 dest/ review-cli
# The consumer should GITIGNORE the placed binary (it is a verified build artifact), the
# same way it gitignores plugins/xreview.js, .xreview/, .vendor/.
set -eu

tool=""
src=""
dest=""
usage="usage: install-bundle.sh <source-url-dir-or-gh> <dest-scripts-dir> [tool] [--tool NAME]"
# Positionals: <source> <dest> [tool]; --tool NAME (or --tool=NAME) also sets the tool.
while [ $# -gt 0 ]; do
  case "$1" in
    --tool) [ $# -ge 2 ] || { echo "$usage" >&2; exit 2; }; tool="$2"; shift 2 ;;
    --tool=) echo "--tool= requires a value" >&2; exit 2 ;;
    --tool=*) tool="${1#--tool=}"; shift ;;
    -h|--help) echo "$usage" >&2; exit 0 ;;
    *) if [ -z "$src" ]; then src="$1"
       elif [ -z "$dest" ]; then dest="$1"
       elif [ -z "$tool" ]; then tool="$1"
       else echo "unexpected argument: $1" >&2; exit 2; fi; shift ;;
  esac
done
tool="${tool:-xreview}"
if [ -z "$src" ] || [ -z "$dest" ]; then
  echo "$usage" >&2
  exit 2
fi
# Constrain the tool name: it becomes a filename and a `gh --pattern`, so reject path
# separators / leading dots / glob-or-shell metacharacters (no traversal, no glob injection).
case "$tool" in
  *[!A-Za-z0-9._-]*|""|.*|*/*) echo "invalid tool name: $tool" >&2; exit 2 ;;
esac
mkdir -p "$dest"

# Clean up partial downloads on any exit/interrupt (temps are only promoted after verification).
tmp="$dest/.bundle-manifest.json.tmp"
bin_tmp=""
trap 'rm -f "$tmp" "$bin_tmp"' EXIT HUP INT TERM

# Resolve host os/arch → binary filename.
os=$(uname -s 2>/dev/null || echo unknown)
case "$os" in
  Linux) os=linux ;;
  Darwin) os=darwin ;;
  MINGW*|MSYS*|CYGWIN*|Windows_NT) os=windows ;;
  *) echo "unsupported OS: $os" >&2; exit 1 ;;
esac
arch=$(uname -m 2>/dev/null || echo unknown)
case "$arch" in
  x86_64|amd64) arch=amd64 ;;
  aarch64|arm64) arch=arm64 ;;
  *) echo "unsupported arch: $arch" >&2; exit 1 ;;
esac
# Preferred per-platform artifact name; the actual name is confirmed against the manifest
# below (an arch-less artifact like embedding-runner is published under its bare tool name).
bin="${tool}-${os}-${arch}"
[ "$os" = windows ] && bin="${bin}.exe"

# gh://OWNER/REPO@TAG → parse repo + tag for `gh release download`.
gh_repo=""; gh_tag=""
case "$src" in
  gh://*)
    _rest="${src#gh://}"          # OWNER/REPO@TAG
    gh_repo="${_rest%@*}"         # OWNER/REPO
    gh_tag="${_rest##*@}"         # TAG
    if [ "$gh_repo" = "$_rest" ] || [ -z "$gh_repo" ] || [ -z "$gh_tag" ]; then
      echo "malformed gh source (want gh://OWNER/REPO@TAG): $src" >&2; exit 2
    fi
    command -v gh >/dev/null 2>&1 || { echo "gh CLI required for gh:// sources but not found on PATH" >&2; exit 1; }
    ;;
esac

# fetch <relpath> <out>: resolve a single bundle file from the source.
#   gh://   → gh release download (auth via gh; reaches private assets)
#   http(s) → curl; add Authorization: Bearer $GH_TOKEN/$GITHUB_TOKEN ONLY for a GitHub host
#             (never leak the token to an arbitrary URL)
#   dir     → cp
fetch() {
  case "$src" in
    gh://*)
      gh release download "$gh_tag" --repo "$gh_repo" --pattern "$1" --output "$2" --clobber
      ;;
    http://*|https://*)
      _tok="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
      _host=${src#*://}; _host=${_host%%/*}; _host=${_host%%:*}   # host, port stripped
      case "$_host" in
        github.com|*.github.com) _gh_host=1 ;;
        *) _gh_host=0 ;;
      esac
      if [ -n "$_tok" ] && [ "$_gh_host" = 1 ]; then
        curl -fsSL -H "Authorization: Bearer $_tok" "${src%/}/$1" -o "$2"
      else
        curl -fsSL "${src%/}/$1" -o "$2"
      fi
      ;;
    *) cp "${src%/}/$1" "$2" ;;
  esac
}

# Resolve the manifest, PREFERRING a committed/reviewed manifest already at the destination as
# the TRUST ANCHOR. A locally-present manifest is NEVER overwritten by a fetched one — otherwise
# a compromised release could serve both a tampered binary AND matching checksums, making the
# committed manifest decorative. Only when no local manifest exists do we fetch one (the original
# gitignored-artifact model, e.g. xreview). [CR-2026-07-06-097]
manifest_name="${tool}-bundle-manifest.json"
if [ -f "$dest/$manifest_name" ]; then
  :                                          # committed tool-scoped manifest → trust anchor
elif [ -f "$dest/bundle-manifest.json" ]; then
  manifest_name="bundle-manifest.json"       # committed legacy manifest → trust anchor
elif fetch "$manifest_name" "$tmp" 2>/dev/null; then
  mv "$tmp" "$dest/$manifest_name"
elif fetch "bundle-manifest.json" "$tmp"; then
  manifest_name="bundle-manifest.json"; mv "$tmp" "$dest/$manifest_name"
else
  echo "no bundle manifest: none committed at $dest and none fetchable ($manifest_name or bundle-manifest.json) from $src" >&2
  exit 1
fi

# Resolve the artifact name + its sha256 from the manifest. Prefer the per-platform name
# ("<tool>-<os>-<arch>"); if absent, accept a bare "<tool>" entry (arch-less artifact like
# embedding-runner). Prints "<name> <sha256>" or nothing when neither is present.
resolved=$(python3 - "$dest/$manifest_name" "$bin" "$tool" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
plat = m.get("platforms", {})
for name in (sys.argv[2], sys.argv[3]):   # per-platform, then bare tool
    p = plat.get(name)
    if p:
        print("%s %s" % (name, p["sha256"]))   # names/shas are space-free
        break
PY
)
if [ -z "$resolved" ]; then
  echo "manifest has no entry for $bin (or bare $tool)" >&2
  exit 1
fi
bin=${resolved%% *}
want=${resolved#* }

bin_tmp="$dest/$bin.tmp"
fetch "$bin" "$bin_tmp"
sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}';
  else shasum -a 256 "$1" | awk '{print $1}'; fi
}
got=$(sha256_of "$bin_tmp")
if [ "$got" != "$want" ]; then
  echo "checksum mismatch for $bin: got $got want $want" >&2
  exit 1
fi
mv "$bin_tmp" "$dest/$bin"; bin_tmp=""
chmod +x "$dest/$bin" 2>/dev/null || true

echo "installed $bin (sha256 verified) → $dest"
echo "recommend: gitignore this binary — add to your .gitignore:"
# Per-platform artifacts glob as "<tool>-*"; an arch-less artifact is its own bare name.
if [ "$bin" = "$tool" ]; then
  echo "  $(basename "$dest")/${bin}"
else
  echo "  $(basename "$dest")/${tool}-*"
fi
