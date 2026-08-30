from pathlib import Path

from custom_components.contract_generated_ui.rooms_panel import build_rooms_registry_bootstrap

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
    assert 'diagnosticDevices.filter((device)' in source
    assert 'hasExcludedLabel(entity)' in source
    assert 'if (entity.device_id) return deviceIds.has(entity.device_id);' in source
    assert 'return operational(entity);' in source


def test_rooms_v11_keeps_non_operational_inventory_in_diagnostics():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'diagnosticDevices: []' in source
    assert 'diagnosticEntities: []' in source
    assert 'diagnosticStandalone: []' in source
    assert 'room.diagnosticDevices.map' in source
    assert 'room.diagnosticEntities.filter' in source
    assert 'room.diagnosticStandalone.map' in source


def test_rooms_v11_explains_status_and_opening_type():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'function openingKind(entity, hass)' in source
    assert '"Окна"' in source
    assert '"Двери"' in source
    assert '"Ворота"' in source
    assert '"Роллеты"' in source
    assert 'Система не настроена' in source
    assert 'Нет датчиков' in source
    assert 'Соединение с HA потеряно' in source
    assert 'Недоступно ${unavailable}' in source
    assert 'Состояние неизвестно' in source


def test_rooms_v11_overview_does_not_stretch_floors_and_respects_safe_area():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'justify-content:flex-start' in source
    assert 'justify-content:space-between' not in source
    assert 'env(safe-area-inset-bottom,0px)' in source


def test_rooms_v11_builds_operational_and_diagnostic_views_from_labels():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'const CLIMATE_LABEL = "datchik_klimata_pomeshcheniia"' in source
    assert 'isPrimaryClimateEntity(room, entity)' in source
    assert 'labelsOf(entity).includes(CLIMATE_LABEL)' in source
    assert 'Дополнительные климатические датчики' in source
    assert 'Диагностика' in source
    assert 'data-filter' in source
    assert 'applyDiagnosticFilter(filter)' in source
    assert 'room.diagnosticStandalone.map' in source
    assert 'hass-more-info' in source


def test_rooms_v11_patches_state_without_rebuilding_the_shell():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'mountShell()' in source
    assert 'if (this._mounted) return;' in source
    assert 'scheduleStatePatch()' in source
    assert 'node.textContent !== value' in source
    assert 'card.classList.toggle(`tone-${tone}`' in source
    assert 'this.shadowRoot.innerHTML' not in source[source.index('patchStates() {'):source.index('scheduleChromeSync() {')]


def test_rooms_v11_recovers_from_registry_loading_races_and_timeouts():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'const REGISTRY_TIMEOUT_MS = 12000' in source
    assert 'if (!this.isConnected) return;' in source
    assert 'this._loadGeneration += 1;' in source
    assert 'generation !== this._loadGeneration' in source
    assert 'Registry request timed out' in source
    assert 'id="retry-registries"' in source
    assert 'Не удалось прочитать реестры Home Assistant.' in source
    assert 'registrySnapshot()' in source
    assert 'Object.values(hass.labels)' in source
    assert 'this.waitForHass();' in source
    assert 'Панель не получила данные от Home Assistant.' in source
    assert 'const LOAD_WATCHDOG_MS = 6000' in source
    assert 'this.panelRegistryBootstrap()' in source
    assert 'this.adoptRegistries(bootstrap)' in source
    assert 'document.querySelector("home-assistant")?.hass' in source


def test_rooms_registry_bootstrap_is_compact_and_frontend_compatible():
    document = {
        "spec": {
            "areas": [
                {"area_id": "bathroom", "name": "01 — Ванная"},
                {"area_id": "office", "name": "Кабинет"},
            ],
            "devices": [
                {
                    "device_id": "bath-sensor",
                    "area_id": "bathroom",
                    "labels": ["v_ekspluatatsii"],
                    "disabled": False,
                },
                {"device_id": "office-sensor", "area_id": "office", "disabled": False},
            ],
            "entities": [
                {
                    "entity_id": "binary_sensor.bath_window",
                    "device_id": "bath-sensor",
                    "labels": ["v_ekspluatatsii"],
                    "disabled": False,
                    "hidden": False,
                },
                {
                    "entity_id": "sensor.office_temperature",
                    "device_id": "office-sensor",
                    "disabled": False,
                    "hidden": False,
                },
            ],
            "labels": [
                {"label_id": "v_ekspluatatsii", "name": "В эксплуатации"},
                {"label_id": "unrelated", "name": "Лишний"},
            ],
        }
    }

    bootstrap = build_rooms_registry_bootstrap(document)

    assert bootstrap["areas"] == [{"area_id": "bathroom", "name": "01 — Ванная"}]
    assert [device["id"] for device in bootstrap["devices"]] == ["bath-sensor"]
    assert bootstrap["devices"][0]["disabled_by"] is None
    assert [entity["entity_id"] for entity in bootstrap["entities"]] == [
        "binary_sensor.bath_window"
    ]
    assert bootstrap["entities"][0]["hidden_by"] is None
    assert bootstrap["labels"] == [
        {"label_id": "v_ekspluatatsii", "name": "В эксплуатации"}
    ]


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
    assert 'ROOMS_PANEL_BUILD = "1100b007"' in const_source
    assert 'ROOMS_PANEL_MODULE_URL' in const_source
    assert 'ROOMS_PANEL_WEB_COMPONENT = "nikas-rooms-v11-10824"' in panel_source
    assert 'ROOMS_PANEL_URL_PATH = "dashboard-rooms"' in panel_source
    assert '"ui_version": "11.0.0"' in panel_source
    assert '"registry_bootstrap": registry_bootstrap' in panel_source
