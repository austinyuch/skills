---
name: sonarqube-bridge
description: Ingest SonarQube static-scan findings and fuse them with the code graph and the project's remediation vocabulary into one ranked review report. Use when the team uses SonarQube and you want its findings enriched with blast-radius / business capability / actionable fixes, when reviewing a PR that has a SonarQube report, or when asked to "pull in the Sonar issues / combine Sonar with the code graph". It does NOT scan — SonarQube is the authoritative scanner; this is the adapter. Orchestrated by the code-review skill alongside the heuristic helper skills.
---

# sonarqube-bridge

## Overview

SonarQube is the department's authoritative static-scan / SAST and quality-gate tool. This
skill is the **adapter**, not another scanner: it *consumes* SonarQube findings (live Web API or
an offline export), normalizes them into the shared review-finding schema, and **enriches** each
with code-graph blast-radius, business capability, and the project's remediation vocabulary, then
ranks by real risk. `code-review` folds the result in next to the heuristic helper skills.

Division of labour (see also [references/sonar-integration.md](references/sonar-integration.md)):
- **SonarQube** owns broad taint SAST, smells/complexity/duplication, coverage import, and the
  **blocking Quality Gate**.
- **This project** adds Sonar's blind spots — program-graph impact, capability/requirement
  traceability, the refactoring move + test-safety-net vocabulary, and (via the sibling skills)
  test *effectiveness* and *generation*.
- **This bridge** is the connective tissue. It never gates and never scans.

## Contract

Invocation: `python3 scripts/run.py '<json>'` (also accepts JSON on stdin).

Offline / greenfield (export file):
```json
{"source":"file","issues_file":"sonar-issues.json",
 "impact_map":{"internal/pay/charge.go":10},
 "capability_map":{"internal/pay/charge.go":"Payment"}}
```
Live (Web API):
```json
{"source":"api","host":"https://sonarqube.example.com","project_key":"my_proj","token_env":"SONAR_TOKEN"}
```
`issues_file` accepts either a raw `/api/issues/search` response (`{"issues":[...]}`) or a bare
issues array. `impact_map` (file→blast-radius) and `capability_map` (file→capability) are optional
and come from `review-cli impact`/`developer-routing` and `capability-mapper`/the graph.

Output (stdout): `skill_version`, `project`, `source`, `explained`, `summary`
(`by_severity`/`by_type`/`max_risk_score`), `risk_ranking` (your triage order), and `findings[]`
— each with `source="sonarqube"`, `rule`, `type`, `severity`, `file`, `line`, `message`, `owasp`,
`cwe`, `blast_radius`, `capability`, `risk_score`, `remediation`.

Exit is non-zero only on bad input, an unreadable file, an unconfigured API, or a forced
`--explain` provider failure. It never fabricates findings.

### Risk model
`risk_score = severity_weight{high:3,med:2,low:1} × type_factor{vuln/bug:1.5, hotspot:1.2,
smell:1.0} × max(blast_radius,1)`. So a CRITICAL vuln in a widely-imported file outranks the same
vuln in a leaf — Sonar alone ranks by severity, not by how much depends on the file.

### Remediation vocabulary
Sonar messages are terse. The bridge maps each finding to an actionable next step: code smells →
a named refactoring move + the test safety-net it needs first (see `code-refactoring-advisor`);
vulnerabilities/hotspots → an OWASP pointer (see `security-risk-reviewer`); bugs → fix + a
red-first regression test.

## When code-review invokes this

After a SonarQube scan exists for the branch/PR: pull the issues (API or the CI-exported JSON),
pass `impact_map`/`capability_map` from the graph, and present the `risk_ranking` as the triage
list with each finding's remediation. Use `--explain` to turn terse Sonar messages into
context-specific fixes for the top findings.

## Optional LLM explanation, mock mode, install, testing

`--explain` (or `SONARQUBE_BRIDGE_EXPLAIN=1`) rewrites terse messages via `CODE_REVIEW_LLM_*`
(Bedrock-first; fails closed if forced and unconfigured). `SONARQUBE_BRIDGE_MOCK=1` (or `--mock`)
emits labelled offline sample findings. Install with `scripts/install.sh` (self-naming). Test with
`python3 scripts/test_run.py`; coverage `python3 scripts/covcheck.py`; mutation
`python3 scripts/mutation_check.py`. Evidence: [TESTS.md](TESTS.md).
