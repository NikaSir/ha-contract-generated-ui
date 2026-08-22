from __future__ import annotations

import json
from pathlib import Path

import yaml

from generator.subpanel_shell import (
    apply_navigation_shell,
    compile_navigation_registry,
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
                "sections": [
                    {
                        "type": "grid",
                        "cards": [
                            {
                                "type": "markdown",
                                "content": f"placeholder {index}",
                            }
                        ],
                    }
                ],
            }
            for index in range(view_count)
        ]
    }


def test_zont_and_starline_are_short_declarative_subpanel_manifests() -> None:
    zont = _load_yaml(ROOT / "manifests" / "zont.yaml")
    starline = _load_yaml(ROOT / "manifests" / "starline.yaml")

    assert zont["spec"]["subpanel"] == {
        "template": "standard_v1",
        "navigation": "main",
        "parent": "house.heating",
    }
    assert starline["spec"]["subpanel"] == {
        "template": "standard_v1",
        "navigation": "main",
        "parent": "house.vehicles",
    }

    assert [view["title"] for view in zont["spec"]["views"]] == [
        "Обзор",
        "Отопление",
        "Датчики",
        "Сервис",
    ]
    assert [view["title"] for view in starline["spec"]["views"]] == [
        "Обзор",
        "Охрана",
        "Двигатель",
        "Авто",
        "Сервис",
    ]
    assert all(view["modules"] == [] for view in zont["spec"]["views"])
    assert all(view["modules"] == [] for view in starline["spec"]["views"])


def test_subpanel_shell_generates_native_header_back_and_bottom_clearance() -> None:
    manifest = _load_yaml(ROOT / "manifests" / "zont.yaml")
    dashboard = _sections_dashboard(len(manifest["spec"]["views"]))

    rendered, groups = apply_navigation_shell(dashboard, manifest, ROOT)

    assert len(groups) == 1
    group = groups[0]
    assert group["title"] == "ZONT"
    assert group["parent"]["path"] == "/dashboard-house/heating"
    assert len(group["tabs"]) == 4

    for view in rendered["views"]:
        assert view["subview"] is True
        assert view["back_path"] == "/dashboard-house/heating"
        assert view["title"] == "ZONT"
        spacer = view["sections"][-1]["cards"][0]
        assert spacer["type"] == "markdown"
        assert spacer["text_only"] is True

    base = "0" * 64
    assert navigation_shell_engine_sha256(base, groups) != base


def test_navigation_registry_drives_different_tab_counts_without_frontend_hardcode() -> None:
    registry = compile_navigation_registry(ROOT)
    assert registry["api_version"] == "nikas.home-assistant/navigation-registry/v1"

    groups = {group["id"]: group for group in registry["subpanels"]}
    assert {"power", "zont", "starline"} <= set(groups)

    assert len(groups["zont"]["tabs"]) == 4
    assert len(groups["starline"]["tabs"]) == 5
    assert groups["zont"]["parent"]["path"] == "/dashboard-house/heating"
    assert groups["starline"]["parent"]["path"] == "/dashboard-house/vehicles"
    assert groups["power"]["embedded"] is True
    assert groups["zont"]["embedded"] is False

    serialized = json.dumps(registry, ensure_ascii=False)
    assert "entity_id" not in serialized
    assert "device_id" not in serialized

    frontend = (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "frontend"
        / "nikas-ui.js"
    ).read_text(encoding="utf-8")
    assert 'const REGISTRY_URL = "/contract_generated_ui/navigation.json"' in frontend
    assert "registrySubpanelModel" in frontend
    assert "POWER_ITEMS" not in frontend
    assert "ZONT" not in frontend
    assert "StarLine" not in frontend


def test_generator_and_runtime_subpanel_sources_are_byte_equivalent() -> None:
    assert (
        ROOT / "generator" / "subpanel_shell.py"
    ).read_bytes() == (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "runtime_subpanel_shell.py"
    ).read_bytes()

    assert (
        ROOT / "generator" / "render_subpanel_placeholder.py"
    ).read_bytes() == (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "runtime_render_subpanel_placeholder.py"
    ).read_bytes()


def test_navigation_contract_is_packaged_with_demo_manifests() -> None:
    assert (
        ROOT / "navigation" / "main.yaml"
    ).read_bytes() == (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "bundled_sources"
        / "navigation"
        / "main.yaml"
    ).read_bytes()

    for name in ("zont.yaml", "starline.yaml"):
        assert (
            ROOT / "manifests" / name
        ).read_bytes() == (
            ROOT
            / "custom_components"
            / "contract_generated_ui"
            / "bundled_sources"
            / "manifests"
            / name
        ).read_bytes()
