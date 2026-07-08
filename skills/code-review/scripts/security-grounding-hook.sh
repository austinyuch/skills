#!/usr/bin/env bash
# Advisory Stop-hook wrapper for review-cli security grounding.
#
# Claude, Codex, and Kiro Stop hooks are synchronous command contracts. This
# wrapper captures the hook payload, starts the bounded grounding scan in the
# background, and exits 0 immediately so advisory review never blocks session
# shutdown. Results are written to a per-agent log directory.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
os="$(uname -s | tr '[:upper:]' '[:lower:]')"
case "$os" in
  mingw*|msys*|cygwin*) os="windows" ;;
esac
machine="$(uname -m | tr '[:upper:]' '[:lower:]')"
case "$machine" in
  x86_64|amd64) arch="amd64" ;;
  aarch64|arm64) arch="arm64" ;;
  *) arch="$machine" ;;
esac
ext=""
if [ "$os" = "windows" ]; then
  ext=".exe"
fi

BIN="${REVIEW_CLI_BIN:-$SCRIPT_DIR/review-cli-${os}-${arch}${ext}}"
TIMEOUT_SECONDS="${SECURITY_GROUNDING_TIMEOUT:-45}"
LOG_DIR="${SECURITY_GROUNDING_LOG_DIR:-$HOME/.cache/code-review/security-grounding}"
if ! mkdir -p "$LOG_DIR" 2>/dev/null; then
  LOG_DIR="/tmp/code-review-security-grounding-${USER:-user}"
  mkdir -p "$LOG_DIR" 2>/dev/null || LOG_DIR="/tmp"
fi

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
payload="$LOG_DIR/payload-${stamp}-$$.json"
stdout_log="$LOG_DIR/grounding-${stamp}-$$.stdout"
stderr_log="$LOG_DIR/grounding-${stamp}-$$.stderr"
status_log="$LOG_DIR/grounding-${stamp}-$$.status"
run_script="$LOG_DIR/grounding-${stamp}-$$.run.sh"

cat > "$payload" || true
printf "exit_code=dispatched\npayload=%s\nstdout=%s\nstderr=%s\n" \
  "$payload" "$stdout_log" "$stderr_log" > "$status_log" 2>/dev/null || true

cat > "$run_script" <<EOF
#!/usr/bin/env bash
rc=0
"$BIN" security grounding \\
  --hook-mode \\
  --warn-only \\
  --stderr \\
  --timeout "$TIMEOUT_SECONDS" \\
  < "$payload" \\
  > "$stdout_log" \\
  2> "$stderr_log" || rc=\$?
printf "exit_code=%s\\npayload=%s\\nstdout=%s\\nstderr=%s\\n" \\
  "\$rc" "$payload" "$stdout_log" "$stderr_log" > "$status_log"
EOF
chmod +x "$run_script" 2>/dev/null || true

if command -v setsid >/dev/null 2>&1; then
  setsid "$run_script" >/dev/null 2>&1 </dev/null &
else
  nohup "$run_script" >/dev/null 2>&1 </dev/null &
fi

printf "security-grounding advisory scan started: %s\n" "$status_log" >&2
exit 0
