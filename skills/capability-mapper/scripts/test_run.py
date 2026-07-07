#!/usr/bin/env python3
"""Stdlib-only tests for capability-mapper run.py (Spec #54). No pytest needed.

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
    full_env = dict(os.environ)
    # Isolate from any ambient provider config that could turn an expected
    # failure into a live call.
    for k in list(full_env):
        if k.startswith("CODE_REVIEW_LLM") or k.startswith("CODE_REVIEW_AWS_BEDROCK"):
            full_env.pop(k)
    full_env.pop("CAPABILITY_MAPPER_MOCK", None)
    if env:
        full_env.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=full_env)


class TestCapabilityMapper(unittest.TestCase):
    def test_mock_contract(self):
        r = invoke({"file": "internal/order/fulfilment.go", "symbols": ["ShipOrder"]},
                   env={"CAPABILITY_MAPPER_MOCK": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        for f in ("capability", "description", "confidence", "reasoning", "skill_version"):
            self.assertIn(f, out)
        self.assertTrue(out["skill_version"].endswith("-mock"))
        self.assertTrue(out["reasoning"].startswith("MOCK:"))
        self.assertLessEqual(out["confidence"], 0.5)
        self.assertGreaterEqual(out["confidence"], 0.0)

    def test_mock_deterministic(self):
        payload = {"file": "a/b/billing_service.py", "symbols": ["charge"]}
        r1 = invoke(payload, env={"CAPABILITY_MAPPER_MOCK": "1"})
        r2 = invoke(payload, env={"CAPABILITY_MAPPER_MOCK": "1"})
        self.assertEqual(r1.stdout, r2.stdout)
        self.assertEqual(json.loads(r1.stdout)["capability"], "Billing Service Charge")

    def test_mock_flag_equivalent(self):
        r = invoke({"file": "x/y.go", "symbols": []}, extra_args=["--mock"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout)["skill_version"].endswith("-mock"))

    def test_invalid_input_no_file(self):
        r = invoke({"symbols": ["x"]})
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")
        self.assertIn("file", r.stderr)

    def test_unconfigured_provider_fails_closed(self):
        # LLM-API mode with no provider config → must fail, never fabricate.
        r = invoke({"file": "z.go", "symbols": ["F"]},
                   env={"CODE_REVIEW_CAPABILITY_MODE": "llm-api",
                        "CODE_REVIEW_ALLOW_LEGACY_PYTHON_LLM_API": "1",
                        "CODE_REVIEW_LLM_PROVIDER": "openai"})
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")
        self.assertIn("OPENAI_BASE_URL", r.stderr)

    def test_agent_instruction_default_blocks_provider_env(self):
        r = invoke({"file": "z.go", "symbols": ["F"]},
                   env={"CODE_REVIEW_LLM_PROVIDER": "openai",
                        "CODE_REVIEW_LLM_OPENAI_BASE_URL": "https://example.invalid/v1",
                        "CODE_REVIEW_LLM_OPENAI_API_KEY": "secret"})
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")
        self.assertIn("agent-instruction", r.stderr)
        self.assertIn("llm-api", r.stderr)

    def test_unsupported_provider_fails_closed(self):
        r = invoke({"file": "z.go", "symbols": ["F"]},
                   env={"CODE_REVIEW_CAPABILITY_MODE": "llm-api",
                        "CODE_REVIEW_ALLOW_LEGACY_PYTHON_LLM_API": "1",
                        "CODE_REVIEW_LLM_PROVIDER": "not-a-provider"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unsupported provider", r.stderr)

    def test_llm_api_without_legacy_gate_rejects_python_adapter(self):
        r = invoke({"file": "z.go", "symbols": ["F"]},
                   env={"CODE_REVIEW_CAPABILITY_MODE": "llm-api",
                        "CODE_REVIEW_LLM_PROVIDER": "openai",
                        "CODE_REVIEW_LLM_OPENAI_BASE_URL": "https://example.invalid/v1",
                        "CODE_REVIEW_LLM_OPENAI_API_KEY": "secret"})
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")
        self.assertIn("Go/ADK", r.stderr)
        self.assertIn("legacy/standalone", r.stderr)

    def test_bedrock_model_candidates_default_and_env_override(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("capmap_run", RUN)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        old_model = os.environ.pop("CODE_REVIEW_LLM_BEDROCK_MODEL", None)
        old_seq = os.environ.pop("CODE_REVIEW_LLM_BEDROCK_MODEL_SEQUENCE", None)
        try:
            self.assertEqual(mod.bedrock_model_candidates(),
                             ["moonshotai.kimi-k2.5", "minimax.minimax-m2.5"])
            os.environ["CODE_REVIEW_LLM_BEDROCK_MODEL_SEQUENCE"] = "a, b"
            self.assertEqual(mod.bedrock_model_candidates(), ["a", "b"])
            os.environ["CODE_REVIEW_LLM_BEDROCK_MODEL"] = "configured"
            self.assertEqual(mod.bedrock_model_candidates(), ["configured"])
        finally:
            if old_model is not None:
                os.environ["CODE_REVIEW_LLM_BEDROCK_MODEL"] = old_model
            else:
                os.environ.pop("CODE_REVIEW_LLM_BEDROCK_MODEL", None)
            if old_seq is not None:
                os.environ["CODE_REVIEW_LLM_BEDROCK_MODEL_SEQUENCE"] = old_seq
            else:
                os.environ.pop("CODE_REVIEW_LLM_BEDROCK_MODEL_SEQUENCE", None)


class TestExtractBedrockText(unittest.TestCase):
    """Unit tests for the Bedrock response text extraction (2026-06-07 fix:
    reasoning models emit a reasoningContent block before the text block)."""

    def _run_module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("run_module", RUN)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_converse_reasoning_then_text(self):
        mod = self._run_module()
        resp = {"output": {"message": {"content": [
            {"reasoningContent": {"reasoningText": {"text": "thinking..."}}},
            {"text": "the answer"},
        ]}}}
        self.assertEqual(mod._extract_bedrock_text(resp), "the answer")

    def test_converse_plain_text(self):
        mod = self._run_module()
        resp = {"output": {"message": {"content": [{"text": "hello"}]}}}
        self.assertEqual(mod._extract_bedrock_text(resp), "hello")

    def test_anthropic_invoke_shape(self):
        mod = self._run_module()
        resp = {"content": [{"type": "text", "text": "claude says"}]}
        self.assertEqual(mod._extract_bedrock_text(resp), "claude says")

    def test_no_text_block_fails_closed(self):
        mod = self._run_module()
        resp = {"output": {"message": {"content": [{"reasoningContent": {}}]}}}
        with self.assertRaises(SystemExit):
            mod._extract_bedrock_text(resp)



class TestGlossary(unittest.TestCase):
    """Spec #91: the ubiquitous-language glossary input."""

    def test_mock_snaps_to_glossary_term(self):
        r = invoke(
            {"file": "CLASSES_AddressZipCodeImport_BE.xpo", "symbols": ["run"],
             "glossary": [{"name": "Address / Postal Code Data Management",
                           "aliases": ["Address Data Management"]}]},
            env={"CAPABILITY_MAPPER_MOCK": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["capability"],
                         "Address / Postal Code Data Management")

    def test_mock_without_glossary_unchanged(self):
        r = invoke({"file": "CLASSES_Foo.xpo", "symbols": ["bar"]},
                   env={"CAPABILITY_MAPPER_MOCK": "1"})
        self.assertEqual(json.loads(r.stdout)["capability"], "Classes Foo Bar")

    def test_build_prompt_includes_glossary(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("capmap_run", RUN)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        gloss = [{"name": "Address Validation", "aliases": []}]
        with_g = mod.build_prompt("f.xpo", ["m"], "code", gloss)
        without_g = mod.build_prompt("f.xpo", ["m"], "code", None)
        self.assertIn("Ubiquitous language", with_g)
        self.assertIn("Address Validation", with_g)
        self.assertIn("NEW: ", with_g)
        self.assertNotIn("Ubiquitous language", without_g)



class TestRequirementGrounding(unittest.TestCase):
    """Spec #96: requirement / business-value grounding (folds in spec-tracer)."""

    def _mod(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("capmap_run", RUN)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_skill_version_is_1_1(self):
        self.assertEqual(self._mod().SKILL_VERSION, "capability-mapper/1.1")

    def test_mock_attaches_requirement_linkage(self):
        r = invoke(
            {"file": "internal/order/fulfilment.go", "symbols": ["ShipOrder"],
             "requirements": [
                 {"req_id": "REQ-OF-001", "title": "Ship and cancel customer orders",
                  "source": "spec:order/requirements.md"},
                 {"req_id": "REQ-XX-009", "title": "Unrelated reporting", "source": "RTM.md"}]},
            env={"CAPABILITY_MAPPER_MOCK": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertTrue(out["skill_version"].endswith("1.1-mock"))
        self.assertIn("requirements", out)
        self.assertEqual(out["requirements"][0]["req_id"], "REQ-OF-001")
        self.assertGreaterEqual(out["requirements"][0]["confidence"], 0.0)
        self.assertIn("business_value", out)
        self.assertIn("MOCK", out["business_value"])

    def test_mock_no_requirements_omits_linkage(self):
        r = invoke({"file": "x/y.go", "symbols": ["F"]},
                   env={"CAPABILITY_MAPPER_MOCK": "1"})
        out = json.loads(r.stdout)
        self.assertNotIn("requirements", out)
        self.assertNotIn("business_value", out)
        self.assertTrue(out["skill_version"].endswith("-mock"))

    def test_mock_requirement_deterministic(self):
        payload = {"file": "a/billing_service.py", "symbols": ["charge"],
                   "requirements": [
                       {"req_id": "REQ-BILL-001", "title": "Billing service charge"},
                       {"req_id": "REQ-AUTH-002", "title": "Authentication"}]}
        r1 = invoke(payload, env={"CAPABILITY_MAPPER_MOCK": "1"})
        r2 = invoke(payload, env={"CAPABILITY_MAPPER_MOCK": "1"})
        self.assertEqual(r1.stdout, r2.stdout)
        self.assertEqual(json.loads(r1.stdout)["requirements"][0]["req_id"], "REQ-BILL-001")

    def test_build_prompt_includes_requirements(self):
        mod = self._mod()
        reqs = [{"req_id": "REQ-OF-001", "title": "Ship orders", "source": "x"}]
        with_r = mod.build_prompt("f.go", ["m"], "code", None, reqs)
        without_r = mod.build_prompt("f.go", ["m"], "code", None, None)
        self.assertIn("REQ-OF-001", with_r)
        self.assertIn("business_value", with_r)
        self.assertNotIn("REQ-OF-001", without_r)
        self.assertNotIn("business_value", without_r)

    def test_parse_model_json_optional_requirement_fields(self):
        mod = self._mod()
        good = json.dumps({"capability": "C", "description": "d", "reasoning": "r",
                           "confidence": 0.7,
                           "requirements": [{"req_id": "REQ-A-1", "confidence": 0.9},
                                            {"no_id": True}],
                           "business_value": "  serves REQ-A-1  "})
        obj = mod.parse_model_json(good)
        self.assertEqual(obj["requirements"], [{"req_id": "REQ-A-1", "confidence": 0.9}])
        self.assertEqual(obj["business_value"], "serves REQ-A-1")
        # Absent / blank → keys omitted, never fabricated.
        bare = json.dumps({"capability": "C", "description": "d", "reasoning": "r",
                           "confidence": 0.5, "business_value": "   "})
        obj2 = mod.parse_model_json(bare)
        self.assertNotIn("requirements", obj2)
        self.assertNotIn("business_value", obj2)


class TestRequirementCollector(unittest.TestCase):
    """Spec #96 REQ-CMRG-003: deterministic spec-corpus collector (spec-tracer replacement)."""

    def _collect(self, root):
        cmd = [sys.executable, RUN, "--collect-requirements", root]
        return subprocess.run(cmd, capture_output=True, text=True)

    def _make_corpus(self, base):
        specs = os.path.join(base, ".agents", "specs")
        d = os.path.join(specs, "order-fulfilment")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "requirements.md"), "w", encoding="utf-8") as fh:
            fh.write("# Requirements\n\n"
                     "- **REQ-OF-001 (generic)** — Ship and cancel customer orders.\n"
                     "- **REQ-OF-002** — Track delivery status.\n")
        with open(os.path.join(specs, "RTM.md"), "w", encoding="utf-8") as fh:
            fh.write("| Spec # | Name | Status | Requirements |\n"
                     "|--|--|--|--|\n"
                     "| #1 | Order Fulfilment | Completed | REQ-OF-* |\n"
                     "| #2 | Reporting | Completed | REQ-RPT-* |\n")
        return specs

    def test_collect_parses_corpus(self):
        import tempfile
        with tempfile.TemporaryDirectory() as base:
            self._make_corpus(base)
            r = self._collect(base)
            self.assertEqual(r.returncode, 0, r.stderr)
            out = json.loads(r.stdout)
            ids = {e["req_id"]: e for e in out["requirements"]}
            self.assertIn("REQ-OF-001", ids)
            self.assertEqual(ids["REQ-OF-001"]["title"], "Ship and cancel customer orders.")
            self.assertTrue(ids["REQ-OF-001"]["source"].startswith("spec:"))
            # RTM-only family appears too.
            self.assertIn("REQ-RPT-*", ids)
            self.assertEqual(ids["REQ-RPT-*"]["source"], "RTM.md")
            self.assertGreaterEqual(out["stats"]["count"], 3)

    def test_collect_dedup_concrete_wins_over_family(self):
        import tempfile
        with tempfile.TemporaryDirectory() as base:
            specs = self._make_corpus(base)
            # Add a family row that collides with the concrete REQ-OF-001 family.
            with open(os.path.join(specs, "RTM.md"), "a", encoding="utf-8") as fh:
                fh.write("| #1 | Order Fulfilment Dup | Completed | REQ-OF-001 |\n")
            r = self._collect(base)
            out = json.loads(r.stdout)
            matches = [e for e in out["requirements"] if e["req_id"] == "REQ-OF-001"]
            self.assertEqual(len(matches), 1)
            # Concrete requirements.md title wins, not the RTM row.
            self.assertEqual(matches[0]["title"], "Ship and cancel customer orders.")

    def test_collect_empty_root_fails_closed(self):
        import tempfile
        with tempfile.TemporaryDirectory() as base:
            r = self._collect(base)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip(), "")
            self.assertIn("no spec corpus", r.stderr)

    def test_collect_missing_root_fails_closed(self):
        r = self._collect(os.path.join(HERE, "does-not-exist-xyz"))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


class TestEmitResultEnvelope(unittest.TestCase):
    """Spec #97 CR-2026-06-22-001: --emit-result-envelope wraps per-file annotations
    into an agent-instruction-capabilities-result/v1 file for `review-cli apply-handoff`."""

    def _emit(self, stdin_text, args):
        cmd = [sys.executable, RUN, "--emit-result-envelope"] + args
        return subprocess.run(cmd, input=stdin_text, capture_output=True, text=True)

    def test_wraps_array_into_capabilities_result_envelope(self):
        anns = json.dumps([
            {"source_file": "pkg/charge.go", "capability": "Payment Processing",
             "confidence": 0.9, "skill_version": "capability-mapper/1.1"},
        ])
        r = self._emit(anns, ["--target-root", "/tmp/proj"])
        self.assertEqual(r.returncode, 0, r.stderr)
        env = json.loads(r.stdout)
        self.assertEqual(env["schema_version"], "agent-instruction-capabilities-result/v1")
        self.assertEqual(env["cost_class"], "subscription-agent")
        self.assertEqual(env["provenance"], "agent-instruction")
        self.assertEqual(env["target_root"], "/tmp/proj")
        self.assertEqual(env["candidate_count"], 1)
        self.assertEqual(env["results"][0]["capability"], "Payment Processing")

    def test_accepts_results_wrapper_form(self):
        anns = json.dumps({"results": [
            {"source_file": "a.go", "capability": "Billing", "confidence": 0.5},
        ]})
        r = self._emit(anns, ["--target-root", "/tmp/proj"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["candidate_count"], 1)

    def test_missing_required_fields_fails_closed(self):
        anns = json.dumps([{"capability": "NoSource", "confidence": 0.5}])
        r = self._emit(anns, [])
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_invalid_json_fails_closed(self):
        r = self._emit("not json", [])
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
