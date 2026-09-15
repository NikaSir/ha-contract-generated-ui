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


def test_live_hass_updates_do_not_rebuild_panel_shell() -> None:
    result = _run_panel("shell", states={})
    assert result == {"writes": 1}


def test_header_beta_uses_approved_compact_version_format() -> None:
    assert _run_panel("version") == {"version": "1.0.0-beta003"}


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
