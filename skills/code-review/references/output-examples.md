# Output Examples

Complete examples of command outputs for IDE agent parsing.

## analyze - Code Analysis Output

**Command:**
```bash
review-cli analyze internal/agent/scan.go
```

**Output Format:**
```
Analyzed /path/to/file.go:
- Language: <language>
- Functions: <count>
- Classes: <count>
```

**Example:**
```
Analyzed <workspace-root>/project/internal/agent/scan.go:
- Language: go
- Functions: 3
- Classes: 1
```

**Parsing Guide:**
- Line 1: File path (absolute)
- Line 2: Language detected
- Line 3: Function count (integer)
- Line 4: Class/struct count (integer)

---

## improve - Improvement Suggestions Output

**Command:**
```bash
review-cli improve internal/api/server.go
```

**Output Format:**
```
Improvement suggestions for <filepath>:

[Priority] <Title>
Rationale: <Reason>
Suggestion: <Action>

[Priority] <Title>
...
```

**Example:**
```
Improvement suggestions for internal/api/server.go:

[HIGH] Extract method: handleRequest() is too complex
Rationale: Single Responsibility Principle violated
Suggestion: Split into handleValidation() and handleProcessing()

[MEDIUM] Add error handling: Missing error check at line 42
Rationale: Potential nil pointer dereference
Suggestion: Add if err != nil { return err }

[LOW] Rename variable: 'x' is not descriptive
Rationale: Code readability
Suggestion: Rename to 'requestCount' or similar
```

**Parsing Guide:**
- Priority levels: HIGH, MEDIUM, LOW
- Each suggestion has 3 lines: Title, Rationale, Suggestion
- Blank line separates suggestions

---

## report - Comprehensive Report Output

**Command:**
```bash
review-cli report ./internal
```

**Output Format:** Markdown document

**Example:**
```markdown
# Code Review Report

Generated: 2026-03-03 16:00:00

## Executive Summary

- Total files analyzed: 54
- Total functions: 234
- Total classes/structs: 45
- Total lines of code: 12,450
- Issues found: 12 (2 high, 5 medium, 5 low)

## Issues by Severity

### High Priority (2)

1. **internal/api/server.go:142** - Missing error handling
   - Impact: Potential runtime panic
   - Recommendation: Add error check before dereferencing

2. **internal/agent/orchestrator.go:89** - Race condition detected
   - Impact: Data corruption in concurrent access
   - Recommendation: Add mutex lock

### Medium Priority (5)

...

### Low Priority (5)

...

## Code Metrics

| Package | Files | Functions | Complexity | Test Coverage |
|---------|-------|-----------|------------|---------------|
| api     | 7     | 45        | Medium     | 85%           |
| agent   | 5     | 32        | Low        | 90%           |
| lsp     | 18    | 89        | Medium     | 78%           |

## Recommendations

1. **Refactor complex functions**
   - Target: api/server.go, agent/orchestrator.go
   - Reason: Cyclomatic complexity > 15
   - Action: Extract methods, simplify logic

2. **Improve test coverage**
   - Current: 82% overall
   - Target: 90%+
   - Focus: lsp package (78%)

3. **Add documentation**
   - Missing: 12 exported functions
   - Target: All public APIs

## Architecture Insights

- Design patterns detected: Factory, Strategy, Singleton
- Dependency depth: 3 levels (acceptable)
- Circular dependencies: None detected ✅

## Next Steps

1. Address high-priority issues immediately
2. Schedule refactoring for complex functions
3. Increase test coverage to 90%
4. Add missing documentation
```

**Parsing Guide:**
- Markdown format (can be rendered in IDE)
- Structured sections: Summary, Issues, Metrics, Recommendations
- Tables for metrics
- Actionable next steps

---

## architecture - Architecture Analysis Output

**Command:**
```bash
review-cli architecture ./
```

**Output Format:**
```
Architecture Analysis for <directory>

Modules:
- <package> (<file_count> files)
...

Dependencies:
- <source> → <target> (<count> dependencies)
...

Design Patterns:
- <Pattern>: <location>
...

Recommendations:
- <Recommendation>
...
```

