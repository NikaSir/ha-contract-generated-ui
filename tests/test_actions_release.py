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
    assert manifest["version"] == "0.20.0"
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
    assert "infrastructure_summary_v1" in enum_values
    assert "subpanel_placeholder_v1" in enum_values
    assert "subpanel" in repo_schema["properties"]["spec"]["properties"]

    navigation_schema = json.loads(
        (ROOT / "schemas" / "navigation.schema.json").read_text(encoding="utf-8")
    )
    packaged_navigation_schema = json.loads(
        (
            ROOT
            / "custom_components"
            / "contract_generated_ui"
            / "schemas"
            / "navigation.schema.json"
        ).read_text(encoding="utf-8")
    )
    assert navigation_schema == packaged_navigation_schema

    app_shell = repo_schema["properties"]["spec"]["properties"]["app_shell"]["properties"]
    assert app_shell["active"]["enum"] == ["home", "actions", "infrastructure"]
    assert set(app_shell["routes"]["properties"]) == {
        "home",
        "actions",
        "infrastructure",
    }


def test_frontend_bundle_and_shared_generated_panel_host_are_packaged() -> None:
    frontend_root = ROOT / "custom_components" / "contract_generated_ui" / "frontend"
    bundle = (frontend_root / "nikas-ui.js").read_text(encoding="utf-8")
    panel_bundle = (frontend_root / "nikas-generated-subpanel.js").read_text(encoding="utf-8")

    assert 'const BAR_ID = "nikas-global-tabbar"' in bundle
    assert 'const REGISTRY_URL = "/contract_generated_ui/navigation.json"' in bundle
    assert "position:fixed" in bundle
    assert 'window.addEventListener("location-changed"' in bundle
    assert "Promise.allSettled" in bundle
    assert 'import("./nikas-app-shell.js")' in bundle
    assert 'import("./nikas-infrastructure-summary.js")' in bundle

    assert 'const ELEMENT_NAME = "nikas-generated-subpanel"' in panel_bundle
    assert "mdi:arrow-left" in panel_bundle
    assert "mdi:refresh" in panel_bundle
    assert "position:fixed" in panel_bundle
    assert "safe-area-inset-bottom" in panel_bundle
    assert "ZONT" not in panel_bundle
    assert "StarLine" not in panel_bundle

    const_source = (
        ROOT / "custom_components" / "contract_generated_ui" / "const.py"
    ).read_text(encoding="utf-8")
    assert 'UI_BUNDLE_FILENAME = "nikas-ui.js"' in const_source
    assert 'UI_BUNDLE_BUILD = "b004"' in const_source
    assert 'GENERATED_SUBPANEL_FILENAME = "nikas-generated-subpanel.js"' in const_source
    assert 'GENERATED_SUBPANEL_BUILD = "b004"' in const_source
    assert "GENERATED_SUBPANEL_MODULE_URL" in const_source
    assert 'NAVIGATION_REGISTRY_FILENAME = "navigation.json"' in const_source

    init_source = (
        ROOT / "custom_components" / "contract_generated_ui" / "__init__.py"
    ).read_text(encoding="utf-8")
    assert "GENERATED_SUBPANEL_STATIC_PATH" in init_source
    assert "GENERATED_SUBPANEL_FILENAME" in init_source
    assert "async_register_generated_subpanels" in init_source
    assert "strip_standalone_navigation_groups" in init_source
    assert "add_extra_js_url(hass, UI_BUNDLE_MODULE_URL)" in init_source
    assert "remove_extra_js_url(hass, UI_BUNDLE_MODULE_URL)" in init_source

    doc = (ROOT / "docs" / "FRONTEND_RESOURCE.md").read_text(encoding="utf-8")
    assert "автоматически" in doc.lower()
    assert "b004" in doc
    assert "nikas-generated-subpanel.js" in doc
