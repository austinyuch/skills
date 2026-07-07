#!/usr/bin/env sh
# test-bundle-chain.sh — positive + NEGATIVE regression tests for the download-on-install chain.
# The positive case is verify-bundle.sh (emit -> install -> bytes==source). The negative case
# proves the fail-closed SHA gate actually REJECTS a corrupted artifact instead of installing it:
# emit a manifest, then TAMPER the staged binary (flip a byte) and assert install-bundle.sh exits
# non-zero with a checksum mismatch. Guards install-bundle's core safety property as a test, not
# an assumption. [CR-2026-07-04-074, hardening the CR-071/072/073 chain]
#
# Usage: test-bundle-chain.sh [<tool> <bundle-dir>]   (default: xreview against this scripts dir)
set -eu
here=$(dirname -- "$0"); here=$(cd -- "$here" && pwd)
tool="${1:-xreview}"
dir="${2:-$here}"
dir=$(cd -- "$dir" && pwd)

fail=0

echo "=== [1/2] POSITIVE round-trip (verify-bundle.sh $tool) ==="
if sh "$here/verify-bundle.sh" "$tool" "$dir" >/dev/null 2>&1; then
  echo "  PASS: positive round-trip verified"
else
  echo "  FAIL: positive round-trip did not verify" >&2; fail=1
fi

echo "=== [2/2] NEGATIVE tamper (install-bundle.sh must REJECT a corrupted artifact) ==="
stage=$(mktemp -d 2>/dev/null || mktemp -d -t bundlechain)
dest=$(mktemp -d 2>/dev/null || mktemp -d -t bundlechaindest)
trap 'rm -rf "$stage" "$dest"' EXIT HUP INT TERM

# Stage this tool's artifacts, emit a manifest over the PRISTINE bytes...
candidates="${tool}-linux-amd64 ${tool}-linux-arm64 ${tool}-darwin-amd64 ${tool}-darwin-arm64 \
            ${tool}-windows-amd64.exe ${tool}-windows-arm64.exe ${tool}"
staged=0
for f in $candidates; do
  if [ -f "$dir/$f" ]; then cp "$dir/$f" "$stage/$f"; staged=$((staged + 1)); fi
done
[ "$staged" -gt 0 ] || { echo "  SKIP: no artifacts for '$tool' in $dir" >&2; exit 77; }
sh "$here/emit-bundle-manifest.sh" "$tool" "$stage" --version tamper-test >/dev/null

# ...then CORRUPT every staged binary AFTER the manifest was computed, so the recorded sha no
# longer matches. install-bundle.sh must refuse (fail-closed), leaving no verified binary behind.
for f in "$stage"/*; do
  case "$f" in *-bundle-manifest.json) continue ;; esac
  printf 'TAMPERED-EXTRA-BYTES' >> "$f"
done

set +e
out=$(sh "$here/install-bundle.sh" "$stage" "$dest" "$tool" 2>&1)
rc=$?
set -e
# resolve the artifact name install-bundle would have written (host per-platform, or bare tool)
os=$(uname -s); case "$os" in Linux) os=linux ;; Darwin) os=darwin ;; MINGW*|MSYS*|CYGWIN*) os=windows ;; esac
arch=$(uname -m); case "$arch" in x86_64|amd64) arch=amd64 ;; aarch64|arm64) arch=arm64 ;; esac
binname="${tool}-${os}-${arch}"; [ "$os" = windows ] && binname="${binname}.exe"
# set -e-safe: a bare `[ ] || [ ]` returning 1 (both absent — the EXPECTED reject) would abort.
if [ -f "$dest/$binname" ] || [ -f "$dest/$tool" ]; then promoted=0; else promoted=1; fi

if [ "$rc" -ne 0 ] && [ "$promoted" -ne 0 ]; then
  echo "  PASS: tampered artifact REJECTED (install exit=$rc, no verified binary promoted)"
  case "$out" in *checksum*|*mismatch*) echo "  (reason: checksum mismatch, as expected)" ;; esac
else
  echo "  FAIL: tampered artifact was NOT rejected (install exit=$rc, promoted=$promoted) — SHA gate broken!" >&2
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  echo "=== ALL PASS: chain verifies pristine bytes and rejects tampered bytes ==="
  exit 0
fi
echo "=== FAIL: see above ===" >&2
exit 1
