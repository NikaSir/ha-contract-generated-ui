"""Button platform for Contract Generated UI."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import SNAPSHOT_DIRECTORY, SOURCE_DIRECTORY
from .coordinator import ContractGeneratedUICoordinator
from .registry_snapshot import capture_registry_snapshot, write_registry_snapshot


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ContractGeneratedUICoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Contract Generated UI buttons."""
    async_add_entities([ContractGeneratedUICaptureSnapshotButton(entry)])


class ContractGeneratedUICaptureSnapshotButton(ButtonEntity):
    """Capture a scrubbed Home Assistant entity-registry snapshot."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True
    _attr_icon = "mdi:camera-outline"
    _attr_translation_key = "capture_registry_snapshot"

    def __init__(
        self,
        entry: ConfigEntry[ContractGeneratedUICoordinator],
    ) -> None:
        """Initialize the snapshot button."""
        self._attr_unique_id = f"{entry.entry_id}_capture_registry_snapshot"

    async def async_press(self) -> None:
        """Capture and atomically rotate the local scrubbed snapshot."""
        document = capture_registry_snapshot(self.hass)
        snapshot_root = Path(
            self.hass.config.path(SOURCE_DIRECTORY, SNAPSHOT_DIRECTORY)
        )
        result = await self.hass.async_add_executor_job(
            write_registry_snapshot,
            snapshot_root,
            document,
        )
        self._attr_extra_state_attributes = {
            "snapshot_id": document["metadata"]["snapshot_id"],
            "entity_count": len(document["spec"]["entities"]),
            "registry_changed": result.changed,
            "current_file": str(
                result.current_path.relative_to(Path(self.hass.config.path()))
            ),
            "previous_available": result.previous_path is not None,
        }
        self.async_write_ha_state()
