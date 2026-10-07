"""Tests für ICS-Parsing und die Kalender-Entität."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.brick.const import (
    CONF_CALENDAR_TOKEN,
    CONF_CALENDAR_URL,
    CONF_TOKEN,
    CONF_URL,
    DOMAIN,
)
from custom_components.brick.ics import parse_ics

from .conftest import BASE, CALENDAR_TOKEN, FIXTURES, TOKEN

ICS_URL = f"{BASE}/api/calendar/v1/training.ics"
ICS = (FIXTURES / "sample.ics").read_bytes()


def test_parse_ics_all_day_umlauts_folding_escapes() -> None:
    """Ganztägig, Umlaute, gefaltete Zeilen sowie ``\\,`` und ``\\;``."""
    events = parse_ics(ICS)
    assert [e.summary[:12] for e in events] == [
        "Radfahren 1:",
        "Erledigt: La",
        "Wettkampf: D",
    ]
    ride, done, race = events
    assert ride.start == date(2026, 10, 7)
    assert ride.end == date(2026, 10, 8)
    assert ride.description == "Locker bleiben, Puls niedrig; Kadenz 90."
    # DTEND fehlt → ein Tag
    assert done.start == date(2026, 10, 8)
    assert done.end == date(2026, 10, 9)
    assert done.summary == (
        "Erledigt: Laufen 45 min - Schwellenläufe für Ausdauer, Tempo; "
        "Übergänge mit sehr langem Titel"
    )
    assert race.summary == "Wettkampf: Düsseldorf Triathlon Mittel"
    assert ride.uid == "a1@brick.example"


def test_parse_ics_empty_calendar() -> None:
    """Leerer Feed → keine Ereignisse."""
    assert parse_ics(b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nEND:VCALENDAR\r\n") == []


async def _setup_calendar(hass: HomeAssistant, data: dict[str, str]) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=BASE,
        data={CONF_URL: BASE, CONF_TOKEN: TOKEN, **data},
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_calendar_with_token(
    hass: HomeAssistant,
    mock_summary: AiohttpClientMocker,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Token-Quelle: Bearer-Header, Ereignisse, aktuelles Ereignis."""
    freezer.move_to("2026-10-07 08:00:00+02:00")
    mock_summary.get(ICS_URL, content=ICS, headers={"ETag": '"v1"'})
    await _setup_calendar(hass, {CONF_CALENDAR_TOKEN: CALENDAR_TOKEN})

    state = hass.states.get("calendar.brick_training")
    assert state is not None
    assert state.attributes["message"].startswith("Radfahren 1:20 h")
    assert state.attributes["all_day"] is True
    ics_calls = [c for c in mock_summary.mock_calls if str(c[1]).endswith(".ics")]
    assert len(ics_calls) == 1
    assert ics_calls[0][3]["Authorization"] == f"Bearer {CALENDAR_TOKEN}"
    assert CALENDAR_TOKEN not in str(state.attributes)

    component = hass.data["calendar"]
    entity = component.get_entity("calendar.brick_training")
    events = await entity.async_get_events(
        hass,
        dt_util.parse_datetime("2026-10-08T00:00:00+02:00"),
        dt_util.parse_datetime("2026-10-09T00:00:00+02:00"),
    )
    assert [e.summary[:9] for e in events] == ["Erledigt:"]


async def test_calendar_with_url_and_etag(
    hass: HomeAssistant,
    mock_summary: AiohttpClientMocker,
    freezer: FrozenDateTimeFactory,
) -> None:
    """URL-Quelle (Token in der Query); stündlicher Abruf mit If-None-Match."""
    freezer.move_to("2026-10-07 08:00:00+02:00")
    url = f"{ICS_URL}?token={CALENDAR_TOKEN}"
    mock_summary.get(url, content=ICS, headers={"ETag": '"v1"'})
    await _setup_calendar(hass, {CONF_CALENDAR_URL: url})
    assert hass.states.get("calendar.brick_training") is not None

    def ics_calls() -> list:
        return [c for c in mock_summary.mock_calls if ".ics" in str(c[1])]

    assert len(ics_calls()) == 1
    assert "Authorization" not in (ics_calls()[0][3] or {})

    # Innerhalb der Stunde kein weiterer Abruf.
    freezer.tick(timedelta(minutes=30))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(ics_calls()) == 1

    # Nach einer Stunde: bedingter Abruf, 304 behält die Daten.
    mock_summary.clear_requests()
    mock_summary.get(url, status=304)
    freezer.tick(timedelta(minutes=45))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    calls = [c for c in mock_summary.mock_calls if ".ics" in str(c[1])]
    assert calls[-1][3]["If-None-Match"] == '"v1"'
    state = hass.states.get("calendar.brick_training")
    assert state is not None
    assert state.state != "unavailable"


async def test_calendar_error_keeps_entity_unavailable_without_leaking(
    hass: HomeAssistant,
    mock_summary: AiohttpClientMocker,
    caplog: object,
) -> None:
    """Fehlerhafter Feed: Entität nicht verfügbar, Token nicht im Log."""
    url = f"{ICS_URL}?token={CALENDAR_TOKEN}"
    mock_summary.get(url, status=500)
    await _setup_calendar(hass, {CONF_CALENDAR_URL: url})
    state = hass.states.get("calendar.brick_training")
    assert state is not None
    assert state.state == "unavailable"
    assert CALENDAR_TOKEN not in caplog.text  # type: ignore[attr-defined]


async def test_calendar_not_created_without_source(
    hass: HomeAssistant, mock_summary: AiohttpClientMocker
) -> None:
    """Ohne Kalender-Quelle gibt es keine Kalender-Entität."""
    await _setup_calendar(hass, {})
    assert hass.states.get("calendar.brick_training") is None


def test_datetime_unused_import_guard() -> None:
    """Hilfsfunktion akzeptiert auch datetime-Werte nicht-ganztägiger Ereignisse."""
    text = (
        "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VEVENT\r\nUID:x\r\n"
        "DTSTART:20261007T060000Z\r\nDTEND:20261007T070000Z\r\nSUMMARY:Test\r\n"
        "END:VEVENT\r\nEND:VCALENDAR\r\n"
    )
    (event,) = parse_ics(text)
    assert isinstance(event.start, datetime)
