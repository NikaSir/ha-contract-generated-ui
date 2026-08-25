from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_release_version_and_schema_are_packaged() -> None:
    manifest = json.loads((ROOT / "custom_components" / "contract_generated_ui" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.31.1"
    assert set(manifest["dependencies"]) == {"frontend", "http"}

    repo_schema = json.loads((ROOT / "schemas" / "manifest.schema.json").read_text(encoding="utf-8"))
    packaged_schema = json.loads((ROOT / "custom_components" / "contract_generated_ui" / "schemas" / "manifest.schema.json").read_text(encoding="utf-8"))
    assert repo_schema == packaged_schema
    enum_values = repo_schema["$defs"]["view"]["properties"]["renderer"]["enum"]
    assert "actions_home_v1" in enum_values
    assert "infrastructure_summary_v1" in enum_values
    assert "subpanel_placeholder_v1" in enum_values
    assert "subpanel" in repo_schema["properties"]["spec"]["properties"]

    navigation_schema = json.loads((ROOT / "schemas" / "navigation.schema.json").read_text(encoding="utf-8"))
    packaged_navigation_schema = json.loads((ROOT / "custom_components" / "contract_generated_ui" / "schemas" / "navigation.schema.json").read_text(encoding="utf-8"))
    assert navigation_schema == packaged_navigation_schema

    assert (ROOT / "contracts" / "actions_home.yaml").read_bytes() == (
        ROOT / "custom_components" / "contract_generated_ui" / "bundled_sources" / "contracts" / "actions_home.yaml"
    ).read_bytes()
    assert (ROOT / "manifests" / "actions.yaml").read_bytes() == (
        ROOT / "custom_components" / "contract_generated_ui" / "bundled_sources" / "manifests" / "actions.yaml"
    ).read_bytes()
    assert (ROOT / "navigation" / "main.yaml").read_bytes() == (
        ROOT / "custom_components" / "contract_generated_ui" / "bundled_sources" / "navigation" / "main.yaml"
    ).read_bytes()


def test_frontend_bundle_and_generated_panel_hosts_are_packaged() -> None:
    frontend_root = ROOT / "custom_components" / "contract_generated_ui" / "frontend"
    bundle = (frontend_root / "nikas-ui.js").read_text(encoding="utf-8")
    hero_bundle = (frontend_root / "nikas-house-hero.js").read_text(encoding="utf-8")
    hero_asset = frontend_root / "assets" / "house-hero-day-v1.svg"
    panel_bundle = (frontend_root / "nikas-generated-subpanel.js").read_text(encoding="utf-8")
    zont_bundle = (frontend_root / "nikas-generated-zont.js").read_text(encoding="utf-8")

    assert 'const BAR_ID = "nikas-global-tabbar"' in bundle
    assert 'const REGISTRY_URL = "/contract_generated_ui/navigation.json"' in bundle
    assert "position:fixed" in bundle
    assert 'const ELEMENT_NAME = "nikas-house-hero"' in hero_bundle
    assert "/contract_generated_ui/frontend/assets/house-hero-day-v1.svg" in hero_bundle
    assert "base64" not in hero_bundle.lower()
    assert "https://" not in hero_bundle
    assert "rgba(255,255,255,.86)" in hero_bundle
    assert hero_asset.exists()
    assert 'const ELEMENT_NAME = "nikas-generated-subpanel"' in panel_bundle
    assert 'const ELEMENT_NAME = "nikas-generated-zont"' in zont_bundle
    assert "_boilerCard" in zont_bundle
    assert "_circuitCard" in zont_bundle
    assert "_roomCard" in zont_bundle
    assert "_meterCard" in zont_bundle
    assert "_states" in zont_bundle
    assert "_modeButtons" in zont_bundle
    assert "_mixerState" in zont_bundle
    assert 'type: "config/entity_registry/list"' in zont_bundle
    assert 'type: "config/device_registry/list"' in zont_bundle
    assert ".callService(" not in panel_bundle
    assert 'callService("button", "press"' in zont_bundle
    assert 'callService("switch"' not in zont_bundle
    assert 'callService("climate"' not in zont_bundle
    assert 'type: "call_service"' not in panel_bundle
    assert 'type: "call_service"' not in zont_bundle

    # Contract Generated UI owns only the generic renderer. ZONT-specific
    # application/UI releases are HACS-managed by NikaSir/ha-zont.
    assert not (frontend_root / "nikas-generated-zont-v080.js").exists()

    const_source = (ROOT / "custom_components" / "contract_generated_ui" / "const.py").read_text(encoding="utf-8")
    assert 'UI_BUNDLE_BUILD = "b004"' in const_source
    assert 'HOUSE_HERO_BUILD = "b004"' in const_source
    assert 'HOUSE_HERO_ASSETS_STATIC_PATH = f"/{DOMAIN}/frontend/assets"' in const_source
    assert 'HOUSE_HERO_ASSET_FILENAME = "house-hero-day-v1.svg"' in const_source
    assert 'HOUSE_HERO_ASSET_BUILD = "0310b001"' in const_source
    assert 'GENERATED_SUBPANEL_BUILD = "b006"' in const_source
    assert 'GENERATED_ZONT_FILENAME = "nikas-generated-zont.js"' in const_source
    assert 'GENERATED_ZONT_BUILD = "b005"' in const_source
    assert "GENERATED_ZONT_MODULE_URL" in const_source

    init_source = (ROOT / "custom_components" / "contract_generated_ui" / "__init__.py").read_text(encoding="utf-8")
    assert "HOUSE_HERO_STATIC_PATH" in init_source
    assert "HOUSE_HERO_ASSETS_STATIC_PATH" in init_source
    assert 'StaticPathConfig(HOUSE_HERO_ASSETS_STATIC_PATH, str(frontend_root / "assets"), False)' in init_source
    assert "add_extra_js_url(hass, HOUSE_HERO_MODULE_URL)" in init_source
    assert "GENERATED_ZONT_STATIC_PATH" in init_source
    assert "GENERATED_ZONT_FILENAME" in init_source
    assert "async_register_generated_subpanels" in init_source
    assert "add_extra_js_url(hass, UI_BUNDLE_MODULE_URL)" in init_source

    doc = (ROOT / "docs" / "FRONTEND_RESOURCE.md").read_text(encoding="utf-8")
    assert "автоматически" in doc.lower()
    assert "nikas-generated-subpanel.js" in doc
