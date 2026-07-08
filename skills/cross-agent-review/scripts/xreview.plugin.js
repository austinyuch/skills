// xreview — cross-agent review trigger plugin (canonical source).
//
// This is the readable, version-controlled source of the opencode `session.idle`
// trigger. To ACTIVATE it, run `xreview install --agent opencode`, which writes a
// machine-resolved copy to ~/.config/opencode/plugins/xreview.js with the local
// binary path baked in (see SKILL.md "Auto-trigger"). This template instead
// resolves the binary at RUNTIME by os/arch, so it also works if copied into
// ~/.config/opencode/plugins/ by hand or shipped as-is.
//
// On session idle, dispatch a different-model-family review of the current scope.
// Advisory: a failure here never disrupts the opencode session. Marker: xreview
import { homedir, platform, arch } from "os"
import { join } from "path"
import { existsSync } from "fs"

function resolveBin() {
  // 1) explicit override wins
  if (process.env.XREVIEW_BIN) return process.env.XREVIEW_BIN
  // 2) resolve xreview-<os>-<arch> under an explicit skill dir, or the
  // flat global skill home.
  const os = platform() === "win32" ? "windows" : platform() // linux | darwin | windows
  const cpu = arch() === "x64" ? "amd64" : arch()            // amd64 | arm64
  const ext = os === "windows" ? ".exe" : ""
  const name = `xreview-${os}-${cpu}${ext}`
  if (process.env.XREVIEW_SKILL_DIR) return join(process.env.XREVIEW_SKILL_DIR, "scripts", name)
  return join(homedir(), ".config", "opencode", "skills", "cross-agent-review", "scripts", name)
}

const XREVIEW_BIN = resolveBin()

export const XReviewTrigger = async ({ $, directory, worktree }) => {
  return {
    event: async ({ event }) => {
      if (!event || event.type !== "session.idle") return
      if (!existsSync(XREVIEW_BIN)) return // binary not resolved → advisory no-op
      const dir = worktree || directory || process.cwd()
      try {
        await $`${XREVIEW_BIN} run --host-agent opencode --cwd ${dir}`.quiet().nothrow()
      } catch (_) { /* advisory: swallow */ }
    }
  }
}
