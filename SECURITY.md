# Security Policy

## Reporting a vulnerability

**Please do not open a public issue for security vulnerabilities.**

Report privately via GitHub's **private vulnerability reporting**:
the repository's **Security** tab → **Report a vulnerability**
(<https://github.com/austinyuch/skills/security/advisories/new>).

> Maintainers: enable this under *Settings → Code security and analysis → Private vulnerability
> reporting*. If you prefer email instead, replace this section with a contact address.

Please include:
- a description of the issue and its impact,
- steps to reproduce (or a proof of concept),
- affected skill / file / version.

We aim to acknowledge reports within a few business days and will coordinate a fix and disclosure
timeline with you.

## Scope

This repository is a **collection of agent skills, docs, and installer tooling**. Most relevant to
security:

- **Installer scripts & CLIs** (`bin/`, `scripts/`) — they copy files and, with `--with-cli`, download
  a release binary via `gh`. Report any path-traversal, code-execution, or unsafe-download issues here.
- **Skill content** that instructs an agent to run commands — report prompt-injection or
  unsafe-default concerns.
- **`security-risk-reviewer` / DevSecOps hooks** — false-negative classes that let real issues through.

Native binaries (e.g. `code-review`'s `review-cli`) are built and distributed from their upstream
project; vulnerabilities in the binary itself should be reported to that project.

## Good to know

- This repo runs DevSecOps git hooks (`scripts/git-hooks/`) and CI (`scripts/ci-checks.sh`) that scan
  for secrets, machine-specific paths, and (on push) OWASP-pattern findings in changed source.
- Test fixtures under `evals/` and `test_*` files intentionally contain vulnerable/secret-shaped
  **samples** — those are not live secrets.
