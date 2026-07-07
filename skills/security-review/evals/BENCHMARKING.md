# Security-review local benchmarking

This benchmark runner keeps the current storage policy unchanged:

1. `--benchmark-root` when explicitly provided.
2. `<workspace>/docs/review/security-review/<timestamp>` when the current workspace has a `docs/` directory.
3. `<workspace>/temp/security-review/<timestamp>` when the current workspace has a `temp/` directory but no `docs/` directory.
4. `~/temp/security-review/<timestamp>` as the fallback.

## Provenance hardening

Each benchmark root stores a single `benchmark_context.json`.

- Reusing an existing benchmark root is allowed when the stored provenance matches the requested provenance.
- The runner now fails fast when the existing context is incompatible.
- At minimum, compatibility checks cover `skill_name`, `skill_source_path`, `benchmark_root_source`, and `workspace_root` when present.
- Matching provenance preserves the existing `benchmark_context.json`, which allows `with_skill` and `without_skill` runs to share the same benchmark root safely.

## Installed skill directory is not a benchmark root

The runner now rejects any explicit or resolved benchmark root that points inside the installed skill directory.
Mutable benchmark state must live in the explicit root, workspace docs/temp root, or `~/temp` fallback — never under the installed skill copy.

## Legacy in-skill benchmark tree

`evals/benchmarks/validation-batch5` is **legacy** and **non-canonical**.

- Keep it only as an archived reference marker.
- Do not write new benchmark state there.
- Use the current benchmark-root policy above for all new runs.

## Benchmark catalog

The runner reads `evals/evals.json` and copies the listed fixture files into:

```text
<benchmark-root>/runs/eval-<id>/inputs/
```

It also writes:

```text
<benchmark-root>/runs/eval-<id>/eval_metadata.json
<benchmark-root>/runs/eval-<id>/<with_skill|without_skill>/run-<n>/
```

## Example

```bash
python3 scripts/run_security_benchmark.py --eval-id 1 --config with_skill
python3 scripts/run_security_benchmark.py --eval-id 1 --config without_skill --benchmark-root /tmp/security-review-shared
```
