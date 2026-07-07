#!/usr/bin/env python3
"""Stdlib-only tests for code-summarizer run.py (Spec #56). No pytest needed.

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
    for k in list(full_env):
        if k.startswith("CODE_REVIEW_LLM") or k.startswith("CODE_REVIEW_AWS_BEDROCK"):
            full_env.pop(k)
    full_env.pop("CODE_SUMMARIZER_MOCK", None)
    if env:
        full_env.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=full_env)


class TestCodeSummarizer(unittest.TestCase):
    def test_mock_contract(self):
        r = invoke({"file": "internal/order/fulfilment.go", "symbols": ["ShipOrder"]},
                   env={"CODE_SUMMARIZER_MOCK": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        for f in ("summary", "confidence", "reasoning", "skill_version"):
            self.assertIn(f, out)
        self.assertTrue(out["skill_version"].endswith("-mock"))
        self.assertTrue(out["reasoning"].startswith("MOCK:"))
        self.assertLessEqual(out["confidence"], 0.5)
        self.assertGreaterEqual(out["confidence"], 0.0)

    def test_mock_deterministic(self):
        payload = {"file": "a/b/billing_service.py", "symbols": ["charge"]}
        r1 = invoke(payload, env={"CODE_SUMMARIZER_MOCK": "1"})
        r2 = invoke(payload, env={"CODE_SUMMARIZER_MOCK": "1"})
        self.assertEqual(r1.stdout, r2.stdout)
        self.assertIn("billing_service.py", json.loads(r1.stdout)["summary"])

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
        r = invoke({"file": "z.go", "symbols": ["F"]},
                   env={"CODE_REVIEW_SUMMARY_MODE": "llm-api",
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
                   env={"CODE_REVIEW_SUMMARY_MODE": "llm-api",
                        "CODE_REVIEW_ALLOW_LEGACY_PYTHON_LLM_API": "1",
                        "CODE_REVIEW_LLM_PROVIDER": "not-a-provider"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unsupported provider", r.stderr)

    def test_llm_api_without_legacy_gate_rejects_python_adapter(self):
        r = invoke({"file": "z.go", "symbols": ["F"]},
                   env={"CODE_REVIEW_SUMMARY_MODE": "llm-api",
                        "CODE_REVIEW_LLM_PROVIDER": "openai",
                        "CODE_REVIEW_LLM_OPENAI_BASE_URL": "https://example.invalid/v1",
                        "CODE_REVIEW_LLM_OPENAI_API_KEY": "secret"})
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")
        self.assertIn("Go/ADK", r.stderr)
        self.assertIn("legacy/standalone", r.stderr)

    def test_bedrock_model_candidates_default_and_env_override(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("summary_run", RUN)
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


class TestEmitResultEnvelope(unittest.TestCase):
    """Spec #97 CR-2026-06-22-001: --emit-result-envelope wraps per-file summaries
    into an agent-instruction-summaries-result/v1 file for `review-cli apply-handoff`."""

    def _emit(self, stdin_text, args):
        cmd = [sys.executable, RUN, "--emit-result-envelope"] + args
        return subprocess.run(cmd, input=stdin_text, capture_output=True, text=True)

    def test_wraps_array_into_summaries_result_envelope(self):
        anns = json.dumps([
            {"source_file": "widget.go", "summary": "Builds widgets",
             "confidence": 0.7, "skill_version": "code-summarizer/1.0"},
        ])
        r = self._emit(anns, ["--target-root", "/tmp/proj"])
        self.assertEqual(r.returncode, 0, r.stderr)
        env = json.loads(r.stdout)
        self.assertEqual(env["schema_version"], "agent-instruction-summaries-result/v1")
        self.assertEqual(env["cost_class"], "subscription-agent")
        self.assertEqual(env["provenance"], "agent-instruction")
        self.assertEqual(env["candidate_count"], 1)
        self.assertEqual(env["results"][0]["summary"], "Builds widgets")

    def test_missing_required_fields_fails_closed(self):
        anns = json.dumps([{"summary": "no source", "confidence": 0.5}])
        r = self._emit(anns, [])
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_invalid_json_fails_closed(self):
        r = self._emit("not json", [])
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
