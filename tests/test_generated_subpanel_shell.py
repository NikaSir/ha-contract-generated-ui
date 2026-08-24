from __future__ import annotations

import json
from pathlib import Path

import yaml

from custom_components.contract_generated_ui.generated_panels import (
    build_generated_panel_specs,
    strip_standalone_navigation_groups,
)
from generator.subpanel_shell import (
    apply_navigation_shell,
    compile_navigation_registry,
    embed_subpanel_dashboard,
    navigation_shell_engine_sha256,
)

ROOT = Path(__file__).parents[1]


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _sections_dashboard(view_count: int) -> dict:
    return {
        "views": [
            {
                "title": f"Tab {index}",
                "path": f"tab-{index}",
                "type": "sections",
                "max_columns": 1,
                "sections": [{"type": "grid", "cards": [{"type": "markdown", "content": f"placeholder {index}"}]}],
            }
            for index in range(view_count)
        ]
    }


def test_zont_and_starline_are_shared_custom_panel_manifests() -> None:
    zont = _load_yaml(ROOT / "manifests" / "zont.yaml")
    starline = _load_yaml(ROOT / "manifests" / "starline.yaml")

    assert zont["metadata"]["version"] == "0.8.0"
    assert starline["metadata"]["version"] == "0.5.0"
    assert zont["spec"]["dashboard_path"] == "/dashboard-zont"
    assert starline["spec"]["dashboard_path"] == "/dashboard-starline"
    assert zont["spec"]["subpanel"]["parent"] == "house.heating"
    assert starline["spec"]["subpanel"]["parent"] == "house.vehicles"
    assert zont["spec"]["subpanel"]["source"] == {
        "kind": "entity_registry",
        "platforms": ["zont", "zont_ha"],
        "include_disabled": False,
    }
    assert starline["spec"]["subpanel"]["source"] == {
        "kind": "entity_registry",
        "platforms": ["starline"],
        "include_disabled": False,
    }
    assert [view["id"] for view in zont["spec"]["views"]] == [
        "states", "boilers", "heating", "sensors", "diagnostics"
    ]
    assert len(starline["spec"]["views"]) == 5
    assert all(view["modules"] == [] for view in zont["spec"]["views"])
    assert all(view["modules"] == [] for view in starline["spec"]["views"])
    assert all(view["readonly"] for view in zont["spec"]["views"])
    assert all(view["readonly"] for view in starline["spec"]["views"])
    assert "button" in zont["spec"]["views"][0]["readonly"]["domains"]
    assert "насос" in zont["spec"]["views"][0]["readonly"]["include_keywords"]
    assert "радиатор" in zont["spec"]["views"][2]["readonly"]["include_keywords"]
    assert "rssi" in zont["spec"]["views"][3]["readonly"]["include_keywords"]
    assert starline["spec"]["views"][0]["readonly"]["limit"] == 6


def test_standalone_subpanel_shell_keeps_explicit_parent_and_reviewable_yaml() -> None:
    manifest = _load_yaml(ROOT / "manifests" / "zont.yaml")
    dashboard = _sections_dashboard(len(manifest["spec"]["views"]))
    rendered, groups = apply_navigation_shell(dashboard, manifest, ROOT)

    assert len(groups) == 1
    group = groups[0]
    assert group["title"] == "ZONT"
    assert group["subtitle"] == "Отопление и ГВС · UI v0.8.0"
    assert group["parent"]["path"] == "/dashboard-house/heating"
    assert group["embedded"] is False
    expected = ["states", "boilers", "heating", "sensors", "diagnostics"]
    assert [tab["path"] for tab in group["tabs"]] == [f"/dashboard-zont/{item}" for item in expected]

    for view, name in zip(rendered["views"], expected, strict=True):
        assert view["path"] == name
        assert view["subview"] is True
        assert view["back_path"] == "/dashboard-house/heating"
        assert view["title"] == "ZONT"

    assert navigation_shell_engine_sha256("0" * 64, groups) != "0" * 64


