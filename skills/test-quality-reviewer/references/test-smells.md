# Test-quality principles & smells (reviewer reference)

Read this when explaining a finding to a human or judging a low-confidence flag. The point
is symmetric with the dev side: just as production code follows SOLID/Clean Code, tests
follow FIRST + a known smell catalog + the test pyramid. A passing suite proves nothing
about effectiveness — mutation survival does.

## FIRST (unit-test structure)

- **Fast** — slow tests get skipped; logic belongs at the fastest layer that can prove it.
- **Independent** — no order coupling, no shared mutable state between tests.
- **Repeatable** — same result every run, every machine, offline. No clock/network/random
  without control. Violations → `MYSTERY_GUEST`.
- **Self-validating** — the test asserts pass/fail itself; no human reading logs. A test
  with no assertion is not self-validating → `NO_ASSERTION`.
- **Timely** — written with (ideally before) the code, not bolted on later.

## Test smells (the Clean-Code-for-tests catalog)

- **Assertion Roulette** — many assertions, no failure messages; when it breaks you cannot
  tell which check failed. Fix: one behaviour per test, or labelled asserts / subtests.
- **Mystery Guest** — the test reads an external file/DB/URL it did not create, so it is
  not repeatable. Fix: build inputs in the test; temp dirs; in-memory fakes.
- **Fragile / Brittle Test** — asserts on incidental detail (full rendered string, UI
  selectors, map order) so cosmetic changes break it. Fix: assert structured fields / a
  stable subset.
- **Conditional Test Logic** — `if`/`for`/`while` inside a test; a passing run may never
  reach the real assertion. Fix: table-driven cases / parametrize — one case, one assert.
- **Eager Test** — one test exercises many behaviours. Fix: split.

## Test design techniques (turn "test thoroughly" into cases)

Each is a directive, not a vibe. When a finding says boundaries are missing, this is what
"add boundaries" concretely means:

- **Boundary-value analysis** — for a range [18,65]: test 17/18/19 and 64/65/66, label each
  accept/reject. Off-by-one defects live exactly here.
- **Equivalence partitioning** — one representative per class (valid / too-low / too-high /
  wrong-type), not ten happy values.
- **Decision table** — every combination of conditions → expected action.
- **Pairwise** — for many parameters, cover all pairs instead of the full cross product.
- **State transition** — legal and illegal transitions of a stateful object.

## The oracle problem (when you cannot enumerate expected output)

For sorters, pricing engines, parsers — "write good assertions" is not enough because you
do not know the answer. Use:

- **Metamorphic testing** — a relation that must hold: "reorder line items → total
  unchanged"; "sort then reverse = reverse then sort-desc".
- **Property-based testing** — invariants over generated inputs: "output length ≤ input
  length", "decode(encode(x)) == x". (This repo already uses `pgregory.net/rapid`.)
- **Golden master / differential** — pin known-good output, or compare against a reference
  implementation.

## Effectiveness > coverage

- **Coverage** proves a line *ran*. **Mutation score** proves an assertion *catches a
  defect*. A test that survives every injected mutant (`>`→`>=`, `+`→`-`) is green but
  ineffective. For high-risk code, "no mutant killed" is itself a finding.

## Test pyramid (cost/stability)

Many fast unit tests, fewer integration, fewest E2E. The inverted "ice-cream cone" (mostly
slow brittle E2E) is the anti-pattern → `PYRAMID_INVERSION`. Before adding a test, ask the
lowest layer that can prove the logic.

## Risk-based prioritisation

*What* to test is judgement, not generation. Rank by blast radius × cost-of-failure; test
high-risk paths densely, low-risk paths lightly. Uniform coverage regardless of risk is a
planning smell.
