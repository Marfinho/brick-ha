"""Sensoren: Training heute, morgen und Woche."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import BrickConfigEntry
from .api import BrickSummary
from .coordinator import BrickCoordinator, BrickData, is_done, is_open
from .entity import BrickEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class BrickSensorDescription(SensorEntityDescription):
    """Beschreibt einen Brick-Sensor."""

    object_id: str
    summary: Callable[[BrickData], BrickSummary]
    day: Callable[[BrickData], str | None]
    # Zustand zählt nur offene (heute/morgen) bzw. geplante (Woche) Einheiten.
    include_done_count: bool = False


SENSORS: tuple[BrickSensorDescription, ...] = (
    BrickSensorDescription(
        key="training_today",
        translation_key="training_today",
        object_id="Training heute",
        summary=lambda data: data.today,
        day=lambda data: data.today_date.isoformat(),
        include_done_count=True,
    ),
    BrickSensorDescription(
        key="training_tomorrow",
        translation_key="training_tomorrow",
        object_id="Training morgen",
        summary=lambda data: data.tomorrow,
        day=lambda data: data.tomorrow_date.isoformat(),
        include_done_count=True,
    ),
    BrickSensorDescription(
        key="training_week",
        translation_key="training_week",
        object_id="Training Woche",
        summary=lambda data: data.week,
        day=lambda data: None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BrickConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Legt die Sensoren an."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(BrickTrainingSensor(coordinator, d) for d in SENSORS)


class BrickTrainingSensor(BrickEntity, SensorEntity):
    """Zahl offener bzw. geplanter Einheiten; der Sprechtext liegt im Attribut."""

    entity_description: BrickSensorDescription
    # Text und Einheiten sind groß und ändern sich ständig: nicht in die Historie.
    _unrecorded_attributes = frozenset({"text", "items"})

    def __init__(
        self, coordinator: BrickCoordinator, description: BrickSensorDescription
    ) -> None:
        """Erzeugt den Sensor."""
        super().__init__(coordinator, description.key, description.object_id)
        self.entity_description = description

    @property
    def native_value(self) -> int:
        """Anzahl offener (planned, ohne Ruhetage) Einheiten."""
        summary = self.entity_description.summary(self.coordinator.data)
        return sum(1 for item in summary.items if is_open(item))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Sprechtext und Einheiten; nie Tokens."""
        data = self.coordinator.data
        description = self.entity_description
        summary = description.summary(data)
        attrs: dict[str, Any] = {
            "text": summary.text,
            "items": [dict(item) for item in summary.items],
        }
        if description.include_done_count:
            attrs["done_count"] = sum(1 for item in summary.items if is_done(item))
            attrs["date"] = description.day(data)
        return attrs
