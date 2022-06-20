"""Tests for BleBox shutterBox with tilt api."""
import asyncio

import pytest
from _pytest.logging import LogCaptureFixture
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.blebox_shutterbox_tilt.api import ShutterboxApiClient
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.blebox_shutterbox_tilt.errors import CannotConnectToShutterBox, NoDeviceInfoError, \
    InvalidDeviceTypeError


async def test_api(hass, aioclient_mock: AiohttpClientMocker, caplog: LogCaptureFixture):
    """Test API calls."""

    # To test the api submodule, we first create an instance of our API client
    api = ShutterboxApiClient("192.168.1.123", 80, async_get_clientsession(hass), hass)

    # Use aioclient_mock which is provided by `pytest_homeassistant_custom_components`
    # to mock responses to aiohttp requests. In this case we are telling the mock to
    # return {"test": "test"} when a `GET` call is made to the specified URL. We then
    # call `async_get_data` which will make that `GET` request.
    aioclient_mock.get(
        "http://192.168.1.123/api/device/state", json={
            "device": {
                "deviceName": "My ShutterBox",
                "type": "shutterBox",
                "product": "shutterBox",
                "hv": "9.6",
                "fv": "0.1013",
                "universe": 0,
                "apiLevel": "20190911",
                "iconSet": 0,
                "categories": [
                    5
                ],
                "id": "f12a29130ce",
                "ip": "192.168.2.184",
                "availableFv": None
            }
        }
    )
    assert (await api.async_get_device_info()).get("deviceName") == "My ShutterBox"

    aioclient_mock.get("http://192.168.1.123/api/shutter/state", json=
    {
        "shutter": {
            "state": 2,
            "currentPos": {
                "position": 92,
                "tilt": 100
            },
            "desiredPos": {
                "position": 92,
                "tilt": 100
            },
            "favPos": {
                "position": 240,
                "tilt": 50
            }
        }
    })

    assert (await api.async_get_cover_state()).get("shutter") is not None

    aioclient_mock.clear_requests()
    aioclient_mock.get(
        "http://192.168.1.123/api/device/state", exc=asyncio.TimeoutError
    )
    with pytest.raises(CannotConnectToShutterBox):
        await api.async_get_device_info()

    aioclient_mock.clear_requests()
    aioclient_mock.get(
        "http://192.168.1.123/api/device/state", json={"something": "else"}
    )
    with pytest.raises(NoDeviceInfoError):
        await api.async_get_device_info()

    aioclient_mock.clear_requests()
    aioclient_mock.get(
        "http://192.168.1.123/api/device/state", json={
            "device": {
                "type": "lightBox",
            }
        }

    )
    with pytest.raises(InvalidDeviceTypeError):
        await api.async_get_device_info()
