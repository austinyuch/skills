# SKILLS — Open-Source Roster & Sync Reference

Authoritative roster of every skill open-sourced into this repo, and the basis for
future syncs from the working skill set.

- **Source of truth (upstream):** `~/.config/opencode/skills/<skill-name>`
- **Target (this repo):** `skills/<category>/<skill-name>`
- **Machine-readable companion:** [`skills-manifest.json`](./skills-manifest.json)
- **Last updated:** 2026-07-03

## Sync conventions

1. **Open-sourcing = copy, not move.** The upstream skill in `~/.config/opencode/skills`
   stays live; a sanitized copy lands in `skills/<category>/`. (No upstream skill has been
   deleted by this process.)
2. **Licensing.** The `code-review` family is **Apache-2.0** (each carries its own `NOTICE`);
   every other skill inherits the repo-root **MIT** `LICENSE`. No per-skill license file is
   added outside the `code-review` family.
3. **Accepted public identifiers.** `aclab` (project family name, appears in `NOTICE`),
   `gstack` and `giant` (brand/example content) are intentionally retained — they already
   ship in previously committed skills. Do **not** strip them during routine sync.
4. **Review-before-distribution flags.** Skills marked ⚠️ below carry host/hardware or
   organization-specific content (GPU host names, NGO identity, local infra topology).
   They are in-repo but should be reviewed before any external redistribution.
5. **When adding a skill:** copy → secret-scan → place under the right category →
   register in `skills-manifest.json` → add a row here.

Legend: ★ = recently added (2026-07-02 / 2026-07-03) · License A2 = Apache-2.0, MIT = repo-root MIT.

---

## architecture
| Skill | License | Notes |
|-------|---------|-------|
| agentic-scrum-governance | MIT | |
| committee-decision-making | MIT | |
| continuous-learning | MIT | |
| continuous-learning-v2 | MIT | |
| cross-agents-symlink-bridge | MIT | |
| epic-breakdown-skill | MIT | |
| issue-log-manager | MIT | |
| iterative-retrieval | MIT | |
| requirements-workflow-skill | MIT | |
| shared-governance | MIT | |
| skill-migration-workflow | MIT | |
| strategic-compact | MIT | |
| system-architect ★ | MIT | contains `gstack`/`giant` brand-example content (accepted) |
| uat-demo-agent-packaging | MIT | |
| uat-demo-target-governance-template | MIT | |
| workflow-skill-creator | MIT | |

## code-review (Apache-2.0 family)
| Skill | License | Notes |
|-------|---------|-------|
| code-review | A2 | core CLI; `NOTICE` names "aclab Code Review family" |
| code-refactoring-advisor | A2 | |
| cross-agent-review ★ | A2 | independent cross-agent / cross-model review orchestration; native `xreview-*` binaries are release artifacts, not committed |
| security-risk-reviewer | A2 | |
| sonarqube-bridge | A2 | |
| test-design-generator | A2 | |
| test-quality-reviewer | A2 | |

## creative
| Skill | License | Notes |
|-------|---------|-------|
| frontend-designer ★ | MIT | design+implement+visual-review orchestrator; contains `gstack`/`giant`/A2UI brand-example content (accepted) |
| shadcn | MIT | |
| ui-skill | MIT | |

## data
| Skill | License | Notes |
|-------|---------|-------|
| clickhouse-io | MIT | |
| database-modernization-strangler | MIT | |
| postgres-patterns | MIT | |
| taiwan-civic-budget-tracker | MIT | |

## devops
| Skill | License | Notes |
|-------|---------|-------|
| container-image-janitor | MIT | |
| cross-platform-dev-scripts | MIT | |
| devops-container-orchestration | MIT | |
| k8s-security-patterns | MIT | |
| local-infra-registry-governance | MIT | ⚠️ host-specific: `GB10` GPU, `local-nemotron`, `giant-aero`, `aclab-middlewares` |
| podman-rootless | MIT | |

## domain-expert
| Skill | License | Notes |
|-------|---------|-------|
| microsoft-foundry | MIT | bundles `models/deploy-model/*` sub-references |

## engineering
| Skill | License | Notes |
|-------|---------|-------|
| backend-patterns | MIT | |
| capability-mapper | MIT | |
| code-summarizer | MIT | |
| coding-standards | MIT | |
| eval-harness | MIT | |
| frontend-patterns | MIT | |
| golang-patterns | MIT | |
| golang-testing | MIT | |
| go-rust-optimizer | MIT | |
| node-rust-optimizer | MIT | |
| python-rust-optimizer | MIT | |
| spec-registry-manager | MIT | |
| tdd-workflow | MIT | |
| test-registry-manager | MIT | |
| verification-loop | MIT | |

## productivity
| Skill | License | Notes |
|-------|---------|-------|
| find-skills | MIT | |
| kiro-skill | MIT | |
| name-skill | MIT | |
| pm-skill | MIT | |
| prd-skill | MIT | |
| vibe-skill | MIT | |
| writer-skill | MIT | |

## project-review
| Skill | License | Notes |
|-------|---------|-------|
| project-review-skill | MIT | contains `gstack`-CEO-perspective example content (accepted) |
| project-review-naelt | MIT | ⚠️ NAELT NGO-specific |

## scrum
| Skill | License | Notes |
|-------|---------|-------|
| scrum-developer-skill | MIT | bundles `references/*` (backend/golang/postgres/tdd/security) |
| scrum-master-skill | MIT | |

## security-compliance
| Skill | License | Notes |
|-------|---------|-------|
| iso-ai-security-auditor ★ | MIT | AI/security/privacy/PII/log compliance inventory aid; not certification or legal advice |
| security-review | MIT | |

## social-media
| Skill | License | Notes |
|-------|---------|-------|
| marketing-showcase-creator ★ | MIT | contains `gstack`-CEO PR/FAQ example content (accepted) |
| social-media-platforms | MIT | |
| social-post-generator | MIT | |
| victim-rights-news-tracker | MIT | ⚠️ NAELT advocacy-specific |
| brand-guidelines-naelt | MIT | ⚠️ NAELT NGO brand (provisional CIS) |

## spec-master (family)
| Skill | License | Notes |
|-------|---------|-------|
| spec-master | MIT | contains `gstack`/`giant` example content (accepted) |
| spec-driven-development | MIT | contains `gstack` example content (accepted) |

## tools
| Skill | License | Notes |
|-------|---------|-------|
| local-llm-agent-migrator | MIT | ⚠️ references `local-nemotron` / `GB10` local model host |

## uat-demo
| Skill | License | Notes |
|-------|---------|-------|
| uat-demo-agent | MIT | ⚠️ references `aclab` project profiles · **dedup:** also copied under `architecture/uat-demo-agent` — consolidate to one canonical location |

## user-experience
| Skill | License | Notes |
|-------|---------|-------|
| user-manual-skill | MIT | |

---

## Known follow-ups
- **Duplicate:** `uat-demo-agent` exists under both `uat-demo/` and `architecture/`. Pick one
  canonical home and update `skills-manifest.json` accordingly.
- **⚠️ environment-coupled skills** (`local-infra-registry-governance`, `local-llm-agent-migrator`,
  `uat-demo-agent`) carry host/hardware topology; sanitize further before any external release.
- **⚠️ NAELT-specific skills** (`project-review-naelt`, `brand-guidelines-naelt`,
  `victim-rights-news-tracker`) are organization-specific rather than general-purpose.
