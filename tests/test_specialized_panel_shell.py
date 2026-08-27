import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
FRONTEND = ROOT / "custom_components" / "contract_generated_ui" / "frontend"
DOCS = ROOT / "docs"


def test_specialized_shell_keeps_application_chrome_native() -> None:
    zoom = (FRONTEND / "nikas-panel-zoom.js").read_text(encoding="utf-8")
    shell = (FRONTEND / "nikas-specialized-panel-shell.js").read_text(encoding="utf-8")

    assert "window.NikasPanelZoom.attach" in shell
    assert "Header, selector and bottom" in shell
    assert "env(safe-area-inset-top,0px)" in shell
    assert "env(safe-area-inset-right,0px)" in shell
    assert "env(safe-area-inset-bottom,0px)" in shell
    assert "env(safe-area-inset-left,0px)" in shell
    assert "grid-template-columns:52px minmax(0,1fr) 52px" in shell
    assert "grid-template-columns:48px minmax(0,1fr) 48px" in shell
    assert "min-height:62px" in shell
    assert "font-size:23px" in shell
    assert "font-size:14px" in shell
    assert "font-size:21px" in shell
    assert "font-size:13px" in shell
    assert "--mdc-icon-size:28px" in shell

    assert "class ZoomController" in zoom
    assert 'const DEFAULT_MIN = 0.75' in zoom
    assert 'const DEFAULT_MAX = 2.0' in zoom
    assert 'const AUTO_TARGETS = new Set(["NIKAS-GENERATED-SUBPANEL"])' in zoom
    assert 'this.root.querySelector?.(".canvas-viewport")' in zoom
    assert "touchstart" in zoom
    assert "touchmove" in zoom
    assert "window.localStorage" in zoom
    assert "this.viewport.scrollTop = 0" in zoom
    assert "this.state.scale <= 1" in zoom
    assert "pointercancel" in zoom


def test_v17_canonical_contract_covers_indicator_flicker_typography_and_return() -> None:
    standard = (DOCS / "NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md").read_text(encoding="utf-8")

    assert "Standard v1.7" in standard
    assert "nikas.specialized.source_route.v1" in standard
    assert "history.back()" in standard
    assert "12–25px" in standard
    assert "Локально" in standard
    assert "Облако" in standard
    assert "Резерв" in standard
    assert "Данные актуальны" in standard
    assert "Данные устарели" in standard
    assert "Дом сейчас" in standard
    assert "StarLine" in standard
    assert "shadowRoot.innerHTML" in standard
    assert "lazy DOM caching" in standard
    assert "23/14px" in standard
    assert "21/13px" in standard


def test_copy_adapt_template_cannot_reintroduce_legacy_shell() -> None:
    reference = (ROOT / "templates" / "integration-panel-v1" / "panel-shell-reference.js").read_text(encoding="utf-8")
    zoom_reference = (ROOT / "templates" / "integration-panel-v1" / "zoom-controller-reference.js").read_text(encoding="utf-8")
    runtime_zoom = (FRONTEND / "nikas-panel-zoom.js").read_text(encoding="utf-8")
    contract = json.loads(
        (ROOT / "templates" / "integration-panel-v1" / "panel-contract.example.json").read_text(encoding="utf-8")
    )

    assert "Template v1.7" in reference
    assert 'icon="mdi:menu"' in reference
    assert "hass-toggle-menu" in reference
    assert "mdi:arrow-left" not in reference
    assert reference.count('class="canvas-viewport"') == 1
    assert reference.count('class="work-canvas"') == 1
    assert "commitStableMarkup" in reference
    assert "this._renderQueued" in reference
    assert "window.NikasPanelZoom?.attach" in reference
    assert zoom_reference == runtime_zoom
    assert "this.host?._selectedDeviceId || this.host?._selectedDevice" in zoom_reference
    assert "font-size:23px" in reference
    assert "font-size:14px" in reference
    assert "--mdc-icon-size:28px" in reference
    assert contract["header"]["left_event"] == "hass-toggle-menu"
    assert contract["header"]["title_action"] == "return_to_source_base_panel"
    assert contract["header"]["source_route_handoff_key"] == "nikas.specialized.source_route.v1"
    assert contract["header"]["browser_history_back_allowed"] is False
    assert contract["zoom"]["range_percent"] == [75, 200]
    assert contract["rendering"]["routine_shadow_root_replacement"] is False
    assert contract["connection_indicator"]["enabled"] is False
    assert contract["typography"] == {
        "meaningful_min_px": 12,
        "meaningful_max_px": 25,
        "schematic_redundant_annotation_px": [9, 10],
    }


def test_specialized_shell_contract_is_documented() -> None:
    shell_doc = (DOCS / "SPECIALIZED_PANEL_SHELL_STANDARD.md").read_text(encoding="utf-8")
    zoom_doc = (DOCS / "SPECIALIZED_PANEL_ZOOM_STANDARD.md").read_text(encoding="utf-8")
    ui_doc = (DOCS / "INTEGRATION_DASHBOARD_UI_STANDARD.md").read_text(encoding="utf-8")
    delivery_doc = (DOCS / "SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md").read_text(encoding="utf-8")
    lessons_doc = (DOCS / "STARK_SOLARPOWER_PANEL_LESSONS.md").read_text(encoding="utf-8")

    assert "Specialized Panel Shell Standard v1.3" in shell_doc
    assert "consume exactly once" in shell_doc.lower()
    assert "hass-toggle-menu" in shell_doc
    assert "permanent on-screen zoom controls" in shell_doc.lower()
    assert "two-finger double tap" in shell_doc
    assert "97–103%" in shell_doc
    assert "Масштаб 100%" in shell_doc
    assert "exactly one" in shell_doc.lower()
    assert "Device Selector" in shell_doc
    assert "Bottom Tab Bar" in shell_doc
    assert "Dynamic Island" in shell_doc

    assert "Specialized Panel Zoom Standard v1.3" in zoom_doc
    assert "gesture-only zoom" in zoom_doc.lower()
    assert "two-finger pinch-to-zoom" in zoom_doc
    assert "controls: none" in zoom_doc
    assert "reset_gesture: two_finger_double_tap" in zoom_doc
    assert "snap_to_100_percent_range: [97, 103]" in zoom_doc
    assert "Масштаб 100%" in zoom_doc
    assert "panel-id + peer-device-id + client" in zoom_doc
    assert "exactly one active zoom viewport" in zoom_doc

    assert "Integration-owned dashboard UI standard v1.4" in ui_doc
    assert "hass-toggle-menu" in ui_doc
    assert "no permanent `− / % / +` controls" in ui_doc
    assert "normal measurements use neutral typography" in ui_doc.lower()
    assert "backend owns validated thresholds" in ui_doc.lower()
    assert "Stark SolarPower" in ui_doc

    assert "Specialized Panel Frontend Delivery Standard v1.1" in delivery_doc
    assert "controls: []" in delivery_doc
    assert "hass-toggle-menu" in delivery_doc
    assert "deterministic" in delivery_doc.lower()
    assert "cache busting" in delivery_doc.lower()
    assert "local static assets" in delivery_doc.lower()

    assert "UI `0.3.x` → `0.5.6`" in lessons_doc
    assert "hass-toggle-menu" in lessons_doc
    assert "two-finger double tap" in lessons_doc
    assert "97–103%" in lessons_doc
    assert "nested zoom wrappers" in lessons_doc
