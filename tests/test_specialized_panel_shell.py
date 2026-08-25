from pathlib import Path

ROOT = Path(__file__).parents[1]
FRONTEND = ROOT / "custom_components" / "contract_generated_ui" / "frontend"
DOCS = ROOT / "docs"


def test_specialized_shell_keeps_application_chrome_native() -> None:
    zoom = (FRONTEND / "nikas-panel-zoom.js").read_text(encoding="utf-8")
    shell = (FRONTEND / "nikas-specialized-panel-shell.js").read_text(encoding="utf-8")

    assert 'document.createElement("nikas-panel-zoom")' in shell
    assert 'root.querySelector(".app > main")' in shell
    assert "env(safe-area-inset-top,0px)" in shell
    assert "env(safe-area-inset-right,0px)" in shell
    assert "env(safe-area-inset-bottom,0px)" in shell
    assert "env(safe-area-inset-left,0px)" in shell
    assert "grid-template-columns:52px minmax(0,1fr) 52px" in shell
    assert "grid-template-columns:48px minmax(0,1fr) 48px" in shell
    assert "padding-bottom:calc(82px + env(safe-area-inset-bottom,0px))" in shell

    assert 'const DEFAULT_MIN = 0.75' in zoom
    assert 'const DEFAULT_MAX = 2.0' in zoom
    assert 'const DEFAULT_STEP = 0.10' in zoom
    assert "touchstart" in zoom
    assert "touchmove" in zoom
    assert "window.localStorage" in zoom
    assert "window.scrollTo" in zoom


def test_specialized_shell_contract_is_documented() -> None:
    shell_doc = (DOCS / "SPECIALIZED_PANEL_SHELL_STANDARD.md").read_text(encoding="utf-8")
    zoom_doc = (DOCS / "SPECIALIZED_PANEL_ZOOM_STANDARD.md").read_text(encoding="utf-8")

    assert "Dynamic Island" in shell_doc
    assert "Bottom Tab Bar" in shell_doc
    assert "safe-area-inset-top" in shell_doc
    assert "safe-area-inset-bottom" in shell_doc
    assert "Only the work viewport is scaled" in shell_doc
    assert "pinch-to-zoom" in zoom_doc
    assert "per-panel/per-client" in zoom_doc
