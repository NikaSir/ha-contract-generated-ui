from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "custom_components" / "contract_generated_ui" / "__init__.py"
UI = ROOT / "custom_components" / "contract_generated_ui" / "frontend" / "nikas-ui.js"
STANDARD = ROOT / ".nikas-ui-standard.json"


def test_rooms_preserves_existing_lovelace_dashboard() -> None:
    init_source = INIT.read_text(encoding="utf-8")

    assert "async_register_rooms_panel" not in init_source
    assert "async_unregister_rooms_panel" not in init_source
    assert "ROOMS_PANEL_STATIC_PATH" not in init_source
    assert "StaticPathConfig(ROOMS_PANEL_STATIC_PATH" not in init_source


def test_rooms_keeps_shared_shell_navigation_without_owning_content() -> None:
    source = UI.read_text(encoding="utf-8")

    assert 'const ROOMS_ROOT_PATH = "/dashboard-rooms/rooms"' in source
    assert 'const ROOMS_UI_VERSION = "10.8.25"' in source
    assert "ROOM_VIEW_TITLES" in source
    assert "roomsHeaderModel" in source
    assert "syncRoomsLegacyHeading" in source
    assert 'model?.active === "rooms" ? roomsHeaderModel(pathname) : null' in source


def test_autonomous_rooms_renderer_is_not_a_production_runtime() -> None:
    standard = STANDARD.read_text(encoding="utf-8")

    assert "dist/nikas-rooms-v11.js" not in standard
