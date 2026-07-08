# cross-agent-review `scripts/` — map

Two families live here: the **xreview binary + publishing** (server-side mode B) and the
**download-on-install bundle chain** with its **eval-harness** (grew across CR-071…075). This
file is the index so the growing set stays legible.

## Binary + publishing (mode B)

| Script | Does |
|---|---|
| `build-binaries.sh <go-dir>` | build the 6 `xreview-<os>-<arch>` binaries from Go source + emit `xreview-bundle-manifest.json` |
| `publish.sh` | rebuild + copy this skill into the 9 agent skill homes under flat `cross-agent-review` by default; verify each resolves a binary (`XREVIEW_SKILL_REL` overrides the relative destination, `XREVIEW_NO_BUILD=1` skips the rebuild) |
| `xreview-bin.sh` | resolve the host's `xreview` binary path |

## Download-on-install bundle chain (producer → fetch)

| Script | Does |
|---|---|
| `emit-bundle-manifest.sh <tool> <dir>` | emit the platforms-shape `<tool>-bundle-manifest.json` (single source of truth for the shape) |
| `publish-release.sh <tag> [--tool N] [--from D] --repo R --create` | stage the full platform set + manifest + `SHA256SUMS` and cut a `gh release` |
| `install-bundle.sh <source> <dest> [tool]` | fetch ONLY the host's artifact + SHA-256-verify it; `<source>` = http(s) URL / local dir / `gh://OWNER/REPO@TAG` (private assets via `gh` auth) |
| `verify-bundle.sh <tool> <dir>` | positive round-trip self-test: emit → install → assert installed bytes == source sha |
| `test-bundle-chain.sh <tool> <dir>` | positive round-trip **+ negative** tamper case: `install-bundle.sh` must REJECT a corrupted artifact |

The two manifest shapes (bundle-tree `release-manifest.json` vs platforms-shape
`<tool>-bundle-manifest.json`) and why both stay: [`../references/manifest-shapes.md`](../references/manifest-shapes.md).

## Eval-harness + pre-merge gate

| Script | Does |
|---|---|
| `eval-cap8-security.sh [--peer N] [--case C]` | CAP-8 adversarial-security **matrix**: 3 seeded defect classes (leak-traversal, command-injection, fail-open) each graded by a model-grader, **+ a `clean` false-positive guard** (must not cry wolf). Exit 0 all-pass / 1 fail / 77 skip-loud |
| `pre-merge-dogfood.sh [--base R] [--advisory] [--allow-degraded] [--quick]` | the runnable **gate**: CAP-8 matrix + a peer diff-review with a strict BLOCK/ALLOW model-verdict; fail-closed on an unavailable checker. `--quick` = diff-review only (fast) |
| `install-pre-push-hook.sh [--enforce] [--full] [--uninstall]` | wire `pre-merge-dogfood.sh` in as a git `pre-push` hook (default: fast + non-blocking `--quick --advisory`) |

Capability table + reproduction + grader notes: [`../references/eval.md`](../references/eval.md).
All scripts are POSIX `sh` and shellcheck-clean.
