#!/usr/bin/env bash
# install-bundle.sh — fetch-on-install for the uatdemo platform binary (ISSUE-DIST-001).
#
# Resolves THIS host's os/arch, fetches ONLY that one `uatdemo-<os>-<arch>` binary plus
# `bundle-manifest.json` from <source>, verifies the SHA-256 against the manifest, and
# installs it into <dest> (a scripts dir) as a build artifact you can gitignore — so a
# consumer never commits the platform binaries into its own git history.
#
# Usage:
#   install-bundle.sh <source> <dest>
#
# <source> forms:
#   /path/to/dir          local directory holding uatdemo-* + bundle-manifest.json (cp)
#   https://host/prefix   URL prefix; fetches <prefix>/bundle-manifest.json + <prefix>/<bin> (curl)
#   gh:owner/repo@tag     GitHub release assets; uses `gh` auth, or GH_TOKEN/GITHUB_TOKEN
#                         bearer against the release assets API (works for PRIVATE repos)
#   gh:owner/repo@latest  resolve the repo's LATEST published release tag, then fetch it
#
# Version-check: if <dest>/<bin> already exists and its SHA-256 matches the fetched
# manifest's entry for this platform, the binary is already current — the (large) binary
# download is skipped and only the (small) manifest was fetched. This makes repeated
# installs / runtime self-heal cheap and idempotent.
#
# Requires: bash, python3 (JSON parse), and sha256sum or shasum. curl for URL mode; gh or
# a token + curl for gh mode.
set -euo pipefail

die() { echo "install-bundle: $*" >&2; exit 1; }

[ "$#" -eq 2 ] || die "usage: install-bundle.sh <source> <dest>"
source_ref="$1"
dest="$2"

# --- resolve host os/arch -> binary name ------------------------------------------
os="$(uname -s | tr '[:upper:]' '[:lower:]')"
case "$os" in
  mingw*|msys*|cygwin*|windows*) os="windows" ;;
esac
arch="$(uname -m)"
case "$arch" in
  x86_64|amd64) arch="amd64" ;;
  aarch64|arm64) arch="arm64" ;;
esac
bin="uatdemo-${os}-${arch}"
[ "$os" = "windows" ] && bin="${bin}.exe"

mkdir -p "$dest"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

manifest="$tmp/bundle-manifest.json"
fetched_bin="$tmp/$bin"

sha256() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | cut -d' ' -f1
  else die "need sha256sum or shasum to verify the download"; fi
}

# --- gh helpers (token passed via -K stdin so it never lands in the process argv) --
# Read GitHub token from environment (GH_TOKEN or GITHUB_TOKEN) using indirect expansion
_gh_auth=""
for _ev in GH_TOKEN GITHUB_TOKEN; do
  _tkn="${!_ev:-}"
  [ -n "$_tkn" ] && { _gh_auth="$_tkn"; break; }
done
gh_curl() { # <url> <out> <accept>
  curl -fsSL -H "Accept: $3" -o "$2" -K - "$1" <<CURLCFG
header = "Authorization: Bearer ${_gh_auth}"
CURLCFG
}

resolve_latest_gh_tag() { # <repo> -> tag on stdout, non-zero if unresolved
  local repo="$1"
  if command -v gh >/dev/null 2>&1; then
    gh release view --repo "$repo" --json tagName -q .tagName 2>/dev/null
  else
    [ -n "$_gh_auth" ] || return 1
    local out; out="$(mktemp)"
    gh_curl "https://api.github.com/repos/${repo}/releases/latest" "$out" "application/vnd.github+json" \
      || { rm -f "$out"; return 1; }
    python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("tag_name",""))' "$out"
    rm -f "$out"
  fi
}

fetch_gh_asset() { # <repo> <tag> <asset> <out>
  local repo="$1" tag="$2" asset="$3" out="$4"
  if command -v gh >/dev/null 2>&1; then
    gh release download "$tag" --repo "$repo" --pattern "$asset" --dir "$(dirname "$out")" --clobber >/dev/null 2>&1 \
      || die "gh release download of $asset failed for $repo@$tag"
  else
    [ -n "$_gh_auth" ] || die "gh not installed and no GH_TOKEN/GITHUB_TOKEN for private release API"
    local assets_json; assets_json="$(mktemp)"
    gh_curl "https://api.github.com/repos/${repo}/releases/tags/${tag}" "$assets_json" "application/vnd.github+json" \
      || die "release lookup failed for $repo@$tag"
    local url
    url="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(next((a["url"] for a in d.get("assets",[]) if a["name"]==sys.argv[2]),""))' "$assets_json" "$asset")"
    rm -f "$assets_json"
    [ -n "$url" ] || die "asset $asset not found in release $repo@$tag"
    gh_curl "$url" "$out" "application/octet-stream" || die "download of $asset failed"
  fi
}

