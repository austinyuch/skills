# Contributing to aclab Skills

Thanks for your interest! This repo is a collection of **Agent Skills** plus the glue that catalogs,
installs, and documents them. Please read this before opening a PR — the conventions here are enforced
by git hooks **and** CI, so following them keeps your PR green.

## Quick setup

```bash
git clone https://github.com/austinyuch/skills.git
cd skills
bash scripts/install-git-hooks.sh     # installs pre-commit + pre-push DevSecOps hooks
```

Before pushing, run the same checks CI runs:

```bash
bash scripts/ci-checks.sh
```

## The rules CI enforces

1. **Manifest ⇄ filesystem.** Every skill in `skills-manifest.json` must exist on disk, and every
   on-disk skill (a folder with a `SKILL.md`) must be listed. Update the manifest when you add, remove,
   or rename a skill — and keep the README counts/lists in sync.
2. **Markdown-first docs.** Each explanatory page has a canonical `.md` and a **generated** `.html`
   twin. Edit the markdown, then regenerate: `python3 scripts/render-docs.py` and commit the twins.
   Never hand-edit a generated `*.html` twin. See [`docs/README.md`](docs/README.md).
3. **Bilingual landing pages.** `methodology.html` and the family `index.html` pages are EN + 繁中 —
   every `data-en` needs a matching `data-zh`.
4. **No machine-specific paths.** Don't commit absolute paths like `/home/<your-user>/…` in `skills/**`.
   Use `~/…` or a placeholder like `<workspace-root>`. (Generic example users — `user`, `agent`, `ci` —
   are allowed in docs.)
5. **No secrets.** Hardcoded keys/tokens/private-keys are rejected. Test fixtures under `evals/` and
   `test_*` files are exempt (they may contain secret-shaped *samples*).
6. **No large binaries.** Native binaries / models are gitignored and distributed via
   **GitHub Releases**, never committed and never git LFS. See README → *Native binaries*.

## Adding a skill

1. Create `skills/<category>/<skill-name>/SKILL.md` (valid frontmatter: `name`, `description`). The
   `description` is what triggers the skill — be specific about *when to use* and *when not to*.
2. Add the skill to `skills-manifest.json` under the right family/category.
3. Update `README.md` (and `README.zh-TW.md`) lists + counts.
4. If your skill is derived from or inspired by an external source, **credit it in
   [`CREDITS.md`](CREDITS.md)** and include the upstream license in the skill folder.
5. Run `bash scripts/ci-checks.sh`.

## Licensing of contributions

This repo is **MIT** except the **code-review family** (`code-review`, `code-refactoring-advisor`,
`test-quality-reviewer`, `test-design-generator`, `security-risk-reviewer`, `sonarqube-bridge`), which
is **Apache-2.0** (see each skill's `LICENSE`/`NOTICE`). By contributing, you agree your contribution is
licensed under the license of the area you change (MIT for the repo at large, Apache-2.0 for the
code-review family). Don't relicense the Apache-2.0 family.

## Pull requests

- Keep PRs focused; describe what and why.
- Make sure `bash scripts/ci-checks.sh` passes locally.
- The hooks can be bypassed locally (`--no-verify` / `SKIP_HOOKS=1`) but **CI cannot** — fix issues
  rather than bypassing.

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
