# SonarQube integration reference

How SonarQube composes with this project's review tooling. The governing principle: **SonarQube
is the authoritative gate; the project's tools pre-flight and enrich it — they do not compete.**

## Division of labour

| Concern | Owner | Why |
|---|---|---|
| Broad multi-language taint SAST | **SonarQube** | Real data-flow analysis; far beyond regex heuristics |
| Code smells / complexity / duplication | **SonarQube** | CPD + cognitive-complexity engine |
| Coverage import + ratings | **SonarQube** | Consumes lcov/cobertura/opencover/Go cover |
| **Blocking quality gate at PR** | **SonarQube** | The single merge gate — do not double-gate |
| Program-graph impact / blast-radius | **review-cli graph** | Sonar has no cross-file program graph |
| Business capability / requirement traceability | **capability-mapper + graph** | Sonar has no domain model |
| Test *effectiveness* (smells, mutation) | **test-quality-reviewer** | Sonar imports coverage %, not effectiveness |
| Test *generation* (boundary/pairwise) | **test-design-generator** | Sonar does not generate tests |
| Refactoring move + test safety-net | **code-refactoring-advisor** | Sonar flags "complex", not "Extract Function + add a characterization test first" |
| Fast heuristic security pre-flight | **security-risk-reviewer** | Shift-left; catch the obvious before the gate |
| **Fusing Sonar findings + graph + remediation** | **sonarqube-bridge** | The connective tissue |

## Local, agent-skill-driven left-shift (no remote CI)

This repo left-shifts everything to **local CI** — there is no remote SonarQube CI stage. The
gate runs where the team runs it (local `sonar-scanner` against the SonarQube server, or the
server's own analysis); the *review* is driven locally by agent skills:

1. **Gate (local / authoritative).** `sonar-scanner` runs as part of the local test-left-shift
   (or on the SonarQube server). Its Quality Gate is authoritative. The repo never adds a remote
   CI stage to enforce it.
2. **Local left-shift (agent skills).** `local_ci.py` runs the heuristic helper skills over
   changed files (advisory, `LOCAL_CI_REVIEW_SKILLS=1`), and — when a Sonar issues export is
   present (`SONAR_ISSUES_FILE`) — runs **this bridge** over it, so Sonar findings join the same
   local pre-push review. The `code-review` agent skill orchestrates the same set during review.
3. **Enrichment (this bridge).** Sonar issues (local export or Web API) → join to graph impact +
   capability → map to remediation vocabulary → rank by real risk → one report.

## SonarQube Web API notes (live mode)

- Issues: `GET /api/issues/search?componentKeys=<projectKey>&resolved=false&ps=500` (paginate via
  `&p=`). Security hotspots are a separate endpoint: `GET /api/hotspots/search`.
- Quality gate status: `GET /api/qualitygates/project_status?projectKey=<key>`.
- Auth: SonarQube 10+ accepts `Authorization: Bearer <token>`; older servers use HTTP Basic with
  the token as the username and an empty password. The bridge uses Bearer.
- Tags carry `owasp-*` and `cwe-*` when the rule is security-related; the bridge surfaces them.

## Local left-shift wiring (greenfield checklist)

1. `sonar-project.properties` (repo root) declares `sonar.sources`, `sonar.tests`, and per-language
   coverage report paths — used by `sonar-scanner` wherever it runs.
2. Run the scan **locally** when desired: `sonar-scanner -Dsonar.host.url=$SONAR_HOST_URL
   -Dsonar.token=$SONAR_TOKEN`, then export its issues (Web API `/api/issues/search` → a JSON file).
3. Point the local left-shift at that export: `SONAR_ISSUES_FILE=sonar-issues.json
   LOCAL_CI_REVIEW_SKILLS=1 scripts/local-verify.sh --pre-push` (the bridge runs over it and prints
   the ranked findings, non-blocking), or run `sonarqube-bridge` directly during an agent review.
4. There is **no remote GitLab/GitHub CI stage** — left-shift is local and agent-skill driven.
