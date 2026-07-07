# Legacy benchmark archive marker

This directory is a **legacy, non-canonical benchmark location** kept only as an archive marker.

- Historical path: `evals/benchmarks/validation-batch5`
- Current policy: new benchmark roots must use an explicit root, workspace `docs/`, workspace `temp/`, or `~/temp`
- The benchmark runner now blocks writes into the installed skill directory, so this path must not be reused for new runs

Do not delete this marker as part of provenance-hardening cleanup.
