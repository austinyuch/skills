#!/usr/bin/env python3
"""test-quality-reviewer — judge the quality of EXISTING tests (hybrid skill).

Deterministic detectors (offline, the source of truth) flag test smells and FIRST /
test-pyramid violations in a test file; an OPTIONAL --explain pass asks the configured
LLM to calibrate severity and add human-readable reasoning. The deterministic findings
stand alone, so this is safe to run in CI with no provider and no network.

  invocation : python3 run.py '<json>'        (also accepts the JSON on stdin)
  input JSON : {"file": "<path>"}  (optionally {"content": "..."} to skip disk read)
  output JSON: {"skill_version","target","language","explained","summary","findings":[...]}

Detected rules (Clean-Code-for-tests + FIRST + pyramid):
  NO_ASSERTION            a test body with zero assertions (FIRST: not Self-validating)
  ASSERTION_ROULETTE      many unlabeled assertions in one test — failures are ambiguous
  MYSTERY_GUEST           hidden dependency on an external file / URL / DB (not Repeatable)
  CONDITIONAL_TEST_LOGIC  branching/looping inside a test — hidden, data-dependent asserts
  FRAGILE_ASSERTION       equality against a long/brittle literal — breaks on cosmetic change
  PYRAMID_INVERSION       a *unit* test reaches for E2E/integration machinery (ice-cream cone)
  BOUNDARY_SIGNAL_WEAK    a range/validation-named test with a single assertion (likely no edges)

Exit: 0 with findings JSON on success (empty findings is a valid PASS). Non-zero only on
bad input, or when --explain was requested but the provider failed (honest, never faked).
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_provider import ProviderError, explain, parse_json_block  # noqa: E402

SKILL_VERSION = "test-quality-reviewer/1.0"
MAX_CONTENT_BYTES = 64 * 1024

SEVERITY = {
    "NO_ASSERTION": "high",
    "MYSTERY_GUEST": "high",
    "ASSERTION_ROULETTE": "medium",
    "CONDITIONAL_TEST_LOGIC": "medium",
    "FRAGILE_ASSERTION": "medium",
    "PYRAMID_INVERSION": "medium",
    "BOUNDARY_SIGNAL_WEAK": "low",
}

# Per-language signals.
LANG = {
    "go": {
        "ext": (".go",),
        "decl": re.compile(r"^\s*func\s+(Test|Benchmark|Example|Fuzz)\w*\s*\("),
        "assert": re.compile(r"\bt\.(Error|Errorf|Fatal|Fatalf|Fail|FailNow)\b|\b(require|assert)\.\w+|\bt\.Run\("),
        "cond": re.compile(r"^\s*switch\b"),  # if-err / for-range are idiomatic in Go
    },
    "python": {
        "ext": (".py",),
        "decl": re.compile(r"^\s*def\s+test_?\w*\s*\("),
        "assert": re.compile(r"^\s*assert\b|\bself\.assert\w+|\bpytest\.raises\b|\bself\.fail\(|\bnp\.testing\.assert"),
        "cond": re.compile(r"^\s*(if|elif|for|while)\b"),
    },
    "ts": {
        "ext": (".ts", ".tsx", ".js", ".jsx", ".mjs"),
        "decl": re.compile(r"\b(it|test)\s*\(\s*[\"'`]"),
        "assert": re.compile(r"\bexpect\s*\(|\bassert\b|\.should\b|\btoEqual\b|\btoBe\b"),
        "cond": re.compile(r"^\s*(if|for|while|switch)\b"),
    },
    "csharp": {
        "ext": (".cs",),
        # A test block starts at its xUnit/NUnit/MSTest attribute and runs to the next one.
        "decl": re.compile(r"^\s*\[(?:Fact|Theory|Test|TestMethod|TestCase|DataTestMethod)\b"),
        "assert": re.compile(r"\bAssert\.\w+|\.Should\(\)|\bShould\w*\(|\bAssert\b"),
        "cond": re.compile(r"^\s*(if|for|foreach|while|switch)\b"),
    },
}

MYSTERY = re.compile(r"""(/home/|/Users/|/etc/|/var/|/tmp/[\w./-]+|[A-Za-z]:\\\\|https?://|mongodb://|postgres://|mysql://|redis://|jdbc:)""")
# A locator (path/URL/DSN) is only a Mystery Guest if the test READS it at runtime. Require a real
# I/O CALL somewhere in the same test body (block-level, so a locator assigned on one line and read
# on the next still counts), so a path/URL passed as INPUT to the code under test (`parse("https://x")`)
# or named in a comment is not mistaken for a hidden external dependency. Verbs are matched in CALL
# form (`open(`) or as a known I/O library member, so a bare identifier `open`/`read` or a generic
# `obj.get(...)` does not over-match. [CR-2026-07-05-078]
IO_CALL = re.compile(
    r"\b(?:open|urlopen|fetch|glob|walk|Open|ReadFile|ReadAll|WriteFile|ReadDir|readFile|"
    r"readFileSync|createReadStream|Dial|NewRequest|Exec|ExecContext|Query|QueryContext)\s*\("
    r"|\.(?:read|read_text|read_bytes|readFile|readFileSync|ReadFile|ReadAll)\s*\("
    r"|\brequests?\.(?:get|post|put|patch|delete|head|request|session)\s*\("
    r"|\b(?:urllib\.request|httptest\.NewServer|sql\.Open|pgxpool|http\.Get|http\.Post|axios\.(?:get|post))\s*\(",
    re.I)
_ASSIGN = re.compile(r"^\s*(?:const |let |var |final |auto )?([A-Za-z_]\w*)\s*(?::=|=)(?!=)")
_STRING_SPAN = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`[^`]*`')
_COMMENT_MARK = {"python": "#", "go": "//", "ts": "//", "csharp": "//"}


def _strip_comment(line, language):
    """Drop a trailing line comment (per-language marker) WITHOUT cutting inside a string, so a
    locator that appears only in a comment is not treated as a runtime dependency. Strings are
    blanked first, so a `//` inside `http://…` or a `#` inside a quoted value is never a comment."""
    mark = _COMMENT_MARK.get(language)
    if not mark:
        return line
    idx = _STRING_SPAN.sub('""', line).find(mark)
    return line if idx == -1 else line[:idx]


