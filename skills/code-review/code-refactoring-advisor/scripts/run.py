#!/usr/bin/env python3
"""code-refactoring-advisor — detect code smells and name the refactoring (hybrid skill).

Deterministic detectors (offline, source of truth) find Fowler-style code smells in a
source file and map each to a named refactoring move PLUS the test safety-net it requires
first (Fowler's precondition: refactor only under a trustworthy test). An OPTIONAL
--explain pass calibrates severity and reasoning. Pairs with test-quality-reviewer: this
proposes the change, that one checks the net you refactor against.

  invocation : python3 run.py '<json>'        (also accepts the JSON on stdin)
  input JSON : {"file": "<path>"}  (optional {"content": "..."}; optional {"thresholds": {...}})
  output JSON: {"skill_version","target","language","explained","summary","findings":[...]}

Each finding adds a `refactoring` field (the named Fowler move), a `safety_net` field
(what test must exist before the move is safe), and a `minimality_check` field that applies
the Ponytail/YAGNI ladder before recommending new abstractions. Exit non-zero only on bad
input or a forced --explain provider failure; an empty findings list is a valid PASS.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_provider import ProviderError, explain, parse_json_block  # noqa: E402

SKILL_VERSION = "code-refactoring-advisor/1.0"
MAX_CONTENT_BYTES = 256 * 1024

DEFAULTS = {"long_method": 60, "long_params": 5, "deep_nesting": 4,
            "god_file_lines": 600, "god_file_funcs": 25, "magic_numbers": 6, "bool_ops": 4}

SEVERITY = {
    "LONG_METHOD": "medium", "LONG_PARAMETER_LIST": "medium", "DEEP_NESTING": "medium",
    "GOD_FILE": "medium", "DUPLICATED_BLOCK": "high", "MAGIC_NUMBER": "low",
    "COMPLEX_CONDITION": "medium",
}
# smell -> (named Fowler refactoring, required test safety-net)
MOVE = {
    "LONG_METHOD": ("Extract Function", "characterization test on the method's current output before extracting"),
    "LONG_PARAMETER_LIST": ("Introduce Parameter Object / Preserve Whole Object", "a test pinning each current call site's behaviour"),
    "DEEP_NESTING": ("Replace Nested Conditional with Guard Clauses", "branch-covering tests for each path before flattening"),
    "GOD_FILE": ("Extract Class / Move Function", "tests around the responsibilities being split out"),
    "DUPLICATED_BLOCK": ("Extract Function and call it from both sites", "a test covering both duplicate sites so they cannot drift"),
    "MAGIC_NUMBER": ("Replace Magic Literal with Named Constant", "none beyond the existing suite — mechanically safe"),
    "COMPLEX_CONDITION": ("Decompose Conditional (extract an intention-named boolean)", "tests for each truth combination of the condition"),
}
MINIMALITY = {
    "LONG_METHOD": {
        "phase": "Phase 4 Implementation",
        "question": "Before extracting, is this a cohesive responsibility boundary or just a local readability cleanup?",
        "guidance": "Prefer a small private helper only when it names a real subtask reused or tested independently; otherwise keep the simplest local structure.",
    },
    "LONG_PARAMETER_LIST": {
        "phase": "Phase 4 Implementation",
        "question": "Do these parameters travel together as one concept, or would a parameter object be a new type with no policy boundary?",
        "guidance": "Use an existing domain/stdlib/platform type first; introduce a new object only for a real value boundary, lifecycle, or shared call-site contract.",
    },
    "DEEP_NESTING": {
        "phase": "Phase 4 Implementation",
        "question": "Can guard clauses or early returns flatten the code without adding a new abstraction?",
        "guidance": "Prefer local control-flow simplification before extracting strategy objects or handlers.",
    },
    "GOD_FILE": {
        "phase": "Phase 2 Design / Phase 4 Implementation",
        "question": "Does the split follow real responsibilities and blast-radius evidence, or is it just file-size driven?",
        "guidance": "Use code-review graph-only impact evidence when available; create only the minimum module/class split that isolates a real responsibility.",
    },
    "DUPLICATED_BLOCK": {
        "phase": "Phase 4 Implementation",
        "question": "Is this duplicate behavior stable enough to share, or would extraction create premature coupling?",
        "guidance": "Extract only when both sites share intent; otherwise tolerate short duplication until the policy boundary is clear.",
    },
    "MAGIC_NUMBER": {
        "phase": "Phase 4 Implementation",
        "question": "Would a named constant reveal domain intent better than the literal itself?",
        "guidance": "Use a local const when it names policy; avoid broad config/env plumbing for a value that is not runtime policy.",
    },
    "COMPLEX_CONDITION": {
        "phase": "Phase 4 Implementation",
        "question": "Can a named predicate clarify intent without introducing a new rule engine or strategy layer?",
        "guidance": "Prefer the smallest predicate/helper that names the condition; avoid generalized expression frameworks unless multiple real policies require them.",
    },
}


def minimality_check(rule):
    info = MINIMALITY[rule]
    return {
        "ladder": [
            "Does this need to exist? If no, skip it.",
            "Can the standard library do it? Use it.",
            "Can a native platform feature do it portably? Use it, or isolate OS/arch-specific code behind a small adapter with fallback.",
            "Can an already-installed dependency do it? Use it.",
            "Is it one line? Keep it one line.",
            "Only then build the minimum custom implementation.",
        ],
        "phase": info["phase"],
        "question": info["question"],
        "guidance": info["guidance"],
        "authority": "advisory context; not a Phase 5 review verdict",
        "portability": "architecture/platform agnostic by default; OS/arch-specific native features require an explicit adapter, guard, or fallback",
    }

LANG = {
    "go": {"ext": (".go",), "decl": re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?(\w+)\s*\("), "brace": True},
    "python": {"ext": (".py",), "decl": re.compile(r"^(\s*)def\s+(\w+)\s*\("), "brace": False},
    "ts": {"ext": (".ts", ".tsx", ".js", ".jsx", ".mjs"),
           "decl": re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(|^\s*(?:public|private|protected|static|\s)*\b(\w+)\s*\([^;]*\)\s*[:{]"),
           "brace": True},
    "csharp": {"ext": (".cs",),
               "decl": re.compile(r"^\s*(?:\[[^\]]*\]\s*)*(?:public|private|protected|internal)\s+(?:static\s+|virtual\s+|override\s+|async\s+|sealed\s+)*[\w<>\[\].,\s]+?\b(\w+)\s*\("),
               "brace": True},
}
NUM = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])")
BOOL_OP = re.compile(r"&&|\|\||\band\b|\bor\b")
TRIVIAL_NUMS = {"0", "1", "2", "-1", "100", "1000", "10", "255", "0.0", "1.0"}


def fail(msg, code=2):
    print(f"code-refactoring-advisor: {msg}", file=sys.stderr)
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
    th = dict(DEFAULTS)
    if isinstance(data.get("thresholds"), dict):
        th.update({k: int(v) for k, v in data["thresholds"].items() if k in DEFAULTS})
    return str(data["file"]), data.get("content"), th


def detect_language(path):
    low = path.lower()
    for name, spec in LANG.items():
        if low.endswith(spec["ext"]):
            return name
    return "unknown"


def param_count(decl_and_rest):
    """Count top-level params in the first balanced (...) group."""
    i = decl_and_rest.find("(")
    if i == -1:
        return 0
    depth, commas, seen = 0, 0, False
    for ch in decl_and_rest[i:]:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                break
        elif ch == "," and depth == 1:
            commas += 1
        elif depth == 1 and not ch.isspace():
            seen = True
    return (commas + 1) if seen else 0


def extract_functions(lines, spec):
    """Yield dicts: name, start (0-based decl idx), body (list of lines), sig."""
    funcs = []
    i, n = 0, len(lines)
    while i < n:
        m = spec["decl"].search(lines[i])
        if not m:
            i += 1
            continue
        name = next((g for g in m.groups() if g and g not in (" ",)), "fn")
        if spec["brace"]:
            depth, j, started = 0, i, False
            while j < n:
                depth += lines[j].count("{") - lines[j].count("}")
                if "{" in lines[j]:
                    started = True
                if started and depth <= 0 and j >= i:
                    break
                j += 1
            body = lines[i:j + 1]
            funcs.append({"name": name, "start": i, "body": body, "sig": " ".join(lines[i:i + 3])})
            i = j + 1
        else:  # python: indentation-delimited
            base = len(m.group(1))
            j = i + 1
            while j < n:
                ln = lines[j]
                if ln.strip() and (len(ln) - len(ln.lstrip())) <= base and not ln.lstrip().startswith(("#", '"""', "'''")):
                    break
                j += 1
            body = lines[i:j]
            funcs.append({"name": name, "start": i, "body": body, "sig": " ".join(lines[i:i + 3])})
            i = j
    return funcs


