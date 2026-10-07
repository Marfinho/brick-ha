"""Tests für Config Flow, Reauth, Reconfigure und Optionen."""

from __future__ import annotations

from unittest.mock import patch

import aiohttp
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.brick.config_flow import parse_calendar_source
from custom_components.brick.const import (
    CONF_CALENDAR,
    CONF_CALENDAR_TOKEN,
    CONF_CALENDAR_URL,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    CONF_URL,
    DOMAIN,
)

from .conftest import BASE, CALENDAR_TOKEN, SUMMARY, TOKEN, TOMORROW


async def _start(hass: HomeAssistant, data: dict[str, str]):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    return await hass.config_entries.flow.async_configure(result["flow_id"], data)


async def test_user_flow_success(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Erfolgreiche Einrichtung mit URL-Normalisierung und echtem Abruf."""
    aioclient_mock.get(SUMMARY, json=TOMORROW)
    with patch("custom_components.brick.async_setup_entry", return_value=True):
        result = await _start(
            hass,
            {
                CONF_URL: "HTTPS://Brick.Example/ ",
                CONF_TOKEN: f" {TOKEN} ",
                CONF_CALENDAR: CALENDAR_TOKEN,
            },
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_URL: BASE,
        CONF_TOKEN: TOKEN,
        CONF_CALENDAR_TOKEN: CALENDAR_TOKEN,
    }
    assert result["result"].unique_id == BASE
    call = aioclient_mock.mock_calls[0]
    assert call[3]["Authorization"] == f"Bearer {TOKEN}"


async def test_user_flow_invalid_auth(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """401 → invalid_auth."""
    aioclient_mock.get(SUMMARY, status=401, json={"error": "invalid_token"})
    result = await _start(hass, {CONF_URL: BASE, CONF_TOKEN: TOKEN})
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_cannot_connect(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Netzwerkfehler → cannot_connect."""
    aioclient_mock.get(SUMMARY, exc=aiohttp.ClientError("boom"))
    result = await _start(hass, {CONF_URL: BASE, CONF_TOKEN: TOKEN})
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_rate_limited(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """429 → rate_limited."""
    aioclient_mock.get(SUMMARY, status=429, headers={"Retry-After": "30"})
    result = await _start(hass, {CONF_URL: BASE, CONF_TOKEN: TOKEN})
    assert result["errors"] == {"base": "rate_limited"}


async def test_user_flow_url_without_scheme(hass: HomeAssistant) -> None:
    """URL ohne Schema → Formularfehler, kein Netzwerkzugriff."""
    result = await _start(hass, {CONF_URL: "brick.example", CONF_TOKEN: TOKEN})
    assert result["errors"] == {"base": "invalid_url"}


async def test_user_flow_invalid_calendar(hass: HomeAssistant) -> None:
    """Kalender-Eingabe mit Leerzeichen ist ungültig."""
    result = await _start(
        hass, {CONF_URL: BASE, CONF_TOKEN: TOKEN, CONF_CALENDAR: "a b"}
    )
    assert result["errors"] == {"base": "invalid_calendar"}


async def test_user_flow_http_warning_needs_confirmation(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """http:// außerhalb des LAN warnt und verlangt erneutes Absenden."""
    url = "http://brick.example"
    aioclient_mock.get(f"{url}/api/voice/v1/summary", json=TOMORROW)
    data = {CONF_URL: url, CONF_TOKEN: TOKEN}
    result = await _start(hass, data)
    assert result["errors"] == {"base": "insecure_http"}
    assert not aioclient_mock.mock_calls
    with patch("custom_components.brick.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], data)
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_http_in_lan_needs_no_warning(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """http:// im LAN ist ohne Warnung erlaubt."""
    url = "http://192.168.1.20:8080"
    aioclient_mock.get(f"{url}/api/voice/v1/summary", json=TOMORROW)
    with patch("custom_components.brick.async_setup_entry", return_value=True):
        result = await _start(hass, {CONF_URL: url, CONF_TOKEN: TOKEN})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_URL] == url


async def test_user_flow_already_configured(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    """Dieselbe normalisierte URL kann nur einmal eingerichtet werden."""
    entry.add_to_hass(hass)
    result = await _start(hass, {CONF_URL: f"{BASE}/", CONF_TOKEN: TOKEN})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reauth_flow(
    hass: HomeAssistant, entry: MockConfigEntry, aioclient_mock: AiohttpClientMocker
) -> None:
    """Reauth: falsches Token → Fehler, richtiges Token → aktualisiert."""
    entry.add_to_hass(hass)
    result = await entry.start_reauth_flow(hass)
    assert result["step_id"] == "reauth_confirm"

    aioclient_mock.get(SUMMARY, status=401)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_TOKEN: "lht_wrong"}
    )
    assert result["errors"] == {"base": "invalid_auth"}

    aioclient_mock.clear_requests()
    aioclient_mock.get(SUMMARY, json=TOMORROW)
    with patch("custom_components.brick.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_TOKEN: "lht_new"}
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.data[CONF_TOKEN] == "lht_new"


async def test_reconfigure_flow(
    hass: HomeAssistant, entry: MockConfigEntry, aioclient_mock: AiohttpClientMocker
) -> None:
    """Reconfigure ändert URL und unique_id."""
    entry.add_to_hass(hass)
    new = "https://brick2.example"
    aioclient_mock.get(f"{new}/api/voice/v1/summary", json=TOMORROW)
    result = await entry.start_reconfigure_flow(hass)
    assert result["step_id"] == "reconfigure"
    with patch("custom_components.brick.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_URL: new, CONF_CALENDAR: f"{new}/api/calendar/v1/training.ics"},
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_URL] == new
    assert entry.data[CONF_TOKEN] == TOKEN
    assert entry.unique_id == new
    assert CONF_CALENDAR_URL in entry.data


async def test_reconfigure_flow_url_in_use(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    """Reconfigure auf eine bereits eingerichtete URL bricht ab."""
    entry.add_to_hass(hass)
    other = MockConfigEntry(
        domain=DOMAIN,
        unique_id="https://other.example",
        data={CONF_URL: "https://other.example", CONF_TOKEN: "lht_x"},
    )
    other.add_to_hass(hass)
    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_URL: "https://other.example"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Optionen speichern das Abfrageintervall."""
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    with patch("custom_components.brick.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_SCAN_INTERVAL: 30}
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_SCAN_INTERVAL] == 30


def test_parse_calendar_source() -> None:
    """URL, Token, leer und ungültig."""
    assert parse_calendar_source("") == {}
    assert parse_calendar_source(None) == {}
    assert parse_calendar_source("lht_abc") == {CONF_CALENDAR_TOKEN: "lht_abc"}
    url = f"{BASE}/api/calendar/v1/training.ics?token=lht_abc"
    assert parse_calendar_source(url) == {CONF_CALENDAR_URL: url}
