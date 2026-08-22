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
        APP_SHELL_FILENAME,
        APP_SHELL_MODULE_URL,
        APP_SHELL_STATIC_PATH,
        DOMAIN,
        FRONTEND_DIRECTORY,
        FRONTEND_STATIC_REGISTERED,
        INFRA_SUMMARY_FILENAME,
        INFRA_SUMMARY_MODULE_URL,
        INFRA_SUMMARY_STATIC_PATH,
    )
    from .coordinator import ContractGeneratedUICoordinator

    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get(FRONTEND_STATIC_REGISTERED):
        frontend_root = Path(__file__).parent / FRONTEND_DIRECTORY
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    APP_SHELL_STATIC_PATH,
                    str(frontend_root / APP_SHELL_FILENAME),
                    False,
                ),
                StaticPathConfig(
                    INFRA_SUMMARY_STATIC_PATH,
                    str(frontend_root / INFRA_SUMMARY_FILENAME),
                    False,
                ),
            ]
        )
        domain_data[FRONTEND_STATIC_REGISTERED] = True

    add_extra_js_url(hass, APP_SHELL_MODULE_URL)
    add_extra_js_url(hass, INFRA_SUMMARY_MODULE_URL)

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

    from .const import APP_SHELL_MODULE_URL, INFRA_SUMMARY_MODULE_URL

    unloaded = await hass.config_entries.async_unload_platforms(
        entry,
        (Platform.SENSOR, Platform.BUTTON),
    )
    if unloaded:
        for module_url in (APP_SHELL_MODULE_URL, INFRA_SUMMARY_MODULE_URL):
            try:
                remove_extra_js_url(hass, module_url)
            except KeyError:
                pass
    return unloaded
