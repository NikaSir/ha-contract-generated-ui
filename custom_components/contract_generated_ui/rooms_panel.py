"""Register the integration-owned Rooms v11 panel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .const import DOMAIN, ROOMS_PANEL_MODULE_URL, ROOMS_PANEL_PATH

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

ROOMS_PANEL_WEB_COMPONENT = "nikas-rooms-v11-10823"
ROOMS_PANEL_URL_PATH = "dashboard-rooms"


async def async_register_rooms_panel(hass: HomeAssistant) -> None:
    """Replace the legacy Lovelace Rooms dashboard with the owned v11 panel."""
    from homeassistant.components import frontend, panel_custom

    if frontend.async_panel_exists(hass, ROOMS_PANEL_URL_PATH):
        frontend.async_remove_panel(hass, ROOMS_PANEL_URL_PATH, warn_if_unknown=False)

    await panel_custom.async_register_panel(
        hass=hass,
        frontend_url_path=ROOMS_PANEL_URL_PATH,
        webcomponent_name=ROOMS_PANEL_WEB_COMPONENT,
        sidebar_title="Помещения",
        sidebar_icon="mdi:floor-plan",
        module_url=ROOMS_PANEL_MODULE_URL,
        embed_iframe=False,
        require_admin=False,
        handle_safe_area=True,
        config={
            "title": "Помещения",
            "ui_version": "11.0.0",
            "default_path": "/dashboard-rooms/rooms",
        },
    )
    hass.data.setdefault(DOMAIN, {})[ROOMS_PANEL_PATH] = ROOMS_PANEL_URL_PATH


def async_unregister_rooms_panel(hass: HomeAssistant) -> None:
    """Remove Rooms v11 panel on config-entry unload."""
    from homeassistant.components import frontend

    url_path = hass.data.get(DOMAIN, {}).pop(ROOMS_PANEL_PATH, None)
    if isinstance(url_path, str):
        frontend.async_remove_panel(hass, url_path, warn_if_unknown=False)


__all__ = [
    "ROOMS_PANEL_WEB_COMPONENT",
    "ROOMS_PANEL_URL_PATH",
    "async_register_rooms_panel",
    "async_unregister_rooms_panel",
]