def max_nesting(body, brace):
    depth, mx = 0, 0
    if brace:
        for ln in body:
            depth += ln.count("{") - ln.count("}")
            mx = max(mx, depth)
        return max(mx - 1, 0)  # the function's own brace is depth 1
    indents = [(len(ln) - len(ln.lstrip())) for ln in body if ln.strip()]
    if len(indents) < 2:
        return 0
    unit = min((d for d in indents if d > indents[0]), default=indents[0] + 4) - indents[0] or 4
    return max((max(indents) - indents[0]) // max(unit, 1), 0)


def add(findings, rule, path, line, evidence, reasoning, confidence):
    move, net = MOVE[rule]
    findings.append({
        "rule": rule, "title": rule.replace("_", " ").title(), "file": path, "line": line,
        "severity": SEVERITY[rule], "confidence": round(confidence, 2), "evidence": evidence[:200],
        "reasoning": reasoning, "refactoring": move, "safety_net": net,
        "minimality_check": minimality_check(rule),
    })


def detect(path, content, language, th):
    findings = []
    lines = content.splitlines()
    spec = LANG.get(language)

    if len(lines) > th["god_file_lines"]:
        add(findings, "GOD_FILE", path, 1, f"{len(lines)} lines",
            f"File is {len(lines)} lines (> {th['god_file_lines']}); likely more than one responsibility.", 0.55)

    # Duplicated blocks: windows of 6 normalized, non-trivial lines repeated at distant sites.
    norm = [re.sub(r"\s+", " ", ln.strip()) for ln in lines]
    seen = {}
    W = 6
    for i in range(len(norm) - W):
        win = tuple(norm[i:i + W])
        if sum(1 for x in win if len(x) > 8) < W - 1:
            continue
        key = "".join(win)
        if key in seen and i - seen[key] >= W:
            add(findings, "DUPLICATED_BLOCK", path, i + 1, norm[i][:60],
                f"A {W}-line block is duplicated (first seen at line {seen[key] + 1}); duplicates drift apart and rot.", 0.6)
            seen[key] = i + W  # avoid re-flagging the same run
        elif key not in seen:
            seen[key] = i

    if spec is None:
        return findings

    funcs = extract_functions(lines, spec)
    if len(funcs) > th["god_file_funcs"]:
        add(findings, "GOD_FILE", path, 1, f"{len(funcs)} functions",
            f"{len(funcs)} functions in one file (> {th['god_file_funcs']}); consider splitting by responsibility.", 0.5)

    for fn in funcs:
        ln0 = fn["start"] + 1
        blen = len([b for b in fn["body"] if b.strip()])
        if blen > th["long_method"]:
            add(findings, "LONG_METHOD", path, ln0, fn["sig"].strip(),
                f"`{fn['name']}` is ~{blen} non-blank lines (> {th['long_method']}); hard to read, test, and reuse.", 0.7)
        pc = param_count(fn["sig"])
        if pc > th["long_params"]:
            add(findings, "LONG_PARAMETER_LIST", path, ln0, fn["sig"].strip(),
                f"`{fn['name']}` takes {pc} parameters (> {th['long_params']}); a parameter object clarifies intent.", 0.65)
        nest = max_nesting(fn["body"], spec["brace"])
        if nest > th["deep_nesting"]:
            add(findings, "DEEP_NESTING", path, ln0, fn["sig"].strip(),
                f"`{fn['name']}` nests ~{nest} levels deep (> {th['deep_nesting']}); guard clauses flatten the logic.", 0.6)
        mags = [t for ln in fn["body"] for t in NUM.findall(ln) if t not in TRIVIAL_NUMS]
        if len(mags) > th["magic_numbers"]:
            add(findings, "MAGIC_NUMBER", path, ln0, ", ".join(mags[:6]),
                f"`{fn['name']}` carries {len(mags)} unexplained numeric literals; name them so intent survives.", 0.45)
        for off, ln in enumerate(fn["body"]):
            if len(BOOL_OP.findall(ln)) >= th["bool_ops"]:
                add(findings, "COMPLEX_CONDITION", path, ln0 + off, ln.strip(),
                    "A boolean expression with many operators is hard to read and test; extract a named predicate.", 0.55)
                break
    return findings


def build_explain_prompt(path, language, findings, content):
    items = [{
        "rule": f["rule"],
        "line": f["line"],
        "evidence": f["evidence"],
        "refactoring": f["refactoring"],
        "minimality_question": f["minimality_check"]["question"],
    } for f in findings]
    return (
        "You are a staff engineer reviewing for refactoring. For each smell below, return a calibrated "
        "severity (high|medium|low) and one concrete sentence of reasoning that names the risk and confirms "
        "or adjusts the proposed refactoring. Apply the minimality question before endorsing a new abstraction; "
        "prefer stdlib, portable native platform features, existing dependencies, one-line local code, or the minimum "
        "custom implementation when sufficient. Do not recommend OS/arch-specific code unless it is isolated behind "
        'an explicit adapter, guard, or fallback. Return ONLY JSON: {"findings":[{"rule":str,"line":int,"severity":str,"reasoning":str}]}.\n\n'
        f"File: {path} ({language})\nSmells: {json.dumps(items)}\n\nSource:\n```\n{content[:8000]}\n```\n"
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
    path, content, th = read_input(argv)
    mock = os.environ.get("CODE_REFACTORING_ADVISOR_MOCK") == "1" or "--mock" in argv[1:]
    want_explain = "--explain" in argv[1:] or os.environ.get("CODE_REFACTORING_ADVISOR_EXPLAIN") == "1"
    if content is None:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read(MAX_CONTENT_BYTES)
        except OSError as e:
            fail(f"cannot read target file {path!r}: {e}")
    language = detect_language(path)
    findings = detect(path, content, language, th)
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
    print(json.dumps({
        "skill_version": SKILL_VERSION + ("-mock" if mock else ""), "target": path,
        "language": language, "explained": explained, "summary": summarize(findings), "findings": findings,
    }))


if __name__ == "__main__":
    main()
