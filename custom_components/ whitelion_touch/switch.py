from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN
from .whitelion_api import WhitelionAPI
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Whitelion switches based on a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    device_id = data["device_id"]
    ip_address = data["ip_address"]
    model = data["model"]

    api = WhitelionAPI(device_id, ip_address)
    switches = []

    # Determine the number of switches based on the model mapping
    model_switch_map = {
        "2M": 2,
        "3M": 3,
        "4M": 5,
        "6M": 7,
        "8M": 9,
    }
    switch_count = model_switch_map.get(model, 0)

    # Create switch entities dynamically
    for i in range(1, switch_count + 1):
        switches.append(WhitelionSwitch(api, device_id, model, f"Switch {i}", i))

    # Register the device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, device_id)},
        manufacturer="Whitelion",
        model=model,
        name=f"Whitelion Touch Panel {device_id}",
        sw_version="1.0",  # Example version
        configuration_url=f"http://{ip_address}"
    )

    async_add_entities(switches, update_before_add=True)


class WhitelionSwitch(SwitchEntity):
    """Representation of a Whitelion Switch."""

    def __init__(self, api, device_id, model, name, switch_number):
        """Initialize the switch."""
        self._api = api
        self._device_id = device_id
        self._model = model
        self._name = name
        self._switch_number = switch_number
        self._is_on = False
        self._unique_id = f"{device_id}_{switch_number}"
        self._last_command_time = None

    @property
    def unique_id(self):
        """Return a unique ID for the switch."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return the current state of the switch."""
        return self._is_on

    @property
    def device_info(self):
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            manufacturer="Whitelion",
            model=self._model,
            name=f"Whitelion Touch Panel {self._device_id}",
        )

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        try:
            await self.hass.async_add_executor_job(self._api.set_switch, self._switch_number, 1)
            self._is_on = True
            self._last_command_time = asyncio.get_event_loop().time()
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Error turning on {self._name}: {e}")

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        try:
            await self.hass.async_add_executor_job(self._api.set_switch, self._switch_number, 0)
            self._is_on = False
            self._last_command_time = asyncio.get_event_loop().time()
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Error turning off {self._name}: {e}")

    async def async_update(self):
        """Fetch the latest state of the switch from the backend."""
        try:
            # Wait 2 seconds after a command before fetching state
            if self._last_command_time and (asyncio.get_event_loop().time() - self._last_command_time < 2):
                return

            # Fetch the latest status for all switches
            status = await self.hass.async_add_executor_job(self._api.get_status)

            # Update the state of this specific switch
            switch_status = status.get(self._switch_number, None)
            if switch_status is not None:
                self._is_on = switch_status
                self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Error updating {self._name}: {e}")
