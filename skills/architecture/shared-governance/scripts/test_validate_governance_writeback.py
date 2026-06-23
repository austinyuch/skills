#!/usr/bin/env python3
"""Tests for validate_governance_writeback.py."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest


SCRIPT = Path(__file__).with_name("validate_governance_writeback.py")


EVIDENCE_TEMPLATE = """Lane Identity: `tests/workspace-rollup`
Branch Identity: `tests/workspace-rollup`
Lane Role: `authoritative writable lane`
Artifact / Scope Owned: `workspace .agents/specs/TESTS.md rollup`
Upstream Authority Basis: `module-a/TESTS.md` and `review.md`
Freshness Check Point: `re-read upstream after latest local test evidence refresh`
Conflict Status: `no competing writable lane detected`
Owner / Handoff Owner: `current test-governance lane owner`
Next Action: `proceed writeback`
"""


class ValidateGovernanceWritebackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        (self.workspace / ".agents/specs/governance/ownership-evidence").mkdir(parents=True)
        (self.workspace / "module-a").mkdir(parents=True)
        (self.workspace / "module-a/TESTS.md").write_text("sample test catalog\n", encoding="utf-8")
        (self.workspace / "review.md").write_text("sample review\n", encoding="utf-8")
        (self.workspace / ".agents/specs/governance/ownership-evidence/workspace-tests-demo.md").write_text(
            EVIDENCE_TEMPLATE,
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_script(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        command = [
            "python",
            str(SCRIPT),
            "--workspace",
            str(self.workspace),
            "--target-surface",
            "workspace-tests",
            "--evidence-file",
            str(self.workspace / ".agents/specs/governance/ownership-evidence/workspace-tests-demo.md"),
            *extra_args,
        ]
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def test_pass_output_includes_deterministic_classifications(self) -> None:
        result = self.run_script(
            "--expect-scope-token",
            "workspace .agents/specs/TESTS.md rollup",
            "--upstream",
            str(self.workspace / "module-a/TESTS.md"),
            "--upstream",
            str(self.workspace / "review.md"),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Upstream classifications:", result.stdout)
        self.assertIn("folder-tests\tmodule-a/TESTS.md", result.stdout)
        self.assertIn("source-authority\treview.md", result.stdout)
        self.assertIn("PASS: governance writeback validation succeeded", result.stdout)

    def test_fail_output_still_includes_classifications(self) -> None:
        result = self.run_script(
            "--expect-scope-token",
            "workspace .agents/specs/TESTS.md rollup",
            "--upstream",
            str(self.workspace / ".agents/specs/SPECS.md"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Upstream classifications:", result.stdout)
        self.assertIn("outside-workspace-or-missing\t.agents/specs/SPECS.md", result.stdout)
        self.assertIn("FAIL: governance writeback validation failed", result.stdout)

    def test_empty_required_value_fails(self) -> None:
        evidence = self.workspace / ".agents/specs/governance/ownership-evidence/workspace-tests-demo.md"
        evidence.write_text(EVIDENCE_TEMPLATE.replace("Next Action: `proceed writeback`", "Next Action:"), encoding="utf-8")
        result = self.run_script(
            "--expect-scope-token",
            "workspace .agents/specs/TESTS.md rollup",
            "--upstream",
            str(self.workspace / "module-a/TESTS.md"),
            "--upstream",
            str(self.workspace / "review.md"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Required evidence field has no value: Next Action:", result.stdout)

    def test_missing_scope_token_fails(self) -> None:
        result = self.run_script(
            "--upstream",
            str(self.workspace / "module-a/TESTS.md"),
            "--upstream",
            str(self.workspace / "review.md"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("At least one --expect-scope-token is required", result.stdout)

    def test_rtm_rejects_specs_as_upstream(self) -> None:
        specs_file = self.workspace / ".agents/specs/SPECS.md"
        specs_file.parent.mkdir(parents=True, exist_ok=True)
        specs_file.write_text("sample specs\n", encoding="utf-8")
        command = [
            "python",
            str(SCRIPT),
            "--workspace",
            str(self.workspace),
            "--target-surface",
            "rtm",
            "--evidence-file",
            str(self.workspace / ".agents/specs/governance/ownership-evidence/workspace-tests-demo.md"),
            "--expect-scope-token",
            "workspace .agents/specs/TESTS.md rollup",
            "--upstream",
            str(specs_file),
            "--upstream",
            str(self.workspace / "review.md"),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("specs\t.agents/specs/SPECS.md", result.stdout)
        self.assertIn("RTM.md cannot use SPECS.md as an upstream source", result.stdout)


if __name__ == "__main__":
    unittest.main()
