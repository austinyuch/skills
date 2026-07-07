# Two manifest shapes — decision & boundary

The native-binary release surfaces in this repo carry **two intentionally-different manifest
shapes**. They are **not** redundant; keeping both is the decision (CR-2026-07-04-073). This doc is
the single place that states which is which, so the duplication does not read as accidental drift.

## A. Bundle-tree manifest — `release-manifest.json` + `checksums.txt`

- **Producer:** `scripts/release_code_review_bundle.py` (the code-review skill release).
- **Question it answers:** *"Is this whole skill bundle intact and correctly built?"*
- **Shape:** every file in the assembled skill tree, plus `verification` metadata (wrapper smoke,
  tree-sitter capability, Zig toolchain version, executable-bit policy, forbidden-runtime checks).
  `checksums.txt` is a flat `<sha256>  <relpath>` list over the same tree.
- **Consumer:** the release/verify pipeline itself and `verify_code_review_consolidation.py` —
  a *maintainer-side integrity* audit of the published skill, not a per-platform fetch index.

## B. Platforms-shape manifest — `<tool>-bundle-manifest.json`

- **Producer:** `cross-agent-review/scripts/emit-bundle-manifest.sh <tool> <dir>` (the single
  canonical emitter). As of CR-073 the code-review release **also** emits this, by shelling out to
  the same emitter, so a download-on-install consumer never has to hand-roll it.
- **Question it answers:** *"For tool `<tool>`, which single artifact does host `<os>-<arch>` need,
  and what is its sha256?"*
- **Shape:** `{ "tool", "version", "platforms": { "<file>": {"sha256","bytes"}, … } }` — one entry
  per platform artifact (or a single bare `<tool>` entry for an arch-less tool like
  `embedding-runner`). No bundle-tree, no build metadata.
- **Consumer:** `install-bundle.sh` — a *downstream vendored repo* fetching only its host's binary
  from a (public or private) release and SHA-verifying it, instead of git-LFS-committing all six.

## Why not converge them

They answer different questions for different audiences:

| | A. bundle-tree | B. platforms-shape |
|---|---|---|
| Scope | every file in one skill | per-tool platform artifacts |
| Audience | release/verify pipeline (maintainer integrity) | download-on-install consumer (fetch index) |
| Keys | file relpaths + build verification | `<os>-<arch>` artifact → sha256/bytes |
| Emitter | `release_code_review_bundle.py` | `emit-bundle-manifest.sh` (one source of truth) |

Collapsing B into A would force every consumer to parse a large bundle-tree manifest (with build
metadata it does not need) just to find one binary's sha; collapsing A into B would drop the
build-integrity verification the release gate depends on. So: **both stay, one emitter each, and the
code-review release emits BOTH** (`release-manifest.json` for its own gate + `<tool>-bundle-manifest.json`
for consumers). The round-trip of shape B is guarded by `verify-bundle.sh` (emit → install → sha).