**Example:**
```
Architecture Analysis for ./

Modules:
- internal/api (7 files)
- internal/agent (5 files)
- internal/lsp (18 files)
- internal/parser (4 files)
- internal/graph (3 files)
- internal/vector (2 files)

Dependencies:
- api → agent (3 dependencies)
- agent → parser (5 dependencies)
- agent → graph (2 dependencies)
- lsp → parser (2 dependencies)
- parser → graph (1 dependency)

Dependency Depth: 3 levels
Circular Dependencies: None detected ✅

Design Patterns:
- Factory Pattern: agent/orchestrator.go (NewOrchestrator)
- Strategy Pattern: lsp/plugins.go (Plugin interface)
- Singleton Pattern: config/config.go (LoadConfig)
- Observer Pattern: api/websocket.go (Hub)

Architecture Quality:
- Modularity: Good (clear package boundaries)
- Coupling: Low (minimal cross-package dependencies)
- Cohesion: High (related code grouped together)

Recommendations:
1. Consider splitting api package (7 files, may be too large)
2. Reduce coupling between agent and parser (5 dependencies)
3. Add interface for graph operations (improve testability)
4. Document architecture decisions (ADRs)
```

**Parsing Guide:**
- Sections: Modules, Dependencies, Patterns, Recommendations
- Dependency format: `source → target (count)`
- Pattern format: `Pattern: location (details)`
- Quality metrics: Modularity, Coupling, Cohesion

---

## search-code - GraphRAG Search Output

This example shows the **current Mode A** output surface: base `search-code` retrieval plus bounded graph-aware rerank/result-shaping.

**Command:**
```bash
review-cli search-code ./tests/testdata/xpp_corpus_coupon/gts/Classes/CLASSES_CouponCreateBase.xpo "CouponCreateBase nextCouponId" --graph-init auto --limit 5 --threshold 0.1
```

**Output Format:** JSON

**Example:**
```json
{
  "schema_version": "1.2",
  "artifact_type": "graphrag-search-results",
  "query": "CouponCreateBase nextCouponId",
  "project_boundary_root": "/path/to/project",
  "persistence_mode": "local-sqlite",
  "graph_init": {
    "policy": "auto",
    "action": "performed"
  },
  "vector_sqlite": "/path/to/.code-review/state.sqlite",
  "search_mode": "hybrid",
  "retrieval_stage": "graph_reranked",
  "model_rerank_stage": "executed",
  "model_rerank_provider": "bedrock",
  "model_rerank_model": "arn:aws:bedrock:us-east-1::foundation-model/cohere.rerank-v3-5:0",
  "graph_capability": "available",
  "relation_coverage_status": "ready",
  "graph_refinement": {
    "seed_count": 3,
    "hop_budget": 2,
    "explored_node_count": 3,
    "applied_edge_families": [
      "INHERITS_FROM",
      "REFERENCES_CLASS",
      "OVERRIDES",
      "CALLS"
    ]
  },
  "boundary_summary": {
    "triggered": false
  },
  "ranking_notes": [
    "graph-aware refinement executed with bounded traversal",
    "topology readiness is partial; graph refinement remains bounded and conservative",
    "class semantics are partial; graph refinement remains bounded and conservative"
  ],
  "limit": 5,
  "threshold": 0.1,
  "results": [
    {
      "name": "CouponCreateBase.nextCouponId",
      "entity_type": "function",
      "file_path": "/path/to/CLASSES_CouponCreateBase.xpo",
      "candidate_role": "authoritative_generator",
      "base_similarity": 0.75,
      "final_score": 0.93,
      "ranking_reasons": [
        "candidate role: authoritative_generator",
        "generator/allocator boost",
        "graph traversal boost"
      ],
      "similarity": 0.93,
      "model_rerank_score": 0.98
    }
  ]
}
```

