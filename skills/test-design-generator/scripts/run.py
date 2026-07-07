#!/usr/bin/env python3
"""test-design-generator — turn "test it thoroughly" into concrete cases (hybrid skill).

Deterministic generator (offline, source of truth) applies the classic test-design
techniques — boundary-value analysis, equivalence partitioning, and pairwise combination —
to a structured description of a function's parameters, and recommends an oracle strategy
when outputs cannot be enumerated. An OPTIONAL --explain pass asks the LLM to add semantic /
negative cases a structural generator cannot infer (e.g. injection strings, type confusion).

  invocation : python3 run.py '<json>'        (also accepts the JSON on stdin)
  input JSON : {"subject": "...", "parameters": [{"name","type","min","max","values",...}]}
               (or {"spec": "age accepts 18 to 65"} — a light free-text range is parsed)
  output JSON: {"skill_version","subject","techniques","cases":[...],"combinations":[...],
                "oracle_hint","explained"}

Parameter types: int/number (min,max) · enum (values) · bool · string (minLength,maxLength,
pattern). Exit non-zero only on bad input or a forced --explain provider failure.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_provider import ProviderError, explain, parse_json_block  # noqa: E402

SKILL_VERSION = "test-design-generator/1.0"
RANGE_RE = re.compile(r"(\w+)\D{0,24}?(-?\d+)\s*(?:to|through|and|-|–|\.\.)\s*(-?\d+)", re.I)


def fail(msg, code=2):
    print(f"test-design-generator: {msg}", file=sys.stderr)
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
    if not isinstance(data, dict):
        fail("input JSON must be an object")
    params = data.get("parameters")
    if not isinstance(params, list):
        params = []
    if not params and isinstance(data.get("spec"), str):
        params = parse_spec(data["spec"])
    subject = str(data.get("subject") or data.get("spec") or "subject under test")
    return subject, params


def parse_spec(text):
    """Best-effort: pull integer ranges out of a free-text spec."""
    out = []
    for name, lo, hi in RANGE_RE.findall(text):
        try:
            out.append({"name": name, "type": "int", "min": int(lo), "max": int(hi)})
        except ValueError:
            continue
    return out


# ----------------------------------------------------------------- case generation

def case(technique, param, inputs, expected, rationale):
    return {"technique": technique, "parameter": param, "inputs": inputs,
            "expected": expected, "rationale": rationale}


def gen_param_cases(p):
    """Boundary-value + equivalence-partition cases for one parameter. Returns (cases, reps)
    where reps is the representative value list used for pairwise combination."""
    name, typ = p.get("name", "p"), str(p.get("type", "")).lower()
    cases, reps = [], []
    if typ in ("int", "integer", "number", "float"):
        lo, hi = p.get("min"), p.get("max")
        if lo is None and hi is None:
            cases.append(case("equivalence-partition", name, {name: 0}, "accept", "representative value (no bounds given)"))
            reps = [0, -1, 999999]
            return cases, reps
        lo = lo if lo is not None else hi - 10
        hi = hi if hi is not None else lo + 10
        bv = [(lo - 1, "reject", "just below lower bound"), (lo, "accept", "lower bound"),
              (lo + 1, "accept", "just inside lower bound"), (hi - 1, "accept", "just inside upper bound"),
              (hi, "accept", "upper bound"), (hi + 1, "reject", "just above upper bound")]
        for v, exp, why in bv:
            cases.append(case("boundary-value", name, {name: v}, exp, why))
        mid = (lo + hi) // 2
        cases.append(case("equivalence-partition", name, {name: mid}, "accept", "interior representative"))
        reps = [lo, mid, hi, lo - 1]
    elif typ == "enum":
        vals = p.get("values") or []
        for v in vals:
            cases.append(case("equivalence-partition", name, {name: v}, "accept", "valid enum member"))
        cases.append(case("equivalence-partition", name, {name: "__invalid__"}, "reject", "value outside the enum"))
        reps = list(vals)[:3] + ["__invalid__"]
    elif typ in ("bool", "boolean"):
        cases.append(case("equivalence-partition", name, {name: True}, "accept", "true branch"))
        cases.append(case("equivalence-partition", name, {name: False}, "accept", "false branch"))
        reps = [True, False]
    elif typ in ("string", "str", "text"):
        lo, hi = p.get("minLength"), p.get("maxLength")
        if lo is not None:
            if lo - 1 >= 0:
                cases.append(case("boundary-value", name, {name: "x" * (lo - 1)}, "reject", "one char below minLength"))
            cases.append(case("boundary-value", name, {name: "x" * lo}, "accept", "exactly minLength"))
        if hi is not None:
            cases.append(case("boundary-value", name, {name: "x" * hi}, "accept", "exactly maxLength"))
            cases.append(case("boundary-value", name, {name: "x" * (hi + 1)}, "reject", "one char above maxLength"))
        cases.append(case("equivalence-partition", name, {name: ""}, "reject", "empty string"))
        if str(p.get("pattern", "")).lower() == "email":
            cases.append(case("equivalence-partition", name, {name: "a@b.co"}, "accept", "valid email shape"))
            cases.append(case("equivalence-partition", name, {name: "not-an-email"}, "reject", "missing @/domain"))
        reps = ["valid", "", "x" * ((hi or 5) + 1)]
    else:
        cases.append(case("equivalence-partition", name, {name: "<value>"}, "accept", "representative (unknown type)"))
        reps = ["<value>"]
    return cases, [r for r in reps if r is not None]


def all_pairs(param_values):
    """All-pairs (pairwise) combination cover. Each row is seeded from an uncovered pair
    and the remaining parameters are filled greedily, so every value-pair is covered and
    the loop strictly shrinks `need` each iteration. Returns a list of input dicts."""
    names = [n for n, vs in param_values.items() if vs]
    if len(names) < 2:
        return []
    idx = {n: i for i, n in enumerate(names)}
    valmap = {(i, repr(v)): v for i, n in enumerate(names) for v in param_values[n]}
    need = set()
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            for va in param_values[names[i]]:
                for vb in param_values[names[j]]:
                    need.add((i, repr(va), j, repr(vb)))

    def covered_pairs(row):
        cov = set()
        for a in range(len(names)):
            for b in range(a + 1, len(names)):
                na, nb = names[a], names[b]
                if na in row and nb in row:
                    cov.add((a, repr(row[na]), b, repr(row[nb])))
        return cov

    rows = []
    while need:
        i, ka, j, kb = next(iter(need))
        row = {names[i]: valmap[(i, ka)], names[j]: valmap[(j, kb)]}
        for k, n in enumerate(names):
            if n in row:
                continue
            best, best_cov = param_values[n][0], -1
            for v in param_values[n]:
                cov = 0
                for m in row:
                    mi = idx[m]
                    key = (mi, repr(row[m]), k, repr(v)) if mi < k else (k, repr(v), mi, repr(row[m]))
                    if key in need:
                        cov += 1
                if cov > best_cov:
                    best, best_cov = v, cov
            row[n] = best
        need -= covered_pairs(row)
        rows.append(row)
    return rows


def oracle_hint(params):
    return ("If the function's correct output cannot be enumerated by hand (sorting, pricing, "
            "parsing, formatting), do not hand-pick expected values: use property-based testing "
            "(invariants over generated inputs), metamorphic relations (a transformation that must "
            "preserve a property), or a golden-master/differential reference. Hand-written "
            "assertions only scale when the answer is obvious.")


# ----------------------------------------------------------------- explain (opt-in)

def build_explain_prompt(subject, params, cases):
    return (
        "You are a test designer. The structured cases below cover boundary and equivalence "
        "classes. Add the SEMANTIC/negative cases a structural generator cannot infer: type "
        "confusion, injection/escape strings, unicode/whitespace, null/None, locale, and any "
        "domain rule implied by the subject. Also state the best ORACLE strategy. Return ONLY "
        'JSON: {"extra_cases":[{"technique":str,"parameter":str,"inputs":object,"expected":str,'
        '"rationale":str}],"oracle":str}.\n\n'
        f"Subject: {subject}\nParameters: {json.dumps(params)}\nExisting cases: {json.dumps(cases[:40])}\n"
    )


def main():
    argv = sys.argv
    subject, params = read_input(argv)
    mock = os.environ.get("TEST_DESIGN_GENERATOR_MOCK") == "1" or "--mock" in argv[1:]
    want_explain = "--explain" in argv[1:] or os.environ.get("TEST_DESIGN_GENERATOR_EXPLAIN") == "1"

    cases, reps = [], {}
    for p in params:
        c, r = gen_param_cases(p)
        cases.extend(c)
        if p.get("name"):
            reps[p["name"]] = r
    combinations = [{"inputs": row, "note": "pairwise (all-pairs) combination"} for row in all_pairs(reps)]

    explained = False
    if want_explain or mock:
        if mock:
            cases.append(case("semantic", "*", {"_": "MOCK"}, "reject",
                              "MOCK: deterministic offline placeholder for an LLM-suggested negative case"))
            explained = True
        else:
            try:
                obj = parse_json_block(explain(build_explain_prompt(subject, params, cases)))
                for ec in obj.get("extra_cases", []):
                    if isinstance(ec, dict) and ec.get("inputs") is not None:
                        ec.setdefault("technique", "semantic")
                        ec.setdefault("expected", "reject")
                        ec["source"] = "llm"
                        cases.append(ec)
                explained = True
            except ProviderError as e:
                if want_explain and not mock:
                    fail(f"--explain requested but provider failed: {e}")

    print(json.dumps({
        "skill_version": SKILL_VERSION + ("-mock" if mock else ""),
        "subject": subject,
        "techniques": ["boundary-value", "equivalence-partition", "pairwise"],
        "parameter_count": len(params), "cases": cases, "combinations": combinations,
        "oracle_hint": oracle_hint(params), "explained": explained,
    }))


if __name__ == "__main__":
    main()
