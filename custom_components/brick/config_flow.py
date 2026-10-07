"""Config Flow: Einrichtung, Reauth, Neukonfiguration und Optionen."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    BrickAuthError,
    BrickClient,
    BrickError,
    BrickRateLimitError,
    is_local_host,
    normalize_url,
)
from .const import (
    CONF_CALENDAR,
    CONF_CALENDAR_TOKEN,
    CONF_CALENDAR_URL,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    CONF_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

URL_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.URL))
SECRET_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))


def parse_calendar_source(raw: str | None) -> dict[str, str]:
    """Zerlegt die Kalender-Eingabe in ``calendar_url`` oder ``calendar_token``.

    Leer → keine Kalender-Quelle. ``http(s)://…`` → fertige Feed-URL. Sonst Token.
    Wirft ``ValueError`` bei ungültiger URL.
    """
    value = (raw or "").strip()
    if not value:
        return {}
    if "://" in value:
        # Der Query-Teil (?token=…) bleibt erhalten, nur Schema/Host prüfen.
        normalize_url(value.split("?", 1)[0])
        return {CONF_CALENDAR_URL: value}
    if any(ch.isspace() for ch in value):
        raise ValueError("invalid_calendar")
    return {CONF_CALENDAR_TOKEN: value}


def _calendar_default(data: Mapping[str, Any]) -> str:
    return data.get(CONF_CALENDAR_URL) or data.get(CONF_CALENDAR_TOKEN) or ""


class BrickConfigFlow(ConfigFlow, domain=DOMAIN):
    """Einrichtung der Brick-Integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialisiert den Flow."""
        self._acknowledged_http: str | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Optionen: Abfrageintervall."""
        return BrickOptionsFlow()

    async def _validate(self, url: str, token: str) -> str | None:
        """Echter Summary-Abruf. Gibt einen Fehlerschlüssel oder None zurück."""
        client = BrickClient(async_get_clientsession(self.hass), url, token)
        try:
            await client.get_summary("today", "short")
        except BrickAuthError:
            return "invalid_auth"
        except BrickRateLimitError:
            return "rate_limited"
        except BrickError:
            return "cannot_connect"
        except Exception:
            _LOGGER.exception("Unerwarteter Fehler bei der Validierung")
            return "unknown"
        return None

    def _check_url(self, raw: str) -> tuple[str | None, str | None]:
        """Normalisiert die URL. Rückgabe: (url, fehler)."""
        try:
            url = normalize_url(raw)
        except ValueError:
            return None, "invalid_url"
        if (
            url.startswith("http://")
            and not is_local_host(url)
            and self._acknowledged_http != url
        ):
            # Warnung: erst beim erneuten Absenden akzeptieren.
            self._acknowledged_http = url
            return url, "insecure_http"
        return url, None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Erste Einrichtung."""
        errors: dict[str, str] = {}
        if user_input is not None:
            url, error = self._check_url(user_input[CONF_URL])
            calendar: dict[str, str] = {}
            if error is None:
                try:
                    calendar = parse_calendar_source(user_input.get(CONF_CALENDAR))
                except ValueError:
                    error = "invalid_calendar"
            if error is None and url is not None:
                await self.async_set_unique_id(url)
                self._abort_if_unique_id_configured()
                error = await self._validate(url, user_input[CONF_TOKEN].strip())
                if error is None:
                    return self.async_create_entry(
                        title=f"Brick ({url.split('://', 1)[1]})",
                        data={
                            CONF_URL: url,
                            CONF_TOKEN: user_input[CONF_TOKEN].strip(),
                            **calendar,
                        },
                    )
            errors["base"] = error or "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_URL): URL_SELECTOR,
                        vol.Required(CONF_TOKEN): SECRET_SELECTOR,
                        vol.Optional(CONF_CALENDAR): SECRET_SELECTOR,
                    }
                ),
                {CONF_URL: user_input.get(CONF_URL)} if user_input else None,
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Token wurde im Betrieb abgelehnt (401)."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Neues Sprachassistent-Token abfragen."""
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            token = user_input[CONF_TOKEN].strip()
            if error := await self._validate(entry.data[CONF_URL], token):
                errors["base"] = error
            else:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_TOKEN: token}
                )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_TOKEN): SECRET_SELECTOR}),
            description_placeholders={"url": entry.data[CONF_URL]},
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """URL (und Kalender-Quelle) ändern."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            url, error = self._check_url(user_input[CONF_URL])
            calendar: dict[str, str] = {}
            if error is None:
                try:
                    calendar = parse_calendar_source(user_input.get(CONF_CALENDAR))
                except ValueError:
                    error = "invalid_calendar"
            if error is None and url is not None:
                if any(
                    other.entry_id != entry.entry_id and other.unique_id == url
                    for other in self._async_current_entries(include_ignore=False)
                ):
                    return self.async_abort(reason="already_configured")
                error = await self._validate(url, entry.data[CONF_TOKEN])
                if error is None:
                    data = {
                        CONF_URL: url,
                        CONF_TOKEN: entry.data[CONF_TOKEN],
                        **calendar,
                    }
                    return self.async_update_reload_and_abort(
                        entry,
                        unique_id=url,
                        title=f"Brick ({url.split('://', 1)[1]})",
                        data=data,
                    )
            errors["base"] = error or "unknown"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_URL): URL_SELECTOR,
                        vol.Optional(CONF_CALENDAR): SECRET_SELECTOR,
                    }
                ),
                {
                    CONF_URL: (user_input or entry.data)[CONF_URL],
                    CONF_CALENDAR: (
                        user_input.get(CONF_CALENDAR)
                        if user_input
                        else _calendar_default(entry.data)
                    ),
                },
            ),
            errors=errors,
        )


class BrickOptionsFlow(OptionsFlow):
    """Abfrageintervall in Minuten (Minimum 5)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Intervall einstellen."""
        if user_input is not None:
            return self.async_create_entry(
                data={CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL])}
            )
        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SCAN_INTERVAL, default=current): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL,
                            max=MAX_SCAN_INTERVAL,
                            step=1,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="min",
                        )
                    )
                }
            ),
        )