**Parsing Guide:**
- `artifact_type` identifies the output as graphRAG search results
- `graph_init.action` indicates whether index refresh happened for the search surface
- `retrieval_stage` tells you whether the result stayed `hybrid_only`, was `graph_reranked`, was `boundary_summarized`, or is `capability_unavailable`
- `model_rerank_stage` appears only when model-backed rerank is configured; current executable support is `bedrock`, OpenAI-compatible local hosts, and guarded `local-cpu`
- `relation_coverage_status` tells you whether the currently materialized relation families are `ready`, `partial`, or `insufficient` for downstream topology confidence
- `graph_refinement` summarizes the bounded second-stage traversal that informed reranking
- `boundary_summary` explains cut-off behavior when the frontier is intentionally summarized instead of expanded further
- `results[].candidate_role` highlights whether a surfaced candidate looks like an `authoritative_generator`, `parameter_reference`, `downstream_consumer`, or `helper_or_upgrade`
- `results[].base_similarity` is the hybrid/vector first-pass score before deterministic graph-aware refinement
- `results[].final_score` is the surfaced score after bounded rerank/result shaping; `results[].similarity` remains the same value for backward compatibility
- `results[].ranking_reasons` contains per-candidate audit notes so reviewers can inspect why a result moved
- `results[]` remains ordered output, but `similarity` should now be read as the surfaced score after first-slice refinement rather than a pure old baseline score
- `results[].model_rerank_score` is emitted when configured model-backed or local CPU rerank succeeds
- `follow_up_guidance` may now point directly at a stronger authoritative candidate when the top hit remains ambiguous after deterministic refinement
- Mode B adds `execution_mode: mode_b` and per-result `recovered_context` previews on top of this base ranked-result contract.
- `graph_queryable=true` together with `relation_coverage_status=partial` is a valid state: the graph exists and is usable, but downstream interpretation should remain conservative rather than assuming full topology completeness.

---

## search-code-eval - Fixed Retrieval Evaluation Output

**Command:**
```bash
review-cli search-code-eval ./tests/testdata/xpp_corpus_coupon/gts/Classes/CLASSES_CouponCreateBase.xpo ./tests/testdata/search_code_eval/coupon_cases.json --graph-init always --limit 5 --threshold 0.1
```

**Output Format:** JSON

**Example:**
```json
{
  "schema_version": "1.0",
  "artifact_type": "search-code-eval-result",
  "total_cases": 3,
  "passed_cases": 3,
  "failed_cases": 0,
  "cases": [
    {
      "id": "coupon-numbering-rule",
      "query": "coupon id numbering rule",
      "expected_any": ["CouponCreateBase.nextCouponId"],
      "top_k": 3,
      "passed": true,
      "matched_name": "CouponCreateBase.nextCouponId",
      "matched_rank": 1,
      "retrieval_stage": "graph_reranked",
      "graph_capability": "available",
      "top_results": [
        {
          "rank": 1,
          "name": "CouponCreateBase.nextCouponId",
          "entity_type": "function",
          "candidate_role": "authoritative_generator",
          "base_similarity": 0.15,
          "final_score": 0.53,
          "ranking_reasons": ["candidate role: authoritative_generator"],
          "similarity": 0.53
        }
      ]
    }
  ]
}
```

**Parsing Guide:**
- `passed_cases` and `failed_cases` are the first comparison signal for release-to-release regression checks
- `cases[].matched_rank` is 1-based and only present when an expected candidate matched inside `top_k`
- failed cases retain `top_results[]` so reviewers can diagnose whether the issue is first-pass retrieval, rerank, or expectation drift

---

## graph-relation-eval - Fixed Relation Evaluation Output

**Command:**
```bash
review-cli graph-relation-eval ./tests/testdata/graph_relation_eval/go_callgraph ./tests/testdata/graph_relation_eval/go_callgraph_cases.json --graph-init always
```

**Output Format:** JSON

