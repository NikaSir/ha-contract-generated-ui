from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_release_version_and_schema_are_packaged() -> None:
    manifest = json.loads((ROOT / "custom_components" / "contract_generated_ui" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.37.5"
    assert set(manifest["dependencies"]) == {"frontend", "http"}
    assert manifest["after_dependencies"] == ["lovelace"]

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

    assert (ROOT / "contracts" / "actions_home.yaml").read_bytes() == (ROOT / "custom_components" / "contract_generated_ui" / "bundled_sources" / "contracts" / "actions_home.yaml").read_bytes()
    assert (ROOT / "manifests" / "actions.yaml").read_bytes() == (ROOT / "custom_components" / "contract_generated_ui" / "bundled_sources" / "manifests" / "actions.yaml").read_bytes()
    assert (ROOT / "navigation" / "main.yaml").read_bytes() == (ROOT / "custom_components" / "contract_generated_ui" / "bundled_sources" / "navigation" / "main.yaml").read_bytes()


def test_repository_and_integration_ship_the_same_recognizable_icon() -> None:
    icon_path = ROOT / "custom_components" / "contract_generated_ui" / "brand" / "icon.png"
    icon = icon_path.read_bytes()
    assert icon[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", icon[16:24])
    assert (width, height) == (256, 256)
    assert icon[25] == 6
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "custom_components/contract_generated_ui/brand/icon.png" in readme


def test_frontend_bundle_and_generated_panel_hosts_are_packaged() -> None:
    frontend_root = ROOT / "custom_components" / "contract_generated_ui" / "frontend"
    bundle = (frontend_root / "nikas-ui.js").read_text(encoding="utf-8")
    hero_bundle = (frontend_root / "nikas-house-hero.js").read_text(encoding="utf-8")
    hero_asset = frontend_root / "assets" / "house-hero-photo-day-v3.webp"
    zoom_bundle = (frontend_root / "nikas-panel-zoom.js").read_text(encoding="utf-8")
    shell_bundle = (frontend_root / "nikas-specialized-panel-shell.js").read_text(encoding="utf-8")
    panel_bundle = (frontend_root / "nikas-generated-subpanel.js").read_text(encoding="utf-8")
    house_panel_bundle = (frontend_root / "nikas-house-overview.js").read_text(encoding="utf-8")
    infrastructure_panel_bundle = (frontend_root / "nikas-infrastructure-overview.js").read_text(encoding="utf-8")
    rooms_bundle = (frontend_root / "dist" / "nikas-rooms-v11.js").read_text(encoding="utf-8")

    assert 'const BAR_ID = "nikas-global-tabbar"' in bundle
    assert 'const BOOTSTRAP_VERSION = "b016"' in bundle
    assert "new MutationObserver" in bundle
    assert "chromeHostObserver.observe(document.body, { childList: true, subtree: true })" in bundle
    assert 'const REGISTRY_URL = "/contract_generated_ui/navigation.json"' in bundle
    assert 'import "/contract_generated_ui/frontend/nikas-house-hero.js?build=b013"' in bundle
    assert 'const ACTIONS_HEADER_MODEL = {' in bundle
    assert "ROOM_VIEW_TITLES" in bundle
    assert "roomsHeaderModel" in bundle
    assert 'model?.active === "rooms" ? roomsHeaderModel(pathname) : null' in bundle
    assert 'title: "Действия · v11.0"' in bundle
    assert 'subtitle: "Быстрые команды · UI v0.37.5"' in bundle
    assert 'model?.active === "actions" ? ACTIONS_HEADER_MODEL : null' in bundle
    assert "position:fixed" in bundle
    assert 'id="menu"' in bundle
    assert 'icon="mdi:menu"' in bundle
    assert 'new CustomEvent("hass-toggle-menu"' in bundle
    assert "mdi:arrow-left" not in bundle
    assert "--mdc-icon-size:28px" in bundle
    assert "font-size:23px" in bundle
    assert "font-size:14px" in bundle

    assert 'const ELEMENT_NAME = "nikas-house-hero"' in hero_bundle
    assert "/contract_generated_ui/frontend/assets/house-hero-photo-day-v3.webp?build=0340b001" in hero_bundle
    assert "base64" not in hero_bundle.lower()
    assert "https://" not in hero_bundle
    assert "rgba(255,255,255,.86)" in hero_bundle
    assert hero_asset.exists()
    assert 'const ELEMENT_NAME = "nikas-house-overview"' in house_panel_bundle
    assert 'new CustomEvent("hass-toggle-menu"' in house_panel_bundle
    assert "translate3d(${x}px, ${y}px, 0) scale(${scale})" in house_panel_bundle
    assert 'const ELEMENT_NAME = "nikas-infrastructure-overview"' in infrastructure_panel_bundle
    assert 'new CustomEvent("hass-toggle-menu"' in infrastructure_panel_bundle
    assert "translate3d(${x}px, ${y}px, 0) scale(${scale})" in infrastructure_panel_bundle

    assert "class ZoomController" in zoom_bundle
    assert 'const DEFAULT_MIN = 0.75' in zoom_bundle
    assert 'const DEFAULT_MAX = 2.0' in zoom_bundle
    assert "touchstart" in zoom_bundle and "touchmove" in zoom_bundle
    assert "window.localStorage" in zoom_bundle
    assert "window.NikasPanelZoom" in zoom_bundle
    assert "this.state.scale <= 1" in zoom_bundle
    assert "this.viewport.scrollTop = 0" in zoom_bundle
    assert "pointercancel" in zoom_bundle
    assert '"nikas-generated-subpanel"' in shell_bundle
    assert '"nikas-generated-zont"' not in shell_bundle
    assert '"NIKAS-GENERATED-ZONT"' not in zoom_bundle
    assert "window.NikasPanelZoom.attach" in shell_bundle
    assert "env(safe-area-inset-top,0px)" in shell_bundle
    assert "env(safe-area-inset-bottom,0px)" in shell_bundle
    assert "grid-template-columns:52px minmax(0,1fr) 52px" in shell_bundle

    assert 'const ELEMENT_NAME = "nikas-generated-subpanel"' in panel_bundle
    assert 'icon="mdi:menu"' in panel_bundle
    assert 'new CustomEvent("hass-toggle-menu"' in panel_bundle
    assert "mdi:arrow-left" not in panel_bundle
    assert 'class="canvas-viewport"' in panel_bundle
    assert 'class="work-canvas"' in panel_bundle
    assert ".callService(" not in panel_bundle
    assert 'type: "call_service"' not in panel_bundle
    assert not (frontend_root / "nikas-generated-zont.js").exists()
    assert not (frontend_root / "nikas-generated-zont-v080.js").exists()
    assert not (frontend_root / "assets" / "zont-boiler-casing-v0812.webp").exists()
    assert not (frontend_root / "assets" / "zont-dhw-shell-v0812.webp").exists()

    # Rooms v11: one autonomous production runtime, registry-driven model,
    # stable state patching and no legacy Lovelace DOM reconciliation.
    assert 'const ELEMENT_NAME = "nikas-rooms-v11-10824"' in rooms_bundle
    assert 'const UI_VERSION = "11.0.0"' in rooms_bundle
    assert 'const ACTIVE_LABEL = "v_ekspluatatsii"' in rooms_bundle
    assert 'const CLIMATE_LABEL = "datchik_klimata_pomeshcheniia"' in rooms_bundle
    assert "config/area_registry/list" in rooms_bundle
    assert "config/device_registry/list" in rooms_bundle
    assert "config/entity_registry/list" in rooms_bundle
    assert "config/label_registry/list" in rooms_bundle
    assert "scheduleStatePatch()" in rooms_bundle
    assert "node.textContent !== value" in rooms_bundle
    assert "data-summary-room" in rooms_bundle
    assert "Дополнительные климатические датчики" in rooms_bundle
    assert "OPENING_CLASSES" in rooms_bundle
    assert "ACTIVITY_CLASSES" in rooms_bundle
    assert 'domain(entity.entity_id) === "camera"' in rooms_bundle
    assert "data-filter" in rooms_bundle
    assert "Диагностика" in rooms_bundle
    assert "ensureTitleButton(shadow)" in rooms_bundle
    assert "button.title.rooms-return" in rooms_bundle
    assert "MutationObserver" in rooms_bundle
    assert 'const LOAD_WATCHDOG_MS = 6000' in rooms_bundle
    assert 'this._panel?.config?.registry_bootstrap' in rooms_bundle
    assert 'document.querySelector("home-assistant")?.hass' in rooms_bundle
    assert not any(line.lstrip().startswith("import ") for line in rooms_bundle.splitlines())
    assert "dynamic import" not in rooms_bundle.lower()

    const_source = (ROOT / "custom_components" / "contract_generated_ui" / "const.py").read_text(encoding="utf-8")
    assert 'UI_BUNDLE_BUILD = "b022"' in const_source
    assert 'ROOMS_PANEL_FILENAME = "dist/nikas-rooms-v11.js"' in const_source
    assert 'ROOMS_PANEL_BUILD = "1100b007"' in const_source
    assert "ROOMS_PANEL_MODULE_URL" in const_source
    assert "ROOMS_PANEL_PATH" in const_source
    assert 'PANEL_ZOOM_FILENAME = "nikas-panel-zoom.js"' in const_source
    assert 'PANEL_ZOOM_BUILD = "b002"' in const_source
    assert 'SPECIALIZED_SHELL_FILENAME = "nikas-specialized-panel-shell.js"' in const_source
    assert 'SPECIALIZED_SHELL_BUILD = "b003"' in const_source
    assert "SPECIALIZED_SHELL_MODULE_URL" in const_source
    assert 'HOUSE_HERO_BUILD = "b013"' in const_source
    assert 'HOUSE_PANEL_FILENAME = "dist/nikas-house-overview.js"' in const_source
    assert 'HOUSE_PANEL_BUILD = "b011"' in const_source
    assert 'INFRASTRUCTURE_PANEL_FILENAME = "dist/nikas-infrastructure-overview.js"' in const_source
    assert 'INFRASTRUCTURE_PANEL_BUILD = "b005"' in const_source
    assert 'HOUSE_HERO_ASSETS_STATIC_PATH = f"/{DOMAIN}/frontend/assets"' in const_source
    assert 'HOUSE_HERO_ASSET_FILENAME = "house-hero-photo-day-v3.webp"' in const_source
    assert 'HOUSE_HERO_ASSET_BUILD = "0340b001"' in const_source
    assert 'GENERATED_SUBPANEL_FILENAME = "dist/nikas-generated-subpanel.js"' in const_source
    assert 'GENERATED_SUBPANEL_BUILD = "b008"' in const_source
    assert "GENERATED_ZONT" not in const_source

    dist = frontend_root / "dist"
    for name in ("nikas-house-overview.js", "nikas-infrastructure-overview.js", "nikas-generated-subpanel.js", "nikas-rooms-v11.js"):
        packaged = (dist / name).read_text(encoding="utf-8")
        assert not any(line.lstrip().startswith("import ") for line in packaged.splitlines())

    init_source = (ROOT / "custom_components" / "contract_generated_ui" / "__init__.py").read_text(encoding="utf-8")
    assert "ROOMS_PANEL_STATIC_PATH" in init_source
    assert "StaticPathConfig(ROOMS_PANEL_STATIC_PATH" in init_source
    assert "async_register_rooms_panel" in init_source
    assert "async_unregister_rooms_panel" in init_source
    assert "add_extra_js_url(hass, ROOMS_EQUIPMENT_MODULE_URL)" not in init_source
    assert "add_extra_js_url(hass, ROOMS_LIVE_MODULE_URL)" not in init_source
    assert "add_extra_js_url(hass, ROOMS_DIAGNOSTICS_MODULE_URL)" not in init_source
    assert "PANEL_ZOOM_STATIC_PATH" in init_source
    assert "SPECIALIZED_SHELL_STATIC_PATH" in init_source
    assert "add_extra_js_url(hass, PANEL_ZOOM_MODULE_URL)" in init_source
    assert "add_extra_js_url(hass, SPECIALIZED_SHELL_MODULE_URL)" in init_source
    assert "HOUSE_HERO_STATIC_PATH" in init_source
    assert "HOUSE_PANEL_STATIC_PATH" in init_source
    assert "INFRASTRUCTURE_PANEL_STATIC_PATH" in init_source
    assert "HOUSE_HERO_ASSETS_STATIC_PATH" in init_source
    assert 'StaticPathConfig(HOUSE_HERO_ASSETS_STATIC_PATH, str(frontend_root / "assets"), False)' in init_source
    assert "add_extra_js_url(hass, HOUSE_HERO_MODULE_URL)" in init_source
    assert "GENERATED_ZONT" not in init_source
    assert "async_register_generated_subpanels" in init_source
    assert "async_register_house_panel" in init_source
    assert "async_register_infrastructure_panel" in init_source
    assert "add_extra_js_url(hass, UI_BUNDLE_MODULE_URL)" in init_source

    doc = (ROOT / "docs" / "FRONTEND_RESOURCE.md").read_text(encoding="utf-8")
    assert "автоматически" in doc.lower()
    assert "nikas-generated-subpanel.js" in doc
