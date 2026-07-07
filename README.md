# aclab Skills

**aclab's** curated collection of AI agent skills for professional software development workflows.
This is an **agent-agnostic** collection — the skills run on **OpenCode**, **Claude Code**, and
**Codex** (and other compatible runtimes), not just one vendor.

🌐 **Languages:** [English](README.md) · [繁體中文](README.zh-TW.md)

[![CI](https://github.com/austinyuch/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/austinyuch/skills/actions/workflows/ci.yml)

> 🤖 **Using a coding agent?** Read [`AGENTS.md`](AGENTS.md) — it explains how to navigate this
> collection, when to enter the **Spec Master Method**, and the routing/ownership rules the skills expect.

## Quick Start

Install the skills into your coding agent. **Nothing is published to any registry** — every command
below resolves straight from this Git repo. Pick whichever runtime you already have.

`<agent>` = `opencode` | `claude` | `codex` | `kiro` (default: `opencode`).

**Node — npx / bunx (no clone):**
```bash
npx -y github:austinyuch/skills claude
bunx   github:austinyuch/skills codex
```

**Python — uvx / pipx (no clone):**
```bash
uvx --from git+https://github.com/austinyuch/skills aclab-skills claude
pipx run --spec git+https://github.com/austinyuch/skills aclab-skills codex
```

**No Node/Python — clone + run a script (cross-platform):**
```bash
git clone https://github.com/austinyuch/skills.git && cd skills
bash scripts/install.sh claude       # macOS / Linux
pwsh scripts/install.ps1 claude      # Windows PowerShell
```

By default, skills install with the same hierarchical layout as this repo:
`<skill-home>/<category-or-family>/<skill-name>/`. This matches multi-level skill discovery in modern
Codex / Claude / OpenCode environments. For older flat skill homes, pass `--layout flat` (or set
`SKILLS_LAYOUT=flat`) to install as `<skill-home>/<skill-name>/`.

Override the destination anywhere with `SKILLS_TARGET=/custom/path`. (OpenCode users can also use the
community tool: `npx skills@latest add austinyuch/skills` when that tool's layout matches their runtime.)

### Native binaries (GitHub Releases, not in git)

A few skills rely on **prebuilt native binaries / models that are intentionally not committed** here —
they are large and platform-specific, so they are gitignored. This keeps `git clone`, `npx`, and `uvx`
fast and **LFS-free** (no git-lfs dependency, no pointer-stub breakage). They are distributed via
**GitHub Releases, never git LFS.**

- **`code-review`** uses a `review-cli-<os>-<arch>` binary (+ a ~128 MB embedding model). Installing it
  copies the skill's docs/scripts but **not** the binary. Fetch the matching binary with `--with-cli`:

  ```bash
  npx -y github:austinyuch/skills claude --with-cli
  uvx --from git+https://github.com/austinyuch/skills aclab-skills claude --with-cli
  bash scripts/install.sh claude --with-cli       #   macOS / Linux
  pwsh scripts/install.ps1 claude -WithCli         #   Windows
  ```

  The pure-Python review helpers — `code-refactoring-advisor`, `test-quality-reviewer`,
  `security-risk-reviewer`, `test-design-generator` — work as-is with no binary. The model is not
  fetched (the CLI runs graph-only without it).

> 🔐 **This repository is private.** `npx`/`uvx`/`git clone` **and** the `--with-cli` binary download
> all require GitHub authentication. `--with-cli` uses the **`gh` CLI** (`gh auth login`) to pull the
> asset from the [`review-cli-v0.15.0`](https://github.com/austinyuch/skills/releases/tag/review-cli-v0.15.0)
> release; without `gh` it prints the exact `gh release download …` command to run. Anonymous/public
> install is not available unless the repo (or release) is made public.

## What's Inside

| Category | Skills | Description |
|----------|--------|-------------|
| **Spec Master** | 2 | Spec routing and spec-driven development |
| **Code Review** | 6 | Review, quality, security, and testing tools |
| **Scrum** | 2 | Scrum and agile team workflows |
| **Engineering** | 15 | Core software engineering workflows |
| **Architecture** | 15 | Architecture, governance, and process design |
| **DevOps** | 6 | DevOps, containers, and infrastructure |
| **Productivity** | 7 | Productivity, writing, and collaboration |
| **Data** | 4 | Data analysis, BI, and databases |
| **Domain Expert** | 1 | Domain-specific expert knowledge |
| **Creative** | 2 | Frontend, design, and creative tools |
| **Security & Compliance** | 1 | Security review and compliance |
| **Social Media** | 4 | Social media, advocacy, and marketing |
| **Tools** | 1 | Developer tools and integrations |
| **User Experience** | 1 | User profiles, manuals, and interaction |
| **Project Review** | 2 | Project review and executive reporting |
| **UAT & Demo** | 1 | UAT and demo execution tools |

## The Spec Master Method

> **Bring DevSecOps, Scrum, and TDD into agentic workflows — without losing the truth.**
> 把 DevSecOps、Scrum 與 TDD 帶進 agentic 工作流——而且不失真。

Coding agents made *producing* code cheap but not *coordinating* it. The bottleneck moves from
typing to deciding ownership, keeping evidence fresh, and stopping a green-looking file from lying
about readiness. The **Spec Master Method** is an open-source family of **14 composable skills** that
ports five proven engineering practices into a governed, inspectable agentic workflow.

| Classic practice | Job it still does | Owner skill |
|---|---|---|
| Spec-Driven Development (SDD) | Vague intent → traceable delivery | `spec-driven-development` (inspired by [AWS Kiro](https://kiro.dev)) |
| Test-Driven Development (TDD) | Pin behavior before code changes | `tdd-workflow` + `test-design-generator` |
| Domain-Driven Design (DDD) | Align boundaries with business language | SDD Phase 2 (bounded contexts) |
| Test management | Green CI → auditable risk evidence | `test-registry-manager` + `test-quality-reviewer` |
| Refactoring | Lower cost of change after behavior is protected | `code-refactoring-advisor` |

The 14 skills sit in three layers:

- **Govern & route** — `spec-master` (front door), `spec-registry-manager`, `issue-log-manager`, `local-infra-registry-governance`, `shared-governance`
- **Deliver** — `spec-driven-development` (6-phase lifecycle), `tdd-workflow`, `test-registry-manager`, `test-design-generator`
- **Verify (left-shift)** — `code-review`, `code-refactoring-advisor`, `test-quality-reviewer`, `security-risk-reviewer`, `sonarqube-bridge`

The core anti-false-green rule: **evidence flows one way** — `ISSUE_LOG → spec artifacts → folder-level TESTS.md → workspace rollup → RTM.md → SPECS.md` — and derived summaries never sync back into upstream truth.

**Learn more:**
- 🟦 [`methodology.html`](./methodology.html) — bilingual EN/繁中 landing page
- 📖 [`docs/agentic-delivery-methodology.md`](./docs/agentic-delivery-methodology.md) — the full methodology article (bilingual)
- 🗺️ [`docs/methodology-diagram.md`](./docs/methodology-diagram.md) — handoff, evidence-flow, and practice-map diagrams
- Deep dives: [Spec Master + SDD brief](./skills/spec-master/index.html) · [Code Review family brief](./skills/code-review/index.html)

> `spec-driven-development` is inspired by **AWS Kiro**; the YAGNI ladder adapts **Ponytail** (MIT); it builds on **Scrum**, the **Agile Manifesto**, **TDD/DDD**, and more. Full attribution: [`CREDITS.md`](./CREDITS.md).

## Skill Families

### Spec Master
- `spec-master` - Spec routing, governance, and improvement classification (front door)
- `spec-driven-development` - Systematic spec lifecycle: requirements, design, tasks, implementation, review, optimization

### Code Review
- `code-review` - Code review with CLI tools
- `test-quality-reviewer` - Evaluate test effectiveness
- `code-refactoring-advisor` - Detect code smells and suggest refactorings
- `test-design-generator` - Generate concrete test cases
- `security-risk-reviewer` - OWASP security scanning
- `sonarqube-bridge` - SonarQube integration

### Scrum
- `scrum-master-skill` - Scrum Master coordination
- `scrum-developer-skill` - Scrum developer execution

## Skill Categories

### Engineering
- `spec-registry-manager` - Spec catalog management
- `code-review` - Code review with CLI tools
- `code-refactoring-advisor` - Detect code smells and suggest refactorings
- `code-summarizer` - File-level code summarization
- `test-quality-reviewer` - Evaluate test effectiveness
- `test-design-generator` - Generate concrete test cases
- `test-registry-manager` - Test catalog governance
- `tdd-workflow` - Test-driven development
- `verification-loop` - Post-implementation verification
- `eval-harness` - Evaluation framework
- `backend-patterns` - Backend architecture patterns
- `frontend-patterns` - Frontend development patterns
- `coding-standards` - Universal coding standards
- `golang-patterns` - Idiomatic Go patterns
- `golang-testing` - Go testing patterns
- `go-rust-optimizer` - Go performance optimization with Rust
- `node-rust-optimizer` - Node.js performance optimization with Rust
- `python-rust-optimizer` - Python performance optimization with Rust
- `sonarqube-bridge` - SonarQube integration
- `capability-mapper` - Map code to business capabilities

### Architecture
- `agentic-scrum-governance` - Agentic Scrum governance
- `shared-governance` - Shared governance rules
- `committee-decision-making` - Multi-LLM decision making
- `strategic-compact` - Context compaction strategy
- `iterative-retrieval` - Progressive context retrieval
- `epic-breakdown-skill` - Epic decomposition
- `requirements-workflow-skill` - Requirements management workflow
- `workflow-skill-creator` - Workflow skill generator
- `continuous-learning` - Pattern extraction from sessions
- `continuous-learning-v2` - Instinct-based learning
- `skill-migration-workflow` - Skill migration and comparison
- `cross-agents-symlink-bridge` - Cross-agent bridge setup
- `issue-log-manager` - Issue log governance
- `uat-demo-agent` - UAT/Demo plan execution
- `uat-demo-agent-packaging` - Skill packaging
- `uat-demo-target-governance-template` - Governance templates

### DevOps
- `devops-container-orchestration` - Container orchestration patterns
- `podman-rootless` - Podman rootless development
- `k8s-security-patterns` - Kubernetes security
- `local-infra-registry-governance` - Local infrastructure registry
- `container-image-janitor` - Container image cleanup
- `cross-platform-dev-scripts` - Cross-platform development scripts

### Productivity
- `writer-skill` - Professional documentation writing
- `vibe-skill` - Rapid development workflow
- `kiro-skill` - Systematic development workflow
- `pm-skill` - Product management assistant
- `prd-skill` - PRD document generation
- `name-skill` - Programming naming assistant
- `find-skills` - Skill discovery

### Data
- `clickhouse-io` - ClickHouse database patterns
- `postgres-patterns` - PostgreSQL patterns
- `database-modernization-strangler` - Legacy database modernization
- `taiwan-civic-budget-tracker` - Government budget tracking

### Domain Expert
- `microsoft-foundry` - Azure AI Foundry deployment

### Creative
- `ui-skill` - B2B supply chain interactive HTML
- `shadcn` - shadcn/ui component management

### Security & Compliance
- `security-review` - Security review checklist
- `security-risk-reviewer` - OWASP security scanning

### Social Media
- `social-media-platforms` - Social media content optimization
- `social-post-generator` - Social media post generation
- `victim-rights-news-tracker` - News tracking for advocacy
- `brand-guidelines-naelt` - NAELT brand guidelines

> Also shipped: `NPO-marketing-guide.md` (a standalone reference, installed alongside the skills).

### Tools
- `local-llm-agent-migrator` - Local LLM agent migration

### Scrum
- `scrum-master-skill` - Scrum Master coordination
- `scrum-developer-skill` - Scrum developer execution

### User Experience
- `user-manual-skill` - User manual generation

### Project Review
- `project-review-skill` - Executive project review
- `project-review-naelt` - NAELT project review

### UAT & Demo
- `uat-demo-agent` - UAT/Demo plan execution

## Repository Structure

```
.
├── skills/                          # Categorized skills
│   ├── spec-master/                 # Spec Master family
│   │   ├── spec-master/
│   │   └── spec-driven-development/
│   ├── code-review/                 # Code Review family
│   │   ├── code-review/
│   │   ├── test-quality-reviewer/
│   │   ├── code-refactoring-advisor/
│   │   ├── test-design-generator/
│   │   ├── security-risk-reviewer/
│   │   └── sonarqube-bridge/
│   ├── scrum/                       # Scrum family
│   │   ├── scrum-master-skill/
│   │   └── scrum-developer-skill/
│   ├── engineering/
│   ├── architecture/
│   ├── devops/
│   ├── productivity/
│   ├── data/
│   ├── domain-expert/
│   ├── creative/
│   ├── security-compliance/
│   ├── social-media/
│   ├── tools/
│   ├── user-experience/
│   ├── project-review/
│   └── uat-demo/
├── docs/                            # Methodology article + diagrams
│   ├── agentic-delivery-methodology.md
│   └── methodology-diagram.md
├── bin/
│   ├── aclab-skills.mjs             # Node CLI (npx/bunx github:…)
│   └── aclab_skills.py              # Python CLI (uvx/pipx from git)
├── scripts/
│   ├── install.sh                   # Bash installer (opencode|claude|codex|kiro)
│   ├── install.ps1                  # PowerShell installer (Windows)
│   ├── install-git-hooks.sh         # Install DevSecOps pre-commit + pre-push hooks
│   ├── git-hooks/                   # Versioned hook sources (pre-commit, pre-push)
│   ├── render-docs.py               # Generate browsable .html twins from markdown
│   ├── sync-from-source.sh          # Publish from ~/.config/opencode/skills
│   └── install-to-opencode.sh       # Legacy OpenCode-only installer
├── methodology.html                 # The Spec Master Method — landing page (EN/繁中)
├── skills-manifest.json             # Skill catalog and categorization
├── package.json                     # npm metadata + bin (npx/bunx)
├── pyproject.toml                   # Python packaging for uvx/pipx (from git)
├── AGENTS.md                        # Guide for coding agents using this repo
├── CREDITS.md                       # Attribution and upstream licenses
├── README.md                        # This file (English)
├── README.zh-TW.md                  # 繁體中文版
└── LICENSE                          # MIT License
```

## For Authors

### Publishing New Skills

1. Add the skill to `skills-manifest.json` in the appropriate category
2. Place the skill in `~/.config/opencode/skills/<skill-name>/`
3. Run the sync script:

```bash
cd ~/projects/aclab/skills
bash scripts/sync-from-source.sh
git add .
git commit -m "sync: add <skill-name>"
git push origin main
```

### Local Development Setup

```bash
git clone git@github.com:austinyuch/skills.git
cd skills
# Install skills locally for testing
bash scripts/install-to-opencode.sh
```

## Contributing

PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). In short: install the hooks
(`bash scripts/install-git-hooks.sh`), keep the manifest/README/twins in sync, and make sure
`bash scripts/ci-checks.sh` passes (the same checks CI runs). Please follow the
[Code of Conduct](CODE_OF_CONDUCT.md); report security issues per [SECURITY.md](SECURITY.md).

## License & Attribution

This repository is **MIT** — see the root [LICENSE](LICENSE) — **except** the **code-review family**,
which is **Apache-2.0**. Each of these six skills carries its own `LICENSE` + `NOTICE`:

- Apache-2.0: `code-review`, `code-refactoring-advisor`, `test-quality-reviewer`,
  `test-design-generator`, `security-risk-reviewer`, `sonarqube-bridge`
  (the [Code Review System](https://github.com/austinyuch/skills/tree/main/skills/code-review)).
- MIT (root): everything else, including `capability-mapper` and `code-summarizer`.

> **Note:** skills derived from Anthropic's `anthropics/skills` (and the proprietary `docx`/`pdf`/`pptx`/`xlsx`)
> have been **removed** from this collection. The methodology still credits its sources — **AWS Kiro**,
> **Ponytail** (MIT), the **Scrum Guide**, the **Agile Manifesto**, and others — as concept influences,
> not bundled code. Full attribution is in [**CREDITS.md**](CREDITS.md).
