"""Switch platform for Whitelion Touch."""
import logging
import asyncio
import aiohttp
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from .const import (
    DOMAIN,
    CMD_STATUS,
    CMD_SWITCH_CONTROL,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up switches based on a config entry."""
    ip_address = entry.data["ip_address"]
    device_id = entry.data["device_id"]
    model = entry.data["model"]

    # Extract number of switches from model (e.g., "6M" -> 6)
    try:
        num_switches = int(''.join(filter(str.isdigit, model)))
    except ValueError:
        _LOGGER.error("Could not determine number of switches from model %s", model)
        return

    async def async_update_data():
        """Fetch data from API."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{ip_address}/api",
                json={
                    "cmd": CMD_STATUS,
                    "device_ID": device_id,
                    "serial": 12345
                }
            ) as response:
                data = await response.json()
                return data.get("data", [])

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"whitelion_{device_id}",
        update_method=async_update_data,
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    switches = []
    for switch_num in range(1, num_switches + 1):
        switches.append(
            WhitelionSwitch(
                coordinator,
                ip_address,
                device_id,
                switch_num,
                model
            )
        )

    async_add_entities(switches)

class WhitelionSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Whitelion switch."""

    def __init__(self, coordinator, ip_address, device_id, switch_num, model):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._ip_address = ip_address
        self._device_id = device_id
        self._switch_num = switch_num
        self._model = model
        self._attr_name = f"Whitelion Switch {switch_num}"
        self._attr_unique_id = f"{device_id}_switch_{switch_num}"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"Whitelion {self._model}",
            "manufacturer": "Whitelion",
            "model": self._model,
        }

    @property
    def is_on(self):
        """Return true if switch is on."""
        if self.coordinator.data:
            try:
                # Format switch number to two digits (e.g., 1 -> "01")
                switch_id = f"{self._switch_num:02d}"
                # Find corresponding switch status
                for status in self.coordinator.data:
                    if status.startswith(switch_id):
                        return status.endswith("1")
            except (IndexError, AttributeError):
                return False
        return False

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._send_command(1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._send_command(0)
        await self.coordinator.async_request_refresh()

    async def _send_command(self, state):
        """Send command to the switch."""
        switch_id = f"{self._switch_num:02d}"
        data = f"{switch_id}XX{state}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"http://{self._ip_address}/api",
                    json={
                        "cmd": CMD_SWITCH_CONTROL,
                        "device_ID": self._device_id,
                        "data": data,
                        "serial": 12345
                    }
                ) as response:
                    if response.status == 200:
                        return True
            except aiohttp.ClientError as err:
                _LOGGER.error("Error sending command to switch: %s", err)
                return False
