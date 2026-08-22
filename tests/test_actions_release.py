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
    assert manifest["version"] == "0.13.0"
    assert set(manifest["dependencies"]) == {"frontend", "http"}

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
    app_shell = repo_schema["properties"]["spec"]["properties"]["app_shell"]["properties"]
    assert app_shell["active"]["enum"] == ["home", "actions", "infrastructure"]
    assert set(app_shell["routes"]["properties"]) == {
        "home",
        "actions",
        "infrastructure",
    }


def test_app_shell_module_uses_public_cache_busted_static_path() -> None:
    const_source = (
        ROOT / "custom_components" / "contract_generated_ui" / "const.py"
    ).read_text(encoding="utf-8")
    assert 'APP_SHELL_STATIC_PATH = f"/{DOMAIN}/frontend/{APP_SHELL_FILENAME}"' in const_source
    assert 'APP_SHELL_MODULE_VERSION = "0.13.0"' in const_source
    assert 'APP_SHELL_MODULE_URL = f"{APP_SHELL_STATIC_PATH}?v={APP_SHELL_MODULE_VERSION}"' in const_source
    assert '"/api/contract_generated_ui/frontend"' not in const_source
