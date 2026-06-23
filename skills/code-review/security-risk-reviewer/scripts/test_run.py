#!/usr/bin/env python3
"""Stdlib-only tests for security-risk-reviewer run.py. No pytest, no network.

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
    full.pop("SECURITY_RISK_REVIEWER_MOCK", None)
    full.pop("SECURITY_RISK_REVIEWER_EXPLAIN", None)
    if env:
        full.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=full)


def rules(out):
    return {f["rule"] for f in out["findings"]}


class TestDetectors(unittest.TestCase):
    def test_aws_key(self):
        out = json.loads(invoke({"file": "c.py", "content": 'key = "AKIAIOSFODNN7EXAMPLE"\n'}).stdout)
        self.assertIn("HARDCODED_SECRET", rules(out))
        f = next(x for x in out["findings"] if x["rule"] == "HARDCODED_SECRET")
        self.assertEqual(f["cwe"], "CWE-798")
        self.assertEqual(f["severity"], "high")

    def test_sql_injection(self):
        out = json.loads(invoke({"file": "c.py", "content": 'q = "SELECT * FROM users WHERE id=" + uid\n'}).stdout)
        self.assertIn("SQL_INJECTION", rules(out))

    def test_command_injection(self):
        out = json.loads(invoke({"file": "c.py", "content": 'os.system("rm -rf " + path)\n'}).stdout)
        self.assertIn("COMMAND_INJECTION", rules(out))

    def test_disabled_tls(self):
        out = json.loads(invoke({"file": "c.py", "content": "requests.get(url, verify=False)\n"}).stdout)
        self.assertIn("DISABLED_TLS_VERIFY", rules(out))

    def test_insecure_deserialize(self):
        out = json.loads(invoke({"file": "c.py", "content": "obj = pickle.loads(blob)\n"}).stdout)
        self.assertIn("INSECURE_DESERIALIZE", rules(out))

    def test_weak_crypto(self):
        out = json.loads(invoke({"file": "c.py", "content": "h = hashlib.md5(pw).hexdigest()\n"}).stdout)
        self.assertIn("WEAK_CRYPTO", rules(out))

    def test_ssrf(self):
        out = json.loads(invoke({"file": "c.py", "content": "return requests.get(url)\n"}).stdout)
        self.assertIn("SSRF", rules(out))

    def test_xss(self):
        out = json.loads(invoke({"file": "c.jsx", "content": "el.innerHTML = userInput\n"}).stdout)
        self.assertIn("XSS", rules(out))

    def test_csharp_command_injection(self):
        out = json.loads(invoke({"file": "a.cs", "content": "Process.Start(\"cmd\", userArg);\n"}).stdout)
        self.assertIn("COMMAND_INJECTION", rules(out))

    def test_csharp_insecure_deserialize(self):
        out = json.loads(invoke({"file": "a.cs", "content": "var f = new BinaryFormatter();\n"}).stdout)
        self.assertIn("INSECURE_DESERIALIZE", rules(out))

    def test_csharp_weak_crypto(self):
        out = json.loads(invoke({"file": "a.cs", "content": "var h = MD5.Create();\n"}).stdout)
        self.assertIn("WEAK_CRYPTO", rules(out))

    def test_js_command_injection(self):
        out = json.loads(invoke({"file": "a.js", "content": "child_process.exec(cmd)\n"}).stdout)
        self.assertIn("COMMAND_INJECTION", rules(out))

    def test_js_ssrf(self):
        out = json.loads(invoke({"file": "a.js", "content": "const r = axios.get(url)\n"}).stdout)
        self.assertIn("SSRF", rules(out))

    def test_clean_file_no_findings(self):
        out = json.loads(invoke({"file": "c.go", "content": "func Add(a, b int) int { return a + b }\n"}).stdout)
        self.assertEqual(out["findings"], [])
        self.assertEqual(out["summary"]["max_risk_score"], 0)

    def test_risk_ranking_orders_by_score(self):
        src = ('low = hashlib.md5(x)\n'           # medium
               'key = "AKIAIOSFODNN7EXAMPLE"\n')   # high
        out = json.loads(invoke({"file": "c.py", "content": src}).stdout)
        scores = [r["risk_score"] for r in out["risk_ranking"]]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(out["risk_ranking"][0]["rule"], "HARDCODED_SECRET")

    def test_blast_radius_amplifies_score(self):
        base = json.loads(invoke({"file": "c.py", "content": "h = hashlib.md5(x)\n"}).stdout)
        amp = json.loads(invoke({"file": "c.py", "content": "h = hashlib.md5(x)\n", "blast_radius": 5}).stdout)
        self.assertGreater(amp["findings"][0]["risk_score"], base["findings"][0]["risk_score"])


class TestModesAndHonesty(unittest.TestCase):
    def test_mock_labels(self):
        r = invoke({"file": "c.py", "content": 'key = "AKIAIOSFODNN7EXAMPLE"\n'},
                   env={"SECURITY_RISK_REVIEWER_MOCK": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertTrue(out["skill_version"].endswith("-mock"))
        self.assertTrue(all(f["reasoning"].startswith("MOCK:") for f in out["findings"]))

    def test_bad_input_fails_closed(self):
        r = invoke({"no": "file"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("file", r.stderr)

    def test_explain_forced_unconfigured_fails_closed(self):
        r = invoke({"file": "c.py", "content": 'key = "AKIAIOSFODNN7EXAMPLE"\n'},
                   env={"CODE_REVIEW_LLM_PROVIDER": "openai"}, extra_args=["--explain"])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("provider failed", r.stderr)


if __name__ == "__main__":
    unittest.main()
