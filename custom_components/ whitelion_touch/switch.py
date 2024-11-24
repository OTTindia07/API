from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Whitelion switches from a config entry."""
    ip_address = entry.data["ip_address"]
    device_id = entry.data["device_id"]
    model = entry.data["model"]

    num_switches = int(model[0])  # Assume model format like "3M" or "2M"

    switches = [
        WhitelionSwitch(ip_address, device_id, switch_id)
        for switch_id in range(1, num_switches + 1)
    ]

    async_add_entities(switches, update_before_add=True)

class WhitelionSwitch(SwitchEntity):
    """Representation of a Whitelion Touch switch."""

    def __init__(self, ip_address, device_id, switch_id):
        self._ip_address = ip_address
        self._device_id = device_id
        self._switch_id = switch_id
        self._is_on = False

    @property
    def name(self):
        """Return the name of the switch."""
        return f"Switch {self._switch_id}"

    @property
    def is_on(self):
        """Return the state of the switch."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._send_command(f"01XX{self._switch_id}1")
        self._is_on = True

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._send_command(f"01XX{self._switch_id}0")
        self._is_on = False

    async def _send_command(self, data):
        """Send a command to the device."""
        import requests
        response = requests.post(
            f"http://{self._ip_address}/api",
            json={
                "cmd": "ST",
                "device_ID": self._device_id,
                "data": data,
                "serial": 12345
            },
            timeout=10
        )
        response.raise_for_status()
