"""Cover platform for BleBox shutterBox with tilt."""

import logging
from datetime import timedelta
from typing import Any, Optional

from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
    ATTR_POSITION,
    ATTR_TILT_POSITION,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_CLOSING, STATE_OPENING, STATE_CLOSED, STATE_OPEN
from .api import ShutterboxApiClient

from .const import DOMAIN, STATE, API_CLIENT, COORDINATOR
from .entity import ShutterboxEntity
from .data_update_coordinator import ShutterboxDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    api = hass.data[DOMAIN][entry.entry_id][API_CLIENT]
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    async_add_devices([BleboxShutterboxCover(api, coordinator, entry)], True)


class BleboxShutterboxCover(ShutterboxEntity, CoverEntity):
    """blebox_shutterbox_tilt cover class."""

    def __init__(
            self,
            api: ShutterboxApiClient,
            coordinator: ShutterboxDataUpdateCoordinator,
            config_entry: ConfigEntry,
    ):
        super().__init__(coordinator, config_entry)
        self.api = api
        self._config_entry = config_entry
        self._attr_supported_features = (
                CoverEntityFeature.SET_POSITION
                | CoverEntityFeature.SET_POSITION
                | CoverEntityFeature.OPEN
                | CoverEntityFeature.CLOSE
                | CoverEntityFeature.OPEN_TILT
                | CoverEntityFeature.CLOSE_TILT
                | CoverEntityFeature.SET_TILT_POSITION
        )

    @property
    def name(self) -> Optional[str]:
        return "ShutterBox"  # TODO

    def _state(self) -> dict[str:any]:
        return self.hass.data[DOMAIN][self._config_entry.entry_id][STATE] or {}

    def _hass_state(self):
        return _BLEBOX_TO_HASS_COVER_STATES[self._state().get("state")]

    @property
    def current_cover_position(self) -> Optional[int]:
        if self._state() is None or self._state().get("currentPos") is None:
            return None
        current_pos = self._state().get("currentPos")
        if current_pos is None:
            return None
        position = current_pos.get("position")
        if position == -1:  # possible for shutterBox
            return None

        return position

    @property
    def current_cover_tilt_position(self) -> Optional[int]:
        current_pos = self._state().get("currentPos")
        if current_pos is None:
            return None
        tilt = current_pos.get("tilt")
        return tilt

    @property
    def is_closed(self) -> Optional[bool]:
        return self._hass_state() == STATE_CLOSED

    @property
    def is_closing(self) -> Optional[bool]:
        return self._hass_state() == STATE_CLOSING

    @property
    def is_opening(self) -> Optional[bool]:
        return self._hass_state() == STATE_OPENING

    @property
    def device_class(self) -> CoverDeviceClass:
        return CoverDeviceClass.BLIND  # TODO

    async def async_open_cover(self, **kwargs):
        return await self.api.async_open_cover()

    async def async_close_cover(self, **kwargs):
        return await self.api.async_close_cover()

    async def async_set_cover_position(self, **kwargs):
        position = kwargs[ATTR_POSITION]
        return await self.api.async_set_cover_position(100 - position)

    async def async_stop_cover(self, **kwargs):
        return await self.api.async_stop_cover()

    async def async_open_cover_tilt(self, **kwargs):
        return await self.api.async_open_cover_tilt()

    async def async_close_cover_tilt(self, **kwargs):
        return await self.api.async_close_cover_tilt()

    async def async_set_cover_tilt_position(self, **kwargs):
        position = kwargs[ATTR_TILT_POSITION]
        return await self.api.async_set_cover_tilt_position(position)

    async def async_update(self) -> None:
        return await super().async_update() # TODO


_BLEBOX_TO_HASS_COVER_STATES = {
    None: None,
    0: STATE_CLOSING,  # moving down
    1: STATE_OPENING,  # moving up
    2: STATE_OPEN,  # manually stopped
    3: STATE_CLOSED,  # lower limit
    4: STATE_OPEN,  # upper limit / open
    # gateController
    5: STATE_OPEN,  # overload
    6: STATE_OPEN,  # motor failure
    # 7 is not used
    8: STATE_OPEN,  # safety stop
}
