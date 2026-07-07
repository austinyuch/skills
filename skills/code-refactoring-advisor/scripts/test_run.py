#!/usr/bin/env python3
"""Stdlib-only tests for code-refactoring-advisor run.py. No pytest, no network.

Run: python3 test_run.py
"""

import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "run.py")


def invoke(payload, env=None, extra_args=None):
    cmd = [sys.executable, RUN, json.dumps(payload)] + (extra_args or [])
    full = dict(os.environ)
    for k in list(full):
        if k.startswith("CODE_REVIEW_LLM") or k.startswith("CODE_REVIEW_AWS_BEDROCK"):
            full.pop(k)
    full.pop("CODE_REFACTORING_ADVISOR_MOCK", None)
    full.pop("CODE_REFACTORING_ADVISOR_EXPLAIN", None)
    if env:
        full.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=full)


def rules(out):
    return {f["rule"] for f in out["findings"]}


class TestDetectors(unittest.TestCase):
    def test_long_method(self):
        body = "\n".join(f"    x{i} := {i}" for i in range(70))
        src = f"func Big() {{\n{body}\n}}\n"
        out = json.loads(invoke({"file": "a.go", "content": src}).stdout)
        self.assertIn("LONG_METHOD", rules(out))
        f = next(x for x in out["findings"] if x["rule"] == "LONG_METHOD")
        self.assertEqual(f["refactoring"], "Extract Function")
        self.assertTrue(f["safety_net"])
        self.assertEqual(f["minimality_check"]["authority"], "advisory context; not a Phase 5 review verdict")
        self.assertIn("Does this need to exist?", f["minimality_check"]["ladder"][0])
        self.assertIn("architecture/platform agnostic", f["minimality_check"]["portability"])
        self.assertIn("adapter", f["minimality_check"]["ladder"][2])

    def test_parameter_object_minimality_guardrail(self):
        src = "func F(a int, b int, c int, d int, e int, f int, g int) {\n    return\n}\n"
        out = json.loads(invoke({"file": "a.go", "content": src}).stdout)
        f = next(x for x in out["findings"] if x["rule"] == "LONG_PARAMETER_LIST")
        self.assertIn("parameter object", f["minimality_check"]["question"])
        self.assertIn("existing domain/stdlib/platform type", f["minimality_check"]["guidance"])

    def test_long_parameter_list(self):
        src = "func F(a int, b int, c int, d int, e int, f int, g int) {\n    return\n}\n"
        out = json.loads(invoke({"file": "a.go", "content": src}).stdout)
        self.assertIn("LONG_PARAMETER_LIST", rules(out))

    def test_deep_nesting_python(self):
        src = ("def f(x):\n    if x:\n        for i in x:\n            if i:\n"
               "                while i:\n                    return i\n")
        out = json.loads(invoke({"file": "a.py", "content": src}).stdout)
        self.assertIn("DEEP_NESTING", rules(out))

    def test_duplicated_block(self):
        block = ("    total = price * quantity\n    total = total + shipping\n"
                 "    total = total - discount\n    total = round(total, 2)\n"
                 "    log(total)\n    save(total)\n")
        src = f"def a():\n{block}\ndef b():\n{block}\n"
        out = json.loads(invoke({"file": "a.py", "content": src}).stdout)
        self.assertIn("DUPLICATED_BLOCK", rules(out))

    def test_complex_condition(self):
        src = "func F() bool {\n    return a && b && c && d && e\n}\n"
        out = json.loads(invoke({"file": "a.go", "content": src}).stdout)
        self.assertIn("COMPLEX_CONDITION", rules(out))

    def test_magic_numbers(self):
        src = "func F() int {\n    return 7*13 + 42 - 99 + 17 + 23 + 31\n}\n"
        out = json.loads(invoke({"file": "a.go", "content": src}).stdout)
        self.assertIn("MAGIC_NUMBER", rules(out))

    def test_csharp_long_method(self):
        body = "\n".join(f"        var x{i} = {i};" for i in range(70))
        src = f"public class C {{\n    public void Big() {{\n{body}\n    }}\n}}\n"
        out = json.loads(invoke({"file": "C.cs", "content": src}).stdout)
        self.assertEqual(out["language"], "csharp")
        self.assertIn("LONG_METHOD", rules(out))

    def test_csharp_long_parameter_list(self):
        src = "public class C {\n    public void F(int a, int b, int c, int d, int e, int f) {\n    }\n}\n"
        out = json.loads(invoke({"file": "C.cs", "content": src}).stdout)
        self.assertIn("LONG_PARAMETER_LIST", rules(out))

    def test_clean_small_function_no_findings(self):
        src = "func Add(a, b int) int {\n    return a + b\n}\n"
        out = json.loads(invoke({"file": "a.go", "content": src}).stdout)
        self.assertEqual(out["findings"], [])

    def test_thresholds_override(self):
        src = "func F(a int, b int, c int) {\n    return\n}\n"
        out = json.loads(invoke({"file": "a.go", "content": src, "thresholds": {"long_params": 2}}).stdout)
        self.assertIn("LONG_PARAMETER_LIST", rules(out))


