"""Services brick.announce und brick.refresh."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

import voluptuous as vol
from homeassistant.const import ATTR_ENTITY_ID, STATE_PLAYING
from homeassistant.core import (
    Event,
    EventStateChangedData,
    HomeAssistant,
    ServiceCall,
    callback,
)
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change_event

from .api import BrickError, BrickSummary
from .const import (
    ANNOUNCE_FALLBACK_TEXT,
    ANNOUNCE_LANGUAGE,
    DOMAIN,
    SERVICE_ANNOUNCE,
    SERVICE_REFRESH,
)

_LOGGER = logging.getLogger(__name__)

ATTR_DAY = "day"
ATTR_DETAIL = "detail"
ATTR_MEDIA_PLAYER = "media_player"
ATTR_TTS_ENTITY = "tts_entity"
ATTR_VOLUME = "volume"
ATTR_RESTORE_VOLUME = "restore_volume"
ATTR_NOTIFY_SERVICE = "notify_service"
ATTR_CONFIG_ENTRY = "config_entry"

# Wie lange auf den Start bzw. das Ende der Sprachausgabe gewartet wird (Sekunden).
START_TIMEOUT = 10.0
PLAYBACK_TIMEOUT = 120.0

ANNOUNCE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DAY, default="today"): vol.In(["today", "tomorrow", "week"]),
        vol.Optional(ATTR_DETAIL, default="normal"): vol.In(["short", "normal"]),
        vol.Optional(ATTR_MEDIA_PLAYER): cv.entity_ids,
        vol.Optional(ATTR_TTS_ENTITY): cv.entity_id,
        vol.Optional(ATTR_VOLUME): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
        vol.Optional(ATTR_RESTORE_VOLUME, default=True): cv.boolean,
        vol.Optional(ATTR_NOTIFY_SERVICE): cv.string,
        vol.Optional(ATTR_CONFIG_ENTRY): cv.string,
    }
)
REFRESH_SCHEMA = vol.Schema({vol.Optional(ATTR_CONFIG_ENTRY): cv.string})


@callback
def async_register_services(hass: HomeAssistant) -> None:
    """Registriert die Services der Domain (einmalig in async_setup)."""

    async def _announce(call: ServiceCall) -> None:
        await async_announce(call)

    async def _refresh(call: ServiceCall) -> None:
        for entry in _entries(call):
            await entry.runtime_data.coordinator.async_refresh_throttled()

    hass.services.async_register(
        DOMAIN, SERVICE_ANNOUNCE, _announce, schema=ANNOUNCE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_REFRESH, _refresh, schema=REFRESH_SCHEMA
    )


def _entries(call: ServiceCall) -> list[Any]:
    entries = [
        entry
        for entry in call.hass.config_entries.async_loaded_entries(DOMAIN)
        if call.data.get(ATTR_CONFIG_ENTRY) in (None, entry.entry_id)
    ]
    if not entries:
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="no_loaded_entry"
        )
    return entries


async def async_announce(call: ServiceCall) -> None:
    """Spricht den Trainingsplan über TTS oder Alexa Media Player."""
    hass = call.hass
    data = call.data
    players: list[str] = data.get(ATTR_MEDIA_PLAYER, [])
    tts_entity: str | None = data.get(ATTR_TTS_ENTITY)
    notify_service: str | None = data.get(ATTR_NOTIFY_SERVICE)

    if not notify_service and not (players and tts_entity):
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="announce_target_missing"
        )
    notify_name = _split_notify(notify_service) if notify_service else None

    entry = _entries(call)[0]
    try:
        summary: BrickSummary | None = await entry.runtime_data.client.get_summary(
            data[ATTR_DAY], data[ATTR_DETAIL]
        )
    except BrickError as err:
        _LOGGER.warning("Brick-Abruf für die Ansage fehlgeschlagen (%s)", err)
        summary = None
    text = summary.text if summary and summary.text else ANNOUNCE_FALLBACK_TEXT

    volume: float | None = data.get(ATTR_VOLUME)
    restore: bool = data[ATTR_RESTORE_VOLUME]
    previous = {
        player: _volume_level(hass, player) for player in players
    }  # vor dem Setzen merken

    try:
        if volume is not None:
            for player in players:
                await _set_volume(hass, player, volume)
        if notify_name:
            payload: dict[str, Any] = {"message": text, "data": {"type": "tts"}}
            if players:
                payload["target"] = players
            await hass.services.async_call(
                "notify", notify_name, payload, blocking=True
            )
            await asyncio.gather(*(_await_playback(hass, player) for player in players))
        else:
            assert tts_entity is not None
            await asyncio.gather(
                *(_speak(hass, tts_entity, player, text) for player in players)
            )
    finally:
        if volume is not None and restore:
            for player, old in previous.items():
                if old is not None:
                    try:
                        await _set_volume(hass, player, old)
                    except HomeAssistantError as err:
                        _LOGGER.warning(
                            "Lautstärke von %s nicht zurückgesetzt (%s)", player, err
                        )


def _split_notify(service: str) -> str:
    domain, _, name = service.partition(".")
    if domain != "notify" or not name:
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="invalid_notify_service"
        )
    return name


def _volume_level(hass: HomeAssistant, entity_id: str) -> float | None:
    state = hass.states.get(entity_id)
    level = state.attributes.get("volume_level") if state else None
    return float(level) if isinstance(level, int | float) else None


async def _set_volume(hass: HomeAssistant, entity_id: str, level: float) -> None:
    await hass.services.async_call(
        "media_player",
        "volume_set",
        {ATTR_ENTITY_ID: entity_id, "volume_level": level},
        blocking=True,
    )


async def _speak(hass: HomeAssistant, tts_entity: str, player: str, text: str) -> None:
    await hass.services.async_call(
        "tts",
        "speak",
        {
            ATTR_ENTITY_ID: tts_entity,
            "media_player_entity_id": player,
            "message": text,
            "language": ANNOUNCE_LANGUAGE,
        },
        blocking=True,
    )
    await _await_playback(hass, player)


async def _await_playback(hass: HomeAssistant, player: str) -> None:
    """Wartet, bis die Ausgabe beginnt und wieder endet (jeweils mit Timeout)."""
    if await _wait_for_state(hass, player, lambda s: s == STATE_PLAYING, START_TIMEOUT):
        await _wait_for_state(
            hass, player, lambda s: s != STATE_PLAYING, PLAYBACK_TIMEOUT
        )


async def _wait_for_state(
    hass: HomeAssistant,
    entity_id: str,
    predicate: Callable[[str | None], bool],
    timeout_s: float,
) -> bool:
    """Wartet, bis der Zustand das Prädikat erfüllt. False bei Timeout."""
    state = hass.states.get(entity_id)
    if predicate(state.state if state else None):
        return True
    done: asyncio.Future[None] = hass.loop.create_future()

    @callback
    def _changed(event: Event[EventStateChangedData]) -> None:
        new = event.data["new_state"]
        if not done.done() and predicate(new.state if new else None):
            done.set_result(None)

    unsubscribe = async_track_state_change_event(hass, [entity_id], _changed)
    try:
        async with asyncio.timeout(timeout_s):
            await done
    except TimeoutError:
        return False
    finally:
        unsubscribe()
    return True
