# xreview config (`--config <file.json>`)

Full JSON Schema: `go-review-service`'s spec at
`.agents/specs/cross-agent-review-orchestration/contract/xreview-config.schema.json`.
Every field has a documented default; omit what you don't need.

| Field | Default | Meaning |
|-------|---------|---------|
| `version` | `1` | schema version (required) |
| `backends[]` | — | per-backend overrides: `{name, cli_path?, model?, effort?, extra_args?}`. `name` ∈ {claude, codex, kiro, opencode, antigravity}; unknown → fail closed |
| `pairing.primary` | `["claude","codex"]` | primary mutual cross-review pair |
| `fallback_order` | `["kiro","opencode","antigravity"]` | tried when the primary counterpart is unavailable |
| `consensus.enabled` | `true` | run the review↔revise loop; `false` ⇒ one review + one revision |
| `consensus.single_round` | `false` | same effect as `enabled:false` |
| `consensus.max_rounds` | `4` | hard cap; hitting it ⇒ `max-rounds-exhausted` (no infinite loop) |
| `on_findings` | `"advisory"` | `advisory` = visible, non-blocking; `blocking` = block session stop until addressed |
| `timeouts.dispatch_seconds` | `900` | per backend invocation; exceeding ⇒ `dispatch-timeout` |

Selection is always **different-family** (via the model-card registry); it never silently
picks the author's own family.
