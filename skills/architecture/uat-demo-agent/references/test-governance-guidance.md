# Test Governance Guidance

This reference provides detailed BVT smoke, exploratory test, and tag-based verification procedures for the `uat-demo-agent` skill. It aligns with the test governance model defined in `qa-qc-test-governance-enhancement` and the shared `TEST_GOVERNANCE_GUIDE.md`.

---

## 1. BVT Smoke Operating Flow

BVT (Build Verification Test) smoke is a fast-feedback gate that validates core paths after a UAT run, CI build, hotfix, or release candidate. It does **not** replace full UAT or grant readiness status on its own.

### Step-by-step

1. **Locate the Test Decision Table**
   - Workspace level: `.agents/specs/TESTS.md`
   - Package level: `{module}/TESTS.md` (e.g. `internal/reporting/TESTS.md`)

2. **Filter BVT candidates**
   - Select rows where `Type Tag` includes `smoke`
   - Further narrow to rows where `Risk ≥ 4`
   - These are the minimum set that must pass before any release or handoff claim

3. **Execute filtered tests**
   ```bash
   # Pattern-based (recommended for Go repos)
   go test ./... -run "TestSmoke" -timeout 120s -v

   # If tests use build tags
   go test ./... -tags=smoke -timeout 120s -v

   # For a specific package
   go test ./internal/reporting/... -run "TestSmoke" -timeout 120s -v
   ```

4. **Evaluate results**
   - **PASS**: All filtered tests return `PASS`. Proceed with confidence.
   - **FAIL**: Any filtered test returns `FAIL` → stop, investigate, fix before proceeding.
   - **PASS***: Test passed but with caveats (mock/stub). Treat as conditional — do not claim full-integration readiness.

5. **Record outcome**
   - Update the `Last Run` and `Result` columns in the relevant TESTS.md
   - If running in CI, emit structured output for automated TESTS.md update

### Success criteria

All `smoke` + Risk ≥ 4 test cases must report `PASS` (not `PASS*`, not `SKIP`, not `BLOCKED`). A single failure blocks the gate.

### What BVT smoke does NOT prove

- Full integration readiness
- Demo readiness
- Coverage of all edge cases
- Absence of regression in non-smoke paths

BVT smoke is a necessary but not sufficient condition for readiness claims.

---

## 2. Exploratory Test Charter Template

Exploratory testing supplements structured UAT by systematically probing boundaries that formal test cases may not cover.

### When to trigger

- A new feature integrates for the first time
- A coverage gap is identified (e.g. TESTS.md shows `none` or `mock` status for a critical path)
- A chaos test reveals a new failure mode not covered by existing tests
- Post-release observation surfaces unexpected behavior

### Charter format

```markdown
## Exploratory Test Charter

- **Charter ID**: EXP-{MODULE}-{NNN}
- **Mission**: [What are you trying to learn or break?]
- **Scope**: [Which modules/features/paths are in scope?]
- **Duration**: [Time-boxed: 30min / 60min / 90min]
- **Risk Focus**: [Which Risk levels or Type Tags are you targeting?]
- **Setup Notes**: [Any preconditions, test data, or environment setup]
```

### Session recording format

```markdown
## Session Record

- **Charter**: EXP-{MODULE}-{NNN}
- **Start**: [ISO8601]
- **End**: [ISO8601]
- **Tester**: [agent / human]

### Findings

| # | Observation | Severity | Reproducible | Follow-up |
|---|-------------|----------|--------------|-----------|
| 1 | [description] | [1-5] | [yes/no] | [new test / CR / none] |

### Bugs Filed

- [link or description]

### Follow-up Actions

- [ ] Add test row to TESTS.md: T-{MODULE}-{NNN}
- [ ] Update Risk for existing row: T-{MODULE}-{NNN} → Risk {N}
- [ ] Create CR: CR-{ID} for [description]
```

### Feedback loop

1. Each finding that warrants a permanent test → add a new row to the package-level TESTS.md
2. Each finding that reveals a higher risk than previously assessed → update the `Risk` column
3. Each finding that requires design/contract change → create a CR in the relevant spec's `change-requests/` directory
4. Findings that are informational only → record in session notes, no further action

---

## 3. Tag Filtering Commands

### Go test pattern matching

The recommended naming convention maps Type Tags to test function prefixes:

| Type Tag | Function prefix | Example |
|----------|----------------|---------|
| `smoke` | `TestSmoke_` or `TestSmoke` | `TestSmoke_ReportGeneration` |
| `error-force` | `TestErrorForce_` | `TestErrorForce_BlankArtifactLocator` |
| `regression` | `TestRegression_` | `TestRegression_BundlePersistence` |
| `api` | `TestAPI_` | `TestAPI_PlanValidateEndpoint` |
| `cross-spec` | `TestCrossSpec_` | `TestCrossSpec_PublisherReportIntegrity` |
| `security` | `TestSecurity_` | `TestSecurity_AuthTokenValidation` |
| `ai-agent` | `TestAIAgent_` | `TestAIAgent_ReasoningLoopFallback` |
| `property-based` | `TestPBT_` | `TestPBT_ArtifactMetadataInvariant` |

### Filtering commands

```bash
# Run all smoke tests across the repo
go test ./... -run "TestSmoke" -timeout 120s

# Run error-force tests in a specific package
go test ./internal/reporting/... -run "TestErrorForce" -timeout 60s

# Run multiple tags (smoke + error-force)
go test ./... -run "TestSmoke|TestErrorForce" -timeout 180s

# Run high-risk tests only (combine with grep on TESTS.md)
grep -E "smoke.*[45]|error-force.*[45]" internal/reporting/TESTS.md
```

### TESTS.md grep-based filtering

```bash
# Find all smoke tests with Risk ≥ 4
grep -E "\| smoke.*\| [45] \|" .agents/specs/TESTS.md

# Find all tests that are still mock/stub (potential gaps)
grep -E "\| (mock|stub|none) \|" .agents/specs/TESTS.md

# Find all FAIL or BLOCKED results
grep -E "\| (FAIL|BLOCKED) \|" .agents/specs/TESTS.md
```

---

## 4. Type Tag Quick Reference

The following subset is most relevant to `uat-demo-agent` operations. For the complete 18-tag enumeration, refer to the global `TEST_GOVERNANCE_GUIDE.md`.

| Tag | Purpose | When to use with uat-demo-agent |
|-----|---------|-------------------------------|
| `smoke` | Build verification test | Post `run uat`, CI gate, release preflight |
| `regression` | Regression test | After bug fixes, refactoring, dependency updates |
| `error-force` | Edge / failure path | Validate error propagation, blank inputs, corrupt artifacts |
| `cross-spec` | Cross-spec integration | Validate publisher ↔ reporting ↔ bundle interactions |
| `api` | API / contract test | Validate CLI contract, JSON schema compliance |
| `ai-agent` | AI / agent flow | Validate reasoning loop, LLM fallback, prompt behavior |
| `property-based` | Property-based test | Invariant checks on artifact metadata, report structure |
| `security` | Security risk verification | Auth token handling, path traversal, input sanitization |

### Tags less commonly used in uat-demo-agent context

| Tag | Purpose |
|-----|---------|
| `major-feature` | Spec-level key feature verification |
| `detailed-feature-p1/p2/p3` | Priority-tiered detailed feature tests |
| `ui` | UI / browser flow |
| `hotfix` | Hotfix regression |
| `performance` | Performance testing |
| `i18n-l10n` | Internationalization / localization |
| `cross-system` | External system integration |
| `mutation` | Mutation testing |

---

## 5. Risk Definition Quick Reference

| Risk | Definition | Example in uat-demo-agent context |
|------|-----------|----------------------------------|
| `1` | Trivial — does not affect functionality | Cosmetic log format, comment typo |
| `2` | Low — affects minor paths | Non-critical report field formatting |
| `3` | Medium — affects core experience or external boundary | Report generation edge case, bundle path resolution |
| `4` | High — affects auth / mutation / integration | Artifact metadata integrity, cross-run evidence rejection, publisher validation |
| `5` | Critical — may cause security breach, data corruption, or major error | Evidence false-green, report readiness overclaim, path traversal in artifact locator |

### Risk-based verification strategy

- **Risk 5**: Must have `real-wired` status. Mock/stub not acceptable for readiness.
- **Risk 4**: Should have `real-wired` or `fixture` with documented gap. Include in BVT smoke.
- **Risk 3**: `fixture` or `stub` acceptable for first slice. Plan upgrade path.
- **Risk 1-2**: Any status acceptable. Low priority for coverage improvement.
