#!/usr/bin/env sh
# Print the path to the xreview binary matching this host's OS/arch.
# Platform-agnostic: never hard-code a binary name.
set -eu
here="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

os="$(uname -s 2>/dev/null || echo unknown)"
case "$os" in
  Linux)  goos=linux ;;
  Darwin) goos=darwin ;;
  MINGW*|MSYS*|CYGWIN*|Windows_NT) goos=windows ;;
  *) goos=linux ;;
esac

arch="$(uname -m 2>/dev/null || echo x86_64)"
case "$arch" in
  x86_64|amd64) goarch=amd64 ;;
  arm64|aarch64) goarch=arm64 ;;
  *) goarch=amd64 ;;
esac

if [ "$goos" = "windows" ]; then
  echo "$here/xreview-$goos-$goarch.exe"
else
  echo "$here/xreview-$goos-$goarch"
fi
