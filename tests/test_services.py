"""Tests für brick.announce und brick.refresh."""

from __future__ import annotations

import asyncio
import time
from datetime import timedelta
from unittest.mock import patch

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.brick.const import ANNOUNCE_FALLBACK_TEXT, DOMAIN

from .conftest import SUMMARY, TODAY

PLAYER = "media_player.kueche"
TTS = "tts.home_assistant_cloud"


@pytest.fixture(autouse=True)
def fast_timeouts():
    """Warte-Timeouts verkürzen, damit Tests nicht 10 Sekunden brauchen."""
    with (
        patch("custom_components.brick.services.START_TIMEOUT", 0.05),
        patch("custom_components.brick.services.PLAYBACK_TIMEOUT", 2.0),
    ):
        yield


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


def _player(hass: HomeAssistant, state: str = "idle", volume: float = 0.3) -> None:
    hass.states.async_set(PLAYER, state, {"volume_level": volume})


async def test_announce_sets_and_restores_volume(
    hass: HomeAssistant, entry: MockConfigEntry, mock_summary: AiohttpClientMocker
) -> None:
    """Lautstärke setzen, sprechen, alte Lautstärke wiederherstellen."""
    await _setup(hass, entry)
    _player(hass)
    volume = async_mock_service(hass, "media_player", "volume_set")
    speak = async_mock_service(hass, "tts", "speak")

    await hass.services.async_call(
        DOMAIN,
        "announce",
        {
            "day": "today",
            "media_player": [PLAYER],
            "tts_entity": TTS,
            "volume": 0.7,
        },
        blocking=True,
    )

    assert [c.data["volume_level"] for c in volume] == [0.7, 0.3]
    assert len(speak) == 1
    assert speak[0].data == {
        "entity_id": TTS,
        "media_player_entity_id": PLAYER,
        "message": TODAY["text"],
        "language": "de",
    }


async def test_announce_waits_for_playback_end(
    hass: HomeAssistant, entry: MockConfigEntry, mock_summary: AiohttpClientMocker
) -> None:
    """Die Lautstärke wird erst nach dem Ende der Ausgabe zurückgesetzt."""
    await _setup(hass, entry)
    _player(hass)
    volume = async_mock_service(hass, "media_player", "volume_set")

    async def speak(call):
        hass.states.async_set(PLAYER, "playing", {"volume_level": 0.7})

    hass.services.async_register("tts", "speak", speak)

    task = hass.async_create_task(
        hass.services.async_call(
            DOMAIN,
            "announce",
            {"media_player": [PLAYER], "tts_entity": TTS, "volume": 0.7},
            blocking=True,
        )
    )
    for _ in range(10):  # block_till_done würde auf die laufende Ansage warten
        await asyncio.sleep(0)
    assert not task.done()
    assert len(volume) == 1  # noch keine Wiederherstellung

    hass.states.async_set(PLAYER, "idle", {"volume_level": 0.7})
    await task
    assert [c.data["volume_level"] for c in volume] == [0.7, 0.3]


async def test_announce_without_volume_keeps_volume(
    hass: HomeAssistant, entry: MockConfigEntry, mock_summary: AiohttpClientMocker
) -> None:
    """Ohne volume wird nichts gesetzt oder zurückgesetzt."""
    await _setup(hass, entry)
    _player(hass)
    volume = async_mock_service(hass, "media_player", "volume_set")
    async_mock_service(hass, "tts", "speak")
    await hass.services.async_call(
        DOMAIN,
        "announce",
        {"media_player": [PLAYER], "tts_entity": TTS},
        blocking=True,
    )
    assert not volume


