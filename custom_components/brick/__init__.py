"""Brick: Triathlon-Training in Home Assistant."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration

from .api import BrickClient
from .const import (
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    CONF_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    FRONTEND_FILENAME,
    FRONTEND_URL_BASE,
    MIN_SCAN_INTERVAL,
)
from .coordinator import BrickCoordinator
from .services import async_register_services

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.CALENDAR]


@dataclass(slots=True)
class BrickRuntimeData:
    """Laufzeitdaten eines Config Entries."""

    client: BrickClient
    coordinator: BrickCoordinator


type BrickConfigEntry = ConfigEntry[BrickRuntimeData]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Registriert Services und die mitgelieferte Lovelace-Karte."""
    async_register_services(hass)
    await _async_register_frontend(hass)
    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Liefert dist/brick-training-card.js aus und lädt es im Frontend."""
    card = Path(__file__).parent / "dist" / FRONTEND_FILENAME
    if not await hass.async_add_executor_job(card.is_file):
        _LOGGER.warning("Lovelace-Karte nicht gefunden: %s", card.name)
        return
    url = f"{FRONTEND_URL_BASE}/{FRONTEND_FILENAME}"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(url, str(card), cache_headers=False)]
    )
    version = await _async_integration_version(hass)
    frontend.add_extra_js_url(hass, f"{url}?v={version}")


async def _async_integration_version(hass: HomeAssistant) -> str:
    return str((await async_get_integration(hass, DOMAIN)).version or "0")


async def async_setup_entry(hass: HomeAssistant, entry: BrickConfigEntry) -> bool:
    """Richtet einen Config Entry ein."""
    client = BrickClient(
        async_get_clientsession(hass), entry.data[CONF_URL], entry.data[CONF_TOKEN]
    )
    minutes = max(
        MIN_SCAN_INTERVAL,
        int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
    )
    coordinator = BrickCoordinator(hass, entry, client, timedelta(minutes=minutes))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = BrickRuntimeData(client=client, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: BrickConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: BrickConfigEntry) -> bool:
    """Entlädt einen Config Entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
