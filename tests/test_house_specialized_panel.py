from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from custom_components.contract_generated_ui.house_panel import (
    HOUSE_PANEL_TEMPLATE,
    HOUSE_PANEL_WEB_COMPONENT,
    build_house_panel_spec,
)

ROOT = Path(__file__).parents[1]
FRONTEND = ROOT / "custom_components" / "contract_generated_ui" / "frontend"


def _source_tree(tmp_path: Path) -> Path:
    source = tmp_path / "contract_generated_ui"
    (source / "contracts").mkdir(parents=True)
    (source / "manifests").mkdir()
    (source / "navigation").mkdir()
    shutil.copy2(ROOT / "contracts" / "house_home.yaml", source / "contracts" / "house_home.yaml")
    shutil.copy2(ROOT / "manifests" / "house_v11_preview.yaml", source / "manifests" / "house_v11_preview.yaml")
    shutil.copy2(ROOT / "navigation" / "main.yaml", source / "navigation" / "main.yaml")

    contract = yaml.safe_load((source / "contracts" / "house_home.yaml").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((source / "manifests" / "house_v11_preview.yaml").read_text(encoding="utf-8"))
    roles = contract["spec"]["roles"]
    module = manifest["spec"]["views"][0]["modules"][0]
    bindings = {}
    for role, semantic_key in module["bindings"].items():
        domain = roles[role]["allowed_domains"][0]
        bindings[semantic_key] = {
            "entity_id": f"{domain}.{role}",
            "domain": domain,
            "verification": "verified",
        }
    inventory = {
        "api_version": "nikas.home-assistant/semantic-inventory/v1",
        "kind": "SemanticInventory",
        "metadata": {
            "id": "house-test",
            "version": "1.0.0",
            "scrubbed": True,
            "snapshot_id": "sha256:test",
        },
        "spec": {"bindings": bindings},
    }
    (source / "inventory").mkdir()
    (source / "inventory" / "house.yaml").write_text(
        yaml.safe_dump(inventory, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return source


def test_house_panel_spec_resolves_verified_semantics(tmp_path: Path) -> None:
    panel = build_house_panel_spec(_source_tree(tmp_path))

    assert panel["id"] == "house_v11_preview"
    assert panel["title"] == "Дом · v11.0"
    assert panel["url_path"] == "dashboard-house-v11"
    assert panel["default_path"] == "/dashboard-house-v11/home"
    assert [tab["id"] for tab in panel["tabs"]] == ["home", "actions", "infrastructure"]
    assert panel["hero"]["standalone"] is True
    assert "type" not in panel["hero"]
    assert "grid_options" not in panel["hero"]
    assert len(panel["hero"]["entities"]["safety"]) == 5
    assert len(panel["hero"]["entities"]["cameras"]) == 8


def test_house_manifest_declares_integration_owned_specialized_panel() -> None:
    manifest = yaml.safe_load((ROOT / "manifests" / "house_v11_preview.yaml").read_text(encoding="utf-8"))
    assert manifest["metadata"]["version"] == "0.2.0"
    assert manifest["spec"]["specialized_panel"] == {"template": HOUSE_PANEL_TEMPLATE}
    assert HOUSE_PANEL_WEB_COMPONENT == "nikas-house-overview"


def test_house_panel_uses_one_transform_owned_canvas_and_native_chrome() -> None:
    frontend = (FRONTEND / "nikas-house-overview.js").read_text(encoding="utf-8")

    assert 'const ELEMENT_NAME = "nikas-house-overview"' in frontend
    assert frontend.count('class="canvas-viewport"') == 1
    assert frontend.count('class="work-canvas"') == 1
    assert "translate3d(${x}px, ${y}px, 0) scale(${scale})" in frontend
    assert "transform-origin:0 0" in frontend
    assert "scrollLeft" not in frontend
    assert "scrollTop" not in frontend
    assert "style.zoom" not in frontend
    assert "window.localStorage" in frontend
    assert "pointercancel" in frontend
    assert "CLICK_GUARD" in frontend
    assert "this._state.scale >= 0.97 && this._state.scale <= 1.03" in frontend
    assert "Масштаб 100%" in frontend
    assert "_lastTwoFingerTap" in frontend

    assert 'icon="mdi:menu"' in frontend
    assert 'new CustomEvent("hass-toggle-menu"' in frontend
    assert "mdi:arrow-left" not in frontend
    assert frontend.index('<header class="header">') < frontend.index('class="canvas-viewport"')
    assert frontend.index('class="canvas-viewport"') < frontend.index('<div class="bottom">')


def test_house_panel_has_no_permanent_scale_controls() -> None:
    frontend = (FRONTEND / "nikas-house-overview.js").read_text(encoding="utf-8")
    assert "data-zoom" not in frontend
    assert "zoom-in" not in frontend
    assert "zoom-out" not in frontend
    assert "mdi:magnify-plus" not in frontend
    assert "mdi:magnify-minus" not in frontend
