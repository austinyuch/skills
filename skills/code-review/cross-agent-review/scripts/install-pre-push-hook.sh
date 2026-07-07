#!/usr/bin/env sh
# install-pre-push-hook.sh — wire pre-merge-dogfood.sh into a repo as a git pre-push hook.
# Defaults to FAST + NON-BLOCKING (--quick --advisory): the hook runs a cross-family review of the
# diff on every push and prints findings, but never blocks and skips the slow CAP-8 matrix — so it
# dogfoods without turning every push into a multi-minute gate. Opt into enforcement explicitly.
# The authoritative gate is still the full `pre-merge-dogfood.sh` run BEFORE opening a merge PR.
# [CR-2026-07-04-075]
#
# Usage: install-pre-push-hook.sh [--repo DIR] [--enforce] [--full] [--uninstall]
#   --repo DIR   target git repo (default: the repo this skill lives in / cwd's repo)
#   --enforce    hook blocks the push on findings (default: advisory/non-blocking)
#   --full       hook runs the CAP-8 matrix too (slow; default: --quick diff-review only)
#   --uninstall  remove a hook this script installed (leaves foreign hooks untouched)
set -eu
here=$(dirname -- "$0"); here=$(cd -- "$here" && pwd)

repo=""; enforce=0; full=0; uninstall=0
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) [ $# -ge 2 ] || { echo "--repo needs a value" >&2; exit 2; }; repo="$2"; shift 2 ;;
    --enforce) enforce=1; shift ;;
    --full) full=1; shift ;;
    --uninstall) uninstall=1; shift ;;
    -h|--help) echo "usage: install-pre-push-hook.sh [--repo DIR] [--enforce] [--full] [--uninstall]"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$repo" ]; then repo=$(git -C "$here" rev-parse --show-toplevel 2>/dev/null || pwd); fi
# Resolve the ABSOLUTE git dir (canonical, no relative-path composition) → hooks dir.
gitdir=$(git -C "$repo" rev-parse --absolute-git-dir 2>/dev/null) || { echo "not a git repo: $repo" >&2; exit 1; }
hooks_dir="$gitdir/hooks"
hook="$hooks_dir/pre-push"
marker="# managed-by: cross-agent-review/install-pre-push-hook.sh"

# A symlink at the hook path is a redirection vector (cat >/chmod +x/rm would follow it and touch a
# file OUTSIDE hooks_dir). Refuse to operate on a symlinked hook path — for both install and uninstall.
if [ -L "$hook" ]; then
  echo "refusing to act on a symlinked pre-push hook: $hook" >&2; exit 1
fi
# "managed by us" = the marker present as an EXACT WHOLE LINE (grep -Fxq: fixed-string, full-line), so a
# foreign hook that merely contains the marker text somewhere is NOT mistaken for ours.
is_managed() { [ -f "$1" ] && grep -Fxq -- "$marker" "$1" 2>/dev/null; }

if [ "$uninstall" -eq 1 ]; then
  if is_managed "$hook"; then
    rm -f "$hook"; echo "removed managed pre-push hook: $hook"
  else
    echo "no managed pre-push hook to remove (foreign hook, if any, left untouched): $hook" >&2
  fi
  exit 0
fi

if [ -f "$hook" ] && ! is_managed "$hook"; then
  echo "refusing to overwrite a foreign pre-push hook: $hook" >&2
  echo "(remove it yourself or back it up first)" >&2
  exit 1
fi

flags=""
[ "$enforce" -eq 1 ] || flags="--advisory"
[ "$full" -eq 1 ] || flags="$flags --quick"

mkdir -p "$hooks_dir"
# Write to a temp file in hooks_dir then atomically rename (never write through a pre-existing path).
hook_tmp="$hooks_dir/.pre-push.tmp.$$"
trap 'rm -f "$hook_tmp"' EXIT HUP INT TERM
cat > "$hook_tmp" <<EOF
#!/usr/bin/env sh
$marker
# Cross-family review of the outgoing diff. Non-blocking + quick unless reinstalled with --enforce/--full.
exec sh "$here/pre-merge-dogfood.sh" $flags
EOF
chmod +x "$hook_tmp"
mv -f "$hook_tmp" "$hook"
echo "installed pre-push hook → $hook"
echo "  mode: $( [ "$enforce" -eq 1 ] && echo ENFORCE || echo advisory ) $( [ "$full" -eq 1 ] && echo '(full CAP-8 matrix)' || echo '(--quick diff-review only)')"
echo "  uninstall: install-pre-push-hook.sh --uninstall --repo $repo"
