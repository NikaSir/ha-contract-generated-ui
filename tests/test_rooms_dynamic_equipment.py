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
    assert 'function normArea(value)' in source
    assert 'function labelsOf(item)' in source


def test_rooms_v11_matches_numbered_area_names():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'normArea(item.name) === norm(definition.name)' in source
    assert 'norm(item.area_id) === norm(definition.name)' in source


def test_rooms_v11_applies_operational_admission_policy():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'const ACTIVE_LABEL = "v_ekspluatatsii"' in source
    assert '"rezerv"' in source
    assert '"na_obsluzhivanii"' in source
    assert '"trebuet_zameny"' in source
    assert '"vyvedeno_iz_ekspluatatsii"' in source
    assert 'operational(device)' in source
    assert 'hasExcludedLabel(entity)' in source
    assert 'entity.area_id === area.area_id && operational(entity)' in source


def test_rooms_v11_builds_operational_and_diagnostic_views_from_labels():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'const CLIMATE_LABEL = "datchik_klimata_pomeshcheniia"' in source
    assert 'isPrimaryClimateEntity(room, entity)' in source
    assert 'labelsOf(entity).includes(CLIMATE_LABEL)' in source
    assert 'Дополнительные климатические датчики' in source
    assert 'Диагностика' in source
    assert 'data-filter' in source
    assert 'applyDiagnosticFilter(filter)' in source
    assert 'room.standalone.map' in source
    assert 'hass-more-info' in source


def test_rooms_v11_patches_state_without_rebuilding_the_shell():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'mountShell()' in source
    assert 'if (this._mounted) return;' in source
    assert 'scheduleStatePatch()' in source
    assert 'node.textContent !== value' in source
    assert 'card.classList.toggle(`tone-${tone}`' in source
    assert 'this.shadowRoot.innerHTML' not in source[source.index('patchStates() {'):source.index('scheduleChromeSync() {')]


def test_rooms_v11_owns_header_version_and_hierarchical_return():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'const UI_VERSION = "11.0.0"' in source
    assert 'ensureTitleButton(shadow)' in source
    assert 'button.title.rooms-return' in source
    assert 'min-width:min(290px,100%)' in source
    assert 'color-mix(in srgb,var(--primary-color' in source
    assert 'subtitle: `Диагностика · UI v${UI_VERSION}`' in source
    assert 'backPath: room ? `/dashboard-rooms/room-${room.slug}` : ROOT_PATH' in source


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
    assert 'ROOMS_PANEL_BUILD = "1100b002"' in const_source
    assert 'ROOMS_PANEL_MODULE_URL' in const_source
    assert 'ROOMS_PANEL_WEB_COMPONENT = "nikas-rooms-v11"' in panel_source
    assert 'ROOMS_PANEL_URL_PATH = "dashboard-rooms"' in panel_source
    assert '"ui_version": "11.0.0"' in panel_source
