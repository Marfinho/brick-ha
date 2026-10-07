"""DataUpdateCoordinator: drei Summary-Abrufe pro Zyklus."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    BrickAuthError,
    BrickClient,
    BrickConnectionError,
    BrickItem,
    BrickRateLimitError,
    BrickSummary,
)
from .const import DOMAIN, MIN_REFRESH_GAP, TIMEZONE

_LOGGER = logging.getLogger(__name__)


def is_open(item: BrickItem) -> bool:
    """Offene Trainingseinheit (Ruhetage zählen nicht als Einheit)."""
    return item["status"] == "planned" and item["sport"] != "rest"


def is_done(item: BrickItem) -> bool:
    """Erledigte Einheit."""
    return item["status"] == "done"


@dataclass(frozen=True, slots=True)
class BrickData:
    """Ergebnis eines Abrufzyklus."""

    today: BrickSummary
    tomorrow: BrickSummary
    week: BrickSummary
    today_date: date

    @property
    def tomorrow_date(self) -> date:
        """Kalendertag von morgen."""
        return self.today_date + timedelta(days=1)


class BrickCoordinator(DataUpdateCoordinator[BrickData]):
    """Holt heute, morgen und die Woche von Brick."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: BrickClient,
        interval: timedelta,
    ) -> None:
        """Erzeugt den Coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=interval,
        )
        self.client = client
        self._last_attempt: float | None = None

    async def _async_update_data(self) -> BrickData:
        self._last_attempt = time.monotonic()
        try:
            today = await self.client.get_summary("today", "normal")
            tomorrow = await self.client.get_summary("tomorrow", "short")
            week = await self.client.get_summary("week", "short")
        except BrickAuthError as err:
            raise ConfigEntryAuthFailed("Brick-Token ungültig") from err
        except BrickRateLimitError as err:
            raise UpdateFailed(
                "Brick-Limit erreicht, neuer Versuch später",
                retry_after=err.retry_after,
            ) from err
        except BrickConnectionError as err:
            raise UpdateFailed(f"Brick nicht erreichbar ({err})") from err
        return BrickData(
            today=today,
            tomorrow=tomorrow,
            week=week,
            today_date=datetime.now(TIMEZONE).date(),
        )

    async def async_refresh_throttled(self) -> bool:
        """Aktualisiert sofort, aber höchstens alle 30 s. True, wenn abgerufen wurde."""
        if (
            self._last_attempt is not None
            and time.monotonic() - self._last_attempt < MIN_REFRESH_GAP.total_seconds()
        ):
            _LOGGER.debug("Aktualisierung übersprungen: Mindestabstand von 30 s")
            return False
        await self.async_refresh()
        return True
