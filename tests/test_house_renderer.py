from __future__ import annotations

import json

import pytest

from generator.render import RenderError
from generator.render_house import render_house_dashboard
from generator.render_operational import _manifest_renderer


def _roles() -> dict[str, str]:
    return {
        "safety_01": "binary_sensor.test_safety",
        "opening_01": "binary_sensor.test_opening",
        "motion_01": "binary_sensor.test_motion",
        "light_01": "light.test_light",
        "climate_01": "climate.test_climate",
        "camera_01": "camera.test_camera",
        "weather": "weather.test_weather",
        "power_a": "sensor.test_power_a",
        "power_b": "sensor.test_power_b",
        "power_c": "sensor.test_power_c",
        "water_drinking": "sensor.test_water",
        "internet": "binary_sensor.test_internet",
        "heating_radiators": "binary_sensor.test_radiators",
        "heating_floor": "binary_sensor.test_floor",
        "heating_circulation": "binary_sensor.test_circulation",
        "heating_dhw": "sensor.test_dhw",
        "heating_main": "binary_sensor.test_main_boiler",
        "heating_reserve": "binary_sensor.test_reserve_boiler",
        "heating_main_temp": "sensor.test_main_temp",
        "heating_reserve_temp": "sensor.test_reserve_temp",
        "car_683_alarm": "binary_sensor.test_car_683_alarm",
        "car_683_fuel": "sensor.test_car_683_fuel",
        "car_130_alarm": "binary_sensor.test_car_130_alarm",
        "car_130_fuel": "sensor.test_car_130_fuel",
        "access_entrance": "binary_sensor.test_access_entrance",
        "access_tambour": "binary_sensor.test_access_tambour",
        "access_garage": "binary_sensor.test_access_garage",
        "access_sectional": "binary_sensor.test_access_sectional",
        "access_veranda": "binary_sensor.test_access_veranda",
        "access_garden": "binary_sensor.test_access_garden",
    }


def _dashboard() -> dict:
    return {
        "views": [
            {
                "title": "Дом · preview v0.1",
                "path": "home",
                "type": "masonry",
                "cards": [],
            }
        ]
    }


def _trace() -> dict:
    roles = [
        {
            "role": name,
            "entity_id": entity_id,
            "label": name,
            "domain": entity_id.split(".", 1)[0],
            "action": {"kind": "more_info"},
        }
        for name, entity_id in _roles().items()
    ]
    return {
        "semantics": {
            "views": [
                {
                    "id": "home",
                    "modules": [
                        {
                            "contract": "house.home_preview",
                            "instance": "house",
                            "roles": roles,
                        }
                    ],
                }
            ]
        }
    }


def _navigation() -> dict[str, str]:
    return {
        "safety": "/dashboard-house/safety",
        "open": "/dashboard-house/open",
        "activity": "/dashboard-house/activity",
        "lights": "/dashboard-house/lights",
        "climate": "/dashboard-house/climate",
        "cameras": "/dashboard-house/cameras",
        "weather": "/dashboard-family/family-weather",
        "rooms": "/dashboard-rooms/rooms",
        "family": "/dashboard-family/family",
        "heating": "/dashboard-boiler/heating-boiler",
        "cars": "/dashboard-cars/cars",
        "infrastructure": "/dashboard-infrastructure/overview",
        "actions": "/dashboard-actions/home",
        "water": "/dashboard-infrastructure/overview",
        "electricity": "/dashboard-infrastructure/overview",
        "network": "/dashboard-infrastructure/overview",
        "equipment": "/dashboard-infrastructure/overview",
    }


def _manifest() -> dict:
    return {
        "spec": {
            "navigation": _navigation(),
            "views": [
                {
                    "id": "home",
                    "title": "Дом · preview v0.1",
                    "path": "home",
                    "order": 0,
                    "renderer": "house_home_v1",
                    "modules": [
                        {
                            "contract": "house.home_preview",
                            "instance": "house",
                            "order": 0,
                            "bindings": {"weather": "house.context.weather"},
                        }
                    ],
                }
            ],
        }
    }


def _section_heading(section: dict) -> str:
    return section["cards"][0]["heading"]


def _walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_house_preview_preserves_protected_mobile_order() -> None:
    first = render_house_dashboard(_dashboard(), _trace(), _manifest())
    second = render_house_dashboard(_dashboard(), _trace(), _manifest())
    assert first == second

    view = first["views"][0]
    assert view["type"] == "sections"
    assert view["max_columns"] == 2
    assert view["dense_section_placement"] is True

    assert [_section_heading(section) for section in view["sections"][1:]] == [
        "Дом сейчас",
        "Активные события",
        "Ресурсы",
        "Отопление и ГВС",
        "Автомобили",
        "Ключевые точки доступа",
    ]


def test_house_preview_uses_declared_navigation_and_no_stale_zone_home() -> None:
    dashboard = render_house_dashboard(_dashboard(), _trace(), _manifest())
    serialized = json.dumps(dashboard, ensure_ascii=False)
    assert "zone.home" not in serialized

    navigation_paths = {
        node["tap_action"]["navigation_path"]
        for node in _walk(dashboard)
        if isinstance(node.get("tap_action"), dict)
        and "navigation_path" in node["tap_action"]
    }
    assert "/dashboard-infrastructure/overview" in navigation_paths


def test_house_resources_are_household_summary_only() -> None:
    dashboard = render_house_dashboard(_dashboard(), _trace(), _manifest())
    resources = dashboard["views"][0]["sections"][3]["cards"]
    assert resources[0]["heading"] == "Ресурсы"
    assert [card.get("primary") for card in resources[1:]] == [
        "Электросеть дома",
        "Питьевая вода",
        "Интернет",
    ]
    serialized = json.dumps(resources, ensure_ascii=False)
    assert "UPS" not in serialized
    assert "Вода для полива" not in serialized


def test_house_renderer_requires_verified_role_shape() -> None:
    trace = _trace()
    trace["semantics"]["views"][0]["modules"][0]["roles"] = [
        role
        for role in trace["semantics"]["views"][0]["modules"][0]["roles"]
        if role["role"] != "internet"
    ]
    with pytest.raises(RenderError, match="missing roles: internet"):
        render_house_dashboard(_dashboard(), trace, _manifest())


def test_mixed_manifest_renderers_fail_closed() -> None:
    manifest = _manifest()
    manifest["spec"]["views"].append(
        {
            "id": "other",
            "title": "Other",
            "path": "other",
            "order": 1,
            "renderer": "operational_v1",
            "modules": [],
        }
    )
    with pytest.raises(RenderError, match="mixed view renderers"):
        _manifest_renderer(manifest)
