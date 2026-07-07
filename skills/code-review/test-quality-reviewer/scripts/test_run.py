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


class TestPrecisionGuards(unittest.TestCase):
    """False-positive guards: a test-smell reviewer that flags GOOD tests gets muted. These lock the
    precision boundary against the over-matches probing surfaced — MYSTERY_GUEST on a path/URL used as
    INPUT (not a runtime dependency) or in a comment, and FRAGILE_ASSERTION on a long INPUT literal
    (not an assertion). The skill had clean guards only for NO_ASSERTION. [CR-2026-07-05-078]"""

    def assertRuleClean(self, payload, rule):
        out = json.loads(invoke(payload).stdout)
        got = rules(out)
        self.assertNotIn(rule, got, f"false positive: {rule} fired on {payload['content']!r} -> {sorted(got)}")

    def test_url_as_input_not_mystery_guest(self):  # a URL passed to the code under test is not a hidden dep
        self.assertRuleClean({"file": "url_test.py", "content": 'def test_parse():\n    u = parse("https://example.com/a")\n    assert u.host == "example.com"\n'}, "MYSTERY_GUEST")

    def test_path_as_input_not_mystery_guest(self):
        self.assertRuleClean({"file": "p_test.py", "content": 'def test_norm():\n    assert normalize("/etc/hosts") == "/etc/hosts"\n'}, "MYSTERY_GUEST")

    def test_locator_in_comment_not_mystery_guest(self):
        self.assertRuleClean({"file": "a_test.py", "content": "def test_ok():\n    # see https://tracker/ISSUE-42 for context\n    assert add(1, 2) == 3\n"}, "MYSTERY_GUEST")

    def test_long_input_literal_not_fragile_assertion(self):  # long string is INPUT, not an assertion
        src = 'def test_decode():\n    blob = "' + "a" * 90 + '"\n    assert decode(blob).ok\n'
        self.assertRuleClean({"file": "d_test.py", "content": src}, "FRAGILE_ASSERTION")

    def test_generic_get_on_object_not_mystery_guest(self):  # CR-078 dogfood: `.get(` is not I/O
        src = 'def test_p():\n    options = {"url": "https://example.test/input"}\n    got = parser.get(options["url"])\n    assert got.scheme == "https"\n'
        self.assertRuleClean({"file": "p_test.py", "content": src}, "MYSTERY_GUEST")

    def test_bare_open_identifier_not_mystery_guest(self):  # CR-078 dogfood: bare `open` name, not a call
        src = 'def test_s():\n    open = True\n    got = parse_state("https://example.test/open")\n    assert got.enabled == open\n'
        self.assertRuleClean({"file": "s_test.py", "content": src}, "MYSTERY_GUEST")

    def test_io_on_fixture_plus_unrelated_url_input_not_mystery(self):
        # CR-078 v2 dogfood: block-wide 'any I/O + any locator' over-flags; dataflow-lite fixes it —
        # a legit fixture read AND an unrelated input URL (never read) must not flag the URL.
        src = ('def test_u(tmp_path):\n    data = open(tmp_path / "fixture.txt").read()\n'
               '    result = parse_url("https://example.test/path")\n    assert result.host == "example.test"\n')
        self.assertRuleClean({"file": "u_test.py", "content": src}, "MYSTERY_GUEST")

    def test_long_input_after_unrelated_assert_not_fragile(self):
        # CR-078 v2 dogfood: a long INPUT literal two lines below an already-finished assert is not a
        # fragile assertion (the earlier assert does not continue onto it).
        src = 'def test_p():\n    assert parser is not None\n    raw = "' + "a" * 90 + '"\n    assert parse(raw).ok\n'
        self.assertRuleClean({"file": "p2_test.py", "content": src}, "FRAGILE_ASSERTION")


class TestRecallHeld(unittest.TestCase):
    """Paired recall guards: the REAL smells the precision fixes narrowed MUST still fire, proving the
    I/O-context and assertion-context requirements removed only false positives, not detection."""

    def test_real_mystery_guest_io_still_fires(self):
        for src in ('def test_r():\n    data = open("/home/ci/fixture.json").read()\n    assert data\n',
                    'def test_a():\n    r = requests.get("https://api.internal/x")\n    assert r.ok\n'):
            out = json.loads(invoke({"file": "m_test.py", "content": src}).stdout)
            self.assertIn("MYSTERY_GUEST", rules(out), f"recall lost on real mystery guest: {src!r}")

    def test_real_fragile_assertion_still_fires(self):  # this rule had NO positive test before CR-078
        src = 'def test_render():\n    assert render() == "<html><body><div>' + "x" * 80 + '</div></body></html>"\n'
        out = json.loads(invoke({"file": "f_test.py", "content": src}).stdout)
        self.assertIn("FRAGILE_ASSERTION", rules(out), "recall lost on a real fragile assertion")

    def test_split_locator_then_read_still_fires(self):  # CR-078 dogfood: variable-link, not same-line
        src = ('func TestG(t *testing.T) {\n    path := "/tmp/golden/orders.json"\n'
               '    got, err := os.ReadFile(path)\n    require.NoError(t, err)\n    require.NotEmpty(t, got)\n}\n')
        out = json.loads(invoke({"file": "g_test.go", "content": src}).stdout)
        self.assertIn("MYSTERY_GUEST", rules(out), "recall lost: locator assigned then read on next line")

    def test_pathlib_read_text_still_fires(self):  # CR-078 v2 dogfood: read_text/read_bytes are I/O
        src = 'def test_c():\n    text = pathlib.Path("/etc/app/config.yaml").read_text()\n    assert "name:" in text\n'
        out = json.loads(invoke({"file": "c_test.py", "content": src}).stdout)
        self.assertIn("MYSTERY_GUEST", rules(out), "recall lost on pathlib .read_text()")

    def test_wrapped_fragile_assertion_still_fires(self):  # CR-078 dogfood: literal wraps below assert
        src = ('def test_html():\n    assert render(o) == (\n        "<html><body>' + "a" * 74
               + '</body></html>"\n    )\n')
        out = json.loads(invoke({"file": "h_test.py", "content": src}).stdout)
        self.assertIn("FRAGILE_ASSERTION", rules(out), "recall lost on a wrapped fragile assertion")


if __name__ == "__main__":
    unittest.main()
