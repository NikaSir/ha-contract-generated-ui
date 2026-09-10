"""Exercise the real aggregate gate and its temporary A21 compatibility alias.

Set NIKAS_CI_WORKFLOW_PATH to inspect the same contract in another workflow.
The subprocess executes only the aggregate/compatibility gate scripts, never dependency jobs.
"""

import json
import os
from pathlib import Path
import subprocess
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = Path(os.environ.get(
    "NIKAS_CI_WORKFLOW_PATH", ROOT / ".github/workflows/repository-checks.yml"
))


class CIGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = yaml.safe_load(WORKFLOW.read_text())
        cls.jobs = cls.workflow["jobs"]
        cls.gate = cls.jobs["nikas-required-gate"]
        cls.required = cls.gate["needs"]
        cls.step = cls.gate["steps"][0]
        cls.compat = cls.jobs["validate"]
        cls.compat_step = cls.compat["steps"][0]

    def results(self):
        return {name: {"result": "success", "outputs": {}}
                for name in self.required}

    def run_gate(self, results):
        env = os.environ.copy()
        env["NIKAS_JOB_RESULTS"] = json.dumps(results)
        return subprocess.run(
            ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c",
             self.step["run"]],
            env=env, text=True, capture_output=True, timeout=5,
        )

    def run_compat(self, result):
        env = os.environ.copy()
        env["NIKAS_REQUIRED_GATE_RESULT"] = result
        return subprocess.run(
            ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c",
             self.compat_step["run"]],
            env=env, text=True, capture_output=True, timeout=5,
        )

    def test_unique_gate_covers_every_validation_job_and_cannot_be_skipped(self):
        self.assertIsInstance(self.required, list)
        self.assertEqual(
            set(self.required),
            set(self.jobs) - {"nikas-required-gate", "validate"},
        )
        self.assertEqual(len(self.required), len(set(self.required)))
        self.assertEqual(self.gate["if"], "${{ always() }}")
        self.assertEqual(self.gate.get("name"), "nikas-required-gate")
        self.assertFalse(self.gate.get("continue-on-error", False))
        self.assertEqual(len(self.gate["steps"]), 1)
        self.assertFalse(self.step.get("continue-on-error", False))
        self.assertNotIn("if", self.step)
        self.assertEqual(self.step["env"]["NIKAS_JOB_RESULTS"], "${{ toJSON(needs) }}")
        for name in self.required:
            self.assertFalse(self.jobs[name].get("continue-on-error", False))

    def test_legacy_validate_context_is_a_fail_closed_compatibility_alias(self):
        self.assertEqual(self.compat.get("name"), "validate")
        self.assertEqual(self.compat["if"], "${{ always() }}")
        self.assertEqual(self.compat["needs"], ["nikas-required-gate"])
        self.assertEqual(len(self.compat["steps"]), 1)
        self.assertFalse(self.compat.get("continue-on-error", False))
        self.assertFalse(self.compat_step.get("continue-on-error", False))
        self.assertEqual(
            self.compat_step["env"]["NIKAS_REQUIRED_GATE_RESULT"],
            "${{ needs.nikas-required-gate.result }}",
        )
        self.assertEqual(self.run_compat("success").returncode, 0)
        for result in ("failure", "cancelled", "skipped", "neutral", "", "unknown"):
            with self.subTest(result=result):
                self.assertNotEqual(self.run_compat(result).returncode, 0)

    def test_job_contexts_are_unique_across_workflows(self):
        names = []
        for path in WORKFLOW.parent.iterdir():
            if path.suffix not in (".yml", ".yaml"):
                continue
            workflow = yaml.safe_load(path.read_text())
            for job_id, job in workflow.get("jobs", {}).items():
                names.append(job.get("name", job_id))
        self.assertEqual(len(names), len(set(names)), names)

    def test_complete_success_is_accepted(self):
        result = self.run_gate(self.results())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_every_unsuccessful_dependency_is_rejected(self):
        for name in self.required:
            for status in ("failure", "cancelled", "skipped", "neutral", "", None):
                with self.subTest(job=name, status=status):
                    results = self.results()
                    results[name]["result"] = status
                    self.assertNotEqual(self.run_gate(results).returncode, 0)

    def test_missing_dependency_or_result_is_rejected(self):
        for name in self.required:
            with self.subTest(job=name, missing="dependency"):
                results = self.results()
                del results[name]
                self.assertNotEqual(self.run_gate(results).returncode, 0)
            with self.subTest(job=name, missing="result"):
                results = self.results()
                del results[name]["result"]
                self.assertNotEqual(self.run_gate(results).returncode, 0)

    def test_empty_and_unexpected_job_results_are_rejected(self):
        self.assertNotEqual(self.run_gate({}).returncode, 0)
        results = self.results()
        results["unexpected-job"] = {"result": "success"}
        self.assertNotEqual(self.run_gate(results).returncode, 0)


if __name__ == "__main__":
    unittest.main()
