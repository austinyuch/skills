# Eval — cross-agent-review Localhost (pure-skill) mode

An eval-harness (EDD) check that an agent following ONLY the SKILL.md **Localhost** method produces a
correct independent review. Most cases are **pure-docs and reproducible**: run the exact command the
SKILL.md documents against a seeded repo, then grep the reviewer's text — the steps below ARE the harness
(a maintainer or an agent reproduces them directly). **CAP-8 additionally ships a runnable matrix** —
`scripts/eval-cap8-security.sh` (3 seeded defect classes → drive a peer → grade via **model-grader**
as the authoritative verdict, keyword scan only a pre-filter; exit 0/1/2, or 77 SKIP if no peer / peer
errors, never a silent false-green). Requires a peer CLI on PATH (codex/claude/opencode).

## How to reproduce one case

```sh
mkdir /tmp/ev && cd /tmp/ev && git init -q
printf 'package bank\nfunc Withdraw(b,a int) int { return b - a }\n' > bank.go && git add -A && git commit -qm init
printf 'package bank\nfunc Withdraw(b,a int) int { return b + a }\n' > bank.go   # seed the bug in the worktree
# drive a DIFFERENT-family peer over the diff — CLOSE STDIN (< /dev/null) in any no-tty/automated context:
codex exec "You are an INDEPENDENT code reviewer from a different model family. Review ONLY the diff below for correctness bugs, security issues, and clear quality problems. List findings as '- file:line — issue', most severe first; if nothing material, say 'no material findings'. Do not restate the diff.

$(git diff)" < /dev/null
```
PASS if the review names the add/subtract bug. Swap `codex exec` for `claude -p` / `opencode run` /
`kiro-cli chat` to test the other directions.

> **Gotcha the eval found:** without `< /dev/null`, `codex exec` prints *"Reading additional input from
> stdin…"* and blocks forever in a no-tty context. Always close stdin when driving it headlessly. (The
> `xreview` binary is immune — it passes the prompt as an argv element and leaves the child's stdin on the
> null device; locked by `dispatch.TestExecRunnerChildStdinIsNullNotInherited`.)

## Capability suite

| ID | Seed | PASS criterion | Status |
|----|------|----------------|--------|
| CAP-1 | `Withdraw` returns `b + a` (should subtract) | names the add/subtract bug | **PASS** — pass^3 (3/3, see below) + reverse |
| CAP-2 | `Ping` runs `sh -c "ping "+host` (injection) | flags injection / shell / unsanitized input | **PASS** (codex gave an exploit + fix) |
| CAP-3 | comment/format-only change, no bug | says "no material findings" (no false positive) | **PASS** (false-positive guard held) |
| CAP-4 | nil-pointer deref on an unchecked map/ptr | flags the nil-deref | **PASS** ("`m[k]` can be nil … will panic") |
| CAP-5 | auth check removed | flags the missing authorization | **PASS** ("any non-admin can delete … authorization bypass") |
| CAP-6 | reverse direction: **claude** reviews a codex author's bug | claude names the bug | **PASS** (CR-061 `claude -p`, also caught a comment-downgrade) |
| CAP-7 | only a **same-family** peer is available | discloses "same-family — weaker than cross-family independence" (never a silent self-review) | **PASS** — deterministic doc-grader: SKILL.md + agent def + agent-definitions.md all instruct the disclosure |
| CAP-8 | a script/shell diff with a **security** defect (secret to an arbitrary host, path traversal, injection, fail-open verification) | names the security defect + its failure mode, not just style | **PASS** — RUNNABLE **matrix** `scripts/eval-cap8-security.sh`: 3 defect cases (`leak-traversal`, `command-injection`, `fail-open`) **+ a `clean` false-positive guard** (CR-075: benign diff → must NOT fabricate). Each → peer → **model-grader** verdict; **4/4 PASS** live (codex). Skips loudly (77) with no peer, never a silent false-green. Also caught for real on CR-070..074 diffs |