async def test_announce_no_restore(
    hass: HomeAssistant, entry: MockConfigEntry, mock_summary: AiohttpClientMocker
) -> None:
    """restore_volume=false lässt die neue Lautstärke stehen."""
    await _setup(hass, entry)
    _player(hass)
    volume = async_mock_service(hass, "media_player", "volume_set")
    async_mock_service(hass, "tts", "speak")
    await hass.services.async_call(
        DOMAIN,
        "announce",
        {
            "media_player": [PLAYER],
            "tts_entity": TTS,
            "volume": 0.5,
            "restore_volume": False,
        },
        blocking=True,
    )
    assert [c.data["volume_level"] for c in volume] == [0.5]


async def test_announce_fetch_failure_speaks_fallback(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    aioclient_mock: AiohttpClientMocker,
    mock_summary: AiohttpClientMocker,
) -> None:
    """Fällt der Abruf aus, wird der Ersatztext gesprochen."""
    await _setup(hass, entry)
    _player(hass)
    aioclient_mock.clear_requests()
    aioclient_mock.get(SUMMARY, status=500)
    speak = async_mock_service(hass, "tts", "speak")
    await hass.services.async_call(
        DOMAIN,
        "announce",
        {"media_player": [PLAYER], "tts_entity": TTS},
        blocking=True,
    )
    assert speak[0].data["message"] == ANNOUNCE_FALLBACK_TEXT
    assert (
        ANNOUNCE_FALLBACK_TEXT == "Das Training konnte gerade nicht abgerufen werden."
    )


async def test_announce_restores_volume_when_tts_fails(
    hass: HomeAssistant, entry: MockConfigEntry, mock_summary: AiohttpClientMocker
) -> None:
    """Auch bei einem TTS-Fehler wird die Lautstärke zurückgesetzt."""
    await _setup(hass, entry)
    _player(hass)
    volume = async_mock_service(hass, "media_player", "volume_set")

    async def speak(call):
        raise ServiceValidationError("tts kaputt")

    hass.services.async_register("tts", "speak", speak)
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "announce",
            {"media_player": [PLAYER], "tts_entity": TTS, "volume": 0.9},
            blocking=True,
        )
    assert [c.data["volume_level"] for c in volume] == [0.9, 0.3]


async def test_announce_alexa_notify(
    hass: HomeAssistant, entry: MockConfigEntry, mock_summary: AiohttpClientMocker
) -> None:
    """Alexa Media Player: notify mit data.type=tts, kein tts.speak."""
    await _setup(hass, entry)
    notify = async_mock_service(hass, "notify", "alexa_media_echo_kueche")
    speak = async_mock_service(hass, "tts", "speak")
    await hass.services.async_call(
        DOMAIN,
        "announce",
        {"notify_service": "notify.alexa_media_echo_kueche", "day": "today"},
        blocking=True,
    )
    assert not speak
    assert notify[0].data == {"message": TODAY["text"], "data": {"type": "tts"}}


async def test_announce_requires_target(
    hass: HomeAssistant, entry: MockConfigEntry, mock_summary: AiohttpClientMocker
) -> None:
    """Ohne Ziel gibt es einen Validierungsfehler."""
    await _setup(hass, entry)
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "announce", {"media_player": [PLAYER]}, blocking=True
        )
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, "announce", {"notify_service": "light.kueche"}, blocking=True
        )


async def test_refresh_respects_minimum_gap(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mock_summary: AiohttpClientMocker,
    freezer: FrozenDateTimeFactory,
) -> None:
    """brick.refresh ruft höchstens alle 30 s ab."""
    await _setup(hass, entry)
    assert len(mock_summary.mock_calls) == 3

    await hass.services.async_call(DOMAIN, "refresh", {}, blocking=True)
    assert len(mock_summary.mock_calls) == 3  # zu früh

    with patch(
        "custom_components.brick.coordinator.time.monotonic",
        return_value=time.monotonic() + 31,
    ):
        await hass.services.async_call(DOMAIN, "refresh", {}, blocking=True)
    assert len(mock_summary.mock_calls) == 6
    _ = timedelta  # Zeitquelle ist monotonic, nicht freezegun
