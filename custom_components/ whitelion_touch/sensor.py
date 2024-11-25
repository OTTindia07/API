from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_DEVICE_ID, CONF_API_URL

class WhitelionTouchSensor(SensorEntity):
    """Representation of the Whitelion Touch Panel sensor."""

    def __init__(self, device_id, api_url):
        self._device_id = device_id
        self._api_url = api_url
        self._state = None

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            async with ClientSession() as session:
                payload = {
                    "cmd": "DL",
                    "device_ID": self._device_id,
                    "serial": 1,
                }
                headers = {"Content-Type": "application/json"}
                async with session.post(self._api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._state = data.get("model")
        except Exception:
            self._state = None

    @property
    def name(self):
        return f"Whitelion Touch Sensor ({self._device_id})"

    @property
    def state(self):
        return self._state
