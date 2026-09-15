from pathlib import Path

ROOT = Path(__file__).parents[1]
PANEL = (ROOT / "custom_components/contract_generated_ui/frontend/device-availability-panel.js").read_text()
CONST = (ROOT / "custom_components/contract_generated_ui/const.py").read_text()


def test_beta004_version_and_loading_key():
    assert 'UI_VERSION = "1.0.0-beta004"' in PANEL
    assert 'DEVICE_AVAILABILITY_PANEL_BUILD = "b004"' in CONST


def test_header_refresh_uses_ui22_surface_not_black_override():
    assert '.refresh{grid-column:3;color:var(--primary-color,#03a9d9)}' in PANEL
    assert 'background:#111418;color:#fff' not in PANEL.split('.refresh{grid-column:3', 1)[1].split('}', 1)[0]


def test_title_has_no_domain_wifi_icon():
    assert '<span class="title-heading"><strong>Доступность устройств</strong></span>' in PANEL
    assert '<span class="title-heading"><ha-icon icon="mdi:wifi"' not in PANEL


def test_hass_updates_use_state_patch_not_active_view_rebuild():
    setter = PANEL.split('set hass(value)', 1)[1].split('get hass()', 1)[0]
    assert 'this._patchTelemetry();' in setter
    assert 'this._patchActiveView();' not in setter
