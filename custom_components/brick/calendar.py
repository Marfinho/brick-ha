"""Kalender: Brick-Trainingsplan aus dem ICS-Feed."""

from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime

import aiohttp
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from . import BrickConfigEntry
from .api import calendar_url_for
from .const import (
    CALENDAR_REFRESH_INTERVAL,
    CONF_CALENDAR_TOKEN,
    CONF_CALENDAR_URL,
    CONF_URL,
    REQUEST_TIMEOUT,
    TIMEZONE,
)
from .entity import device_info
from .ics import parse_ics

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1
SCAN_INTERVAL = CALENDAR_REFRESH_INTERVAL


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BrickConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Legt den Kalender nur an, wenn eine Kalender-Quelle konfiguriert ist."""
    url = entry.data.get(CONF_CALENDAR_URL)
    token = entry.data.get(CONF_CALENDAR_TOKEN)
    if not url and not token:
        return
    feed_url = url or calendar_url_for(entry.data[CONF_URL])
    async_add_entities(
        [BrickCalendar(entry, feed_url, token if not url else None)],
        update_before_add=True,
    )


class BrickCalendar(CalendarEntity):
    """Ganztägige Trainingstermine; Abruf höchstens stündlich mit ETag."""

    _attr_has_entity_name = True
    _attr_translation_key = "training"
    _attr_should_poll = True

    def __init__(
        self, entry: BrickConfigEntry, feed_url: str, bearer_token: str | None
    ) -> None:
        """Erzeugt den Kalender. URL und Token werden nie ausgegeben."""
        self._feed_url = feed_url
        self._bearer_token = bearer_token
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_device_info = device_info(entry)
        self._events: list[CalendarEvent] = []
        self._etag: str | None = None
        self._last_fetch: datetime | None = None
        self._loaded = False

    @property
    def suggested_object_id(self) -> str | None:
        """Stabile Objekt-ID calendar.brick_training."""
        return "Training"

    @property
    def event(self) -> CalendarEvent | None:
        """Heutiges oder nächstes Ereignis."""
        today = datetime.now(TIMEZONE).date()
        for event in self._events:
            end = event.end
            end_date = end.date() if isinstance(end, datetime) else end
            if end_date > today:
                return event
        return None

    async def async_update(self) -> None:
        """Stündlich aktualisieren."""
        await self._async_refresh()

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Ereignisse im Zeitraum (Ende exklusiv)."""
        await self._async_refresh()
        start = _day(start_date)
        end = _day(end_date)
        return [
            event
            for event in self._events
            if _day(event.start) < end and _day(event.end) > start
        ]

    async def _async_refresh(self) -> None:
        now = dt_util.utcnow()
        if (
            self._loaded
            and self._last_fetch is not None
            and now - self._last_fetch < CALENDAR_REFRESH_INTERVAL
        ):
            return
        session = async_get_clientsession(self.hass)
        headers: dict[str, str] = {}
        if self._bearer_token:
            headers["Authorization"] = f"Bearer {self._bearer_token}"
        if self._etag:
            headers["If-None-Match"] = self._etag
        try:
            async with (
                asyncio.timeout(REQUEST_TIMEOUT),
                session.get(self._feed_url, headers=headers) as response,
            ):
                if response.status == 304:
                    self._last_fetch = now
                    self._attr_available = True
                    return
                if response.status != 200:
                    raise _FeedError(f"http_{response.status}")
                body = await response.read()
                etag = response.headers.get("ETag")
            self._events = await self.hass.async_add_executor_job(parse_ics, body)
        except (aiohttp.ClientError, TimeoutError, _FeedError, ValueError) as err:
            # Nur der Typ: Exception-Texte können die Feed-URL samt Token enthalten.
            _LOGGER.warning(
                "Brick-Kalender nicht aktualisiert (%s)", type(err).__name__
            )
            self._attr_available = bool(self._loaded)
            return
        self._etag = etag
        self._last_fetch = now
        self._loaded = True
        self._attr_available = True


class _FeedError(Exception):
    """Unerwarteter HTTP-Status des Kalender-Feeds."""


def _day(value: date | datetime) -> date:
    if isinstance(value, datetime):
        return value.astimezone(TIMEZONE).date()
    return value