def test_shared_custom_panel_specs_and_zont_control_scope() -> None:
    specs = {item["id"]: item for item in build_generated_panel_specs(ROOT)}
    assert {"zont", "starline"} <= set(specs)
    assert specs["zont"]["url_path"] == "dashboard-zont"
    assert specs["starline"]["url_path"] == "dashboard-starline"
    assert specs["zont"]["parent"]["path"] == "/dashboard-house/heating"
    assert specs["zont"]["source"]["platforms"] == ["zont", "zont_ha"]
    assert [tab["label"] for tab in specs["zont"]["tabs"]] == [
        "Состояния", "Котлы", "Отопление", "Датчики", "Диагностика"
    ]
    assert len(specs["starline"]["tabs"]) == 5

    shared_frontend = (ROOT / "custom_components" / "contract_generated_ui" / "frontend" / "nikas-generated-subpanel.js").read_text(encoding="utf-8")
    zont_frontend = (ROOT / "custom_components" / "contract_generated_ui" / "frontend" / "nikas-generated-zont.js").read_text(encoding="utf-8")
    zont_v080 = (ROOT / "custom_components" / "contract_generated_ui" / "frontend" / "nikas-generated-zont-v080.js").read_text(encoding="utf-8")
    assert 'const ELEMENT_NAME = "nikas-generated-subpanel"' in shared_frontend
    assert 'const ELEMENT_NAME = "nikas-generated-zont"' in zont_frontend
    assert 'type: "config/entity_registry/list"' in zont_frontend
    assert 'type: "config/device_registry/list"' in zont_frontend
    assert "_boilerCard" in zont_frontend
    assert "_roomCard" in zont_frontend
    assert "_meterCard" in zont_frontend
    assert "_states" in zont_frontend
    assert "_modeButtons" in zont_frontend
    assert "_mixerState" in zont_frontend
    assert 'callService("button", "press"' in zont_frontend
    assert 'domainOf(entityId) !== "button"' in zont_frontend
    assert '["zont", "zont_ha"].includes(item.entry.platform)' in zont_frontend
    assert 'callService("switch"' not in zont_frontend
    assert 'callService("climate"' not in zont_frontend
    assert "_systemOverviewV080" in zont_v080
    assert 'new Event("hass-toggle-menu"' in zont_v080
    assert "history.back" not in zont_v080


def test_global_navigation_overlay_drops_standalone_custom_panel_groups(tmp_path: Path) -> None:
    registry = compile_navigation_registry(ROOT)
    path = tmp_path / "navigation.json"
    path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert strip_standalone_navigation_groups(path) is True
    filtered = json.loads(path.read_text(encoding="utf-8"))
    groups = {group["id"]: group for group in filtered["subpanels"]}
    assert "power" in groups
    assert groups["power"]["embedded"] is True
    assert "zont" not in groups
    assert "starline" not in groups


def test_embedded_mode_remains_available_when_real_host_manifest_exists() -> None:
    manifest = _load_yaml(ROOT / "manifests" / "zont.yaml")
    manifest["spec"]["dashboard_path"] = "/dashboard-house"
    child, groups = apply_navigation_shell(_sections_dashboard(len(manifest["spec"]["views"])), manifest, ROOT)
    assert groups[0]["embedded"] is True

    host_manifest = {"spec": {"dashboard_path": "/dashboard-house"}}
    host = {"views": [{"title": "Отопление и ГВС", "path": "heating", "type": "sections", "sections": [{"type": "grid", "cards": [{"type": "markdown", "content": "Heating"}]}]}]}
    composed = embed_subpanel_dashboard(host, host_manifest, child, groups[0])
    paths = [view["path"] for view in composed["views"]]
    assert paths[0] == "heating"
    assert "zont-states" in paths
    launch = composed["views"][0]["sections"][-1]["cards"][0]
    assert launch["tap_action"]["navigation_path"] == "/dashboard-house/zont-states"


def test_generator_and_runtime_subpanel_sources_are_byte_equivalent() -> None:
    assert (ROOT / "generator" / "subpanel_shell.py").read_bytes() == (ROOT / "custom_components" / "contract_generated_ui" / "runtime_subpanel_shell.py").read_bytes()
    assert (ROOT / "generator" / "render_subpanel_placeholder.py").read_bytes() == (ROOT / "custom_components" / "contract_generated_ui" / "runtime_render_subpanel_placeholder.py").read_bytes()


def test_navigation_contract_and_demo_manifests_are_packaged() -> None:
    assert (ROOT / "navigation" / "main.yaml").read_bytes() == (ROOT / "custom_components" / "contract_generated_ui" / "bundled_sources" / "navigation" / "main.yaml").read_bytes()
    for name in ("zont.yaml", "starline.yaml"):
        assert (ROOT / "manifests" / name).read_bytes() == (ROOT / "custom_components" / "contract_generated_ui" / "bundled_sources" / "manifests" / name).read_bytes()
