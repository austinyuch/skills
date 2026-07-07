---
name: cross-agent-review
description: Set up and run cross-agent / cross-model code review — where one coding agent's work is independently reviewed by a DIFFERENT model family to avoid single-model blind spots. Use this whenever the user wants a second-opinion / QA / QC review from another agent or model, wants to configure or switch which backend reviews (claude / codex / kiro / opencode / antigravity), wants to auto-trigger review when an agent finishes work (stop-hook), wants to run a one-off independent review of the current changes, or wants to update the SOTA model-card registry. Trigger this even when the user only says things like "have another model check this", "cross-check my changes", "review by a different agent", "set up automatic review when I stop", "install the review hook", or "which model should review this" — the whole point is independent cross-family review, so lean toward using it.
---

# Cross-Agent Review Orchestration (`xreview`)

Independent, cross-model code review. When a coding agent finishes a unit of work, `xreview`
dispatches a **different model family** to run the `code-review` skill over the current scope,
so review independence is real (not a model reviewing its own blind spots). Default pairing is
**Claude ↔ Codex mutual**, with a review↔revise **consensus loop** and honest degradation — it
never silently self-reviews and never blocks the host session.

## Two ways to run it — pick by where you are

| Mode | Use when | How | Cost/setup |
|------|----------|-----|-----------|
| **A. Localhost peer-CLI** (simplest) | Both agents' CLIs are on THIS machine | **You** drive a **different-family peer's own CLI** headlessly (`claude -p`, `codex exec`, `opencode run`, `kiro-cli chat`) over your diff — pure skill, see the **Localhost** section next | **No binary, no API keys, no script.** Each CLI runs on its own subscription |
| **B. `xreview` binary** (server-side / advanced) | Cross-machine, CI/server, API/Bedrock transports, screenshot payloads, consensus loop, or a machine without the peer CLI | The native `xreview-<os>-<arch>` binary resolves a transport (direct-API / Bedrock / exec / ACP / server) and runs the full consensus loop — everything below the Localhost section | Prebuilt binary; keys/creds only for API transports |

