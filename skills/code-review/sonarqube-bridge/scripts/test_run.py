#!/usr/bin/env python3
"""Tests for sonarqube-bridge run.py — unit + seeded PBT + integration. Stdlib only.

Run: python3 test_run.py
Line coverage: python3 -m trace --count --missing -C /tmp/cov test_run.py  (see TESTS.md)
"""

import importlib.util
import json
import os
import random
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "run.py")


def _mod():
    spec = importlib.util.spec_from_file_location("sonar_run", RUN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def invoke(payload, env=None, extra_args=None):
    cmd = [sys.executable, RUN, json.dumps(payload)] + (extra_args or [])
    full = dict(os.environ)
    for k in list(full):
        if k.startswith("CODE_REVIEW_LLM") or k.startswith("CODE_REVIEW_AWS_BEDROCK"):
            full.pop(k)
    full.pop("SONARQUBE_BRIDGE_MOCK", None)
    full.pop("SONARQUBE_BRIDGE_EXPLAIN", None)
    if env:
        full.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=full)


SAMPLE = {"issues": [
    {"key": "A1", "rule": "go:S2076", "severity": "CRITICAL", "type": "VULNERABILITY",
     "component": "proj:internal/api/handler.go", "line": 42,
     "message": "Make sure running this OS command is safe.", "tags": ["cwe-78", "owasp-a3"]},
    {"key": "A2", "rule": "csharpsquid:S3776", "severity": "MAJOR", "type": "CODE_SMELL",
     "component": "proj:src/Pricing.cs", "line": 10,
     "message": "Refactor this method to reduce its Cognitive Complexity.", "tags": ["brain-overload"]},
    {"key": "A3", "rule": "typescript:S1764", "severity": "MINOR", "type": "BUG",
     "component": "proj:web/app.ts", "line": 5, "message": "Correct this identical sub-expression.", "tags": []},
]}


def write_fixture(obj):
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f)
    return path


# ----------------------------------------------------------------- REQ-SONAR-001 ingest