**Adversarial security lens (CAP-8) — a standing dimension, not a one-off.** Capability evals ask *"does it
find the right bug?"*; they do **not** ask *"what does this code leak, where can it write, what fails open?"* — that
framing has to be prompted explicitly. For any script/IO/credential/release-tooling change, run the peer review
with a security-specific prompt (leak / traversal / injection / fail-open-verification). This is exactly how
CR-070 (Bedrock empty-reply false-green), CR-071 (token leak + traversal) and CR-072 (fail-open partial release)
were all caught — by the peer, after the functional tests were already green.

**Pre-merge dogfood cadence — now a RUNNABLE GATE.** Treat "cross-family review of the actual diff" as a
**required pre-merge step**, not an optional finale. `scripts/pre-merge-dogfood.sh` (CR-074) makes it enforceable:
it runs the CAP-8 matrix (capability gate) **and** drives a peer over `git diff BASE...HEAD` with a strict
BLOCK/ALLOW model-verdict (BLOCK only on a real high-severity finding; a peer-unavailable SKIP warns, never
blocks). Default enforce (non-zero exit → wire as a `pre-push` hook via `scripts/install-pre-push-hook.sh`, which
defaults to fast + non-blocking `--quick --advisory`); `--advisory` warns only, `--quick` skips the slow CAP-8 matrix.
Each of the last FIVE CRs found a real bug this way that seeded evals structurally could not — including a `$tool`
traversal in CR-073's own `verify-bundle.sh` and **three fail-open holes in the gate/eval machinery itself** (CR-074,
the gate BLOCKing its own diff). Cheap (`codex exec` over the diff), high-yield, and it dogfoods the skill on real
code every time.

**Metric:** capability pass@1 = **8/8** (CAP-1..8); **CAP-8 = 4/4** matrix (leak-traversal, command-injection,
fail-open, + `clean` false-positive guard). **CAP-1 pass^3 = 3/3** (all three independent `codex exec` attempts named the bug → reliable, not a
lucky single shot). CAP-3 is the **false-positive guard** (a review that invents findings on a clean diff is worse
than none — must hold). CAP-7 is the **honesty guard** (a same-family review must never masquerade as independent) —
graded deterministically by grepping the shipped instructions, so it can't silently rot.

**Bundle-chain regression tests (CR-073/074).** `scripts/verify-bundle.sh <tool> <dir>` proves the happy round-trip
(emit → install → bytes==source); `scripts/test-bundle-chain.sh <tool> <dir>` adds the **negative** guard — it
tampers a staged artifact and asserts `install-bundle.sh` **rejects** it (checksum mismatch, nothing promoted), so
the fail-closed SHA gate is tested, not assumed. Both proven on the real `review-cli`/`embedding-runner` binaries.

## Grader note (EDD lesson from this suite)

Code-based **regex graders are brittle on open-ended review text**. In the pass^3 run, one attempt wrote
*"increases the balance by amt instead of decreasing it"* — a correct finding a naive `subtract|adds`
pattern scored as a FALSE negative. Worse, a **false-positive guard cannot be regex-graded at all**: a clean
review says *"this is **not** SQL injection"* / *"`passMark` is **not** a magic number"* — the very keyword a
regex would trip on appears, negated. Fixes: (a) synonym-robust patterns for the presence cases
(`add|subtract|increas|decreas|revers|instead of…`); (b) for open-ended and **all negation-sensitive**
cases, a **model-grader** — drive a peer over the review with a yes/no rubric:

```sh
codex exec --skip-git-repo-check "Grade this code review. Did it correctly identify <SEEDED ISSUE> (or, for a
clean-code case, correctly conclude there is NO such issue)? Answer exactly PASS or FAIL, then one reason.

REVIEW:
$(cat review.txt)" < /dev/null
```

This dogfoods cross-agent review *as the grader* and handles negation. Keep deterministic graders only where
there is an exact expected string — CAP-3 (clean="no material findings"), CAP-7 (the disclosure phrase), and the
uat-demo-agent `plan validate` exit code (0=accept / 1=reject).

## When to re-run

After any change to the SKILL.md Localhost method, the reviewer prompt, or the peer-CLI commands — and when
a peer CLI ships a new version (its headless/resume flags can drift). Add a new CAP row for each real bug
class you want the reviewer to reliably catch; keep CAP-3's false-positive guard.
