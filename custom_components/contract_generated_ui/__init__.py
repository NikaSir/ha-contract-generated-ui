"""Contract Generated UI integration."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import yaml
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
    """Set up Contract Generated UI from a config entry."""
    from homeassistant.components.frontend import add_extra_js_url
    from homeassistant.components.http import StaticPathConfig
    from homeassistant.const import Platform

    from .const import (
        APP_SHELL_FILENAME,
        APP_SHELL_STATIC_PATH,
        DOMAIN,
        FRONTEND_DIRECTORY,
        FRONTEND_STATIC_REGISTERED,
        GENERATED_DIRECTORY,
        INFRA_SUMMARY_FILENAME,
        INFRA_SUMMARY_STATIC_PATH,
        NAVIGATION_REGISTRY_FILENAME,
        NAVIGATION_REGISTRY_STATIC_PATH,
        SOURCE_DIRECTORY,
        UI_BUNDLE_FILENAME,
        UI_BUNDLE_MODULE_URL,
        UI_BUNDLE_STATIC_PATH,
    )
    from .coordinator import ContractGeneratedUICoordinator
    from .runtime_source_sync import sync_bundled_public_sources
    from .runtime_subpanel_shell import (
        write_empty_navigation_registry,
        write_navigation_registry,
    )

    source_root = Path(hass.config.path(SOURCE_DIRECTORY))
    generated_root = source_root / GENERATED_DIRECTORY
    navigation_registry_path = generated_root / NAVIGATION_REGISTRY_FILENAME

    try:
        await hass.async_add_executor_job(
            sync_bundled_public_sources,
            source_root,
        )
        await hass.async_add_executor_job(
            write_navigation_registry,
            source_root,
            navigation_registry_path,
        )
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, yaml.YAMLError) as err:
        _LOGGER.warning("Cannot build NikaS navigation registry during setup: %s", err)
        await hass.async_add_executor_job(
            write_empty_navigation_registry,
            navigation_registry_path,
        )

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
                StaticPathConfig(
                    UI_BUNDLE_STATIC_PATH,
                    str(frontend_root / UI_BUNDLE_FILENAME),
                    False,
                ),
                StaticPathConfig(
                    NAVIGATION_REGISTRY_STATIC_PATH,
                    str(navigation_registry_path),
                    False,
                ),
            ]
        )
        domain_data[FRONTEND_STATIC_REGISTERED] = True

    # The navigation bundle is progressive enhancement only: central and generated
    # dashboards remain native Lovelace if it loads late. Auto-loading here removes
    # the manual Lovelace-resource dependency while preserving race-proof content.
    add_extra_js_url(hass, UI_BUNDLE_MODULE_URL)

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

    from .const import UI_BUNDLE_MODULE_URL

    unloaded = await hass.config_entries.async_unload_platforms(
        entry,
        (Platform.SENSOR, Platform.BUTTON),
    )
    if unloaded:
        try:
            remove_extra_js_url(hass, UI_BUNDLE_MODULE_URL)
        except KeyError:
            pass
    return unloaded
