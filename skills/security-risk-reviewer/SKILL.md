---
name: security-risk-reviewer
description: Scan a source file for OWASP Top-10 security patterns and rank findings by risk so review effort goes to the highest-impact issues first. Use during security-conscious code review, when asked "is this secure / any vulnerabilities / injection risk / secrets in here", or as the security pass of a code review. Flags hardcoded secrets, SQL/command injection, XSS, weak crypto, insecure deserialization, disabled TLS verification, and path traversal, each mapped to OWASP/CWE. Orchestrated by the code-review skill; it is the concrete detector behind the skill's prose security guidance.
---

# security-risk-reviewer

## Overview

A hybrid reviewer skill: a **deterministic scanner** flags common OWASP Top-10 patterns
offline and ranks them by **risk score** (severity × confidence × blast radius) so a reviewer
triages the dangerous findings first — directly answering the article's risk-based point
(*what to review is judgement, not generation*). An OPTIONAL `--explain` pass judges
exploitability (security regex is noisy) and tightens remediation.

It makes the `code-review` skill's existing prose security guidance (Spec #42
REQ-CRQAQC-003) executable: prose said "look for SQL injection / hardcoded secrets"; this
skill actually finds the lines and prioritizes them.

## Contract

Invocation: `python3 scripts/run.py '<json>'` (also accepts JSON on stdin).

Input:
```json
{"file": "internal/api/handler.go"}
```
Optional: `content` (skip disk read), `blast_radius` (a number, e.g. from the code graph's
impact analysis — amplifies the risk score of findings in widely-depended-on files).

Output (stdout): `summary` (counts + `max_risk_score`), `risk_ranking` (findings ordered by
`risk_score`, highest first — your triage list), and `findings[]` where each carries `owasp`,
`cwe`, `severity`, `confidence`, `risk_score`, `evidence`, `remediation`. Empty findings is a
valid PASS; exit is non-zero only on bad input or a forced `--explain` provider failure.

### Patterns detected

| Rule | OWASP / CWE | Severity |
|------|-------------|----------|
| `HARDCODED_SECRET` | A07 / CWE-798 | high |
| `SQL_INJECTION` | A03 / CWE-89 | high |
| `COMMAND_INJECTION` | A03 / CWE-78 | high |
| `INSECURE_DESERIALIZE` | A08 / CWE-502 | high |
| `DISABLED_TLS_VERIFY` | A05 / CWE-295 | high |
| `SSRF` | A10 / CWE-918 | medium |
| `XSS` | A03 / CWE-79 | medium |
| `WEAK_CRYPTO` | A02 / CWE-327 | medium |
| `PATH_TRAVERSAL` | A01 / CWE-22 | medium |

Pattern rationale + remediations: [references/owasp-patterns.md](references/owasp-patterns.md).

**Languages:** patterns cover Python, JavaScript/TypeScript, C#, and Go idioms (e.g.
`Process.Start`/`BinaryFormatter`/`MD5.Create` for .NET, `child_process.exec`/`axios` for
JS, `exec.Command`/`InsecureSkipVerify` for Go). Secret/TLS/SQL rules are largely
language-agnostic.

## Risk-based prioritization

The `risk_ranking` is the deliverable that matters: don't review every finding equally.
Start at the top (highest `risk_score`). Pass `blast_radius` from the code graph
(`impact` / `developer-routing`) so a secret in a core, widely-imported file outranks the same
secret in a leaf script.

## Honesty about false positives

Security regex over-matches by design (better to over-flag than miss). The lower-confidence
rules — `SQL_INJECTION`, `PATH_TRAVERSAL`, `WEAK_CRYPTO`, the generic secret pattern — should
be confirmed with `--explain` or a human before reporting as real. The high-confidence rules
(`AKIA…` keys, PEM blocks, `verify=False`) are reliable.

This precision boundary is an **executable contract**, not just prose: `scripts/test_run.py`
ships a `TestPrecisionGuards` suite of benign-but-vuln-shaped inputs each noisy rule must **not**
flag (parameterized SQL, ORM queries, placeholder/`${…}`/env-ref secrets, a bare `verify = False`
a constant `filepath.Join`, `md5` named only in a comment), a paired `TestRecallHeld` suite proving
the real vuln variants still fire, and `TestAcceptedOverflags` which locks the context-dependent
over-flags (e.g. `Math.random()`, a bare `verify = False`) at **low/known confidence** so they
can't silently become alert-fatigue. The one recall-safe refiner: the generic secret rule skips
**non-literal** values only — templates/refs (`${…}`, `{{…}}`, `<…>`, env refs) and a curated
instructional-placeholder set (`changeme`, `your-api-key-here`, `xxxxxx`). It deliberately still
flags weak/**default** credentials (a password field containing the literal `"password"`,
`"admin"`, `"0000…"`) and any
entropy-bearing value (`your-prod-key-9f3a7c2b`) — a cross-family security review (CR-076) showed
dropping those was a real recall loss, not noise reduction. [CR-076] This skill is a triage aid, **not a
SAST replacement** — **SonarQube is the authoritative SAST + quality gate**; this skill is the
fast shift-left pre-flight that catches the obvious before the gate. Pull the authoritative
findings via the `sonarqube-bridge` skill.

The rule set is a **floor, not a ceiling**: it guarantees the known classes are never missed,
but it is finite. Do not stop at the detector output — also apply judgement for issues outside
the rules (business-logic flaws, auth bypass, novel sinks). Treat zero findings as "no *known
pattern* matched", not "secure". The scanner is **line-based**, so it will not follow data flow
across lines (e.g. `flag = False` then `verify=flag`), non-literal falsey values (`verify=0`), or a
call whose risky argument is split across lines — apply judgement for those. `--explain` (LLM) and
SonarQube (authoritative SAST) cover what a per-line regex structurally cannot.

## Optional LLM explanation, mock mode, install, testing

`--explain` (or `SECURITY_RISK_REVIEWER_EXPLAIN=1`) adds a true-positive/exploitability
judgement via `CODE_REVIEW_LLM_*` (Bedrock-first; fails closed if forced and
unconfigured). `SECURITY_RISK_REVIEWER_MOCK=1` (or `--mock`) gives labelled offline output.
Install with `scripts/install.sh` (self-naming). Test with `python3 scripts/test_run.py`
(stdlib, no network).
