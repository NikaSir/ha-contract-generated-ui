from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


def _navigation() -> dict:
    return yaml.safe_load(
        (ROOT / "navigation" / "main.yaml").read_text(encoding="utf-8")
    )


def test_common_navigation_resolves_base_tabs() -> None:
    navigation = _navigation()
    routes = navigation["spec"]["routes"]
    tabs = navigation["spec"]["global_tabs"]

    assert [
        {
            "id": tab["id"],
            "title": tab["title"],
            "icon": tab["icon"],
            "path": routes[tab["route"]]["path"],
        }
        for tab in tabs
    ] == [
        {
            "id": "home",
            "title": "Дом",
            "icon": "mdi:home-outline",
            "path": "/dashboard-house-v13/home",
        },
        {
            "id": "rooms",
            "title": "Помещения",
            "icon": "mdi:floor-plan",
            "path": "/dashboard-rooms-v11/rooms",
        },
        {
            "id": "actions",
            "title": "Действия",
            "icon": "mdi:lightning-bolt-outline",
            "path": "/dashboard-actions/home",
        },
        {
            "id": "infrastructure",
            "title": "Инфра",
            "icon": "mdi:server-network",
            "path": "/dashboard-infrastructure/overview",
        },
    ]


def test_navigation_source_is_packaged_byte_for_byte() -> None:
    assert (ROOT / "navigation" / "main.yaml").read_bytes() == (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "bundled_sources"
        / "navigation"
        / "main.yaml"
    ).read_bytes()


def test_water_route_matches_the_owner_contract() -> None:
    navigation = _navigation()
    assert navigation["metadata"]["version"] == "2.1.1"
    assert navigation["spec"]["specialized_routes"]["water_accounting"] == {
        "path": "/dashboard-water",
        "safe_return_route": "/dashboard-house-v13/home",
    }
