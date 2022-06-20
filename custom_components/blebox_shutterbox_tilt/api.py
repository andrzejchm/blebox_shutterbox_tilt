"""Sample API Client."""
import logging
from typing import Optional

import aiohttp

from homeassistant.core import HomeAssistant

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class ShutterboxApiClient:
    def __init__(
        self,
        ip_address: str,
        port: str,
        session: aiohttp.ClientSession,
        hass: HomeAssistant,
    ) -> None:
        """Sample API Client."""
        self._ip_address = ip_address
        self._port = port
        self._session = session
        self._hass = hass

    async def async_init_cover(self) -> Optional[dict]:
        """Get data from the API."""
        state_response = await self._session.get(
            f"http://{self._ip_address}/api/shutter/state"
        )
        json = await state_response.json()
        if "shutter" in json.keys():
            return json
        return None

    async def async_open_cover(self) -> None:
        await self._session.get(f"http://{self._ip_address}/s/u/")

    async def async_close_cover(self) -> None:
        await self._session.get(f"http://{self._ip_address}/s/d/")

    async def async_set_cover_position(self, position: int) -> None:
        await self._session.get(f"http://{self._ip_address}/s/p/{position}/")

    async def async_stop_cover(self) -> None:
        await self._session.get(f"http://{self._ip_address}/s/s/")

    async def async_open_cover_tilt(self) -> None:
        await self._session.get(f"http://{self._ip_address}/s/t/100")

    async def async_close_cover_tilt(self) -> None:
        await self._session.get(f"http://{self._ip_address}/s/t/0")

    async def async_set_cover_tilt_position(self, position: int) -> None:
        await self._session.get(f"http://{self._ip_address}/s/t/{position}")

    async def async_stop_cover_tilt(self, position: int) -> None:
        await self._session.get(f"http://{self._ip_address}/s/t/{position}")