def _mystery_offset(body, language):
    """Body offset of a Mystery-Guest locator line, else None. A path/URL/DSN is a hidden dependency
    only when the test READS it: either the locator and an I/O call are on the SAME line, or the
    locator is assigned to a variable a later I/O call reads (`path := "/x"` … `os.ReadFile(path)`).
    A locator merely passed as INPUT to the code under test — no I/O on it — is not a Mystery Guest,
    which is why block-wide 'any I/O + any locator' would over-flag. Dep hidden in a helper or via
    env is a known limit (needs dataflow the heuristic lacks)."""
    assigned = {}  # var -> offset of the line that assigns it a locator-bearing string
    for off, ln in enumerate(body):
        code = _strip_comment(ln, language)
        if not MYSTERY.search(code):
            continue
        if IO_CALL.search(code):
            return off
        m = _ASSIGN.match(ln)
        if m:
            assigned[m.group(1)] = off
    for ln in body:
        code = _strip_comment(ln, language)
        if IO_CALL.search(code):
            for var, voff in assigned.items():
                if re.search(r"\b" + re.escape(var) + r"\b", code):
                    return voff
    return None
# E2E / integration machinery that should not appear in a *unit* test.
E2E = re.compile(r"\b(playwright|selenium|webdriver|cypress|puppeteer|page\.goto|browser\.new|chromedriver)\b", re.I)
INTEG = re.compile(r"\b(httptest\.NewServer|sql\.Open|pgxpool|docker|podman|testcontainers|amqp|net\.Dial|\.Listen\()\b", re.I)
LONG_STR = re.compile(r"""(['"])(?:\\.|(?!\1).){80,}\1""")
RANGE_NAME = re.compile(r"(valid|invalid|range|limit|boundary|min|max|edge|negativ|overflow)", re.I)


def fail(msg, code=2):
    print(f"test-quality-reviewer: {msg}", file=sys.stderr)
    sys.exit(code)


def read_input(argv):
    args = [a for a in argv[1:] if a not in ("--mock", "--explain")]
    raw = args[0] if args else (sys.stdin.read() if not sys.stdin.isatty() else None)
    if not raw:
        fail("no input JSON provided (argv[1] or stdin)")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"invalid input JSON: {e}")
    if not isinstance(data, dict) or not data.get("file"):
        fail("input JSON must be an object with a non-empty 'file' field")
    return str(data["file"]), data.get("content")


