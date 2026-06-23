# OpenCode Skills Collection

A curated collection of AI agent skills for professional software development workflows.

## Quick Start

### Install via npx (recommended)

```bash
npx skills@latest add austinyuch/skills
```

Or install directly to OpenCode:

```bash
git clone https://github.com/austinyuch/skills.git
cd skills
bash scripts/install-to-opencode.sh
```

## What's Inside

| Category | Skills | Description |
|----------|--------|-------------|
| **Spec Master** | 1 | Spec routing and spec-driven development |
| **Code Review** | 6 | Review, quality, security, and testing tools |
| **Scrum** | 2 | Scrum and agile team workflows |
| **Engineering** | 15 | Core software engineering workflows |
| **Architecture** | 16 | Architecture, governance, and process design |
| **DevOps** | 6 | DevOps, containers, and infrastructure |
| **Productivity** | 9 | Productivity, writing, and collaboration |
| **Data** | 5 | Data analysis, BI, and databases |
| **Domain Expert** | 3 | Domain-specific expert knowledge |
| **Creative** | 8 | Frontend, design, and creative tools |
| **Document** | 4 | Document processing and generation |
| **Security & Compliance** | 1 | Security review and compliance |
| **Social Media** | 9 | Social media, advocacy, and marketing |
| **Tools** | 6 | Developer tools and integrations |
| **User Experience** | 2 | User profiles, manuals, and interaction |

## Skill Families

### Spec Master
- `spec-master` - Spec routing, governance, and spec-driven development workflow (merged)

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
- `spec-driven-development` - Systematic development workflow
- `spec-master` - Spec routing and governance
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
- `doc-coauthoring` - Document collaboration workflow
- `internal-comms` - Internal communications
- `vibe-skill` - Rapid development workflow
- `kiro-skill` - Systematic development workflow
- `pm-skill` - Product management assistant
- `prd-skill` - PRD document generation
- `name-skill` - Programming naming assistant
- `find-skills` - Skill discovery

### Data
- `bi-analyst-skill` - Business intelligence analysis
- `clickhouse-io` - ClickHouse database patterns
- `postgres-patterns` - PostgreSQL patterns
- `database-modernization-strangler` - Legacy database modernization
- `taiwan-civic-budget-tracker` - Government budget tracking

### Domain Expert
- `mes-domain-expert-skill` - Manufacturing execution systems
- `aws-agent-solution-architect` - AWS AI agent architecture
- `microsoft-foundry` - Azure AI Foundry deployment

### Creative
- `frontend-design-skill` - Production-grade UI/UX design
- `ui-skill` - B2B supply chain interactive HTML
- `theme-factory` - Artifact theming toolkit
- `algorithmic-art` - Generative algorithmic art
- `canvas-design` - Visual art creation
- `slack-gif-creator` - Slack-optimized GIF creation
- `web-artifacts-builder` - Complex web artifacts
- `shadcn` - shadcn/ui component management

### Document
- `docx` - Word document operations
- `pdf` - PDF operations
- `pptx` - PowerPoint operations
- `xlsx` - Excel spreadsheet operations

### Security & Compliance
- `security-review` - Security review checklist
- `security-risk-reviewer` - OWASP security scanning

### Social Media
- `social-media-platforms` - Social media content optimization
- `social-post-generator` - Social media post generation
- `victim-rights-news-tracker` - News tracking for advocacy
- `brand-guidelines` - Anthropic brand guidelines
- `brand-guidelines-naelt` - NAELT brand guidelines
- `brand-guideline-company` - Company brand guidelines
- `project-review-naelt` - NAELT project review
- `project-review-skill` - Executive project review
- `NPO-marketing-guide` - NPO marketing guide

### Tools
- `mcp-builder` - MCP server development
- `claude-api` - Claude API development
- `local-llm-agent-migrator` - Local LLM agent migration
- `jsm-query-skill` - Jira Service Management queries
- `webapp-testing` - Playwright web app testing
- `skill-creator` - Skill development tool

### Scrum
- `scrum-master-skill` - Scrum Master coordination
- `scrum-developer-skill` - Scrum developer execution

### User Experience
- `user-profile-skill` - User profile management
- `user-manual-skill` - User manual generation

## Repository Structure

```
.
├── skills/                          # Categorized skills
│   ├── spec-master/                 # Spec Master family
│   │   └── spec-master/
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
│   ├── document/
│   ├── security-compliance/
│   ├── social-media/
│   ├── tools/
│   └── user-experience/
├── scripts/
│   ├── sync-from-source.sh          # Publish from ~/.config/opencode/skills
│   └── install-to-opencode.sh       # Install to ~/.config/opencode/skills
├── skills-manifest.json             # Skill catalog and categorization
├── package.json                     # npm metadata
├── README.md                        # This file
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

## License

MIT License - see [LICENSE](LICENSE) file for details.
