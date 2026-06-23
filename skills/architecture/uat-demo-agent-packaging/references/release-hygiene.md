# Release Hygiene

This reference defines the current bounded release/binary hygiene contract for `uat-demo-agent`.

## Binary Refresh Triggers

Refresh bundled multi-arch binaries when any of the following is true:

1. you are publishing a new `uat-demo-agent` release bundle through `scripts/release_uatdemo_skill_bundle.py`
2. the managed wrapper or bundled platform binaries changed
3. dist manifest / checksum metadata needs regeneration from current binaries

## Dirty Working Tree Boundary

1. dirty working tree releases are still allowed for bounded local publish/install workflows
2. dirty working tree releases are **not** eligible for signing-ready promotion
3. the authoritative effect is encoded in release metadata as `promotion_gate.reason = dirty-working-tree-build`

## Publisher Coupling

1. shared publisher uses the delegated `uat-demo-agent` release lane
2. that delegated lane rebuilds and syncs managed binaries back into `.agents/skills/uat-demo-agent/scripts/*` unless the release script is run with `--no-sync`
3. shared publisher `--skip-binary-refresh` is the productized operator mode that forwards the declared no-sync release args
4. therefore publisher-driven delegated release refreshes managed binaries by default, but can intentionally publish/install from the latest verified bundle without workspace sync-back

## Non-Claims

1. this contract does not upgrade `dirty-working-tree-build` into a signing-safe posture
2. this contract does not remove the need for preflight verification
3. this contract does not imply package-manager or signed-release automation
4. this contract does not claim that `--skip-binary-refresh` makes a stale workspace source bundle equivalent to a newly refreshed source tree
