"""options flow"""
import logging

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from . import create_schema
from . import ShutterboxApiClient
from .const import CONF_IP_ADDRESS
from .const import CONF_PORT
from .errors import ErrorWithMessageId

_LOGGER = logging.getLogger(__name__)


class ShutterboxOptionsFlow(config_entries.OptionsFlow):
    """Config flow options handler for blebox_shutterbox_tilt."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)
        self._errors = {}
        self.device_info = {}

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input: dict = None):
        """Handle a flow initialized by the user."""
        session = async_create_clientsession(self.hass)
        self._errors = {}
        if user_input is not None:
            api = ShutterboxApiClient(user_input[CONF_IP_ADDRESS], user_input[CONF_PORT], session, self.hass)
            try:
                self.device_info = await api.async_get_device_info()
                if user_input is not None:
                    self.options.update(user_input)
                    return await self._update_options()
            except ErrorWithMessageId as ex:
                message = f'{ex}'
                _LOGGER.exception(message)
                self._errors = {'base': ex.message_id()}
            except Exception as ex:
                message = f'{ex}'
                _LOGGER.exception(message)
                self._errors = {'base': 'unknown'}
            if self._errors:
                return self.async_show_form(
                    step_id="user",
                    data_schema=create_schema(user_input),
                    errors=self._errors
                )
        else:
            return self.async_show_form(
                step_id="user",
                data_schema=create_schema(user_input),
                errors=self._errors
            )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.device_info.get('deviceName'),
            data=self.options,
        )
