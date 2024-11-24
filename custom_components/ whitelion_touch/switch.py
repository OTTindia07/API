"""Switch platform for Whitelion Touch."""

from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Whitelion switches dynamically."""
    ip_address = entry.data["ip_address"]
    device_id = entry.data["device_id"]
    model = entry.data["model"]

    # Parse number of switches from the model (e.g., "3M" = 3 switches)
    num_switches = int(model[0]) if model[0].isdigit() else 1

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
        return f"Whitelion Switch {self._switch_id}"

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        await self._send_command("1")
        self._is_on = True

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        await self._send_command("0")
        self._is_on = False

    async def _send_command(self, state):
        """Send ST command to the device."""
        data = f"{self._switch_id:02}XX{state}"
        payload = {
            "cmd": "ST",
            "device_ID": self._device_id,
            "data": data,
            "serial": 12345
        }
        url = f"http://{self._ip_address}/api"
        try:
            response = await self.hass.async_add_executor_job(
                requests.post, url, json=payload, timeout=10
            )
            response.raise_for_status()
        except requests.exceptions.RequestException:
            pass
