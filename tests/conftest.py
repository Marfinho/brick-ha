"""Gemeinsame Fixtures. Es werden nie echte HTTP-Aufrufe gemacht."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.brick.const import (
    CONF_TOKEN,
    CONF_URL,
    DOMAIN,
)

BASE = "https://brick.example"
# Nur Testdaten ohne Bezug zu einem echten Token.
TOKEN = "lht_test_voice_token"
CALENDAR_TOKEN = "lht_test_calendar_token"
SUMMARY = f"{BASE}/api/voice/v1/summary"
FIXTURES = Path(__file__).parent / "fixtures"

TODAY: dict[str, Any] = {
    "text": "Heute steht Radfahren für 1 Stunde 20 auf dem Plan. Du bist gut erholt.",
    "items": [
        {
            "sport": "bike",
            "title": "Grundlagen Z2",
            "durationMin": 80,
            "status": "planned",
            "date": "2026-10-07",
        },
        {
            "sport": "run",
            "title": "Lockerer Lauf",
            "durationMin": 45,
            "status": "done",
            "date": "2026-10-07",
        },
        {
            "sport": "rest",
            "title": "Ruhe",
            "durationMin": 0,
            "status": "planned",
            "date": "2026-10-07",
        },
    ],
}
TOMORROW: dict[str, Any] = {
    "text": "Morgen schwimmst du 45 Minuten.",
    "items": [
        {
            "sport": "swim",
            "title": "Technik",
            "durationMin": 45,
            "status": "planned",
            "date": "2026-10-08",
        }
    ],
}
WEEK: dict[str, Any] = {
    "text": "In den nächsten Tagen stehen 3 Einheiten an.",
    "items": [*TODAY["items"][:2], *TOMORROW["items"]],
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Custom Integrations in allen Tests aktivieren."""


@pytest.fixture
def mock_summary(aioclient_mock: AiohttpClientMocker) -> AiohttpClientMocker:
    """Erfolgreiche Summary-Antworten für alle drei Abrufe."""
    aioclient_mock.get(f"{SUMMARY}?day=today&detail=normal", json=TODAY)
    aioclient_mock.get(f"{SUMMARY}?day=tomorrow&detail=short", json=TOMORROW)
    aioclient_mock.get(f"{SUMMARY}?day=week&detail=short", json=WEEK)
    return aioclient_mock


@pytest.fixture
def entry() -> MockConfigEntry:
    """Config Entry ohne Kalender."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=BASE,
        title="Brick",
        data={CONF_URL: BASE, CONF_TOKEN: TOKEN},
    )
