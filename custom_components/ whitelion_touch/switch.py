import random
from aiohttp import ClientSession
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, MANUFACTURER

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Whitelion switches from a config entry."""
    ip_address = config_entry.data["ip_address"]
    device_id = config_entry.data["device_id"]

    # Fetch model information
    model_info = await fetch_model_info(ip_address, device_id)
    num_switches = int(model_info["model"][0]) + 1 if model_info["model"][0].isdigit() else 0

    # Fetch initial switch states
    switch_states = await fetch_switch_states(ip_address, device_id)

    # Create switches
    switches = [
        WhitelionSwitch(ip_address, device_id, switch_id, switch_states[switch_id - 1], config_entry)
        for switch_id in range(1, num_switches + 1)
    ]
    async_add_entities(switches)

async def fetch_model_info(ip_address, device_id):
    """Fetch model information."""
    serial_number = random.randint(0, 65536)
    async with ClientSession() as session:
        async with session.post(
            f"http://{ip_address}/api",
            json={"cmd": "DL", "device_ID": device_id, "serial": serial_number},
            timeout=10,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

async def fetch_switch_states(ip_address, device_id):
    """Fetch current switch states."""
    serial_number = random.randint(0, 65536)
    async with ClientSession() as session:
        async with session.post(
            f"http://{ip_address}/api",
            json={"cmd": "DS", "device_ID": device_id, "serial": serial_number},
            timeout=10,
        ) as resp:
            resp.raise_for_status()
            return (await resp.json())["data"]

class WhitelionSwitch(SwitchEntity):
    """Representation of a Whitelion Touch switch."""

    def __init__(self, ip_address, device_id, switch_id, initial_state, config_entry):
        self._ip_address = ip_address
        self._device_id = device_id
        self._switch_id = switch_id
        self._is_on = initial_state.endswith("1")
        self._config_entry = config_entry

    @property
    def unique_id(self):
        return f"{self._device_id}_{self._switch_id}"

    @property
    def name(self):
        return f"Switch {self._switch_id}"

    @property
    def device_info(self):
        """Return device information for the entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name="Whitelion Touch Panel",
            manufacturer=MANUFACTURER,
            model="Touch Panel",
        )

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._send_command(f"01XX{self._switch_id}1")
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._send_command(f"01XX{self._switch_id}0")
        self._is_on = False
        self.async_write_ha_state()

    async def _send_command(self, command_data):
        """Send a command to the device."""
        serial_number = random.randint(0, 65536)
        async with ClientSession() as session:
            async with session.post(
                f"http://{self._ip_address}/api",
                json={"cmd": "ST", "device_ID": self._device_id, "data": command_data, "serial": serial_number},
                timeout=10,
            ) as resp:
                resp.raise_for_status()
