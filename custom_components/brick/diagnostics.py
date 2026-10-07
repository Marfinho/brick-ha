"""Diagnose-Daten mit geschwärzten Zugangsdaten."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import BrickConfigEntry
from .const import CONF_CALENDAR_TOKEN, CONF_CALENDAR_URL, CONF_TOKEN, CONF_URL

TO_REDACT = {CONF_TOKEN, CONF_URL, CONF_CALENDAR_URL, CONF_CALENDAR_TOKEN}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: BrickConfigEntry
) -> dict[str, Any]:
    """Liefert Konfiguration (geschwärzt) und Status des Coordinators."""
    coordinator = entry.runtime_data.coordinator
    data = coordinator.data
    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "update_interval_s": (
            coordinator.update_interval.total_seconds()
            if coordinator.update_interval
            else None
        ),
        "last_update_success": coordinator.last_update_success,
        "data": {
            "date": data.today_date.isoformat(),
            "today_items": len(data.today.items),
            "tomorrow_items": len(data.tomorrow.items),
            "week_items": len(data.week.items),
        },
    }
