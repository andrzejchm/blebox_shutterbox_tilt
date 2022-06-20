import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ShutterboxApiClient
from .const import DOMAIN, STATE

_LOGGER: logging.Logger = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=30)


class ShutterboxDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: ShutterboxApiClient,
    ) -> None:
        """Initialize."""
        self._api = client

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            cover_state = await self._api.async_init_cover()
            self.hass.data[DOMAIN][self.config_entry.entry_id][STATE] = cover_state
        except Exception as exception:
            raise UpdateFailed() from exception
