"""Tamper and refusal tests for the read-only repository contract inspector."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/nikas_repository_contract.py"
SPEC = importlib.util.spec_from_file_location("nikas_repository_contract", MODULE_PATH)
contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.write("custom_components/example/manifest.json", json.dumps({"domain": "example", "version": "0.1.0"}))
        self.write("custom_components/example/__init__.py", "# Registration requires runtime verification.\n")
        self.write("custom_components/example/const.py", 'PANEL_FILE = "panel.js"\nCACHE_VERSION = "1.2.3"\n')
        self.write("custom_components/example/frontend/panel.js", 'const UI_VERSION = "1.2.3";\ncustomElements.define("test-panel", class {});\n')
        self.profile = {
            "schema_version": 1, "repository": "NikaSir/ha-example", "source_revision": "a" * 40,
            "kind": "ha_integration", "domain": "example",
            "manifest_path": "custom_components/example/manifest.json",
            "artifacts": [{
                "id": "panel", "path": "custom_components/example/frontend/panel.js", "ui_version": "1.2.3",
                "bindings": [
                    {"role": "entrypoint", "path": "custom_components/example/const.py",
                     "pattern": r'PANEL_FILE\s*=\s*"(?P<value>[^"\r\n]+)"', "expected": "panel.js", "path_mode": "basename"},
                    {"role": "ui_version", "path": "custom_components/example/frontend/panel.js",
                     "pattern": r'UI_VERSION\s*=\s*"(?P<value>[^"\r\n]+)"', "expected": "1.2.3"},
                    {"role": "cache_key", "path": "custom_components/example/const.py",
                     "pattern": r'CACHE_VERSION\s*=\s*"(?P<value>[^"\r\n]+)"', "expected": "1.2.3"},
                ], "registration_evidence_paths": ["custom_components/example/__init__.py"], "binding_limitations": [],
            }],
            "standards": {"applicable": True, "declaration_path": ".nikas-ui-standard.json", "reason": "Active panel", "evidence_paths": ["custom_components/example/__init__.py"]},
            "publication": {"default_branch": "main", "github_releases": False, "automatic_tags": False},
            "evidence": [], "findings": [],
        }

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def checked_profile(self, profile=None):
        path = self.write("profile.json", json.dumps(profile or self.profile))
        return contract.load_profile(path)

    def artifact_results(self):
        return contract.check_artifact(self.profile["artifacts"][0], self.root)[0]

    def test_stale_entrypoint_cannot_pass_binding(self):
        self.write("custom_components/example/const.py", 'PANEL_FILE = "current.js"\nCACHE_VERSION = "1.2.3"\n')
        checks = self.artifact_results()
        self.assertTrue(any(item["requirement"] == "artifact_bindings" and item.get("role") == "entrypoint" and item["status"] == "fail" for item in checks))

    def test_binding_self_consistency_does_not_prove_active_registration(self):
        checks = self.artifact_results()
        self.assertTrue(any(item["requirement"] == "registration_reachability" and item["status"] == "not_verified" for item in checks))
        self.assertNotEqual(contract.aggregate(checks), "pass")

    def test_old_version_file_cannot_substitute_for_runtime(self):
        old = "custom_components/example/frontend/old.js"
        self.write(old, 'const UI_VERSION = "1.2.3";')
        self.profile["artifacts"][0]["bindings"][1]["path"] = old
        checks = self.artifact_results()
        self.assertTrue(any(item["requirement"] == "version_coherence" and item["status"] == "not_verified" for item in checks))

    def test_visible_ui_version_mismatch_fails(self):
        self.write("custom_components/example/frontend/panel.js", 'const UI_VERSION = "9.9.9";')
        self.assertTrue(any(item["requirement"] == "artifact_bindings" and item.get("role") == "ui_version" and item["status"] == "fail" for item in self.artifact_results()))

    def test_commented_binding_is_not_a_fact(self):
        self.write("custom_components/example/const.py", '# PANEL_FILE = "panel.js"\nCACHE_VERSION = "1.2.3"\n')
        self.assertTrue(any(item.get("role") == "entrypoint" and item["status"] == "not_verified" for item in self.artifact_results()))

    def test_import_graph_follows_actual_dependency_and_detects_dynamic(self):
        self.write("custom_components/example/frontend/panel.js", 'import "./first.js"; import("./second.js");')
        self.write("custom_components/example/frontend/first.js", 'export { x } from "./third.js";')
        self.write("custom_components/example/frontend/second.js", "// empty\n")
        self.write("custom_components/example/frontend/third.js", "export const x = 1;")
        checks, graph = contract.check_artifact(self.profile["artifacts"][0], self.root)
        self.assertEqual(len(graph["files"]), 4)
        self.assertTrue(any(edge["dynamic"] for edge in graph["edges"]))
        self.assertTrue(any(item["requirement"] == "artifact_autonomy" and item["status"] == "fail" for item in checks))

    def test_computed_dynamic_import_is_unverified(self):
        self.write("custom_components/example/frontend/panel.js", 'const page = "./module.js"; import(page);')
        checks = self.artifact_results()
        self.assertTrue(any(item["requirement"] == "artifact_autonomy" and item["status"] == "not_verified" for item in checks))

    def test_escaped_static_import_does_not_disappear(self):
        imports, unknown = contract.imports_from(r'import "./legacy\u002ejs";')
        self.assertTrue(unknown)

    def test_no_recognized_imports_is_not_complete_autonomy_proof(self):
        checks = self.artifact_results()
        self.assertEqual(next(item for item in checks if item["requirement"] == "artifact_autonomy")["status"], "not_verified")
        self.assertEqual(next(item for item in checks if item["requirement"] == "artifact_syntax")["status"], "not_verified")
        self.assertEqual(next(item for item in checks if item["requirement"] == "reproducible_build")["status"], "not_verified")

    def test_comments_strings_and_regex_examples_are_not_runtime_imports(self):
        source = '''// import "./fake1.js";
/* import('./fake2.js'); */
const label = "import('./fake3.js')";
const pattern = /import\\('fake'\\)/;
'''
        imports, unknown = contract.imports_from(source)
        self.assertEqual(imports, [])
        self.assertEqual(unknown, [])

    def test_template_interpolation_import_cannot_pass(self):
        imports, unknown = contract.imports_from('const html = `${import(name)}`;')
        self.assertTrue(unknown)

    def test_missing_runtime_cannot_pass_autonomy(self):
        (self.root / self.profile["artifacts"][0]["path"]).unlink()
        checks = self.artifact_results()
        self.assertFalse(any(item["requirement"] == "artifact_autonomy" and item["status"] == "pass" for item in checks))

    def test_manifest_domain_mismatch_fails(self):
        self.write("custom_components/example/manifest.json", '{"domain":"wrong","version":"0.1.0"}')
        checks = contract.check_identity(self.profile, self.root)
        self.assertTrue(any(item["requirement"] == "manifest_identity" and item["status"] == "fail" for item in checks))

    def test_non_object_manifest_and_standard_report_failure(self):
        self.write("custom_components/example/manifest.json", '[]')
        checks = contract.check_identity(self.profile, self.root)
        self.assertEqual(next(item for item in checks if item["requirement"] == "manifest_identity")["status"], "fail")
        self.write(".nikas-ui-standard.json", '[]')
        self.assertEqual(contract.check_standards(self.profile, self.root)[0]["status"], "fail")

    def test_old_documents_with_matching_local_hashes_still_fail(self):
        standard = self.write("docs/ui.md", "Old v1.9 standard")
        navigation = self.write("docs/nav.md", "Old nav")
        declaration = {"version": "1.9", "navigation_contract_version": "1.0", "standard_path": "docs/ui.md",
                       "standard_sha256": contract.digest(standard), "navigation_contract_path": "docs/nav.md",
                       "navigation_contract_sha256": contract.digest(navigation)}
        self.write(".nikas-ui-standard.json", json.dumps(declaration))
        checks = contract.check_standards(self.profile, self.root)
        self.assertEqual(sum(item["status"] == "fail" for item in checks), 4)

    def test_changing_only_standard_version_does_not_hide_old_content(self):
        self.write("docs/ui.md", "Old standard")
        self.write("docs/nav.md", "Old nav")
        baseline = contract.load_standard_baseline()
        declaration = {"version": "2.2", "navigation_contract_version": "1.2", "standard_path": "docs/ui.md",
                       "standard_sha256": baseline["ui_sha256"], "navigation_contract_path": "docs/nav.md",
                       "navigation_contract_sha256": baseline["navigation_sha256"]}
        self.write(".nikas-ui-standard.json", json.dumps(declaration))
        checks = contract.check_standards(self.profile, self.root)
        self.assertEqual(sum(item["status"] == "fail" for item in checks), 2)

    def test_frontend_cannot_disable_ui_applicability(self):
        self.profile["standards"]["applicable"] = False
        self.assertEqual(contract.check_standards(self.profile, self.root)[0]["status"], "fail")

    def test_omitted_artifacts_do_not_prove_absent_runtime(self):
        self.profile["artifacts"] = []
        self.profile["standards"]["applicable"] = False
        self.assertEqual(contract.check_standards(self.profile, self.root)[0]["status"], "not_verified")
        self.profile["kind"] = "standards"
        checks = contract.check_evidence(self.profile, self.root, {})
        self.assertFalse(any(item["status"] in {"pass", "not_applicable"} for item in checks))

    def test_supported_standard_version_alias_preserves_factual_baseline(self):
        self.write(".nikas-ui-standard.json", '{"standard_version":"2.2"}')
        checks = contract.check_standards(self.profile, self.root)
        self.assertEqual(next(item for item in checks if item.get("field") == "version")["status"], "pass")
        self.assertEqual(next(item for item in checks if item.get("field") == "navigation_contract_version")["status"], "not_verified")

    def test_missing_pending_and_not_applicable_behavior_do_not_become_pass(self):
        for status in (None, "pending", "not_applicable"):
            with self.subTest(status=status):
                self.profile["evidence"] = [] if status is None else [{"requirement": "command_safety", "status": status, "paths": [], "note": "Unavailable readback not yet tested"}]
                checks = contract.check_evidence(self.profile, self.root, {})
                result = next(item for item in checks if item["requirement"] == "command_safety")
                self.assertEqual(result["status"], "not_verified")
                self.assertEqual(next(item for item in checks if item["requirement"] == "device_acceptance")["status"], "not_verified")

    def test_document_cannot_be_machine_behavior_evidence(self):
        self.write("evidence.md", "PASS: unknown/unavailable behavior tested")
        self.profile["evidence"] = [{"requirement": "data_quality", "status": "recorded", "paths": ["evidence.md"], "note": "Declared", "report_path": "evidence.md"}]
        result = next(item for item in contract.check_evidence(self.profile, self.root, {}) if item["requirement"] == "data_quality")
        self.assertEqual(result["status"], "not_verified")

    def test_machine_evidence_requires_matching_subjects_scenarios_revision(self):
        runtime = self.profile["artifacts"][0]["path"]
        hashes = {runtime: contract.digest(self.root / runtime)}
        report = {"schema_version": 1, "repository": self.profile["repository"], "source_revision": "a" * 40,
                  "requirement": "data_quality", "subject_files": hashes, "scenarios": sorted(contract.REQUIREMENTS["data_quality"]),
                  "runner_kind": "behavior_test", "runner_id": "test-run-123", "environment": {"python": "3.13"}, "result": "pass"}
        self.write("evidence.json", json.dumps(report))
        self.profile["evidence"] = [{"requirement": "data_quality", "status": "recorded", "paths": [runtime], "note": "Recorded run", "report_path": "evidence.json"}]
        with patch.object(contract, "git_value", return_value="a" * 40):
            checks = contract.check_evidence(self.profile, self.root, hashes)
            self.assertEqual(next(item for item in checks if item["requirement"] == "data_quality")["status"], "pass")
            self.write(runtime, '// Changed after test\n')
            checks = contract.check_evidence(self.profile, self.root, hashes)
            self.assertEqual(next(item for item in checks if item["requirement"] == "data_quality")["status"], "not_verified")

    def test_device_acceptance_cannot_be_certified_by_behavior_runner(self):
        runtime = self.profile["artifacts"][0]["path"]
        hashes = {runtime: contract.digest(self.root / runtime)}
        report = {"schema_version": 1, "repository": self.profile["repository"], "source_revision": "a" * 40,
                  "requirement": "device_acceptance", "subject_files": hashes,
                  "scenarios": sorted(contract.REQUIREMENTS["device_acceptance"]),
                  "runner_kind": "behavior_test", "runner_id": "unittest", "environment": {"python": "3.13"}, "result": "pass"}
        self.write("evidence.json", json.dumps(report))
        self.profile["evidence"] = [{"requirement": "device_acceptance", "status": "recorded", "paths": [runtime], "note": "Synthetic run", "report_path": "evidence.json"}]
        with patch.object(contract, "git_value", return_value="a" * 40):
            checks = contract.check_evidence(self.profile, self.root, hashes)
        self.assertEqual(next(item for item in checks if item["requirement"] == "device_acceptance")["status"], "not_verified")

    def test_backend_receipt_must_cover_actual_runtime_subjects(self):
        self.profile["artifacts"] = []
        readme = self.write("README.md", "Documentation")
        report = {"schema_version": 1, "repository": self.profile["repository"], "source_revision": "a" * 40,
                  "requirement": "data_quality", "subject_files": {"README.md": contract.digest(readme)},
                  "scenarios": sorted(contract.REQUIREMENTS["data_quality"]), "runner_kind": "behavior_test",
                  "runner_id": "test-run", "environment": {"python": "3.13"}, "result": "pass"}
        self.write("evidence.json", json.dumps(report))
        self.profile["evidence"] = [{"requirement": "data_quality", "status": "recorded", "paths": ["README.md"], "note": "Insufficient subject scope", "report_path": "evidence.json"}]
        with patch.object(contract, "git_value", return_value="a" * 40):
            report = contract.validate_repository(self.checked_profile(), self.root)
        self.assertEqual(next(item for item in report["requirements"] if item["requirement"] == "data_quality")["status"], "not_verified")

    def test_malformed_evidence_shapes_do_not_crash_or_pass(self):
        self.profile["evidence"] = [{"requirement": "data_quality", "status": "recorded", "paths": [], "note": "bad shape", "report_path": "evidence.json"}]
        for report in ([], {"scenarios": [{}]}, {"subject_files": []}):
            self.write("evidence.json", json.dumps(report))
            checks = contract.check_evidence(self.profile, self.root, {})
            self.assertEqual(next(item for item in checks if item["requirement"] == "data_quality")["status"], "not_verified")

    def test_yaml_release_step_detected_but_comment_and_echo_ignored(self):
        self.write(".github/workflows/check.yml", '''name: Checks
on: [pull_request]
# uses: softprops/action-gh-release@v1
jobs:
  checks:
    steps:
      - run: |
          # gh release create v1
          echo "gh release create is forbidden"
          python -m unittest
''')
        checks = contract.check_publication(self.profile, self.root)
        result = next(item for item in checks if item["requirement"] == "publication_workflows")
        self.assertEqual(result["status"], "not_verified")
        self.assertEqual(result["findings"], [])
        self.write(".github/workflows/release.yml", '''on: [push]
jobs:
  release:
    steps:
      - run: gh release create "$VERSION"
''')
        checks = contract.check_publication(self.profile, self.root)
        self.assertEqual(next(item for item in checks if item["requirement"] == "publication_workflows")["status"], "fail")

    def test_release_driven_hacs_policy_allows_a_release_workflow_without_certifying_it(self):
        self.profile["publication"] = {
            "default_branch": "main",
            "github_releases": True,
            "automatic_tags": True,
        }
        self.write(".github/workflows/release.yml", '''on: [push]
jobs:
  release:
    steps:
      - run: gh release create "$VERSION"
''')
        checks = contract.check_publication(self.profile, self.root)
        self.assertEqual(next(item for item in checks if item["requirement"] == "publication_policy")["status"], "pass")
        result = next(item for item in checks if item["requirement"] == "publication_workflows")
        self.assertEqual(result["status"], "not_verified")
        self.assertEqual(result["findings"][0]["command"], "gh release create")

    def test_unsupported_publication_policy_fails_closed(self):
        self.profile["publication"] = {
            "default_branch": "main",
            "github_releases": True,
            "automatic_tags": False,
        }
        checks = contract.check_publication(self.profile, self.root)
        self.assertEqual(next(item for item in checks if item["requirement"] == "publication_policy")["status"], "fail")

    def test_publication_wrapper_is_unknown_and_continuation_detected(self):
        self.write(".github/workflows/check.yml", 'jobs:\n  check:\n    steps:\n      - run: ./scripts/publish.sh\n')
        checks = contract.check_publication(self.profile, self.root)
        self.assertEqual(next(item for item in checks if item["requirement"] == "publication_workflows")["status"], "not_verified")
        self.assertEqual(contract.forbidden_shell_commands("gh release \\\ncreate v1"), ["gh release create"])
        self.assertEqual(contract.forbidden_shell_commands("git tag"), [])

    def test_malformed_workflow_steps_report_failure(self):
        self.write(".github/workflows/check.yml", 'jobs:\n  check:\n    steps: null\n')
        checks = contract.check_publication(self.profile, self.root)
        self.assertEqual(next(item for item in checks if item["requirement"] == "publication_workflows")["status"], "fail")

    def test_origin_lookalike_host_cannot_pass_identity(self):
        def fake_git(root, *args):
            if args[0] == "config":
                return "https://evil.example/NikaSir/ha-example.git"
            if args[0] == "rev-parse":
                return "a" * 40
            return ""
        with patch.object(contract, "git_value", side_effect=fake_git):
            checks = contract.check_identity(self.profile, self.root)
        self.assertEqual(next(item for item in checks if item["requirement"] == "repository_identity")["status"], "not_verified")

    def test_dirty_worktree_cannot_pass_source_pin(self):
        def fake_git(root, *args):
            if args[0] == "config":
                return "git@github.com:NikaSir/ha-example.git"
            if args[0] == "rev-parse":
                return "a" * 40
            return " M custom_components/example/const.py"
        with patch.object(contract, "git_value", side_effect=fake_git):
            checks = contract.check_identity(self.profile, self.root)
        self.assertEqual(next(item for item in checks if item["requirement"] == "source_identity")["status"], "not_verified")

    def test_release_action_and_duplicate_job_names_fail(self):
        self.write(".github/workflows/one.yml", "jobs:\n  validate:\n    steps:\n      - uses: softprops/action-gh-release@v2\n")
        self.write(".github/workflows/two.yml", "jobs:\n  validate:\n    steps:\n      - run: echo ok\n")
        checks = contract.check_publication(self.profile, self.root)
        self.assertEqual(next(item for item in checks if item["requirement"] == "publication_workflows")["status"], "fail")
        self.assertEqual(next(item for item in checks if item["requirement"] == "ci_job_identity")["status"], "fail")

    def test_profile_path_traversal_is_malformed(self):
        for path in ("../secret", "/etc/passwd", "a/../../secret", "a\\secret"):
            with self.subTest(path=path):
                profile = copy.deepcopy(self.profile)
                profile["artifacts"][0]["path"] = path
                with self.assertRaises(contract.InvalidInput):
                    self.checked_profile(profile)

    def test_symlink_and_import_escaping_root_rejected(self):
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(contract.InvalidInput):
            contract.local_path(self.root, "escape/secret")
        self.write("custom_components/example/frontend/panel.js", 'import "../../../../outside.js";')
        with self.assertRaises(contract.InvalidInput):
            contract.import_graph(self.root, self.profile["artifacts"][0]["path"])

    def test_repository_dot_paths_rejected(self):
        for name in (".", "..", ".other"):
            profile = copy.deepcopy(self.profile)
            profile["repository"] = f"NikaSir/{name}"
            with self.assertRaises(contract.InvalidInput):
                self.checked_profile(profile)

    def test_valid_schema_is_not_a_compliance_claim(self):
        self.checked_profile()
        registry = self.root / "registry"
        registry.mkdir()
        (registry / "example.json").write_text(json.dumps(self.profile))
        self.assertEqual(contract.main(["schema", "--registry", str(registry)]), 0)
        self.assertEqual(contract.main(["validate", "--profile", str(self.root / "profile.json"), "--root", str(self.root)]), 1)

    def test_missing_checkout_gives_not_verified_and_strict_failure(self):
        profile = self.checked_profile()
        report = contract.validate_repository(profile, self.root / "missing")
        self.assertEqual(report["status"], "not_verified")

    def test_open_finding_cannot_be_waived_by_other_passes(self):
        self.profile["findings"] = [{"id": "A01", "requirement": "command_safety", "status": "open", "note": "Known command defect"}]
        report = contract.validate_repository(self.checked_profile(), self.root)
        self.assertTrue(any(item.get("finding") == "A01" and item["status"] == "fail" for item in report["requirements"]))

    def test_profile_commands_are_not_accepted(self):
        self.profile["commands"] = ["touch should-not-exist"]
        with self.assertRaises(contract.InvalidInput):
            self.checked_profile()


if __name__ == "__main__":
    unittest.main()
