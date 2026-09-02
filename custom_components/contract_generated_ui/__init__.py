"""Contract Generated UI registry and shared-asset service."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .coordinator import ContractGeneratedUICoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ContractGeneratedUICoordinator],
) -> bool:
    """Set up registry snapshots, diagnostics and shared static assets."""
    from homeassistant.components.http import StaticPathConfig
    from homeassistant.const import Platform

    from .const import (
        DOMAIN,
        FRONTEND_DIRECTORY,
        FRONTEND_STATIC_REGISTERED,
        HOUSE_HERO_ASSETS_STATIC_PATH,
        SOURCE_DIRECTORY,
    )
    from .coordinator import ContractGeneratedUICoordinator
    from .runtime_source_sync import sync_bundled_public_sources
    from .snapshot_download import async_register_snapshot_download_view

    source_root = Path(hass.config.path(SOURCE_DIRECTORY))
    try:
        await hass.async_add_executor_job(sync_bundled_public_sources, source_root)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, yaml.YAMLError) as err:
        _LOGGER.warning("Cannot synchronize preserved NikaS sources during setup: %s", err)

    async_register_snapshot_download_view(hass)
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get(FRONTEND_STATIC_REGISTERED):
        frontend_root = Path(__file__).parent / FRONTEND_DIRECTORY
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    HOUSE_HERO_ASSETS_STATIC_PATH,
                    str(frontend_root / "assets"),
                    False,
                ),
            ]
        )
        domain_data[FRONTEND_STATIC_REGISTERED] = True

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
    """Unload registry service entities."""
    from homeassistant.const import Platform

    unloaded = await hass.config_entries.async_unload_platforms(
        entry,
        (Platform.SENSOR, Platform.BUTTON),
    )
    return unloaded
