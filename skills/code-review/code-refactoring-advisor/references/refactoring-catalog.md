# Refactoring catalog (advisor reference)

Read when explaining a smell or deciding whether a heuristic flag is real. Grounded in
Fowler, *Refactoring* (2nd ed.) — still the canonical reference. The governing rule: **a
refactoring changes structure without changing behaviour, and is only safe under a
trustworthy test.** Every move below names that net first.

## Minimality check before prescribing structure

The advisor also applies the Ponytail/YAGNI ladder before recommending new structure:

1. Does this need to exist? If no, skip it.
2. Can the standard library do it? Use it.
3. Can a native platform feature do it portably? Use it, or isolate OS/arch-specific code behind a small adapter with fallback.
4. Can an already-installed dependency do it? Use it.
5. Is it one line? Keep it one line.
6. Only then build the minimum custom implementation.

This is a Phase 2 / Phase 4 rubric for avoiding over-engineering, not a Phase 5 review
verdict. It should reject speculative abstractions, but preserve abstractions that carry a
real policy, lifecycle, error, security, external-contract, or domain boundary.

Keep the recommendation architecture/platform agnostic. If a native feature is OS/arch-specific,
the review should require an explicit adapter, guard, or fallback before treating it as a
minimal replacement for custom code.

## The smells and their moves

### Long Method (`LONG_METHOD`) → Extract Function
A method doing many things is hard to name, test, and reuse. Extract cohesive chunks into
intention-named functions. *Net first:* a characterization test pinning current output, so
the extraction provably preserves behaviour.

### Long Parameter List (`LONG_PARAMETER_LIST`) → Introduce Parameter Object / Preserve Whole Object
Many parameters travel together and obscure intent. Group them into a value object, or pass
the whole object the caller already has. *Net first:* a test pinning each call site.

### Deep Nesting (`DEEP_NESTING`) → Replace Nested Conditional with Guard Clauses
Arrow-shaped code hides the happy path. Return/continue early on the exceptional cases, then
write the main path flat. *Net first:* branch-covering tests so no path silently changes.

### God File / Large Class (`GOD_FILE`) → Extract Class / Move Function
One file with too many responsibilities resists change (Shotgun Surgery / Divergent Change).
Split by responsibility. *Net first:* tests around each responsibility being moved. Use the
code graph's impact/`developer-routing` to see blast radius before splitting.

### Duplicated Block (`DUPLICATED_BLOCK`) → Extract Function, call from both sites
Duplicates drift apart and one copy gets fixed while the other rots. Extract once, call from
both. *Net first:* a test exercising both sites so they cannot diverge again.

### Magic Number/Literal (`MAGIC_NUMBER`) → Replace Magic Literal with Named Constant
An unexplained literal loses its intent. Name it. Mechanically safe under the existing suite.

### Complex Condition (`COMPLEX_CONDITION`) → Decompose Conditional
A boolean with many operators is unreadable and untestable. Extract an intention-named
predicate (`isEligibleForDiscount(...)`). *Net first:* tests for each truth combination.

## Related smells worth naming in review (not auto-detected)

- **Feature Envy** — a method more interested in another object's data than its own → Move
  Function.
- **Primitive Obsession** — strings/ints standing in for domain concepts → Replace Primitive
  with Object / Introduce Parameter Object. (`MAGIC_NUMBER` + `LONG_PARAMETER_LIST` are proxies.)
- **Shotgun Surgery** — one change forces edits in many files → Move Function/Field to gather.
- **Divergent Change** — one module changes for many unrelated reasons → Extract Class (SRP).

## How this connects to SOLID

Smells are SOLID violations made concrete: Divergent Change / God File ↔ SRP; a `switch` on
type that grows ↔ OCP (Replace Conditional with Polymorphism); wrong-way dependency ↔ DIP
(Dependency Injection). Naming the SOLID principle alongside the move makes the review
teachable, not just corrective.