class TestIngest(unittest.TestCase):
    def test_file_source(self):
        p = write_fixture(SAMPLE)
        try:
            out = json.loads(invoke({"source": "file", "issues_file": p}).stdout)
        finally:
            os.unlink(p)
        self.assertEqual(out["summary"]["total"], 3)
        self.assertEqual(out["source"], "file")

    def test_mock_mode(self):
        r = invoke({}, env={"SONARQUBE_BRIDGE_MOCK": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertTrue(out["skill_version"].endswith("-mock"))
        self.assertGreater(out["summary"]["total"], 0)

    def test_api_unconfigured_fails_closed(self):
        r = invoke({"source": "api"})  # no host/token
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")
        self.assertIn("host", r.stderr.lower())

    def test_missing_file_fails_closed(self):
        r = invoke({"source": "file", "issues_file": "/no/such/file.json"})
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_bad_input_fails_closed(self):
        r = subprocess.run([sys.executable, RUN, "not json"], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)


# ------------------------------------------------- REQ-SONAR-002/003/004 normalize+enrich

class TestNormalizeEnrich(unittest.TestCase):
    def setUp(self):
        self.m = _mod()

    def test_severity_map(self):
        self.assertEqual(self.m.map_severity("BLOCKER"), "high")
        self.assertEqual(self.m.map_severity("CRITICAL"), "high")
        self.assertEqual(self.m.map_severity("MAJOR"), "medium")
        self.assertEqual(self.m.map_severity("MINOR"), "low")
        self.assertEqual(self.m.map_severity("INFO"), "low")

    def test_component_to_file(self):
        f = self.m.normalize_issue(SAMPLE["issues"][0])
        self.assertEqual(f["file"], "internal/api/handler.go")
        self.assertEqual(f["source"], "sonarqube")

    def test_owasp_cwe_extraction(self):
        f = self.m.normalize_issue(SAMPLE["issues"][0])
        self.assertEqual(f["cwe"], "cwe-78")
        self.assertEqual(f["owasp"], "owasp-a3")

    def test_blast_radius_amplifies(self):
        findings = [self.m.normalize_issue(SAMPLE["issues"][0])]
        base = self.m.enrich([dict(findings[0])], {}, {})[0]["risk_score"]
        amp = self.m.enrich([dict(findings[0])], {"internal/api/handler.go": 5}, {})[0]["risk_score"]
        self.assertGreater(amp, base)

    def test_capability_tagging(self):
        f = self.m.enrich([self.m.normalize_issue(SAMPLE["issues"][0])],
                          {}, {"internal/api/handler.go": "Payment"})[0]
        self.assertEqual(f["capability"], "Payment")

    def test_remediation_code_smell_complexity(self):
        f = self.m.enrich([self.m.normalize_issue(SAMPLE["issues"][1])], {}, {})[0]
        self.assertIn("Extract Function", f["remediation"])

    def test_remediation_vulnerability(self):
        f = self.m.enrich([self.m.normalize_issue(SAMPLE["issues"][0])], {}, {})[0]
        self.assertIn("OWASP", f["remediation"].upper())

    def test_remediation_bug(self):
        f = self.m.enrich([self.m.normalize_issue(SAMPLE["issues"][2])], {}, {})[0]
        self.assertIn("regression test", f["remediation"].lower())

    def test_remediation_duplicate(self):
        iss = {"severity": "MAJOR", "type": "CODE_SMELL", "component": "p:a", "line": 1,
               "message": "This block is duplicated."}
        f = self.m.enrich([self.m.normalize_issue(iss)], {}, {})[0]
        self.assertIn("Extract the shared", f["remediation"])

    def test_remediation_parameter_object(self):
        iss = {"severity": "MAJOR", "type": "CODE_SMELL", "component": "p:a", "line": 1,
               "message": "Method has too many parameters."}
        f = self.m.enrich([self.m.normalize_issue(iss)], {}, {})[0]
        self.assertIn("Parameter Object", f["remediation"])

    def test_remediation_generic_smell(self):
        iss = {"severity": "MINOR", "type": "CODE_SMELL", "component": "p:a", "line": 1,
               "message": "Remove this unused import."}
        f = self.m.enrich([self.m.normalize_issue(iss)], {}, {})[0]
        self.assertIn("trustworthy test", f["remediation"])

    def test_blast_non_numeric_defaults_to_one(self):
        iss = self.m.normalize_issue(SAMPLE["issues"][0])
        f = self.m.enrich([dict(iss)], {iss["file"]: "not-a-number"}, {})[0]
        self.assertEqual(f["blast_radius"], 1.0)

    def test_bare_list_issues_form(self):
        p = write_fixture(SAMPLE["issues"])  # a bare list, not {"issues": [...]}
        try:
            out = json.loads(invoke({"source": "file", "issues_file": p}).stdout)
        finally:
            os.unlink(p)
        self.assertEqual(out["summary"]["total"], 3)

    def test_malformed_issues_json_fails_closed(self):
        p = write_fixture({"not_issues": 1})
        try:
            r = invoke({"source": "file", "issues_file": p})
        finally:
            os.unlink(p)
        self.assertNotEqual(r.returncode, 0)

    def test_vuln_outranks_smell_same_severity(self):
        m = self.m
        vuln = m.normalize_issue({"severity": "MAJOR", "type": "VULNERABILITY", "component": "p:a", "line": 1, "message": "x"})
        smell = m.normalize_issue({"severity": "MAJOR", "type": "CODE_SMELL", "component": "p:b", "line": 1, "message": "x"})
        ev = m.enrich([vuln, smell], {}, {})
        self.assertGreater(ev[0]["risk_score"], ev[1]["risk_score"])


# ----------------------------------------------------------------- REQ-SONAR-003 ranking

class TestRanking(unittest.TestCase):
    def test_ranking_sorted_desc(self):
        out = json.loads(invoke({}, env={"SONARQUBE_BRIDGE_MOCK": "1"}).stdout)
        scores = [r["risk_score"] for r in out["risk_ranking"]]
        self.assertEqual(scores, sorted(scores, reverse=True))


# ----------------------------------------------------------------- REQ-SONAR-005 explain

class TestExplainHonesty(unittest.TestCase):
    def test_default_offline_no_explain(self):
        p = write_fixture(SAMPLE)
        try:
            out = json.loads(invoke({"source": "file", "issues_file": p}).stdout)
        finally:
            os.unlink(p)
        self.assertFalse(out["explained"])

    def test_explain_forced_unconfigured_fails_closed(self):
        p = write_fixture(SAMPLE)
        try:
            r = invoke({"source": "file", "issues_file": p},
                       env={"CODE_REVIEW_LLM_PROVIDER": "openai"}, extra_args=["--explain"])
        finally:
            os.unlink(p)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("provider failed", r.stderr)


# ----------------------------------------------------------------- PBT (seeded, stdlib)

class TestProperties(unittest.TestCase):
    def setUp(self):
        self.m = _mod()

    def _gen_issue(self, rng, i):
        sev = rng.choice(["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"])
        typ = rng.choice(["VULNERABILITY", "BUG", "CODE_SMELL", "SECURITY_HOTSPOT"])
        return {"key": f"K{i}", "severity": sev, "type": typ,
                "component": f"proj:src/file{i % 7}.cs", "line": rng.randint(1, 500),
                "message": rng.choice(["Cognitive Complexity", "duplicated", "too many parameters", "unsafe"]),
                "tags": rng.choice([[], ["cwe-89"], ["owasp-a1"]])}

    def test_invariants(self):
        m = self.m
        rng = random.Random(20260615)
        for _ in range(250):
            n = rng.randint(0, 12)
            issues = [self._gen_issue(rng, i) for i in range(n)]
            impact = {f"src/file{i}.cs": rng.randint(1, 9) for i in range(7)}
            findings, ranking, summary = m.process(issues, impact, {})
            # (a) no drops
            self.assertEqual(len(findings), n)
            # (b) required keys + (c) severity domain
            for f in findings:
                for k in ("source", "rule", "type", "severity", "file", "line", "risk_score", "remediation"):
                    self.assertIn(k, f)
                self.assertIn(f["severity"], ("high", "medium", "low"))
                self.assertGreaterEqual(f["risk_score"], 1)
            # (d) ranking sorted desc
            rs = [r["risk_score"] for r in ranking]
            self.assertEqual(rs, sorted(rs, reverse=True))
            self.assertEqual(summary["total"], n)

    def test_blast_monotonic(self):
        m = self.m
        rng = random.Random(7)
        for _ in range(200):
            iss = self._gen_issue(rng, 0)
            f = m.normalize_issue(iss)
            lo = m.enrich([dict(f)], {f["file"]: 1}, {})[0]["risk_score"]
            hi = m.enrich([dict(f)], {f["file"]: rng.randint(2, 20)}, {})[0]["risk_score"]
            self.assertGreaterEqual(hi, lo)


# ----------------------------------------------------------------- integration (E2E)

class TestIntegration(unittest.TestCase):
    def test_e2e_ranked_top_finding(self):
        export = {"issues": [
            {"key": "B1", "rule": "csharpsquid:S3776", "severity": "MINOR", "type": "CODE_SMELL",
             "component": "proj:src/Util.cs", "line": 3, "message": "Cognitive Complexity", "tags": []},
            {"key": "B2", "rule": "go:S2076", "severity": "CRITICAL", "type": "VULNERABILITY",
             "component": "proj:internal/pay/charge.go", "line": 88, "message": "OS command", "tags": ["cwe-78"]},
        ]}
        p = write_fixture(export)
        try:
            out = json.loads(invoke({"source": "file", "issues_file": p, "project_key": "proj",
                                     "impact_map": {"internal/pay/charge.go": 10},
                                     "capability_map": {"internal/pay/charge.go": "Payment"}}).stdout)
        finally:
            os.unlink(p)
        self.assertEqual(out["summary"]["total"], 2)
        top = out["risk_ranking"][0]
        self.assertEqual(top["file"], "internal/pay/charge.go")  # high sev + high blast wins
        topf = next(f for f in out["findings"] if f["file"] == "internal/pay/charge.go")
        self.assertEqual(topf["capability"], "Payment")
        self.assertEqual(topf["cwe"], "cwe-78")


if __name__ == "__main__":
    unittest.main()
