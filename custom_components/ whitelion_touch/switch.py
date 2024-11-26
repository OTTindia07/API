import random
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN, CONF_DEVICE_ID, CONF_IP_ADDRESS, CONF_MODEL

def setup_platform(hass, config_entry, add_entities, discovery_info=None):
    """Set up switches based on the model."""
    ip_address = config_entry.data[CONF_IP_ADDRESS]
    device_id = config_entry.data[CONF_DEVICE_ID]
    model = config_entry.data[CONF_MODEL]

    # Determine the number of switches based on the model
    switch_count = {
        "3M": 3,
        "4M": 5,
        "6M": 7,
        "8M": 9
    }.get(model, 0)

    switches = [
        WhitelionSwitch(ip_address, device_id, f"Switch {i+1}", i + 1)
        for i in range(switch_count)
    ]

    add_entities(switches)

class WhitelionSwitch(SwitchEntity):
    """Representation of a Whitelion Touch switch."""

    def __init__(self, ip_address, device_id, name, switch_id):
        self._ip_address = ip_address
        self._device_id = device_id
        self._name = name
        self._switch_id = switch_id
        self._is_on = False

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        serial = random.randint(0, 65536)
        await self._send_command("ST", f"{self._switch_id}XX1", serial)
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        serial = random.randint(0, 65536)
        await self._send_command("ST", f"{self._switch_id}XX0", serial)
        self._is_on = False
        self.async_write_ha_state()

    async def async_update(self):
        serial = random.randint(0, 65536)
        response = await self._send_command("DS", None, serial)
        status_data = response.get("data", [])
        for item in status_data:
            if item.startswith(f"{self._switch_id:02}"):
                self._is_on = item[-1] == "1"
                self.async_write_ha_state()

    async def _send_command(self, command, data, serial):
        import requests
        payload = {
            "cmd": command,
            "device_ID": self._device_id,
            "serial": serial,
        }
        if data:
            payload["data"] = data

        response = requests.post(
            f"http://{self._ip_address}/api", json=payload, timeout=10
        )
        response.raise_for_status()
        return response.json()
