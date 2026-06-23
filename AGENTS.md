# AGENTS.md — Guide for coding agents working in this repository

This repo is a **collection of Agent Skills** for coding agents (OpenCode, Claude Code, Codex, Kiro,
and compatible runtimes). It is not an application — it is the skills, their docs, a methodology, and
the glue that catalogs and installs them. Read this before editing.

> 本 repo 是給程式代理人使用的 **Agent Skills 合集**；以下規則同時適用於人類與 agent。

---

## 1. What lives here

| Path | What it is |
|---|---|
| `skills/<category>/<skill>/` | One skill per folder; each has a `SKILL.md` (the contract) plus optional `references/`, `scripts/`, `evals/`, `phases/`, `index.html`. |
| `skills-manifest.json` | The **authoritative catalog**: families, categories, and which skill names belong where. Keep it in sync with the filesystem. |
| `methodology.html` | Bilingual EN/繁中 landing page for **The Spec Master Method**. |
| `docs/` | Methodology article (`agentic-delivery-methodology.md`) and Mermaid diagrams. |
| `CREDITS.md` | Upstream attribution and per-component licenses. |
| `README.md` | Human-facing index. |
| `scripts/` | `sync-from-source.sh` (publish from `~/.config/opencode/skills`) and `install-to-opencode.sh`. |

## 2. The Spec Master Method (use this for non-trivial work)

When a task is a real feature, complex fix, or any spec/governance work, **do not freelance** — enter
the family through its front door. The 14 skills sit in three layers:

- **Govern & route** — `spec-master` (front door + improvement classifier), `spec-registry-manager`,
  `issue-log-manager`, `local-infra-registry-governance`, `shared-governance`
- **Deliver** — `spec-driven-development` (6-phase lifecycle), `tdd-workflow`, `test-registry-manager`,
  `test-design-generator`
- **Verify (left-shift)** — `code-review`, `code-refactoring-advisor`, `test-quality-reviewer`,
  `security-risk-reviewer`, `sonarqube-bridge`

**Routing rule:** route by *authority surface*, not by whichever file was mentioned first.

| The request is about… | Go to |
|---|---|
| New feature / complex fix / design / tasks / review / optimization | `spec-driven-development` |
| `SPECS.md` lifecycle, CR summary, registry wording | `spec-registry-manager` |
| `TESTS.md` rows, stale evidence, traceability | `test-registry-manager` |
| Unresolved improvement with no safe owner yet | `issue-log-manager` |
| Local dev / UAT / E2E runtime allocation | `local-infra-registry-governance` |
| Cross-lane git/worktree ownership & writeback safety | `shared-governance` |
| Owner unclear / "who should own this?" | `spec-master` (it decides, then hands off) |

**The one rule that prevents false-green:** evidence flows **one way** —
`ISSUE_LOG → spec artifacts → folder-level TESTS.md → workspace rollup → RTM.md → SPECS.md`.
Derived summaries (`SPECS.md`, `RTM.md`) must **never** overwrite the upstream artifacts they
summarize, and `review.md` — not a green dashboard — owns the readiness verdict.

Full narrative: [`methodology.html`](methodology.html) · [`docs/agentic-delivery-methodology.md`](docs/agentic-delivery-methodology.md).

## 3. Editing or adding a skill

1. A skill is **self-contained in its own folder**. It may reference *other skills by name* (the
   runtime resolves them from the installed skill homes), but it must not depend on files outside the
   repo or on a contributor's machine-specific paths. Use placeholders like `<workspace-root>` instead
   of absolute paths such as `/home/<user>/...`.
2. Every skill needs a `SKILL.md` with valid frontmatter (`name`, `description`). The `description`
   is what triggers the skill — keep it specific about *when to use* and *when not to*.
3. After adding/removing/renaming a skill, **update `skills-manifest.json`** (the right family/category
   list) and the matching list + counts in `README.md`. Keep the manifest and the filesystem in sync —
   no manifest entry should point at a missing folder, and no installed skill should be absent from the
   manifest.
4. Install paths like `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.kiro/skills/` inside
   skill docs are **intentional** — they are the cross-agent install homes, not broken references.

## 4. Licensing & attribution (do not regress)

- This repository is **MIT** (see `LICENSE`). Keep it that way.
- **Do not re-introduce Anthropic-owned skills.** Skills derived from `anthropics/skills` (Apache-2.0)
  and Anthropic's proprietary `docx`/`pdf`/`pptx`/`xlsx` were **removed** on purpose. If you need that
  functionality, install from upstream separately — do not vendor it back into this MIT repo.
- When you add anything inspired by or derived from an external source, **credit it in `CREDITS.md`**.
  Current concept sources include **AWS Kiro** (spec-driven workflow), **Ponytail** (MIT, YAGNI ladder),
  the **Scrum Guide**, the **Agile Manifesto**, **TDD/DDD**, Martin Fowler, EARS, OWASP, and NIST/OECD/ISO.

## 5. House conventions

- Bilingual artifacts: the family `index.html` pages and `methodology.html` are **EN + 繁中**. If you
  edit them, keep both languages in sync (every `data-en` needs a matching `data-zh`).
- Prefer the dedicated skill for a job over re-deriving it inline — that is the whole point of routing.
- Don't overstate readiness. A change is "done" only when its evidence (tests, `review.md`) says so.

## 6. Quick checks before you commit

- `skills-manifest.json` ⇄ filesystem: no missing folders, no unlisted skills.
- README counts/lists match the manifest.
- No new absolute machine paths (`/home/<user>/...`) introduced into skills.
- New external influences credited in `CREDITS.md`.
- Bilingual HTML still balanced.
