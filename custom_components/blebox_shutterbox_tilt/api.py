"""Sample API Client."""
import logging
from typing import Optional

import aiohttp
from homeassistant.core import HomeAssistant

from .errors import (
    InvalidDeviceTypeError,
    NoDeviceInfoError,
    CannotConnectToShutterBox,
)

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class ShutterboxApiClient:
    """Api client for BleBox shutterBox"""

    def __init__(
            self,
            ip_address: str,
            port: int,
            session: aiohttp.ClientSession,
            hass: HomeAssistant,
    ) -> None:
        """Sample API Client."""
        self._ip_address = ip_address
        self._port = port
        self._session = session
        self._hass = hass

    async def async_get_device_info(self) -> Optional[dict]:
        """Gets device info"""
        try:
            state_response = await self._session.get(
                f"http://{self._ip_address}/api/device/state"
            )
        except Exception as ex:
            raise CannotConnectToShutterBox() from ex
        json = await state_response.json()
        device = json.get("device")
        if not device:
            raise NoDeviceInfoError()
        if device and device.get("type") == "shutterBox":
            return device
        raise InvalidDeviceTypeError()

    async def async_get_cover_state(self) -> Optional[dict]:
        """Get data from the API."""
        state_response = await self._session.get(
            f"http://{self._ip_address}/api/shutter/state"
        )
        return await self._get_state_from_response(state_response)

    @staticmethod
    async def _get_state_from_response(state_response):
        json = await state_response.json()
        if "shutter" in json.keys():
            return json
        return None

    async def async_open_cover(self) -> None:
        """Opens shutterBox fully"""
        response = await self._session.get(f"http://{self._ip_address}/s/u/")
        return await self._get_state_from_response(response)

    async def async_close_cover(self) -> None:
        """Closes shutterBox fully"""
        response = await self._session.get(f"http://{self._ip_address}/s/d/")
        return await self._get_state_from_response(response)

    async def async_set_cover_position(self, position: int) -> None:
        """sets exact shutterBox position"""
        response = await self._session.get(f"http://{self._ip_address}/s/p/{position}/")
        return await self._get_state_from_response(response)

    async def async_stop_cover(self) -> None:
        """Stops shutterBox position change immediately"""
        response = await self._session.get(f"http://{self._ip_address}/s/s/")
        return await self._get_state_from_response(response)

    async def async_open_cover_tilt(self) -> None:
        """Opens shutterBox' tilt fully"""
        response = await self._session.get(f"http://{self._ip_address}/s/t/100")
        return await self._get_state_from_response(response)

    async def async_close_cover_tilt(self) -> None:
        """Closes shutterBox' tilt fully"""
        response = await self._session.get(f"http://{self._ip_address}/s/t/0")
        return await self._get_state_from_response(response)

    async def async_set_cover_tilt_position(self, position: int) -> None:
        """Sets shutterBox' tilt position"""
        response = await self._session.get(f"http://{self._ip_address}/s/t/{position}")
        return await self._get_state_from_response(response)

    async def async_stop_cover_tilt(self, position: int) -> None:
        """Stops shutterBox tilt position change immediately"""
        response = await self._session.get(f"http://{self._ip_address}/s/t/{position}")
        return await self._get_state_from_response(response)
