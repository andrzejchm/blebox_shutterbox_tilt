"""Cover platform for BleBox shutterBox with tilt."""

import logging
from datetime import timedelta
from typing import Optional

from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
    ATTR_POSITION,
    ATTR_TILT_POSITION,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_CLOSING, STATE_OPENING, STATE_CLOSED, STATE_OPEN
from homeassistant.helpers.entity import DeviceInfo

from .api import ShutterboxApiClient

from .const import DOMAIN, STATE, API_CLIENT, DEVICE_INFO, VERSION

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    api = hass.data[DOMAIN][entry.entry_id][API_CLIENT]
    async_add_devices([BleboxShutterboxCover(api, entry)], True)


class BleboxShutterboxCover(CoverEntity):
    """blebox_shutterbox_tilt cover class."""

    def __init__(
            self,
            api: ShutterboxApiClient,
            config_entry: ConfigEntry,
    ):
        super().__init__()
        self._api = api
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
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self._config_entry.entry_id

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=self._device_info().get("deviceName"),
            model=VERSION,
            manufacturer="BleBox",
        )

    @property
    def name(self) -> Optional[str]:
        return self._device_info().get("deviceName")

    @property
    def current_cover_position(self) -> Optional[int]:
        desired_pos = self._desired_position()
        if desired_pos is None:
            return None
        position = desired_pos.get("position")
        if position == -1 or position is None:  # possible for shutterBox
            return None

        return 100 - position

    @property
    def current_cover_tilt_position(self) -> Optional[int]:
        desired_pos = self._desired_position()
        if desired_pos is None:
            return None
        tilt = desired_pos.get("tilt")
        return tilt

    @property
    def is_closed(self) -> Optional[bool]:
        return self._cover_state() == STATE_CLOSED

    @property
    def is_closing(self) -> Optional[bool]:
        return self._cover_state() == STATE_CLOSING

    @property
    def is_opening(self) -> Optional[bool]:
        return self._cover_state() == STATE_OPENING

    @property
    def device_class(self) -> CoverDeviceClass:
        return CoverDeviceClass.SHUTTER

    async def async_open_cover(self, **kwargs):
        await self._update_hass_state(await self._api.async_open_cover())

    async def async_close_cover(self, **kwargs):
        await self._update_hass_state(await self._api.async_close_cover())

    async def async_set_cover_position(self, **kwargs):
        position = kwargs[ATTR_POSITION]
        await self._update_hass_state(
            await self._api.async_set_cover_position(100 - position)
        )

    async def async_stop_cover(self, **kwargs):
        await self._update_hass_state(await self._api.async_stop_cover())

    async def async_open_cover_tilt(self, **kwargs):
        await self._update_hass_state(await self._api.async_open_cover_tilt())

    async def async_close_cover_tilt(self, **kwargs):
        await self._update_hass_state(await self._api.async_close_cover_tilt())

    async def async_set_cover_tilt_position(self, **kwargs):
        position = kwargs[ATTR_TILT_POSITION]
        await self._update_hass_state(
            await self._api.async_set_cover_tilt_position(position)
        )

    async def async_update(self) -> None:
        _LOGGER.info(f"performing async update for {self.entity_id}")
        cover_state = await self._api.async_get_cover_state()
        await self._update_hass_state(cover_state)

    async def _update_hass_state(self, cover_state):
        self.hass.data[DOMAIN][self._config_entry.entry_id][STATE] = cover_state
        if self.entity_id is not None:
            self.async_write_ha_state()

    def _state(self) -> dict[str:any]:
        state = self.hass.data[DOMAIN][self._config_entry.entry_id][STATE]
        if state is not None:
            state = state.get("shutter") or state
        return state or {}

    def _device_info(self) -> dict[str:any]:
        return self.hass.data[DOMAIN][self._config_entry.entry_id][DEVICE_INFO] or {}

    def _cover_state(self):
        return _BLEBOX_TO_HASS_COVER_STATES[self._state().get("state")]

    def _desired_position(self):
        return self._state().get("desiredPos")


_BLEBOX_TO_HASS_COVER_STATES = {
    None: None,
    0: STATE_CLOSING,  # moving down
    1: STATE_OPENING,  # moving up
    2: STATE_OPEN,  # manually stopped
    3: STATE_CLOSED,  # lower limit
    4: STATE_OPEN,  # upper limit / open
}
