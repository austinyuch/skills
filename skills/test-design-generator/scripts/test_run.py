#!/usr/bin/env python3
"""Stdlib-only tests for test-design-generator run.py. No pytest, no network.

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
    full.pop("TEST_DESIGN_GENERATOR_MOCK", None)
    full.pop("TEST_DESIGN_GENERATOR_EXPLAIN", None)
    if env:
        full.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=full)


class TestGeneration(unittest.TestCase):
    def test_int_range_boundaries(self):
        out = json.loads(invoke({"subject": "age", "parameters": [{"name": "age", "type": "int", "min": 18, "max": 65}]}).stdout)
        ages = {c["inputs"]["age"]: c["expected"] for c in out["cases"] if "age" in c["inputs"]}
        # The canonical boundary set: 17 reject, 18/19 accept, 64/65 accept, 66 reject.
        self.assertEqual(ages[17], "reject")
        self.assertEqual(ages[18], "accept")
        self.assertEqual(ages[66], "reject")

    def test_enum_cases(self):
        out = json.loads(invoke({"parameters": [{"name": "country", "type": "enum", "values": ["US", "CA"]}]}).stdout)
        vals = {json.dumps(c["inputs"]): c["expected"] for c in out["cases"]}
        self.assertIn('{"country": "US"}', vals)
        self.assertEqual(vals['{"country": "__invalid__"}'], "reject")

    def test_string_length_boundaries(self):
        out = json.loads(invoke({"parameters": [{"name": "u", "type": "string", "minLength": 3, "maxLength": 8}]}).stdout)
        lens = {len(c["inputs"]["u"]): c["expected"] for c in out["cases"] if "u" in c["inputs"]}
        self.assertEqual(lens[2], "reject")   # below minLength
        self.assertEqual(lens[3], "accept")   # exactly minLength
        self.assertEqual(lens[9], "reject")   # above maxLength

    def test_spec_freetext_range(self):
        out = json.loads(invoke({"spec": "age accepts 18 to 65"}).stdout)
        self.assertTrue(any(c["inputs"].get("age") == 17 and c["expected"] == "reject" for c in out["cases"]))

    def test_pairwise_covers_all_pairs(self):
        payload = {"parameters": [
            {"name": "a", "type": "enum", "values": ["a1", "a2"]},
            {"name": "b", "type": "enum", "values": ["b1", "b2"]},
            {"name": "c", "type": "bool"},
        ]}
        out = json.loads(invoke(payload).stdout)
        rows = [r["inputs"] for r in out["combinations"]]
        # Every (a,b) value pair must appear in some combination row.
        for av in ("a1", "a2"):
            for bv in ("b1", "b2"):
                self.assertTrue(any(r.get("a") == av and r.get("b") == bv for r in rows),
                                f"pair {av},{bv} not covered")

    def test_oracle_hint_present(self):
        out = json.loads(invoke({"subject": "price engine"}).stdout)
        self.assertIn("property-based", out["oracle_hint"])

    def test_output_schema(self):
        out = json.loads(invoke({"subject": "x"}).stdout)
        for k in ("skill_version", "subject", "techniques", "cases", "combinations", "oracle_hint", "explained"):
            self.assertIn(k, out)


class TestModesAndHonesty(unittest.TestCase):
    def test_mock_labels(self):
        r = invoke({"subject": "x", "parameters": [{"name": "n", "type": "int", "min": 1, "max": 3}]},
                   env={"TEST_DESIGN_GENERATOR_MOCK": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertTrue(out["skill_version"].endswith("-mock"))
        self.assertTrue(any(c["rationale"].startswith("MOCK:") for c in out["cases"]))

    def test_bad_input_fails_closed(self):
        cmd = [sys.executable, RUN, "not json"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)

    def test_explain_forced_unconfigured_fails_closed(self):
        r = invoke({"subject": "x", "parameters": [{"name": "n", "type": "int", "min": 1, "max": 3}]},
                   env={"CODE_REVIEW_LLM_PROVIDER": "openai"}, extra_args=["--explain"])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("provider failed", r.stderr)


if __name__ == "__main__":
    unittest.main()
