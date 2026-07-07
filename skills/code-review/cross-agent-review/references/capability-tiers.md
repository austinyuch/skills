# Capability Tiers (probed 2026-07-01, linux/x86_64)

Independence is judged on **model family**, not CLI name — `kiro`/`opencode`/`antigravity`
can each host multiple families. Verify before relying; CLIs self-update.

## Headless reviewer (can be dispatched to review)

| Backend | Command | Family | Status |
|---------|---------|--------|--------|
| claude | `claude -p` | anthropic | verified |
| codex | `codex exec` (`-c model=`) | openai | **verified live** (gpt-5.5) |
| antigravity | `agy -p` | google | **blocked**: exits 0 but no stdout in non-TTY; needs `--log-file` capture path |
| opencode | `opencode run -m <prov/model>` | multi | adapter exists; needs `cards update` to seed families |
| kiro | `kiro-cli chat --no-interactive --trust-all-tools --model M` | deepseek/minimax/glm/qwen (+claude) | adapter wired; **live-blocked**: kiro-cli's rust→kiro-cli-chat→detached-bun-TUI leaves a descendant that hangs `os/exec` Wait() past the dispatch timeout (survived procgroup-kill + file-redirect + stderr=nil). Needs a session/output API or non-TUI mode |

## Author trigger (fires review when the agent finishes) — updated 2026-07-02

`xreview install --agent <name>` writes the correct mechanism per agent. All installers merge
(never clobber), are idempotent, back up, and uninstall only their own entry. Idempotency/uninstall
match the `run --host-agent` invocation signature (not the binary filename → survives a rename).

| Backend | Mechanism (event) | Status |
|---------|-------------------|--------|
| claude | native `Stop` hook in `~/.claude/settings.json` (deep-merge) | **verified (live)** |
| codex | `Stop` hook in `~/.codex/hooks.json` — schema identical to Claude (CODEX_HOME-aware) | **runtime-fire LIVE-PROVEN** — after a one-time interactive `/hooks` trust (codex safety gate; `--dangerously-bypass-hook-trust` NOT used), a plain `codex exec` fired it → auditable record |
| opencode | JS plugin `~/.config/opencode/plugins/xreview.js` on `session.idle` (Bun `$`) | **shipped + live-validated** — plugin behavior proven under Bun (opencode's runtime) + `opencode models` load smoke; live authenticated session.idle fire is host-bound |
| kiro | `hooks.stop` in a **kiro-cli agent config** (`~/.kiro/agents/<name>.json`) | **shipped** — installer output validated via `kiro-cli agent validate`. Kiro hooks are **per-agent** (event set `agentSpawn|userPromptSubmit|preToolUse|postToolUse|stop`); xreview uses `stop`. Default dedicated agent `xreview`; use `--settings <agent.json>` to attach to your own agent. Live session fire is host-bound |
| antigravity (agy) | an **agy plugin** — `plugin.json` + **root-level** `hooks.json` (Claude-style `Stop`), registered via `agy plugin install <dir>` | **shipped** — end-to-end validated on-host: `agy plugin install` accepts the plugin (`agy plugin list` → `components: [hooks]`, source antigravity), `uninstall` removes it. agy's hook engine has a `stop` event (binary: `stop_hooks`/`StopHookArgs`). **Correction:** agy's trigger surface is the **plugin system**, NOT `~/.gemini/antigravity-cli/settings.json` (that flat schema has no hooks — the earlier "not shipped/unverified" call looked at the wrong surface). Live session-end fire is host-bound |

Note on kiro: the older sample-config `$schema` points at upstream `amazon-q-developer-cli` (only `agentSpawn`/`userPromptSubmit`), but the **installed kiro-cli** binary accepts `stop` (+`preToolUse`/`postToolUse`) — verified empirically via `kiro-cli agent validate`.

## Rule

The installer and orchestrator label every trigger `verified | adapter-pending |
needs-investigation` in output and in the review-record, and degrade honestly rather than
claim an unverified path works. No false green.
