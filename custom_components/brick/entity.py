"""Gemeinsame Basisklasse der Brick-Entitäten."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME
from .coordinator import BrickCoordinator


def device_info(entry: ConfigEntry) -> DeviceInfo:
    """Das eine Gerät "Brick" je Config Entry."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=NAME,
        manufacturer="Brick",
        entry_type=DeviceEntryType.SERVICE,
    )


class BrickEntity(CoordinatorEntity[BrickCoordinator]):
    """Entität am Brick-Coordinator."""

    _attr_has_entity_name = True
    # Deutsche Objekt-ID, unabhängig von der Systemsprache.
    _object_id: str

    def __init__(self, coordinator: BrickCoordinator, key: str, object_id: str) -> None:
        """Erzeugt die Entität."""
        super().__init__(coordinator)
        self._object_id = object_id
        self._attr_translation_key = key
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{key}"
        self._attr_device_info = device_info(coordinator.config_entry)

    @property
    def suggested_object_id(self) -> str | None:
        """Stabile, deutsche Objekt-ID."""
        return self._object_id
