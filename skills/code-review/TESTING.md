# Code Review Skill - Testing Results

## ✅ Expected Verification Gates

### Workspace Bundle Smoke

```bash
cd .agents/skills/code-review
scripts/review-cli-linux-amd64 version  # replace with the matching review-cli-<os>-<arch> binary
scripts/review-cli-linux-amd64 analyze ../../../go-review-service/internal/agent/improve.go
```

### Canonical Release Workflow

```bash
cd ../../../go-review-service
make release-code-review-skill
```

The staged release workflow verifies the canonical bundle against the packaged binaries and staged viewer assets before syncing managed files into `.agents/skills/code-review/`.

### Global Install Smoke

```bash
cd ../../../go-review-service
make install-skill
~/.config/opencode/skills/code-review/scripts/review-cli-linux-amd64 version
```

### Runtime Preflight Smoke

```bash
.agents/skills/code-review/scripts/review-cli-linux-amd64 runtime status . --stage evidence
.agents/skills/code-review/scripts/review-cli-linux-amd64 runtime request . --stage evidence
.agents/skills/code-review/scripts/review-cli-linux-amd64 runtime bootstrap-register . --stage evidence
```

Use `runtime request` as the governed start/reuse authority path for the required bundle. `runtime bootstrap-register` is only for already-ready current-state recovery.

These runtime commands are **raw producer-side inputs only**. Final readiness authority still comes from `review.md`, and `SPECS.md` may only summarize that declared review outcome.

### Report Viewer Executed Evidence

```bash
cd ../../../code-visualization-frontend
npm run test:e2e-viewer
```

Expected executed evidence artifact:

```text
temp/report-viewer-e2e/report-viewer-evidence-summary.json
```

This lane is fixture/static viewer proof only. It is not a runtime-readiness authority.

### Frontend E2E Lane Matrix

See:

```text
docs/review/frontend-e2e-lane-matrix.json
```

Use it to distinguish:

- default frontend Playwright lane
- compose-backed runtime lane
- mock-heavy contract lane
- historical legacy lane
- report-viewer lane
- graph-explorer lane

## Cross-Platform Native Binaries

The published skill now ships the native binary matrix directly:
1. linux amd64 / arm64
2. darwin amd64 / arm64
3. windows amd64 / arm64

Select the matching `review-cli-<os>-<arch>` binary for your host. The canonical `make release-code-review-skill` workflow is the place where this six-platform matrix is built, verified, and published into the skill bundle.

## Usage Examples

### From Skill Directory

```bash
cd .agents/skills/code-review

# Analyze file
scripts/review-cli-linux-amd64 analyze <filepath>

# Improve code
scripts/review-cli-linux-amd64 improve <filepath>

# Generate report
scripts/review-cli-linux-amd64 report <directory>

# Generate bounded ax development context
PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true \
scripts/review-cli-linux-amd64 bounded-context <xpo-file> <object-qualified-method> --layers 1

# Generate generic producer-side handoff
PERSISTENCE_MODE=local-sqlite SQLITE_ENABLED=true \
scripts/review-cli-linux-amd64 developer-routing <artifact-path> [symbol-identity] --layers 1
```

## Environment Requirements

### Database Connections
- Neo4j: bolt://localhost:17687
- PostgreSQL: localhost:15432

### Native bootstrap / Load
- `CODE_REVIEW_GLOBAL_ENV_FILE`
- `~/.env`
- optional sibling `.env` beside the current binary when authoritative global env is unavailable

### Graph/Query Guard

Project-local graph/query surfaces require:

```bash
PERSISTENCE_MODE=local-sqlite
SQLITE_ENABLED=true
```

## Known Constraints

1. Requires database connections for project-local graph/query work
2. `developer-routing` is producer-side only and does not perform downstream workspace-local orchestration