def detect_language(path):
    low = path.lower()
    for name, spec in LANG.items():
        if low.endswith(spec["ext"]):
            return name
    return "unknown"


def looks_like_test(path, content):
    low = path.lower()
    return ("test" in low or "spec" in low or "_test." in low
            or "describe(" in content or "def test" in content or "func Test" in content)


def find_blocks(lines, spec):
    """Return [(start_idx, end_idx_exclusive, decl_line)] for each test in the file."""
    starts = [i for i, ln in enumerate(lines) if spec["decl"].search(ln)]
    blocks = []
    for n, s in enumerate(starts):
        e = starts[n + 1] if n + 1 < len(starts) else len(lines)
        blocks.append((s, e, lines[s].strip()))
    return blocks


def add(findings, rule, path, line, evidence, reasoning, remediation, confidence):
    findings.append({
        "rule": rule, "title": rule.replace("_", " ").title(),
        "file": path, "line": line, "severity": SEVERITY[rule],
        "confidence": round(confidence, 2), "evidence": evidence[:200],
        "reasoning": reasoning, "remediation": remediation,
    })


def detect(path, content, language):
    findings = []
    lines = content.splitlines()
    spec = LANG.get(language)

    # File-level pyramid check: a unit-named test that drags in E2E/integration machinery.
    is_unit = ("e2e" not in path.lower() and "integration" not in path.lower()
               and "/it/" not in path.lower())
    if is_unit:
        for i, ln in enumerate(lines):
            if E2E.search(ln):
                add(findings, "PYRAMID_INVERSION", path, i + 1, ln.strip(),
                    "A unit-layer test reaches for browser/E2E machinery; this belongs in the slow, "
                    "brittle E2E tier. Logic provable at the unit layer should not pay E2E cost.",
                    "Move to an e2e/ suite, or replace the browser drive with a direct unit assertion.",
                    0.7)
                break

    if spec is None:
        return findings  # unknown language: only the file-level pyramid heuristic applies

    for s, e, decl in find_blocks(lines, spec):
        body = lines[s:e]
        body_text = "\n".join(body)
        asserts = sum(1 for ln in body if spec["assert"].search(ln))

        if asserts == 0:
            add(findings, "NO_ASSERTION", path, s + 1, decl,
                "This test body contains no assertion — it can only fail on a panic/exception, so it "
                "is not Self-validating (FIRST). A mutant in the code under test would survive it.",
                "Add an explicit assertion on the observable outcome, or delete the test.", 0.9)

        if asserts >= 6:
            labeled = sum(1 for ln in body if spec["assert"].search(ln) and ("," in ln and ("\"" in ln or "msg" in ln.lower() or "t.Run(" in ln)))
            if labeled < asserts // 2:
                add(findings, "ASSERTION_ROULETTE", path, s + 1, decl,
                    f"{asserts} assertions in one test with few/no failure labels — when it breaks you "
                    "cannot tell which check failed (Assertion Roulette).",
                    "Split into focused tests / subtests (t.Run / it blocks), or add failure messages.", 0.6)

        moff = _mystery_offset(body, language)
        if moff is not None:
            add(findings, "MYSTERY_GUEST", path, s + moff + 1, body[moff].strip(),
                "The test depends on an external file/URL/DB not created in its own setup — it is "
                "not Repeatable and fails on another machine or offline (Mystery Guest).",
                "Use a temp dir / in-memory fixture / mock; construct inputs inside the test.", 0.75)

        cond_hits = [(off, ln) for off, ln in enumerate(body[1:], start=1) if spec["cond"].search(ln)]
        if cond_hits:
            off, ln = cond_hits[0]
            add(findings, "CONDITIONAL_TEST_LOGIC", path, s + off + 1, ln.strip(),
                "Branching/looping inside a test makes its assertions data-dependent and can hide an "
                "untested path; a passing run may never reach the real check.",
                "Use table-driven cases / parametrize so each case is its own explicit assertion.",
                0.55 if language == "go" else 0.6)

        # Only an ASSERTION against a long literal is fragile — a long INPUT/fixture string on a
        # non-assert line (e.g. `blob = "…80 chars…"`) is not. The literal is on the assert line, or
        # wraps onto the next line of a CONTINUED assert (prev line ends with `(`/`==`/`\`/`+`) — an
        # unrelated preceding assert that already ended does not count. [CR-2026-07-05-078]
        for off, ln in enumerate(body):
            m = LONG_STR.search(ln)
            if not m:
                continue
            here = spec["assert"].search(ln)
            prev_cont = (off >= 1 and spec["assert"].search(body[off - 1])
                         and body[off - 1].rstrip().endswith(("(", "==", "\\", "+")))
            if here or prev_cont:
                add(findings, "FRAGILE_ASSERTION", path, s + off + 1, m.group(0)[:60] + "…",
                    "Asserting against a long literal string couples the test to cosmetic output; a "
                    "harmless formatting change breaks it (Fragile Test).",
                    "Assert on parsed/structured fields or a stable subset, not the whole rendered blob.", 0.5)
                break

        if RANGE_NAME.search(decl) and asserts == 1:
            add(findings, "BOUNDARY_SIGNAL_WEAK", path, s + 1, decl,
                "A range/validation-named test with a single assertion likely checks one happy value "
                "and omits boundary/negative cases (no 17/18/19, 64/65/66-style edges).",
                "Apply boundary-value analysis and equivalence partitioning; add the just-in/just-out cases.",
                0.45)

    return findings


