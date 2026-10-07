"""Schlanker Client für die Brick-Sprachassistent-API (nur der Summary-Endpunkt)."""

from __future__ import annotations

import asyncio
import ipaddress
from dataclasses import dataclass
from typing import Any, Literal, TypedDict
from urllib.parse import urlsplit

import aiohttp

from .const import CALENDAR_PATH, REQUEST_TIMEOUT, SUMMARY_PATH

Day = Literal["today", "tomorrow", "week"]
Detail = Literal["short", "normal"]

LOCAL_SUFFIXES = (".local", ".lan", ".home", ".internal", ".localdomain", ".home.arpa")


class BrickError(Exception):
    """Basisklasse für alle Brick-Fehler."""


class BrickConnectionError(BrickError):
    """Brick ist nicht erreichbar oder antwortet unerwartet."""


class BrickAuthError(BrickError):
    """Das Token ist ungültig, widerrufen oder hat den falschen Scope."""


class BrickRateLimitError(BrickError):
    """Brick hat die Abfrage mit 429 abgelehnt."""

    def __init__(self, retry_after: float | None) -> None:
        """Merkt sich die Wartezeit in Sekunden."""
        super().__init__("too_many_requests")
        self.retry_after = retry_after


class BrickItem(TypedDict):
    """Eine Trainingseinheit aus dem Summary-Endpunkt."""

    sport: str
    title: str
    durationMin: int
    status: str
    date: str


@dataclass(frozen=True, slots=True)
class BrickSummary:
    """Antwort des Summary-Endpunkts."""

    text: str
    items: list[BrickItem]


def normalize_url(raw: str) -> str:
    """Normalisiert die Brick-URL (Schema, Kleinschreibung, ohne Slash am Ende).

    Wirft ``ValueError``, wenn Schema oder Host fehlen.
    """
    parts = urlsplit(raw.strip())
    if parts.scheme.lower() not in ("http", "https") or not parts.hostname:
        raise ValueError("invalid_url")
    try:
        port = parts.port
    except ValueError as err:
        raise ValueError("invalid_url") from err
    host = parts.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    netloc = f"{host}:{port}" if port else host
    path = parts.path.rstrip("/")
    return f"{parts.scheme.lower()}://{netloc}{path}"


def is_local_host(url: str) -> bool:
    """Prüft, ob die URL ins lokale Netz zeigt (für den http://-Warnhinweis)."""
    host = (urlsplit(url).hostname or "").lower()
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return host == "localhost" or "." not in host or host.endswith(LOCAL_SUFFIXES)
    return address.is_private or address.is_loopback or address.is_link_local


def calendar_url_for(base_url: str) -> str:
    """Kalender-Endpunkt zur Brick-URL."""
    return f"{base_url}{CALENDAR_PATH}"


class BrickClient:
    """Ruft ``/api/voice/v1/summary`` ab. Das Token wird nie geloggt."""

    def __init__(
        self, session: aiohttp.ClientSession, base_url: str, token: str
    ) -> None:
        """Erzeugt den Client."""
        self._session = session
        self._base_url = base_url
        self._token = token

    @property
    def base_url(self) -> str:
        """Normalisierte Brick-URL."""
        return self._base_url

    async def get_summary(self, day: Day, detail: Detail) -> BrickSummary:
        """Holt Sprechtext und Einheiten."""
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(
                    f"{self._base_url}{SUMMARY_PATH}",
                    params={"day": day, "detail": detail},
                    headers={
                        "Authorization": f"Bearer {self._token}",
                        "Accept": "application/json",
                    },
                )
                async with response:
                    return await self._handle(response)
        except TimeoutError as err:
            raise BrickConnectionError("timeout") from err
        except aiohttp.ClientError as err:
            # Bewusst nur der Typ: Exception-Texte können URLs enthalten.
            raise BrickConnectionError(type(err).__name__) from err

    @staticmethod
    async def _handle(response: aiohttp.ClientResponse) -> BrickSummary:
        if response.status == 401:
            raise BrickAuthError("invalid_token")
        if response.status == 429:
            raise BrickRateLimitError(_parse_retry_after(response.headers))
        if response.status != 200:
            raise BrickConnectionError(f"http_{response.status}")
        try:
            payload = await response.json(content_type=None)
        except (aiohttp.ClientError, ValueError) as err:
            raise BrickConnectionError("invalid_json") from err
        return parse_summary(payload)


def _parse_retry_after(headers: Any) -> float | None:
    try:
        return max(1.0, float(headers.get("Retry-After")))
    except (TypeError, ValueError):
        return None


def parse_summary(payload: Any) -> BrickSummary:
    """Validiert und normalisiert die JSON-Antwort."""
    if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
        raise BrickConnectionError("invalid_payload")
    raw_items = payload.get("items", [])
    if not isinstance(raw_items, list):
        raise BrickConnectionError("invalid_payload")
    items: list[BrickItem] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        duration = raw.get("durationMin")
        items.append(
            BrickItem(
                sport=str(raw.get("sport", "other")),
                title=str(raw.get("title", "")),
                durationMin=duration if isinstance(duration, int) else 0,
                status=str(raw.get("status", "planned")),
                date=str(raw.get("date", "")),
            )
        )
    return BrickSummary(text=payload["text"], items=items)
