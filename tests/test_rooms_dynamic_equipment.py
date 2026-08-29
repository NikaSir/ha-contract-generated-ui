from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "custom_components" / "contract_generated_ui" / "frontend" / "nikas-rooms-equipment.js"
INIT = ROOT / "custom_components" / "contract_generated_ui" / "__init__.py"
CONST = ROOT / "custom_components" / "contract_generated_ui" / "const.py"


def test_rooms_equipment_uses_live_home_assistant_registries():
    source = FRONTEND.read_text(encoding="utf-8")
    assert 'config/area_registry/list' in source
    assert 'config/device_registry/list' in source
    assert 'config/entity_registry/list' in source
    assert 'config/label_registry/list' in source
    assert 'effectiveAreaId' in source
    assert 'labelIds' in source
    assert 'HIDE_LABEL_PATTERN' in source


def test_rooms_equipment_exposes_all_and_label_filters():
    source = FRONTEND.read_text(encoding="utf-8")
    assert '[["*", "Все"]' in source
    assert 'item.labelIds.has(this._filter)' in source
    assert 'Нет оборудования для выбранного ярлыка.' in source
    assert 'hass-more-info' in source


def test_rooms_equipment_module_is_registered_and_unloaded():
    init_source = INIT.read_text(encoding="utf-8")
    const_source = CONST.read_text(encoding="utf-8")
    assert 'ROOMS_EQUIPMENT_STATIC_PATH' in init_source
    assert init_source.count('ROOMS_EQUIPMENT_MODULE_URL') >= 3
    assert 'nikas-rooms-equipment.js' in const_source
