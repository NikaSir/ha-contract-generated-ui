"""Lifecycle for the integration-owned device availability technical panel."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .const import (
    DEVICE_AVAILABILITY_PANEL_MODULE_URL,
    DEVICE_AVAILABILITY_PANEL_PATH,
    DEVICE_AVAILABILITY_PANEL_URL_PATH,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

PANEL_COMPONENT_NAME = "nikas-device-availability-panel"
PANEL_DEFAULT_PATH = f"/{DEVICE_AVAILABILITY_PANEL_URL_PATH}"
PANEL_PARENT_ROUTE = "/home/overview"
_LOGGER = logging.getLogger(__name__)


async def async_register_device_availability_panel(hass: HomeAssistant) -> bool:
    """Register the technical route when it has no existing owner."""
    from homeassistant.components import frontend, panel_custom

    if frontend.async_panel_exists(hass, DEVICE_AVAILABILITY_PANEL_URL_PATH):
        _LOGGER.warning(
            "Cannot register device availability panel: route %s already has an owner",
            DEVICE_AVAILABILITY_PANEL_URL_PATH,
        )
        return False

    await panel_custom.async_register_panel(
        hass=hass,
        frontend_url_path=DEVICE_AVAILABILITY_PANEL_URL_PATH,
        webcomponent_name=PANEL_COMPONENT_NAME,
        sidebar_title="Доступность устройств",
        sidebar_icon="mdi:shield-pulse-outline",
        module_url=DEVICE_AVAILABILITY_PANEL_MODULE_URL,
        embed_iframe=False,
        require_admin=False,
        handle_safe_area=True,
        config={
            "title": "Доступность устройств",
            "parent_route": PANEL_PARENT_ROUTE,
            "default_path": PANEL_DEFAULT_PATH,
        },
    )
    hass.data.setdefault(DOMAIN, {})[DEVICE_AVAILABILITY_PANEL_PATH] = (
        DEVICE_AVAILABILITY_PANEL_URL_PATH
    )
    return True


def async_unregister_device_availability_panel(hass: HomeAssistant) -> None:
    """Remove only the route recorded as owned by this integration."""
    from homeassistant.components import frontend

    url_path = hass.data.get(DOMAIN, {}).pop(DEVICE_AVAILABILITY_PANEL_PATH, None)
    if isinstance(url_path, str):
        frontend.async_remove_panel(hass, url_path, warn_if_unknown=False)


__all__ = [
    "async_register_device_availability_panel",
    "async_unregister_device_availability_panel",
]
