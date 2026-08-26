from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from custom_components.contract_generated_ui.infrastructure_panel import (
    INFRASTRUCTURE_PANEL_TEMPLATE,
    INFRASTRUCTURE_PANEL_WEB_COMPONENT,
    build_infrastructure_panel_spec,
)

ROOT = Path(__file__).parents[1]
FRONTEND = ROOT / "custom_components" / "contract_generated_ui" / "frontend"


def _source_tree(tmp_path: Path) -> Path:
    source = tmp_path / "contract_generated_ui"
    (source / "contracts").mkdir(parents=True)
    (source / "manifests").mkdir()
    (source / "navigation").mkdir()
    for name in (
        "infrastructure_power_grid.yaml",
        "infrastructure_ups.yaml",
        "infrastructure_keenetic.yaml",
    ):
        shutil.copy2(ROOT / "contracts" / name, source / "contracts" / name)
    shutil.copy2(ROOT / "manifests" / "infrastructure.yaml", source / "manifests" / "infrastructure.yaml")
    shutil.copy2(ROOT / "navigation" / "main.yaml", source / "navigation" / "main.yaml")

    contracts = {}
    for path in (source / "contracts").glob("*.yaml"):
        contract = yaml.safe_load(path.read_text(encoding="utf-8"))
        contracts[contract["metadata"]["id"]] = contract
    manifest = yaml.safe_load((source / "manifests" / "infrastructure.yaml").read_text(encoding="utf-8"))
    bindings = {}
    for view in manifest["spec"]["views"]:
        for module in view["modules"]:
            roles = contracts[module["contract"]]["spec"]["roles"]
            for role, semantic_key in module["bindings"].items():
                domain = roles[role]["allowed_domains"][0]
                bindings[semantic_key] = {
                    "entity_id": f"{domain}.{semantic_key.replace('.', '_')}",
                    "domain": domain,
                    "verification": "verified",
                }
    inventory = {
        "api_version": "nikas.home-assistant/semantic-inventory/v1",
        "kind": "SemanticInventory",
        "metadata": {
            "id": "infrastructure-test",
            "version": "1.0.0",
            "scrubbed": True,
            "snapshot_id": "sha256:test",
        },
        "spec": {"bindings": bindings},
    }
    (source / "inventory").mkdir()
    (source / "inventory" / "infrastructure.yaml").write_text(
        yaml.safe_dump(inventory, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return source


def test_infrastructure_panel_resolves_four_verified_cards(tmp_path: Path) -> None:
    panel = build_infrastructure_panel_spec(_source_tree(tmp_path))

    assert panel["id"] == "infrastructure"
    assert panel["title"] == "Инфраструктура · v11.0"
    assert panel["url_path"] == "dashboard-infrastructure"
    assert panel["default_path"] == "/dashboard-infrastructure/overview"
    assert [tab["id"] for tab in panel["tabs"]] == ["home", "actions", "infrastructure"]
    assert [card["variant"] for card in panel["cards"]] == [
        "power_grid",
        "ups",
        "ups",
        "keenetic",
    ]
    assert len(panel["cards"][0]["roles"]) == 15


def test_infrastructure_panel_uses_native_chrome_and_one_canvas() -> None:
    frontend = (FRONTEND / "nikas-infrastructure-overview.js").read_text(encoding="utf-8")

    assert f'const ELEMENT_NAME = "{INFRASTRUCTURE_PANEL_WEB_COMPONENT}"' in frontend
    assert frontend.count('class="canvas-viewport"') == 1
    assert frontend.count('class="work-canvas"') == 1
    assert "translate3d(${x}px, ${y}px, 0) scale(${scale})" in frontend
    assert "scrollLeft" not in frontend
    assert "overflow-x:hidden;overflow-y:auto" in frontend
    assert "if (this._state.scale <= 1) return;" in frontend
    assert "viewport.scrollTop = 0" in frontend
    assert "style.zoom" not in frontend
    assert 'icon="mdi:menu"' in frontend
    assert 'new CustomEvent("hass-toggle-menu"' in frontend
    assert "mdi:arrow-left" not in frontend
    assert "Масштаб 100%" in frontend
    assert "data-zoom" not in frontend
    assert ".tab ha-icon{--mdc-icon-size:28px" in frontend
    assert "min-height:52px" in frontend
    assert "box-shadow:0 7px 20px rgba(23,45,76,.08)" in frontend


def test_infrastructure_manifest_declares_specialized_panel() -> None:
    manifest = yaml.safe_load((ROOT / "manifests" / "infrastructure.yaml").read_text(encoding="utf-8"))
    assert manifest["spec"]["specialized_panel"] == {
        "template": INFRASTRUCTURE_PANEL_TEMPLATE
    }


def test_infrastructure_cards_patch_stable_dom_and_respect_type_floor() -> None:
    summary = (FRONTEND / "nikas-infrastructure-summary.js").read_text(encoding="utf-8")

    assert "this.shadowRoot.innerHTML" not in summary
    assert "commitStableMarkup(this.shadowRoot, markup)" in summary
    assert "sameTreeShape" in summary
    assert "syncTree" in summary
    assert "_nikasDetailsBound" in summary
    for forbidden in (
        "font-size:10.5px",
        "font-size:11px",
        "font-size:11.5px",
    ):
        assert forbidden not in summary
