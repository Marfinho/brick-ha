"""Tests für Diagnostics und die Frontend-Registrierung."""

from __future__ import annotations

import json

from custom_components.brick.const import (
    CONF_CALENDAR_TOKEN,
    CONF_CALENDAR_URL,
    CONF_TOKEN,
    CONF_URL,
    DOMAIN,
)
from custom_components.brick.diagnostics import async_get_config_entry_diagnostics
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from .conftest import BASE, CALENDAR_TOKEN, TOKEN


async def test_diagnostics_redacts_secrets(
    hass: HomeAssistant, mock_summary: AiohttpClientMocker
) -> None:
    """Token, URL und Kalender-Zugangsdaten erscheinen nie in Diagnostics."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=BASE,
        data={
            CONF_URL: BASE,
            CONF_TOKEN: TOKEN,
            CONF_CALENDAR_URL: f"{BASE}/c.ics?token={CALENDAR_TOKEN}",
            CONF_CALENDAR_TOKEN: CALENDAR_TOKEN,
        },
    )
    entry.add_to_hass(hass)
    mock_summary.get(f"{BASE}/c.ics?token={CALENDAR_TOKEN}", content=b"")
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await async_get_config_entry_diagnostics(hass, entry)
    dump = json.dumps(result)
    assert TOKEN not in dump
    assert CALENDAR_TOKEN not in dump
    assert result["entry"][CONF_TOKEN] == "**REDACTED**"
    assert result["entry"][CONF_CALENDAR_URL] == "**REDACTED**"
    assert result["data"]["today_items"] == 3


async def test_card_is_served_and_registered(
    hass: HomeAssistant, entry: MockConfigEntry, mock_summary: AiohttpClientMocker
) -> None:
    """Die Karte wird als statischer Pfad ausgeliefert und im Frontend geladen."""
    from homeassistant.components.frontend import _frontend_root  # noqa: F401
    from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    urls = hass.data[DATA_EXTRA_MODULE_URL].urls
    assert any(u.startswith("/brick_static/brick-training-card.js?v=") for u in urls)
