from __future__ import annotations

from pathlib import Path

import yaml

from generator.subpanel_shell import compile_navigation_registry

ROOT = Path(__file__).parents[1]


def test_complete_v11_rc_global_tabs_stay_inside_preview_set() -> None:
    registry = compile_navigation_registry(ROOT)
    tabs = {tab["id"]: tab for tab in registry["global_tabs"]}

    assert tabs["home"]["path"] == "/dashboard-house-v11/home"
    assert tabs["actions"]["path"] == "/dashboard-actions"
    assert tabs["infrastructure"]["path"] == "/dashboard-infrastructure/overview"


def test_preview_home_route_does_not_rewrite_subpanel_parent_routes() -> None:
    navigation = yaml.safe_load((ROOT / "navigation" / "main.yaml").read_text(encoding="utf-8"))
    routes = navigation["spec"]["routes"]

    assert navigation["metadata"]["version"] == "1.1.1"
    assert routes["home"]["path"] == "/dashboard-house-v11/home"
    assert routes["house.heating"]["path"] == "/dashboard-house/heating"
    assert routes["actions"]["path"] == "/dashboard-actions"
    assert routes["actions.irrigation_candidate"]["path"] == "/dashboard-irrigation-generated/overview"

    packaged = ROOT / "custom_components" / "contract_generated_ui" / "bundled_sources" / "navigation" / "main.yaml"
    assert packaged.read_bytes() == (ROOT / "navigation" / "main.yaml").read_bytes()
