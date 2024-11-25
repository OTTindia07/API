from homeassistant.components.switch import SwitchEntity
from aiohttp import ClientSession
from .const import DOMAIN, CONF_DEVICE_ID, CONF_API_URL

class WhitelionTouchSwitch(SwitchEntity):
    """Representation of a switch for the Whitelion Touch Panel."""

    def __init__(self, device_id, api_url, switch_number):
        self._device_id = device_id
        self._api_url = api_url
        self._switch_number = switch_number
        self._state = False

    async def async_turn_on(self):
        """Turn the switch on."""
        await self._send_command(f"{self._switch_number}XX1")
        self._state = True

    async def async_turn_off(self):
        """Turn the switch off."""
        await self._send_command(f"{self._switch_number}XX0")
        self._state = False

    async def _send_command(self, data):
        """Send a command to the touch panel."""
        async with ClientSession() as session:
            payload = {
                "cmd": "ST",
                "device_ID": self._device_id,
                "data": data,
                "serial": 1,
            }
            headers = {"Content-Type": "application/json"}
            await session.post(self._api_url, json=payload, headers=headers)

    @property
    def is_on(self):
        return self._state
