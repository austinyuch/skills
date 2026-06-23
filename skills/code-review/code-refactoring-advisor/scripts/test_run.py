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


if __name__ == "__main__":
    unittest.main()
