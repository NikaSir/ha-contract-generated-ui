"""Contract Generated UI integration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .coordinator import ContractGeneratedUICoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ContractGeneratedUICoordinator],
) -> bool:
    """Set up Contract Generated UI from a config entry."""
    from homeassistant.components.frontend import add_extra_js_url
    from homeassistant.components.http import StaticPathConfig
    from homeassistant.const import Platform

    from .const import (
        APP_SHELL_MODULE_URL,
        DOMAIN,
        FRONTEND_DIRECTORY,
        FRONTEND_STATIC_REGISTERED,
        FRONTEND_URL_PATH,
    )
    from .coordinator import ContractGeneratedUICoordinator

    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get(FRONTEND_STATIC_REGISTERED):
        frontend_path = Path(__file__).parent / FRONTEND_DIRECTORY
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    FRONTEND_URL_PATH,
                    str(frontend_path),
                    False,
                )
            ]
        )
        domain_data[FRONTEND_STATIC_REGISTERED] = True

    add_extra_js_url(hass, APP_SHELL_MODULE_URL)

    coordinator = ContractGeneratedUICoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        (Platform.SENSOR, Platform.BUTTON),
    )
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ContractGeneratedUICoordinator],
) -> bool:
    """Unload a Contract Generated UI config entry."""
    from homeassistant.components.frontend import remove_extra_js_url
    from homeassistant.const import Platform

    from .const import APP_SHELL_MODULE_URL

    unloaded = await hass.config_entries.async_unload_platforms(
        entry,
        (Platform.SENSOR, Platform.BUTTON),
    )
    if unloaded:
        try:
            remove_extra_js_url(hass, APP_SHELL_MODULE_URL)
        except KeyError:
            pass
    return unloaded