# --------------------------------------------------------------------- explain (opt-in)

def build_explain_prompt(path, language, findings, content):
    snippet = content[:8000]
    items = [{"rule": f["rule"], "line": f["line"], "evidence": f["evidence"]} for f in findings]
    return (
        "You are a senior test engineer reviewing test quality. For each finding below, return a "
        "calibrated severity (high|medium|low) and one concrete sentence of reasoning a developer can "
        "act on. Consider the test's real risk (does a mutant survive? is it brittle/flaky?). Return "
        'ONLY JSON: {"findings":[{"rule":str,"line":int,"severity":str,"reasoning":str}]}.\n\n'
        f"File: {path} (language: {language})\nFindings: {json.dumps(items)}\n\nTest source:\n```\n{snippet}\n```\n"
    )


def apply_explanation(findings, text):
    obj = parse_json_block(text)
    by_key = {(str(f.get("rule")), int(f.get("line", -1))): f for f in obj.get("findings", []) if isinstance(f, dict)}
    for f in findings:
        upd = by_key.get((f["rule"], f["line"]))
        if upd:
            if upd.get("severity") in ("high", "medium", "low"):
                f["severity"] = upd["severity"]
            if upd.get("reasoning"):
                f["reasoning"] = str(upd["reasoning"])
    return findings


def summarize(findings):
    by_sev, by_rule = {"high": 0, "medium": 0, "low": 0}, {}
    for f in findings:
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
        by_rule[f["rule"]] = by_rule.get(f["rule"], 0) + 1
    return {"total": len(findings), "by_severity": by_sev, "by_rule": by_rule}


def main():
    argv = sys.argv
    path, content = read_input(argv)
    mock = os.environ.get("TEST_QUALITY_REVIEWER_MOCK") == "1" or "--mock" in argv[1:]
    want_explain = "--explain" in argv[1:] or os.environ.get("TEST_QUALITY_REVIEWER_EXPLAIN") == "1"

    if content is None:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read(MAX_CONTENT_BYTES)
        except OSError as e:
            fail(f"cannot read target file {path!r}: {e}")

    language = detect_language(path)
    findings = detect(path, content, language)

    explained = False
    if findings and (want_explain or mock):
        if mock:
            for f in findings:
                f["reasoning"] = "MOCK: " + f["reasoning"]
            explained = True
        else:
            try:
                findings = apply_explanation(findings, explain(build_explain_prompt(path, language, findings, content)))
                explained = True
            except ProviderError as e:
                if want_explain and not mock:
                    fail(f"--explain requested but provider failed: {e}")

    out = {
        "skill_version": SKILL_VERSION + ("-mock" if mock else ""),
        "target": path, "language": language, "explained": explained,
        "summary": summarize(findings), "findings": findings,
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
