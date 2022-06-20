"""Adds config flow for BleBox shutterBox with tilt."""
import logging
from typing import Dict
from typing import Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import ShutterboxApiClient
from .const import CONF_IP_ADDRESS
from .const import CONF_PORT
from .const import DEFAULT_PORT
from .const import DOMAIN
from .errors import ErrorWithMessageId
from .options_flow import ShutterboxOptionsFlow

_LOGGER = logging.getLogger(__name__)


class ShutterboxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for blebox_shutterbox_tilt."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input: dict = None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            device_info = await self._test_config(
                user_input[CONF_IP_ADDRESS],
                user_input[CONF_PORT],
            )
            if device_info:
                return self.async_create_entry(
                    title=device_info.get("deviceName") or user_input[CONF_IP_ADDRESS],
                    description=user_input[CONF_IP_ADDRESS],
                    data=user_input,
                )

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    async def _test_config(
            self,
            ip_address: str,
            port: int,
    ) -> Optional[Dict[str, any]]:
        """Return true if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = ShutterboxApiClient(ip_address, port, session, self.hass)
            device_info = await client.async_get_device_info()
            if device_info is not None:
                unique_id = device_info.get("id") or ip_address
                await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            return device_info
        except ErrorWithMessageId as ex:
            message = f"{ex}"
            _LOGGER.exception(message)
            self._errors["base"] = ex.message_id()

        return None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ShutterboxOptionsFlow(config_entry)

    async def _show_config_form(
            self,
            user_input: Optional[Dict[str, any]],
    ):
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=self._create_schema(user_input),
            errors=self._errors,
        )

    @staticmethod
    def _create_schema(
            user_input: Optional[Dict[str, any]],
    ) -> vol.Schema:
        if user_input is not None:
            ip_address = user_input.get(CONF_IP_ADDRESS) or ""
            port = user_input.get(CONF_PORT) or DEFAULT_PORT
        else:
            ip_address = ""
            port = DEFAULT_PORT
        return vol.Schema(
            {
                vol.Required(
                    CONF_IP_ADDRESS,
                    default=ip_address,
                ): str,
                vol.Required(
                    CONF_PORT,
                    default=port,
                ): int,
            }
        )
