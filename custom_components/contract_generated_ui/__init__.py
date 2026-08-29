"""Contract Generated UI integration."""

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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry[ContractGeneratedUICoordinator]) -> bool:
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
        GENERATED_SUBPANEL_FILENAME,
        GENERATED_SUBPANEL_STATIC_PATH,
        HOUSE_HERO_ASSETS_STATIC_PATH,
        HOUSE_HERO_FILENAME,
        HOUSE_HERO_MODULE_URL,
        HOUSE_HERO_STATIC_PATH,
        HOUSE_PANEL_FILENAME,
        HOUSE_PANEL_STATIC_PATH,
        INFRASTRUCTURE_PANEL_FILENAME,
        INFRASTRUCTURE_PANEL_STATIC_PATH,
        INFRA_SUMMARY_FILENAME,
        INFRA_SUMMARY_STATIC_PATH,
        NAVIGATION_REGISTRY_FILENAME,
        NAVIGATION_REGISTRY_STATIC_PATH,
        PANEL_ZOOM_FILENAME,
        PANEL_ZOOM_MODULE_URL,
        PANEL_ZOOM_STATIC_PATH,
        ROOMS_PANEL_FILENAME,
        ROOMS_PANEL_STATIC_PATH,
        SOURCE_DIRECTORY,
        SPECIALIZED_SHELL_FILENAME,
        SPECIALIZED_SHELL_MODULE_URL,
        SPECIALIZED_SHELL_STATIC_PATH,
        UI_BUNDLE_FILENAME,
        UI_BUNDLE_MODULE_URL,
        UI_BUNDLE_STATIC_PATH,
    )
    from .coordinator import ContractGeneratedUICoordinator
    from .generated_panels import async_register_generated_subpanels, strip_standalone_navigation_groups
    from .house_panel import async_register_house_panel
    from .infrastructure_panel import async_register_infrastructure_panel
    from .rooms_panel import async_register_rooms_panel
    from .runtime_source_sync import sync_bundled_public_sources
    from .runtime_subpanel_shell import write_empty_navigation_registry, write_navigation_registry
    from .snapshot_download import async_register_snapshot_download_view

    source_root = Path(hass.config.path(SOURCE_DIRECTORY))
    generated_root = source_root / GENERATED_DIRECTORY
    navigation_registry_path = generated_root / NAVIGATION_REGISTRY_FILENAME
    try:
        await hass.async_add_executor_job(sync_bundled_public_sources, source_root)
        await hass.async_add_executor_job(write_navigation_registry, source_root, navigation_registry_path)
        await hass.async_add_executor_job(strip_standalone_navigation_groups, navigation_registry_path)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, yaml.YAMLError) as err:
        _LOGGER.warning("Cannot build NikaS navigation registry during setup: %s", err)
        await hass.async_add_executor_job(write_empty_navigation_registry, navigation_registry_path)

    async_register_snapshot_download_view(hass)
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get(FRONTEND_STATIC_REGISTERED):
        frontend_root = Path(__file__).parent / FRONTEND_DIRECTORY
        await hass.http.async_register_static_paths([
            StaticPathConfig(APP_SHELL_STATIC_PATH, str(frontend_root / APP_SHELL_FILENAME), False),
            StaticPathConfig(INFRA_SUMMARY_STATIC_PATH, str(frontend_root / INFRA_SUMMARY_FILENAME), False),
            StaticPathConfig(UI_BUNDLE_STATIC_PATH, str(frontend_root / UI_BUNDLE_FILENAME), False),
            StaticPathConfig(ROOMS_PANEL_STATIC_PATH, str(frontend_root / ROOMS_PANEL_FILENAME), False),
            StaticPathConfig(PANEL_ZOOM_STATIC_PATH, str(frontend_root / PANEL_ZOOM_FILENAME), False),
            StaticPathConfig(SPECIALIZED_SHELL_STATIC_PATH, str(frontend_root / SPECIALIZED_SHELL_FILENAME), False),
            StaticPathConfig(HOUSE_HERO_STATIC_PATH, str(frontend_root / HOUSE_HERO_FILENAME), False),
            StaticPathConfig(HOUSE_PANEL_STATIC_PATH, str(frontend_root / HOUSE_PANEL_FILENAME), False),
            StaticPathConfig(INFRASTRUCTURE_PANEL_STATIC_PATH, str(frontend_root / INFRASTRUCTURE_PANEL_FILENAME), False),
            StaticPathConfig(HOUSE_HERO_ASSETS_STATIC_PATH, str(frontend_root / "assets"), False),
            StaticPathConfig(GENERATED_SUBPANEL_STATIC_PATH, str(frontend_root / GENERATED_SUBPANEL_FILENAME), False),
            StaticPathConfig(NAVIGATION_REGISTRY_STATIC_PATH, str(navigation_registry_path), False),
        ])
        domain_data[FRONTEND_STATIC_REGISTERED] = True

    add_extra_js_url(hass, UI_BUNDLE_MODULE_URL)
    add_extra_js_url(hass, PANEL_ZOOM_MODULE_URL)
    add_extra_js_url(hass, SPECIALIZED_SHELL_MODULE_URL)
    add_extra_js_url(hass, HOUSE_HERO_MODULE_URL)

    try:
        await async_register_house_panel(hass, source_root)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, yaml.YAMLError) as err:
        _LOGGER.warning("Cannot register specialized NikaS House panel: %s", err)
    try:
        await async_register_rooms_panel(hass)
    except (OSError, ValueError, RuntimeError) as err:
        _LOGGER.warning("Cannot register NikaS Rooms v11 panel: %s", err)
    try:
        await async_register_infrastructure_panel(hass, source_root)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, yaml.YAMLError) as err:
        _LOGGER.warning("Cannot register specialized NikaS Infrastructure panel: %s", err)
    try:
        await async_register_generated_subpanels(hass, source_root)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, yaml.YAMLError) as err:
        _LOGGER.warning("Cannot register generated NikaS subpanels: %s", err)

    coordinator = ContractGeneratedUICoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, (Platform.SENSOR, Platform.BUTTON))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry[ContractGeneratedUICoordinator]) -> bool:
    """Unload Contract Generated UI config entry."""
    from homeassistant.components.frontend import remove_extra_js_url
    from homeassistant.const import Platform
    from .const import (
        HOUSE_HERO_MODULE_URL,
        PANEL_ZOOM_MODULE_URL,
        SPECIALIZED_SHELL_MODULE_URL,
        UI_BUNDLE_MODULE_URL,
    )
    from .generated_panels import async_unregister_generated_subpanels
    from .house_panel import async_unregister_house_panel
    from .infrastructure_panel import async_unregister_infrastructure_panel
    from .rooms_panel import async_unregister_rooms_panel

    unloaded = await hass.config_entries.async_unload_platforms(entry, (Platform.SENSOR, Platform.BUTTON))
    if unloaded:
        async_unregister_house_panel(hass)
        async_unregister_rooms_panel(hass)
        async_unregister_infrastructure_panel(hass)
        async_unregister_generated_subpanels(hass)
        for module_url in (
            UI_BUNDLE_MODULE_URL,
            PANEL_ZOOM_MODULE_URL,
            SPECIALIZED_SHELL_MODULE_URL,
            HOUSE_HERO_MODULE_URL,
        ):
            try:
                remove_extra_js_url(hass, module_url)
            except KeyError:
                pass
    return unloaded
