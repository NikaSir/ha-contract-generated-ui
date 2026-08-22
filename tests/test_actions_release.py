from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_release_version_and_schema_are_packaged() -> None:
    manifest = json.loads(
        (ROOT / "custom_components" / "contract_generated_ui" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["version"] == "0.11.0"
    assert "frontend" in manifest["dependencies"]

    repo_schema = json.loads(
        (ROOT / "schemas" / "manifest.schema.json").read_text(encoding="utf-8")
    )
    packaged_schema = json.loads(
        (
            ROOT
            / "custom_components"
            / "contract_generated_ui"
            / "schemas"
            / "manifest.schema.json"
        ).read_text(encoding="utf-8")
    )
    assert repo_schema == packaged_schema
    enum_values = repo_schema["$defs"]["view"]["properties"]["renderer"]["enum"]
    assert "actions_home_v1" in enum_values
    assert repo_schema["properties"]["spec"]["properties"]["app_shell"]["properties"][
        "active"
    ]["enum"] == ["home", "actions", "infrastructure"]