**Example:**
```json
{
  "schema_version": "1.0",
  "artifact_type": "graph-relation-eval-result",
  "persistence_mode": "local-sqlite",
  "graph_init": "performed",
  "relation_coverage_status": "partial",
  "total_cases": 2,
  "passed_cases": 2,
  "failed_cases": 0,
  "relation_family_counts": {
    "CALLS": 2,
    "CONTAINS": 1,
    "DEFINES": 3
  },
  "cases": [
    {
      "id": "go-direct-call-handle-validates-coupon",
      "relation_type": "CALLS",
      "source_name": "HandleCoupon",
      "target_name": "validateCoupon",
      "source_label": "Function",
      "target_label": "Function",
      "passed": true,
      "edge_family_count": 2,
      "matched_edges": [
        {
          "relation_type": "CALLS",
          "source_label": "Function",
          "source_name": "HandleCoupon",
          "target_label": "Function",
          "target_name": "validateCoupon",
          "language": "go",
          "provenance": "parser-call"
        }
      ]
    }
  ]
}
```

**Parsing Guide:**
- `passed_cases` and `failed_cases` are the first comparison signal for graph topology regression checks
- `relation_family_counts` helps distinguish "edge missing" from "relation family was never produced"
- failed cases retain `edge_family_count` so reviewers can see whether a family exists but the expected endpoint pair is absent
- XPP semantic cases may carry `warning_code`, such as `UNRESOLVED_CLASS_TARGET`, and should be treated as reviewable partial evidence rather than full semantic completeness
- Checked-in relation fixtures currently cover Go `CALLS`, Go same-file and same-package cross-file interface-signature `IMPLEMENTS`, TypeScript same-file syntax/signature `IMPLEMENTS`, TypeScript same-directory relative-import interface-signature `IMPLEMENTS`, XPP `REFERENCES_CLASS`, XPP `INHERITS_FROM`, and XPP `OVERRIDES`; use the multi-family XPP fixture when validating class hierarchy and override edges together.

---

## eval-compare - Fixed Evaluation Comparison Output

**Command:**
```bash
review-cli eval-compare .code-review/baseline/search-code-eval.json .code-review/current/search-code-eval.json
```

**Output Format:** JSON

**Example:**
```json
{
  "schema_version": "1.0",
  "artifact_type": "eval-comparison-result",
  "compared_artifact_type": "search-code-eval-result",
  "baseline_total_cases": 3,
  "current_total_cases": 3,
  "baseline_passed_cases": 3,
  "current_passed_cases": 2,
  "passed_delta": -1,
  "failed_delta": 1,
  "regression_count": 1,
  "improvement_count": 0,
  "unchanged_count": 2,
  "added_count": 0,
  "removed_count": 0,
  "case_deltas": [
    {
      "id": "coupon-numbering-rule",
      "status": "regressed",
      "baseline_passed": true,
      "current_passed": false,
      "current_failure_reason": "expected candidate not found within top_k"
    },
    {
      "id": "coupon-run-number",
      "status": "unchanged",
      "baseline_passed": true,
      "current_passed": true,
      "baseline_matched_rank": 3,
      "current_matched_rank": 1,
      "matched_rank_delta": -2
    }
  ]
}
```

**Parsing Guide:**
- Treat `regression_count > 0` as the first release-gate warning signal.
- `added` and `removed` case statuses indicate benchmark drift, not product quality by themselves.
- For search comparisons, negative `matched_rank_delta` means the expected candidate moved closer to the top.
- For graph relation comparisons, use `relation_family_deltas[]` to distinguish expected-edge regressions from broad relation-family production changes.
- The graph relation comparison fixtures demonstrate an `OVERRIDES` improvement and relation-family delta in the same machine-readable artifact.
- The Go and TypeScript implementation comparison fixtures demonstrate same-file, same-package/same-directory, and relative-import `IMPLEMENTS` improvements and relation-family deltas in machine-readable artifacts.

---

## eval-gate - Fixed Evaluation Gate Output

**Command:**
```bash
review-cli eval-gate .code-review/current/eval-comparison.json
```

**Output Format:** JSON

