"""Binärsensor: heute ist noch Training offen."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import BrickConfigEntry
from .coordinator import BrickCoordinator, is_open
from .entity import BrickEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BrickConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Legt den Binärsensor an."""
    async_add_entities([BrickTrainingOpenSensor(entry.runtime_data.coordinator)])


class BrickTrainingOpenSensor(BrickEntity, BinarySensorEntity):
    """An, solange heute mindestens eine Einheit "planned" ist."""

    def __init__(self, coordinator: BrickCoordinator) -> None:
        """Erzeugt den Sensor."""
        super().__init__(coordinator, "training_open", "Training offen")

    @property
    def is_on(self) -> bool:
        """Mindestens eine offene Einheit heute."""
        return any(is_open(item) for item in self.coordinator.data.today.items)
