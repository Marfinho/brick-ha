"""Konstanten der Brick-Integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final
from zoneinfo import ZoneInfo

DOMAIN: Final = "brick"
NAME: Final = "Brick"

CONF_URL: Final = "url"
CONF_TOKEN: Final = "token"
CONF_CALENDAR: Final = "calendar"
CONF_CALENDAR_URL: Final = "calendar_url"
CONF_CALENDAR_TOKEN: Final = "calendar_token"
CONF_SCAN_INTERVAL: Final = "scan_interval"

# Abfrageintervall in Minuten. Das Minimum hält die 30 Abfragen/Minute je Token
# (drei Abrufe pro Zyklus) sicher ein.
DEFAULT_SCAN_INTERVAL: Final = 15
MIN_SCAN_INTERVAL: Final = 5
MAX_SCAN_INTERVAL: Final = 240

REQUEST_TIMEOUT: Final = 15
MIN_REFRESH_GAP: Final = timedelta(seconds=30)
CALENDAR_REFRESH_INTERVAL: Final = timedelta(hours=1)

SUMMARY_PATH: Final = "/api/voice/v1/summary"
CALENDAR_PATH: Final = "/api/calendar/v1/training.ics"

TIMEZONE: Final = ZoneInfo("Europe/Berlin")

SERVICE_ANNOUNCE: Final = "announce"
SERVICE_REFRESH: Final = "refresh"

ANNOUNCE_FALLBACK_TEXT: Final = "Das Training konnte gerade nicht abgerufen werden."
ANNOUNCE_LANGUAGE: Final = "de"

FRONTEND_URL_BASE: Final = "/brick_static"
FRONTEND_FILENAME: Final = "brick-training-card.js"
