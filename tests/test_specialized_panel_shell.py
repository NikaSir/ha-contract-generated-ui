from pathlib import Path

ROOT = Path(__file__).parents[1]
FRONTEND = ROOT / "custom_components" / "contract_generated_ui" / "frontend"
DOCS = ROOT / "docs"


def test_specialized_shell_keeps_application_chrome_native() -> None:
    zoom = (FRONTEND / "nikas-panel-zoom.js").read_text(encoding="utf-8")
    shell = (FRONTEND / "nikas-specialized-panel-shell.js").read_text(encoding="utf-8")

    assert "window.NikasPanelZoom.attach" in shell
    assert "Header, controls and bottom" in shell
    assert "env(safe-area-inset-top,0px)" in shell
    assert "env(safe-area-inset-right,0px)" in shell
    assert "env(safe-area-inset-bottom,0px)" in shell
    assert "env(safe-area-inset-left,0px)" in shell
    assert "grid-template-columns:52px minmax(0,1fr) 52px" in shell
    assert "grid-template-columns:48px minmax(0,1fr) 48px" in shell
    assert "padding-bottom:calc(82px + env(safe-area-inset-bottom,0px))" in shell

    assert "class ZoomController" in zoom
    assert 'const DEFAULT_MIN = 0.75' in zoom
    assert 'const DEFAULT_MAX = 2.0' in zoom
    assert 'const DEFAULT_STEP = 0.10' in zoom
    assert "this.root.querySelector?.(\"main\")" in zoom
    assert "touchstart" in zoom
    assert "touchmove" in zoom
    assert "window.localStorage" in zoom
    assert "window.scrollTo" in zoom


def test_specialized_shell_contract_is_documented() -> None:
    shell_doc = (DOCS / "SPECIALIZED_PANEL_SHELL_STANDARD.md").read_text(encoding="utf-8")
    zoom_doc = (DOCS / "SPECIALIZED_PANEL_ZOOM_STANDARD.md").read_text(encoding="utf-8")
    ui_doc = (DOCS / "INTEGRATION_DASHBOARD_UI_STANDARD.md").read_text(encoding="utf-8")
    delivery_doc = (DOCS / "SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md").read_text(encoding="utf-8")
    lessons_doc = (DOCS / "STARK_SOLARPOWER_PANEL_LESSONS.md").read_text(encoding="utf-8")

    assert "Specialized Panel Shell Standard v1.2" in shell_doc
    assert "consume once" in shell_doc.lower()
    assert "exactly one" in shell_doc.lower()
    assert "Home Assistant main-system menu" in shell_doc
    assert "Device Selector" in shell_doc
    assert "Bottom Tab Bar" in shell_doc
    assert "Dynamic Island" in shell_doc
    assert "safe-area-inset-top" in shell_doc
    assert "safe-area-inset-bottom" in shell_doc

    assert "Specialized Panel Zoom Standard v1.2" in zoom_doc
    assert "two-finger pinch-to-zoom" in zoom_doc
    assert "controls are optional" in zoom_doc.lower()
    assert "exactly one active zoom viewport" in zoom_doc
    assert "panel-id + peer-device-id + client" in zoom_doc

    assert "Integration-owned dashboard UI standard v1.3" in ui_doc
    assert "normal factual measurements use neutral typography" in ui_doc.lower()
    assert "backend owns validated thresholds" in ui_doc.lower()
    assert "Stark SolarPower" in ui_doc

    assert "Specialized Panel Frontend Delivery Standard v1.0" in delivery_doc
    assert "one stable production entry" in delivery_doc.lower()
    assert "deterministic" in delivery_doc.lower()
    assert "cache busting" in delivery_doc.lower()
    assert "local static assets" in delivery_doc.lower()

    assert "Stark SolarPower panel lessons" in lessons_doc
    assert "nested zoom wrappers" in lessons_doc
    assert "gesture-only" in lessons_doc
