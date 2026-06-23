#!/usr/bin/env python3
"""Stdlib-only tests for test-quality-reviewer run.py. No pytest, no network.

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
    full.pop("TEST_QUALITY_REVIEWER_MOCK", None)
    full.pop("TEST_QUALITY_REVIEWER_EXPLAIN", None)
    if env:
        full.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=full)


def rules(out):
    return {f["rule"] for f in out["findings"]}


class TestDetectors(unittest.TestCase):
    def test_no_assertion_go(self):
        src = "func TestThing(t *testing.T) {\n    got := Compute(2)\n    _ = got\n}\n"
        r = invoke({"file": "x_test.go", "content": src})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NO_ASSERTION", rules(json.loads(r.stdout)))

    def test_clean_go_test_has_no_no_assertion(self):
        src = ("func TestAdd(t *testing.T) {\n    if got := Add(1, 2); got != 3 {\n"
               "        t.Errorf(\"Add(1,2)=%d want 3\", got)\n    }\n}\n")
        out = json.loads(invoke({"file": "x_test.go", "content": src}).stdout)
        self.assertNotIn("NO_ASSERTION", rules(out))

    def test_mystery_guest(self):
        src = ("def test_reads():\n    data = open('/home/ci/fixture.json').read()\n"
               "    assert data\n")
        out = json.loads(invoke({"file": "t_test.py", "content": src}).stdout)
        self.assertIn("MYSTERY_GUEST", rules(out))

    def test_conditional_logic_python(self):
        src = ("def test_paths():\n    for v in [1, 2, 3]:\n        if v > 1:\n"
               "            assert v > 0\n")
        out = json.loads(invoke({"file": "t_test.py", "content": src}).stdout)
        self.assertIn("CONDITIONAL_TEST_LOGIC", rules(out))

    def test_assertion_roulette(self):
        body = "\n".join(f"    assert f{i}() == {i}" for i in range(8))
        src = f"def test_many():\n{body}\n"
        out = json.loads(invoke({"file": "t_test.py", "content": src}).stdout)
        self.assertIn("ASSERTION_ROULETTE", rules(out))

    def test_pyramid_inversion(self):
        src = ("def test_login():\n    page.goto('http://localhost')\n    assert page\n")
        out = json.loads(invoke({"file": "unit/login_test.py", "content": src}).stdout)
        self.assertIn("PYRAMID_INVERSION", rules(out))

    def test_csharp_no_assertion(self):
        src = "[Fact]\npublic void Computes() {\n    var got = Compute(2);\n}\n"
        out = json.loads(invoke({"file": "Calc.Tests.cs", "content": src}).stdout)
        self.assertEqual(out["language"], "csharp")
        self.assertIn("NO_ASSERTION", rules(out))

    def test_csharp_clean_with_assert(self):
        src = "[Fact]\npublic void Adds() {\n    Assert.Equal(3, Add(1, 2));\n}\n"
        out = json.loads(invoke({"file": "Calc.Tests.cs", "content": src}).stdout)
        self.assertNotIn("NO_ASSERTION", rules(out))

    def test_clean_file_no_findings(self):
        src = ("def test_add():\n    assert add(1, 2) == 3\n\n"
               "def test_sub():\n    assert sub(3, 1) == 2\n")
        out = json.loads(invoke({"file": "calc_test.py", "content": src}).stdout)
        self.assertEqual(out["findings"], [])
        self.assertEqual(out["summary"]["total"], 0)

    def test_output_schema(self):
        out = json.loads(invoke({"file": "x_test.go", "content": "func TestX(t *testing.T) {}\n"}).stdout)
        for k in ("skill_version", "target", "language", "explained", "summary", "findings"):
            self.assertIn(k, out)
        self.assertEqual(out["language"], "go")


class TestModesAndHonesty(unittest.TestCase):
    def test_mock_labels_reasoning(self):
        src = "func TestX(t *testing.T) { _ = 1 }\n"
        r = invoke({"file": "x_test.go", "content": src}, env={"TEST_QUALITY_REVIEWER_MOCK": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertTrue(out["explained"])
        self.assertTrue(out["skill_version"].endswith("-mock"))
        self.assertTrue(all(f["reasoning"].startswith("MOCK:") for f in out["findings"]))

    def test_bad_input_fails_closed(self):
        r = invoke({"content": "no file"})
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")
        self.assertIn("file", r.stderr)

    def test_explain_forced_unconfigured_fails_closed(self):
        # A real finding + forced explain + no provider must fail, never fake.
        src = "func TestX(t *testing.T) { x := 1; _ = x }\n"
        r = invoke({"file": "x_test.go", "content": src},
                   env={"CODE_REVIEW_LLM_PROVIDER": "openai"}, extra_args=["--explain"])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("provider failed", r.stderr)

    def test_default_offline_succeeds_without_provider(self):
        src = "func TestX(t *testing.T) { x := 1; _ = x }\n"
        r = invoke({"file": "x_test.go", "content": src})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(json.loads(r.stdout)["explained"])


if __name__ == "__main__":
    unittest.main()
