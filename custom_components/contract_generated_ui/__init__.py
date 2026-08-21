"""Contract Generated UI integration."""

from __future__ import annotations

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
    from homeassistant.const import Platform

    from .coordinator import ContractGeneratedUICoordinator

    coordinator = ContractGeneratedUICoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, (Platform.SENSOR,))
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ContractGeneratedUICoordinator],
) -> bool:
    """Unload a Contract Generated UI config entry."""
    from homeassistant.const import Platform

    return await hass.config_entries.async_unload_platforms(
        entry,
        (Platform.SENSOR,),
    )
