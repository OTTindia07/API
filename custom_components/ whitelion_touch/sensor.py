from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    api = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([WhitelionTouchStatusSensor(api)])

class WhitelionTouchStatusSensor(SensorEntity):
    def __init__(self, api):
        self.api = api
        self._status = None

    @property
    def name(self):
        return "Touch Panel Status"

    @property
    def state(self):
        return self._status

    async def async_update(self):
        response = self.api.get_status()
        if response.get("error") == 0:
            self._status = response.get("data")
