"""options flow"""

import voluptuous as vol

from homeassistant import config_entries
from .const import CONF_IP_ADDRESS, CONF_PORT


# TODO
class ShutterboxOptionsFlow(config_entries.OptionsFlow):
    """Config flow options handler for blebox_shutterbox_tilt."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IP_ADDRESS,
                        default=self.options.get(CONF_IP_ADDRESS, ''),
                    ): str,
                    vol.Required(
                        CONF_IP_ADDRESS,
                        default=self.options.get(CONF_PORT, 80),
                    ): int
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_IP_ADDRESS),
            data=self.options,
        )
