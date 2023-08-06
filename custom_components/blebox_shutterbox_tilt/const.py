"""Constants for BleBox shutterBox with tilt."""
# Base component constants
NAME = "BleBox shutterBox with tilt"
DOMAIN = "blebox_shutterbox_tilt"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "1.0.1"

ISSUE_URL = "https://github.com/andrzejchm/blebox_shutterbox_tilt/issues"


# Platforms
COVER = "cover"
PLATFORMS = [COVER]


# Configuration and options
CONF_IP_ADDRESS = "ip_address"
CONF_PORT = "port"
STATE = "state"
DATA = "data"
API_CLIENT = "api_client"
DEVICE_INFO = "device_info"

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_SETUP_TIMEOUT = 10
DEFAULT_PORT = 80

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
