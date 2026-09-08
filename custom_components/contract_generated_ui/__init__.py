"""Contract Generated UI registry and common contract service."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .coordinator import ContractGeneratedUICoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ContractGeneratedUICoordinator],
) -> bool:
    """Set up common source validation, registry snapshots and diagnostics."""
    from homeassistant.const import Platform
    from homeassistant.helpers import entity_registry as er

    from .const import DOMAIN, SOURCE_DIRECTORY
    from .coordinator import ContractGeneratedUICoordinator
    from .runtime_source_sync import sync_bundled_public_sources
    from .snapshot_download import async_register_snapshot_download_view

    source_root = Path(hass.config.path(SOURCE_DIRECTORY))
    try:
        await hass.async_add_executor_job(sync_bundled_public_sources, source_root)
    except OSError as err:
        _LOGGER.warning("Cannot synchronize common NikaS sources during setup: %s", err)

    async_register_snapshot_download_view(hass)

    entity_registry = er.async_get(hass)
    legacy_generate_entity_id = entity_registry.async_get_entity_id(
        Platform.BUTTON,
        DOMAIN,
        f"{entry.entry_id}_generate_dashboards",
    )
    if legacy_generate_entity_id is not None:
        entity_registry.async_remove(legacy_generate_entity_id)

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
    """Unload common service entities."""
    from homeassistant.const import Platform

    return await hass.config_entries.async_unload_platforms(
        entry,
        (Platform.SENSOR, Platform.BUTTON),
    )
