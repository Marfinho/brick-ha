"""Tests für Coordinator, Sensoren und Binärsensor."""

from __future__ import annotations

from datetime import timedelta

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.brick.const import CONF_SCAN_INTERVAL, MIN_SCAN_INTERVAL

from .conftest import SUMMARY, TODAY, TOKEN, TOMORROW, WEEK


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


@pytest.mark.usefixtures("mock_summary")
async def test_setup_and_states(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Zustände und Attribute stammen aus den Beispiel-Antworten."""
    await _setup(hass, entry)
    assert entry.state is ConfigEntryState.LOADED

    today = hass.states.get("sensor.brick_training_heute")
    assert today is not None
    assert today.state == "1"  # Rad offen; Lauf erledigt; Ruhetag zählt nicht
    assert today.attributes["text"] == TODAY["text"]
    assert today.attributes["done_count"] == 1
    assert today.attributes["items"] == TODAY["items"]
    assert today.attributes["date"]
    assert TOKEN not in str(today.attributes)

    tomorrow = hass.states.get("sensor.brick_training_morgen")
    assert tomorrow is not None
    assert tomorrow.state == "1"
    assert tomorrow.attributes["text"] == TOMORROW["text"]
    assert tomorrow.attributes["done_count"] == 0

    week = hass.states.get("sensor.brick_training_woche")
    assert week is not None
    assert week.state == "2"  # zwei geplante, eine erledigt
    assert week.attributes["text"] == WEEK["text"]
    assert len(week.attributes["items"]) == 3

    open_sensor = hass.states.get("binary_sensor.brick_training_offen")
    assert open_sensor is not None
    assert open_sensor.state == "on"

    assert hass.states.get("calendar.brick_training") is None


async def test_long_text_is_not_the_state(
    hass: HomeAssistant, entry: MockConfigEntry, aioclient_mock: AiohttpClientMocker
) -> None:
    """Auch ein Text über 255 Zeichen ist unkritisch, da er im Attribut liegt."""
    long = {**TODAY, "text": "x" * 400, "items": []}
    aioclient_mock.get(f"{SUMMARY}?day=today&detail=normal", json=long)
    aioclient_mock.get(f"{SUMMARY}?day=tomorrow&detail=short", json=TOMORROW)
    aioclient_mock.get(f"{SUMMARY}?day=week&detail=short", json=WEEK)
    await _setup(hass, entry)
    state = hass.states.get("sensor.brick_training_heute")
    assert state is not None
    assert state.state == "0"
    assert len(state.attributes["text"]) == 400
    assert hass.states.get("binary_sensor.brick_training_offen").state == "off"


async def test_three_requests_per_cycle(
    hass: HomeAssistant, entry: MockConfigEntry, mock_summary: AiohttpClientMocker
) -> None:
    """Pro Zyklus genau drei Abrufe mit den richtigen Parametern."""
    await _setup(hass, entry)
    queries = sorted(str(call[1].query_string) for call in mock_summary.mock_calls)
    assert queries == [
        "day=today&detail=normal",
        "day=tomorrow&detail=short",
        "day=week&detail=short",
    ]


async def test_auth_failure_starts_reauth(
    hass: HomeAssistant, entry: MockConfigEntry, aioclient_mock: AiohttpClientMocker
) -> None:
    """401 im Betrieb → SETUP_ERROR und Reauth-Flow."""
    aioclient_mock.get(SUMMARY, status=401, json={"error": "invalid_token"})
    await _setup(hass, entry)
    assert entry.state is ConfigEntryState.SETUP_ERROR
    flows = hass.config_entries.flow.async_progress_by_handler("brick")
    assert [f["context"]["source"] for f in flows] == ["reauth"]


async def test_auth_failure_during_update(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mock_summary: AiohttpClientMocker,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Ein später widerrufenes Token startet Reauth."""
    await _setup(hass, entry)
    mock_summary.clear_requests()
    mock_summary.get(SUMMARY, status=401)
    freezer.tick(timedelta(minutes=16))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    flows = hass.config_entries.flow.async_progress_by_handler("brick")
    assert [f["context"]["source"] for f in flows] == ["reauth"]


async def test_rate_limit_respects_retry_after(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mock_summary: AiohttpClientMocker,
    freezer: FrozenDateTimeFactory,
) -> None:
    """429 → Sensoren nicht verfügbar, nächster Versuch erst nach Retry-After."""
    await _setup(hass, entry)
    coordinator = entry.runtime_data.coordinator
    mock_summary.clear_requests()
    mock_summary.get(SUMMARY, status=429, headers={"Retry-After": "120"})

    freezer.tick(timedelta(minutes=16))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert not coordinator.last_update_success
    assert hass.states.get("sensor.brick_training_heute").state == "unavailable"
    calls = len(mock_summary.mock_calls)
    assert calls == 1  # Abbruch beim ersten 429, kein Hämmern

    freezer.tick(timedelta(seconds=60))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(mock_summary.mock_calls) == calls  # noch innerhalb von Retry-After

    mock_summary.clear_requests()
    mock_summary.get(f"{SUMMARY}?day=today&detail=normal", json=TODAY)
    mock_summary.get(f"{SUMMARY}?day=tomorrow&detail=short", json=TOMORROW)
    mock_summary.get(f"{SUMMARY}?day=week&detail=short", json=WEEK)
    freezer.tick(timedelta(seconds=61))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert coordinator.last_update_success


async def test_connection_error_is_retried(
    hass: HomeAssistant, entry: MockConfigEntry, aioclient_mock: AiohttpClientMocker
) -> None:
    """Netzwerkfehler beim ersten Abruf → SETUP_RETRY."""
    aioclient_mock.get(SUMMARY, status=500)
    await _setup(hass, entry)
    assert entry.state is ConfigEntryState.SETUP_RETRY


@pytest.mark.usefixtures("mock_summary")
async def test_scan_interval_option_has_floor(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    """Das Intervall wird nie unter 5 Minuten gesetzt."""
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options={CONF_SCAN_INTERVAL: 1})
    await _setup(hass, entry)
    interval = entry.runtime_data.coordinator.update_interval
    assert interval == timedelta(minutes=MIN_SCAN_INTERVAL)


@pytest.mark.usefixtures("mock_summary")
async def test_unique_ids_and_device(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    """Alle Entitäten hängen am Gerät "Brick"."""
    await _setup(hass, entry)
    registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(registry, entry.entry_id)
    assert {e.entity_id for e in entries} == {
        "sensor.brick_training_heute",
        "sensor.brick_training_morgen",
        "sensor.brick_training_woche",
        "binary_sensor.brick_training_offen",
    }
    assert len({e.device_id for e in entries}) == 1
