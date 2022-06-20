"""
Custom integration to integrate BleBox shutterBox with tilt with Home Assistant.

For more details about this integration, please refer to
https://github.com/andrzejchm/blebox-shutterbox-tilt
"""
import asyncio
import logging
from typing import Optional, Dict
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ShutterboxApiClient
from .const import API_CLIENT, DEFAULT_PORT
from .const import CONF_IP_ADDRESS
from .const import CONF_PORT
from .const import DATA
from .const import DEVICE_INFO
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        _LOGGER.info(STARTUP_MESSAGE)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id].setdefault(DATA, {})
    hass.data[DOMAIN][entry.entry_id][DATA] = entry.data
    ip_address = entry.data.get(CONF_IP_ADDRESS)
    port = entry.data.get(CONF_PORT)

    session = async_get_clientsession(hass)
    client = ShutterboxApiClient(ip_address, port, session, hass)

    hass.data[DOMAIN][entry.entry_id][API_CLIENT] = client
    try:
        device_info = await client.async_get_device_info()
    except ConfigEntryNotReady as ex:
        raise ex
    except Exception as ex:
        raise ConfigEntryNotReady(f"{ex}") from ex
    hass.data[DOMAIN][entry.entry_id][DEVICE_INFO] = device_info

    for platform in PLATFORMS:
        await hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    entry.add_update_listener(async_reload_entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


def create_schema(
        user_input: Optional[Dict[str, any]],
) -> vol.Schema:
    """creates schema for config flow and options flow"""
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