class TestModesAndHonesty(unittest.TestCase):
    def test_mock_labels(self):
        body = "\n".join(f"    x{i} := {i}" for i in range(70))
        r = invoke({"file": "a.go", "content": f"func Big() {{\n{body}\n}}\n"},
                   env={"CODE_REFACTORING_ADVISOR_MOCK": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertTrue(out["skill_version"].endswith("-mock"))
        self.assertTrue(all(f["reasoning"].startswith("MOCK:") for f in out["findings"]))

    def test_bad_input_fails_closed(self):
        r = invoke({"nope": 1})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("file", r.stderr)

    def test_explain_forced_unconfigured_fails_closed(self):
        body = "\n".join(f"    x{i} := {i}" for i in range(70))
        r = invoke({"file": "a.go", "content": f"func Big() {{\n{body}\n}}\n"},
                   env={"CODE_REVIEW_LLM_PROVIDER": "openai"}, extra_args=["--explain"])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("provider failed", r.stderr)


class TestPrecisionGuards(unittest.TestCase):
    """False-positive guards for a smell advisor: the dangerous direction here is CRYING WOLF on
    clean-but-structured code — a refactoring advisor that fires on tidy code gets muted. These lock
    the precision boundary into an executable contract (the skill previously had one trivial clean
    guard, `func Add`, for 7 smell families). [CR-2026-07-05-077]"""

    def assertRuleClean(self, payload, rule):
        out = json.loads(invoke(payload).stdout)
        got = rules(out)
        self.assertNotIn(rule, got, f"false positive: {rule} fired on {payload['content']!r} -> {sorted(got)}")

    def test_numbers_in_strings_not_magic(self):  # dates/URLs/versions in strings are not magic numbers
        src = ('def cfg():\n    return {\n        "url": "https://api.example.com/v2/9/8/7",\n'
               '        "date": "2026-07-05", "ver": "1.4.7",\n        "ts": "2024-01-02T03:04:05",\n    }\n')
        self.assertRuleClean({"file": "a.py", "content": src}, "MAGIC_NUMBER")

    def test_numbers_in_comment_not_magic(self):  # digits in a trailing comment are not magic numbers
        src = "def f(x):\n    return x  # retry 3x, wait 30s, timeout 60, backoff 2, max 500, cap 999, tries 7\n"
        self.assertRuleClean({"file": "a.py", "content": src}, "MAGIC_NUMBER")

    def test_table_driven_data_not_duplicated_block(self):  # short repeated struct rows aren't a dup smell
        src = ('var table = []Case{\n  {name: "aaaaaaaaa", in: "bbbbbbbbb", want: "ccccccccc"},\n'
               '  {name: "dddddddddd", in: "eeeeeeeee", want: "fffffffff"},\n'
               '  {name: "gggggggggg", in: "hhhhhhhhh", want: "iiiiiiiii"},\n}\n')
        self.assertRuleClean({"file": "a.go", "content": src}, "DUPLICATED_BLOCK")

    def test_format_specs_and_brace_strings_not_magic(self):
        # CR-077 v2 dogfood: an interpolation body's text after the first ':' is a format spec
        # (`{x:.0f}`) or brace-string data (`{"port":8080}`), not a code literal — must not count.
        jsn = 'def f():\n    return \'{"port":8080,"timeout":30,"retries":3,"limit":50,"a":77,"b":88,"c":99}\'\n'
        self.assertRuleClean({"file": "a.py", "content": jsn}, "MAGIC_NUMBER")
        fmt = 'def g(a,b,c,d,e,f,g):\n    return f"{a:8080}{b:9090}{c:7000}{d:6000}{e:5000}{f:4000}{g:3000}"\n'
        self.assertRuleClean({"file": "a.py", "content": fmt}, "MAGIC_NUMBER")

    def test_small_class_not_god_file(self):  # a normal small class is not a god file
        src = ('class User:\n    def __init__(self, name):\n        self.name = name\n'
               '    def greet(self):\n        return f"hi {self.name}"\n')
        self.assertRuleClean({"file": "a.py", "content": src}, "GOD_FILE")

    def test_normal_function_not_long_or_nested(self):  # a tidy function trips no threshold smell
        out = json.loads(invoke({"file": "a.go", "content": "func F(a, b int) int {\n    if a > b {\n        return a\n    }\n    return b\n}\n"}).stdout)
        self.assertEqual(out["findings"], [], f"clean function flagged: {sorted(rules(out))}")


class TestRecallHeld(unittest.TestCase):
    """Paired recall guards: the REAL smell variants of the precision fixes above MUST still fire,
    proving the string/comment stripping narrowed only false positives, not detection."""

    def test_real_magic_numbers_in_code_still_fire(self):
        out = json.loads(invoke({"file": "a.py", "content": "def score(x):\n    return x*7 + 13 - 42 + 17 + 23 + 31 + 99\n"}).stdout)
        self.assertIn("MAGIC_NUMBER", rules(out), "recall lost on real in-code magic numbers")

    def test_ts_private_field_not_treated_as_comment(self):
        # a TS `#private` field is code, not a Python-style comment — its numbers must still count
        src = "class C {\n  #count = 5\n  run() { return this.#count + 3 + 7 + 11 + 13 + 17 + 19 + 23 }\n}\n"
        out = json.loads(invoke({"file": "a.ts", "content": src}).stdout)
        self.assertIn("MAGIC_NUMBER", rules(out), "recall lost: #private field misread as a comment")

    def test_magic_numbers_in_interpolation_expressions_still_fire(self):
        # CR-077 dogfood: string literals are blanked, but interpolation EXPRESSIONS are code — a
        # real magic number inside f-string / template / $"..." interpolation must still count.
        py = 'def f(a):\n    return f"{a/86400} {a*3600} {a*7} {a*13} {a*17} {a*23} {a*31}"\n'
        ts = "function g(a) { return `${a/86400}+${a*3600}+${a*7}+${a*13}+${a*17}+${a*23}+${a*31}` }\n"
        for name, src in (("a.py", py), ("a.ts", ts)):
            out = json.loads(invoke({"file": name, "content": src}).stdout)
            self.assertIn("MAGIC_NUMBER", rules(out), f"recall lost on interpolation magic numbers in {name}")


if __name__ == "__main__":
    unittest.main()
