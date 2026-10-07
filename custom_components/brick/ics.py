"""Parser für den Brick-ICS-Feed (ganztägige Ereignisse)."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEvent
from icalendar import Calendar

_LOGGER = logging.getLogger(__name__)


def parse_ics(text: bytes | str) -> list[CalendarEvent]:
    """Wandelt einen ICS-Text in sortierte Kalenderereignisse um.

    Blockierend (CPU), daher im Executor aufrufen. Die Bibliothek übernimmt
    das Auflösen gefalteter Zeilen und das Entmaskieren von ``\\,`` und ``\\;``.
    """
    calendar = Calendar.from_ical(text)
    events: list[CalendarEvent] = []
    for component in calendar.walk("VEVENT"):
        start = _as_value(component.get("DTSTART"))
        if start is None:
            continue
        end = _as_value(component.get("DTEND"))
        if end is None or type(end) is not type(start):
            end = start + (
                timedelta(days=1) if not isinstance(start, datetime) else timedelta()
            )
        summary = str(component.get("SUMMARY", "")).strip()
        description = component.get("DESCRIPTION")
        events.append(
            CalendarEvent(
                start=start,
                end=end,
                summary=summary,
                description=str(description).strip() if description else None,
                uid=str(component["UID"]) if component.get("UID") else None,
            )
        )
    events.sort(key=lambda event: (_as_date(event.start), event.summary))
    _LOGGER.debug("ICS geparst: %d Ereignisse", len(events))
    return events


def _as_value(prop: object) -> date | datetime | None:
    value = getattr(prop, "dt", None)
    return value if isinstance(value, date) else None


def _as_date(value: date | datetime) -> date:
    return value.date() if isinstance(value, datetime) else value
