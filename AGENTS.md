# AGENTS.md — Guide for coding agents working in this repository

This is **aclab's collection of Agent Skills** for coding agents (OpenCode, Claude Code, Codex, Kiro,
and compatible runtimes). It is not an application — it is the skills, their docs, a methodology, and
the glue that catalogs and installs them. It is **agent-agnostic**: install with
`scripts/install.sh <opencode|claude|codex|kiro>`. Read this before editing.

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

- Also credit external sources that informed concrete skills: **everything-claude-code** (MIT, the
  `continuous-learning` skills), **gstack** (MIT), **mattpocock/skills** (MIT). Giant-proprietary
  assets and Anthropic skills have also been purged from git history — do not re-add them.
- **Native binaries / models are gitignored, never git LFS.** `code-review` needs `review-cli-<os>-<arch>`
  binaries (built from the upstream **aclab-code-review** Go `go-review-service`, published via its
  `code-review-publish` flow) and a ~128 MB embedding model. They are intentionally **not** committed
  (`.gitignore`: `review-cli-*`, `*.onnx`, `uatdemo-*`), so a clone/`npx`/`uvx` install ships the skill
  without them. Distribute such binaries out-of-band (GitHub Releases), not via LFS — LFS would break
  the no-dependency `git clone`/`npx`/`uvx` install flow.

## 5. House conventions

- **Markdown-first.** Each explanatory landing page has a canonical `README.md`/`.md` source and a
  **generated** `index.html`/`.html`. Edit the markdown first, then regenerate the HTML. The
  source↔rendered map and the rule live in [`docs/README.md`](docs/README.md).
- **Bilingual HTML.** The family `index.html` pages and `methodology.html` are **EN + 繁中**. Keep both
  languages in sync (every `data-en` needs a matching `data-zh`).
- **One brief per family.** `spec-master` + `spec-driven-development` share **one** merged brief at
  `skills/spec-master/` — do not split them into separate landing pages again. The code-review family
  has its single brief at `skills/code-review/`.
- Prefer the dedicated skill for a job over re-deriving it inline — that is the whole point of routing.
- Don't overstate readiness. A change is "done" only when its evidence (tests, `review.md`) says so.

## 6. DevSecOps git hooks (run them)

This repo ships versioned hooks in `scripts/git-hooks/`. Install once after cloning:

```bash
bash scripts/install-git-hooks.sh      # copies pre-commit + pre-push into .git/hooks
```

- **pre-commit** (fast, staged files): secret scan, absolute-machine-path scan under `skills/**`,
  purged-skill denylist, JSON validity, conflict markers, `bash -n` / `py_compile`, bilingual-HTML
  balance, and markdown→HTML twin freshness.
- **pre-push** (push range): `security-risk-reviewer` scan of changed source (fails on high
  severity), full manifest⇄filesystem consistency, and relative-link checks.
- Bypass when you must: `git commit --no-verify` / `git push --no-verify`, or `SKIP_HOOKS=1`.

The same checks are the manual pre-commit checklist: manifest ⇄ filesystem in sync, README counts
match the manifest, no `/home/<user>/...` paths in skills, external influences credited in
`CREDITS.md`, bilingual HTML balanced, and doc twins regenerated (`python3 scripts/render-docs.py`).
