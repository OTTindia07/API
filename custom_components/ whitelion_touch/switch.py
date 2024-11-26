import random
import aiohttp
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Whitelion switches from a config entry."""
    ip_address = entry.data["ip_address"]
    device_id = entry.data["device_id"]

    # Fetch model information to determine number of switches.
    model_info = await fetch_model_info(ip_address, device_id)
    
    # Extract number of switches from model (e.g., '6M' -> 7 switches).
    num_switches = int(model_info['model'][0]) + 1 if model_info['model'][0].isdigit() else 0
    
    # Fetch initial switch states.
    switch_states = await fetch_switch_states(ip_address, device_id)

    # Create switch entities.
    switches = [
        WhitelionSwitch(ip_address, device_id, switch_id, switch_states[switch_id - 1])
        for switch_id in range(1, num_switches + 1)
    ]
    
    async_add_entities(switches)

async def fetch_model_info(ip_address, device_id):
    """Fetch model information from the panel."""
    serial_number = random.randint(0, 65536)
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://{ip_address}/api",
            json={"cmd": "DL", "device_ID": device_id, "serial": serial_number},
            timeout=10
        ) as resp:
            if resp.status != 200:
                raise aiohttp.ClientError("Failed to fetch model information.")
            
            model_info = await resp.json()
            if "model" not in model_info:
                raise ValueError("Model information missing in response.")
            return model_info

async def fetch_switch_states(ip_address, device_id):
    """Fetch current switch states from the panel."""
    serial_number = random.randint(0, 65536)
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://{ip_address}/api",
            json={"cmd": "DS", "device_ID": device_id, "serial": serial_number},
            timeout=10
        ) as resp:
            if resp.status != 200:
                raise aiohttp.ClientError("Failed to fetch switch states.")
            
            state_info = await resp.json()
            if "data" not in state_info:
                raise ValueError("Switch states missing in response.")
            return state_info["data"]

class WhitelionSwitch(SwitchEntity):
    """Representation of a Whitelion Touch switch."""

    def __init__(self, ip_address, device_id, switch_id, initial_state):
        self._ip_address = ip_address
        self._device_id = device_id
        self._switch_id = switch_id
        self._is_on = initial_state.endswith("1")  # Assume '1' means ON and '0' means OFF

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
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._send_command(f"01XX{self._switch_id}0")
        self._is_on = False
        self.async_write_ha_state()

    async def _send_command(self, command_data):
        """Send a command to the device."""
        serial_number = random.randint(0, 65536)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{self._ip_address}/api",
                json={"cmd": "ST", "device_ID": self._device_id, "data": command_data, "serial": serial_number},
                timeout=10
            ) as resp:
                resp.raise_for_status()
