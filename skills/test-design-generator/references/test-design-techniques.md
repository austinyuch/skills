# Test-design techniques (generator reference)

Each technique targets a distinct defect class. The generator applies the structural ones;
this reference explains them and the ones that need human/LLM judgement.

## Boundary-value analysis
Off-by-one and `>` vs `>=` defects cluster at the edges of a range, not the middle. For an
accepted range [lo, hi], test `lo-1` (reject), `lo`, `lo+1`, `hi-1`, `hi`, `hi+1` (reject).
Always label each accept/reject — that is the test's oracle.

## Equivalence partitioning
Inputs fall into classes that the code treats the same way (valid / too-low / too-high /
wrong-type / empty). Test one representative per class instead of ten values from the same
class. Combine with boundary-value: partitions tell you *which* classes, boundaries tell you
*where they meet*.

## Decision tables
When the output depends on a combination of conditions, enumerate every condition
combination → expected action. Catches missing/contradictory business rules. Best when rules
are few and interacting.

## Pairwise (all-pairs) combination
Most combinatorial defects are triggered by the interaction of just **two** parameters. With
many parameters, testing every combination explodes; pairwise covers every value-pair with a
small set of rows. The generator emits this in `combinations[]`. Use it instead of a full
cartesian product when you have 3+ multi-valued parameters.

## State-transition testing
For stateful objects, test legal transitions (and that illegal ones are rejected): e.g. an
order can go Created→Paid→Shipped but not Shipped→Created. The generator does not infer state
machines — supply them, or use `--explain`.

## The oracle problem (knowing the right answer)
Generating inputs is the easy half. For functions where you cannot enumerate the expected
output by hand:

- **Property-based testing** — assert invariants over generated inputs ("output length ≤
  input length"; "decode(encode(x)) == x"). This repo uses `pgregory.net/rapid`.
- **Metamorphic testing** — a transformation that must preserve a relation ("reorder line
  items → total unchanged"; "scale all prices ×2 → total ×2").
- **Golden master** — pin a known-good output and diff future runs.
- **Differential testing** — compare against a reference/older implementation.

Pick an oracle strategy *before* writing assertions; it determines whether hand-written
expected values are even feasible.

## What needs human/LLM judgement (use `--explain`)
- Semantic negatives: injection/escape strings, unicode/whitespace, null/None, locale.
- Domain rules implied by the subject (a "discount" field that cannot exceed the subtotal).
- Risk weighting: which parameter combinations are worth the most cases.
