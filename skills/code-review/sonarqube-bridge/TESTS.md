# sonarqube-bridge — Test Registry (folder-level)

> Spec: `sonarqube-static-scan-integration`. Dependency-free TDD (stdlib `unittest` + seeded
> PBT + stdlib `trace` coverage + a manual mutation harness). Run all: `python3 scripts/test_run.py`.

## Unit / PBT / integration (`scripts/test_run.py`, 26 tests)

| Test ID | Test(s) | Type | Req / Trace | Evidence |
|---|---|---|---|---|
| SONAR-U1 | `TestIngest.test_file_source` / `test_bare_list_issues_form` | unit | REQ-SONAR-001.1 | PASS (object + bare-list forms) |
| SONAR-U2 | `TestIngest.test_mock_mode` | unit | REQ-SONAR-001.4 | PASS (labelled, `-mock`) |
| SONAR-U3 | `TestIngest.test_api_unconfigured_fails_closed` | unit | REQ-SONAR-001.3 | PASS (no host → exit≠0, no stdout) |
| SONAR-U4 | `TestIngest.test_missing_file` / `test_bad_input` / `test_malformed_issues_json` | unit | REQ-SONAR-005.1 | PASS (honest fail-closed) |
| SONAR-U5 | `TestNormalizeEnrich.test_severity_map` | unit (table) | REQ-SONAR-002.2 | PASS (BLOCKER/CRITICAL→high … INFO→low) |
| SONAR-U6 | `test_component_to_file` / `test_owasp_cwe_extraction` | unit | REQ-SONAR-002.1/3/4 | PASS |
| SONAR-U7 | `test_blast_radius_amplifies` / `test_blast_non_numeric_defaults_to_one` | unit | REQ-SONAR-003.1 | PASS |
| SONAR-U8 | `test_capability_tagging` | unit | REQ-SONAR-003.2 | PASS |
| SONAR-U9 | `test_remediation_{code_smell_complexity,duplicate,parameter_object,generic_smell,vulnerability,bug}` | unit | REQ-SONAR-004 | PASS (all 6 remediation branches) |
| SONAR-U10 | `test_vuln_outranks_smell_same_severity` | unit | REQ-SONAR-003.3 | PASS (type factor) |
| SONAR-U11 | `TestRanking.test_ranking_sorted_desc` | unit | REQ-SONAR-003.4 | PASS |
| SONAR-U12 | `TestExplainHonesty.test_default_offline_no_explain` / `test_explain_forced_unconfigured_fails_closed` | unit | REQ-SONAR-005.2/3 | PASS (deterministic source-of-truth; forced explain fails closed) |
| SONAR-P1 | `TestProperties.test_invariants` | property (seeded, 250 cases) | REQ-SONAR-002/003 | PASS (no-drop · required-keys · severity-domain · ranking-sorted) |
| SONAR-P2 | `TestProperties.test_blast_monotonic` | property (seeded, 200 cases) | REQ-SONAR-003.1 | PASS (risk_score non-decreasing in blast) |
| SONAR-I1 | `TestIntegration.test_e2e_ranked_top_finding` | integration (subprocess E2E) | REQ-SONAR-001/003 | PASS (multi-lang export → high-sev+high-blast vuln ranks #1; capability+cwe attached) |

**Command:** `python3 scripts/test_run.py` → `Ran 26 tests OK`.

## Coverage (`scripts/covcheck.py`, stdlib `trace`)

| Test ID | Type | Evidence |
|---|---|---|
| SONAR-COV | line coverage | **164/177 = 92%**. Uncovered = the live `_load_api` network GET (its config-error paths are unit-covered; the success path is now exercised live by SONAR-LIVE against a real server, 2026-06-22), the LLM-explain success glue (provider-dependent; `apply_explanation` unit-tested), and the `__main__` entry line. Deterministic core fully covered. |

## Mutation (`scripts/mutation_check.py`, 4 targeted mutants)

| Test ID | Type | Evidence |
|---|---|---|
| SONAR-M | mutation | **4/4 KILLED** — M1 severity-map flip → SONAR-U5; M2 ranking ascending → SONAR-U11/I1; M3 drop blast multiplier → SONAR-U7; M4 drop type factor → SONAR-U10. |

## Live server proof (`reports/2026-06-22-live-server-proof.md`)

| Test ID | Type | Req / Trace | Evidence |
|---|---|---|---|
| SONAR-LIVE | live current-host E2E | REQ-SONAR-001.2, 002, 003, 004, 005.1 | **PASS 2026-06-22.** Real SonarQube 26.6.0 (podman `:9001`) + real `sonar-scanner` → 9 real issues (Quality Gate `OK`); bridge `source:"api"` + Bearer `USER_TOKEN` ingested all 9, ranked `python:S3776` (Payment, blast 8) at 24.0 above same-severity `javascript:S3504` (blast 3) at 9.0, with capability tags + `Extract Function`/`Parameter Object` remediation. Live fail-closed: wrong token → HTTP 401 exit 2; missing token → exit 2. |

## External Execution (org-bound — remaining)
- ~~Live `source:"api"` against a running SonarQube (`/api/issues/search` with `SONAR_TOKEN`).~~
  **CLOSED current-host 2026-06-22 (SONAR-LIVE).**
- `sonar-scanner` Quality Gate decorating a real **merge request** on the org/department shared
  server (the current-host proof ran the gate `OK` but not against a real PR).
- `--explain` against a live `CODE_REVIEW_LLM_*` provider.
