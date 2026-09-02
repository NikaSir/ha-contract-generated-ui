"""Button platform for Contract Generated UI."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.button import ButtonEntity
from homeassistant.components.persistent_notification import async_create as async_create_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import SNAPSHOT_DIRECTORY, SOURCE_DIRECTORY
from .coordinator import ContractGeneratedUICoordinator
from .registry_snapshot import capture_registry_snapshot, write_registry_snapshot
from .snapshot_download import SNAPSHOT_DOWNLOAD_URL


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ContractGeneratedUICoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Contract Generated UI buttons."""
    async_add_entities(
        [
            ContractGeneratedUICaptureSnapshotButton(entry),
            ContractGeneratedUIDownloadSnapshotButton(entry),
        ]
    )


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


class ContractGeneratedUIDownloadSnapshotButton(ButtonEntity):
    """Expose the current scrubbed registry snapshot through an authenticated URL."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True
    _attr_icon = "mdi:download"
    _attr_translation_key = "download_registry_snapshot"

    def __init__(
        self,
        entry: ConfigEntry[ContractGeneratedUICoordinator],
    ) -> None:
        """Initialize the snapshot download button."""
        self._attr_unique_id = f"{entry.entry_id}_download_registry_snapshot"

    async def async_press(self) -> None:
        """Publish an authenticated download link for current.json."""
        path = Path(
            self.hass.config.path(SOURCE_DIRECTORY, SNAPSHOT_DIRECTORY, "current.json")
        )
        if not path.is_file():
            message = "Сначала нажмите «Снять снимок реестра». Файл current.json ещё не создан."
            self._attr_extra_state_attributes = {
                "download_url": None,
                "current_file": None,
                "last_error": message,
            }
            self.async_write_ha_state()
            raise HomeAssistantError(message)

        self._attr_extra_state_attributes = {
            "download_url": SNAPSHOT_DOWNLOAD_URL,
            "current_file": str(path.relative_to(Path(self.hass.config.path()))),
            "last_error": None,
        }
        self.async_write_ha_state()
        async_create_notification(
            self.hass,
            (
                "Снимок реестра готов к скачиванию.\n\n"
                f"[Скачать current.json]({SNAPSHOT_DOWNLOAD_URL})\n\n"
                "Ссылка доступна только авторизованному пользователю Home Assistant."
            ),
            title="Contract Generated UI · снимок реестра",
            notification_id="contract_generated_ui_registry_snapshot_download",
        )
