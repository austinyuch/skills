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


class TestPrecisionGuards(unittest.TestCase):
    """False-positive guards (the CAP-3 analogue for the OWASP detector): benign code that
    *resembles* a vuln must NOT be flagged. SKILL.md's 'Honesty about false positives' names the
    noisy rules in prose; these lock that precision boundary into an executable contract so a regex
    tightening can't silently regress recall and a loosening can't silently start crying wolf.
    Each guards a specific over-match hazard found by probing run.py. [CR-2026-07-05-076]"""

    def assertRuleClean(self, payload, rule):
        out = json.loads(invoke(payload).stdout)
        got = rules(out)
        self.assertNotIn(rule, got, f"false positive: {rule} fired on {payload['content']!r} -> {sorted(got)}")

    def test_parameterized_sql_clean(self):  # SQL_INJECTION must not fire on a safe query
        self.assertRuleClean({"file": "a.py", "content": 'cur.execute("SELECT * FROM users WHERE id = ?", [uid])\n'}, "SQL_INJECTION")

    def test_orm_query_clean(self):
        self.assertRuleClean({"file": "a.py", "content": "q = session.query(User).filter(User.id == uid)\n"}, "SQL_INJECTION")

    def test_placeholder_secret_clean(self):  # generic secret rule must skip obvious placeholders
        for val in ("changeme", "your-api-key-here", "example", "xxxxxxxxxx", "placeholder", "REDACTED"):
            self.assertRuleClean({"file": "a.py", "content": f'api_key = "{val}"\n'}, "HARDCODED_SECRET")

    def test_templated_secret_clean(self):  # ${...}/{{...}}/env refs are not literal secrets
        for content in ('secret = "${SECRET}"\n', 'password = "{{ vault_pw }}"\n', 'token = "<your-token>"\n'):
            self.assertRuleClean({"file": "a.py", "content": content}, "HARDCODED_SECRET")

    def test_literal_url_get_clean(self):  # SSRF must not fire on a hardcoded (non-user) URL
        self.assertRuleClean({"file": "a.py", "content": 'r = requests.get("https://api.example.com/health")\n'}, "SSRF")

    def test_constant_path_join_clean(self):  # PATH_TRAVERSAL must not fire on a constant path
        self.assertRuleClean({"file": "a.go", "content": 'p := filepath.Join(baseDir, "config.yaml")\n'}, "PATH_TRAVERSAL")

    def test_md5_in_prose_clean(self):  # WEAK_CRYPTO needs a call, not the word 'md5' in a comment
        self.assertRuleClean({"file": "a.py", "content": "# migrated away from md5 to sha256 last year\nalgo = \"sha256\"\n"}, "WEAK_CRYPTO")


class TestRecallHeld(unittest.TestCase):
    """Paired recall guards: the REAL vuln variants of the precision fixes above MUST still fire,
    proving the refiners narrowed only the false positives, not detection. A precision fix that
    also silences a true positive is a recall regression and must fail here."""

    def test_real_secret_still_fires(self):
        for val in ("sk_live_51H8xYq0abcdefG", "S3cr3tP@ssw0rd2024"):
            out = json.loads(invoke({"file": "a.py", "content": f'api_key = "{val}"\n'}).stdout)
            self.assertIn("HARDCODED_SECRET", rules(out), f"recall lost on real secret {val!r}")

    def test_entropy_tail_behind_placeholder_prefix_still_fires(self):
        # CR-076 dogfood: a real secret with a your-/my- prefix but an entropy tail must NOT be
        # dropped as a placeholder (the over-broad prefix glob that did this was narrowed).
        for val in ("your-prod-key-9f3a7c2b", "my-service-token-827364"):
            out = json.loads(invoke({"file": "a.py", "content": f'api_key = "{val}"\n'}).stdout)
            self.assertIn("HARDCODED_SECRET", rules(out), f"recall lost on entropy-tail secret {val!r}")

    def test_entropy_secret_with_bracket_chars_still_fires(self):
        # CR-076 v2 dogfood: a real high-entropy secret containing '<'/'>' must NOT be dropped as a
        # template — angle brackets are a placeholder only when they WRAP the whole value.
        for val in ('N7<kP9>q2Z!', 'a<b>c-d3f8k1'):
            out = json.loads(invoke({"file": "a.py", "content": f'password = "{val}"\n'}).stdout)
            self.assertIn("HARDCODED_SECRET", rules(out), f"recall lost on bracket-bearing secret {val!r}")

    def test_weak_default_credentials_still_fire(self):
        # CR-076 dogfood: weak/DEFAULT creds are real CWE-798/CWE-521 findings, not placeholders.
        for val in ("password", "secret", "123456", "00000000"):  # all >= the rule's 6-char floor
            out = json.loads(invoke({"file": "a.py", "content": f'password = "{val}"\n'}).stdout)
            self.assertIn("HARDCODED_SECRET", rules(out), f"recall lost on default cred {val!r}")

    def test_verify_all_forms_still_fire(self):
        # DISABLED_TLS_VERIFY stays line-based and broad (CR-076 dogfood reverted a tightening that
        # missed multiline-formatted kwargs and variable-flow — real recall loss for a security tool).
        for content in ("session.verify = False\n", "r = requests.get(u, verify=False)\n",
                        "    verify=False,\n", "verify = False\nrequests.get(url, verify=verify)\n"):
            out = json.loads(invoke({"file": "a.py", "content": content}).stdout)
            self.assertIn("DISABLED_TLS_VERIFY", rules(out), f"recall lost on {content!r}")

    def test_path_traversal_fires(self):  # the rule previously had NO positive test at all
        out = json.loads(invoke({"file": "a.py", "content": "return open(request.args.get('f'))\n"}).stdout)
        self.assertIn("PATH_TRAVERSAL", rules(out))


class TestAcceptedOverflags(unittest.TestCase):
    """Documented, ACCEPTED over-flags (SKILL.md 'floor, not ceiling'): these fire by design on
    context-dependent patterns the offline regex cannot disambiguate (Math.random used for jitter
    vs. for tokens). They MUST stay LOW confidence so --explain / a human triages them out — this
    guards against a well-meaning severity bump turning an accepted over-flag into alert fatigue."""

    def test_math_random_fires_but_stays_low_confidence(self):
        out = json.loads(invoke({"file": "a.js", "content": "const jitter = Math.random() * 100\n"}).stdout)
        wc = [f for f in out["findings"] if f["rule"] == "WEAK_CRYPTO"]
        self.assertTrue(wc, "Math.random() should still be flagged (accepted over-flag, not silently dropped)")
        self.assertLessEqual(wc[0]["confidence"], 0.5)
        self.assertEqual(wc[0]["severity"], "medium")


if __name__ == "__main__":
    unittest.main()