# --- resolve the source into a single-asset fetcher -------------------------------
gh_repo=""; gh_tag=""; url_prefix=""; local_dir=""
case "$source_ref" in
  gh:*)
    spec="${source_ref#gh:}"           # owner/repo@tag  (tag may be "latest")
    gh_repo="${spec%@*}"
    gh_tag="${spec#*@}"
    [ "$gh_repo" != "$spec" ] && [ -n "$gh_tag" ] || die "gh source must be gh:owner/repo@tag"
    if [ "$gh_tag" = "latest" ]; then
      gh_tag="$(resolve_latest_gh_tag "$gh_repo")" || die "could not resolve latest release tag for $gh_repo"
      [ -n "$gh_tag" ] || die "no latest release found for $gh_repo"
      echo "install-bundle: resolved latest release of $gh_repo -> $gh_tag" >&2
    fi
    ;;
  https://*) url_prefix="${source_ref%/}" ;;
  http://*)
    # No transport integrity for an unsigned manifest: a MITM could serve a malicious
    # binary AND a matching manifest, and the SHA-256 check would pass against it.
    die "refusing plaintext http:// source; use https:// (or a local dir / gh: release)"
    ;;
  *)
    [ -d "$source_ref" ] || die "local source is not a directory: $source_ref"
    local_dir="$source_ref"
    ;;
esac

fetch_asset() { # <asset> <out>
  local asset="$1" out="$2"
  if [ -n "$gh_repo" ]; then fetch_gh_asset "$gh_repo" "$gh_tag" "$asset" "$out"
  elif [ -n "$url_prefix" ]; then curl -fsSL "${url_prefix}/${asset}" -o "$out" || die "fetch $asset failed"
  else
    [ -f "$local_dir/$asset" ] || die "no $asset in $local_dir"
    cp "$local_dir/$asset" "$out"
  fi
}

# --- fetch the (small) manifest first, then version-check before the (large) binary
fetch_asset "bundle-manifest.json" "$manifest"
[ -f "$manifest" ] || die "bundle-manifest.json was not fetched"

expected="$(python3 -c 'import json,sys; m=json.load(open(sys.argv[1])); print(next((b["sha256"] for b in m.get("binaries",[]) if b["name"]==sys.argv[2]),""))' "$manifest" "$bin")"
[ -n "$expected" ] || die "manifest has no entry for $bin"

# VERSION-CHECK: if the destination binary already matches the manifest's SHA-256 it is
# already the released version — skip the (large) binary download entirely (idempotent).
if [ -f "$dest/$bin" ] && [ "$(sha256 "$dest/$bin")" = "$expected" ]; then
  ver="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("version",""))' "$manifest" 2>/dev/null || true)"
  echo "install-bundle: $bin already current (sha256 matches manifest${ver:+, version=$ver}) — skipping download"
  exit 0
fi

fetch_asset "$bin" "$fetched_bin"
[ -f "$fetched_bin" ] || die "$bin was not fetched"
actual="$(sha256 "$fetched_bin")"
[ "$expected" = "$actual" ] || die "checksum mismatch for $bin (expected $expected, got $actual)"

# Warn on an unreproducible (dirty-tree) build so the operator can reject it.
if python3 -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1])).get("dirty") else 1)' "$manifest" 2>/dev/null; then
  ver="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("version",""))' "$manifest" 2>/dev/null || true)"
  echo "install-bundle: WARNING: manifest marks a DIRTY (uncommitted-tree) build (version=${ver}) — not reproducible" >&2
fi

# --- install --------------------------------------------------------------------
install -m 0755 "$fetched_bin" "$dest/$bin" 2>/dev/null || { cp "$fetched_bin" "$dest/$bin"; chmod 0755 "$dest/$bin" 2>/dev/null || true; }
echo "install-bundle: installed $bin -> $dest/$bin (sha256 verified)"
