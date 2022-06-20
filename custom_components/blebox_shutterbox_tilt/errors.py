"""errors used across the integration"""
from abc import ABC, abstractmethod

from homeassistant.exceptions import ConfigEntryNotReady


class ErrorWithMessageId(ConfigEntryNotReady, ABC):
    """Error with message id for translation purposes"""

    @abstractmethod
    def message_id(self) -> str:
        """translation message_id"""


class CannotConnectToShutterBox(ErrorWithMessageId):
    """Raised when cannot connect to shutterbox"""

    def message_id(self) -> str:
        return "cannot_connect"


class NoDeviceInfoError(ErrorWithMessageId):
    """raised when the device info is malformed"""

    def message_id(self) -> str:
        return "no_device_info"


class InvalidDeviceTypeError(ErrorWithMessageId):
    """Raised when fetched device info is not shutterBox"""

    def message_id(self) -> str:
        return "invalid_device_type"
