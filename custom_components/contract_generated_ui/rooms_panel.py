"""Register the integration-owned Rooms v11 panel."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .const import DOMAIN, ROOMS_PANEL_MODULE_URL, ROOMS_PANEL_PATH

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

ROOMS_PANEL_WEB_COMPONENT = "nikas-rooms-v11-10824"
ROOMS_PANEL_URL_PATH = "dashboard-rooms"

ROOM_AREA_NAMES = frozenset(
    {
        "ванная",
        "спальня",
        "гардероб",
        "у саши",
        "у ильи",
        "лестница",
        "коридор",
        "холл",
        "котельная",
        "кухня",
        "столовая",
        "гостиная",
        "туалет",
        "тамбур",
        "веранда",
        "гараж",
        "чердак",
        "теплица",
    }
)


def _normalized_area_name(value: object) -> str:
    """Normalize numbered Home Assistant area names for Rooms matching."""
    normalized = str(value or "").strip().casefold().replace("ё", "е")
    normalized = re.sub(r"\s+", " ", normalized)
    return re.sub(r"^\d+(?:[.,]\d+)?\s*(?:[-–—.:)]\s*)?", "", normalized).strip()


def build_rooms_registry_bootstrap(document: dict[str, object]) -> dict[str, list[dict[str, object]]]:
    """Return the compact, JSON-safe registry subset required by Rooms."""
    spec = document.get("spec")
    if not isinstance(spec, dict):
        return {"areas": [], "devices": [], "entities": [], "labels": []}

    raw_areas = spec.get("areas") if isinstance(spec.get("areas"), list) else []
    raw_devices = spec.get("devices") if isinstance(spec.get("devices"), list) else []
    raw_entities = spec.get("entities") if isinstance(spec.get("entities"), list) else []
    raw_labels = spec.get("labels") if isinstance(spec.get("labels"), list) else []

    areas = [
        dict(area)
        for area in raw_areas
        if isinstance(area, dict) and _normalized_area_name(area.get("name")) in ROOM_AREA_NAMES
    ]
    area_ids = {str(area["area_id"]) for area in areas if area.get("area_id")}

    entity_records = [entity for entity in raw_entities if isinstance(entity, dict)]
    selected_entity_device_ids = {
        str(entity["device_id"])
        for entity in entity_records
        if entity.get("area_id") in area_ids and entity.get("device_id")
    }
    device_records = [device for device in raw_devices if isinstance(device, dict)]
    selected_devices = [
        device
        for device in device_records
        if device.get("area_id") in area_ids
        or str(device.get("device_id") or "") in selected_entity_device_ids
    ]
    device_ids = {
        str(device["device_id"])
        for device in selected_devices
        if device.get("device_id")
    }
    selected_entities = [
        entity
        for entity in entity_records
        if entity.get("area_id") in area_ids
        or str(entity.get("device_id") or "") in device_ids
    ]

    label_ids: set[str] = set()
    for record in (*selected_devices, *selected_entities):
        labels = record.get("labels")
        if isinstance(labels, list):
            label_ids.update(str(label) for label in labels)

    devices = []
    for source in selected_devices:
        device = dict(source)
        device["id"] = device.get("device_id")
        device["disabled_by"] = "registry" if device.get("disabled") else None
        devices.append(device)

    entities = []
    for source in selected_entities:
        entity = dict(source)
        entity["disabled_by"] = "registry" if entity.get("disabled") else None
        entity["hidden_by"] = "registry" if entity.get("hidden") else None
        entities.append(entity)

    labels = [
        dict(label)
        for label in raw_labels
        if isinstance(label, dict) and str(label.get("label_id") or "") in label_ids
    ]
    return {"areas": areas, "devices": devices, "entities": entities, "labels": labels}


async def async_register_rooms_panel(hass: HomeAssistant) -> None:
    """Replace the legacy Lovelace Rooms dashboard with the owned v11 panel."""
    from homeassistant.components import frontend, panel_custom
    from .registry_snapshot import capture_registry_snapshot

    registry_bootstrap = build_rooms_registry_bootstrap(capture_registry_snapshot(hass))

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
            "registry_bootstrap": registry_bootstrap,
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
    "build_rooms_registry_bootstrap",
    "async_register_rooms_panel",
    "async_unregister_rooms_panel",
]
