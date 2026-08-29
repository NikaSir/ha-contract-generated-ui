from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "custom_components" / "contract_generated_ui" / "frontend" / "dist" / "nikas-rooms-v11.js"
INIT = ROOT / "custom_components" / "contract_generated_ui" / "__init__.py"
CONST = ROOT / "custom_components" / "contract_generated_ui" / "const.py"
ROOMS_PANEL = ROOT / "custom_components" / "contract_generated_ui" / "rooms_panel.py"


def test_rooms_v11_uses_live_home_assistant_registries():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'config/area_registry/list' in source
    assert 'config/device_registry/list' in source
    assert 'config/entity_registry/list' in source
    assert 'config/label_registry/list' in source
    assert 'normArea' in source
    assert 'labelsOf' in source


def test_rooms_v11_matches_numbered_area_names():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'function normArea(v)' in source
    assert 'normArea(a.name)===norm(def.name)' in source
    assert 'norm(a.area_id)===norm(def.name)' in source


def test_rooms_v11_applies_operational_admission_policy():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'const ACTIVE_LABEL="v_ekspluatatsii"' in source
    assert '"rezerv"' in source
    assert '"na_obsluzhivanii"' in source
    assert '"trebuet_zameny"' in source
    assert '"vyvedeno_iz_ekspluatatsii"' in source
    assert 'operational(d)' in source


def test_rooms_v11_keeps_diagnostics_and_native_more_info():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'Диагностика' in source
    assert 'data-entity' in source
    assert 'hass-more-info' in source
    assert 'room.devices.map' in source
    assert 'labelsOf(d)' in source


def test_rooms_v11_is_registered_and_legacy_runtime_is_not_loaded():
    init_source = INIT.read_text(encoding="utf-8")
    const_source = CONST.read_text(encoding="utf-8")
    panel_source = ROOMS_PANEL.read_text(encoding="utf-8")

    assert 'ROOMS_PANEL_STATIC_PATH' in init_source
    assert 'async_register_rooms_panel' in init_source
    assert 'async_unregister_rooms_panel' in init_source
    assert 'add_extra_js_url(hass, ROOMS_EQUIPMENT_MODULE_URL)' not in init_source
    assert 'add_extra_js_url(hass, ROOMS_LIVE_MODULE_URL)' not in init_source
    assert 'add_extra_js_url(hass, ROOMS_DIAGNOSTICS_MODULE_URL)' not in init_source

    assert 'ROOMS_PANEL_FILENAME = "dist/nikas-rooms-v11.js"' in const_source
    assert 'ROOMS_PANEL_BUILD = "1100b001"' in const_source
    assert 'ROOMS_PANEL_MODULE_URL' in const_source
    assert 'ROOMS_PANEL_WEB_COMPONENT = "nikas-rooms-v11"' in panel_source
    assert 'ROOMS_PANEL_URL_PATH = "dashboard-rooms"' in panel_source
