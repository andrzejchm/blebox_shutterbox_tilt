"""Adds config flow for BleBox shutterBox with tilt."""
from typing import Optional, Dict

import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from blebox_uniapi import products

from .options_flow import ShutterboxOptionsFlow
from .api import ShutterboxApiClient
from .const import CONF_IP_ADDRESS, CONF_PORT, DOMAIN, DEFAULT_PORT

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
            valid = await self._test_config(
                user_input[CONF_IP_ADDRESS],
                user_input[CONF_PORT],
            )
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_IP_ADDRESS], data=user_input
                )
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    async def _test_config(self, ip_address: str, port: str):
        """Return true if credentials is valid."""
        try:
            products.Products()
            session = async_create_clientsession(self.hass)
            client = ShutterboxApiClient(ip_address, port, session, self.hass)
            await client.async_init_cover()
            return True
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.exception(f"{ex}")
            pass
        return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ShutterboxOptionsFlow(config_entry)

    async def _show_config_form(
        self,
        user_input: Optional[Dict[str, any]],
    ):  # pylint: disable=unused-argument
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
