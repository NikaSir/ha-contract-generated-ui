"""Canonical baseline parity and refusal tests for repository inspection."""
from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "nikas_standard_baseline_contract",
    REPOSITORY_ROOT / "scripts/nikas_repository_contract.py",
)
contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract)


def panel_profile():
    return {
        "standards": {"applicable": True, "declaration_path": ".nikas-ui-standard.json"},
        "artifacts": [{"id": "panel"}],
    }


def metadata_checks(checks):
    return [item for item in checks if item["requirement"] == "ui_standard"]


class CurrentCheckoutBaselineTests(unittest.TestCase):
    def test_current_canonical_documents_pass_metadata_without_proving_behavior(self):
        checks = contract.check_standards(panel_profile(), REPOSITORY_ROOT)
        self.assertEqual([item["status"] for item in metadata_checks(checks)], ["pass"] * 4)
        behavior = next(item for item in checks if item["requirement"] == "ui_behavior")
        self.assertEqual(behavior["status"], "not_verified")

    def test_report_baseline_records_actual_canonical_inputs(self):
        declaration_path = REPOSITORY_ROOT / ".nikas-ui-standard.json"
        declaration = json.loads(declaration_path.read_text(encoding="utf-8"))
        policy = contract.load_standard_baseline()
        self.assertEqual(policy["contract_version"], 1)
        self.assertEqual(policy["ui_version"], declaration["version"])
        self.assertEqual(policy["navigation_version"], declaration["navigation_contract_version"])
        self.assertEqual(policy["ui_sha256"], contract.digest(REPOSITORY_ROOT / declaration["standard_path"]))
        self.assertEqual(policy["navigation_sha256"], contract.digest(REPOSITORY_ROOT / declaration["navigation_contract_path"]))
        self.assertEqual(policy["declaration_sha256"], contract.digest(declaration_path))
        self.assertEqual(policy["canonical_repository"], "NikaSir/ha-contract-generated-ui")
        self.assertEqual(policy["canonical_revision"], contract.git_value(REPOSITORY_ROOT, "rev-parse", "HEAD"))


class BaselineIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.canonical = self.root / "canonical"
        self.consumer = self.root / "consumer"
        self.canonical.mkdir()
        self.consumer.mkdir()
        self.declaration = {
            "role": "registry",
            "version": "2.2",
            "navigation_contract_version": "1.2",
            "standard_path": "docs/ui.md",
            "navigation_contract_path": "docs/navigation.md",
        }
        self.write(self.canonical, "docs/ui.md", "# NikaS Specialized Panel UI Standard v2.2\n\nCurrent UI requirements.\n")
        self.write(self.canonical, "docs/navigation.md", "# NikaS Panel Navigation and Return Contract v1.2\n\nCurrent navigation requirements.\n")
        self.refresh_declaration()
        self.copy_to_consumer()
        baseline_root = patch.object(contract, "TOOL_ROOT", self.canonical)
        baseline_root.start()
        self.addCleanup(baseline_root.stop)

    def write(self, root, relative, text):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_declaration(self, root, declaration):
        return self.write(root, ".nikas-ui-standard.json", json.dumps(declaration))

    def refresh_declaration(self):
        for path_key, hash_key in (
            ("standard_path", "standard_sha256"),
            ("navigation_contract_path", "navigation_contract_sha256"),
        ):
            self.declaration[hash_key] = contract.digest(self.canonical / self.declaration[path_key])
        self.write_declaration(self.canonical, self.declaration)

    def copy_to_consumer(self):
        for key in ("standard_path", "navigation_contract_path"):
            relative = self.declaration[key]
            self.write(self.consumer, relative, (self.canonical / relative).read_text(encoding="utf-8"))
        self.write_declaration(self.consumer, {**self.declaration, "role": "mirror"})

    def changed_consumer(self):
        declaration = {**self.declaration, "role": "registry"}
        for path_key, hash_key in (
            ("standard_path", "standard_sha256"),
            ("navigation_contract_path", "navigation_contract_sha256"),
        ):
            path = self.consumer / declaration[path_key]
            path.write_text(path.read_text(encoding="utf-8") + "Consumer-only requirements.\n", encoding="utf-8")
            declaration[hash_key] = contract.digest(path)
        self.write_declaration(self.consumer, declaration)
        return declaration

    def registry_profile(self):
        profile = json.loads((REPOSITORY_ROOT / "deployments/repository-contracts/nikasir-github.json").read_text(encoding="utf-8"))
        profile["evidence"] = []
        profile["findings"] = []
        return profile

    def test_consumer_cannot_authorize_simultaneous_document_and_hash_changes(self):
        declaration = self.changed_consumer()
        profile = panel_profile()
        profile["policy"] = {"ui_sha256": declaration["standard_sha256"]}
        checks = metadata_checks(contract.check_standards(profile, self.consumer))
        self.assertEqual([item["status"] for item in checks], ["pass", "pass", "fail", "fail"])
        self.assertEqual(checks[2]["required_hash"], self.declaration["standard_sha256"])
        self.assertEqual(checks[3]["required_hash"], self.declaration["navigation_contract_sha256"])

    def test_previous_same_version_mirror_fails_after_canonical_content_changes(self):
        for relative in ("docs/ui.md", "docs/navigation.md"):
            path = self.canonical / relative
            path.write_text(path.read_text(encoding="utf-8") + "New required behavior.\n", encoding="utf-8")
        self.refresh_declaration()
        checks = metadata_checks(contract.check_standards(panel_profile(), self.consumer))
        self.assertEqual([item["status"] for item in checks], ["pass", "pass", "fail", "fail"])

    def test_consistent_canonical_update_is_adopted_without_inspector_changes(self):
        original = contract.load_standard_baseline()
        for relative in ("docs/ui.md", "docs/navigation.md"):
            path = self.canonical / relative
            path.write_text(path.read_text(encoding="utf-8") + "New required behavior.\n", encoding="utf-8")
        self.refresh_declaration()
        self.copy_to_consumer()
        updated = contract.load_standard_baseline()
        self.assertNotEqual(updated["ui_sha256"], original["ui_sha256"])
        self.assertNotEqual(updated["navigation_sha256"], original["navigation_sha256"])
        self.assertNotEqual(updated["declaration_sha256"], original["declaration_sha256"])
        checks = contract.check_standards(panel_profile(), self.consumer)
        self.assertEqual([item["status"] for item in metadata_checks(checks)], ["pass"] * 4)

    def test_missing_malformed_or_non_object_canonical_declaration_is_rejected(self):
        path = self.canonical / ".nikas-ui-standard.json"
        path.unlink()
        with self.assertRaises(contract.InvalidInput):
            contract.load_standard_baseline()
        for content in ("{", "[]", "null", "{}"):
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(contract.InvalidInput):
                    contract.load_standard_baseline()

    def test_canonical_role_and_version_fields_must_be_valid(self):
        changes = [
            {"role": "mirror"}, {"role": None},
            {"version": "invalid"}, {"version": 2.2}, {"version": None},
            {"navigation_contract_version": True}, {"navigation_contract_version": ""},
        ]
        for change in changes:
            with self.subTest(change=change):
                self.write_declaration(self.canonical, {**self.declaration, **change})
                with self.assertRaises(contract.InvalidInput):
                    contract.load_standard_baseline()

    def test_canonical_document_hash_mismatch_is_rejected(self):
        for field in ("standard_sha256", "navigation_contract_sha256"):
            for value in ("0" * 64, "not-a-sha256", None):
                with self.subTest(field=field, value=value):
                    self.write_declaration(self.canonical, {**self.declaration, field: value})
                    with self.assertRaises(contract.InvalidInput):
                        contract.load_standard_baseline()

    def test_document_heading_version_must_match_declaration_even_with_correct_hash(self):
        for relative, old, new in (
            ("docs/ui.md", "v2.2", "v2.1"),
            ("docs/navigation.md", "v1.2", "v1.1"),
        ):
            with self.subTest(document=relative):
                path = self.canonical / relative
                original = path.read_text(encoding="utf-8")
                path.write_text(original.replace(old, new), encoding="utf-8")
                self.refresh_declaration()
                with self.assertRaises(contract.InvalidInput):
                    contract.load_standard_baseline()
                path.write_text(original, encoding="utf-8")
                self.refresh_declaration()

    def test_canonical_paths_cannot_escape_checkout(self):
        outside = self.write(self.root, "outside.md", "outside baseline\n")
        link = self.canonical / "linked.md"
        link.symlink_to(outside)
        for relative in ("../outside.md", str(outside), "linked.md"):
            with self.subTest(path=relative):
                self.write_declaration(self.canonical, {
                    **self.declaration, "standard_path": relative,
                    "standard_sha256": contract.digest(outside),
                })
                with self.assertRaises(contract.InvalidInput):
                    contract.load_standard_baseline()

    def test_conflicting_canonical_version_alias_is_rejected(self):
        self.write_declaration(self.canonical, {**self.declaration, "standard_version": "2.1"})
        with self.assertRaises(contract.InvalidInput):
            contract.load_standard_baseline()

    def test_conflicting_consumer_version_alias_fails_metadata(self):
        self.write_declaration(self.consumer, {**self.declaration, "standard_version": "2.1"})
        checks = metadata_checks(contract.check_standards(panel_profile(), self.consumer))
        self.assertEqual(checks[0]["status"], "fail")

    def test_repository_report_keeps_canonical_provenance_separate_from_consumer(self):
        def revision(root, *args):
            return "a" * 40 if root.resolve() == self.canonical.resolve() else "b" * 40

        with patch.object(contract, "git_value", side_effect=revision):
            expected = contract.load_standard_baseline()
            report = contract.validate_repository(self.registry_profile(), self.consumer)
        self.assertEqual(report["policy"], expected)
        self.assertEqual(report["policy"]["canonical_revision"], "a" * 40)
        self.assertEqual(report["observed_revision"], "b" * 40)

    def schema_run(self):
        registry = self.root / "registry"
        self.write(registry, "consumer.json", json.dumps(self.registry_profile()))
        report_path = self.root / "schema-report.json"
        with patch("sys.stdout", new_callable=io.StringIO), patch("sys.stderr", new_callable=io.StringIO):
            code = contract.main(["schema", "--registry", str(registry), "--json-output", str(report_path)])
        return code, json.loads(report_path.read_text(encoding="utf-8"))

    def test_schema_report_includes_verified_canonical_baseline(self):
        code, report = self.schema_run()
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["policy"], contract.load_standard_baseline())
        self.assertIn("no product compliance asserted", report["scope"])

    def test_schema_command_cannot_pass_with_corrupted_canonical_baseline(self):
        self.write_declaration(self.canonical, {**self.declaration, "standard_sha256": "0" * 64})
        code, report = self.schema_run()
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "fail")
        self.assertTrue(report["errors"])


if __name__ == "__main__":
    unittest.main()
