# Cross-agent-reviewer as a named AGENT (per platform)

The Localhost method in `SKILL.md` turns *any* host agent into the reviewer-orchestrator. If you want it
as a **named, discoverable agent** — "a code-review agent that calls a different coding agent's CLI" —
each platform has a thin agent definition whose body is that same method. There is no new logic and no
script: the agent just follows the skill and drives a **different-family** peer's CLI.

The one rule every version must keep: **the reviewer peer is a DIFFERENT model family than the host the
agent runs under** (claude/kiro = anthropic · codex = openai · opencode = open models · antigravity =
google). An agent running under Claude drives codex; under Codex drives claude; etc. Never a same-family
self-review.

## Claude — `.claude/agents/cross-agent-reviewer.md` (project) or `~/.claude/agents/` (global)

A ready-to-install copy is bundled at **`assets/agents/cross-agent-reviewer.claude.md`** — install it with:

```sh
cp assets/agents/cross-agent-reviewer.claude.md ~/.claude/agents/cross-agent-reviewer.md   # global
# or into a repo's .claude/agents/ for project scope
```

Markdown with frontmatter (`name`, `description`, `tools: Bash, Read, Grep`) + the Localhost method as the
system prompt. Invoke it as a subagent — it drives **codex exec** since it runs under Claude.

## Kiro — `~/.kiro/agents/cross-agent-reviewer.json` (global) or `.kiro/agents/` (project)

Kiro agents are JSON with a `prompt` field. Its peer must be a *non-anthropic* family (codex/opencode):

```json
{
  "name": "cross-agent-reviewer",
  "description": "Independent code review by a DIFFERENT model family — drives a peer coding agent's CLI (codex/opencode) over the current git diff.",
  "prompt": "You are the cross-agent code reviewer. You run under Kiro (anthropic), so your reviewer peer MUST be a different family — primary codex (openai), else opencode. Method: (1) git diff; if empty, stop. (2) Drive the peer headlessly with the diff EMBEDDED: codex exec \"You are an INDEPENDENT reviewer from a different model family. Review ONLY the diff for correctness, security, and clear quality bugs; list '- file:line — issue', most severe first; if nothing material say 'no material findings'. $(git diff)\". (3) Return the peer's findings, advisory. (4) Re-review via the peer's native resume (codex resume --last). Never present a same-family review as independent.",
  "tools": ["shell", "read", "grep"],
  "model": null
}
```

Activate with `kiro-cli chat --agent cross-agent-reviewer`.

## Codex

Codex has no per-agent subagent file; it reads `AGENTS.md` for standing instructions. Add a short section
there: *"To cross-review, drive a different-family peer (claude/opencode) over `git diff`: `claude -p "…$(git diff)"`.
You run under Codex (openai) so the peer must NOT be openai."* The reviewer peer for a Codex host is
**claude** (`claude -p`) primary, else opencode.

## Antigravity (agy)

Drive it the same way from an agy workflow/plugin: on review, run a different-family peer over the diff
(agy is google, so peer = claude/codex/opencode). agy's plugin/hook surface (see the main SKILL.md and
`references/capability-tiers.md`) can invoke the peer CLI; the body is identical to the Claude version
with the host/peer families swapped.

## Why thin

All four are the *same* skill method with the host/peer families swapped — no re-implementation, no
binary, no script. Keeping them thin (a pointer to the Localhost method, not a fork of it) is what stops
them drifting apart. For anything a local peer CLI can't do (cross-machine, CI, API/Bedrock, records,
vision), the agent should defer to the `xreview` binary (mode B).
