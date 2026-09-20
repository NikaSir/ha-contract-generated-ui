from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
HARNESS = ROOT / "tests" / "device_availability_model_harness.mjs"
PANEL_HARNESS = ROOT / "tests" / "device_availability_panel_harness.mjs"


def _run(operation: str, states: dict, **options) -> object:
    completed = subprocess.run(
        ["node", str(HARNESS)],
        input=json.dumps({"operation": operation, "states": states, **options}),
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(completed.stdout)


def _state(value, **attributes) -> dict:
    return {"state": str(value), "attributes": attributes}


def _run_panel(operation: str, **options) -> object:
    completed = subprocess.run(
        ["node", str(PANEL_HARNESS)],
        input=json.dumps({"operation": operation, **options}),
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(completed.stdout)


def test_missing_integration_is_distinct_from_healthy() -> None:
    snapshot = _run("build", {"sensor.outside": _state("1")})
    assert snapshot["status"] == "no_integration"
    assert snapshot["totals"] == {
        "total": 0,
        "online": 0,
        "offline": 0,
        "stale": 0,
        "low_battery": 0,
        "poor_signal": 0,
    }
    assert snapshot["groups"] == []
    assert snapshot["updateEntityIds"] == []


def test_group_summary_builds_problem_first_snapshot_from_053_attributes() -> None:
    states = {
        "sensor.entity_availability_svet_group_summary": _state(
            3,
            friendly_name="Entity Availability - Свет Group summary",
            total_entities=3,
            essential=3,
            online=1,
            offline=1,
            stale=1,
            low_battery=1,
            poor_signal=1,
            suppressed=0,
            entities=["light.kitchen", "light.hall", "light.porch"],
            display_names={
                "light.kitchen": "Кухня",
                "light.hall": "Холл",
                "light.porch": "Крыльцо",
            },
            offline_entities=["light.porch"],
            stale_entities=["light.hall"],
            low_battery_entities=["light.hall"],
            poor_signal_entities=["light.porch"],
            battery_levels={"light.hall": 14},
            signal_levels={"light.porch": 43},
            signal_units={"light.porch": "LQI"},
            offline_since={"light.porch": "2026-09-14T18:00:00+00:00"},
            last_seen={"light.hall": "2026-09-14T17:30:00+00:00"},
        ),
        "sensor.entity_availability_okna_group_summary": _state(
            2,
            friendly_name="Entity Availability - Окна Group summary",
            total_entities=2,
            essential=2,
            online=2,
            offline=0,
            stale=0,
            low_battery=0,
            poor_signal=0,
            suppressed=0,
            entities=["binary_sensor.window_1", "binary_sensor.window_2"],
            display_names={
                "binary_sensor.window_1": "Окно спальни",
                "binary_sensor.window_2": "Окно кухни",
            },
        ),
    }

    snapshot = _run("build", states)

    assert snapshot["status"] == "problem"
    assert snapshot["totals"] == {
        "total": 5,
        "online": 3,
        "offline": 1,
        "stale": 1,
        "low_battery": 1,
        "poor_signal": 1,
    }
    assert [group["slug"] for group in snapshot["groups"]] == ["svet", "okna"]
    items = {item["entityId"]: item for item in snapshot["items"]}
    assert items["light.porch"]["condition"] == "offline"
    assert items["light.porch"]["signal"] == {"value": 43, "unit": "LQI"}
    assert items["light.hall"]["condition"] == "stale"
    assert items["light.hall"]["battery"] == 14
    assert items["light.kitchen"]["condition"] == "online"
    assert snapshot["updateEntityIds"] == [
        "sensor.entity_availability_okna_group_summary",
        "sensor.entity_availability_svet_group_summary",
    ]


def test_group_summary_reconciles_non_essential_entities_with_total() -> None:
    states = {
        "sensor.entity_availability_okna_group_summary": _state(
            36,
            friendly_name="Entity Availability - Окна Group summary",
            total_entities=36,
            essential=31,
            online=30,
            offline=1,
            suppressed=0,
            non_essential=5,
            non_essential_online=4,
            non_essential_offline=1,
            non_essential_suppressed=0,
            stale=0,
            stale_non_essential=0,
            low_battery=0,
            low_battery_non_essential=0,
            poor_signal=0,
            poor_signal_non_essential=0,
            entities=["binary_sensor.window", "switch.seasonal"],
            non_essential_entities=["switch.seasonal"],
            offline_entities=["binary_sensor.window"],
            offline_entities_non_essential=["switch.seasonal"],
        )
    }

    snapshot = _run("build", states)

    assert snapshot["composition"] == {
        "essential": 31,
        "non_essential": 5,
        "suppressed": 0,
        "non_essential_online": 4,
        "non_essential_offline": 1,
        "non_essential_suppressed": 0,
    }
    assert snapshot["composition"]["essential"] + snapshot["composition"][
        "non_essential"
    ] == snapshot["totals"]["total"]
    group = snapshot["groups"][0]
    assert group["essential"] == 31
    assert group["nonEssential"] == 5
    assert group["nonEssentialOnline"] == 4
    assert group["nonEssentialOffline"] == 1
    items = {item["entityId"]: item for item in snapshot["items"]}
    assert items["switch.seasonal"]["nonEssential"] is True


def test_unavailable_summary_reports_no_data_without_discarding_other_group() -> None:
    states = {
        "sensor.entity_availability_svet_group_summary": _state(
            "unavailable", friendly_name="Entity Availability - Свет Group summary"
        ),
        "sensor.entity_availability_okna_group_summary": _state(
            1,
            friendly_name="Entity Availability - Окна Group summary",
            total_entities=1,
            essential=1,
            online=1,
            offline=0,
            entities=["binary_sensor.window_1"],
            display_names={"binary_sensor.window_1": "Окно"},
        ),
    }
    snapshot = _run("build", states)
    assert snapshot["status"] == "no_data"
    assert [group["condition"] for group in snapshot["groups"]] == [
        "no_data",
        "healthy",
    ]
    assert snapshot["totals"]["total"] == 1
    assert "sensor.entity_availability_svet_group_summary" in snapshot["diagnostics"][
        "unavailableSources"
    ]


def test_search_and_filters_operate_on_display_name_group_and_condition() -> None:
    states = {
        "sensor.entity_availability_svet_group_summary": _state(
            2,
            friendly_name="Entity Availability - Свет Group summary",
            total_entities=2,
            essential=2,
            online=1,
            offline=1,
            entities=["light.kitchen", "light.porch"],
            display_names={"light.kitchen": "Кухня", "light.porch": "Крыльцо"},
            offline_entities=["light.porch"],
        )
    }
    by_text = _run("filter", states, query="кух")
    assert [item["entityId"] for item in by_text] == ["light.kitchen"]
    offline = _run("filter", states, group="svet", condition="offline")
    assert [item["entityId"] for item in offline] == ["light.porch"]


def test_multiple_problem_conditions_use_one_highest_priority_group() -> None:
    states = {
        "sensor.entity_availability_svet_group_summary": _state(
            2,
            friendly_name="Entity Availability - Свет Group summary",
            total_entities=2,
            essential=2,
            online=0,
            offline=1,
            stale=1,
            low_battery=1,
            poor_signal=1,
            entities=["light.porch", "light.hall"],
            display_names={"light.porch": "Крыльцо", "light.hall": "Холл"},
            offline_entities=["light.porch"],
            stale_entities=["light.porch"],
            low_battery_entities=["light.porch"],
            poor_signal_entities=["light.hall"],
        ),
        "light.porch": _state("unavailable"),
        "light.hall": _state("on"),
    }

    groups = _run("problems", states)

    assert [group["condition"] for group in groups["essential"]] == [
        "offline",
        "poor_signal",
    ]
    porch = groups["essential"][0]["items"][0]
    assert porch["entityId"] == "light.porch"
    assert porch["conditions"] == ["offline", "stale", "low_battery"]
    assert sum(
        item["entityId"] == "light.porch"
        for group in groups["essential"]
        for item in group["items"]
    ) == 1


def test_problem_groups_separate_non_essential_rows() -> None:
    states = {
        "sensor.entity_availability_service_group_summary": _state(
            2,
            friendly_name="Entity Availability - Сервис Group summary",
            total_entities=2,
            essential=1,
            non_essential=1,
            online=0,
            offline=1,
            non_essential_offline=1,
            entities=["switch.main", "switch.reference"],
            non_essential_entities=["switch.reference"],
            offline_entities=["switch.main"],
            offline_entities_non_essential=["switch.reference"],
        )
    }

    groups = _run("problems", states)

    assert [item["entityId"] for item in groups["essential"][0]["items"]] == [
        "switch.main"
    ]
    assert [item["entityId"] for item in groups["nonEssential"][0]["items"]] == [
        "switch.reference"
    ]


def test_unknown_problem_uses_live_state_only_without_higher_source_condition() -> None:
    states = {
        "sensor.entity_availability_datchiki_group_summary": _state(
            2,
            friendly_name="Entity Availability - Датчики Group summary",
            total_entities=2,
            essential=2,
            online=1,
            offline=1,
            entities=["sensor.unknown_value", "sensor.source_offline"],
            offline_entities=["sensor.source_offline"],
        ),
        "sensor.unknown_value": _state("unknown"),
        "sensor.source_offline": _state("unknown"),
    }

    groups = _run("problems", states)

    assert [group["condition"] for group in groups["essential"]] == [
        "offline",
        "unknown",
    ]
    assert groups["essential"][0]["items"][0]["conditions"] == ["offline"]
    assert groups["essential"][1]["items"][0]["conditions"] == ["unknown"]


def test_suppressed_unknown_item_keeps_source_suppression() -> None:
    states = {
        "sensor.entity_availability_service_group_summary": _state(
            1,
            friendly_name="Entity Availability - Сервис Group summary",
            total_entities=1,
            essential=1,
            online=0,
            offline=0,
            suppressed=1,
            entities=["sensor.maintenance"],
            suppressed_until={"sensor.maintenance": "2026-09-21T10:00:00+00:00"},
        ),
        "sensor.maintenance": _state("unknown"),
    }

    snapshot = _run("build", states)

    assert snapshot["items"][0]["condition"] == "suppressed"
    assert snapshot["items"][0]["conditions"] == ["suppressed"]
    assert _run("problems", states) == {"essential": [], "nonEssential": []}


def test_problem_groups_are_empty_when_every_item_is_healthy() -> None:
    states = {
        "sensor.entity_availability_okna_group_summary": _state(
            1,
            friendly_name="Entity Availability - Окна Group summary",
            total_entities=1,
            essential=1,
            online=1,
            offline=0,
            entities=["binary_sensor.window"],
        ),
        "binary_sensor.window": _state("off"),
    }

    assert _run("problems", states) == {"essential": [], "nonEssential": []}


def test_problems_tab_uses_approved_navigation_order() -> None:
    assert _run_panel("tabs") == {
        "tabs": [
            {"id": "summary", "label": "Сводка"},
            {"id": "problems", "label": "Проблемы"},
            {"id": "devices", "label": "Устройства"},
            {"id": "diagnostics", "label": "Диагностика"},
        ]
    }


def test_problem_view_groups_primary_problem_and_shows_secondary_badges() -> None:
    states = {
        "sensor.entity_availability_svet_group_summary": _state(
            2,
            friendly_name="Entity Availability - Свет Group summary",
            total_entities=2,
            essential=1,
            non_essential=1,
            online=0,
            offline=1,
            non_essential_offline=1,
            stale=1,
            low_battery=1,
            entities=["light.porch", "switch.reference"],
            display_names={
                "light.porch": "Крыльцо",
                "switch.reference": "Сезонная подсветка",
            },
            non_essential_entities=["switch.reference"],
            offline_entities=["light.porch"],
            offline_entities_non_essential=["switch.reference"],
            stale_entities=["light.porch"],
            low_battery_entities=["light.porch"],
        )
    }

    result = _run_panel("problems", states=states)

    assert "Недоступны / нет связи" in result["text"]
    assert "Данные устарели" in result["text"]
    assert "Низкий заряд" in result["text"]
    assert "Не влияют на общий статус" in result["text"]
    assert result["html"].count('data-entity="light.porch"') == 1
    assert result["html"].count('data-entity="switch.reference"') == 1


def test_problem_view_has_calm_empty_state() -> None:
    states = {
        "sensor.entity_availability_okna_group_summary": _state(
            1,
            friendly_name="Entity Availability - Окна Group summary",
            total_entities=1,
            essential=1,
            online=1,
            offline=0,
            entities=["binary_sensor.window"],
        ),
        "binary_sensor.window": _state("off"),
    }

    result = _run_panel("problems", states=states)

    assert "Проблемных устройств нет" in result["text"]
    assert "Недоступны / нет связи" not in result["text"]


def test_problem_view_never_treats_unavailable_sources_as_all_clear() -> None:
    unavailable = {
        "sensor.entity_availability_svet_group_summary": _state(
            "unavailable",
            friendly_name="Entity Availability - Свет Group summary",
        )
    }
    mixed = {
        **unavailable,
        "sensor.entity_availability_okna_group_summary": _state(
            1,
            friendly_name="Entity Availability - Окна Group summary",
            total_entities=1,
            essential=1,
            online=0,
            offline=1,
            entities=["binary_sensor.window"],
            offline_entities=["binary_sensor.window"],
        ),
    }

    for states in (unavailable, mixed):
        result = _run_panel("problems", states=states)
        assert "Есть источники без данных" in result["text"]
        assert "Проблемных устройств нет" not in result["text"]

    mixed_result = _run_panel("problems", states=mixed)
    assert "Недоступны / нет связи" in mixed_result["text"]


def test_problems_tab_telemetry_keeps_single_panel_shell() -> None:
    result = _run_panel("activate_problems", states={})
    assert result == {"activeTab": "problems", "writes": 1}


def test_live_hass_updates_do_not_rebuild_panel_shell() -> None:
    result = _run_panel("shell", states={})
    assert result == {"writes": 1}


def test_header_beta_uses_approved_compact_version_format() -> None:
    assert _run_panel("version") == {"version": "1.0.0-beta005"}


def test_summary_explains_non_essential_entities_without_hiding_the_balance() -> None:
    states = {
        "sensor.entity_availability_okna_group_summary": _state(
            36,
            friendly_name="Entity Availability - Окна Group summary",
            total_entities=36,
            essential=31,
            online=30,
            offline=1,
            suppressed=0,
            non_essential=5,
            non_essential_online=4,
            non_essential_offline=1,
            non_essential_suppressed=0,
            stale=0,
            low_battery=0,
            poor_signal=0,
            entities=["binary_sensor.window", "switch.seasonal"],
            non_essential_entities=["switch.seasonal"],
            offline_entities=["binary_sensor.window"],
            offline_entities_non_essential=["switch.seasonal"],
        )
    }

    text = _run_panel("summary", states=states)["text"]

    assert "31 основных" in text
    assert "5 не влияют на статус" in text
    assert "4 доступно" in text
    assert "1 отключено" in text


def test_more_info_uses_home_assistant_event_contract() -> None:
    result = _run_panel("more_info")
    assert result == {
        "type": "hass-more-info",
        "detail": {"entityId": "light.kitchen"},
    }


def test_header_navigation_returns_to_builtin_overview() -> None:
    result = _run_panel("navigate")
    assert result == {
        "paths": ["/home/overview"],
        "events": ["location-changed"],
    }


def test_refresh_updates_all_summary_sources_and_honors_minimum_busy_time() -> None:
    result = _run_panel("refresh")
    assert result["calls"] == [
        [
            "homeassistant",
            "update_entity",
            {"entity_id": ["sensor.one", "sensor.two"]},
        ]
    ]
    assert result["sleeps"] == [900]
