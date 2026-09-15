from __future__ import annotations

import asyncio
import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "custom_components" / "contract_generated_ui"


def _load_module():
    package_name = "contract_generated_ui_panel_test"
    package = types.ModuleType(package_name)
    package.__path__ = [str(PACKAGE)]
    sys.modules[package_name] = package

    const_spec = importlib.util.spec_from_file_location(
        f"{package_name}.const", PACKAGE / "const.py"
    )
    assert const_spec and const_spec.loader
    const_module = importlib.util.module_from_spec(const_spec)
    sys.modules[const_spec.name] = const_module
    const_spec.loader.exec_module(const_module)

    panel_spec = importlib.util.spec_from_file_location(
        f"{package_name}.device_availability_panel",
        PACKAGE / "device_availability_panel.py",
    )
    assert panel_spec and panel_spec.loader
    panel_module = importlib.util.module_from_spec(panel_spec)
    sys.modules[panel_spec.name] = panel_module
    panel_spec.loader.exec_module(panel_module)
    return panel_module


class FakeHass:
    def __init__(self) -> None:
        self.data: dict = {}


def _install_frontend(*, exists: bool):
    frontend = types.ModuleType("homeassistant.components.frontend")
    frontend.async_panel_exists = lambda _hass, _path: exists
    frontend.removed = []
    frontend.async_remove_panel = (
        lambda _hass, path, warn_if_unknown=False: frontend.removed.append(
            (path, warn_if_unknown)
        )
    )

    panel_custom = types.ModuleType("homeassistant.components.panel_custom")
    panel_custom.calls = []

    async def register(**kwargs):
        panel_custom.calls.append(kwargs)

    panel_custom.async_register_panel = register
    components = types.ModuleType("homeassistant.components")
    components.frontend = frontend
    components.panel_custom = panel_custom
    homeassistant = types.ModuleType("homeassistant")
    homeassistant.components = components
    sys.modules.update(
        {
            "homeassistant": homeassistant,
            "homeassistant.components": components,
            "homeassistant.components.frontend": frontend,
            "homeassistant.components.panel_custom": panel_custom,
        }
    )
    return frontend, panel_custom


def test_registers_owned_route_even_without_entity_availability_states() -> None:
    module = _load_module()
    _frontend, panel_custom = _install_frontend(exists=False)
    hass = FakeHass()

    assert asyncio.run(module.async_register_device_availability_panel(hass)) is True
    assert len(panel_custom.calls) == 1
    call = panel_custom.calls[0]
    assert call["frontend_url_path"] == "dashboard-device-availability"
    assert call["webcomponent_name"] == "nikas-device-availability-panel"
    assert call["module_url"].startswith(
        "/contract_generated_ui/frontend/device-availability-panel.js?build="
    )
    assert call["module_url"].endswith("build=b004")
    assert call["config"] == {
        "title": "Доступность устройств",
        "parent_route": "/home/overview",
        "default_path": "/dashboard-device-availability",
    }
    assert hass.data[module.DOMAIN][module.DEVICE_AVAILABILITY_PANEL_PATH] == (
        "dashboard-device-availability"
    )


def test_route_collision_is_preserved() -> None:
    module = _load_module()
    _frontend, panel_custom = _install_frontend(exists=True)
    hass = FakeHass()

    assert asyncio.run(module.async_register_device_availability_panel(hass)) is False
    assert panel_custom.calls == []
    assert hass.data.get(module.DOMAIN, {}) == {}


def test_unload_removes_only_recorded_owned_route() -> None:
    module = _load_module()
    frontend, _panel_custom = _install_frontend(exists=False)
    hass = FakeHass()
    hass.data[module.DOMAIN] = {
        module.DEVICE_AVAILABILITY_PANEL_PATH: "dashboard-device-availability"
    }

    module.async_unregister_device_availability_panel(hass)
    module.async_unregister_device_availability_panel(hass)

    assert frontend.removed == [("dashboard-device-availability", False)]