**Example:**
```json
{
  "schema_version": "1.0",
  "artifact_type": "eval-gate-result",
  "compared_artifact_type": "search-code-eval-result",
  "passed": false,
  "policy": {
    "max_regressions": 0,
    "min_passed_delta": 0,
    "max_failed_delta": 0,
    "max_matched_rank_regression": 0,
    "require_no_removed": true,
    "require_no_relation_drop": true
  },
  "summary": {
    "regression_count": 1,
    "passed_delta": -1,
    "failed_delta": 1
  },
  "violation_count": 3,
  "violations": [
    {
      "code": "REGRESSION_COUNT",
      "message": "regression count exceeds policy",
      "actual": 1,
      "threshold": 0
    }
  ]
}
```

**Parsing Guide:**
- Treat `passed: false` as a release-gate failure.
- Use `violations[].code` for deterministic CI messages.
- A graph `RELATION_FAMILY_DROP` violation means the relation family count decreased even if individual checked cases still passed.

---

## scan - Spec Validation Output

**Command:**
```bash
review-cli scan ./.agents/specs/my-feature
```

**Output Format:**
```
Spec Validation Results for <directory>

Files:
✅ <filename>: <status>
⚠️  <filename>: <status>
   - <issue>
❌ <filename>: <status>

Completeness: <percentage>%

Issues:
- <issue_description>
...
```

**Example:**
```
Spec Validation Results for ./.agents/specs/go-backend-rewrite

Files:
✅ requirements.md: Complete (all sections present)
✅ design.md: Complete (architecture documented)
⚠️  tasks.md: Incomplete (2 issues)
   - Missing: Acceptance Criteria section
   - Missing: Testing Strategy section

Completeness: 85%

Issues:
- tasks.md: Missing acceptance criteria for 3 tasks
- tasks.md: No testing strategy defined
- design.md: API endpoints not fully documented (only 5 of 7)

Recommendations:
1. Add acceptance criteria to all tasks
2. Define testing strategy (unit, integration, e2e)
3. Complete API endpoint documentation
```

**Parsing Guide:**
- Status symbols: ✅ (complete), ⚠️ (warning), ❌ (error)
- Completeness percentage: 0-100%
- Issues list: Specific problems found
- Recommendations: Actionable fixes

---

## version - Version Information Output

**Command:**
```bash
review-cli version
```

**Output Format:**
```
Code Review System v<version>
<Build info>
```

**Example:**
```
Code Review System v0.1.0
Go Backend - Phase 4 Complete
```

---

## Exit Codes

All commands use standard exit codes:

- `0` - Success
- `1` - General error (file not found, invalid input)
- `2` - Invalid arguments
- `3` - Database connection error
- `4` - Analysis error (parsing failed)

**Usage in IDE Agent:**
```python
result = subprocess.run(["review-cli", "analyze", "file.go"])
if result.returncode == 0:
    # Success - parse stdout
    parse_output(result.stdout)
elif result.returncode == 3:
    # Database error - show connection error
    show_error("Database connection failed")
else:
    # Other error - show stderr
    show_error(result.stderr)
```

---

## Output Parsing Tips

### For IDE Integration

1. **Structured Output**: All outputs are line-based, easy to parse
2. **Consistent Format**: Each command has predictable structure
3. **Error Handling**: Check exit code first, then parse stdout/stderr
4. **Markdown Support**: Report output can be rendered in IDE

### Example Parser (Python)

```python
def parse_analyze_output(output: str) -> dict:
    """Parse analyze command output"""
    lines = output.strip().split('\n')
    
    return {
        'filepath': lines[0].split(': ')[0].replace('Analyzed ', ''),
        'language': lines[1].split(': ')[1],
        'functions': int(lines[2].split(': ')[1]),
        'classes': int(lines[3].split(': ')[1])
    }

def parse_improve_output(output: str) -> list:
    """Parse improve command output"""
    suggestions = []
    blocks = output.split('\n\n')[1:]  # Skip header
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            suggestions.append({
                'priority': lines[0].split(']')[0].replace('[', ''),
                'title': lines[0].split('] ')[1],
                'rationale': lines[1].replace('Rationale: ', ''),
                'suggestion': lines[2].replace('Suggestion: ', '')
            })
    
    return suggestions
```
