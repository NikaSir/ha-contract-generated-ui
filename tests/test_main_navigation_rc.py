from __future__ import annotations

from pathlib import Path

import yaml

from generator.subpanel_shell import compile_navigation_registry

ROOT = Path(__file__).parents[1]


def test_complete_v11_rc_global_tabs_stay_inside_preview_set() -> None:
    registry = compile_navigation_registry(ROOT)
    tabs = {tab["id"]: tab for tab in registry["global_tabs"]}

    assert tabs["home"]["path"] == "/dashboard-house-v11/home"
    assert tabs["rooms"] == {
        "id": "rooms",
        "label": "Помещения",
        "icon": "mdi:floor-plan",
        "path": "/dashboard-rooms/rooms",
    }
    assert tabs["actions"]["path"] == "/dashboard-actions/home"
    assert tabs["infrastructure"]["path"] == "/dashboard-infrastructure/overview"


def test_navigation_registry_uses_canonical_public_panel_routes() -> None:
    navigation = yaml.safe_load((ROOT / "navigation" / "main.yaml").read_text(encoding="utf-8"))
    routes = navigation["spec"]["routes"]

    assert navigation["metadata"]["version"] == "1.4.0"
    assert routes["home"]["path"] == "/dashboard-house-v11/home"
    assert routes["rooms"]["path"] == "/dashboard-rooms/rooms"
    assert routes["house.heating"]["path"] == "/dashboard-zont"
    assert routes["house.water"]["path"] == "/dashboard-water"
    assert routes["house.vehicles"]["path"] == "/starline"
    assert routes["house.cleaning"]["path"] == "/dashboard-s8-omni"
    assert routes["actions"]["path"] == "/dashboard-actions/home"
    assert routes["actions.irrigation"]["path"] == "/dashboard-irrigation"
    assert routes["actions.irrigation_candidate"]["path"] == "/dashboard-irrigation-generated/overview"
    assert routes["infrastructure.ups"]["path"] == "/dashboard-ups"
    assert routes["infrastructure.keenetic"]["path"] == "/dashboard-keenetic"
    assert routes["infrastructure.lider"]["path"] == "/dashboard-lider"

    packaged = ROOT / "custom_components" / "contract_generated_ui" / "bundled_sources" / "navigation" / "main.yaml"
    assert packaged.read_bytes() == (ROOT / "navigation" / "main.yaml").read_bytes()