Start with **A** on a dev box (it's the whole point of "just call the other agent"). Reach for **B**
when the reviewer isn't a local CLI or you need the binary's transports/consensus/vision payloads.
The binary does not re-implement review logic either — the actual review payload is the `code-review` skill.

## Localhost — you run the review yourself by driving a peer agent's CLI (pure skill, no binary, no script)

On a dev box with more than one coding-agent CLI installed, you do **not** need the `xreview` binary
or any script to get an independent cross-family review — **you perform it directly** by calling a
*different-family* peer coding agent's own CLI over your changes. This section IS the method (it is the
binary's review logic, expressed as instructions for you to follow); there is nothing to install.

**When.** Right after you finish a unit of work, or when asked for a second opinion — and the working
tree has changes. Skip an empty diff, or a scope you already reviewed this way.

**1 · Pick an independent reviewer — a DIFFERENT model family.** Independence is the whole point, so the
reviewer must not share your family:

| Coding agent (CLI) | Family |
|---|---|
| claude (`claude`), kiro (`kiro-cli`) | anthropic |
| codex (`codex`) | openai |
| opencode (`opencode`) | open models |
| antigravity (`agy`) | google |

Primary pairing is **claude ↔ codex**. If your counterpart isn't on PATH, fall back to another
different-family CLI that is (opencode, then kiro). If ONLY a same-family CLI exists, say so honestly
("same-family — weaker than cross-family independence") rather than pass it off as independent — never
review your own family and call it independent.

**2 · Capture the scope.** `git diff` (working tree) or `git diff --staged`. Embed the diff *inside* the
prompt — passing it in means the reviewer needs no file tools and cannot stall on a tool-permission gate.

**3 · Drive the peer's CLI headlessly, diff embedded — one shot, no interaction.** e.g. you are claude,
codex reviews:

```sh
codex exec "You are an INDEPENDENT code reviewer from a different model family. Review ONLY the diff below for correctness bugs, security issues, and clear quality problems. List findings as '- file:line — issue', most severe first; if nothing material, say 'no material findings'. Do not restate the diff.

$(git diff)"
```

Swap the leading command for whichever peer you picked:

| Peer | Headless one-shot |
|---|---|
| claude | `claude -p "<prompt>"` |
| codex | `codex exec "<prompt>"` |
| opencode | `opencode run "<prompt>"` |
| kiro | `kiro-cli chat "<prompt>"` |

> **Automated/no-tty gotcha (from an eval run):** when you drive these from a hook, script, or any
> context without a terminal, **close stdin** — e.g. `codex exec "<prompt>" < /dev/null`. Otherwise
> `codex exec` prints *"Reading additional input from stdin…"* and blocks forever waiting for more input.
> Interactively (an agent's own shell with a tty) it's not needed, but `< /dev/null` is always safe.

**4 · Act on the findings, then converge (optional).** Present or apply them. To re-review after you
revise, **resume the peer's OWN session** so it keeps the prior context — this is the review→revise
consensus loop, run through the peer CLI's native lifecycle, which you control:

| Peer | Continue last | Resume a specific session | List / pick / other |
|---|---|---|---|
| claude | `claude --continue` | `claude --resume <name>` | `claude --from-pr <number>` — review a PR headlessly (`claude -p` is the one-shot form) |
| codex | `codex resume --last` | `codex resume <session_id>` | `codex resume` — interactive picker (`codex exec "…"` is the one-shot form) |
| opencode | `opencode run -c "…"` (`--continue`) | `opencode run -s <id> "…"` (`--session`) | `opencode sessions --list` |
| kiro | `kiro-cli chat --resume` (`-r`, most recent) | `kiro-cli chat --resume-id <session_id>` | `kiro-cli chat --resume-picker` · `kiro-cli chat --list-sessions` |

**5 · Stay advisory and bounded.** Findings inform; they never block your session. Loop at most 2–3
rounds, then stop even if not fully converged.

That is the entire localhost method — pure skill, nothing to run but the peer's own CLI. Reach for
**mode B (the `xreview` binary)** only for what a smart agent genuinely can't do by hand: **auto-trigger**
on session-end (a Stop hook, `xreview install`), **cross-machine / CI / server** review, the
**API/Bedrock** transports (review from a box that lacks the peer CLI), machine-checkable **records**, or
**screenshot/vision** payloads for rendered-UI review.

> **Want it as a named agent?** The same method is packaged as a thin **`cross-agent-reviewer` agent**
> definition per platform (Claude subagent, Kiro agent JSON, Codex `AGENTS.md`, agy) — see
> [`references/agent-definitions.md`](references/agent-definitions.md) (installable Claude copy at
> `assets/agents/cross-agent-reviewer.claude.md`). Each is just a pointer to this Localhost method with the
> host/peer families swapped — no new logic, no script.
>
> **Is it actually good?** This method is evaluated (eval-harness / EDD) — see
> [`references/eval.md`](references/eval.md): pass@1 3/3 on seeded bugs (arithmetic, command-injection,
> and a clean-diff false-positive guard), both directions. Re-run it after changing the method or when a
> peer CLI version bumps.

## When to reach for which command

| Goal | Command |
|------|---------|
| Review the current changes once, now | `xreview review --host-agent <agent>` |
| Auto-review when the author agent finishes | `xreview install --agent <claude\|codex\|opencode\|kiro\|antigravity>` |
| Remove the auto-review trigger | `xreview uninstall --agent <claude\|codex\|opencode\|kiro\|antigravity>` |
| Change which model/agent reviews | edit the config (below), no reinstall needed |
| Refresh which SOTA models are available | `xreview cards update` |

> **Which `--agent`?** Use the agent **you are running as right now** — that's the *author* whose
> work gets reviewed by a different family. If you're Claude, `--agent claude`; if Codex,
> `--agent codex`; and so on for `opencode` / `kiro` / `antigravity`. All five have working
> trigger installers.

## Resolve the binary (platform-agnostic)

Always pick the binary matching the host OS/arch — never hard-code a path:

```sh
# scripts/xreview-bin.sh prints the right binary path for this machine
BIN="$(sh "$(dirname "$0")/scripts/xreview-bin.sh")"
```

Binaries live in `scripts/xreview-<os>-<arch>` (linux/darwin/windows × amd64/arm64), pure Go, no
runtime dependency. A published skill ships them prebuilt. If `"$BIN"` doesn't exist (fresh checkout),
populate them once from the Go source:

```sh
sh "$(dirname "$0")/scripts/build-binaries.sh" /path/to/go-review-service   # runs make build-all-xreview
```

**Maintainer refresh (one command):** `scripts/publish.sh` rebuilds the six binaries and copies this
skill into the local agent skill homes (`~/.claude`, `~/.kiro`, `~/.config/opencode`, `~/.codex`,
`~/.gemini`, `~/.gemini/antigravity`, `~/.copilot`), then verifies each copy resolves an executable
binary. Run after any binary/behavior change. Overrides: `XREVIEW_GO_DIR`, `XREVIEW_SKILL_HOMES`, `XREVIEW_NO_BUILD=1`.

**Live transport smoke (opt-in, host-bound):** `go test -tags live -run TestLiveSmoke -timeout 15m
./internal/xreview/run/` drives present-backend transports against a real review, asserting each is
self-describing + fast (never a silent hang). Gated by the `live` tag (NOT default lanes), self-skips
absent backends; run it when an agent CLI/server API may have changed. [CR-2026-07-03-039]

**Vendored consumers — fetch-on-install instead of committing binaries.** A downstream repo
**gitignores** the binary and fetches it (verified artifact) rather than committing all six (~300 MB).
**Tool-parameterized** (`xreview`/`review-cli`/arch-less `embedding-runner`/`uatdemo`) + **auth-aware**:
`emit-bundle-manifest.sh <tool> <dir>` → platforms-shape `<tool>-bundle-manifest.json`;
`install-bundle.sh <source> <dest> [tool]` fetches only the host's artifact + verifies **SHA-256**
(fail-closed) — `<source>` = http(s) URL (Bearer `$GH_TOKEN` for github.com), local dir, or
**`gh://OWNER/REPO@TAG`** (`gh` auth → **private** assets, no in-repo token); `publish-release.sh <tag>
[--tool N] [--from <dir>] --repo <r> --create` stages the full 6-set (partial rejected) + manifest +
`SHA256SUMS`; `verify-bundle.sh <tool> <dir>` round-trips it (emit → install → assert bytes==source sha).
The code-review release (`release_code_review_bundle.py`) emits the platforms-shape manifest via the same
emitter. Two manifest shapes (bundle-tree `release-manifest.json` vs platforms-shape) & why both stay:
[references/manifest-shapes.md](references/manifest-shapes.md). [CR-2026-07-03-016/017/020, 07-04-071/072/073]

## One-off review

Run an independent cross-family review of the current git working-tree changes:

```sh
"$BIN" review --host-agent claude
```

What happens: fingerprint the changed files → skip if this exact scope was already reviewed →
select a **different-family** reviewer via the model-card registry (Claude author → Codex, etc.)
→ dispatch it headlessly to run the `code-review` skill → run the consensus loop → write a
review-record. The result is advisory (visible, non-blocking) unless `on_findings: blocking` is set.

**Machine-readable output + multi-turn (session id).** `--format json` returns the full review
record as one JSON object on stdout (outcome, reviewer, findings, degrade_codes, remediation, and
`session`), so a host agent can parse it and **continue the review conversation in a later turn**:

```sh
"$BIN" run --host-agent codex --format json    # → {"outcome":…,"session":{"id":…,"provider":"acp:kiro","resume":…}}
```

`record.session.id` is the reviewer transport's session id. Three transports expose a real, resumable
one today: **ACP/kiro** (`session/load`), **codex exec** (its `--json` `thread_id`), and **opencode exec**
(its `run --format json` `sessionID` — declare `transport:"exec"` with a provider-prefixed model like
`opencode-go/glm-5.2`). **Continue the review conversation in a later turn** by passing it back:

```sh
"$BIN" run --host-agent codex --resume <session-id> --format json   # reviewer continues the SAME session over the revised scope
```

`--resume` re-enters the prior reviewer session so it keeps full context across turns — Kiro via ACP
`session/load`, codex via `codex exec resume <id>`, opencode via `opencode run --session <id>` (best-effort
for ACP: if the session can't be loaded it falls back to a fresh review). Within one run, EVERY stateful
transport chains its re-review rounds through the same session — codex/opencode exec, ACP/kiro, and the
opencode server (best-effort; a lost/locked session falls back to fresh). Resume is a no-op for the stateless
API transport. (The underlying agents also expose their own resume: `codex exec resume <id>`, `kiro-cli chat
--resume`, `opencode run --session <id>`, `claude --resume <id>`.)
[CR-2026-07-03-024/025/026/029/036]

## Auto-trigger when the author agent finishes

Each agent exposes a different "finished a turn / session" mechanism; `xreview install --agent <name>`
writes the right one for you. Every installer **merges** (never clobbers), is **idempotent**, backs up
the prior file, removes only its own entry on `uninstall`, and writes the resolved local binary path
(so it works on any OS/arch). Idempotency/uninstall match the `run --host-agent` invocation signature,
so a renamed/relocated binary is still recognized.

```sh
"$BIN" install --agent claude       # → Stop hook in ~/.claude/settings.json
"$BIN" install --agent codex        # → Stop hook in ~/.codex/hooks.json (CODEX_HOME-aware)
"$BIN" install --agent opencode     # → session.idle JS plugin in ~/.config/opencode/plugins/xreview.js
"$BIN" install --agent kiro         # → hooks.stop in a kiro-cli agent config (see note)
"$BIN" install --agent antigravity  # → agy plugin (plugin.json + root hooks.json Stop), via `agy plugin install`
```

All five author agents are covered. Every installer **merges/writes** without clobbering, is idempotent,
removes only its own entry on `uninstall`, and embeds the resolved local binary path.

> **opencode plugin source of record.** The activated `~/.config/opencode/plugins/xreview.js` is
> written by `install --agent opencode` with the local binary path baked in (machine-specific — not
> committed). Its canonical, portable source lives in this skill at
> [`scripts/xreview.plugin.js`](scripts/xreview.plugin.js): same `session.idle` logic, but it
> resolves `xreview-<os>-<arch>` at **runtime** (honoring an `XREVIEW_BIN` override, else the
> canonical `~/.config/opencode/skills/cross-agent-review/scripts/` home) and no-ops if no binary
> resolves. Prefer `install --agent opencode` to activate; the template is for reading/auditing the
> hook, or hand-copying into `~/.config/opencode/plugins/` on a machine where the resolved path is
> the global skill home.

| Agent | Trigger surface | Event | Maturity |
|-------|-----------------|-------|----------|
| **claude** | `~/.claude/settings.json` (deep-merge) | `Stop` | ✅ verified (live) |
| **codex** | `~/.codex/hooks.json` — identical schema to Claude | `Stop` | ✅ **runtime-fire live-proven** (after a one-time interactive `/hooks` trust — a codex safety gate) |
| **opencode** | JS plugin `~/.config/opencode/plugins/xreview.js`, Bun `$` | `session.idle` | ✅ plugin loads + fires correctly (validated under Bun + `opencode models`); live agent-session fire is host-bound |
| **kiro** | a **kiro-cli agent config** (`~/.kiro/agents/<name>.json`), `hooks.stop` | `stop` | ✅ installer validated via `kiro-cli agent validate`; per-agent (see note) |
| **antigravity (agy)** | an **agy plugin** (`plugin.json` + root `hooks.json`), registered via `agy plugin install` | `Stop` | ✅ **shipped** — end-to-end validated: `agy plugin install` accepts it (`components: [hooks]`), `uninstall` removes it; live session-end fire is host-bound. (agy's trigger surface is the plugin system, NOT its flat `settings.json`.) |

> **Kiro is per-agent, not global.** Unlike Claude/Codex (one global hook file for all sessions), kiro
> hooks live inside a specific agent's config. `install --agent kiro` defaults to a dedicated agent
> `~/.kiro/agents/xreview.json` (activate with `kiro-cli chat --agent xreview`, or
> `kiro-cli agent set-default xreview`). To trigger on the agent you already use, merge the stop-hook
> into it instead: `install --agent kiro --settings ~/.kiro/agents/<your-agent>.json`. The kiro event
> set is `agentSpawn|userPromptSubmit|preToolUse|postToolUse|stop`; xreview uses `stop`
> ("runs when the assistant finishes responding").
>
> The installer never silently claims an unverified trigger — see `references/capability-tiers.md`.

## Configuration (switch the reviewer without code changes)

Pass `--config <file.json>` (schema: `references/config.schema.notes.md`). Common cases:

```jsonc
// Use Codex gpt-5.5 at max effort as the reviewer for a Claude author (this is also the default)
{ "version": 1, "backends": [{ "name": "codex", "model": "gpt-5.5", "effort": "xhigh" }] }

// Turn the consensus loop OFF → one review + one revision only
{ "version": 1, "consensus": { "enabled": false } }

// Block the session until findings are addressed (default is non-blocking advisory)
{ "version": 1, "on_findings": "blocking" }
```

The reviewer is **always** a different family than the author (decided via the model-card
registry, at the model level — not the CLI name). If only a same-family model is available it
degrades honestly (`same-family-degraded`), never a silent self-review.

**Default pairing & fallback** (maintainer preference, in `config` + `model-cards.json`):

- **Primary — Claude ↔ Codex mutual.** A Claude Code (Anthropic) author is reviewed by
  **codex (GPT/OpenAI)**, and a Codex author is reviewed by **Claude (Anthropic)** — the two
  strongest families, each independent of the other, both live-proven.
- **Fallback — opencode Zen (cost-efficient, open-source):** `opencode/glm-5.2` (Zhipu),
  `opencode/kimi-k2.7-code` (Moonshot, code-review-focused), `opencode/kimi-k2.6`. Used when the
  primary counterpart is unavailable; distinct families, so they stay valid reviewers for a
  Claude or Codex author. Then kiro / antigravity.

**This preference lives in config FILES, not hardcoded.** The shipped **template**
(`scripts/config.template.json` + `scripts/model-cards.json`, next to the binary) is the
default — auto-loaded when no per-repo config exists. To customise per repo without
committing keys:

```sh
"$BIN" init          # seeds ./.xreview/{config.json,model-cards.json} from the templates
                     # and adds .xreview/ to .gitignore (real config is never committed)
# edit ./.xreview/config.json (pairing.primary, fallback_order) — it overrides the template
```

Resolution order (each of config / model-cards): `--config`/`--cards` flag →
`<repo>/.xreview/…` (real, gitignored) → shipped template beside the binary → a generic
built-in baseline. Reviewer **keys stay in the environment**, never in these files.

### Reviewer policy — prohibitions & cost (config-driven, org-specific)

Two config knobs express an org's reviewer policy without hardcoding anything:

- **`deny_backends`** — a **compliance gate**: backends this repo/org *prohibits* as a reviewer.
  A denied backend is **never** selected even if its card is Available (distinct degrade
  `reviewer-denied-by-policy`). Example — Giant forbids opencode + codex:
  `"deny_backends": ["opencode", "codex"]`. Personal repos leave it empty.
- **`prefer_cost`** + card **`cost_tier`** (0 = subscription/already-paid: kiro-ACP,
  opencode-Go, codex-OAuth · 1 = self-paid metered e.g. Gemini · 2 = premium metered e.g.
  Anthropic API). With `prefer_cost: true`, the **cheapest** eligible different-family reviewer
  wins (ties by tier) — a subscription route beats a metered API even at a higher tier. Default
  (false): pairing/fallback order wins and cost only steers the automatic sweep.
- **`prefer_subscription`** — a **route preference within a family**: when `true`, the KEYLESS
  subscription/credential route is used **instead of a metered provider API key even when the key
  is set** — anthropic → **AWS Bedrock** (never `ANTHROPIC_API_KEY`); openai/google → the OAuth
  **exec** CLI (`exec:codex` / `agy`, never `OPENAI_API_KEY` / `GEMINI_API_KEY`). If no
  subscription route is available it degrades honestly (not-serviceable) rather than silently
  falling back to the key — so the preference is *enforced*, not advisory. Default (false): a
  present API key wins, then the subscription route. Orthogonal to `prefer_cost` (which ranks
  *across* families by tier); use `prefer_subscription` to guarantee "never bill my metered key".
  [CR-2026-07-04-059]

**Kiro as a subscription reviewer (ACP).** `kiro-cli acp` drives Kiro's Anthropic models
(`claude-opus-4.5`) on the **subscription** (no API key, provider `acp:kiro`) — a legitimate,
vision-capable Anthropic reviewer for **non-Anthropic authors** (the Claude Code CLI stays
ToS-excluded). Just have a logged-in `kiro-cli` on PATH.

### Frontend visual review (modality-aware routing)

Reviewing frontend **code** (JSX/TSX/CSS/logic/a11y) is a text task — a text-only model
(GLM-5.2, GLM/Kimi-K2.7-code) does it well and cheaply. Reviewing **rendered visuals**
(does the UI match the design; layout, hierarchy, contrast) needs a model that can *see
images*. Each model card declares `"modalities": ["text"]` or `["text","vision"]`
(vision: claude, codex, gemini, **kimi-k2.6**; text-only: glm-5.2, kimi-k2.7-code, deepseek).

With `visual_review: "auto"` (default), when the scope touches rendered-UI files
(`.tsx/.jsx/.vue/.svelte/.css/.html`, image assets) xreview **prefers a vision-capable
different-family reviewer**. If only a text-only reviewer is available, the code is still
reviewed but the record is honestly flagged **`visual-fidelity-not-reviewed`** (advisory,
never a silent false-green). `xreview doctor` shows whether the selected reviewer is
`vision-capable` or `text-only`. Set `visual_review: "off"` for pure code review.

**Screenshots are actually sent to the reviewer** (CR-2026-07-03-008/018). Over the direct-API
transport *and* the Kiro ACP transport, when a visual scope is routed to a vision reviewer
xreview attaches rendered-UI images to the payload (API image parts / ACP image content
blocks) so it inspects the *rendered* UI, not just the diff text:

- **In-scope image assets** (`.png/.jpg/.jpeg/.webp/.gif` — VRT baselines, design mockups,
  committed screenshots) are always attached automatically.
- **External screenshot dirs** — point `visual_artifacts` (config globs, e.g.
  `["playwright-report/*.png", ".vrt/*/*.png"]`) at where **`frontend-designer`** /
  `webapp-testing` write their Playwright/VRT captures; matching images are attached too.
- **Auto-capture before review** — set `visual_capture.command` (argv, no shell) to a
  screenshot tool (`["npx","playwright","test"]`) and xreview runs it in the repo root
  *before* collecting, so fresh renders exist to attach. Bounded by `visual_capture.timeout_seconds`
  (default 120, also capped by `dispatch_seconds`); a failure is recorded (`visual-capture-failed`)
  but never fails the review. Only runs on a visual scope routed to a vision reviewer. [CR-2026-07-03-009]

Payload is bounded (≤6 images, ≤4 MiB each, ≤12 MiB total). The record proves what happened:
**`visual-artifacts-reviewed:N`** when N images were sent; **`visual-artifacts-unavailable`**
when a vision reviewer was selected but no screenshot existed to attach (code reviewed,
visuals not — honest, distinct from the text-only case). SVG is treated as text (it is), not
attached as an image.

> The rendered-UI *judgement* (which screenshots to capture, design-system fidelity) is the
> **`frontend-designer`** skill's domain; xreview's job is to route to a model that can see
> images and to actually put those images in front of it.

## Reviewer transport & keys (preferred: direct API)

The reviewer is driven over one of two transports, chosen automatically:

1. **Direct LLM-API** (preferred — reliable, no subprocess to hang): used when a key
   resolves for the reviewer's family. Preference order:
   - a **real direct provider key**: `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` /
     `GEMINI_API_KEY` / `DEEPSEEK_API_KEY` (more expensive, preferred);
   - for the **anthropic family with NO `ANTHROPIC_API_KEY`: AWS Bedrock** — serves Claude on the
     **ambient AWS credential** (`~/.aws` / env / SSO / IAM role; provider `bedrock-anthropic`), so a
     non-anthropic author gets a **Claude reviewer with no API key** — a legitimate route, NOT the
     ToS-excluded Claude Code CLI. The model is a Bedrock **inference-profile** id (bare `claude-…` →
     `us.anthropic.claude-…`; `us.`/`global.`/`arn:` pass through). `AWS_REGION` is auto-pinned to the
     profile's geo (`us.`→us-east-1), so a `us.` profile works from any region. [CR-058/070]
   - then **opencode Go/Zen** — a portable subscription key over an OpenAI-compatible gateway
     (final fallback). **Go** (subscription, `…/zen/go/v1`, the default) and **Zen** (metered,
     `…/zen/v1`) are separate endpoints on the same key; models are **bare ids** (`glm-5.2`,
     `kimi-k2.6`, `kimi-k2.7-code`). Set `OPENCODE_API_KEY` (endpoint override `OPENCODE_ZEN_BASE_URL`),
     **or** set nothing and xreview reuses the opencode CLI's stored credential
     (`~/.local/share/opencode/auth.json`, provider `opencode-go-local`). [CR-2026-07-03-010/011]
2. **exec** (the agent CLI): only for OAuth-friendly, clean-exit CLIs — chiefly **codex**.

Two further transports are **declared** per backend (`transport:"server"` / `"acp"`), not auto-chosen:
- **server** — skill-based review over a managed server (`opencode serve` today), resolved by **backend
  identity** from a registry; a backend declaring `transport:"server"` with no registered runtime **fails
  closed** (`server-runtime-unavailable:<backend>`) rather than being silently served by opencode. [CR-031]
- **acp** — Agent Client Protocol (`kiro-cli acp` today), a subscription-driven programmatic surface.

Compliance notes baked into selection:
- **Kiro** and **Antigravity (agy)** are AWS/GCP-OAuth-bound (no portable API key); their
  families are served via a real key (e.g. google→Gemini API) or opencode Zen, not their CLIs.
- The **Claude Code** subscription CLI is **not** driven as an automated reviewer (ToS), but a keyless
  **Anthropic-family reviewer** still has two routes: **AWS Bedrock** (`bedrock-anthropic`, on `~/.aws`)
  or **Kiro ACP** (`acp:kiro`). `ANTHROPIC_API_KEY` also works but isn't required. (Claude as your own
  author session is always fine.)

Set the key(s) in the environment before the trigger fires. Records show which was used
via `reviewer.provider` (e.g. `gemini-api`, `opencode-zen`, `exec:codex`).

### Known-good quick-start (cost-efficient first)

Prefer **subscription** routes over metered API keys — set `"prefer_subscription": true` in the
config to *enforce* that (never bill a metered key even if one is set; see reviewer policy above).
Cheapest first:

**1. opencode Zen/Go (recommended — most cost-efficient, any family).** A single API-key
subscription serves SOTA open-source models (e.g. **GLM-5.2**) over an OpenAI-compatible
gateway, and works as a reviewer for *any* author family — easier to wire into a workflow
than an OAuth2 subscription.

```sh
export OPENCODE_API_KEY=…          # opencode Zen subscription; optional OPENCODE_ZEN_BASE_URL
"$BIN" run --host-agent claude --cwd "$PWD"   # any author → different family via Zen
```

**2. codex OAuth (ChatGPT family, no per-token cost).** A legitimately free OAuth login;
codex runs as the reviewer over the exec transport — **live-proven** (`claude` author →
`codex (openai)` reviewer → `consensus-reached`). Just have an authenticated `codex` on PATH.

```sh
"$BIN" run --host-agent claude --cwd "$PWD"   # → reviewer.provider = exec:codex
```

**3. AWS Bedrock — keyless Anthropic reviewer (for a non-Anthropic author).** If `~/.aws`
credentials are present, a Codex/other-family author is reviewed by **Claude with no API key**
(provider `bedrock-anthropic`). Nothing to export beyond the standard AWS credential chain
(optionally `AWS_REGION`). Live-proven: `codex` author → `claude` (Bedrock) reviewer.

```sh
"$BIN" run --host-agent codex --cwd "$PWD"   # → reviewer.provider = bedrock-anthropic (no ANTHROPIC_API_KEY)
```

**4. Direct provider API keys (higher cost — use when you need a specific model).**
`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` / `DEEPSEEK_API_KEY`.

> Author-side note: **Claude Code** covers the Anthropic family for your *authoring* session but
> cannot act as an *automated reviewer* (Claude Code CLI is ToS-excluded). An Anthropic-family
> *reviewer* has three keyless/low-friction routes: **AWS Bedrock** (`~/.aws` credential, no
> key), **Kiro ACP** (`kiro-cli acp`, subscription), or opencode Zen — plus `ANTHROPIC_API_KEY`
> if you have one.

Verify a route is live before wiring the hook with the non-dispatching preflight:

```sh
"$BIN" doctor --host-agent <you>
# READY — claude (anthropic) author → codex (openai) reviewer via exec:codex
# NOT READY — backend-unavailable
#   → to enable a cross-family reviewer: … set GEMINI_API_KEY …; or set OPENCODE_API_KEY …
```

`doctor` runs the exact selection + availability logic the hook uses, but dispatches
nothing — so a READY result means the gate will actually fire, and a NOT READY result
names the minimal credential/route to set.

**`--probe` (live invokability check).** Plain `doctor` is offline: for an API/Bedrock reviewer
it reports READY on **credential existence**, which cannot tell whether the carded model is
actually invokable (e.g. a Bedrock inference-profile the account lacks access to still resolves a
credential). `doctor --probe` does **one bounded PING** to the resolved reviewer and only reports
READY if it truly answers — otherwise `NOT READY — provider-model-unavailable` with the real
provider error. Use it in CI / before wiring a hook to a newly-carded model; it costs one token,
so it is opt-in (default `doctor` stays free). A probed-OK run appends `[live-probed: reviewer
invokable]`. [CR-2026-07-04-060]

```sh
"$BIN" doctor --host-agent codex --probe
# READY — codex (openai) author → claude (anthropic) reviewer via api:bedrock-anthropic … [live-probed: reviewer invokable]
```

### Self-explaining degradation

When a run degrades for a credential/availability reason, `xreview` prints to **stderr** the
minimal route that would enable a real cross-family reviewer for the family it selected — e.g.
`to enable a cross-family reviewer for the google family: set GEMINI_API_KEY …; or set
OPENCODE_API_KEY …`. The same hint is persisted on the record as `remediation`. This tells you
*which* key to set, distinct from a generic "tool unavailable".

## SOTA model-card registry

`scripts/model-cards.json` lists which models each backend offers, their family, SOTA tier, and
availability. It drives different-family selection and picks the best available reviewer. Refresh
it as models change:

```sh
"$BIN" cards update    # probes installed CLIs; stale registry warns, never hard-fails
```

Edit `scripts/model-cards.json` to add/adjust models. Keep `family` accurate — independence
depends on it.

## Outcomes (all distinct, all honest)

`consensus-reached` · `max-rounds-exhausted` · `single-round` · `skipped-already-reviewed` ·
`skipped-empty-scope` · `skipped-reentrant` · `same-family-degraded` · `backend-unavailable` ·
`dispatch-timeout` · `reviewer-unavailable-midloop`. Every run resolves to exactly one; none block the host session. Records at `~/.xreview/records/<repo-id>.jsonl`.

## What this skill does NOT do

It does not review code itself (it dispatches the `code-review` skill to another agent), does not manage
model credentials (each backend uses its own auth), and does not guarantee a same-machine reviewer for
every backend (capability tiers).
