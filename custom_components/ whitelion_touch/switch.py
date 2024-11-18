from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    api = hass.data[DOMAIN][config_entry.entry_id]
    switches = [TouchPanelSwitch(api, i) for i in range(1, 6)]  # Example: 5 switches
    async_add_entities(switches)

class TouchPanelSwitch(SwitchEntity):
    def __init__(self, api, switch_id):
        self.api = api
        self.switch_id = switch_id
        self._is_on = False

    @property
    def name(self):
        return f"Touch Panel Switch {self.switch_id}"

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        response = self.api.set_switch(self.switch_id, True)
        if response.get("error") == 0:
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        response = self.api.set_switch(self.switch_id, False)
        if response.get("error") == 0:
            self._is_on = False
            self.async_write_ha_state()
