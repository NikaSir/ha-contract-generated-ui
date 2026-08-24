from __future__ import annotations

from generator.render_actions import _swing_gate_placeholder
from generator.render_house import _replace_heating_summary
from generator.render_infrastructure_summary import _summary_dashboard


def _role(name: str, entity: str, *, target: str | None = None) -> dict:
    action = {"kind": "navigate", "target": target} if target else {"kind": "more_info"}
    return {
        "role": name,
        "label": name,
        "entity_id": entity,
        "domain": entity.split(".", 1)[0],
        "action": action,
    }


def _power_module() -> dict:
    return {
        "instance": "power",
        "contract": "infrastructure.power_grid",
        "title": "Электросеть",
        "roles": [
            _role("grid_ok", "binary_sensor.grid_ok", target="/dashboard-infrastructure/power-overview"),
            _role("meter_online", "binary_sensor.meter_online"),
            _role("phase_loss", "binary_sensor.phase_loss"),
            _role("phase_a_present", "binary_sensor.phase_a_present"),
            _role("phase_b_present", "binary_sensor.phase_b_present"),
            _role("phase_c_present", "binary_sensor.phase_c_present"),
            _role("voltage_a", "sensor.voltage_a"),
            _role("voltage_b", "sensor.voltage_b"),
            _role("voltage_c", "sensor.voltage_c"),
            _role("voltage_imbalance", "sensor.voltage_imbalance"),
            _role("total_power", "sensor.total_power"),
            _role("non_interruptible_voltage", "sensor.boiler_input_voltage"),
            _role("non_interruptible_frequency", "sensor.boiler_input_frequency"),
            _role("non_interruptible_mode", "sensor.boiler_mode"),
            _role("non_interruptible_data_stale", "binary_sensor.boiler_stale"),
        ],
    }


def test_infrastructure_overview_uses_house_voltage_quality_thresholds() -> None:
    module = _power_module()
    dashboard = {
        "views": [
            {
                "title": "Инфраструктура · v0.12",
                "path": "overview",
                "type": "masonry",
                "cards": [
                    {"type": "heading", "heading": "Электросеть"},
                    {"type": "grid", "cards": []},
                ],
            }
        ]
    }
    trace = {
        "bindings": {},
        "semantics": {"views": [{"id": "overview", "modules": [module]}]},
    }

    rendered = _summary_dashboard(dashboard, trace)
    content = rendered["views"][0]["sections"][0]["cards"][0]["content"]

    assert "(volts|min)<198" in content
    assert "(volts|max)>242" in content
    assert "(volts|min)<205" in content
    assert "(volts|max)>235" in content
    assert "(volts|min)<210" in content
    assert "(volts|max)>230" in content
    assert "🔴 Авария" in content
    assert "🟠 Отклонение" in content
    assert "🟡 Внимание" in content
    assert "🟢 Нормально" in content


def test_power_before_tracks_voltage_entities_for_quality_refresh() -> None:
    module = _power_module()
    dashboard = {
        "views": [
            {
                "title": "До стабилизаторов",
                "path": "power-before",
                "type": "masonry",
                "cards": [
                    {"type": "heading", "heading": "Электросеть"},
                    {"type": "grid", "cards": []},
                ],
            }
        ]
    }
    trace = {
        "bindings": {},
        "semantics": {"views": [{"id": "power-before", "modules": [module]}]},
    }

    rendered = _summary_dashboard(dashboard, trace)
    status = rendered["views"][0]["sections"][0]["cards"][0]["cards"][0]
    assert {"sensor.voltage_a", "sensor.voltage_b", "sensor.voltage_c"}.issubset(
        set(status["entity_id"])
    )
    assert "Отклонение входящей сети" in status["content"]
    assert "Внимание · входящая сеть" in status["content"]


def test_actions_swing_gate_status_fits_half_width_mobile_card() -> None:
    card = _swing_gate_placeholder()
    assert card["secondary"] == "Нет датчика"
    assert card["tap_action"] == {"action": "none"}
    assert card["grid_options"] == {"columns": 6}


def test_house_heating_summary_uses_mobile_safe_boiler_name() -> None:
    view = {
        "sections": [
            {
                "type": "grid",
                "cards": [
                    {"type": "heading", "heading": "Дом сейчас"},
                    {
                        "type": "custom:mushroom-template-card",
                        "primary": "Отопление",
                        "secondary": "old",
                    },
                ],
            }
        ]
    }
    entities = {
        "heating_main": "binary_sensor.main",
        "heating_reserve": "binary_sensor.reserve",
        "heating_radiators": "binary_sensor.radiators",
        "heating_floor": "binary_sensor.floor",
        "heating_circulation": "binary_sensor.circulation",
        "heating_main_temp": "sensor.main_temp",
        "heating_reserve_temp": "sensor.reserve_temp",
    }

    _replace_heating_summary(view, entities)
    secondary = view["sections"][0]["cards"][1]["secondary"]
    assert "Основной" in secondary
    assert "Резервный" in secondary
    assert "Основной котёл" not in secondary
    assert "Резервный котёл" not in secondary
