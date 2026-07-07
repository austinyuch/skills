---
name: local-llm-agent-migrator
description: Point a coding-agent CLI (Claude Code, OpenAI Codex CLI, or OpenCode) at the locally-hosted LLM (local-nemotron, served by vLLM via the TensorZero adapter). Use whenever the user wants an agent to use the local/self-hosted model instead of a cloud provider — e.g. "make Codex use the local model", "switch Claude Code to local-nemotron", "point opencode at the local LLM", "use my own GPU model for the agent", "stop using the cloud API for codex", "onboard this laptop to the local model over the LAN/WiFi", or "undo the local-model change / put codex back". Also use to verify a local-model route is live or to roll a migration back. Trigger this even if the user names the model or agent loosely (e.g. "the nemotron", "the GB10 model", "my local server").
---

# Local LLM Agent Migrator

Routes Claude Code / Codex / OpenCode at the self-hosted model **`local-nemotron`**
through the **TensorZero adapter strategy** (one adapter, OpenAI + Anthropic
surfaces, ClickHouse observability). This skill is a thin driver over the spec's
migration dispatcher — it does not reimplement the logic.

> Authoritative tooling + evaluation + full runbook:
> `scripts/agent-llm-routing/migrate.py` and `docs/LOCAL_LLM_AGENT_ROUTING.md`
> (spec `.agents/specs/local-llm-cli-agent-routing/`). Read the doc when the user
> needs background, troubleshooting, or the LAN architecture.

## Decide the route profile first

Pick the profile before running anything — it changes the endpoint and what works:

| Situation | Profile | Notes |
|-----------|---------|-------|
| Agent runs **on the model's host** (this server), want observability | `adapter` *(default)* | localhost:13001; calls recorded in ClickHouse |
| On-host, want lowest latency, don't need Claude Code or observability | `direct` | vLLM directly; **no Anthropic surface → Claude Code not supported on this profile** |
| Agent runs on **another machine on the WiFi/LAN** | `lan` | Traefik `https://vllm.local:8443`, needs the bearer key + name resolution |

If unsure and the work is on this host, use `adapter`.

## Workflow

All commands run from the repo root. The dispatcher takes an agent
(`codex` | `opencode` | `claude` | `all`) and `--profile`.

1. **Preview** (safe, no writes):
   ```bash
   python3 scripts/agent-llm-routing/migrate.py <agent> --profile <profile> --dry-run
   ```
2. **Migrate** (backs up the existing config first, idempotent):
   ```bash
   python3 scripts/agent-llm-routing/migrate.py <agent> --profile <profile>
   ```
3. **Verify the route is actually live** (promotes "configured" to "working"):
   ```bash
   export VLLM_API_KEY="$(cat vllm-serving/.api_key)"   # needed for direct/lan
   python3 scripts/agent-llm-routing/migrate.py <agent> --verify --profile <profile>
   ```
   A `FAIL` here usually means the serving stack is down — start it with the
   `vllm-serving-manager` skill, then re-verify. Report the real status; do not
   claim success on a config write alone.
4. **Roll back** if asked to undo:
   ```bash
   python3 scripts/agent-llm-routing/migrate.py <agent> --rollback
   ```

After migrating, tell the user the one extra step their agent needs:
- **Codex**: select the provider with `codex --profile local-nemotron`.
- **OpenCode / Claude Code**: pick model `local-nemotron`; for Claude Code,
  restart it so the new `ANTHROPIC_BASE_URL` env takes effect.

## LAN / WiFi onboarding

When the request is about reaching the model from **another machine**:

- On this server, first confirm the front door is healthy:
  ```bash
  scripts/agent-llm-routing/lan_server_check.sh
  ```
  It prints the server LAN IP and the client command to run.
- Linux client: `scripts/agent-llm-routing/lan_client_linux.sh --server-ip <ip> --key-file <key> [--agent <name>] [--apply]`
- Windows client (elevated PowerShell): `scripts/agent-llm-routing/lan_client_windows.ps1 -ServerIp <ip> -KeyFile <key> [-Agent <name>] -Apply`

The bearer key is in `vllm-serving/.api_key` on the server — copy it to the client
securely and never commit it.

## Guardrails

- **Don't start the serving stack from here.** If `--verify` shows the model is
  down, hand off to the `vllm-serving-manager` skill (and governed runtime) to
  bring vLLM/TensorZero up; this skill only configures agents.
- **Claude Code tool-use is a known gap on the local route**: text chat works via
  the adapter's `/v1/messages`, but OpenAI→Anthropic `tool_use` streaming is not
  yet translated, so agentic tool loops in Claude Code are not covered. Say so if
  the user expects full tool-calling in Claude Code; Codex/OpenCode are unaffected.
- **Never inline the bearer key** in configs or messages — the tooling references
  it via `VLLM_API_KEY` / key files and masks it in output.
- Migrations are reversible; if a write looks risky, run `--dry-run` first and show
  the user the planned endpoint + target file.
